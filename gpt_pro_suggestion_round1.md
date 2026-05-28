我认真看了。我的结论很明确：**仓库已经从“v1.5 方向建议”推进到“v1.5 已经实现、激活、训练筛选、失败诊断都做了”的阶段；但现在还不能写 strong closed-loop superiority。** 现在最大的 blocker 不是方法论不够新，也不是 storage/cascade/release 没激活，而是 **completion / unfinished-vehicle safety** 没解决。下一步不能继续堆 r115、r116 这种局部 guard；要把 completion safety 提升为方法论核心，开一个结构性新版本。

## 1. 我对当前仓库的总体判断

仓库现在的研究骨架是强的。README 仍然把研究问题定义为：能否把 capacitated traffic-network relaxation 的 movement-level dual sensitivities 变成 interpretable generalized-pressure principle，并压缩成 auditable symbolic policies。这个问题本身够强，也不是普通 SUMO heuristic。

但当前已经被 repo 自己锁死的一点是：**现有 proven evidence route 仍是 pressure-equivalent generalized-pressure symbolic recovery，不允许说 dual / v1.4 / 当前 v1.5 已经 closed-loop superior。** README 明确写了 v1.3/v1.4 Gate C 不支持 superiority over max-pressure-style baselines，而 active v1.5 方向是 vehicle-count occupancy、stateful storage/release/cascade/service shadow prices，并且必须对比 max-pressure、capacity-aware pressure、finite-storage double pressure、static v1.4 和 occupancy-aware ablations；这些 baselines 是 first-class，不是 strawmen。

最关键的新更新是：v1.5 不是还停留在想法。README 已经记录 v1.5 加了 occupancy-based finite-storage state、occupancy-aware capacity baseline、`finite_storage_dynamic_primal_dual_v1_5`、deterministic method gates、closed-loop diagnostics 和 locked holdout tooling；但 revised binding protocol 虽然激活了 storage/cascade/release mechanisms，early locked rows 触发了 safety-guard failures，因此 closed-loop superiority 仍然 disallowed。

所以一句话：

> **v1.5 的方法论方向是对的，也已经比 v1.4 更像一个真正 contribution；但当前性能证据还没过。下一步要做的是“completion-aware finite-storage primal-dual control”，而不是继续给当前 v1.5 打补丁。**

---

## 2. 当前最强的好消息：方法论机制已经站起来了

v1.4 最大问题是像 weighted pressure heuristic；v1.5 已经明显往真正方法论贡献前进。

`v1_5_dynamic_primal_dual_gates.json` 显示 deterministic method gates 是 `PASSED`，controller 是 `finite_storage_dynamic_primal_dual_v1_5`，并且四个核心机制都过了：slack pressure recovery、occupancy storage separation、cascade spillback separation、upstream release value。 这个很重要，因为它说明你不是只调权重，而是真的做出了：

1. slack regime 下退化为 pressure；
2. occupancy-based storage scarcity；
3. multi-hop cascade spillback；
4. upstream release value。

而且 occupancy-storage separation 的具体 gate 也比较有说服力：它明确检查 storage uses vehicle count、dynamic changes from pressure、queue ablation misses storage fullness、storage price active。 在该 case 里，pressure action 是 0，但 v1.5 finite-storage action 和 selected action 都变成 1，说明它不是纸面公式，而是真的能改变 action ranking。 对 phase 0 的 decomposition 也显示，虽然 pressure 分数高，但 downstream_storage、spillback、storage_price 把它压下去了；最终 action_changed_relative_to_pressure 为 true，changing terms 正是 downstream_storage、spillback、storage_price。 

closed-loop diagnostic 也证明机制激活不是只在 toy one-step gate 里发生。`v1_5_closed_loop_diagnostics.json` 是 `PASSED`；100 个 decisions 中有 55 个相对 pressure 改变，action-change rate = 0.55；binding decisions 中 action-change rate = 0.7556。 storage/spillback/storage_price/cascade_price/release 等动态项都有非零计数，criteria 也显示 binding state observed、action-change target met、storage/spillback terms active、dynamic terms active。

这部分可以成为你的 **method contribution** 核心。现在不是“没有创新”，而是“创新机制已经激活，但 closed-loop 完成率/unfinished safety 还没被理论和控制器共同处理好”。

---

## 3. 当前最硬的坏消息：性能证据还不能支持 strong claim

v1.4 已经完整执行，但 strict evidence 非 PASSED。README 明确说 v1.4 locked Gate C 执行了 1440/1440 rows，但 remained non-PASSED，closed-loop superiority 仍然 disallowed。 `.planning/STATE.md` 也记录 Phase 17 v1.4 locked execution completed 1440/1440 with clean row audit，但 strict Gate C remained non-PASSED，closed-loop superiority remains disallowed。

v1.5 原始 locked protocol 也被 superseded，因为 early rows 没有 storage-binding decisions；后来的 binding protocol 虽然通过 activation audit，但 paired evidence 仍是 `INCONCLUSIVE`，early holdout risk 是 `FAILED`，原因是 activation 后 strong baselines 上出现 repeated safety-guard harm。

这说明现在不能说：

> “我们的 v1.5 已经超过所有 baselines。”

也不能弱化成：

> “只要 composite 好一点就算赢。”

因为仓库自己的 safety-contract audit 明确不支持这么做。

---

## 4. 真正 blocker：不是 storage activation，而是 completion / unfinished safety

这是我看完 repo 后最重要的判断。

`v1_5_revision_candidate_summary.json` 显示：`NO_CANDIDATE_SELECTED`，`claim_ready=false`，candidate_count = 113，selected_candidate_count = 0，rejected_candidate_count = 112，completion_safety_blocker_count = 107。 这不是偶然一两个 seed 问题，而是系统性 blocker。

`v1_5_completion_safety_contract_audit.json` 更直接：45 个候选里，0 个 selected；27 个有 positive core composite signal，23 个同时有 positive composite 和 action separation，但 **0 个** 同时通过 unfinished safety guard；unfinished_safety_blocker_count = 43。 也就是说，你的方法经常能降低 composite cost，也经常能产生足够 action separation，但它会在 unfinished vehicles 上伤到 strong baselines。

这就是目前最核心的 tradeoff：

> **v1.5 storage/cascade/release 机制能改善有限存储运行成本，但它还没有学会在有限 horizon 下保护 vehicle completion。**

tradeoff analysis 也支持这个判断：107 个 analyzed training cases 中，75 个 unsafe，52 个 composite-win，24 个 safe-and-composite-win，33 个 core-baseline oracle conflicts。 典型例子是 r3：candidate composite beat all core baselines，但 unfinished safety 不安全，而且 unfinished oracle 和 composite oracle 发生冲突。 r10 也很典型：第一个 case safe 且 composite win，第二个 case composite 仍赢但 unfinished safety 又失败。

这就是为什么我不建议继续调 storage/cascade/release 的权重。问题不是这些项没用，而是 **你的 objective 和 controller 没有把 terminal completion feasibility 当成一等约束**。

---

## 5. r2–r114 的信号：继续堆 guard 会削弱 contribution

我还看了 controller registry 和训练候选路径。现在 `run_closed_loop_sumo.py` 里已经有从原始 `finite_storage_dynamic_primal_dual_v1_5` 到很多 r-variants 的长链，包含 guarded、double release、terminal flush、route completion、horizon model、baseline envelope、reactivated dual、release-risk horizon blend、negative-total/low-signal caps、unique finishable semantics 等一系列补丁。 

这说明你已经做了大量认真探索，但也有危险：如果论文最后主方法变成“第 114 个 guard 的组合”，审稿人会觉得它是 post-hoc engineering，而不是一个强 methodology contribution。

r114 也还不是解决方案。`v1_5_r114_training_selection.json` 里状态仍是 `REJECTED`，`claim_ready=false`，而且 input artifact 还是 `IN_PROGRESS`；row audit 只完成 24/324 rows，missing 300 rows。 r114 的 mechanism summary 显示 binding decision rate 很高，但 action_change_rate 只有 0.0557，同时 route-horizon completion filter 和多种 conflict guard 大量触发。 它在部分 early rows 上有 positive composite differences，但同一个 artifact 仍有 safety harms，并且 claim_scope 明确 closed_loop_superiority_claim_allowed = false。 

所以我的建议很坚决：

> **不要继续把 r115 做成“再加一个 cap / guard / threshold”。要停止这一条 patch chain，重新抽象成一个干净的新方法。**

---

# 你下一步应该怎么做

## Step 1：先把当前 v1.5 定性为“method-risk finding”，不要硬救当前 claim

你应该马上做一个小的 repo cleanup / milestone close，不是为了放弃，而是为了避免后面 claim 污染。

当前应该在 README / `.planning` / summary 里明确三件事：

1. v1.5 deterministic gates passed：方法机制成立。
2. v1.5 closed-loop diagnostic passed：storage/cascade/release 在 short SUMO 中确实激活。
3. v1.5 training / early holdout failed：completion / unfinished safety 没过，所以 superiority claim 不允许。

README 当前 next experiments 已经写得很对：把 current v1.5 binding rows 当作 method-risk finding，不是 superiority result；在 fresh training seeds 上重建 completion modeling 或 stronger completion-safety guard；未来 confirmatory paired-evidence 前必须重新 lock training protocol。

我建议你把这一步命名为：

> **v1.5 closeout: mechanism success, completion-safety failure, no superiority claim.**

这会保护你后面真正的强贡献。负结果不是包袱，它是新方法的动机。

---

## Step 2：新开 v1.6，不要叫 r115

我建议新方法名直接改成：

```text
finite_storage_completion_safe_primal_dual_v1_6
```

或者：

```text
completion-aware dynamic finite-storage primal-dual pressure
```

这个名字要传达一个清楚变化：**completion safety 不是 guard，不是 patch，而是 primal-dual relaxation 的一部分。**

现在的 v1.5 贡献是：

> storage / cascade / release shadow prices.

下一版贡献必须升级为：

> storage / cascade / release / terminal-completion shadow prices.

也就是说，理论里不要只写 finite-storage constraint，还要写 terminal completion / exit feasibility constraint。否则仿真里 unfinished vehicles 永远会成为 baselines 攻击你的点。

---

## Step 3：把 completion safety 写进理论，而不是写成 fallback

当前 r-chain 的问题是很多东西像 fallback：

* finite-storage-double fallback；
* capacity-aware lock；
* max-pressure terminal lock；
* completion envelope；
* pressure-safe horizon guard；
* negative-total cap；
* low-signal margin cap。

这些东西可以救局部 case，但不构成一个强 contribution。

我建议你重新写一个统一 score：

[
S_p(t)
======

S^{storage\text{-}dual}_p(t)
+
\lambda_c , C_p(t)
------------------

## \lambda_r , R_p(t)

\eta L(p,p_t)
]

其中：

[
S^{storage\text{-}dual}_p(t)
============================

\sum_{m=(i,j)\in p}
s_m(t)
[
q_i(t)-q_j(t)
+\alpha r_i(t)
-\beta \mu_j(t)
-\gamma \xi_j(t)
+\delta a_i(t)
]
]

新增的核心不是再调 (\alpha,\beta,\gamma)，而是：

[
C_p(t)
======

\text{completion value of vehicles that can still reach sink before horizon}
]

[
R_p(t)
======

\text{unfinished-risk / terminal-deficit risk under action }p
]

再引入 terminal completion dual：

[
\nu_\ell(t+1)
=============

\left[
(1-\rho_\nu)\nu_\ell(t)
+
\kappa_\nu
\left(
\widehat{d}^{exit}_\ell(t)
--------------------------

\widehat{s}^{exit}*\ell(t)
\right)*+
\right]_+
]

直观解释：

* (\mu_j)：下游 link storage scarcity；
* (\xi_j)：多跳 cascade spillback price；
* (r_i)：upstream release value；
* (\nu_\ell)：terminal completion / exit deficit price；
* (C_p(t))：当前 phase 对“能完成车辆”的贡献；
* (R_p(t))：当前 phase 可能造成 unfinished regression 的风险。

这样论文贡献就变成：

> **A completion-aware finite-storage primal-dual controller that recovers max-pressure in slack regimes, introduces storage/cascade/release shadow prices under binding finite-storage constraints, and adds terminal-completion dual prices to avoid finite-horizon unfinished-vehicle regressions.**

这比“v1.5 r114 guard stack”强很多。

---

## Step 4：重新设计 action selection：用“安全可行集 + primal-dual 最优”而不是事后 veto

我建议把控制器写成两层，但理论上是一体的。

第一层：构造 completion-safe feasible action set：

[
\mathcal{A}_{safe}(t)
=====================

{p:
\widehat{U}*p(t)
\le
\min*{b \in \mathcal{B}}
\widehat{U}_b(t)
+
\epsilon_U(t)
}
]

这里 (\widehat{U}_p(t)) 是选择 action (p) 后的 predicted unfinished risk；(\mathcal{B}) 是 core strong baselines 的候选动作集合，例如 max-pressure、capacity-aware、finite-storage double-pressure。注意：这不是“抄 baseline”，而是把 baselines 作为 safety certificate。

第二层：在 safe set 里选 dynamic finite-storage primal-dual score 最高的 action：

[
p^\star(t)
==========

\arg\max_{p \in \mathcal{A}_{safe}(t)}
S_p(t)
]

如果 (\mathcal{A}_{safe}) 为空，就 fail-closed 到一个预注册 baseline envelope，比如：

[
\arg\min_{b \in \mathcal{B}} \widehat{U}_b(t)
]

这比现在的各种 late lock / cap / veto 更干净。它也能形成理论贡献：

> **Safety-constrained generalized pressure:** pressure-style baselines define a completion-safety envelope, while finite-storage primal-dual prices optimize within that envelope.

这样你既保住强 baselines，又能解释为什么你的方法不是 baseline imitation：baseline 只定义安全域，真正的优化排序由 storage/cascade/release/completion dual 完成。

---

## Step 5：重新定义 v1.6 的 method gates

v1.6 不要一开始就跑 324-row training。先做 deterministic gates。建议新增这些 artifacts：

```text
experiments/dual_sensitivity/v1_6_completion_primal_dual_gates.json
experiments/dual_sensitivity/v1_6_completion_safety_state_audit.json
experiments/dual_sensitivity/v1_6_completion_separation_cases.json
```

必须至少有 5 个 gates：

1. **Pressure recovery gate**
   storage slack、completion slack 时，v1.6 与 max-pressure action 一致。

2. **Storage separation gate**
   下游 storage nearly full 时，v1.6 避免 pressure 会选的 unsafe receiving movement。

3. **Cascade separation gate**
   immediate downstream 看起来可用，但 downstream descendant 高 shadow price 时，v1.6 提前避开 cascade path。

4. **Release value gate**
   upstream occupancy 高且 downstream path 有 slack 时，v1.6 能释放 upstream queue，避免 upstream spillback。

5. **Terminal completion gate**
   两个 action 的 storage benefit 相近，但一个 action 会造成 terminal unfinished risk 时，v1.6 选择 completion-safe action。

第 5 个 gate 是现在仓库缺的核心。没有它，后面还是会陷入 composite win 但 unfinished harm。

---

## Step 6：重做 state schema，别让 completion proxy 再变成 patch

我建议新增或扩展这些 state fields：

```python
completion_state = {
    edge: {
        "vehicle_count": ...,
        "halting_queue": ...,
        "occupancy_ratio": ...,
        "residual_receiving_capacity": ...,
        "distance_to_exit": ...,
        "estimated_time_to_exit": ...,
        "remaining_horizon": ...,
        "finishable_vehicle_count": ...,
        "finishable_ratio": ...,
        "positive_pressure_support": ...,
        "path_min_residual_capacity": ...,
        "terminal_deficit_price": ...,
    }
}
```

并且要明确分工：

* pressure 用 halting queue；
* storage scarcity 用 vehicle count / occupancy；
* spillback 用 occupancy + blocking；
* release 用 upstream occupancy + downstream path slack；
* completion 用 finishable vehicle count、time-to-exit、remaining horizon、path capacity；
* terminal safety 用 predicted unfinished risk。

你已经从 r96–r114 里发现了 route-horizon / finishable counting 的细节问题，例如 duplicate movement、finishable volume inflated、low-signal completion bonus 等。不要把这些散落在 guard 名字里；要把它们整理成一个 **completion_state semantics**。这会显著增强论文可信度。

---

## Step 7：训练协议要保留强 baselines，但换成“先选候选，再锁 holdout”

当前仓库的 baseline 体系很好，不能弱化。`run_closed_loop_suite.py` 里 required strong baselines 包括 fixed_time、actuated_local_pressure、max_pressure、capacity_aware_pressure、cycle_pressure、finite_storage_double_pressure、finite_storage_primal_dual。 默认 controller list 已经包含 occupancy_capacity_aware_pressure、finite_storage_primal_dual_v1_4_score、finite_storage_dynamic_primal_dual_v1_5。 stress scenarios 也覆盖 downstream blockage、spillback stress、incident capacity drop、oversaturation、turning shock、switching-loss-sensitive 等。

v1.6 training selection 建议这样做：

### Training Stage A：12-row fast screen

目标不是 claim，只是排除明显坏候选。

必须满足：

* action separation ≥ 5%，最好 10–25%；
* binding action changes 集中在 high occupancy / low receiving capacity / high terminal risk states；
* no catastrophic unfinished harm；
* composite signal 不得对全部 core baselines 为负。

### Training Stage B：full 324-row training

候选必须同时满足：

* composite (J) 对 core strong baselines 的 mean improvement 为正；
* unfinished vehicles 不超过预注册 safety tolerance；
* delay / penalized travel time 无 practical harm；
* action separation 不能 collapse 到 pressure-equivalent；
* mechanism activation 不只靠 terminal fallback，而要有 storage/cascade/release/completion dual 的实际贡献。

当前 safety audit 已经明确：现有证据不支持 weakening unfinished guard；它建议不要 lock confirmatory holdout，下一步应 rebuild completion modeling，而不是再加 marginal horizon filter。 所以 v1.6 初始仍应保持强 safety contract；只有当你有 calibration evidence 证明 1-vehicle tolerance 是 simulation noise 或 censoring artifact，才能预注册 practical margin。

### Training Stage C：candidate selection

只有一个候选能进入 holdout。不要让 r2–r114 这种长链继续污染 final protocol。

selection artifact 应该长这样：

```json
{
  "experiment": "v1_6_training_selection",
  "status": "SELECTED",
  "controller_id": "finite_storage_completion_safe_primal_dual_v1_6",
  "claim_ready": false,
  "training_only": true,
  "passes_core_composite": true,
  "passes_unfinished_safety": true,
  "passes_action_separation": true,
  "passes_mechanism_activation": true,
  "holdout_lock_allowed": true
}
```

注意：training selection 也不能 claim superiority，只能允许 lock holdout。

---

## Step 8：confirmatory holdout 必须换 fresh seeds，不能复用当前 failed holdout

`.planning/STATE.md` 已经写明：不能在 current binding holdout seeds 上调参，再复用同一个 protocol 当 confirmatory evidence。 这一点必须坚持。

v1.6 holdout 应该：

* fresh seeds；
* fresh protocol fingerprint；
* protocol 在 training selection 后冻结；
* candidate 固定；
* baselines 固定；
* objective weights 固定；
* safety thresholds 固定；
* no mid-run candidate editing。

否则就算结果好，也容易被审稿人认为是 post-hoc tuning。

---

## Step 9：主 claim 要强，但必须定义成“大部分目标场景超过所有 strong baselines”

你想要“至少大部分场景超过所有 baselines”，这是合理目标，但要写得精确。不要写 universal dominance。建议主 claim 写成：

> In finite-storage binding regimes, the proposed completion-aware dynamic finite-storage primal-dual controller reduces pre-registered composite operating cost relative to max-pressure, capacity-aware pressure, occupancy-capacity-aware pressure, finite-storage double pressure, and static finite-storage ablations on most locked paired-seed holdout scenarios, while satisfying pre-registered unfinished-vehicle and delay safety guards.

这句话比“beats baselines”强，因为它包含：

* finite-storage binding regimes；
* completion-aware dynamic finite-storage primal-dual；
* pre-registered composite objective；
* strong baselines；
* most locked scenarios；
* unfinished/delay safety guards。

我建议 holdout pass 条件这样设：

1. **Primary pass**：在每个 scenario group 内，v1.6 对每个 core baseline 的 paired composite (J) mean improvement 为正；至少 70–80% scenario × demand groups 为正。
2. **Strong pass**：对 max-pressure、capacity-aware、finite-storage double-pressure 三个 core baselines，至少大部分 binding scenarios 达到 practical improvement。
3. **Safety pass**：unfinished vehicles、penalized travel time、total delay 不出现 practical harm。
4. **Mechanism pass**：action differences 主要发生在 storage-binding / cascade-risk / completion-risk states，而不是随机抖动。
5. **Ablation pass**：full v1.6 优于 no-completion、no-cascade、no-release、static v1.4，证明不是某一个 baseline envelope 在起作用。

---

## Step 10：论文 contribution 重新写成 4 个强贡献

你现在最适合的贡献表述不是“dual beats pressure”，而是下面这个版本：

**Contribution 1 — Theory.**
A completion-aware finite-storage primal-dual generalized-pressure principle for traffic signal control. It recovers max-pressure in slack regimes and introduces storage-scarcity, cascade-spillback, upstream-release, and terminal-completion shadow prices when constraints bind.

**Contribution 2 — Algorithm.**
An auditable symbolic controller that maintains stateful shadow prices and selects actions by optimizing finite-storage primal-dual pressure inside a completion-safety envelope.

**Contribution 3 — Separation.**
Formal separation cases showing that local pressure, capacity-aware pressure, and finite-storage double pressure can select actions that are storage-safe but completion-unsafe, or completion-safe but spillback-unsafe, while the proposed controller resolves the tradeoff through dual prices.

**Contribution 4 — Evidence.**
A pre-registered paired-seed locked protocol against max-pressure, capacity-aware pressure, occupancy-capacity-aware pressure, finite-storage double pressure, static v1.4, and ablations, demonstrating improvements in most finite-storage binding scenarios while satisfying unfinished-vehicle safety guards.

这才是你要的“一个强一个强的 contribution”。

---

# 我建议你马上执行的具体清单

## 立即停止

1. 不要把当前 r114 或 r115 当主方法。
2. 不要 lock confirmatory holdout。
3. 不要 weaken unfinished safety guard 来救当前 candidates。
4. 不要删除或弱化 strong baselines。
5. 不要写“v1.5 已经 closed-loop superior”。

## 立刻做

1. 新建 `v1.6_completion_safe_primal_dual` milestone。
2. 写 `v1_5_closeout_method_risk.md`：机制成功、completion safety 失败、claim 不允许。
3. 新增 completion-state schema 和 deterministic completion gate。
4. 把 route-horizon / finishable semantics 从 r96–r114 的 patch chain 整理成一个干净模型。
5. 实现 `finite_storage_completion_safe_primal_dual_v1_6`，不要叫 r115。
6. 先跑 deterministic gates，再跑 12-row screen，再跑 324-row training。
7. 只有 training selection `PASSED` 后，才 lock fresh holdout。

## 建议的新 artifact 路线

```text
experiments/dual_sensitivity/v1_5_closeout_method_risk.md
experiments/dual_sensitivity/v1_6_completion_primal_dual_theory_cases.json
experiments/dual_sensitivity/v1_6_completion_state_audit.json
experiments/dual_sensitivity/v1_6_completion_primal_dual_gates.json
experiments/dual_sensitivity/v1_6_training_protocol.json
experiments/dual_sensitivity/v1_6_training_execution.json
experiments/dual_sensitivity/v1_6_training_selection.json
experiments/dual_sensitivity/v1_6_locked_holdout_protocol.json
experiments/dual_sensitivity/v1_6_locked_holdout_execution.json
experiments/dual_sensitivity/v1_6_paired_evidence.json
```

最终判断：**这篇还值得冲强 contribution，但必须把“completion-aware finite-storage primal-dual”作为新核心。** v1.5 已经证明 storage/cascade/release 机制能激活；现在要证明它不会为了 storage objective 牺牲 completion。只要这一步做通，你的方法才有机会在大部分 finite-storage binding 场景下真正超过所有 strong baselines，而不是只在 composite 上局部赢、在 unfinished safety 上被 repo 自己否掉。
