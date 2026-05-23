---
phase: 04-closed-loop-sumo-evaluation
plan: "03"
subsystem: closed-loop-reporting
tags: [python, markdown, csv, closed-loop, claim-discipline]

requires:
  - phase: 04-closed-loop-sumo-evaluation
    provides: Plan 04-02 Block 4 suite JSON with raw rows, aggregates, baseline coverage, and completion gates.
provides:
  - Deterministic Markdown renderer for Block 4 closed-loop report.
  - CSV export for raw seed rows and aggregate rows.
  - Report-level validation of completion gates and overclaim guardrails.
affects: [phase-04-closed-loop-sumo, CLOP-01, CLOP-02, CLOP-03, CLOP-04, CLOP-05]

tech-stack:
  added: []
  patterns:
    - Render human-facing closed-loop evidence from JSON without manual metric transcription.
    - Validate arterial/grid 5-seed gates and real scenario manipulations before reporting.
    - Preserve pressure-equivalent generalized-pressure framing.

key-files:
  created:
    - scripts/render_closed_loop_report.py
    - experiments/dual_sensitivity/block4_closed_loop_suite_report.md
    - experiments/dual_sensitivity/block4_closed_loop_suite.csv
  modified:
    - tests/test_closed_loop_sumo.py

key-decisions:
  - "Renderer refuses to report incomplete arterial/grid core-baseline seed gates."
  - "Renderer requires real demand-shift and failure-mode completion gates before report generation."
  - "Report states pressure-equivalent and generalized-pressure symbolic recovery, not dual superiority."

patterns-established:
  - "render_closed_loop_report.render_report(payload, input_path) returns deterministic Markdown after schema/gate validation."
  - "render_closed_loop_report.write_csv(payload, csv_path) writes seed and aggregate rows for downstream tables."

requirements-completed: [CLOP-01, CLOP-02, CLOP-03, CLOP-04, CLOP-05]

completed: 2026-05-23
---

# Phase 4 Plan 03: Closed-Loop Report Summary

Rendered the Phase 4 closed-loop SUMO suite into reproducible Markdown and CSV artifacts with pressure-equivalent claim discipline.

## Accomplishments

- Created `scripts/render_closed_loop_report.py` with top-level schema validation, completion-gate validation, Markdown rendering, CSV export, and forbidden-phrase guardrails.
- Updated `tests/test_closed_loop_sumo.py` with renderer tests for report/CSV generation and incomplete gate rejection.
- Generated `experiments/dual_sensitivity/block4_closed_loop_suite_report.md` from the raw suite JSON.
- Generated `experiments/dual_sensitivity/block4_closed_loop_suite.csv` with seed and aggregate rows.

## Verification Results

Passed:

- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 -m py_compile scripts/render_closed_loop_report.py tests/test_closed_loop_sumo.py`
- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 tests/test_closed_loop_sumo.py`
- Renderer command wrote `block4_closed_loop_suite_report.md` and `block4_closed_loop_suite.csv`.
- Final assertions printed `closed-loop report ok`.

Materialized report checks:

| Field | Value |
|---|---|
| Route decision | `pressure-equivalent` |
| Required framing | generalized-pressure symbolic recovery |
| Core seed gates | 5 completed seeds per arterial/grid core baseline |
| Demand-shift gate | true |
| Failure-mode gate | true |
| Forbidden overclaim language | absent |

## Notes

The report records SUMO emergency-braking warnings as simulator-behavior caveats and states that the completed local main suite used a short horizon to satisfy required seed gates within local runtime.

## Next Phase Readiness

Phase 4 is ready for code review and verification. Phase 5 can use the Block 4 JSON/CSV/report artifacts in reproducibility documentation and table-generation paths.
