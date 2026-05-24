---
phase: 11-long-horizon-paired-seed-evidence
plan: 03
subsystem: research-evidence-gate
tags: [gate-c, paired-statistics, fail-closed, json-artifact, sumo]

requires:
  - phase: 11-long-horizon-paired-seed-evidence
    provides: Phase 11 paired evidence contracts and main-profile input artifact from Plans 01-02
provides:
  - Standalone strict Phase 11 Gate C paired evidence checker
  - Machine-readable Gate C companion artifact for the Phase 11 main artifact
  - Synthetic tests for checker scope, demand provenance, profile eligibility, and claim discipline
affects: [phase-12-reproducibility, gate-c, paired-seed-evidence]

tech-stack:
  added: []
  patterns: [standalone JSON gate checker, shared Gate C rule import, fail-closed profile and demand provenance validation]

key-files:
  created:
    - scripts/run_gate_c_paired_evidence.py
    - experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json
  modified:
    - tests/test_phase11_paired_evidence.py

key-decisions:
  - "The standalone checker recomputes Gate C from raw scenario_results via Plan 01 shared helpers rather than trusting upstream status fields."
  - "Strict mode exits nonzero only for FAILED; documented INCONCLUSIVE remains zero to support fail-closed missing-evidence artifacts."
  - "Current Gate C output is honestly INCONCLUSIVE because the Phase 11 main artifact has no executed long-horizon rows."

patterns-established:
  - "Gate C companion artifacts expose profile_eligibility, demand_multiplier_provenance_summary, gate_c_primary_metrics_v1, binding/context/inconclusive/not_evidence sections, and caveats."
  - "Metadata-only demand provenance is an explicit checker failure even when synthetic metric rows would otherwise pass."

requirements-completed: [GATE-03, EXP-05]

duration: 4min 18s
completed: 2026-05-24
---

# Phase 11 Plan 03: Strict Gate C Paired Evidence Checker Summary

**Standalone fail-closed Gate C checker that recomputes binding-regime paired evidence and emits an INCONCLUSIVE companion artifact for missing executed rows**

## Performance

- **Duration:** 4min 18s
- **Started:** 2026-05-24T11:08:07Z
- **Completed:** 2026-05-24T11:12:25Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Added `scripts/run_gate_c_paired_evidence.py` with `--input`, `--out`, and `--strict`, JSON loading, shared Gate C recomputation, artifact writing, and compact JSON CLI output.
- Enforced binding-only dominance, required strong comparators, all D-11-04 primary metrics via `gate_c_primary_metrics_v1`, profile eligibility, actual demand provenance, and claim-discipline checks.
- Generated `experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json` with `status="INCONCLUSIVE"`, explicit profile/missing-row reasons, required scenario/comparator/metric metadata, and demand provenance summary.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create strict Gate C checker CLI and JSON output** - `993c324` (feat)
2. **Task 2: Enforce shared all-primary-metric, strongest-comparator, and binding-only dominance rules** - `5b3da5a` (feat)
3. **Task 3: Generate Gate C artifact and full Phase 11 validation command** - `3457237` (feat)

**Plan metadata:** pending final docs commit

## Files Created/Modified

- `scripts/run_gate_c_paired_evidence.py` - Standalone strict Gate C checker that imports shared Phase 11 constants/evaluator/rule helpers and writes a companion JSON artifact.
- `tests/test_phase11_paired_evidence.py` - Adds synthetic checker tests for output schema, profile eligibility, binding-only scope, metadata-only demand rejection, pilot rejection, and forbidden-language rejection.
- `experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json` - Generated Gate C checker output for the current Phase 11 main artifact.

## Decisions Made

- Recomputed Gate C from raw `scenario_results` instead of trusting the upstream Phase 11 artifact status, preserving tamper-resistant fail-closed behavior.
- Kept `INCONCLUSIVE` as a successful strict-mode exit because the current main artifact is validly fail-closed for missing executions; only `FAILED` exits nonzero.
- Treated artifact-level metadata-only demand provenance as `FAILED` even when raw rows would otherwise pass synthetic metric checks.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- SciPy continues to emit precision-loss warnings on intentionally constant synthetic paired differences inherited from Plan 01 tests; tests pass and the helper handles constant differences deterministically.
- The generated Gate C artifact is `INCONCLUSIVE`, not `PASSED`, because Plan 02's main artifact intentionally contains zero executed rows under the runtime guard.
- Pre-existing uncommitted/untracked files from prior phases remain in the main worktree and were not modified or committed by this plan.

## User Setup Required

None - no external service configuration required.

## Verification

- `python /home/samuel/projects/pi_light_OR/tests/test_phase11_paired_evidence.py`
- `python /home/samuel/projects/pi_light_OR/tests/test_phase11_paired_evidence.py && python /home/samuel/projects/pi_light_OR/scripts/run_gate_c_paired_evidence.py --input /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json --strict`

## Known Stubs

None detected in files created or modified by this plan. The `INCONCLUSIVE` Gate C artifact is not a stub; it is the honest fail-closed output for the current missing-execution main artifact.

## Next Phase Readiness

Phase 12 can consume the strict checker and companion artifact to decide whether future manuscript/reproducibility inputs may use Gate C. At present, the checker explicitly blocks any passed dominance claim until the long-horizon main artifact contains executed paired rows satisfying all required scenarios, comparators, metrics, and demand provenance.

## Self-Check: PASSED

- Created files exist: `scripts/run_gate_c_paired_evidence.py`, `experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json`, and this summary.
- Modified test file exists: `tests/test_phase11_paired_evidence.py`.
- Task commits recorded: `993c324`, `5b3da5a`, `3457237`.

---
*Phase: 11-long-horizon-paired-seed-evidence*
*Completed: 2026-05-24*
