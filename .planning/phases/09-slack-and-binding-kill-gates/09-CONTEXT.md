---
phase: 09-slack-and-binding-kill-gates
status: ready_for_planning
requirements:
  - GATE-01
  - GATE-02
  - GATE-04
depends_on:
  - phase: 08-live-finite-storage-primal-dual-controller
    provides: finite_storage_primal_dual helpers, action decomposition contract, slack/binding fixture tests
  - phase: 07-theory-and-separation-package
    provides: deterministic slack and binding examples with objective margins
  - phase: 06-claim-discipline-and-explicit-state-foundation
    provides: explicit state/objective schema and claim discipline
---

# Phase 9: Slack and Binding Kill Gates — Context

## Phase Boundary

Phase 9 builds fail-closed gates for slack-regime recovery and binding-regime action/objective separation. It must distinguish Gate A recovery evidence from Gate B separation evidence and must fail closed when explicit state, objective components, action decomposition, or pressure comparators are missing.

This phase must not implement Gate C, paired-seed closed-loop dominance, new baseline suites, stress scenarios, long-horizon evidence, statistical dominance tests, or manuscript claims. Those belong to Phases 10–12.

## Required Outcomes

- **GATE-01:** Gate A verifies slack-regime recovery: finite-storage action matches pressure/backpressure or pressure action lies in a tie set; ties are reported as expected behavior, not wins.
- **GATE-02:** Gate B verifies binding-regime separation: finite-storage action differs from pressure and improves a predeclared constrained objective or one-step objective on explicit finite-storage/spillback/switching/incident state.
- **GATE-04:** Gates fail closed when required explicit fields, action decomposition, pressure comparator, objective data, or required source artifacts are missing.

## Available Inputs

- `experiments/dual_sensitivity/phase7_theory_separation.json`
  - `slack_recovery`
  - `storage_binding_two_phase_separation`
  - `objective_totals`, `objective_margin`, `pressure_action`, `finite_storage_action`, tie sets
- `scripts/run_closed_loop_sumo.py`
  - `select_finite_storage_action_with_audit`
  - `finite_storage_phase_decomposition`
  - `FINITE_STORAGE_DECOMPOSITION_FIELDS`
- `scripts/finite_storage_schema.py`
  - `validate_state_objective_sample`
  - `validate_finite_storage_state`

## Design Decisions

### D-09-01 Gate Shape

Use a small deterministic gate runner such as `scripts/run_slack_binding_gates.py` rather than expanding the closed-loop suite. Phase 9 gates are explicit-state and action-decomposition gates, not journal-grade closed-loop performance evidence.

### D-09-02 Artifact Shape

Emit a machine-readable JSON artifact under `experiments/dual_sensitivity/phase9_slack_binding_gates.json` with:

- top-level `status: PASSED|FAILED`
- `scope: static_explicit_state_action_decomposition_only_no_gate_c`
- `requirements_covered: [GATE-01, GATE-02, GATE-04]`
- `gate_a_slack_recovery`
- `gate_b_binding_separation`
- `fail_closed_checks`
- caveats forbidding Gate C/dominance interpretation

### D-09-03 Fail-Closed Behavior

Missing source artifact, missing explicit state/objective components, missing action-audit fields, missing pressure comparator fields, non-strict objective improvement in binding examples, or absent binding examples must make the gate status `FAILED` or raise in tests. It must not silently skip.

### D-09-04 Claim Discipline

Gate A output must use recovery/tie language. Gate B output may use separation and one-step constrained-objective improvement language only. No output may claim closed-loop dominance, universal superiority, deployment readiness, paired-seed evidence, or baseline-suite evidence.

## Implementation Expectations

- Add pure helper functions to evaluate Gate A and Gate B from Phase 7 examples translated into Phase 8 runtime helper inputs.
- Recompute action audit via `select_finite_storage_action_with_audit` rather than trusting only stored static action labels.
- Validate every example with `validate_state_objective_sample`.
- Add tests for pass cases and fail-closed negative cases.
- Keep implementation CPU/stdlib-only; no new dependencies.

## Out of Scope

- Gate C closed-loop dominance.
- Paired seeds, confidence intervals, statistical tests.
- New baselines or stress scenarios.
- Long-horizon SUMO evidence.
- Manuscript text or broad performance claims.
