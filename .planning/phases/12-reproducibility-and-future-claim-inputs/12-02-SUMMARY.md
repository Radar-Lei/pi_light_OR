---
phase: 12-reproducibility-and-future-claim-inputs
plan: 02
subsystem: reproducibility
tags: [python, json, csv, provenance, claim-audit, sumo]
requires:
  - phase: 12-reproducibility-and-future-claim-inputs
    provides: Plan 12-01 Phase 12 generator, tests, and initial phase12 artifacts
provides:
  - Real Phase 12 reproducibility package generated from Phase 7/9/10/11 artifacts
  - Provenance manifest, table inputs, claim inputs, claim audit, reproduction manifest, and audit summary
  - Strict fail-closed validation result for current INCONCLUSIVE Phase 11/Gate C artifacts
affects: [phase12, reproducibility, future-claim-inputs, gate-c]
tech-stack:
  added: []
  patterns: [status-preserving artifact generation, raw-to-derived provenance, fail-closed strict validation]
key-files:
  created:
    - experiments/dual_sensitivity/phase12_reproducibility_package.json
    - experiments/dual_sensitivity/phase12_provenance_manifest.json
    - experiments/dual_sensitivity/phase12_table_inputs.csv
    - experiments/dual_sensitivity/phase12_claim_inputs.json
    - experiments/dual_sensitivity/phase12_claim_audit.json
    - experiments/dual_sensitivity/phase12_reproduction_manifest.json
    - experiments/dual_sensitivity/phase12_summary.md
  modified:
    - tests/test_phase12_reproducibility_inputs.py
key-decisions:
  - "Current Phase 11 main and Gate C artifacts remain INCONCLUSIVE and block strict mode rather than becoming claim-ready evidence."
  - "Phase 10 remains SMOKE_ONLY capability context and is not treated as dominance evidence."
patterns-established:
  - "Real-output assertions validate generated Phase 12 artifact shape in addition to synthetic fixtures."
  - "Strict mode nonzero exit is expected and correct when Phase 11/Gate C source statuses are non-PASSED."
requirements-completed: [CLAIM-03, REPRO-01, REPRO-02, REPRO-03]
duration: 2min 3s
completed: 2026-05-24
---

# Phase 12 Plan 02: Reproducibility Package Validation Summary

**Auditable Phase 12 reproducibility/future-claim package with provenance-linked artifacts and fail-closed strict blockers for current INCONCLUSIVE Gate C evidence**

## Performance

- **Duration:** 2min 3s
- **Started:** 2026-05-24T12:20:49Z
- **Completed:** 2026-05-24T12:22:52Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Refreshed all seven required `phase12_*` artifacts under `experiments/dual_sensitivity/` from current raw Phase 7/9/10/11 artifacts.
- Preserved current source statuses: Phase 7/9 `PASSED`, Phase 10 `SMOKE_ONLY`, and Phase 11 main/Gate C `INCONCLUSIVE`.
- Verified strict mode fails closed with explicit blockers for Phase 11 main and Gate C non-PASSED statuses.
- Added real-default-output shape assertions to `tests/test_phase12_reproducibility_inputs.py` without weakening existing synthetic coverage.

## Task Commits

No commits were created because the user explicitly requested: Do not commit.

## Files Created/Modified

- `scripts/run_phase12_reproducibility_inputs.py` - Existing Plan 01 generator used to refresh the package.
- `tests/test_phase12_reproducibility_inputs.py` - Added real output shape checks for package/provenance/CSV/claim/reproduction artifacts.
- `experiments/dual_sensitivity/phase12_reproducibility_package.json` - Authoritative package status and strict blockers.
- `experiments/dual_sensitivity/phase12_provenance_manifest.json` - Raw-to-derived traceability for every Phase 12 output.
- `experiments/dual_sensitivity/phase12_table_inputs.csv` - Status-qualified table/figure-data input surface.
- `experiments/dual_sensitivity/phase12_claim_inputs.json` - Bounded future claim inputs and limitations.
- `experiments/dual_sensitivity/phase12_claim_audit.json` - Generated-output claim audit, currently `PASSED` with zero hits.
- `experiments/dual_sensitivity/phase12_reproduction_manifest.json` - CPU/SUMO reproduction command surface with long-horizon execution marked opt-in.
- `experiments/dual_sensitivity/phase12_summary.md` - Human audit summary, explicitly not manuscript prose.

## Decisions Made

- Current Phase 11 main and Gate C `INCONCLUSIVE` statuses are retained as limitations and strict blockers.
- The 2160-row long-horizon SUMO suite was not executed; it remains an opt-in reproduction command only.
- Phase 10 `SMOKE_ONLY` evidence remains capability context, not superiority/dominance evidence.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical Coverage] Added direct real-output assertions**
- **Found during:** Task 2 (Validate provenance, claim audit, and reproduction manifest on real outputs)
- **Issue:** Existing tests strongly covered synthetic fixtures and CLI behavior, but did not directly assert the shape of already-generated default Phase 12 artifacts when present.
- **Fix:** Added `test_real_default_outputs_have_required_shape_when_present()` to validate real package requirements, source status map, provenance coverage, CSV columns, Phase 11 limitation caveats, claim audit status, and reproduction-command constraints.
- **Files modified:** `tests/test_phase12_reproducibility_inputs.py`
- **Verification:** `python tests/test_phase12_reproducibility_inputs.py`
- **Committed in:** Not committed per user instruction.

---

**Total deviations:** 1 auto-fixed (Rule 2 missing critical validation coverage)
**Impact on plan:** Strengthened required validation without changing generator semantics or broadening scope.

## Validation Results

1. `python tests/test_phase12_reproducibility_inputs.py` — PASSED
2. `python scripts/run_phase12_reproducibility_inputs.py --out-dir experiments/dual_sensitivity` — PASSED, wrote all seven Phase 12 outputs with package status `INCONCLUSIVE` and claim audit `PASSED`
3. `python scripts/run_phase12_reproducibility_inputs.py --out-dir experiments/dual_sensitivity --strict` — EXPECTED NONZERO, fail-closed because:
   - `phase11_long_horizon_paired_seed_evidence source status is INCONCLUSIVE, expected one of ['PASSED']`
   - `phase11_gate_c_paired_evidence source status is INCONCLUSIVE, expected one of ['PASSED']`

## Known Stubs

None found in files created/modified for this plan. Unknown horizon/network fields in static Phase 7/9 rows are explicit artifact qualifiers, not UI/data-source stubs.

## Issues Encountered

- Strict mode exited nonzero as expected for current INCONCLUSIVE Phase 11/Gate C inputs; this is correct fail-closed behavior, not a failure.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 12 package is ready for audit as a future manuscript-input surface, not manuscript prose.
- Strict release remains blocked until Phase 11 long-horizon rows and Gate C source status become `PASSED`.

## Self-Check: PASSED

- Confirmed all seven required Phase 12 artifacts exist under `experiments/dual_sensitivity/`.
- Confirmed Plan 12-02 summary exists at `.planning/phases/12-reproducibility-and-future-claim-inputs/12-02-SUMMARY.md`.
- Confirmed validation commands produced the expected pass/pass/fail-closed outcomes.

---
*Phase: 12-reproducibility-and-future-claim-inputs*
*Completed: 2026-05-24*
