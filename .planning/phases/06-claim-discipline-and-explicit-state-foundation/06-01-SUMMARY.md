---
phase: 06-claim-discipline-and-explicit-state-foundation
plan: 01
subsystem: claim-discipline
tags: [python, pytest, json, claim-audit, fail-closed]

requires:
  - phase: 05-reproducibility-and-repository-hardening
    provides: reproducibility manifest, paper artifact guard patterns, pressure-equivalent route discipline
provides:
  - Central bounded claim policy helper and machine-readable policy artifact
  - Fail-closed claim audit CLI for CLAIM-01 and CLAIM-02
  - Pytest coverage for bounded claim language, forbidden wording, and generated artifact boundaries
affects: [phase-06, phase-07, phase-09, phase-12, claim-discipline, report-generation]

tech-stack:
  added: []
  patterns:
    - stdlib argparse JSON CLI gates
    - central claim vocabulary imported by scanners
    - metadata-excluding prose scan with separate artifact validation

key-files:
  created:
    - scripts/claim_policy.py
    - scripts/audit_claim_discipline.py
    - tests/test_claim_discipline.py
    - experiments/dual_sensitivity/phase6_claim_policy.json
    - experiments/dual_sensitivity/phase6_claim_audit.json
  modified: []

key-decisions:
  - "Phase 6 claim scans treat negated/bounded caveats as safe while still failing on affirmative superiority wording."
  - "Historical v1.0 pressure-equivalent artifacts are quarantined as insufficient_historical_v1_0 rather than treated as binding-regime superiority evidence."

patterns-established:
  - "Claim policy single source of truth: scripts import bounded claim vocabulary instead of duplicating forbidden phrases."
  - "Claim audit scan contract: report prose and configured content are scanned, while policy/audit metadata is validated separately."

requirements-completed: [CLAIM-01, CLAIM-02]

duration: 9min 11s
completed: 2026-05-23
---

# Phase 06 Plan 01: Claim Discipline Policy and Audit Summary

**Bounded finite-storage claim policy with fail-closed audit CLI preventing v1.0 pressure-equivalent evidence from becoming dual-superiority language**

## Performance

- **Duration:** 9min 11s
- **Started:** 2026-05-23T12:27:59Z
- **Completed:** 2026-05-23T12:37:10Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added `scripts/claim_policy.py` as the central source of truth for permitted bounded claims, forbidden claim patterns, default scan paths, and historical evidence quarantine rules.
- Added `scripts/audit_claim_discipline.py`, a fail-closed CLI that writes policy/audit JSON, scans configured repository/report surfaces, skips metadata self-matches, and exits nonzero on unsupported superiority wording.
- Added pytest coverage for CLAIM-01 and CLAIM-02, including RED tests, fail-closed temp-report subprocess checks, bounded-language pass checks, and generated artifact assertions.
- Generated `phase6_claim_policy.json` and `phase6_claim_audit.json` under `experiments/dual_sensitivity/` with status `PASSED` for the current repository scan.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add failing claim-discipline behavior tests** - `b2fa50e` (test)
2. **Task 2: Implement central claim policy and audit CLI** - `505f161` (feat)
3. **Task 3: Verify claim artifacts and repository scan boundaries** - `06ccb65` (test)
4. **Verification artifact refresh** - `63f111b` (chore)

**Plan metadata:** pending final docs commit

_Note: TDD tasks used RED then GREEN commits; final artifact timestamp refresh records deterministic post-verification JSON outputs._

## Files Created/Modified

- `scripts/claim_policy.py` - central bounded claim policy, forbidden pattern matcher, historical evidence quarantine helper, and policy artifact writer.
- `scripts/audit_claim_discipline.py` - argparse CLI and reusable `audit_claim_paths()` implementation that writes fail-closed JSON audit artifacts.
- `tests/test_claim_discipline.py` - pytest behavior tests for policy vocabulary, forbidden phrase detection, CLI pass/fail behavior, and generated artifact boundaries.
- `experiments/dual_sensitivity/phase6_claim_policy.json` - machine-readable bounded claim policy artifact.
- `experiments/dual_sensitivity/phase6_claim_audit.json` - latest repository claim audit result.

## Decisions Made

- Negated or bounded caveat contexts such as “must not” and “does not claim” are not treated as affirmative forbidden claims, so existing limitations text remains allowed while direct overclaim wording still fails closed.
- Historical pressure-equivalent surfaces are recorded under `insufficient_historical_v1_0`; only affirmative superiority wording makes the audit fail.
- Phase 6 schema/fixture artifact validation is explicitly deferred in the audit payload to Plan 06-03, matching the plan boundary.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Avoided false positives on bounded caveat language**
- **Found during:** Task 2 (Implement central claim policy and audit CLI)
- **Issue:** The initial repository audit flagged phrases inside negative statements such as “does not claim ... universal dominance” and checklist caveats describing what a theorem does not prove.
- **Fix:** Added bounded/negated context handling before recording forbidden phrase hits or historical superiority violations.
- **Files modified:** `scripts/claim_policy.py`, `scripts/audit_claim_discipline.py`
- **Verification:** `python3 -m pytest tests/test_claim_discipline.py -q && python3 scripts/audit_claim_discipline.py --policy-out experiments/dual_sensitivity/phase6_claim_policy.json --audit-out experiments/dual_sensitivity/phase6_claim_audit.json`
- **Committed in:** `505f161` (part of Task 2 commit)

**2. [Rule 2 - Missing Critical] Generated artifacts were refreshed after final verification**
- **Found during:** Task 3 (Verify claim artifacts and repository scan boundaries)
- **Issue:** Running the audit CLI updates generated timestamps, leaving policy/audit artifacts modified after the task commit.
- **Fix:** Added a dedicated verification artifact refresh commit so repository artifacts match the final passed audit run.
- **Files modified:** `experiments/dual_sensitivity/phase6_claim_policy.json`, `experiments/dual_sensitivity/phase6_claim_audit.json`
- **Verification:** Final audit status is `PASSED` and generated artifacts are committed.
- **Committed in:** `63f111b`

---

**Total deviations:** 2 auto-fixed (1 bug, 1 missing critical)
**Impact on plan:** Both fixes preserve the intended fail-closed claim discipline without adding unrelated scope.

## Issues Encountered

- The repository already contains historical limitation language with forbidden terms in negated contexts. This required precise bounded-context handling rather than weakening the forbidden phrase list.

## Known Stubs

None detected in files created or modified by this plan.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: filesystem_scan | `scripts/audit_claim_discipline.py` | New CLI scans configured repository files/directories; mitigated by resolving `--root`, recording checked paths, skipping unsupported suffixes, and validating artifacts separately. |

## User Setup Required

None - no external service configuration required.

## Self-Check: PASSED

- Found created files: `scripts/claim_policy.py`, `scripts/audit_claim_discipline.py`, `tests/test_claim_discipline.py`, `experiments/dual_sensitivity/phase6_claim_policy.json`, `experiments/dual_sensitivity/phase6_claim_audit.json`.
- Found task commits: `b2fa50e`, `505f161`, `06ccb65`, `63f111b`.
- Final verification passed: `python3 -m pytest tests/test_claim_discipline.py -q` and `python3 scripts/audit_claim_discipline.py --policy-out experiments/dual_sensitivity/phase6_claim_policy.json --audit-out experiments/dual_sensitivity/phase6_claim_audit.json`.

## Next Phase Readiness

- Plan 06-02 can build explicit finite-storage state/objective artifacts while reusing the bounded claim vocabulary.
- Plan 06-03 can integrate this audit into render/reproducibility surfaces and add validation for the schema/fixture artifacts once they exist.

---
*Phase: 06-claim-discipline-and-explicit-state-foundation*
*Completed: 2026-05-23*
