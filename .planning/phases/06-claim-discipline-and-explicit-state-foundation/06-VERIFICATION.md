---
phase: 06-claim-discipline-and-explicit-state-foundation
verified: 2026-05-24T00:00:00Z
status: passed
score: 9/9 must-haves verified
overrides_applied: 0
---

# Phase 6: Claim Discipline and Explicit State Foundation Verification Report

**Phase Goal:** Researchers can audit explicit finite-storage state/objective data and see that all project language prevents v1.0 evidence from being treated as dual-superiority evidence.
**Verified:** 2026-05-24T00:00:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | User can inspect milestone claim guards and see the bounded claim: slack regimes recover/tie max-pressure, while improvement claims are restricted to binding storage/spillback/switching/service/incident regimes. | VERIFIED | `scripts/claim_policy.py` defines `PERMITTED_CLAIM`, `allowed_claims.slack_recovery_or_tie`, `allowed_claims.binding_regime_improvement_only`, and evidence prerequisites including `finite_storage_state` and `objective_components`; `experiments/dual_sensitivity/phase6_claim_policy.json` status is `PASSED`. |
| 2 | User can run or inspect artifact generation and find explicit downstream storage, residual receiving capacity, spillback/blocking, switching-loss, service-urgency, and incident/capacity-drop fields instead of proxy-only labels. | VERIFIED | `scripts/finite_storage_schema.py` defines and validates all six `FINITE_STORAGE_STATE_FIELDS`; `scripts/generate_static_regime_states.py` builds `finite_storage_state` for every sample; regenerated fixture artifact contains 18 samples and every sample has the exact six required fields. |
| 3 | User can audit finite-storage objective outputs decomposed into delay, unfinished-vehicle penalty, spillback/blocking time, and switching lost-time terms. | VERIFIED | `scripts/finite_storage_schema.py` defines `OBJECTIVE_COMPONENT_FIELDS` with all four required terms and canonical `build_objective_components_from_metrics()`; fixture artifact and closed-loop row builders use `objective_components`. |
| 4 | User can see repository/report checks that prevent v1.0 pressure-equivalent evidence from being described as dual superiority. | VERIFIED | `scripts/audit_claim_discipline.py`, `scripts/render_closed_loop_report.py`, `scripts/render_paper_artifacts.py`, and `scripts/reproduce_blocks.py` import central claim-policy checks; independent audit CLI exited 0 with status `PASSED` and no `forbidden_hits`. |
| 5 | User can inspect a machine-readable bounded claim policy and a fail-closed claim audit CLI. | VERIFIED | `scripts/claim_policy.py`, `scripts/audit_claim_discipline.py`, `phase6_claim_policy.json`, and `phase6_claim_audit.json` exist, are substantive, and are covered by `tests/test_claim_discipline.py`; failing overclaim behavior is tested. |
| 6 | User can inspect generated state fixtures with explicit finite-storage fields and objective components. | VERIFIED | `experiments/dual_sensitivity/phase6_explicit_state_schema.json` and `phase6_state_objective_fixtures.json` are generated artifacts with status `PASSED`; independent regeneration command succeeded. |
| 7 | Proxy-only regime labels are insufficient for v1.1 binding-regime evidence. | VERIFIED | `finite_storage_schema.validate_state_objective_sample()` rejects samples lacking `finite_storage_state` and `objective_components`; tests assert proxy-only samples fail; generated artifact contains `legacy_proxy_note` documenting insufficiency. |
| 8 | Static fixture and closed-loop runner/report surfaces validate explicit finite-storage state and objective components before downstream claims. | VERIFIED | `run_static_kill_gate.py` calls `validate_state_objective_sample()` for Phase 6 samples; `run_closed_loop_sumo.py` validates every completed/not-feasible row via `validate_closed_loop_row()` before return; `render_closed_loop_report.py` surfaces objective component columns. |
| 9 | User can run targeted pytest, full pytest, and claim audit CLI as the Phase 6 verification gate. | VERIFIED | Independent execution: `python3 -m pytest /home/samuel/projects/pi_light_OR/tests -q` returned `41 passed`; claim audit CLI returned `PASSED`; fixture/schema regeneration returned `PASSED`. |

**Score:** 9/9 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `scripts/claim_policy.py` | Central bounded claim vocabulary and policy writer | VERIFIED | 7.5KB substantive module; exports policy constants/helpers and forbidden phrase scanning. |
| `scripts/audit_claim_discipline.py` | Fail-closed audit CLI | VERIFIED | Imports `claim_policy`, writes policy/audit artifacts, validates metadata separately, exits nonzero on `FAILED`. |
| `scripts/finite_storage_schema.py` | Required-field validators/builders for state/objective schema | VERIFIED | Defines exact state/objective fields, builders, validators, schema artifact writer. |
| `scripts/generate_static_regime_states.py` | Static fixture generator emitting explicit Phase 6 fields | VERIFIED | Imports schema helpers, calls `build_finite_storage_state`, `build_objective_components`, and `validate_state_objective_sample` for each sample. |
| `scripts/run_static_kill_gate.py` | Schema validation integration for explicit Phase 6 samples | VERIFIED | Calls `validate_state_objective_sample()` when Phase 6 schema markers or nested fields are present. |
| `scripts/run_closed_loop_sumo.py` | Closed-loop rows with finite_storage_state and objective_components | VERIFIED | Uses shared objective helper and validates full state/objective sample before emitting rows. |
| `scripts/run_closed_loop_suite.py` | Suite payload metadata for nested schema fields | VERIFIED | Publishes `objective_component_schema()` and `finite_storage_state_schema()` while scalar aggregation remains separate. |
| `scripts/render_closed_loop_report.py` | Claim-policy report guard and objective CSV surfacing | VERIFIED | Imports `claim_policy`; CSV output includes `objective_*` columns for all objective components. |
| `scripts/render_paper_artifacts.py` | Paper-facing Phase 6 guard validation | VERIFIED | Validates all four Phase 6 guard artifacts and fails closed on missing/malformed/non-PASSED guards. |
| `scripts/reproduce_blocks.py` | Reproducibility registry for Phase 6 artifacts | VERIFIED | Includes `phase6_claim_state_guards` block with CLAIM-01, CLAIM-02, STATE-01, STATE-02, STATE-03. |
| `tests/test_claim_discipline.py` | CLAIM-01/CLAIM-02 behavior tests | VERIFIED | Tests bounded policy, forbidden phrases, fail-closed CLI, bounded language pass, generated artifacts. |
| `tests/test_finite_storage_schema.py` | STATE-01/STATE-02/STATE-03 schema tests | VERIFIED | Tests required fields, objective keys, fixture generation, static kill-gate validation, diagnostic failures. |
| `tests/test_closed_loop_sumo.py` | Closed-loop row/report/paper guard tests | VERIFIED | Tests row schema, suite metadata, renderer CSV columns, paper artifact guard, reproducibility registry. |
| `experiments/dual_sensitivity/phase6_claim_policy.json` | Machine-readable bounded claim policy | VERIFIED | Status `PASSED`, requirements `CLAIM-01`, `CLAIM-02`, allowed bounded claim categories present. |
| `experiments/dual_sensitivity/phase6_claim_audit.json` | Latest claim audit result | VERIFIED | Status `PASSED`, no forbidden hits after independent audit run. |
| `experiments/dual_sensitivity/phase6_explicit_state_schema.json` | Machine-readable state/objective schema | VERIFIED | Status `PASSED`; exact state and objective field sets present. |
| `experiments/dual_sensitivity/phase6_state_objective_fixtures.json` | Deterministic explicit state/objective fixtures | VERIFIED | Regenerated successfully; 18 samples; every sample has exact state and objective fields. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `scripts/audit_claim_discipline.py` | `scripts/claim_policy.py` | `from claim_policy import ...` | WIRED | Audit CLI imports central policy, forbidden hits, historical quarantine, policy writer. |
| `scripts/generate_static_regime_states.py` | `scripts/finite_storage_schema.py` | imports builders/validators | WIRED | Generator builds and validates nested `finite_storage_state` and `objective_components`. |
| `scripts/run_static_kill_gate.py` | `scripts/finite_storage_schema.py` | `validate_state_objective_sample` | WIRED | Explicit Phase 6 samples are validated during loading/grouping. |
| `scripts/run_closed_loop_sumo.py` | `scripts/finite_storage_schema.py` | shared objective builder and validators | WIRED | Completed and not-feasible rows are validated before return. |
| `scripts/run_closed_loop_suite.py` | `scripts/finite_storage_schema.py` | schema metadata constants | WIRED | Suite output carries nested schema metadata. |
| `scripts/render_paper_artifacts.py` | `scripts/claim_policy.py` and Phase 6 JSON guards | central forbidden checks and `validate_phase6_guard_artifacts` | WIRED | Paper-facing validation fails closed unless all guard artifacts exist and pass. |
| `scripts/reproduce_blocks.py` | Phase 6 artifacts | registry block `phase6_claim_state_guards` | WIRED | Reproduction registry lists all Phase 6 guard artifacts and five requirement IDs. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `phase6_claim_policy.json` | `allowed_claims`, `evidence_categories`, forbidden patterns | `claim_policy.bounded_claim_policy()` via `write_policy_artifact()` | Yes | FLOWING |
| `phase6_claim_audit.json` | `checked_paths`, `forbidden_hits`, quarantine hits | `audit_claim_discipline.audit_claim_paths()` scanning configured repo/report surfaces | Yes | FLOWING |
| `phase6_explicit_state_schema.json` | state/objective field schema | `finite_storage_schema.schema_artifact_payload()` | Yes | FLOWING |
| `phase6_state_objective_fixtures.json` | `samples[*].finite_storage_state`, `samples[*].objective_components` | `generate_static_regime_states.generate_payload()` from SUMO network metadata plus deterministic regime generators | Yes | FLOWING |
| Closed-loop rows | `finite_storage_state`, `objective_components` | `run_closed_loop_sumo.run_experiment()` / `infeasible_row()` using schema builders and validators | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full automated test suite passes | `python3 -m pytest /home/samuel/projects/pi_light_OR/tests -q` | `41 passed in 0.81s` | PASS |
| Claim audit fails closed/passes current bounded repo scan | `python3 /home/samuel/projects/pi_light_OR/scripts/audit_claim_discipline.py --root /home/samuel/projects/pi_light_OR --policy-out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase6_claim_policy.json --audit-out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase6_claim_audit.json` | JSON status `PASSED` | PASS |
| Phase 6 explicit fixture/schema generation works | `python3 /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py --target-per-regime 3 --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase6_state_objective_fixtures.json --schema-out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase6_explicit_state_schema.json` | JSON status `PASSED`, 18 samples | PASS |
| Generated JSON artifacts contain required schema | Python JSON validation script over all four Phase 6 artifacts | All checks true | PASS |

### Probe Execution

No probe scripts were declared for Phase 6, and no conventional `scripts/*/tests/probe-*.sh` probes were found or required for this repository phase. Status: SKIPPED.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| CLAIM-01 | 06-01, 06-03 | Bounded claim: recover/tie max-pressure when slack, improvement only in binding regimes | SATISFIED | `claim_policy.py` and `phase6_claim_policy.json` encode permitted claim and allowed claim categories. |
| CLAIM-02 | 06-01, 06-03 | Prevent v1.0 pressure-equivalent evidence from being described as dual superiority | SATISFIED | Claim audit CLI, renderers, paper artifacts, and reproduce blocks use central forbidden checks; audit status `PASSED`. |
| STATE-01 | 06-02 | Replace proxy-only labels with explicit downstream storage, residual receiving capacity, spillback/blocking, switching-loss, service urgency, incident/capacity-drop fields | SATISFIED | `finite_storage_schema.py` validators and regenerated fixture samples contain all exact state fields. |
| STATE-02 | 06-02 | Predeclare delay, unfinished-vehicle penalty, spillback/blocking time, switching lost-time terms | SATISFIED | `OBJECTIVE_COMPONENT_FIELDS` and `build_objective_components_from_metrics()` define the exact four terms; artifacts contain them. |
| STATE-03 | 06-03 | Static fixtures and closed-loop runners emit schema-validated artifacts with explicit state/objective fields | SATISFIED | Static generator, static kill gate, and closed-loop runner call validators; tests cover malformed rejection and row validation. |

No additional Phase 6 requirements are orphaned in `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md`.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `scripts/audit_claim_discipline.py` | 63, 67, 78, 91 | Empty return values | Info | Legitimate no-file/no-prose/no-error branches; not user-visible stubs. |
| `scripts/reproduce_blocks.py` | 231 | `return {}` | Info | Legitimate `json_count()` fallback for non-dict/non-list payloads. |
| `tests/test_closed_loop_sumo.py` | 443-449 | `placeholder_guard` variable name | Info | Negative test fixture proving status-only placeholder guard fails closed. |

No unreferenced `TBD`, `FIXME`, or `XXX` markers were found in Phase 6 modified files.

### Human Verification Required

None. Phase goal concerns machine-readable claim discipline, JSON artifacts, schema validation, and runnable CLIs/tests; these were programmatically verified.

### Gaps Summary

No blocking gaps found. The Phase 6 goal is achieved in the codebase: bounded claim policy exists and is wired into audits/renderers/reproducibility, explicit finite-storage state/objective artifacts exist with validators and generated samples, v1.0 pressure-equivalent overclaim language is mechanically guarded, and all five declared requirement IDs are accounted for.

---

_Verified: 2026-05-24T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
