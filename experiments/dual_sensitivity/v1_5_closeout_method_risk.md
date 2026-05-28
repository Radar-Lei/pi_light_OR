# v1.5 Closeout: Method-Risk Finding

**Date**: 2026-05-28
**Status**: CLOSEOUT — mechanism success, completion-safety failure, no superiority claim

## Summary

v1.5 (finite_storage_dynamic_primal_dual_v1_5) 引入了 occupancy-based finite-storage state 和动态 shadow prices（storage scarcity、cascade spillback、upstream release）。方法机制已通过确定性验证和闭环诊断激活，但在训练选择和 early holdout 中，所有 113 个候选均因 completion / unfinished safety blocker 被拒绝。不允许 closed-loop superiority claim。

## Three Conclusions

### 1. Deterministic Method Gates: PASSED

四个核心机制门全部通过：
- **Slack pressure recovery**: storage/cascade/completion slack 时退化为 max-pressure ✓
- **Occupancy storage separation**: vehicle count 和 occupancy 替代 queue-only 指标，storage price 在高 occupancy 时激活 ✓
- **Cascade spillback separation**: 多跳 downstream shadow price 传播，避免 immediate downstream 可用但 descendant 拥堵的情况 ✓
- **Upstream release value**: upstream 高 occupancy + downstream path slack 时释放上游队列 ✓

Artifact: `v1_5_dynamic_primal_dual_gates.json` — status: PASSED

### 2. Closed-Loop Diagnostics: PASSED

100 个闭环决策中：
- Action-change rate: 0.55（55% 的决策相对 pressure 改变）
- Binding action-change rate: 0.756（75.6% 的 binding 决策发生改变）
- Binding decision rate: 0.45（45% 的决策处于 binding 状态）
- storage_price、cascade_price、spillback 均有 45 次激活
- downstream_storage、release 分别有 8 和 9 次激活

Artifact: `v1_5_closed_loop_diagnostics.json` — status: PASSED

### 3. Training / Early Holdout: FAILED (completion-safety blocker)

- Revision candidate summary: 113 个候选，0 个被选中，112 个被拒绝
- Completion safety blocker count: 107（占拒绝原因的 95%）
- Completion safety contract audit: 45 个候选，0 个通过 unfinished safety guard
- 27 个候选有 positive core composite signal，23 个同时有 positive composite + action separation
- 但 **0 个** 同时通过 unfinished safety guard

核心 tradeoff：v1.5 storage/cascade/release 机制能改善有限存储运行成本，但在有限 horizon 下未能保护 vehicle completion。

Artifacts:
- `v1_5_revision_candidate_summary.json` — NO_CANDIDATE_SELECTED
- `v1_5_completion_safety_contract_audit.json` — REVISION_REQUIRED
- `v1_5_tradeoff_analysis.json`
- `v1_5_binding_early_holdout_risk.json` — FAILED

## Why This Is Not a Negative Result

v1.5 的机制激活证据（deterministic gates + closed-loop diagnostics）构成了方法论贡献的正面基础。问题不在方法论方向，而在于 completion safety 被当作 post-hoc guard 而非 primal-dual relaxation 的一等约束。

## Implications for v1.6

v1.6 必须将 terminal completion feasibility 作为 primal-dual formulation 的核心组成部分，而非 fallback guard。具体要求：
1. 引入 terminal completion dual price (ν_ℓ)
2. 两阶段 action selection：completion-safe feasible set → primal-dual optimal
3. completion-state schema 成为 state model 的一等 citizen
4. 不得弱化 strong baselines 或 unfinished safety guard

## Disallowed Claims

- "v1.5 is closed-loop superior to max-pressure-style baselines" — 不允许
- "v1.5 reduces composite cost in most scenarios" — 不允许（仅 training 数据，未经 holdout 确认）
- "v1.5 mechanisms are sufficient for superiority" — 不允许（机制激活 ≠ 性能优越）

## Allowed Claims

- "v1.5 deterministic gates demonstrate that storage/cascade/release shadow prices change action rankings relative to pressure" — 允许
- "v1.5 closed-loop diagnostics show mechanism activation in binding states" — 允许
- "v1.5 training revealed a systematic completion-safety tradeoff" — 允许，且是 v1.6 的核心动机
