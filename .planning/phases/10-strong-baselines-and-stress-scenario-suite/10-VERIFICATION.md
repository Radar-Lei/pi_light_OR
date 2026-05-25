---
phase: 10-strong-baselines-and-stress-scenario-suite
status: passed
verified: 2026-05-24
requirements:
  - EXP-01
  - EXP-02
  - EXP-04
---

# Phase 10 Verification

## Verdict

PASS — Phase 10 adds honest strong baseline coverage and explicit stress scenario suite coverage as smoke/spec capability evidence, while preserving the boundary that Gate C, paired-seed dominance, long-horizon statistics, and manuscript claims remain out of scope.

## Must-Have Checks

1. Required feasible baselines are registered and covered: `fixed_time`, `actuated_local_pressure`, `max_pressure`, `capacity_aware_pressure`, `cycle_pressure`, `finite_storage_double_pressure`, and `finite_storage_primal_dual` — PASS.
2. `local_pilight` and `full_dual_symbolic` remain guarded as `not_feasible` with actual artifact rows — PASS.
3. Stress scenario coverage includes downstream blockage, spillback, incident/capacity drop, oversaturation, turning shock, and switching-loss-sensitive categories — PASS.
4. Stress coverage fails closed unless scenario rows and expected mechanism evidence exist — PASS.
5. Grid fixed-time counterexample metadata exists before broad performance language — PASS.
6. Optimized fixed-time is explicitly documented as a current limitation, not claimed as implemented tuning/search — PASS.
7. Phase 10 artifact is `SMOKE_ONLY` and includes scope caveats preventing dominance interpretation — PASS.

## Verification Commands

```bash
python3 -m py_compile scripts/run_closed_loop_sumo.py scripts/run_closed_loop_suite.py scripts/render_closed_loop_report.py tests/test_closed_loop_sumo.py
python3 -m pytest tests/test_closed_loop_sumo.py -q
python3 scripts/run_closed_loop_suite.py --profile smoke --controllers fixed_time actuated_local_pressure max_pressure capacity_aware_pressure cycle_pressure finite_storage_double_pressure finite_storage_primal_dual local_pilight full_dual_symbolic --steps 80 --warmup 20 --action-interval 10 --out experiments/dual_sensitivity/phase10_baselines_stress_suite.json
python3 -m pytest tests/test_closed_loop_sumo.py tests/test_slack_binding_gates.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q
python3 tests/test_closed_loop_sumo.py
```

## Results

- Compile: passed.
- Phase 10 closed-loop pytest: 30 passed.
- Artifact generation: passed, wrote `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` with `status: SMOKE_ONLY`, 99 raw rows, `strong_baseline_coverage.passed: true`, and `stress_scenario_coverage.passed: true`.
- Relevant regression pytest: 66 passed.
- Script-style closed-loop tests: passed.

## Code Review

Initial review found fail-open coverage issues. Fixes applied:

- Required strong baselines now require `status: run`.
- Guarded infeasible controllers now require actual `not_feasible` rows.
- Stress scenario coverage now requires completed/run rows and expected mechanism evidence.
- Unknown controllers now fail closed in suite and runner code paths.
- Phase 10 artifact now uses a Phase 10 experiment id and Phase 10 capability-only claim framing.

## Scope Audit

Phase 10 did not add Gate C, paired-seed statistical dominance checks, long-horizon evidence, manuscript text, deployment claims, or broad performance dominance language. The generated artifact is explicitly smoke/spec capability evidence only.
