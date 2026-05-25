---
phase: 10-strong-baselines-and-stress-scenario-suite
plan: 01
status: complete
completed: 2026-05-24
requirements:
  - EXP-01
  - EXP-02
  - EXP-04
---

# Phase 10 Plan 01 Summary

## Files Modified

- `scripts/run_closed_loop_sumo.py`
- `scripts/run_closed_loop_suite.py`
- `scripts/render_closed_loop_report.py`
- `tests/test_closed_loop_sumo.py`
- `experiments/dual_sensitivity/phase10_baselines_stress_suite.json`

## What Changed

- Added feasible Phase 10 baseline variants: `cycle_pressure` and `finite_storage_double_pressure`.
- Preserved `local_pilight` and `full_dual_symbolic` as honest `not_feasible` guarded controllers.
- Expanded the closed-loop suite with explicit stress scenario tags covering downstream blockage, spillback, incident/capacity drop, oversaturation, turning shock, and switching-loss-sensitive categories.
- Added Phase 10 payload metadata: `strong_baseline_coverage`, `stress_scenario_coverage`, `grid_fixed_time_counterexample_check`, `optimized_fixed_time_metadata`, and `phase10_scope_caveats`.
- Made baseline and stress coverage fail closed: required feasible baselines must have run rows, guarded infeasible controllers must have actual `not_feasible` rows, and stress scenarios must have completed rows plus expected mechanism evidence.
- Added unknown-controller validation in suite and runner paths.
- Regenerated `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` as a `SMOKE_ONLY` capability artifact with 99 rows.

## Tests Added

- Phase 10 registry coverage for `cycle_pressure` and `finite_storage_double_pressure`.
- Selectability tests for cycle pressure and finite-storage double-pressure behavior.
- Suite-spec tests verifying all required stress scenario tags are included.
- Payload tests for Phase 10 baseline/stress/grid/optimized-fixed-time/scope metadata.
- Negative tests verifying missing required baseline rows, missing guard rows, missing stress rows, and forged stress mechanisms fail closed.

## Verification Results

- `python3 -m py_compile scripts/run_closed_loop_sumo.py scripts/run_closed_loop_suite.py scripts/render_closed_loop_report.py tests/test_closed_loop_sumo.py` — passed.
- `python3 -m pytest tests/test_closed_loop_sumo.py -q` — 30 passed.
- `python3 scripts/run_closed_loop_suite.py --profile smoke --controllers fixed_time actuated_local_pressure max_pressure capacity_aware_pressure cycle_pressure finite_storage_double_pressure finite_storage_primal_dual local_pilight full_dual_symbolic --steps 80 --warmup 20 --action-interval 10 --out experiments/dual_sensitivity/phase10_baselines_stress_suite.json` — passed, artifact status `SMOKE_ONLY`.
- `python3 -m pytest tests/test_closed_loop_sumo.py tests/test_slack_binding_gates.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q` — 66 passed.
- `python3 tests/test_closed_loop_sumo.py` — passed.

## Scope Boundaries Preserved

- No Gate C implementation.
- No paired-seed dominance evidence.
- No long-horizon statistical claims.
- No manuscript drafting or broad dominance language.
- Optimized fixed-time is recorded as `documented_limit`, not silently conflated with ordinary `fixed_time`.
