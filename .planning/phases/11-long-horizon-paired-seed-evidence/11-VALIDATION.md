---
phase: 11
slug: long-horizon-paired-seed-evidence
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-24
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python direct assertion tests |
| **Config file** | none — existing script-style tests |
| **Quick run command** | `python tests/test_closed_loop_sumo.py` |
| **Full suite command** | `python tests/test_closed_loop_sumo.py && python scripts/run_gate_c_paired_evidence.py --input experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json --out experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json --strict` |
| **Estimated runtime** | quick tests ~10s; full Phase 11 main SUMO profile may be long-running |

---

## Sampling Rate

- **After every task commit:** Run `python tests/test_closed_loop_sumo.py`
- **After every plan wave:** Run the Phase 11 artifact/gate command for the available profile (`pilot` during development, `main` when long-horizon evidence is being generated)
- **Before `/gsd:verify-work`:** Full suite and Gate C artifact checks must be green or explicitly `INCONCLUSIVE` with fail-closed reasons
- **Max feedback latency:** 60 seconds for synthetic/unit checks; long-horizon SUMO runs are exempt but must emit auditable artifacts

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | EXP-03 | T-11-01 | N/A | unit/spec | `python tests/test_closed_loop_sumo.py` | ❌ W0 | ⬜ pending |
| 11-01-02 | 01 | 1 | EXP-05 | T-11-02 | N/A | unit/statistics | `python tests/test_closed_loop_sumo.py` | ❌ W0 | ⬜ pending |
| 11-01-03 | 01 | 1 | GATE-03 | T-11-03 | N/A | gate | `python scripts/run_gate_c_paired_evidence.py --input experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json --out experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json --strict` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_closed_loop_sumo.py` — add synthetic tests for Phase 11 spec, paired statistics, Gate C pass/fail, missing comparator, unpaired seed, missing stress metadata, missing action decomposition, and forbidden claim text.
- [ ] `scripts/run_gate_c_paired_evidence.py` or equivalent — must exist before strict gate command can pass.
- [ ] `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` — pilot artifact may be generated first; main artifact must record profile and seed count.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Main long-horizon runtime feasibility | EXP-03 | 20 seeds × 6 stress scenarios × comparators may be expensive on CPU/SUMO | Inspect Phase 11 artifact `profile`, `steps`, `warmup`, `seeds`, and row counts; if only pilot ran, artifact must state why main remains pending/inconclusive. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s for unit/gate checks
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
