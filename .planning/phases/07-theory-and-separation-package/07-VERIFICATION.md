---
phase: 07-theory-and-separation-package
verified: 2026-05-24T03:47:39Z
status: passed
score: 6/6 must-haves verified
overrides_applied: 0
---

# Phase 7: Theory and Separation Package Verification Report

**Phase Goal:** Researchers have a formal finite-storage primal-dual separation package that justifies exactly when the method reduces to pressure and when it can differ.  
**Verified:** 2026-05-24T03:47:39Z  
**Status:** passed  
**Re-verification:** No — initial verification; no previous `07-VERIFICATION.md` existed.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | THRY-01: slack/infinite-storage, no switching loss, fixed turning ratios, and slack operational constraints recover or tie classical max-pressure/backpressure. | VERIFIED | `refine-logs/THEORY_AND_SEPARATION.md` contains a THRY-01 theorem with those assumptions and the `lambda_up - lambda_down` sign convention. `experiments/dual_sensitivity/phase7_theory_separation.json` has `slack_recovery` with pressure scores equal finite-storage scores for selected action `phase_a`; `criteria.THRY-01=true`. `tests/test_theory_separation.py::test_slack_recovery_matches_pressure_or_tie` verifies this. |
| 2 | THRY-02: explicit binding finite-storage/spillback state causes primal-dual action separation from classical pressure. | VERIFIED | JSON example `storage_binding_two_phase_separation` uses full `finite_storage_state`; `down_a` has zero residual receiving capacity and spillback/blocking true. Pressure selects `phase_a`; finite-storage selects `phase_b`; `actions_separate=true`; `criteria.THRY-02=true`. Memo THRY-02 explains the counterexample and rank-change algebra. |
| 3 | THRY-03: binding separation strictly improves a predeclared one-step constrained objective. | VERIFIED | JSON predeclares `one_step_objective_definition` with Phase 6 components and unit weights before comparison. Binding example totals are `phase_a=59.0`, `phase_b=57.0`, `objective_margin=2.0`, `strict_objective_improvement=true`; `criteria.THRY-03=true`. Memo THRY-03 states the same objective formula and local-scope boundary. |
| 4 | THRY-04: exactly one additional guarantee candidate is included with clear boundaries. | VERIFIED | JSON `guarantee_candidates` is exactly `["constrained_lp_oracle_regret"]`; detail scope is `finite_sample_oracle_relative` with no closed-loop/deployment claim. Memo THRY-04 defines constrained LP oracle regret and states finite-sample/oracle-relative boundaries. |
| 5 | No controller, closed-loop, baseline, or paper-drafting scope creep entered Phase 7 outputs. | VERIFIED | `scripts/check_theory_separation.py` imports only stdlib plus Phase 6 schema helpers; no `traci`, `sumolib`, `cityflow`, `torch`, `pi_light_code`, closed-loop runner, or baseline implementation is used. Scope terms in memo/JSON appear only as explicit exclusions/boundaries. |
| 6 | Claim audit and pytest verification evidence exists and passes. | VERIFIED | Re-ran after review fixes: `python3 scripts/check_theory_separation.py --out experiments/dual_sensitivity/phase7_theory_separation.json` -> PASSED; `python3 -m pytest tests/test_theory_separation.py -q` -> 8 passed; `python3 -m pytest tests/test_finite_storage_schema.py tests/test_claim_discipline.py tests/test_theory_separation.py -q` -> 22 passed; `python3 scripts/audit_claim_discipline.py --paths refine-logs/THEORY_AND_SEPARATION.md experiments/dual_sensitivity/phase7_theory_separation.json --policy-out /tmp/phase7_claim_policy.json --audit-out /tmp/phase7_claim_audit.json` -> PASSED; `python3 -m pytest tests -q` -> 49 passed. |

**Score:** 6/6 must-haves verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `refine-logs/THEORY_AND_SEPARATION.md` | THRY-01~THRY-04 theory memo with guardrails | VERIFIED | Contains required sections, theorem/counterexample/proof sketches, objective formula, constrained LP oracle regret candidate, and explicit non-claim boundaries. |
| `scripts/check_theory_separation.py` | Deterministic checker/generator | VERIFIED | Exposes `build_and_check_phase7_payload()` and `main()`, computes pressure/finite-storage scores and objective totals, validates Phase 6 schema, writes JSON, exits nonzero if criteria fail. |
| `tests/test_theory_separation.py` | Pytest contract for Phase 7 | VERIFIED | Eight tests cover slack recovery, binding separation, strict objective improvement, CLI output, checked-in artifact validation, memo markers/claim safety, targeted claim audit, and guarantee boundary. |
| `experiments/dual_sensitivity/phase7_theory_separation.json` | Machine-readable Phase 7 evidence | VERIFIED | `status=PASSED`, `requirements_covered` exactly THRY-01~THRY-04, schema version `phase6_explicit_state_v1`, scope `theory_static_one_step_only_no_closed_loop_claims`. |
| `scripts/claim_policy.py` | Bounded claim policy source | VERIFIED | Defines forbidden patterns and permitted bounded claim categories used by tests/audit. |
| `scripts/finite_storage_schema.py` | Phase 6 explicit state/objective schema | VERIFIED | Defines required finite-storage and objective fields plus validators consumed by checker/tests. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `scripts/check_theory_separation.py` | `scripts/finite_storage_schema.py` | imports schema constants/validators | WIRED | Imports `OBJECTIVE_COMPONENT_FIELDS`, `SCHEMA_VERSION`, `validate_objective_components`, and `validate_state_objective_sample`; uses validators before emitting examples. |
| `tests/test_theory_separation.py` | `scripts/check_theory_separation.py` | helper import plus subprocess CLI | WIRED | Imports `build_and_check_phase7_payload()` inside helper and runs CLI via subprocess. |
| `refine-logs/THEORY_AND_SEPARATION.md` | generated JSON artifact | explicit artifact reference | WIRED | Memo references `experiments/dual_sensitivity/phase7_theory_separation.json` and describes its THRY-01~THRY-04 content. |
| Claim audit | memo + JSON | `audit_claim_discipline.py --paths ...` | WIRED | Command completed with `status: PASSED` and writes audit output under `/tmp`. |

### Data-Flow Trace

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `phase7_theory_separation.json` | `examples`, `criteria`, `objective_totals` | `build_and_check_phase7_payload()` in checker | Yes | FLOWING — generated from deterministic Python computations and schema validation, not a hand-only prose stub. |
| `tests/test_theory_separation.py` | payload under test | checker helper + temporary CLI output | Yes | FLOWING — tests recompute objective totals and assert generated fields. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Checker regenerates passed artifact | `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/check_theory_separation.py --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json` | `status: PASSED` | PASS |
| Phase 7 tests pass | `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 -m pytest /home/samuel/projects/pi_light_OR/tests/test_theory_separation.py -q` | `8 passed` | PASS |
| Phase 6/7 regression tests pass | `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 -m pytest /home/samuel/projects/pi_light_OR/tests/test_finite_storage_schema.py /home/samuel/projects/pi_light_OR/tests/test_claim_discipline.py /home/samuel/projects/pi_light_OR/tests/test_theory_separation.py -q` | `22 passed` | PASS |
| Claim audit passes | `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/audit_claim_discipline.py --paths /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_SEPARATION.md /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json --policy-out /tmp/phase7_claim_policy_verify.json --audit-out /tmp/phase7_claim_audit_verify.json` | `status: PASSED` | PASS |

### Probe Execution

No `probe-*.sh` probe was declared for Phase 7; phase verification is covered by checker, pytest, and claim audit commands above.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| THRY-01 | `07-01-PLAN.md` | Slack special-case recovery to max-pressure/backpressure | SATISFIED | Memo theorem plus JSON `slack_recovery` and pytest assertion. |
| THRY-02 | `07-01-PLAN.md` | Binding finite-storage/spillback separation | SATISFIED | JSON binding example with explicit `finite_storage_state`, pressure action `phase_a`, finite-storage action `phase_b`. |
| THRY-03 | `07-01-PLAN.md` | Strict improvement on auditable predeclared one-step objective | SATISFIED | Objective definition uses Phase 6 components; margin `2.0 > 0`; pytest recomputes totals. |
| THRY-04 | `07-01-PLAN.md` | Additional guarantee candidate | SATISFIED | Exactly constrained LP oracle regret, finite-sample/oracle-relative, in memo and JSON. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| None | - | No unreferenced `TBD`/`FIXME`/`XXX`, placeholder, empty implementation, or console-only implementation found in Phase 7 files scanned. | - | - |

### Human Verification Required

None. Phase 7 is a static theory/checker/test artifact package; no visual UI, live controller behavior, external service, or closed-loop SUMO behavior is required for this phase.

### Gaps Summary

No blocker gaps found. The Phase 7 goal is achieved: the repository contains an auditable finite-storage primal-dual separation package that establishes slack recovery/tie, explicit binding action separation, strict one-step objective improvement, a bounded constrained-LP-oracle-regret candidate, and claim-safe verification evidence without controller/closed-loop/baseline/paper-drafting scope creep.

---

_Verified: 2026-05-24T03:47:39Z_  
_Verifier: Claude (gsd-verifier)_
