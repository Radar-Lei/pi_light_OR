---
phase: 12-reproducibility-and-future-claim-inputs
plan: 01
subsystem: reproducibility
tags: [python, json, csv, provenance, claim-audit, sumo]

requires:
  - phase: 07-theory-and-separation-package
    provides: Phase 7 static theory/separation artifact
  - phase: 09-slack-and-binding-kill-gates
    provides: Phase 9 Gate A/B slack and binding artifact
  - phase: 10-strong-baselines-and-stress-scenario-suite
    provides: Phase 10 smoke/spec baseline-stress artifact
  - phase: 11-long-horizon-paired-seed-evidence
    provides: Phase 11 paired-evidence and Gate C status artifacts
provides:
  - Phase 12 source registry, status-preserving loaders, claim-input builders, provenance and reproduction manifests, claim audit, and CLI writer
  - Direct synthetic assertion tests for CLAIM-03, REPRO-01, REPRO-02, and REPRO-03
affects: [phase12, reproducibility, future-claim-inputs, claim-discipline]

tech-stack:
  added: []
  patterns: [stdlib-json-csv-argparse, fail-closed-status-propagation, bounded-claim-audit, direct-python-assertion-tests]

key-files:
  created:
    - scripts/run_phase12_reproducibility_inputs.py
    - tests/test_phase12_reproducibility_inputs.py
    - experiments/dual_sensitivity/phase12_reproducibility_package.json
    - experiments/dual_sensitivity/phase12_provenance_manifest.json
    - experiments/dual_sensitivity/phase12_table_inputs.csv
    - experiments/dual_sensitivity/phase12_claim_inputs.json
    - experiments/dual_sensitivity/phase12_claim_audit.json
    - experiments/dual_sensitivity/phase12_reproduction_manifest.json
    - experiments/dual_sensitivity/phase12_summary.md
    - .planning/phases/12-reproducibility-and-future-claim-inputs/12-01-SUMMARY.md
  modified: []

key-decisions:
  - "Phase 10 SMOKE_ONLY is accepted only as baseline/stress capability context and remains claim_allowed=false for dominance-style evidence."
  - "Phase 11 and Gate C INCONCLUSIVE statuses are preserved as limitations; strict Phase 12 mode exits nonzero until those sources are PASSED."
  - "Reproduction manifest records opt-in long-horizon SUMO execution but default Phase 12 generation only packages/audits existing raw artifacts."

patterns-established:
  - "Fixed source registry maps every Phase 7/9/10/11 raw artifact to roles, status policies, rerun commands, requirements, and caveats."
  - "Derived claim rows preserve simulator, network, horizon, warmup, seed count, profile, demand multiplier, gate status, source status, and caveat qualifiers."
  - "Generated JSON/CSV/Markdown surfaces are audited with scripts/claim_policy.py plus Phase-12-specific forbidden phrases."

requirements-completed: [CLAIM-03, REPRO-01, REPRO-02, REPRO-03]

duration: 31min
completed: 2026-05-24T12:18:32Z
---

# Phase 12 Plan 01: Reproducibility Input Generator Summary

**Status-preserving Phase 12 JSON/CSV/Markdown generator with provenance, CPU/SUMO reproduction manifest, bounded claim inputs, and fail-closed strict mode.**

## Performance

- **Duration:** 31 min
- **Started:** 2026-05-24T11:47:00Z
- **Completed:** 2026-05-24T12:18:32Z
- **Tasks:** 3/3
- **Files created:** 10

## Accomplishments

- Created `scripts/run_phase12_reproducibility_inputs.py` with fixed Phase 7/9/10/11 source registry, status-preserving JSON loaders, bounded claim-input rows, table rows, provenance manifest, reproduction manifest, generated-output claim audit, artifact writer, and strict/non-strict CLI behavior.
- Created `tests/test_phase12_reproducibility_inputs.py` with direct synthetic tests for missing, invalid, PASSED, FAILED, INCONCLUSIVE, PILOT_ONLY, and SMOKE_ONLY sources; qualifier preservation; provenance coverage; forbidden claim scanning; and strict-mode exit behavior.
- Generated Phase 12 artifacts under `experiments/dual_sensitivity/phase12_*`; current package status is `INCONCLUSIVE` because Phase 11 long-horizon and Gate C sources remain `INCONCLUSIVE`, while claim audit is `PASSED`.

## Task Commits

No commits were created because the user explicitly requested: "Do not commit."

## Files Created/Modified

- `scripts/run_phase12_reproducibility_inputs.py` - Phase 12 generator implementation and CLI.
- `tests/test_phase12_reproducibility_inputs.py` - Direct assertion test suite.
- `experiments/dual_sensitivity/phase12_reproducibility_package.json` - Authoritative Phase 12 package.
- `experiments/dual_sensitivity/phase12_provenance_manifest.json` - Raw-to-derived provenance manifest.
- `experiments/dual_sensitivity/phase12_table_inputs.csv` - Table/figure-data rows with source statuses and qualifiers.
- `experiments/dual_sensitivity/phase12_claim_inputs.json` - Machine-readable bounded future-claim input records.
- `experiments/dual_sensitivity/phase12_claim_audit.json` - Generated-output claim audit.
- `experiments/dual_sensitivity/phase12_reproduction_manifest.json` - CPU/SUMO reproduction command manifest with opt-in long-horizon command.
- `experiments/dual_sensitivity/phase12_summary.md` - Generated human audit summary, explicitly not manuscript prose.
- `.planning/phases/12-reproducibility-and-future-claim-inputs/12-01-SUMMARY.md` - This execution summary.

## Decisions Made

- Phase 10 `SMOKE_ONLY` is represented only as baseline/stress capability context and cannot become dominance or superiority evidence.
- Phase 11 main and Gate C `INCONCLUSIVE` sources remain limitations; non-strict generation writes auditable artifacts, and strict mode exits nonzero.
- The reproduction manifest reuses existing scripts and records long-horizon SUMO execution as opt-in/fail-closed; no new external package or GPU dependency was introduced.

## Deviations from Plan

None - plan executed as specified, except commits were intentionally skipped per user instruction.

## Validation

- `python /home/samuel/projects/pi_light_OR/tests/test_phase12_reproducibility_inputs.py` - PASSED.
- `python /home/samuel/projects/pi_light_OR/scripts/run_phase12_reproducibility_inputs.py --out-dir /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity` - PASSED with package status `INCONCLUSIVE` and claim audit `PASSED`.
- `python /home/samuel/projects/pi_light_OR/scripts/run_phase12_reproducibility_inputs.py --out-dir /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity --strict` - expected fail-closed nonzero because Phase 11 main and Gate C sources are `INCONCLUSIVE`.

## Known Stubs

None found in created source/test files. The generated package uses explicit `unknown` qualifiers only when a raw source artifact does not expose that qualifier; those are caveated data-quality markers, not UI/rendering stubs.

## Threat Flags

No new network endpoints, authentication paths, schema changes, or file-access trust boundaries beyond the planned local CLI artifact reads/writes were introduced.

## Issues Encountered

- Existing repository contains many unrelated modified/untracked files from prior phases. They were not changed or committed.
- Strict generation correctly exits nonzero with current real artifacts because Phase 11 evidence remains inconclusive.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02 can consume the generated Phase 12 package and manifests. The current strict blocker is evidence-related, not tooling-related: Phase 11 long-horizon and Gate C artifacts must become `PASSED` before strict Phase 12 validation can pass.

## Self-Check: PASSED

All created source, test, generated artifact, and summary files exist. Validation commands produced the expected outcomes: direct tests passed, non-strict generation wrote an `INCONCLUSIVE` package with passed claim audit, and strict mode failed closed on current Phase 11 `INCONCLUSIVE` sources.

---
*Phase: 12-reproducibility-and-future-claim-inputs*
*Completed: 2026-05-24T12:18:32Z*
