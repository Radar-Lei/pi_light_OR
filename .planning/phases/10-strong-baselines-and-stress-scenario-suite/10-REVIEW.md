---
phase: 10-strong-baselines-and-stress-scenario-suite
status: clean_after_fixes
reviewed: 2026-05-24
requirements:
  - EXP-01
  - EXP-02
  - EXP-04
---

# Phase 10 Code Review

## Initial Findings

### Critical: Strong baseline coverage was fail-open

`strong_baseline_coverage()` initially allowed required baselines to be `not_requested` and treated guarded controllers as passing solely because they were registered in `NOT_FEASIBLE_CONTROLLERS`.

**Fix:** Required baselines must now have `status: run`, and `local_pilight` / `full_dual_symbolic` must have actual `not_feasible` rows.

### Critical: Stress scenario coverage only checked declarations

`stress_scenario_coverage()` initially passed if scenario tags were declared, even if no rows or mechanisms existed.

**Fix:** Coverage now requires completed/run rows and expected mechanism evidence per stress scenario tag.

### Critical: Suite accepted unknown controllers

`run_closed_loop_suite.py` did not validate controller names before invoking `run_experiment()`.

**Fix:** Added unknown-controller validation in suite `main()`, `run_experiment()`, `movement_score()`, and `choose_controller_action()`.

### Warning: Phase 10 artifact used Block 4 framing

The artifact initially used `block4_closed_loop_suite` and Phase 4 claim framing.

**Fix:** Artifact now uses `phase10_baselines_stress_suite` and Phase 10 capability-only claim framing.

## Follow-up Validation

- `python3 -m pytest tests/test_closed_loop_sumo.py -q` — 30 passed.
- `python3 -m pytest tests/test_closed_loop_sumo.py tests/test_slack_binding_gates.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q` — 66 passed.
- Regenerated `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` with `strong_baseline_coverage.passed: true` and `stress_scenario_coverage.passed: true`.

## Final Verdict

Clean after fixes. No remaining known Critical or Warning findings for Phase 10 scope.
