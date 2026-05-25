---
phase: 10-strong-baselines-and-stress-scenario-suite
status: complete
requirements:
  - EXP-01
  - EXP-02
  - EXP-04
---

# Phase 10 Pattern Map

## Existing Patterns to Reuse

| Need | Existing File | Pattern |
|---|---|---|
| Controller registration | `scripts/run_closed_loop_sumo.py` | `CONTROLLER_REGISTRY`, `movement_score`, `phase_score`, `choose_controller_action` |
| Scenario suite registration | `scripts/run_closed_loop_suite.py` | `SCENARIOS`, `build_suite_spec`, profile-specific seeds/controllers |
| Suite artifact | `scripts/run_closed_loop_suite.py` | `build_payload`, `baseline_coverage`, schema metadata |
| Stress mechanics | `scripts/run_closed_loop_sumo.py` | `demand_shift_tick`, `apply_failure_mode`, scenario tag checks |
| Tests | `tests/test_closed_loop_sumo.py` | synthetic payloads, suite spec, coverage/gate assertions |

## Expected Additions

### Runner

- Add lightweight controller variants if used: `cycle_pressure`, `finite_storage_double_pressure`.
- Add scenario metadata fields for explicit stress categories.
- Preserve `full_dual_symbolic` and `local_pilight` not-feasible honesty.

### Suite

- Expand `DEFAULT_CONTROLLERS` / coverage metadata to include `finite_storage_primal_dual` and new feasible baselines.
- Expand `SCENARIOS` or add stress scenario spec metadata for the six required stress categories.
- Add artifact fields such as `stress_scenario_coverage`, `strong_baseline_coverage`, `grid_fixed_time_counterexample_check`, and scope caveats.

### Tests

- Controller registry includes new feasible baselines and not-feasible guards remain intact.
- `build_suite_spec(profile="smoke")` includes stress scenario tags/categories.
- Stress coverage contains downstream blockage, spillback, incident capacity drop, oversaturation, turning shock, switching-loss-sensitive.
- Phase 10 artifact generation smoke runs short and records caveats; it must not assert dominance.

## Guardrails

- Do not implement Gate C.
- Do not add paired-seed CI/statistical tests.
- Do not run 3600–7200s experiments in Phase 10.
- Do not add manuscript text.
- Do not reinterpret short smoke as performance evidence.
