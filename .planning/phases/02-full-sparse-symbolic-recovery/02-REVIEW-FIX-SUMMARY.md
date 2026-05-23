---
phase: 02-full-sparse-symbolic-recovery
review_fix: true
completed: 2026-05-23
files_modified:
  - scripts/run_sparse_recovery.py
  - experiments/dual_sensitivity/block2_sparse_recovery.json
  - experiments/dual_sensitivity/block2_sparse_recovery.csv
  - experiments/dual_sensitivity/block2_sparse_recovery_rules.txt
  - .planning/phases/02-full-sparse-symbolic-recovery/02-REVIEW.md
---

# Phase 2 Review Fix Summary

## Fixed Findings

- **CR-01:** Public recovery objective fields now report the realized rule regret plus penalties, so `objective_value_with_penalties` no longer presents the solver's optimistic tie-selected `y` regret as the recovered rule's regret. The original solver objective remains available as `solver_objective_value` for diagnostics.
- **CR-02:** Atom category indices are deduplicated before counting and penalty application, so genuine dual and placebo atoms are not double-counted.
- **WR-01:** Dual-vs-pressure comparison outputs were moved out of Phase 2 gate fields into `phase3_candidate_diagnostics` with a non-gating note.
- **WR-02:** Added `gate_multi_atom_program_observed` so Phase 2 distinguishes K>1 solved capacity from actually observing a selected multi-atom program on the current sample.

## Validation

- `python3 -m py_compile scripts/run_sparse_recovery.py`
- `python3 scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json --budgets 1 2 3 --out experiments/dual_sensitivity/block2_sparse_recovery.json --csv-out experiments/dual_sensitivity/block2_sparse_recovery.csv --rules-out experiments/dual_sensitivity/block2_sparse_recovery_rules.txt`
- JSON assertions confirmed: status `PASSED`, no Phase 3 comparison gates, deduplicated dual/placebo counts, and public objective equals realized regret plus total penalty.
- Re-review result: clean.
