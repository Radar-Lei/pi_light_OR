# Phase 2: Full Sparse Symbolic Recovery - Validation

**Created:** 2026-05-23
**Purpose:** Define script-based acceptance gates for RECV-01 through RECV-05 before Phase 2 execution is marked complete.

## Validation Strategy

Phase 2 validation is script-based and CPU/SciPy/HiGHS oriented. The gate verifies recovery completeness and output auditability, not the Phase 3 scientific claim about whether dual sensitivity beats pressure.

## Quick Gate Command

```bash
python3 scripts/run_sparse_recovery.py \
  --states experiments/dual_sensitivity/targeted_bottleneck_states.json \
  --budgets 1 2 3 \
  --out experiments/dual_sensitivity/block2_sparse_recovery.json \
  --csv-out experiments/dual_sensitivity/block2_sparse_recovery.csv \
  --rules-out experiments/dual_sensitivity/block2_sparse_recovery_rules.txt
```

## Full Gate Command

```bash
python3 scripts/run_dual_sanity.py \
  --out experiments/dual_sensitivity/block2_dual_sanity.json
python3 scripts/run_sparse_recovery.py \
  --states experiments/dual_sensitivity/arterial_sampled_states.json \
  --states experiments/dual_sensitivity/targeted_bottleneck_states.json \
  --budgets 1 2 3 \
  --out experiments/dual_sensitivity/block2_sparse_recovery_combined.json \
  --csv-out experiments/dual_sensitivity/block2_sparse_recovery_combined.csv \
  --rules-out experiments/dual_sensitivity/block2_sparse_recovery_combined_rules.txt
```

## Requirement Gates

| Requirement | Gate | Pass Condition |
|---|---|---|
| RECV-01 | K-atom sparse recovery | At least one solved run has `max_atoms` or `budget` greater than 1 and selected program complexity is reported. |
| RECV-02 | Regret-first objective | JSON records `objective_mode` as oracle-regret/value-gap, realized regret metrics are present, and action agreement is diagnostic only. |
| RECV-03 | Explicit tradeoff controls | Runs expose total program-size, neighbor, genuine dual, and placebo budgets or penalties plus counts and penalty breakdown. |
| RECV-04 | Required atom families | Atom metadata includes local queue/pressure, downstream capacity/slack, raw neighbor queue, pressure/backpressure, dual sensitivity/price imbalance, and random/permuted dual placebo families. |
| RECV-05 | Auditable outputs | JSON, CSV, and rule text files are generated and cross-reference selected atoms, counts, solve time, regret, action agreement, and rule text. |

## Non-Goals

- Do not require dual atoms to outperform pressure atoms in Phase 2.
- Do not claim closed-loop traffic-control performance from sparse recovery outputs.
- Do not introduce GPU-heavy training, AMPL-only dependencies, or a new unrelated recovery pipeline.

## Phase Completion Criteria

Phase 2 passes when the quick gate command produces complete JSON/CSV/TXT artifacts, the schema gates are true, and at least one K > 1 run solves successfully while preserving explicit Phase 3 claim deferral in the output note.
