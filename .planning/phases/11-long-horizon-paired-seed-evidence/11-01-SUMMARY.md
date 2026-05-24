---
phase: 11-long-horizon-paired-seed-evidence
plan: 01
subsystem: research-evidence-gate
tags: [sumo, paired-statistics, gate-c, finite-storage, scipy]

requires:
  - phase: 10-strong-baselines-and-stress-scenario-suite
    provides: strong feasible baseline names and binding stress scenario tags
  - phase: 08-live-finite-storage-primal-dual-controller
    provides: finite_storage_primal_dual row audit and action decomposition contract
provides:
  - Phase 11 binding-only paired-seed spec/profile helper layer
  - Direction-aware paired Gate C primary-metric statistical rule
  - Fail-closed Gate C evaluator and bounded claim-scope validation primitives
affects: [phase-11-plan-02, phase-11-plan-03, gate-c, paired-seed-evidence]

tech-stack:
  added: []
  patterns: [direct executable Python tests, paired bootstrap statistics, fail-closed JSON evidence validation]

key-files:
  created:
    - scripts/run_phase11_paired_evidence.py
    - tests/test_phase11_paired_evidence.py
  modified: []

key-decisions:
  - "Gate C helper semantics are binding-regime-only and require all D-11-04 primary metrics instead of a single objective metric."
  - "Pilot/spec-only artifacts are pipeline validation only; complete Gate C evidence requires main-profile 3600/900 rows."

patterns-established:
  - "Phase 11 specs enumerate scenario/controller/seed/demand-multiplier rows with explicit demand behavior contracts."
  - "Gate C statistics use paired seed differences and fail closed before interpreting malformed evidence."

requirements-completed: [GATE-03, EXP-03, EXP-05]

duration: 7min 13s
completed: 2026-05-24
---

# Phase 11 Plan 01: Long-Horizon Paired-Seed Evidence Contract Summary

**Binding-regime-only Phase 11 evidence contracts with paired-seed Gate C statistics and fail-closed claim validation**

## Performance

- **Duration:** 7min 13s
- **Started:** 2026-05-24T10:43:45Z
- **Completed:** 2026-05-24T10:50:58Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Added `scripts/run_phase11_paired_evidence.py` with Phase 11 constants, main/pilot spec construction, paired demand-multiplier contracts, and Phase 10 non-reuse metadata.
- Implemented all D-11-04 primary metrics with direction-aware paired seed differences, paired bootstrap confidence intervals, paired diagnostics, effect sizes, and Holm-Bonferroni family metadata.
- Added fail-closed Gate C primitives that reject missing scenarios/comparators/metrics/provenance/audit fields, classify slack rows as context only, and reject forbidden overclaiming language.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define Phase 11 evidence profile contracts and demand multiplier contract tests** - `5afeea1` (feat)
2. **Task 2: Implement paired statistics and reusable Gate C primary-metric family rule** - `02126fe` (feat)
3. **Task 3: Add Gate C core evaluator, demand provenance validation, and claim-discipline primitives** - `6787796` (feat)

**Plan metadata:** pending final docs commit

## Files Created/Modified

- `scripts/run_phase11_paired_evidence.py` - Phase 11 profile/spec helpers, paired statistics, Gate C evaluator, demand provenance checks, and claim-scope validation.
- `tests/test_phase11_paired_evidence.py` - Fast synthetic direct-assertion tests for spec construction, metric rule behavior, fail-closed Gate C validation, and forbidden claim text.

## Decisions Made

- Used `route_demand_scaling` as the default demand multiplier contract method while allowing `insertion_intensity_scaling` as a valid actual-SUMO-behavior alternative for later runner work.
- Treated exact-zero paired confidence intervals as `INCONCLUSIVE` rather than passed non-worsening, preserving the plan's requirement for at least one strict positive signal per family.

## Deviations from Plan

None - plan executed as written.

## Issues Encountered

- SciPy emits precision-loss warnings on intentionally identical synthetic paired differences; tests still pass and the helper handles constant differences deterministically.
- Pre-existing uncommitted/untracked files from earlier phases were present in the main worktree and were left untouched except for the plan-specific files.

## User Setup Required

None - no external service configuration required.

## Verification

- `python /home/samuel/projects/pi_light_OR/tests/test_phase11_paired_evidence.py`
- `grep -v '^#' /home/samuel/projects/pi_light_OR/scripts/run_phase11_paired_evidence.py | grep -c 'GATE_C_PRIMARY_METRICS'` returned greater than 0 via the combined verification command.

## Known Stubs

None detected in files created by this plan.

## Next Phase Readiness

Phase 11 Plan 02 can consume the spec builder, demand multiplier contract fields, and shared Gate C metric rule without redefining evidence semantics. Phase 11 Plan 03 can reuse the fail-closed evaluator and claim validation primitives for a strict checker.

## Self-Check: PASSED

- Created files exist: `scripts/run_phase11_paired_evidence.py`, `tests/test_phase11_paired_evidence.py`, and this summary.
- Task commits recorded: `5afeea1`, `02126fe`, `6787796`.

---
*Phase: 11-long-horizon-paired-seed-evidence*
*Completed: 2026-05-24*
