我看了更新后的仓库。我的判断很明确：**你说得对，现在还没达到你想要的目标；而且现在已经不是“实验没跑完”的问题，而是“完整跑完以后，当前方法没有形成 closed-loop superiority”的问题。**

和之前评估里“先把 1440-row Gate C 跑完整”的建议相比，现在 blocker 已经变了：仓库最新提交是 **2026-05-27 的 `chore: record locked gate c execution results`**，说明你已经把 locked Gate C 结果写进来了；debug 记录也显示 1440/1440 行已经执行完成，row audit 干净，没有 missing、failed、duplicate、unpaired、bad provenance、schema invalid。([GitHub][1])  但同一个 debug 记录接着说，strict paired evidence 仍然是 `INCONCLUSIVE`，根因是 input artifact 的 Gate C status 是 `FAILED`；`gate_c_primary_metrics_v1.status` 在 Holm-Bonferroni correction 下也是 `FAILED`，所以 closed-loop superiority 仍然不允许。 这和之前“还没产生强 claim 证据”的判断一脉相承，但现在证据更硬：**不是没证据，而是当前方法没有赢。** 

仓库自己的 summary 也没有给你留灰区：`Package status: INCONCLUSIVE`，`Strict Gate C status: INCONCLUSIVE`，`Closed-loop superiority claim allowed: false`。 最新 v1.4 locked protocol 的比较对象也不是弱 baseline，而是 `max_pressure`、`capacity_aware_pressure`、`finite_storage_double_pressure`，并且场景覆盖 downstream blockage、spillback stress、incident capacity drop、oversaturation、turning shock、switching-loss-sensitive，主指标包括 penalized travel time、delay、spillback、blocking、unfinished vehicles。  所以现在不能继续把论文写成“现有 v1.4 已经强于 baselines”。这会被你自己的 repo 推翻。

但我同意你的方向：**这篇不能只做一个 claim discipline 很好的 negative / equivalence paper。要坚持理论创新，而且效果上要能打过强 baselines。** 为了做到这一点，我不建议继续微调 v1.4 的权重；我建议开一个 **v1.5 方法论重构**，把贡献从现在的 “finite-storage weighted pressure” 升级成：

> **Dynamic finite-storage primal-dual pressure control：从有限存储交通网络的动态约束松弛中导出可更新的 storage / spillback / release shadow prices；在 slack regime 严格退化为 max-pressure，在 binding regime 通过真实存储占用、多跳 spillback cascade 和 upstream release value 与 pressure-style baselines 分离。**

这条路线可以同时保住你要的两件事：**理论上强**，并且有更现实的机会在效果上超过 baselines。

---

## 1. 当前 v1.4 为什么没达到目标

v1.4 选中的候选是 `finite_storage_primal_dual_v1_4_score`，候选选择理由是它直接针对 bounded-harm 和低 action-change 两个失败模式，改动项包括 `downstream_storage`、`spillback`、`switching`、`service`，并保留 action decomposition audit surface。 表面看这是对的，但结果显示它没有真正把动作从 pressure family 中分离出来。

失败诊断很关键：bounded harm 有 48 个，non-worsening 只有 10 个，strict-positive signals 只有 4 个。更严重的是，诊断把最高等级 failure driver 标为 `controller_action_weakness`，并指出 finite-storage decisions 只在 **9.833%** 的 audited TLS decisions 中不同于 pressure；非零组件主要是 `pressure` 和 `switching`，而不是你理论上想要的 downstream storage / spillback / service。

这说明 v1.4 的问题不是“统计检验太严”那么简单，而是：

**当前 controller 实际上大部分时间还是 pressure controller。**
如果动作只有约 10% 不同，而且不同项主要不是 storage/spillback，那么它很难在 closed-loop 指标上稳定超过 `capacity_aware_pressure` 和 `finite_storage_double_pressure`。

---

## 2. 我认为最致命的技术问题：finite storage state 用错了“存储变量”

这是我看代码后最想强调的一点。

`finite_storage_schema.build_finite_storage_state()` 里，residual receiving capacity、occupancy ratio、spillback/blocking 都是用 `normalized_queues` 计算的；也就是用 halting queue 近似链路存储占用。 live SUMO 控制里，finite-storage controller 也是把 `queues` 和 `capacities` 传进 `build_completed_finite_storage_state()`，而不是把 edge vehicle count / occupancy 作为存储状态传进去。

这在理论上和实验上都很危险。**有限存储约束绑定的是 link occupancy / number of vehicles / receiving capacity，不是 halting queue。** 下游 link 可能已经被 moving vehicles 填满，receiving capacity 已经很小，但 halting queue 还不高；此时用 queue/capacity 作为 storage occupancy 会低估 binding，导致 downstream_storage 和 spillback 项不激活。诊断里“storage/spillback 组件没有成为主要非零项”正好符合这个现象。

这也解释了为什么 v1.4 打不过 baselines：`capacity_aware_pressure` 和 `finite_storage_double_pressure` 已经在 pressure 上加了 downstream fullness / receiving-capacity correction；如果你的 finite-storage 项又没有用真实 storage occupancy 激活，那它就没有足够新增信息。仓库里的 controller registry 也显示，现有 baselines 已经包含 capacity-aware pressure 和 finite-storage double-pressure，而 v1.4 只是“stronger binding-regime terms”的 finite-storage score variant。 v1.4 score 的实际改动也只是固定权重：pressure 1.0、downstream_storage 1.4、spillback 1.6、switching 1.25、service 1.35、incident 1.0。

**结论：v1.4 不是一个足够新的方法。它更像 weighted pressure heuristic。要强 claim，必须升级为真正的动态原始-对偶有限存储控制。**

---

## 3. 我建议的 v1.5 方法：Dynamic Finite-Storage Primal-Dual Pressure

不要再只写：

[
score = pressure + storage\ penalty + spillback\ penalty + switching\ penalty
]

这个太像 heuristic，也太容易被 `capacity_aware_pressure` 吃掉。

建议改成一个有明确优化来源的动态 controller：

[
S_p(t)=
\sum_{m=(i,j)\in p}
s_m(t)
\Big[
q_i(t)-q_j(t)
+\alpha r_i(t)
-\beta \mu_j(t)
-\gamma \xi_j(t)
+\delta a_i(t)
\Big]
-\eta L(p,p_t)
]

其中：

* (q_i-q_j)：pressure special case；
* (\mu_j(t))：下游 link (j) 的 storage scarcity dual price，由真实 occupancy 更新；
* (\xi_j(t))：多跳 downstream spillback cascade price，不只看 immediate downstream；
* (r_i(t))：upstream release value，表示如果不服务上游，可能触发 upstream spillback；
* (a_i(t))：age / starvation / service urgency；
* (L(p,p_t))：switching lost time 或 phase transition cost；
* (s_m(t))：movement service / saturation proxy。

动态 dual update 可以写成：

[
\mu_j(t+1)=
\left[
(1-\rho)\mu_j(t)
+
\kappa\left(\frac{n_j(t)}{C_j}-\theta\right)*+
\right]*+
]

[
r_i(t+1)=
\left[
(1-\rho)r_i(t)
+
\kappa_r\left(\frac{n_i(t)}{C_i}-\theta_r\right)*+
\cdot \mathbf{1}{\text{downstream path has receiving slack}}
\right]*+
]

[
\xi_j(t)=\sum_{k\in \mathcal{D}(j)} P_{jk}\mu_k(t)
]

这里 (n_j(t)) 必须是 link occupancy / vehicle count，而不是 halting queue。这样理论贡献就变成：

1. **Pressure recovery theorem**：当所有 storage constraints slack、(\mu=\xi=r=0)，controller 退化为 max-pressure。
2. **Finite-storage separation theorem**：当两个 movements 有相同 local pressure 但 downstream storage scarcity 不同，dynamic primal-dual score 会选择 receiving-capacity 更安全的 movement，而 max-pressure / local pressure 不能区分。
3. **Cascade spillback proposition**：当 immediate downstream 还没满、但 downstream descendant 已经高 shadow price 时，多跳 (\xi_j) 会提前抑制会造成 spillback cascade 的 movement；这是 `capacity_aware_pressure` 的 local fullness correction 不具备的。
4. **Auditable symbolic approximation**：最终 controller 仍可以压缩为 symbolic rule，但 symbolic rule 是从 dynamic dual state 中恢复，而不是从 static queue-pressure 中恢复。

这比现在的“weighted finite-storage pressure”强很多，因为它不是加几个 penalty，而是从动态约束松弛导出一套可更新的 shadow-price controller。

---

## 4. 代码层面最应该改的地方

### A. 把 finite-storage state 从 queue-based 改成 occupancy-based

现在 `build_finite_storage_state()` 用 queue 来算 residual 和 occupancy。 我建议拆成两套状态：

```python
queues = {edge: traci.edge.getLastStepHaltingNumber(edge)}
vehicles = {edge: traci.edge.getLastStepVehicleNumber(edge)}
occupancy = {edge: vehicles[edge] / capacity[edge]}

residual_receiving_capacity = capacity[edge] - vehicles[edge]
service_urgency = queue[edge] / capacity[edge]  # 或 waiting-time based
storage_urgency = vehicles[edge] / capacity[edge]
```

也就是说：

* pressure 仍然可以用 queue；
* storage constraint 必须用 vehicles / occupancy；
* spillback/blocking 应该用 occupancy + queue 共同判断；
* service urgency 可以用 queue、waiting time、age；
* release value 可以用 upstream occupancy。

这一个改动就会显著提高 binding activation，而且理论上更正确。

### B. 增加 stateful dual variables，而不是每一步重新算 heuristic

现在 finite-storage controller 基本是 memoryless score decomposition。v1.4 只是固定权重调整。 我建议在 `run_experiment()` 里维护：

```python
dual_state_by_edge = {
    edge: {
        "storage_price": 0.0,
        "release_price": 0.0,
        "cascade_price": 0.0,
        "service_age": 0.0,
    }
}
```

每个 action interval 后更新一次。这样你才真正有 “primal-dual” 的动态含义，而不是静态 pressure correction。

### C. 增加一个新 controller，不要覆盖 v1.4

在 `CONTROLLER_REGISTRY` 里新增：

```python
"finite_storage_dynamic_primal_dual_v1_5":
    "Dynamic finite-storage primal-dual pressure with occupancy-based storage duals, cascade spillback prices, and upstream release values."
```

保留 v1.4 作为 ablation。这样论文里可以很清楚：

* max_pressure：local pressure baseline；
* capacity_aware_pressure：local downstream fullness baseline；
* finite_storage_double_pressure：finite receiving correction baseline；
* finite_storage_primal_dual_v1_4_score：static weighted finite-storage ablation；
* finite_storage_dynamic_primal_dual_v1_5：你的主方法。

### D. 不要把 v1.5 的 tuning 直接塞进 v1.4 Gate C

仓库的 strict checker 明确把 final evidence 和 exploratory pilots 分开，Gate C 也要求 input artifact status 是 PASSED，否则 strict v1.4 evidence 只能是 inconclusive。 你应该新开 v1.5：

* v1.5-A：state truth / storage activation gate；
* v1.5-B：theory separation synthetic states；
* v1.5-C：training/pilot scenarios for hyperparameter search；
* v1.5-D：locked holdout confirmation；
* v1.5-E：real/grid/Chengdu robustness。

这样不会污染 v1.4 的 claim discipline，也不会被审稿人说 post-hoc tuning。

---

## 5. 实验协议也要改：现在的 Gate C 过于“全指标全格子不许输”

当前 Gate C 的判定逻辑是：每个 scenario × demand multiplier × comparator × metric 都做 paired metric summary，若任何 result 是 bounded harm，则 status = FAILED；只有所有结果都是 non-worsening，并且每个 scenario/demand/comparator group 至少有一个 strict-positive signal，才 PASSED。 这非常保守。保守不是坏事，但如果你要做“比 baselines 好”的论文主 claim，不能让主结论被 279 个细碎 comparisons 绑架。

我建议 v1.5 的主 endpoint 改成理论一致的 composite finite-storage operating cost：

[
J =
\text{delay}
+
\lambda_u \cdot \text{unfinished}
+
\lambda_s \cdot \text{spillback/blocking}
+
\lambda_l \cdot \text{switching lost time}
]

这个 objective 已经和 repo 的 objective components 方向一致：代码里 objective component fields 包含 delay、unfinished vehicle penalty、spillback/blocking time、switching lost time。 后面从 metrics 生成 objective components 时，也正是 delay、unfinished、spillback+blocking、switching count 这些项。

v1.5 Gate 应该这样定义：

**Primary claim：** 主方法在 locked finite-storage binding holdout 上，相比每个强 baseline，paired-seed composite (J) 显著降低。

**Safety guard：** penalized travel time、total delay、unfinished vehicles 不能出现超过预注册阈值的 practical harm。

**Secondary metrics：** spillback、blocking、switching、throughput 分别报告，但不要求每个 cell 都 Holm-Bonferroni 后显著。

这样更像 Transportation Science / TRB 的论文：主目标和理论 objective 一致，其他指标做 mechanism and robustness，而不是用 279 个 comparisons 把自己锁死。

---

## 6. 具体研究路线：我建议你这样重启 v1.5

### Step 1：先修 storage state truth

目标不是马上赢 baseline，而是先证明 finite-storage signal 真的被激活。新的 diagnostic gate：

* storage occupancy 使用 vehicle count；
* residual receiving capacity 使用 capacity - vehicle count；
* spillback/blocking 使用 occupancy threshold + queue；
* downstream_storage、spillback、release、cascade 组件在 binding scenarios 中非零；
* finite-storage action 与 pressure action 的差异率至少达到一个预注册阈值，例如 20%；
* 差异动作必须集中出现在 high occupancy / low receiving capacity 的时段。

如果这一步不过，后面 closed-loop 不可能稳定赢。

### Step 2：做理论 separation，不要只靠仿真

构造两个 movements：

* movement A：高 upstream queue，高 downstream queue，local pressure 看起来不错，但 downstream storage nearly full；
* movement B：upstream queue 稍低，但 downstream receiving capacity 充足；
* max-pressure / capacity-aware pressure 在某些参数下会选 A 或无法稳定区分；
* dynamic primal-dual storage price 会选 B，避免 blocking / spillback propagation。

这可以写成 proposition，而不是实验现象。

### Step 3：训练/选择参数只用 pilot split

不要在 locked holdout 上调 (\alpha,\beta,\gamma,\delta,\eta)。用 training scenarios 和 training seeds 选择参数，然后冻结：

```json
{
  "controller_id": "finite_storage_dynamic_primal_dual_v1_5",
  "alpha_release": ...,
  "beta_storage": ...,
  "gamma_cascade": ...,
  "delta_service": ...,
  "eta_switching": ...,
  "dual_step_size": ...,
  "dual_decay": ...
}
```

之后生成 `v1_5_locked_protocol.json`。

### Step 4：locked holdout 必须保留强 baseline

不要弱化 baseline。继续保留：

* `max_pressure`
* `capacity_aware_pressure`
* `finite_storage_double_pressure`

但我建议再加两个 ablation baseline：

* `finite_storage_static_v1_4_score`
* `occupancy_capacity_aware_pressure`

这样如果 v1.5 仍然赢，你的 claim 会更硬：不是因为 baseline 没看到 occupancy，而是因为 dynamic dual / cascade / release 机制真的有用。

### Step 5：主结果表不要写“到处赢”，写“目标域赢”

你可以强，但要精确：

> 在 finite-storage binding regimes 中，dynamic primal-dual generalized pressure 在 locked paired-seed holdout 上降低 composite finite-storage operating cost，并在 spillback/blocking/unfinished vehicle 指标上相对 max-pressure-style baselines 显示机制性改善；在 slack regimes 中，该方法退化为 pressure-equivalent behavior。

这比“dual sensitivity beats pressure”更强，因为它有边界、有理论、有机制、有结果。

---

## 7. 可以直接替换论文贡献表述

我建议把 contribution 改成下面这种：

**Contribution 1 — Theory.**
We derive a dynamic finite-storage primal-dual signal-control principle from a capacitated traffic-network relaxation. The controller recovers max-pressure in slack regimes and introduces storage-scarcity, cascade-spillback, and upstream-release shadow prices when finite-storage constraints bind.

**Contribution 2 — Algorithm.**
We instantiate the theory as an auditable symbolic controller with stateful dual updates and action decomposition at the movement and phase levels.

**Contribution 3 — Separation.**
We prove and empirically verify finite-storage separation cases where local pressure and capacity-aware pressure select unsafe receiving movements, while the dynamic primal-dual controller avoids spillback propagation.

**Contribution 4 — Evidence.**
Under a pre-registered paired-seed locked protocol, the proposed controller improves finite-storage operating cost relative to max-pressure, capacity-aware pressure, and finite-storage double-pressure baselines in binding arterial regimes, with secondary evidence on delay, spillback, blocking, and unfinished vehicles.

这个版本保住了你想坚持的“理论创新比较强”，也为“效果超过 baselines”留出合理落点。

---

## 8. 我对当前仓库的最终判断

现在 v1.4 不应该再硬救。它完整执行了，但 closed-loop superiority 没过；仓库自己也明确说 claim 不允许。 继续在 v1.4 上调固定权重，大概率只是在 pressure family 附近小幅震荡。

真正应该做的是：

**开 v1.5，做方法论升级。**

核心不是“把 penalty 调大”，而是：

1. 用真实 link occupancy 建 finite-storage state；
2. 引入 stateful dynamic dual variables；
3. 加入 multi-hop spillback cascade price；
4. 加入 upstream release value；
5. 用 theory-aligned composite objective 做 primary endpoint；
6. 用 training/holdout split 防止 post-hoc；
7. 保留强 baseline 和 ablation，让结果真的硬。

如果这一版跑通，你的论文就不再是“pressure-equivalent symbolic recovery”，而可以变成：

> **Finite-storage dynamic primal-dual generalized pressure: pressure recovery in slack networks, provable separation under binding storage constraints, and locked closed-loop superiority over max-pressure-style baselines in finite-storage arterial regimes.**

[1]: https://github.com/Radar-Lei/pi_light_OR/commits/main/ "Commits · Radar-Lei/pi_light_OR · GitHub"
