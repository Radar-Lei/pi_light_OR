---
phase: 03-static-pressure-failure-kill-gate
plan: "02"
subsystem: experiment-runner
tags: [python, scipy, sparse-recovery, static-kill-gate, dual-sensitivity, pressure]

requires:
  - phase: 02-full-sparse-symbolic-recovery
    provides: Phase 2 sparse recovery core, atom libraries, example construction, solver, and rule rendering contracts.
  - phase: 03-static-pressure-failure-kill-gate
    provides: Plan 03-01 labeled static-regime state fixture for valid-example kill-gate analysis.
provides:
  - Phase 3 static kill-gate runner that groups samples by regime and reuses Phase 2 sparse recovery.
  - Per-regime dual_sensitivity vs pressure_backpressure metrics with sample sufficiency and route decision fields.
  - Block 3 JSON, CSV, rule text, and static-only route report artifacts.
affects: [phase-03-static-kill-gate, phase-04-closed-loop-sumo, KILL-02, KILL-03, KILL-04, KILL-05]

tech-stack:
  added: []
  patterns:
    - Reuse run_sparse_recovery atoms_for_library, build_example, solve_library, and imported conversion/LP summary functions.
    - Align dual and pressure result rows by source/scenario before computing tie-aware wins and regrets.

key-files:
  created:
    - scripts/run_static_kill_gate.py
    - experiments/dual_sensitivity/block3_static_kill_gate.json
    - experiments/dual_sensitivity/block3_static_kill_gate.csv
    - experiments/dual_sensitivity/block3_static_kill_gate_rules.txt
    - experiments/dual_sensitivity/block3_static_kill_gate_report.md
  modified: []

key-decisions:
  - "Route Phase 3 static evidence to pressure-equivalent because all six supported/proxy regimes tie pressure on oracle regret under the generated fixture."
  - "Treat legacy unlabeled fixtures as preliminary/proxy evidence when --default-regime is used, while preserving schema validation and input_labeling_notes."
  - "Keep the generated Markdown route report as a runner artifact for KILL-05 traceability, but do not execute the separate 03-03 standalone renderer."

patterns-established:
  - "Static kill-gate JSON stores thresholds, raw and valid counts, per-regime metrics, runs_by_regime, route rationale, and caveats."
  - "CSV exposes KILL-02 metrics and selected atom lists per regime; rules text groups finite-dictionary sample-relative rules by regime and library."
  - "Sample sufficiency is computed from valid converted examples, not raw JSON sample counts."

requirements-completed: [KILL-02, KILL-03, KILL-04]

duration: 6min
completed: 2026-05-22
---

# Phase 3 Plan 02: Static Kill-Gate Metrics and Route Summary

**Per-regime static dual-vs-pressure kill gate using Phase 2 sparse recovery, routing the current fixture to pressure-equivalent evidence.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-05-22T19:01:33Z
- **Completed:** 2026-05-22T19:07:29Z
- **Tasks:** 3 completed
- **Files modified:** 6 created/modified

## Accomplishments

- Created `scripts/run_static_kill_gate.py`, a Phase 3 runner that groups labeled state samples by regime and reuses `run_sparse_recovery.py` functions instead of reimplementing LP, oracle, atom, or MILP logic.
- Added tie-aware KILL-02 aggregation for `dual_sensitivity` vs `pressure_backpressure`, including disagreement, win/tie rates, mean/worst regrets, selected atoms, recovered rules, and claim scope.
- Generated Block 3 artifacts from `experiments/dual_sensitivity/block3_regime_states.json`: JSON, CSV, rule text, and a static-only route report.
- Confirmed 1,200 valid converted examples and `sample_target_met=true`; all six regimes tied pressure with zero regret delta, so `route_decision=pressure-equivalent` with MEDIUM confidence.

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Add failing static kill gate behavior tests** - `089e821` (test; completed by previous executor and preserved)
2. **Task 1 GREEN: Build per-regime sparse-recovery runner** - `65780a6` (feat)
3. **Task 2: Compute KILL-02 metrics and KILL-04 route decision** - `0c2f312` (feat)
4. **Task 3: Write CSV and rule artifacts for generated regime fixture** - `336a7de` (chore)

## Files Created/Modified

- `scripts/run_static_kill_gate.py` - Main Phase 3 kill-gate runner with CLI validation, regime grouping, sparse-recovery solves, metrics, route selection, CSV/rules/report writers.
- `tests/test_run_static_kill_gate.py` - Existing RED behavior tests preserved from prior executor; verifies tie-aware disagreement and sample-shortfall routing.
- `experiments/dual_sensitivity/block3_static_kill_gate.json` - Machine-readable route decision, sample sufficiency, per-regime metrics, thresholds, caveats, and underlying solved runs.
- `experiments/dual_sensitivity/block3_static_kill_gate.csv` - Per-regime KILL-02 metric table with selected dual/pressure atoms and rule path.
- `experiments/dual_sensitivity/block3_static_kill_gate_rules.txt` - Recovered symbolic rule text grouped by regime and library.
- `experiments/dual_sensitivity/block3_static_kill_gate_report.md` - Static-only route report generated by the runner for traceability.

## Verification Results

Plan verification commands passed:

- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 -m py_compile scripts/run_static_kill_gate.py`
- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 tests/test_run_static_kill_gate.py` printed `static kill-gate tests ok`.
- Import/use gate passed: non-comment source contains `from run_sparse_recovery import` and uses `solve_library`.
- Quick legacy fixture command passed on `experiments/dual_sensitivity/targeted_bottleneck_states.json` with `--default-regime storage_binding_proxy`; JSON assertions printed `kill-gate metrics ok` / `overall quick validation ok`.
- Full generated fixture command passed on `experiments/dual_sensitivity/block3_regime_states.json`; CSV/rules assertions printed `full artifacts ok`.

Materialized full gate summary:

| Regime | Valid examples | Disagreement | Dual win | Pressure win | Tie | Δ regret pressure-dual |
|---|---:|---:|---:|---:|---:|---:|
| corridor_bottleneck_proxy | 200 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| demand_shift_proxy | 200 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| incident_capacity_drop | 200 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| slack | 200 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| storage_binding | 200 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| supply_binding_proxy | 200 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |

## Decisions Made

- Selected `pressure-equivalent` as the machine route because dual and pressure have tie-equivalent static oracle regret across all solved regimes.
- Kept route language static/sample-relative and explicitly deferred closed-loop interpretation to later phases.
- Included a runner-generated Markdown report for KILL-05 traceability because the plan required `--report-out`; the standalone 03-03 report renderer was not executed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Preserved and used existing RED tests from prior executor**
- **Found during:** Continuation start / Task 1
- **Issue:** The plan marked Tasks 1 and 2 as TDD, and the previous executor had already committed failing behavior tests in `089e821`. Recreating or replacing them would risk invalidating the RED gate.
- **Fix:** Kept `tests/test_run_static_kill_gate.py` intact and implemented `compare_dual_pressure()` / `decide_route()` to satisfy those tests.
- **Files modified:** `scripts/run_static_kill_gate.py`
- **Verification:** `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 tests/test_run_static_kill_gate.py` passed.
- **Committed in:** `65780a6`, `0c2f312`

**2. [Rule 2 - Missing Critical] Wrote runner-generated report artifact required by CLI/output contract**
- **Found during:** Task 3
- **Issue:** The plan's required CLI includes `--report-out`, and validation context requires a route report artifact for KILL-05, even though user scope forbids running the 03-03 standalone report renderer.
- **Fix:** Implemented an internal deterministic `render_report()` in `run_static_kill_gate.py` and generated `block3_static_kill_gate_report.md` without invoking or creating the standalone 03-03 renderer.
- **Files modified:** `scripts/run_static_kill_gate.py`, `experiments/dual_sensitivity/block3_static_kill_gate_report.md`
- **Verification:** Quick and full gate commands both wrote `report_out`; JSON contains report path and static-only caveats.
- **Committed in:** `65780a6`, `336a7de`

---

**Total deviations:** 2 auto-fixed (2 missing critical)
**Impact on plan:** Both deviations were required for TDD continuity and output-contract completeness; no closed-loop or 03-03 standalone renderer scope was added.

## Issues Encountered

- The working tree contained unrelated modified/untracked files before execution. They were left untouched; only files directly needed for Plan 03-02 were staged and committed.
- The repository is on `main` and is not a GSD worktree (`.git` is a directory), so worktree-only protected branch assertions did not apply.

## Known Stubs

None found in created code/artifacts. The stub-pattern scan only matched normal Python defaults (`default=[]`) and CSV file opening (`newline=""`), neither of which is a UI/data stub.

## Threat Flags

None. The new surface is a local CLI experiment runner covered by the plan threat model; it validates sample schema, numeric CLI flags, library names, thresholds, and records thresholds/counts/caveats in JSON for route traceability.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 03-03 can consume `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.json` and related CSV/rules/report artifacts. The selected static route is `pressure-equivalent`, so downstream reporting should frame this as generalized-pressure symbolic recovery evidence rather than dual-over-pressure static superiority.

## Self-Check: PASSED

- Found created files:
  - `/home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py`
  - `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.json`
  - `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.csv`
  - `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_rules.txt`
  - `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_report.md`
  - `/home/samuel/projects/pi_light_OR/.planning/phases/03-static-pressure-failure-kill-gate/03-02-SUMMARY.md`
- Found task commits: `089e821`, `65780a6`, `0c2f312`, `336a7de`
- Verification commands completed successfully.

---
*Phase: 03-static-pressure-failure-kill-gate*
*Completed: 2026-05-22*
