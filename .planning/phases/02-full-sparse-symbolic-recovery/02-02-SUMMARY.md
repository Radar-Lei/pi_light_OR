---
phase: 02-full-sparse-symbolic-recovery
plan: 02
subsystem: recovery
tags: [python, scipy, highs, sparse-recovery, milp, regret-objective]
requires:
  - phase: 02-full-sparse-symbolic-recovery
    provides: explicit sparse-recovery atom metadata registry and library selection from 02-01
provides:
  - K-atom sparse recovery with --budgets and --max-atoms controls
  - metadata-driven neighbor, genuine dual, and placebo hard atom budgets
  - regret-first objective metadata with realized regret and penalty breakdown outputs
affects: [phase-2, phase-3-static-pressure-failure-kill-gate]
tech-stack:
  added: []
  patterns:
    - metadata-driven MILP category constraints over z variables
    - regret-first objective reporting with diagnostic action agreement
key-files:
  created:
    - .planning/phases/02-full-sparse-symbolic-recovery/02-02-SUMMARY.md
  modified:
    - scripts/run_sparse_recovery.py
key-decisions:
  - "Kept empirical oracle regret/value gap as the MILP action-choice objective and left action agreement as diagnostic output."
  - "Derived neighbor, genuine dual, and placebo counts from ATOM_REGISTRY metadata rather than atom-name heuristics."
  - "Kept Phase 2 outputs sample-relative and deferred dual-vs-pressure empirical claim routing to Phase 3."
patterns-established:
  - "solve_library() receives hard atom budgets and soft penalties, then applies category constraints over z_j variables."
  - "Successful runs use status SOLVED and include realized regret, max regret, objective_with_penalties, and penalty_breakdown."
requirements-completed: [RECV-01, RECV-02, RECV-03]
duration: 6min
completed: 2026-05-22
---

# Phase 2 Plan 02: K-Atom Regret-First Sparse Recovery Summary

**K-atom MILP recovery now optimizes oracle regret with explicit size, neighbor, genuine dual, and placebo budget/penalty accounting.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-05-22T17:42:24Z
- **Completed:** 2026-05-22T17:48:47Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Added explicit K controls through preserved `--budgets` sweeps and `--max-atoms` single-run alias.
- Added `--max-neighbor-atoms`, `--max-dual-atoms`, `--max-placebo-atoms`, and `--time-limit-sec` with fail-fast nonnegative validation before MILP solving.
- Added metadata-driven hard constraints over selected atom variables for neighbor, genuine dual, and placebo categories.
- Added soft penalties for complexity, neighbor atoms, genuine dual atoms, and placebo atoms while keeping realized regret separately reported.
- Added `objective_mode`, `objective_value_with_penalties`, `realized_total_regret`, `realized_mean_regret`, `max_regret`, `action_agreement`, category counts, `penalty_breakdown`, and rule text summaries to successful run payloads.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add K/budget CLI controls and metadata-driven MILP constraints** - `5ef3e44` (feat)
2. **Task 2: Preserve regret-first objective and expose penalty breakdown** - `a367eb0` (feat)
3. **Rule 1 follow-up: Preserve sparse recovery tie feasibility** - `021be26` (fix)

**Plan metadata:** pending final metadata commit

## Files Created/Modified

- `scripts/run_sparse_recovery.py` - Adds K-atom budget controls, category constraints, objective metadata, penalty reporting, realized regret metrics, and rule text summaries.
- `.planning/phases/02-full-sparse-symbolic-recovery/02-02-SUMMARY.md` - Documents execution, validation, deviations, and plan scope.

## Decisions Made

- Preserved `--budgets` as the sweep interface and used `--max-atoms` only as a clearer single-run alias when supplied.
- Treated `uses_dual and not is_placebo` as genuine dual membership, so random/permuted dual placebo remains separate from genuine dual-sensitivity atoms.
- Kept output status and note focused on recovery/schema completeness, not Phase 3 dual-vs-pressure interpretation.

## Verification Results

- `python3 -m py_compile /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py` — passed.
- `python3 /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py --states /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/targeted_bottleneck_states.json --budgets 1 2 --max-neighbor-atoms 2 --max-dual-atoms 1 --max-placebo-atoms 1 --time-limit-sec 20 --out /tmp/phase2_budget_check.json` — passed; 12/12 runs solved and K>1 solved.
- `python3 /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py --states /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/targeted_bottleneck_states.json --budgets 1 2 3 --objective oracle_regret --complexity-penalty 0.0001 --neighbor-penalty 0.0 --dual-penalty 0.0 --placebo-penalty 0.0 --out /tmp/phase2_regret_check.json` plus JSON assertions — passed; 15/15 runs solved and all required regret/penalty fields were present.
- Overall plan check `--budgets 1 2 3 --objective oracle_regret` plus field inspection — passed with `status: PASSED` and at least one solved K>1 run.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Restored feasible tie handling in K>1 MILP solves**
- **Found during:** Task 2 validation after adding rule text and objective fields.
- **Issue:** An implementation detail tightened the big-M action-choice inequality by `tie_margin`, making several K>1 runs infeasible even though the planned recovery problem should permit ties.
- **Fix:** Kept validation for nonnegative `--tie-margin` but restored the original non-tightened big-M action constraints.
- **Files modified:** `scripts/run_sparse_recovery.py`
- **Verification:** Re-ran Task 1 budget validation, Task 2 regret validation, and overall plan validation; all passed with solved K>1 runs.
- **Committed in:** `021be26`

---

**Total deviations:** 1 auto-fixed bug.
**Impact on plan:** The fix was required for correctness and did not expand scope beyond K-atom regret-first sparse recovery.

## Known Stubs

None found. The only empty/default literals in the modified paths are CLI defaults or fallback lists, not UI/data stubs that prevent the plan goal.

## Threat Flags

None. The modified script only extends local CLI-to-MILP controls already covered by the plan threat model; no new network, auth, file-access, or schema trust boundary was introduced.

## Issues Encountered

- Existing repository state contained unrelated modified/untracked planning artifacts before execution. They were left untouched and not included in task commits.
- The validation output `/tmp/phase2_budget_check.json` and `/tmp/phase2_regret_check.json` was intentionally left under `/tmp` and not committed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Wave 3 can now add JSON/CSV/rule text schema gates on top of stable run fields: `objective_mode`, K budgets, category counts, realized regret, penalty breakdown, and `rule_text`. Phase 3 claim interpretation remains deferred.

## Self-Check: PASSED

- Found `scripts/run_sparse_recovery.py`.
- Found `.planning/phases/02-full-sparse-symbolic-recovery/02-02-SUMMARY.md`.
- Found task commits `5ef3e44`, `a367eb0`, and `021be26` in git log.

---
*Phase: 02-full-sparse-symbolic-recovery*
*Completed: 2026-05-22*
