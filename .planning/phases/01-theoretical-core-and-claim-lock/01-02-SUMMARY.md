---
phase: 01-theoretical-core-and-claim-lock
plan: 02
subsystem: theory
tags: [traffic-control, max-pressure, backpressure, dual-sensitivity, scarcity-correction]

requires:
  - phase: 01-theoretical-core-and-claim-lock
    provides: THRY-01 relaxation and THRY-02 movement-level dual convention from plan 01-01
provides:
  - THRY-03 pressure/backpressure special-case theorem
  - THRY-04 binding-regime scarcity correction proposition
  - Phase 3 claim routing language for scarcity-correction empirical usefulness
affects: [phase-01, phase-02-sparse-recovery, phase-03-pressure-failure-kill-gate]

tech-stack:
  added: []
  patterns: [Markdown technical memo, theorem/proposition proof sketch, script-gate validation]

key-files:
  created:
    - .planning/phases/01-theoretical-core-and-claim-lock/01-02-SUMMARY.md
  modified:
    - refine-logs/THEORY_AND_CLAIMS.md

key-decisions:
  - "Frame ordinary max-pressure/backpressure as the slack or ranking-neutral special case of dual movement ranking."
  - "State scarcity deviations only as sufficient rank-change conditions tied to explicit primal constraints."
  - "Route empirical usefulness of binding-regime corrections to the Phase 3 static pressure-failure kill gate."

patterns-established:
  - "Pressure equivalence proofs should distinguish theorem assumptions from implementation alignment."
  - "Scarcity correction claims must be algebraic and model-dependent, not universal performance claims."

requirements-completed: [THRY-03, THRY-04]

duration: 2min 26s
completed: 2026-05-22
---

# Phase 01 Plan 02: Pressure Special Case and Scarcity Correction Summary

**Pressure/backpressure recovery theorem plus binding-regime scarcity rank-change proposition with Phase 3 claim routing**

## Performance

- **Duration:** 2min 26s
- **Started:** 2026-05-22T16:23:20Z
- **Completed:** 2026-05-22T16:25:46Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added `THRY-03 — Pressure/Backpressure Special Case` to `refine-logs/THEORY_AND_CLAIMS.md` with theorem assumptions, proof sketch, phase-score reduction, implementation alignment, and validation-code alignment.
- Added `THRY-04 — Binding-Regime Scarcity Correction` with a sufficient rank-change proposition comparing pressure gaps against modeled scarcity corrections.
- Preserved the claim boundary by avoiding universal max-pressure dominance language and routing empirical usefulness to Phase 3.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add THRY-03 pressure/backpressure special-case theorem** - `459881e` (docs)
2. **Task 2: Add THRY-04 binding-regime scarcity correction proposition** - `aed78f7` (docs)

**Plan metadata:** pending final summary commit

## Files Created/Modified

- `refine-logs/THEORY_AND_CLAIMS.md` - Extended Phase 1 theory memo with THRY-03 and THRY-04.
- `.planning/phases/01-theoretical-core-and-claim-lock/01-02-SUMMARY.md` - Execution summary for plan 01-02.

## Decisions Made

- Used the existing THRY-01/THRY-02 notation directly: movement value remains `lambda_i - lambda_j` and phase score is the sum over movement values.
- Treated `max_pressure.py` as implementation alignment for upstream-minus-downstream phase scoring, not as proof evidence.
- Deferred corridor/service correction claims unless a corresponding primal corridor/service constraint is explicitly written.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The repository still contains pre-existing uncommitted planning changes and untracked phase planning files. They were left untouched except for the required `01-02-SUMMARY.md`.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None found in files created/modified by this plan.

## Threat Flags

None. This plan modified documentation only and introduced no network endpoints, authentication paths, file-access flows, or schema trust boundaries.

## Verification

- `grep -q "THRY-03" refine-logs/THEORY_AND_CLAIMS.md` — passed
- `grep -q "THRY-04" refine-logs/THEORY_AND_CLAIMS.md` — passed
- `grep -q "binding-regime" refine-logs/THEORY_AND_CLAIMS.md` — passed
- `grep -Eq "scarcity|storage|supply" refine-logs/THEORY_AND_CLAIMS.md` — passed
- `grep -Eq "sufficient|rank" refine-logs/THEORY_AND_CLAIMS.md` — passed
- `! grep -E "universally dominates|always beats|guarantees superiority|dominates max-pressure" refine-logs/THEORY_AND_CLAIMS.md` — passed
- `python scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json` — passed

## Next Phase Readiness

Plan 01-03 can now add the finite-dictionary recovery-quality statement and reviewer-facing checklist using THRY-03 and THRY-04 as locked theory blocks.

## Self-Check: PASSED

- Modified file exists: `refine-logs/THEORY_AND_CLAIMS.md`
- Summary file exists: `.planning/phases/01-theoretical-core-and-claim-lock/01-02-SUMMARY.md`
- Task commit exists: `459881e`
- Task commit exists: `aed78f7`

---
*Phase: 01-theoretical-core-and-claim-lock*
*Completed: 2026-05-22*
