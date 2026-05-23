---
phase: 06
slug: claim-discipline-and-explicit-state-foundation
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-23
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 available; direct Python script gates also used |
| **Config file** | none detected |
| **Quick run command** | `python3 -m pytest tests/test_claim_discipline.py tests/test_finite_storage_schema.py -q` |
| **Full suite command** | `python3 -m pytest tests -q` |
| **Estimated runtime** | ~30-90 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/test_claim_discipline.py tests/test_finite_storage_schema.py -q`
- **After every plan wave:** Run `python3 -m pytest tests -q`
- **Before `/gsd:verify-work`:** Full suite and Phase 6 claim audit CLI must be green
- **Max feedback latency:** 90 seconds for targeted Phase 6 tests

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | CLAIM-01 | T-06-01 | Claim policy encodes bounded slack/tie and binding-only improvement language | unit | `python3 -m pytest tests/test_claim_discipline.py::test_claim_policy_encodes_bounded_claim -q` | ❌ W0 | ⬜ pending |
| 06-01-02 | 01 | 1 | CLAIM-02 | T-06-02 | v1.0 superiority wording fails closed without v1.1 evidence | unit/integration | `python3 -m pytest tests/test_claim_discipline.py::test_v1_pressure_equivalent_superiority_wording_fails_closed -q` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 1 | STATE-01 | T-06-03 | Explicit finite-storage state fields are required and proxy-only fields are insufficient | unit/schema | `python3 -m pytest tests/test_finite_storage_schema.py::test_explicit_finite_storage_state_required_fields -q` | ❌ W0 | ⬜ pending |
| 06-02-02 | 02 | 1 | STATE-02 | T-06-04 | Objective components include delay, unfinished_vehicle_penalty, spillback_blocking_time, and switching_lost_time | unit/schema | `python3 -m pytest tests/test_finite_storage_schema.py::test_objective_components_required_keys -q` | ❌ W0 | ⬜ pending |
| 06-03-01 | 03 | 2 | STATE-03 | T-06-05 | Static fixtures and closed-loop rows are schema-validated before downstream claims | integration | `python3 -m pytest tests/test_finite_storage_schema.py::test_phase6_fixture_generation_and_validation -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_claim_discipline.py` — stubs and behavior tests for CLAIM-01 and CLAIM-02
- [ ] `tests/test_finite_storage_schema.py` — stubs and behavior tests for STATE-01, STATE-02, and STATE-03
- [ ] `scripts/claim_policy.py` — single source of truth for bounded claim policy and forbidden wording
- [ ] `scripts/finite_storage_schema.py` — shared validation helper for explicit state and objective components

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 90s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-05-23
