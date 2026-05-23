---
phase: 04-closed-loop-sumo-evaluation
plan: "01"
subsystem: closed-loop-sumo
tags: [python, sumo, traci, closed-loop, pressure-equivalent]

requires:
  - phase: 03-static-pressure-failure-kill-gate
    provides: Phase 3 pressure-equivalent route decision and claim caveats.
provides:
  - Real SUMO/TraCI closed-loop runner for single-intersection smoke evaluation.
  - Controller registry for fixed-time, max-pressure, and capacity-aware pressure.
  - CLOP-04 metric schema in JSON smoke artifact.
  - Phase 3 route metadata carried into Phase 4 outputs.
affects: [phase-04-closed-loop-sumo, CLOP-01, CLOP-02, CLOP-04]

tech-stack:
  added: []
  patterns:
    - Use TraCI to read queues, choose TLS phases, apply actions, and record closed-loop metrics.
    - Keep Phase 4 outputs pressure-equivalent and generalized-pressure framed.

key-files:
  created:
    - scripts/run_closed_loop_sumo.py
    - tests/test_closed_loop_sumo.py
    - experiments/dual_sensitivity/block4_closed_loop_smoke.json
  modified: []

key-decisions:
  - "Start Phase 4 with a real single-intersection SUMO smoke path before multi-network suite orchestration."
  - "Carry Phase 3 route_decision=pressure-equivalent into every closed-loop output."
  - "Treat fixed-time, max-pressure, and capacity-aware pressure as first-class smoke baselines."

patterns-established:
  - "run_closed_loop_sumo.run_experiment(...) returns one JSON-serializable controller/seed row with CLOP-04 metrics."
  - "choose_controller_action(...) supports deterministic fixed-time, max-pressure, and capacity-aware pressure action selection."

requirements-completed: [CLOP-01, CLOP-02, CLOP-04]

duration: TBD
completed: 2026-05-23
---

# Phase 4 Plan 01: Closed-Loop SUMO Smoke Runner Summary

Implemented the first real closed-loop SUMO/TraCI execution path for Phase 4.

## Accomplishments

- Created `scripts/run_closed_loop_sumo.py` with a reusable runner, controller registry, phase-action selection, route metadata loading, and JSON output generation.
- Added `tests/test_closed_loop_sumo.py` with stdlib tests for controller coverage, action selection, capacity-aware penalties, metric aggregation, and route metadata validation.
- Generated `experiments/dual_sensitivity/block4_closed_loop_smoke.json` from a real single-intersection TraCI run using `fixed_time`, `max_pressure`, and `capacity_aware_pressure`.
- Preserved Phase 3 claim discipline by carrying `route_decision: pressure-equivalent` and generalized-pressure symbolic recovery framing.

## Verification Results

Passed:

- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 -m py_compile scripts/run_closed_loop_sumo.py tests/test_closed_loop_sumo.py`
- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 tests/test_closed_loop_sumo.py`
- Single-intersection smoke command wrote `block4_closed_loop_smoke.json` with 3 controller rows.
- JSON assertions confirmed required CLOP-04 metrics and no forbidden dual-superiority phrasing.

## Notes

SUMO emitted emergency braking warnings during the smoke run. The run completed and wrote metrics; these warnings should be monitored in Plan 04-02 when longer arterial/grid experiments are added.

## Next Phase Readiness

Plan 04-02 can now build on `run_experiment(...)`, the controller registry, and the smoke metric schema to add arterial/grid networks, multi-seed suite orchestration, confidence intervals, demand-shift, and bottleneck/failure-mode scenarios.
