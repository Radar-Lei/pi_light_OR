---
phase: 01-theoretical-core-and-claim-lock
plan: 01
subsystem: theory
tags: [traffic-control, dual-sensitivity, max-pressure, ctM-lite, linear-programming]

requires:
  - phase: initialization
    provides: project claim discipline and Phase 1 theory scope
provides:
  - THRY-01 continuous capacitated traffic-network relaxation
  - THRY-02 movement-level dual-sensitivity decomposition
  - Sign convention aligned to scripts/run_dual_sanity.py equality_duals[up] - equality_duals[down]
affects: [phase-01, phase-02-sparse-recovery, phase-03-pressure-failure-kill-gate]

tech-stack:
  added: []
  patterns: [Markdown technical memo, script-gate validation, LP shadow-price notation]

key-files:
  created:
    - refine-logs/THEORY_AND_CLAIMS.md
  modified: []

key-decisions:
  - "Use a Markdown technical memo as the Phase 1 theory artifact for THRY-01 and THRY-02."
  - "Keep corridor/service dual terms explicitly model-dependent: no primal constraint means no claimed corridor dual."
  - "Define positive movement value as objective improvement using equality_duals[up] - equality_duals[down]."

patterns-established:
  - "Theory sections map requirement IDs directly to reviewer-facing model definitions and lemmas."
  - "Validation evidence is cited as notation consistency, not closed-loop performance evidence."

requirements-completed: [THRY-01, THRY-02]

duration: 2min 24s
completed: 2026-05-22
---

# Phase 01 Plan 01: Theoretical Core and Claim Lock Summary

**Continuous capacitated traffic-network relaxation and dual-sensitivity decomposition aligned to the Block 0 LP sanity scaffold**

## Performance

- **Duration:** 2min 24s
- **Started:** 2026-05-22T16:13:38Z
- **Completed:** 2026-05-22T16:16:02Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Created `refine-logs/THEORY_AND_CLAIMS.md` with Phase 1 purpose, claim guardrails, notation, assumptions, and THRY-01 model definition.
- Added THRY-02 sign convention, movement-level dual-sensitivity decomposition, lemma, proof sketch, and validation-code alignment.
- Verified all plan-level checks, including `python scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create THRY-01 capacitated relaxation section** - `d5f4539` (docs)
2. **Task 2: Add THRY-02 dual-sensitivity decomposition** - `3fda38e` (docs)

**Plan metadata:** pending final summary commit

## Files Created/Modified

- `refine-logs/THEORY_AND_CLAIMS.md` - Main Phase 1 theory and claim-lock memo containing THRY-01 and THRY-02.
- `.planning/phases/01-theoretical-core-and-claim-lock/01-01-SUMMARY.md` - Execution summary for plan 01-01.

## Decisions Made

- Used the requested `refine-logs/THEORY_AND_CLAIMS.md` path rather than creating alternate theory memo names.
- Kept the artifact as a technical memo and did not add empirical dominance claims.
- Treated `scripts/run_dual_sanity.py` as validation evidence for notation and sign convention, not as the source of paper notation.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Repository contains pre-existing uncommitted planning changes in `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/config.json`, and untracked `.planning/phases/` content. These were left untouched except for the plan summary file required by this execution.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None found in files created/modified by this plan.

## Threat Flags

None. The plan created documentation only and introduced no new network endpoints, authentication paths, file-access flows, or schema trust boundaries.

## Verification

- `test -f refine-logs/THEORY_AND_CLAIMS.md` — passed
- `grep -q "THRY-01" refine-logs/THEORY_AND_CLAIMS.md` — passed
- `grep -q "THRY-02" refine-logs/THEORY_AND_CLAIMS.md` — passed
- `python scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json` — passed

## Next Phase Readiness

The theory memo is ready for the next Phase 1 plans to add pressure/backpressure special-case content, binding-regime scarcity corrections, and finite-dictionary recovery statements without changing the THRY-01/THRY-02 sign convention.

## Self-Check: PASSED

- Created file exists: `refine-logs/THEORY_AND_CLAIMS.md`
- Summary file exists: `.planning/phases/01-theoretical-core-and-claim-lock/01-01-SUMMARY.md`
- Task commit exists: `d5f4539`
- Task commit exists: `3fda38e`

---
*Phase: 01-theoretical-core-and-claim-lock*
*Completed: 2026-05-22*
