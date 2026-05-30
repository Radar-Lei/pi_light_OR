# v1.7 CFS-PD-MPC Training Closeout

**Date:** 2026-05-29
**Controller:** `finite_storage_completion_primal_dual_v1_7`
**Schema:** phase6_explicit_state_v1

---

## Status

**Training selection: REJECTED.** `claim_ready: false`.

The deterministic method-gate battery passed all 7 gates (see below), confirming that the v1.7 CFS-PD-MPC mechanism is structurally sound at the one-step level. However, the closed-loop training selection over 378 rows (3 scenarios x 6 seeds x 3 demand multipliers x 7 controllers) rejected the candidate due to regime-classifier collapse, excessive conservatism, insufficient action separation, and 243 safety-guard violations against strong baselines.

No closed-loop superiority claim is permitted. The locked-holdout stage is not reached.

---

## Method Gates

All 7 deterministic one-step gates **PASSED**. Gate artifact: `v1_7_cfs_pd_mpc_gates.json`, generated 2026-05-28T12:58:04Z.

| # | Gate | Regime | Key Criteria | Result |
|---|------|--------|-------------|--------|
| 1 | **Pressure recovery** | slack | v17_matches_pressure=true, dual_prices_zero=true, regime_is_slack=true | PASSED |
| 2 | **Storage separation** | storage_binding | storage_price_active_down_a=true, v17_changes_from_pressure=true, regime_is_storage_binding=true | PASSED |
| 3 | **Cascade separation** | N/A | descendant_storage_price_active=true, intermediate_cascade_price_active=true, cascade_exceeds_single_storage=true, v17_avoids_cascade_path=true | PASSED |
| 4 | **Terminal completion** | completion_critical | completion_price_asymmetric=true, down_a_completion_price_positive=true, v17_selects_completion_safe_action=true | PASSED |
| 5 | **Rollout calibration** | N/A | all_monotone=true, rollout_has_phases=true | PASSED |
| 6 | **Baseline envelope audit** | N/A | safe_nonempty_picks_min_J_H=true, safe_set_contains_phase_1=true, advantage_gate_not_active_a=true, empty_safe_set_fail_closed=true, advantage_gate_reverts=true, advantage_gate_selects_baseline=true | PASSED |
| 7 | **Regime tagging** | N/A | all_low_occupancy_is_slack=true, high_occupancy_is_storage_binding=true, cascade_risk_detected=true, short_horizon_low_finishable_is_completion_critical=true | PASSED |

**Claim scope (gates only):** deterministic one-step v1.7 method-gate evidence. Not claimed: closed-loop superiority, deployment readiness, universal cross-regime advantage, locked-holdout performance.

---

## Training Protocol

Locked 2026-05-28T19:01:59Z. Fingerprint: `3977337233b0a99d4dbfa120abb9dba32ab02b7596d0ebf422e0ea5034b933ff`.

- **Controller ID:** `finite_storage_completion_primal_dual_v1_7`
- **Baselines (6 required):**
  - `max_pressure`
  - `capacity_aware_pressure`
  - `occupancy_capacity_aware_pressure`
  - `finite_storage_double_pressure`
  - `delay_based_max_pressure`
  - `switching_loss_max_pressure`
- **Primary endpoint:** `composite_finite_storage_operating_cost` = delay + unfinished_vehicle_penalty + spillback_blocking_time + switching_lost_time (all weight 1.0)
- **Selection rule:** minimax regret -- min over candidates of max over baselines of [J(candidate,s) - J(baseline,s)]+
- **Eligibility gate:** no safety-guard harm against max_pressure / capacity_aware_pressure / finite_storage_double_pressure; advantage_gate_activation_rate > 0; action_separation_rate > 0.05

**Key controller parameters:**

| Parameter | Value |
|-----------|-------|
| H_rollout | 3.0 |
| alpha_release | 0.7 |
| beta_storage | 0.15 |
| lambda_spillback | 0.5 |
| lambda_switching | 0.25 |
| lambda_blocking | 0.3 |
| completion_horizon_fraction | 0.7 |
| completion_critical_horizon_fraction | 0.3 |
| completion_deficit_threshold | 0.75 |
| completion_safe_margin | 0.1 |
| dual_step_size | 0.3 |
| dual_decay | 0.25 |
| storage_threshold | 0.72 |
| slack_occupancy_threshold | 0.65 |
| storage_binding_threshold | 0.8 |
| cascade_risk_threshold | 0.3 |

**Training split:**

| Dimension | Values |
|-----------|--------|
| Scenarios | arterial_v1_5_storage_activation, arterial_spillback_stress, arterial_downstream_blockage |
| Seeds | 20261701, 20261702, 20261703, 20261704, 20261705, 20261706 |
| Demand multipliers | 0.85, 1.0, 1.15 |
| Steps / warmup / action_interval | 3600 / 900 / 10 |
| Expected rows | 378 (3 x 6 x 3 x 7) |

**Safety guards (with tolerances):**

| Metric | Tolerance | Direction |
|--------|-----------|-----------|
| penalized_avg_travel_time | 5% | lower_is_better |
| total_delay | 5% | lower_is_better |
| unfinished_vehicle_count | 0% (strict) | lower_is_better |

---

## Training Execution

| Field | Value |
|-------|-------|
| Expected rows | 378 |
| Raw rows | 378 |
| Completed rows | 378 |
| Missing rows | 0 |
| Failed rows | 0 |
| Duplicate rows | 0 |

All 378 rows executed successfully. The training execution (`v1_7_training_full.json`) reports status `COMPLETE_PENDING_SELECTION` with `all_rows_executed: true`. No execution failures contributed to the rejection.

---

## Training Selection Result

**Decision: `reject_finite_storage_completion_primal_dual_v1_7`**
**Reason: training rows show safety-guard harm against strong baselines**

### Mechanism Summary

| Metric | Value |
|--------|-------|
| Controller rows | 54 |
| Total decisions | 72,900 |
| Action-changed-relative-to-pressure count | 2,057 |
| **Action-change rate** | **0.0282 (2.82%)** -- target >5% |
| Binding decision count | 24,270 |
| Binding decision rate | 0.3329 (33.29%) |
| Advantage gate activation count | 259 |
| Advantage gate activation rate | 0.9593 (95.93%) |

### Regime Distribution

| Regime | Count | Fraction |
|--------|-------|----------|
| slack | 0 | 0.0 |
| storage_binding | 0 | 0.0 |
| cascade_risk | 0 | 0.0 |
| **completion_critical** | **270** | **1.0** |

All 270 binding decisions fell into `completion_critical`. Zero decisions were classified as `slack`, `storage_binding`, or `cascade_risk`. This constitutes a complete regime-classifier collapse into the most conservative regime.

---

## Failure Modes

### 1. Action separation too low

2,057 / 72,900 decisions = **2.82% action-change rate** (target > 5%).

The controller deviated from the pressure baseline in only 2.82% of decisions, meaning it effectively replicated max-pressure in ~97% of cases while adding computational overhead. The low separation means the controller fails to exploit the dual-sensitivity corrections that the method gates validated at the one-step level.

### 2. Regime classifier collapse

All 270 regime-tagged decisions classified as `completion_critical`. Regime counts:
- slack: 0, storage_binding: 0, cascade_risk: 0, completion_critical: 270.

The `completion_critical_horizon_fraction=0.3` threshold combined with the `completion_deficit_threshold=0.75` triggered completion-critical tagging in every scenario-seed-demand combination, even in low-demand states (dm=0.85) where no completion risk should exist. This caused the controller to activate the completion-safe envelope universally, making it overly conservative.

### 3. Baseline regret

Worst baseline: `switching_loss_max_pressure` with minimax regret of **1,949,566.46**.

The largest single-scenario regret against switching_loss_max_pressure was **9,206,477** (arterial_v1_5_storage_activation, dm=1.15, seed=20261703). At high demand, the candidate produced composite costs of 126,764,985 vs the baseline's 117,558,508.

### 4. Safety harms

**243 total safety-guard violations** across all scenarios, seeds, and demand multipliers.

Breakdown by metric:

| Metric | Violations | Max excess | Avg excess |
|--------|-----------|------------|------------|
| unfinished_vehicle_count | 133 | +785.0 vehicles | +28.9 vehicles |
| total_delay | 88 | +234,329.0 | +21,210.6 |
| penalized_avg_travel_time | 22 | +174.88 seconds | +34.43 seconds |

Breakdown by baseline:

| Baseline | Violations |
|----------|-----------|
| switching_loss_max_pressure | 92 |
| delay_based_max_pressure | 70 |
| occupancy_capacity_aware_pressure | 24 |
| max_pressure | 23 |
| finite_storage_double_pressure | 20 |
| capacity_aware_pressure | 14 |

Breakdown by demand multiplier:

| Multiplier | Violations |
|-----------|-----------|
| 0.85 | 44 |
| 1.0 | 81 |
| 1.15 | 118 |

Breakdown by scenario:

| Scenario | Violations |
|----------|-----------|
| arterial_v1_5_storage_activation | 93 |
| arterial_downstream_blockage | 75 |
| arterial_spillback_stress | 75 |

Worst single violation: arterial_v1_5_storage_activation, dm=1.15, seed=20261703 vs switching_loss_max_pressure -- unfinished_vehicle_count: candidate=1,004, baseline=219, excess=785 vehicles. Total_delay: candidate=387,731, baseline=153,402, excess=234,329.

---

## Regret Analysis

Minimax regret objective: max over baselines of mean_[J(candidate) - J(baseline)]+

| Baseline | Mean Regret |
|----------|-------------|
| switching_loss_max_pressure | 1,949,566.46 |
| delay_based_max_pressure | 1,272,257.04 |
| max_pressure | 1,078,330.65 |
| finite_storage_double_pressure | 252,151.61 |
| occupancy_capacity_aware_pressure | 6,527.74 |
| capacity_aware_pressure | 4,712.78 |

**Minimax regret: 1,949,566.46** (worst baseline: switching_loss_max_pressure).

Core composite mean differences:

| Baseline | Mean Difference |
|----------|----------------|
| finite_storage_double_pressure | +21,264,162.59 (candidate worse) |
| max_pressure | -829,011.13 (candidate better) |
| capacity_aware_pressure | -2,601.59 (candidate slightly better) |

The candidate performed competitively against plain max_pressure and capacity_aware_pressure on average, but catastrophically worse against switching_loss_max_pressure and delay_based_max_pressure, particularly in the arterial_v1_5_storage_activation scenario at high demand (dm=1.15). The unfinished_vehicle_penalty component dominates the composite in oversaturated scenarios where the controller's completion-safe envelope paradoxically prevents throughput-maximizing phase switches.

---

## Iteration History

Eight training iterations (r4 through r11) were evaluated. All were **REJECTED**.

| Iteration | Action Rate | Regime Distribution | Minimax Regret | Safety Harms | Worst Baseline |
|-----------|-------------|---------------------|---------------|-------------|----------------|
| r4 | 0.0434 (4.34%) | slack=0, storage=0, cascade=0, completion=270 | 1,139,532.43 | 234 | switching_loss_max_pressure |
| r5 | 0.0185 (1.85%) | slack=0, storage=0, cascade=0, completion=270 | 1,310,982.15 | 221 | switching_loss_max_pressure |
| r6 | 0.0185 (1.85%) | slack=0, storage=0, cascade=0, completion=270 | 1,310,982.15 | 221 | switching_loss_max_pressure |
| r7 | 0.0185 (1.85%) | slack=0, storage=0, cascade=0, completion=270 | 1,310,982.15 | 221 | switching_loss_max_pressure |
| r8 | 0.0175 (1.75%) | slack=90, storage=0, cascade=0, completion=140 | 1,009,951.83 | 168 | switching_loss_max_pressure |
| r9 | 0.0095 (0.95%) | slack=90, storage=0, cascade=0, completion=140 | 969,669.48 | 172 | switching_loss_max_pressure |
| r10 | 0.0187 (1.87%) | slack=90, storage=0, cascade=0, completion=180 | 801,352.70 | 210 | switching_loss_max_pressure |
| r11 | 0.0185 (1.85%) | slack=90, storage=0, cascade=0, completion=180 | 802,155.96 | 216 | switching_loss_max_pressure |

Key observations:
- **r4 had the highest action-change rate at 4.34%** but still fell short of the 5% eligibility threshold.
- **r5-r7 were identical** (same parameters, same results), indicating a stalled iteration.
- **r8 introduced partial regime differentiation** (90 slack / 140 completion_critical) but action-change rate dropped further to 1.75%.
- **r9 achieved the lowest minimax regret (969,669.48)** but with the worst action-change rate (0.95%).
- **r10-r11 partially recovered** action-change rate but regime collapse persisted (no storage_binding or cascade_risk decisions in any iteration).
- No iteration ever produced `storage_binding` or `cascade_risk` regime classifications. The regime tagger's `storage_binding_threshold=0.8` and `cascade_risk_threshold=0.3` never activated in closed-loop operation.
- The final production run (the main `v1_7_training_selection.json`) used parameters equivalent to r4, with full regime collapse back to completion_critical=270.

---

## Conclusion and Recommendation

**v1.7 CFS-PD-MPC is closed.**

The deterministic method-gate battery confirmed that the Completion- and Finite-Storage-aware Primal-Dual MPC mechanism is structurally correct at the one-step level: it recovers max-pressure in slack conditions, activates storage duals under storage binding, detects and avoids cascade paths, and selects completion-safe actions when the horizon is short and finishable ratios are low.

However, the closed-loop training selection over 378 rows (3 scenarios, 6 seeds, 3 demand multipliers) **rejected** the controller on all measured dimensions:

1. **Regime collapse:** The completion-critical classifier triggered universally (270/270 decisions), preventing the controller from exploiting slack and storage-binding regime corrections. The `completion_critical_horizon_fraction=0.3` threshold is too aggressive for closed-loop operation where rolling horizons cause near-permanent critical tagging.

2. **Excessive conservatism:** The completion-safe envelope, designed to prevent unfinished vehicles at the end of the horizon, paradoxically increased unfinished vehicles by 785 (max) in oversaturated scenarios by preventing throughput-maximizing phase switches.

3. **Insufficient switching modeling:** The worst baseline was `switching_loss_max_pressure`, which explicitly accounts for yellow-time switching losses. The v1.7 controller's `lambda_switching=0.25` was insufficient to prevent the candidate from incurring large switching-related composite cost penalties.

4. **No iteration achieved the 5% action-separation threshold.** Across 8 iterations, the highest rate was 4.34% (r4), and the final production run achieved only 2.82%.

**Recommendation:** Proceed to **v1.8 Regime-Calibrated CFS-PD-MPC** with the following design changes:
- Regime-dependent safety envelopes that relax completion-safe constraints in slack and storage-binding regimes.
- Calibrated rollout horizons that avoid permanent critical-tagging by adapting `completion_critical_horizon_fraction` to observed demand levels.
- Explicit switching-loss integration matching or exceeding `switching_loss_max_pressure`'s loss model.
- A two-phase regime classifier that separates regime detection from envelope activation, preventing cascade into completion-critical.
