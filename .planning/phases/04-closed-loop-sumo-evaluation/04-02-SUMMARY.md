---
phase: 04-closed-loop-sumo-evaluation
plan: "02"
subsystem: closed-loop-sumo-suite
tags: [python, sumo, traci, closed-loop, confidence-intervals, baselines]

requires:
  - phase: 04-closed-loop-sumo-evaluation
    provides: Plan 04-01 closed-loop runner and smoke metric schema.
provides:
  - Multi-network closed-loop suite orchestrator.
  - Full Phase 4 baseline coverage metadata.
  - Raw per-seed and aggregate CI-ready Block 4 suite JSON.
  - Completed arterial/grid 5-seed core baseline gates.
  - Real demand-shift and bottleneck/failure-mode scenario manipulations.
affects: [phase-04-closed-loop-sumo, CLOP-01, CLOP-02, CLOP-03, CLOP-04, CLOP-05]

tech-stack:
  added: []
  patterns:
    - Keep all baseline names explicit in controller registry and baseline_coverage.
    - Mark only non-adaptable PI-Light/full-dual rows as not_feasible with explicit reasons.
    - Gate Phase 4 completion on completed seeds and real scenario manipulation metadata.

key-files:
  created:
    - scripts/run_closed_loop_suite.py
    - experiments/dual_sensitivity/block4_closed_loop_suite.json
  modified:
    - scripts/run_closed_loop_sumo.py
    - tests/test_closed_loop_sumo.py

key-decisions:
  - "Use 150-step main runs to complete 5 seeds for arterial/grid core baselines within local runtime while recording the shorter horizon."
  - "Treat local_pilight as not_feasible because no safely adaptable PI-Light local DSL baseline is present in the SUMO runner interface; do not relabel a queue heuristic as PI-Light."
  - "Treat full_dual_symbolic as not_feasible until live per-TLS dual Scenario conversion is safe for actuation."
  - "Use TraCI vehicle insertion for demand-shift and edge speed reduction for bottleneck/failure-mode evidence."

patterns-established:
  - "run_closed_loop_suite.build_suite_spec(...) defines single, arterial, grid, demand-shift, and bottleneck/failure-mode scenarios."
  - "run_closed_loop_suite.aggregate_results(...) emits mean, standard error, and 95% CI by network/scenario/controller."
  - "completion_gates ensure arterial/grid core baselines have 5 completed seeds and real scenario manipulations are present."

requirements-completed: [CLOP-01, CLOP-02, CLOP-03, CLOP-04, CLOP-05]

completed: 2026-05-23
---

# Phase 4 Plan 02: Closed-Loop SUMO Suite Summary

Expanded the smoke runner into a multi-network closed-loop SUMO suite with baseline coverage, CI-ready aggregation, and completed Phase 4 gates.

## Accomplishments

- Expanded `scripts/run_closed_loop_sumo.py` to support `single`, `arterial`, and `grid_4x4` networks plus the full CLOP-02 controller registry.
- Added honest infeasibility metadata for `local_pilight` and `full_dual_symbolic` instead of substituting unrelated heuristics.
- Created `scripts/run_closed_loop_suite.py` with smoke/main profiles, suite specification, baseline coverage, aggregate CI computation, and completion gates.
- Updated `tests/test_closed_loop_sumo.py` to cover controller registry completeness, network resolution, infeasible controller metadata, suite spec contents, aggregation, and gates.
- Generated `experiments/dual_sensitivity/block4_closed_loop_suite.json` with 104 raw rows and 26 aggregate rows.

## Verification Results

Passed:

- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 -m py_compile scripts/run_closed_loop_sumo.py scripts/run_closed_loop_suite.py tests/test_closed_loop_sumo.py`
- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 tests/test_closed_loop_sumo.py`
- Smoke suite run wrote `/tmp/block4_closed_loop_suite_smoke.json` with 40 rows.
- Main suite run wrote `experiments/dual_sensitivity/block4_closed_loop_suite.json`.
- Artifact assertions printed `closed-loop suite artifact ok`.

Materialized suite summary:

| Field | Value |
|---|---|
| Route decision | `pressure-equivalent` |
| Raw rows | 104 |
| Aggregate rows | 26 |
| Completion gates passed | true |
| Scenarios | single_sanity, arterial_main, grid_scalability, arterial_demand_shift, arterial_bottleneck_failure_mode |
| Core arterial seeds | 5 per core baseline |
| Core grid seeds | 5 per core baseline |
| Demand-shift mechanism | `traci_vehicle_insertion` |
| Failure-mode mechanism | `edge_speed_reduction` |

## Notes

SUMO emitted emergency braking warnings during several closed-loop runs. The runs completed and artifacts were written; these warnings should be reported as simulator-behavior caveats in Plan 04-03.

## Next Phase Readiness

Plan 04-03 can render the raw suite JSON into Markdown/CSV, surface baseline coverage and completion gates, and preserve the Phase 3 pressure-equivalent framing.
