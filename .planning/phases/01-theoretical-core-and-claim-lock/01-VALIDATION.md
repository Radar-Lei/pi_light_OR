---
phase: 01
slug: theoretical-core-and-claim-lock
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-22
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Script/file assertion gates |
| **Config file** | none — no unit-test framework configured |
| **Quick run command** | `test -f refine-logs/THEORY_AND_CLAIMS.md && grep -q "THRY-01" refine-logs/THEORY_AND_CLAIMS.md` |
| **Full suite command** | `python scripts/run_dual_sanity.py && test -f refine-logs/THEORY_AND_CLAIMS.md && test -f refine-logs/THEORY_REVIEW_CHECKLIST.md` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run the relevant file-existence and grep assertions for the task’s requirement IDs.
- **After every plan wave:** Run `python scripts/run_dual_sanity.py` plus artifact existence checks.
- **Before `/gsd:verify-work`:** Full suite must be green.
- **Max feedback latency:** 60 seconds.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | THRY-01 | — | N/A | source assertion | `grep -q "queue conservation" refine-logs/THEORY_AND_CLAIMS.md` | ✅ | ⬜ pending |
| 01-01-02 | 01 | 1 | THRY-02 | — | N/A | source assertion | `grep -q "dual-sensitivity decomposition" refine-logs/THEORY_AND_CLAIMS.md` | ✅ | ⬜ pending |
| 01-02-01 | 02 | 2 | THRY-03 | — | N/A | source assertion + script gate | `python scripts/run_dual_sanity.py` | ✅ | ⬜ pending |
| 01-02-02 | 02 | 2 | THRY-04 | — | N/A | source assertion | `grep -q "binding-regime" refine-logs/THEORY_AND_CLAIMS.md` | ✅ | ⬜ pending |
| 01-03-01 | 03 | 3 | THRY-05 | — | N/A | source assertion | `grep -q "finite-dictionary" refine-logs/THEORY_AND_CLAIMS.md` | ✅ | ⬜ pending |
| 01-03-02 | 03 | 3 | THRY-01..THRY-05 | — | N/A | checklist assertion | `test -f refine-logs/THEORY_REVIEW_CHECKLIST.md` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test framework is required for this theory-artifact phase.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Reviewer-facing mathematical plausibility | THRY-01..THRY-05 | Formal proof quality cannot be fully machine-verified by grep/script gates | Read `refine-logs/THEORY_AND_CLAIMS.md` and confirm every proposition maps to the checklist without claiming universal pressure dominance. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-05-22
