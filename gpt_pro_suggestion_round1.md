According to a document from 2026-05-28, 你的判断是对的：**现在仍然没有达到“在大部分场景下胜过所有 strong baselines”的目标。** 结合我刚查到的 2026-05-29 仓库状态，最新进展可以更明确地说成一句话：

> **v1.7 已经把 CFS-PD-MPC 方向实现出来了，method gates 也过了，但 full training selection 仍然 rejected；所以现在不能写 closed-loop superiority。下一步不是再堆 guard，而是做“regime-calibrated safe policy improvement”：让控制器在 storage / cascade / completion / switching 不同 regime 下有不同的安全边界、优势门槛和优化目标。**

GitHub 最新提交显示，仓库在 2026-05-29 已经进入 `feat(v1.7): CFS-PD-MPC controller, training suite, ablation framework, and experiment artifacts` 这一版；也就是说，你之前文档里建议的 “Completion-aware Finite-Storage Primal-Dual Model-Predictive Pressure” 已经被推进到实现和训练实验阶段。([GitHub][1]) 但 README 仍然明确保留 claim discipline：当前 proven route 还是 pressure-equivalent generalized-pressure symbolic recovery，v1.4 / v1.5 不支持 superiority over max-pressure-style baselines；v1.5 的 113 个 training candidates 也全部 rejected，主要问题是 completion safety。([GitHub][2]) 这和你上传的 5 月 28 日判断一致：storage/cascade/release 机制不是没用，而是没有稳定转化成对 strong baselines 的 closed-loop win，尤其 unfinished / completion safety 会被 baselines 抓住。

## 1. 最新 v1.7 到底进展到哪了

好消息是：**方法论 gate 已经不是问题。** v1.7 的 deterministic gates 是 `PASSED`，覆盖 pressure recovery、storage separation、cascade separation、terminal completion、rollout calibration、baseline envelope audit、regime tagging；但这个 artifact 自己也明确说，这只是 deterministic one-step / method gate，不代表 closed-loop superiority、deployment readiness 或 locked holdout performance。([GitHub][3])

v1.7 的训练协议也比 v1.5 更像一篇严肃 OR/control paper 的 protocol：controller 是 `finite_storage_completion_primal_dual_v1_7`，核心参数包括 rollout horizon、release/storage/cascade/completion/switching 权重、advantage gate、completion safety margin；baselines 包括 `max_pressure`、`capacity_aware_pressure`、`occupancy_capacity_aware_pressure`、`finite_storage_double_pressure`、`delay_based_max_pressure`、`switching_loss_max_pressure`。([GitHub][4]) 主 endpoint 也已经转成 theory-aligned composite finite-storage operating cost：delay、unfinished vehicle penalty、spillback/blocking time、switching lost time，并且要求 unfinished / delay / penalized travel time safety guards。([GitHub][4])

坏消息是：**v1.7 training selection 仍然 rejected。** `v1_7_training_selection` 显示 `status = REJECTED`、`claim_ready = false`，虽然 row audit 是干净的：expected / raw / completed 都是 378，没有 missing、failed、duplicate。([GitHub][5]) 这说明它不是工程没跑完，而是完整训练后 candidate 没达到选择条件。

更关键的是失败形态变了。v1.5 的问题是“机制太 aggressive，赢 composite 时伤 completion”；v1.7 的问题更像是“safe policy improvement 过度保守，最终又退回 pressure / baseline envelope 附近”。v1.7 训练选择里的 mechanism summary 显示：总 decisions 72,900，但 relative-to-pressure action change 只有 2,057，action-change rate 约 2.82%；而之前 protocol 对 action separation 有要求。更奇怪的是 regime counts 全部落在 `completion_critical = 270`，没有真正形成 storage / cascade / release / switching 的多 regime 分布。([GitHub][5])

regret analysis 也说明它没有打过强 baselines：相对 `max_pressure`、`capacity_aware_pressure`、`delay_based_max_pressure`、`switching_loss_max_pressure` 等仍有明显 regret，尤其 worst baseline 是 `switching_loss_max_pressure`。([GitHub][5]) 所以你说“没有在大部分场景胜过所有 baseline”非常准确。

## 2. 我对失败原因的判断

现在不是“没有理论创新”。v1.5 已经证明 storage/cascade/release 机制可以激活，v1.7 又证明 completion-aware CFS-PD-MPC 的 deterministic components 可以过 gate。你上传的记录也已经明确指出，CFS-PD-MPC 的核心应该是 finite-storage dual prices、terminal completion dual prices、short-horizon rollout、baseline-envelope safe policy improvement，而不是单步 score。

真正问题有四个。

第一，**v1.7 的 safety envelope 太保守，导致 action separation 不够。**
v1.5 的痛点是 completion harm，所以 v1.7 加了 baseline envelope 和 advantage gate，这是正确方向；但现在偏离 pressure 的比例只有 2.82%，说明控制器大多数时候没有真正利用 storage/cascade/release/completion dual 去创造新动作。一个想“超过 baseline”的 controller，不能只是安全地贴着 baseline 走。

第二，**regime classifier collapsed。**
所有 regime 都被打成 `completion_critical`，这很危险。finite-storage controller 的主要优势应该发生在 storage-binding、cascade-risk、release-critical、switching-sensitive 等状态。如果日志里几乎看不到这些 regime，说明 controller 的机制解释和实际动作之间断了。你上传的方案里本来就建议用 auditable regime-switching policy：slack 用 MP，storage-binding 用 storage controller，cascade-risk 用 cascade controller，completion-critical 用 completion controller，coordination/platoon 用 coordination controller。 v1.7 看起来没有把这个分区真正跑出来。

第三，**v1.7 对 switching-loss / delay-based baselines 的适配不够。**
新增 `delay_based_max_pressure` 和 `switching_loss_max_pressure` 是对的，因为它们是更强的实用 baseline。但 v1.7 regret 分析显示 worst baseline 是 switching-loss MP，这说明当前 CFS-PD-MPC 的 switching / coordination 部分还不够强。([GitHub][5]) 之前只想着不伤 completion，现在还要处理“频繁切换、绿损、干道协调”这类实用 baselines 的优势。

第四，**rollout 还没有变成可靠的 advantage predictor。**
v1.7 引入 H=3 rollout 和 advantage gate，但如果 predicted advantage 不能稳定预测 realized advantage，controller 要么过度冒险，要么过度保守。你上传的文档已经建议把 unfinished vehicles 从“仿真结束后才发现”变成“每个 action 前可预测”，用 finishable vehicles 和 terminal risk 来约束动作。 现在下一步要做的不只是有 rollout，而是校准 rollout。

## 3. 下一步不要做什么

不要开始写 strong performance paper。现在可以写 method note / internal report，但不能写“v1.7 beats all baselines”。仓库的 claim discipline 和 training selection 都不支持这个说法。([GitHub][5])

不要弱化 baselines。`max_pressure`、`capacity_aware_pressure`、`occupancy_capacity_aware_pressure`、`finite_storage_double_pressure`、`delay_based_max_pressure`、`switching_loss_max_pressure` 都应该保留。弱化 baselines 会让结果变得好看，但论文反而更脆。

不要简单调大 storage/cascade 权重，也不要简单调松 unfinished safety。v1.5 的经验已经说明，调大 storage/cascade/release 容易赢 composite 但伤 unfinished；文档里也明确指出，继续堆 r-chain guard 会让方法看起来像 post-hoc engineering，而不是强 methodology contribution。

不要在当前 failed training selection 上直接 lock holdout。只有 training selection 过了，才应该 lock fresh holdout；你上传的方案也强调，训练阶段不能 claim superiority，只能作为 holdout lock 的前置条件。

## 4. 我建议的新方向：v1.8 Regime-Calibrated CFS-PD-MPC

我建议下一版不要叫 v1.7-r2，也不要叫 r115。直接开一个干净 milestone：

> **v1.8 Regime-Calibrated Completion-Safe Finite-Storage Primal-Dual MPC**
> 简称：**RC-CFS-PD-MPC**

核心思想是：**v1.7 的 baseline envelope 是对的，但应该按 regime 校准；不同交通状态下，允许偏离 baseline 的幅度、completion safety margin、advantage threshold、switching penalty 都不应该相同。**

现在 v1.7 的动作选择大概是：

[
\mathcal A_{\text{safe}}(t)
===========================

{p:\widehat U_H(p)\le \min_{b\in\mathcal B}\widehat U_H(p_b)+\epsilon_U}
]

[
p^\star = \arg\min_{p\in\mathcal A_{\text{safe}}} \widehat J_H(p)
]

再用 advantage gate 决定是否偏离 baseline。这个结构本身是对的；你上传的文档也强调，baseline 不是被抄袭，而是作为 safety certificate，真正排序仍然由 finite-storage primal-dual + completion dual + rollout value 完成。

但 v1.8 要把它改成 **regime-dependent**：

[
\mathcal A_{\text{safe}}^{r}(t)
===============================

\left{
p:
\widehat U_H(p)
\le
\min_{b\in\mathcal B}\widehat U_H(p_b)
+
\epsilon_U^{r}
\right}
]

[
p^\star
=======

\arg\min_{p\in \mathcal A_{\text{safe}}^{r}(t)}
\widehat J_H^{r}(p)
]

[
\text{deviate only if }
\Delta_H^{r}(p)
===============

## \widehat J_H^{r}(p_{\text{best baseline}})

\widehat J_H^{r}(p)

>

\tau_{\text{adv}}^{r}
]

这里 (r) 是 regime：slack、storage-binding、cascade-risk、completion-critical、switching-sensitive、coordination/platoon。这样可以解决 v1.7 的核心矛盾：completion-critical 时保守，storage/cascade-binding 时允许更积极，switching-sensitive 时提高 switching loss 权重。

## 5. v1.8 方法设计细节

### 5.1 先修 regime classifier：不能再全部变成 completion_critical

新版本必须有一个明确的 multi-label regime classifier。每个 decision log 至少输出：

```json
{
  "regime_primary": "slack | storage_binding | cascade_risk | completion_critical | switching_sensitive | coordination",
  "regime_scores": {
    "storage_binding": ...,
    "cascade_risk": ...,
    "completion_critical": ...,
    "switching_sensitive": ...,
    "coordination": ...
  },
  "selected_action": ...,
  "best_baseline_action": ...,
  "mp_action": ...,
  "predicted_advantage": ...,
  "predicted_unfinished_margin": ...,
  "realized_next_interval_delta": ...,
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

判定规则建议：

* **slack**：所有下游 occupancy < 0.65，cascade price 低，completion risk 低。动作应恢复 MP，不追求赢。
* **storage_binding**：任一下游 occupancy > 0.80 或 residual receiving capacity 低。允许 storage dual 更强。
* **cascade_risk**：immediate downstream 还没满，但 descendant shadow price (\xi) 高。允许提前避开 cascade path。
* **completion_critical**：remaining horizon / ETA 紧，finishable vehicles 对 action 敏感。completion safety margin 最严格。
* **switching_sensitive**：切换损失高、当前 green 仍有可服务队列、phase change 会造成 lost time。提高 switching penalty / hysteresis。
* **coordination/platoon**：upstream moving platoon 或 progression value 高。避免局部 pressure 打断干道流。

v1.8 的第一个 gate 就应该是 **regime balance gate**：在 synthetic cases 里，storage case 必须被判成 storage_binding，cascade case 必须被判成 cascade_risk，terminal case 才是 completion_critical。否则后续训练没有意义。

### 5.2 把 safety margin 和 advantage threshold 按 regime 分开

v1.7 一个统一的 (\epsilon_U) / (\tau_{\text{adv}}) 很容易过度保守。建议：

```json
{
  "eps_u": {
    "slack": 0.00,
    "completion_critical": 0.00,
    "storage_binding": 0.05,
    "cascade_risk": 0.05,
    "switching_sensitive": 0.03,
    "coordination": 0.03
  },
  "tau_adv": {
    "slack": "high",
    "completion_critical": "high",
    "storage_binding": "medium_low",
    "cascade_risk": "medium_low",
    "switching_sensitive": "medium",
    "coordination": "medium"
  }
}
```

直觉是：slack 和 completion-critical 不要轻易偏离 baseline；storage/cascade 真正 binding 时，baseline 本来容易犯错，应该允许更低 advantage threshold；switching-sensitive 时，只有当 rollout 证明切换后收益足够大，才切换。

### 5.3 加 switching / coordination 机制，否则打不过 switching-loss MP

现在 worst baseline 是 `switching_loss_max_pressure`，这说明 v1.7 对 switching-loss-sensitive 场景没有建模好。v1.8 需要把 switching 不再只当 penalty，而是做成 **stateful switching / coordination dual**：

[
\zeta_p(t+1)
============

(1-\rho_\zeta)\zeta_p(t)
+
\kappa_\zeta
\cdot
\mathbf 1{\text{phase }p\text{ recently switched too often}}
]

并在 objective 里加：

[
\widehat J_H^{r}(p)
===================

\lambda_d^r \widehat D_H(p)
+
\lambda_u^r \widehat U_H(p)
+
\lambda_s^r \widehat S_H(p)
+
\lambda_l^r \widehat L_H(p)
---------------------------

\lambda_g^r \widehat G_H(p)
]

其中 ( \widehat G_H(p) ) 是 progression / platoon service value。这样 switching-loss-sensitive 场景不会被 finite-storage dual 牵着乱切。

### 5.4 Rollout 必须校准，不只是存在

下一步要新增一个 artifact：

```text
experiments/dual_sensitivity/v1_8_rollout_calibration_by_regime.csv
```

每个 decision 记录：

* predicted ( \Delta J_H )
* realized next-window ( \Delta J )
* predicted unfinished margin
* realized unfinished difference
* predicted spillback risk
* realized spillback/blocking
* regime
* selected action vs best baseline action

训练前先看 sign accuracy。如果 predicted advantage 的符号准确率低于 60%，advantage gate 就是不可信的。v1.8 不应该先跑 378 rows 训练，而应该先过 **rollout sign sanity gate**。

### 5.5 训练目标改成 regime-weighted minimax regret

当前 v1.7 已经用了 minimax regret 思路，但建议改成 regime-weighted：

[
\min_\theta
\sum_{s\in \mathcal S_{\text{train}}}
w_{r(s)}
\max_{b\in\mathcal B}
\left[
J(\pi_\theta,s)-J(b,s)
\right]*+
+
\lambda_U
\left[
U(\pi*\theta,s)-\min_b U(b,s)-\epsilon_U^{r(s)}
\right]*+
+
\lambda_A
\left[
a*{\min}^{r(s)}-\text{action_sep}^{r(s)}
\right]_+
]

这里不是为了盲目增加 action separation，而是要求 **在 storage/cascade binding regimes 中必须有足够非 baseline 动作**；slack regime 中 action separation 可以低。

## 6. 具体执行方案

### Stage 0：关闭 v1.7，不要再硬救

写一个 artifact：

```text
experiments/dual_sensitivity/v1_7_closeout_training_rejected.md
```

内容写清楚：

* v1.7 CFS-PD-MPC implemented；
* deterministic gates passed；
* training execution complete；
* training selection rejected；
* row audit clean；
* failure modes：action separation too low、regime collapse to completion_critical、regret vs switching_loss / delay baselines、no superiority claim。

这一步很重要。它能防止后续 v1.8 被认为是在 failed holdout 上 post-hoc patch。

### Stage 1：做 v1.7 failure decomposition

新增：

```text
experiments/dual_sensitivity/v1_7_failure_decomposition.json
experiments/dual_sensitivity/v1_7_regime_confusion_audit.csv
experiments/dual_sensitivity/v1_7_rollout_calibration_by_regime.csv
experiments/dual_sensitivity/v1_7_baseline_oracle_map.json
```

你要回答四个问题：

1. 哪些 scenario / demand / seed 输给了哪个 baseline？
2. 输是因为 unfinished、delay、switching、spillback，还是 throughput？
3. 哪些 predicted advantage 实际没兑现？
4. baseline oracle 在不同 regime 下是谁？MP？cap-aware？FSDP？delay-MP？switching-loss-MP？

没有这一步，v1.8 参数搜索会盲。

### Stage 2：实现 v1.8 controller

Controller name 建议：

```python
"finite_storage_regime_calibrated_cfs_pd_mpc_v1_8"
```

新增模块或函数：

```python
class RegimeCalibratedCfsPdMpc:
    def classify_regime(state) -> RegimeScores
    def rollout(action, state, horizon, regime) -> PredictedOutcomes
    def compute_baseline_envelope(state, baselines) -> BaselineEnvelope
    def safe_action_set(actions, envelope, regime) -> list[Action]
    def select_with_advantage_gate(actions, predictions, regime) -> Action
    def update_duals(state, realized_outcomes) -> DualState
```

保留 v1.7 作为 ablation，不要覆盖。

### Stage 3：先跑 deterministic gates，不跑 training

新增：

```text
experiments/dual_sensitivity/v1_8_regime_calibration_gates.json
experiments/dual_sensitivity/v1_8_terminal_completion_gate.json
experiments/dual_sensitivity/v1_8_switching_loss_gate.json
experiments/dual_sensitivity/v1_8_rollout_sign_gate.json
experiments/dual_sensitivity/v1_8_baseline_envelope_gate.json
```

必须过这些 gates：

* pressure recovery：slack 下等价 MP；
* storage separation：storage-binding 下偏离 MP；
* cascade separation：descendant congestion 下提前避开；
* terminal completion：completion-critical 下不伤 finishable vehicles；
* switching-loss：切换收益不足时不切；
* regime balance：synthetic storage/cascade/completion/switching cases 不被全部打成 completion；
* rollout sign：预测优势方向正确。

### Stage 4：小规模参数 screen

先不要跑完整 378 rows。跑 36-row screen：

* scenarios：storage activation、spillback stress、downstream blockage、switching-loss-sensitive；
* demand：0.85 / 1.0 / 1.15；
* seeds：2–3 个；
* baselines：MP、cap-aware、occupancy-cap-aware、FSDP、delay-MP、switching-loss-MP。

参数网格建议：

```json
{
  "H": [2, 3, 4],
  "beta_storage": [0.15, 0.30, 0.60],
  "gamma_cascade": [0.10, 0.30, 0.50],
  "eta_completion": [0.50, 1.00, 1.50],
  "lambda_switching": [0.25, 0.75, 1.50],
  "eps_u_storage": [0.03, 0.05, 0.10],
  "eps_u_completion": [0.00, 0.02],
  "tau_adv_storage": [0.00, 0.02, 0.05],
  "tau_adv_completion": [0.05, 0.10],
  "tau_adv_switching": [0.03, 0.07, 0.12],
  "min_green_hysteresis": [0, 1, 2]
}
```

Screen pass 条件：

* no catastrophic unfinished harm；
* action-change rate > 5% overall；
* action-change rate > 10% in storage/cascade regimes；
* regime distribution 不 collapse；
* positive mean (J) vs MP；
* not dominated by switching-loss MP；
* predicted advantage sign accuracy > 60%。

### Stage 5：full training selection

通过 screen 的候选再跑完整 training。Selection 条件建议：

1. **Row audit clean**。
2. **Safety**：unfinished vehicles、penalized travel time、total delay 不出现 practical harm。
3. **Win vs MP**：至少 70% training scenario × demand groups 的 composite (J) 正改善。
4. **Win vs core finite-storage baselines**：对 capacity-aware、occupancy-cap-aware、FSDP aggregate mean 不输，最好正改善。
5. **Switching robustness**：不能让 `switching_loss_max_pressure` 成为巨大 worst regret。
6. **Mechanism**：storage/cascade/release/completion/switching 至少各自在对应 regime 贡献非零。
7. **Action separation**：不能低于 5%，但也不能靠随机抖动；偏离动作必须集中在 binding/cascade/completion/switching states。
8. **Advantage realization**：偏离 baseline 的动作中，realized (J) 改善比例至少 > 55–60%。

只有一个候选进入 holdout。

### Stage 6：locked holdout

只有 full training selection `PASSED` 后，才生成：

```text
experiments/dual_sensitivity/v1_8_locked_holdout_protocol.json
experiments/dual_sensitivity/v1_8_locked_holdout_execution.json
experiments/dual_sensitivity/v1_8_paired_evidence.json
```

Holdout 必须 fresh seeds，不能复用 training seeds 或失败调参过程中反复看的 seeds。协议固定后不再改 controller、threshold、objective weights、baselines。你上传的方案里也强调，fresh seeds、protocol fingerprint、candidate 固定、baselines 固定、no mid-run editing 是必须的，否则结果很容易被认为是 post-hoc tuning。

### Stage 7：ablation

最终至少需要这些 ablations：

* full v1.8；
* no-completion dual；
* no-baseline-envelope；
* no-rollout；
* no-cascade；
* no-release；
* no-switching/hysteresis；
* no-regime-calibration；
* static v1.4；
* dynamic v1.5；
* v1.7 CFS-PD-MPC。

你上传的文档已经强调，ablation 要证明 no-completion 会重新出现 unfinished harm，no-rollout 会在 finite horizon 上输，no-envelope 会更 aggressive 但 safety 下降，no-cascade / no-release 分别在对应 stress 下输。

## 7. 最终目标怎么定义才合理

不要把目标写成“所有场景超过所有 baselines”。这几乎不现实，也不符合 max-pressure 在 slack regime 的理论地位。建议目标写成：

> **在 finite-storage binding regimes 中，v1.8 在大部分 locked paired-seed scenario × demand groups 上降低 composite finite-storage operating cost，相比 max-pressure、capacity-aware pressure、occupancy-capacity-aware pressure、finite-storage double pressure、delay-based MP、switching-loss MP 不出现 safety harm，并在 storage/cascade/completion/switching regime 中展示可审计机制优势。**

内部 target 可以设成：

* vs Max Pressure：75–85% locked binding groups 正改善；
* vs capacity-aware / FSDP：60–75% 正改善；
* vs best baseline envelope：aggregate non-worse，部分 regime 正改善；
* safety：unfinished / delay / penalized travel time no practical harm；
* mechanism：非 baseline 动作集中在 high occupancy、low receiving capacity、cascade risk、completion critical、switching-sensitive states；
* action separation：overall > 5%，binding regimes > 10%；
* rollout calibration：predicted advantage sign accuracy > 60%。

这比“到处赢”更强，也更审稿友好。它承认 slack regime 下 MP 很强，同时把你的贡献锁定在 finite-storage binding / completion-constrained / switching-aware regimes。

## 8. 我会把下一步优先级排成这样

第一优先级：**做 v1.7 failure decomposition**。先别改 controller。把 v1.7 到底输给哪个 baseline、在哪个 regime、因为什么 metric 输，拆清楚。

第二优先级：**修 regime classifier**。只要 regime 继续全是 completion_critical，CFS-PD-MPC 的 storage/cascade/release 优势就不会出现。

第三优先级：**做 regime-dependent safety envelope 和 advantage gate**。completion-critical 保守，storage/cascade binding 更允许偏离，switching-sensitive 提高切换门槛。

第四优先级：**加强 switching / coordination term**。因为当前 strongest regret 来自 switching-loss MP，v1.8 必须把它作为 first-class 对手，而不是事后 baseline。

第五优先级：**rollout calibration**。没有 calibrated rollout，advantage gate 就不可靠，控制器会在 aggressive 和 conservative 之间摆动。

第六优先级：**小规模 screen → full training → fresh locked holdout**。不要跳过 screen，也不要在 training rejected 的情况下 lock holdout。

我的最终判断是：**方向仍然值得冲，而且 v1.7 比 v1.5 更接近正确结构；但现在的问题已经从“completion safety 没建模”升级为“safe policy improvement 过保守、regime 没分开、switching baseline 没打掉”。下一版的关键不是再发明一个新 penalty，而是把 CFS-PD-MPC 做成 regime-calibrated、rollout-calibrated、switching-aware 的安全策略改进框架。**

[1]: https://github.com/Radar-Lei/pi_light_OR/commits/main "Commits · Radar-Lei/pi_light_OR · GitHub"
[2]: https://raw.githubusercontent.com/Radar-Lei/pi_light_OR/main/README.md "raw.githubusercontent.com"
[3]: https://github.com/Radar-Lei/pi_light_OR/blob/main/experiments/dual_sensitivity/v1_7_cfs_pd_mpc_gates.json "pi_light_OR/experiments/dual_sensitivity/v1_7_cfs_pd_mpc_gates.json at main · Radar-Lei/pi_light_OR · GitHub"
[4]: https://github.com/Radar-Lei/pi_light_OR/blob/main/experiments/dual_sensitivity/v1_7_training_protocol.json "pi_light_OR/experiments/dual_sensitivity/v1_7_training_protocol.json at main · Radar-Lei/pi_light_OR · GitHub"
[5]: https://github.com/Radar-Lei/pi_light_OR/blob/main/experiments/dual_sensitivity/v1_7_training_selection.json "pi_light_OR/experiments/dual_sensitivity/v1_7_training_selection.json at main · Radar-Lei/pi_light_OR · GitHub"
