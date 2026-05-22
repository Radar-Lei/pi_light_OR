---
phase: 02-full-sparse-symbolic-recovery
plan: 01
subsystem: recovery
_tags: [python, scipy, highs, sparse-recovery, atom-registry]
requires:
  - phase: 01-theoretical-core-and-claim-lock
    provides: finite-dictionary recovery-regret framing and Phase 3 claim discipline
provides:
  - explicit sparse-recovery atom metadata registry
  - named library views with full_symbolic coverage
  - validated --libraries and --atom-families CLI selection contracts
affects: [phase-2, phase-3-static-pressure-failure-kill-gate]
tech-stack:
  added: []
  patterns:
    - metadata-driven atom family classification
    - fail-fast CLI validation before sparse MILP solving
key-files:
  created:
    - .planning/phases/02-full-sparse-symbolic-recovery/02-01-SUMMARY.md
  modified:
    - scripts/run_sparse_recovery.py
key-decisions:
  - "Preserved existing library names while adding full_symbolic as an all-family Phase 2 view."
  - "Classified dual and placebo atoms through explicit metadata fields rather than name inference."
  - "Kept summarize_scenario() as the sole oracle/dual/value source and avoided Phase 3 claim interpretation."
patterns-established:
  - "ATOM_REGISTRY defines family, neighbor, dual, placebo, expression, and description fields for every feature atom."
  - "Library and atom-family filtering happens before MILP solving and rejects unknown names early."
requirements-completed: [RECV-03, RECV-04]
duration: 6min
completed: 2026-05-22
---

# Phase 2 Plan 01: Atom Metadata Registry and Library Selection Summary

**Sparse recovery atoms now have explicit auditable metadata, full_symbolic coverage, and validated library/family selection interfaces.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-05-22T17:31:19Z
- **Completed:** 2026-05-22T17:37:56Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Added `ATOM_REGISTRY` for every current feature atom with `family`, `requires_neighbor`, `uses_dual`, `is_placebo`, `expression`, and `description` metadata.
- Preserved the existing named libraries and added `full_symbolic` containing all allowed Phase 2 atom families.
- Added `--libraries`, `--atom-families`, and `--max-atoms` CLI contracts with fail-fast validation for unknown libraries/families and empty selections.
- Added registry and selected-atom metadata into JSON output so downstream plans can count dual/placebo/neighbor categories without string-name heuristics.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add explicit atom metadata registry** - `7d52004` (feat)
2. **Task 2: Preserve named libraries and add family selection interface** - `787e17c` (feat)

**Plan metadata:** pending final metadata commit

## Files Created/Modified

- `scripts/run_sparse_recovery.py` - Adds atom registry metadata, `full_symbolic`, library/family selection helpers, and CLI flags.
- `.planning/phases/02-full-sparse-symbolic-recovery/02-01-SUMMARY.md` - Documents execution, commits, validation, and plan scope.

## Decisions Made

- Kept the recovery implementation in `scripts/run_sparse_recovery.py`; no new recovery pipeline was introduced.
- Treated `random_price` as a placebo family with `uses_dual: true` and `is_placebo: true`, while `dual_sensitivity` remains genuine dual with `is_placebo: false`.
- Allowed family filtering to skip named libraries with no atoms after filtering, but fail when the overall selected atom set is empty.
- Preserved Phase 3 claim discipline: no dual-vs-pressure empirical interpretation was added.

## Verification Results

- `python3 -m py_compile scripts/run_sparse_recovery.py` — passed.
- `grep -q "ATOM_REGISTRY" scripts/run_sparse_recovery.py` — passed.
- `grep -q "full_symbolic" scripts/run_sparse_recovery.py` — passed.
- `grep -q -- "--libraries" scripts/run_sparse_recovery.py` — passed.
- `grep -q -- "--atom-families" scripts/run_sparse_recovery.py` — passed.
- CLI smoke test with `--libraries full_symbolic --atom-families local capacity raw_neighbor pressure dual placebo --budgets 1 2` — completed and produced an `INCONCLUSIVE` scientific status as expected for current gates; this plan only validates schema/interface readiness.

## Deviations from Plan

None - plan executed within the requested scope. The only generated smoke-test JSON was removed after validation because Wave 1 did not require committing experiment artifacts.

## Known Stubs

None found in modified code. The scan only matched the intentional argparse default `default=[]` for repeated `--states`, which is not a UI/data-output stub.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: cli-input-validation | scripts/run_sparse_recovery.py | New `--libraries` and `--atom-families` inputs control which atoms enter recovery; mitigated with explicit allow-list validation before solving. |

## Issues Encountered

- Existing repository state contained unrelated modified/untracked planning artifacts before this execution. They were left untouched and not included in task commits.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02 can now enforce K-atom, neighbor, dual, and placebo budgets/penalties using registry metadata instead of inferring semantics from atom names. Plan 03 can use `selected_atom_metadata` and top-level `atom_registry` when emitting auditable JSON/CSV/rule artifacts.

## Self-Check: PASSED

- Found `scripts/run_sparse_recovery.py`.
- Found `.planning/phases/02-full-sparse-symbolic-recovery/02-01-SUMMARY.md`.
- Found task commits `7d52004` and `787e17c` in git log.

---
*Phase: 02-full-sparse-symbolic-recovery*
*Completed: 2026-05-22*
