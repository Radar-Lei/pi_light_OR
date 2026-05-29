According to a document from 2026-05-28, 我同意你现在的判断：**先别写论文，先把 performance 真正打出来。** 当前仓库最核心的问题不是“没有方法创新”，而是 **storage/cascade/release 机制已经有用，但它还没有稳定地转化成对 strong baselines 的 closed-loop win，尤其在 unfinished / completion safety 上会被 baselines 抓住。** 文档里已经明确记录：v1.5 不是方法论不够新，而是 completion / unfinished-vehicle safety 没解决；下一步不能继续堆 r115/r116 这种 guard，而要把 completion safety 升级为方法论核心。

我的建议很明确：**不要把下一版叫 r115。开一个性能导向的新主方法：Completion-aware finite-storage primal-dual model-predictive pressure，或者 v1.7 / v2.0。目标不是“稍微修 guard”，而是让每一个 deviation from max-pressure 都有可解释、可预测、可审计的 positive advantage。**

---

# 1. 先确认失败模式：你不是“完全没赢”，而是“赢 composite 时输 completion”

当前 evidence 对我们其实很有启发。v1.5 里 113 个 candidate 没有选中，107 个被 completion safety 卡住；completion audit 中 45 个候选 0 个 selected，虽然 27 个有 positive core composite signal、23 个同时有 positive composite 和 action separation，但 0 个通过 unfinished safety guard。也就是说，方法并不是完全没有性能信号，而是 **它能改善 finite-storage composite cost，但经常牺牲 terminal completion / unfinished vehicles。** 

这意味着下一步不该继续调 (\alpha,\beta,\gamma) 的 storage/cascade/release 权重。问题不是 storage terms 没用，而是 **objective 里没有把 terminal completion feasibility 作为一等约束。** 文档也明确说，继续堆 guard 会削弱 contribution，因为 r-chain 已经变成 guarded、double release、terminal flush、route completion、baseline envelope、reactivated dual、low-signal caps 等补丁链；这会让主方法看起来像 post-hoc engineering。

所以性能突破点是：

> **从 “storage-aware pressure + completion guard” 改成 “completion-constrained finite-storage primal-dual control”。**

---

# 2. 主方法建议：CFS-PD-MPC，而不是单步 score

我建议下一版主方法叫：

> **CFS-PD-MPC: Completion-aware Finite-Storage Primal-Dual Model-Predictive Pressure**

它不是普通 MPC，也不是普通 pressure。它的结构是：

[
\text{finite-storage dual prices}
+
\text{terminal completion dual prices}
+
\text{short-horizon rollout}
+
\text{baseline-envelope safe policy improvement}
]

核心 scoring 不再是：

[
score = pressure + storage + spillback + release + switching
]

而是：

[
Q_H(p \mid x_t)
===============

g(x_t,p)
+
\widehat V_{H-1}(\widehat x_{t+\Delta}(p))
]

其中 immediate cost / reward 可以写成：

[
g(x_t,p)
========

*

\Big[
J^{delay}_p
+
\lambda_s J^{spillback}_p
+
\lambda_b J^{blocking}_p
+
\lambda_u J^{unfinished-risk}_p
+
\lambda_l J^{switching}_p
\Big]
]

再把 dual-pressure decomposition 放进去：

[
S^{PD}_p(t)
===========

\sum_{m=(i,j)\in p}
s_m(t)
[
q_i(t)-q_j(t)
+\alpha r_i(t)
-\beta \mu_j(t)
-\gamma \xi_j(t)
+\delta a_i(t)
+\omega \nu_i(t)
]
-\eta L(p,p_t)
]

这里：

* (\mu_j(t))：downstream storage scarcity price；
* (\xi_j(t))：multi-hop cascade spillback price；
* (r_i(t))：upstream release value；
* (a_i(t))：service age / starvation；
* (\nu_i(t))：terminal completion deficit price；
* (L(p,p_t))：switching lost time；
* (H)：短视野，建议先试 (H=2) 或 (H=3)，不要一开始做很重的 full MPC。

你当前已有文档已经建议引入 (C_p(t))、(R_p(t)) 和 terminal completion dual (\nu_\ell)，也就是让 completion value 和 unfinished risk 成为 score 的核心，而不是后置 fallback。

---

# 3. 最关键改动：用 baseline envelope 做 safe policy improvement

如果你想“至少大部分场景超过 Max Pressure”，最稳的办法不是每一步都和 MP 对着干，而是：

> **只有当模型预测当前动作相对 baseline envelope 有 positive advantage 时才偏离 baseline；否则回到 baseline envelope。**

定义强 baseline 集合：

[
\mathcal B
==========

{
\text{max-pressure},
\text{capacity-aware pressure},
\text{finite-storage double pressure},
\text{occupancy-aware pressure},
\text{delay-based MP},
\text{switching-loss MP}
}
]

每个 baseline 在当前状态下给出一个候选 phase (p_b(t))。然后先构造 completion-safe feasible set：

[
\mathcal A_{\text{safe}}(t)
===========================

\left{
p:
\widehat U_H(p)
\le
\min_{b\in \mathcal B}\widehat U_H(p_b)
+
\epsilon_U
\right}
]

其中 (\widehat U_H(p)) 是短视野预测出来的 unfinished risk。

然后在 safe set 里选：

[
p^\star(t)
==========

\arg\min_{p\in \mathcal A_{\text{safe}}(t)}
\widehat J_H(p)
]

如果 safe set 为空，就 fail-closed 到：

[
p^\star(t)
==========

\arg\min_{b\in\mathcal B}
\widehat J_H(p_b)
]

这个设计很重要。它既不会被审稿人说“你弱化 baseline”，也不会变成 baseline imitation。因为 baseline 只定义 **safety certificate / feasible envelope**，真正的优化排序仍由 finite-storage primal-dual + completion dual + rollout value 完成。文档里也已经建议这种“两层但理论上一体”的 action selection：先构造 completion-safe feasible set，再在 safe set 内优化 primal-dual score。

这会显著提高 performance 站得住脚的概率，因为你的方法不再随机冒险，而是做 **safe policy improvement over strong baselines**。

---

# 4. 具体怎么提高超过 Max Pressure 的概率

## 4.1 不要试图在 slack regime 赢 Max Pressure

在 slack / non-binding 场景下，Max Pressure 本来就很强，甚至理论上有 throughput-optimal 传统。你的方法在 slack regime 应该 **recover MP**，不要追求赢它。最新 repo README 也明确说当前 proven evidence route 是 pressure-equivalent generalized-pressure symbolic recovery，不能写 universal dual-over-pressure dominance；active direction 是在 finite-storage / binding regime 中用 occupancy、shadow prices 和 strong baselines 比较。([GitHub][1])

所以实验场景要预注册为：

> **finite-storage binding regimes**：下游接近满、spillback cascade risk、incident capacity drop、oversaturation、turning shock、completion-critical terminal horizon。

这不是 cherry-picking，而是方法适用域。你要写的是：

> We recover Max Pressure in slack regimes and improve over it when finite-storage and completion constraints bind.

## 4.2 把 deviation from MP 变成“优势触发”，不是固定权重触发

当前 v1.5 有 action separation，但仍会带来 unfinished harm。下一版每次偏离 MP 前都要回答：

[
\Delta_H(p)
===========

## \widehat J_H(p_{MP})

\widehat J_H(p)
]

只有当：

[
\Delta_H(p) > \tau_{\text{adv}}
]

并且 completion safety 通过时，才允许选非 MP 动作。否则保持 MP 或 baseline envelope。

这叫 **advantage-gated generalized pressure**。它可以大幅减少“看起来 storage 更好但最终 unfinished 变差”的错误。

## 4.3 用短视野 rollout 修复 unfinished vehicles

当前 v1.5 的根本问题是 finite horizon 下 completion 没建模。你应该做一个非常轻量的 link-level rollout，不需要复杂仿真：

[
n_\ell(t+\Delta)
================

n_\ell(t)
+
in_\ell(t,p)
------------

out_\ell(t,p)
]

[
out_{i\to j}(t,p)
=================

\min
{
q_i(t),
s_{ij}\Delta,
C_j-n_j(t)
}
]

再用 remaining horizon 估计 finishable vehicles：

[
F_\ell(t)
=========

n_\ell(t)\cdot
\mathbf 1[
\widehat \tau_{\ell\to sink}(t)
\le
T-t
]
]

terminal risk：

[
U_H(p)
======

\sum_\ell
\left[
F_\ell^{baseline}(t+H)
----------------------

F_\ell^{p}(t+H)
\right]_+
]

这样就能把 unfinished vehicles 从“仿真结束后才发现的问题”变成“每个 action 之前可预测的问题”。

## 4.4 把 storage 和 completion 做成双目标，不要只让 storage 压过 pressure

你现在需要的是 constrained optimization：

[
\min_p
\widehat J^{storage}_H(p)
]

subject to：

[
\widehat U_H(p)
\le
\widehat U_H(\text{baseline envelope})+\epsilon_U
]

也就是说：

* storage/cascade/release 用来赢；
* completion constraint 用来不输；
* switching/coordination 用来避免被新 MP variants 打败。

这比单一 composite 更安全。Composite 可以作为 reporting metric，但 action selection 应该先过 completion constraint。

---

# 5. 再加一层：regime-switching，不要一个公式打天下

一个 controller 想在所有场景赢所有 baseline 很难。更现实也更 OR 的方式是做 **auditable regime-switching policy**：

[
\pi(x)
======

\begin{cases}
\pi_{MP}, & \text{slack regime}\
\pi_{storage}, & \text{storage-binding regime}\
\pi_{cascade}, & \text{cascade-risk regime}\
\pi_{completion}, & \text{terminal-completion regime}\
\pi_{coordination}, & \text{platoon / progression regime}
\end{cases}
]

每个 regime 都有明确 threshold：

* slack：所有 downstream occupancy < 0.65，completion risk low；
* storage-binding：任一下游 occupancy > 0.80；
* cascade-risk：descendant occupancy price (\xi_\ell) high；
* completion-critical：remaining horizon / ETA ratio low；
* coordination/platoon：upstream moving platoon speed high、queue not fully stopped。

这样你可以解释为什么方法在不同场景下偏离 MP，并且可以做 ablation：

* no-completion；
* no-cascade；
* no-release；
* no-coordination；
* no-MPC-rollout；
* no-baseline-envelope。

这会让 performance result 更容易站得住脚，因为审稿人能看到“为什么赢”。

---

# 6. 必须加入更强 baselines，不然 Transportation Science 审稿人会问

你现在已有 `max_pressure`、`capacity_aware_pressure`、`finite_storage_double_pressure`、`occupancy_capacity_aware_pressure`，这是对的。文档也强调 baselines 不能弱化，而且 required strong baselines 已经包括 max pressure、capacity-aware pressure、finite-storage double pressure、finite-storage primal-dual 等。

但如果目标是 Transportation Science，我建议主文或 appendix 加这些更强/更新 baseline：

## Main OR baselines

1. **Original Max Pressure / Backpressure**
   主 baseline，必须保留。

2. **Capacity-aware Backpressure / Capacity-aware Pressure**
   这是 finite capacity 相关的强对手。早期 capacity-aware back-pressure 文献已经指出普通 back-pressure 在 finite capacities 下会有问题，并提出 capacity-aware correction。([Hal Science][2])

3. **Finite-storage Double Pressure**
   你已有，必须保留。它是你方法最直接的 finite-storage 对照。

4. **Occupancy-aware Max Pressure**
   这是为了避免审稿人说：“你只是因为 baseline 没看 occupancy 才赢。”

5. **Delay-based Max Pressure**
   Liu 和 Gayah 的 delay-based MP 明确针对 original vehicle-count MP 的不足，并在多种 simulation tests 中优于 benchmark MP variants；这会是很强的 practical MP baseline。([科学直通车][3])

6. **Max Pressure with Phase-Switching Loss**
   Wang 等 2022 的 TRC 工作把 phase switching loss 纳入 max-pressure framework，并证明相关 throughput-optimal 性质；如果你的方法有 switching term，必须和这个方向对比。([科学直通车][4])

7. **Smoothing-MP**
   2024 TRC 的 Smoothing-MP 专门考虑 signal coordination，同时保留 max-pressure 稳定区域，并报告 travel time / delay 改善；如果你做 arterial / corridor，必须考虑这个 baseline 或至少讨论。([科学直通车][5])

8. **C-MP / Coordinated Max Pressure**
   2025 TRB 的 C-MP 是 decentralized adaptive-coordinated MP，用 upstream/downstream vehicle counts 和 space-mean-speed 检测 platoons 与 downstream space；这是非常 relevant 的新强 baseline。([科学直通车][6])

9. **Finite-storage MPC baseline**
   用小网络或 arterial 上的 rolling-horizon finite-storage MPC 作为 “strong OR oracle-ish baseline”。MPC 文献明确指出 finite storage 下 MP 可能造成 spillback，因为传统 MP 不考虑 finite storage，并提出带 constraints 的 rolling-horizon / MPC 思路。([美国能源部科学技术信息办公室][7])

## RL baselines 放 appendix 或 secondary，不要当主战场

你可以加 PressLight、CoLight、MPLight、IDQN 作为 robustness。LibSignal 提供跨 simulator 的 TSC benchmark，并支持 SUMO / CityFlow 和多种 benchmark datasets，适合作为 appendix benchmark 框架。([GitHub][8]) PressLight 本身是 “learning max-pressure control” 的代表，重交通下曾显示相对 baselines 的优势。([Faculty of IST][9])

但你的论文目标偏 OR，我建议主文主要打 OR / MP / MPC baselines，RL 放 secondary。

---

# 7. 实验评价要改：不是每个 cell 都必须赢，而是 primary claim 要硬

你想要“大部分场景超过 Max Pressure”，我建议这样定义 pass，不要让 200+ 个碎指标把自己锁死。

文档里也建议：holdout primary pass 应该要求每个 scenario group 内 v1.6 对每个 core baseline 的 paired composite (J) mean improvement 为正，并且至少 70–80% scenario × demand groups 为正；同时 unfinished、penalized travel time、delay 不出现 practical harm，action differences 要集中在 storage/cascade/completion-risk states。

我建议正式写成：

**Primary endpoint**

[
J
=

\text{delay}
+
\lambda_u \cdot \text{unfinished}
+
\lambda_s \cdot \text{spillback/blocking}
+
\lambda_l \cdot \text{switching lost time}
]

**Primary pass**

* 相比 `max_pressure`，至少 75% 的 locked finite-storage binding scenario × demand groups 上 (J) 改善；
* 相比每个 core baseline，mean paired (J) improvement 为正；
* 相比 best single baseline 或 baseline envelope，aggregate (J) 不输，最好正改善。

**Safety pass**

* unfinished vehicles 不得超过 baseline envelope practical margin；
* penalized travel time / total delay 不得出现 practical harm；
* 若有 1-vehicle unfinished difference，必须用 censoring / horizon calibration 证明它是噪声，不能直接放宽。

**Mechanism pass**

* action separation 不能 collapse 到 MP；
* 非 MP action 必须主要发生在 high occupancy、low receiving capacity、cascade risk、completion-critical states；
* full method 必须优于 no-completion、no-cascade、no-release、no-rollout、no-envelope ablations。

这样写，结论可以很强：

> 在 finite-storage binding regimes 中，我们在 most locked paired-seed scenarios 上超过 Max Pressure 和 strong MP variants，同时没有 completion / delay safety harm。

这比“到处赢”更可信，也更容易过审。

---

# 8. 训练目标要从“调权重”改成“minimax regret against baselines”

下一步参数选择不要再是“哪个 r 版本看起来好”。改成一个清楚的 training optimization：

[
\min_{\theta}
\sum_{s\in \mathcal S_{train}}
\max_{b\in \mathcal B}
\left[
J(\pi_\theta,s)-J(b,s)
\right]*+
+
\lambda_U
\left[
U(\pi*\theta,s)-\min_b U(b,s)-\epsilon_U
\right]_+
]

这个目标的意思是：

* 不是只赢 MP；
* 不是只赢 capacity-aware；
* 是尽量降低相对 **最强 baseline envelope** 的 regret；
* 同时把 unfinished safety 作为 hard-ish penalty。

这会比普通 grid search 更贴合你的目标：“performance 上能站住脚”。

参数搜索可以仍然很 OR / audit-friendly：

* Latin hypercube / grid over pre-registered ranges；
* 每个 candidate 输出 score decomposition；
* 只在 training seeds 上选一个；
* holdout fresh seeds；
* no mid-run editing。

不要用 failed holdout seeds 继续调参。文档已经强调，confirmatory holdout 必须换 fresh seeds，protocol、candidate、baselines、objective weights 和 thresholds 都要在 training selection 后冻结。

---

# 9. 具体实现清单

我会按这个顺序改仓库。

## A. 新增 completion-state schema

不要再让 completion proxy 散落在各种 r-variant guard 里。新增统一结构：

```python
completion_state[edge] = {
    "vehicle_count": n_edge,
    "halting_queue": q_edge,
    "occupancy_ratio": n_edge / capacity_edge,
    "residual_receiving_capacity": capacity_edge - n_edge,
    "distance_to_exit": dist_to_sink_edge,
    "estimated_time_to_exit": eta_edge,
    "remaining_horizon": T - t,
    "finishable_vehicle_count": finishable_edge,
    "finishable_ratio": finishable_edge / max(n_edge, 1),
    "path_min_residual_capacity": min_residual_on_path,
    "terminal_deficit_price": nu_edge,
}
```

文档也建议了类似 schema，并明确分工：pressure 用 halting queue，storage 用 vehicle count / occupancy，spillback 用 occupancy + blocking，completion 用 finishable count / time-to-exit / horizon / path capacity，terminal safety 用 predicted unfinished risk。

## B. 新增短视野 fluid rollout

先不要做复杂 exact SUMO rollout。实现 deterministic approximate rollout：

```python
def rollout_state(x, action, H):
    for h in range(H):
        send = min(queue_upstream, saturation * dt)
        receive = max(capacity_downstream - vehicle_count_downstream, 0)
        flow = min(send, receive)
        update queues, vehicles, occupancy, completion_state
    return predicted_state
```

每个 phase 都 roll out 一遍，算：

```python
predicted_J_H[action]
predicted_unfinished_risk_H[action]
predicted_spillback_risk_H[action]
```

## C. 实现 baseline-envelope actions

每步拿到：

```python
baseline_actions = {
    "max_pressure": a_mp,
    "capacity_aware_pressure": a_cap,
    "finite_storage_double_pressure": a_fsd,
    "occupancy_capacity_aware_pressure": a_occ,
    "delay_based_mp": a_delay,
    "switching_loss_mp": a_switch,
}
```

然后：

```python
safe_actions = [
    a for a in all_phases
    if U_hat[a] <= min(U_hat[b] for b in baseline_actions.values()) + eps_u
]
selected = argmin(J_hat[a] for a in safe_actions)
```

## D. Advantage gate

只偏离 baseline envelope 当：

```python
advantage = J_hat[best_baseline_action] - J_hat[selected]
if advantage < tau_adv:
    selected = best_baseline_action
```

这会大幅降低“为了 action separation 而 action separation”的风险。

## E. 加 regime tag 到每个 decision log

每次决策输出：

```json
{
  "regime": "storage_binding | cascade_risk | completion_critical | slack | coordination",
  "selected_action": ...,
  "mp_action": ...,
  "baseline_envelope_action": ...,
  "predicted_advantage": ...,
  "predicted_unfinished_margin": ...,
  "dual_components": {
    "pressure": ...,
    "storage_price": ...,
    "cascade_price": ...,
    "release_price": ...,
    "completion_price": ...,
    "switching_loss": ...
  }
}
```

没有这个，审稿人不会相信性能改善来自方法机制。

---

# 10. 新 artifact 路线

我建议不要继续污染 v1.5 r-chain。直接开：

```text
experiments/dual_sensitivity/v1_7_cfs_pd_mpc_state_audit.json
experiments/dual_sensitivity/v1_7_cfs_pd_mpc_theory_cases.json
experiments/dual_sensitivity/v1_7_cfs_pd_mpc_rollout_sanity.json
experiments/dual_sensitivity/v1_7_cfs_pd_mpc_baseline_envelope_audit.json
experiments/dual_sensitivity/v1_7_training_protocol.json
experiments/dual_sensitivity/v1_7_training_execution.json
experiments/dual_sensitivity/v1_7_training_selection.json
experiments/dual_sensitivity/v1_7_locked_holdout_protocol.json
experiments/dual_sensitivity/v1_7_locked_holdout_execution.json
experiments/dual_sensitivity/v1_7_paired_evidence.json
experiments/dual_sensitivity/v1_7_ablation_evidence.json
```

你的文档已经建议了类似路线：先新增 completion-state schema 和 deterministic completion gate，实现 `finite_storage_completion_safe_primal_dual_v1_6`，先跑 deterministic gates，再跑 12-row screen、324-row training，training selection 通过后再 lock fresh holdout。

我建议在这个基础上再加两项：**rollout sanity** 和 **baseline envelope audit**。因为你现在要的不是“method gates passed”，而是“performance 上能赢”。

---

# 11. Ablation 要设计成能证明“为什么赢”

最终至少要有这些 ablations：

1. **Full CFS-PD-MPC**
2. no-completion dual
3. no-baseline-envelope
4. no-rollout，退化成 one-step score
5. no-cascade
6. no-release
7. no-switching-loss
8. no-regime-switching
9. static v1.4 score
10. dynamic v1.5 no-completion

你要证明：

* no-completion 会重新出现 unfinished harm；
* no-rollout 会在 finite horizon 上输；
* no-envelope 会更 aggressive，但 safety 下降；
* no-cascade 在 spillback stress 上输；
* no-release 在 upstream spillback 上输；
* static v1.4 只是 weighted pressure，性能不稳。

这会让 strong performance claim 更可信。

---

# 12. 我建议的最终主结果表

不要只放平均值。放下面这种表：

| Scenario group           |    Binding type | Win vs MP | Win vs cap-aware | Win vs FSDP | Win vs best baseline | Safety pass | Mechanism tag      |
| ------------------------ | --------------: | --------: | ---------------: | ----------: | -------------------: | ----------: | ------------------ |
| downstream blockage      |         storage |         + |                + |           + |                  +/0 |        pass | storage/completion |
| spillback stress         |         cascade |         + |                + |           + |                    + |        pass | cascade            |
| incident capacity drop   | storage+cascade |         + |                + |         0/+ |                  0/+ |        pass | cascade/release    |
| oversaturation           |      completion |         + |                + |           + |                    + |        pass | completion         |
| turning shock            |         release |         + |              0/+ |           + |                  0/+ |        pass | release            |
| switching-loss-sensitive |       switching |         + |                + |         0/+ |                  0/+ |        pass | switching          |

再给一张 aggregate：

* % scenario × demand × seed groups with (J) improvement vs MP；
* mean paired improvement vs each baseline；
* worst-case regret vs baseline envelope；
* unfinished harm count；
* action separation rate；
* fraction of deviations with positive predicted advantage；
* calibration error of predicted (\widehat J_H)。

---

# 13. 最现实的 performance target

我建议你把 internal target 设成：

1. **vs Max Pressure**：locked binding groups 中 75–85% 正改善；
2. **vs Capacity-aware / FSDP**：60–75% 正改善；
3. **vs baseline envelope**：aggregate non-worse，部分场景正改善；
4. **safety**：unfinished / delay no practical harm；
5. **ablation**：full method 显著优于 no-completion 和 no-rollout。

如果 full method 连 baseline envelope 都显著超过，那就是非常强。若只是超过 MP 和大部分 strong variants，但和 envelope 打平，也仍然能写：

> The method achieves most of the improvement of the best baseline envelope with a single auditable primal-dual controller and improves over each individual pressure-style baseline in most finite-storage binding regimes.

这也很有价值。

---

# 14. 最后给你一个非常具体的下一步路线

现在不要写论文正文。按下面做：

1. **close v1.5**：记录 mechanism success + completion safety failure，不要再叫 r115。
2. **实现 completion_state**：finishable count、ETA、remaining horizon、path residual capacity、terminal deficit price。
3. **实现 H=2/H=3 fluid rollout**：每个 phase 预测 (J_H)、unfinished risk、spillback risk。
4. **实现 baseline envelope**：MP、capacity-aware、FSDP、occupancy-aware、delay-based MP、switching-loss MP。
5. **实现 advantage gate**：只有预测优势超过阈值且 safety margin 通过才偏离 baseline envelope。
6. **做 deterministic gates**：pressure recovery、storage separation、cascade separation、release separation、terminal completion separation、rollout calibration sanity。
7. **跑 12-row screen**：目标是 no catastrophic unfinished harm + positive signal vs MP。
8. **跑 full training selection**：minimax regret against baselines。
9. **lock fresh holdout**：只允许一个 selected candidate。
10. **加 Smoothing-MP、C-MP、finite-storage MPC 作为 stronger baselines / robustness**。

我的最终判断是：

> **要超过 Max Pressure 和其他 strong baselines，你需要的不是更激进的 storage dual，而是更保守、更聪明的 safe policy improvement：在 slack 时像 MP，在 completion-critical 时不输 baseline envelope，在 finite-storage binding 时用 storage/cascade/release dual 找到 baseline 看不到的改善空间。**

这条路线同时保留 OR 方法创新和 performance 可站立性。现在真的应该先做这个，而不是开始写论文。

[1]: https://github.com/Radar-Lei/pi_light_OR "GitHub - Radar-Lei/pi_light_OR · GitHub"
[2]: https://hal.science/hal-00865966/file/capacity-aware-back-pressure-traffic-signal-control.pdf?utm_source=chatgpt.com "Capacity-aware back-pressure traffic signal control"
[3]: https://www.sciencedirect.com/science/article/abs/pii/S0968090X22002303?utm_source=chatgpt.com "A novel Max Pressure algorithm based on traffic delay"
[4]: https://www.sciencedirect.com/science/article/abs/pii/S0968090X22001139?utm_source=chatgpt.com "Learning the max pressure control for urban traffic ..."
[5]: https://www.sciencedirect.com/science/article/abs/pii/S0968090X2400281X?utm_source=chatgpt.com "Smoothing-MP: A novel max-pressure signal control ..."
[6]: https://www.sciencedirect.com/science/article/abs/pii/S0191261525001572?utm_source=chatgpt.com "C-MP: A decentralized adaptive-coordinated traffic signal ..."
[7]: https://www.osti.gov/servlets/purl/1995694?utm_source=chatgpt.com "Model Predictive Control for Urban Traffic Signals with ..."
[8]: https://github.com/DaRL-LibSignal/LibSignal?utm_source=chatgpt.com "MLJ: Libsignal: an open library for traffic signal control"
[9]: https://faculty.ist.psu.edu/jessieli/Publications/2019-KDD-presslight.pdf?utm_source=chatgpt.com "PressLight: Learning Max Pressure Control to Coordinate ..."
