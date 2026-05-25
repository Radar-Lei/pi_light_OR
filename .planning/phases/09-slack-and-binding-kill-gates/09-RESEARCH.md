---
phase: 09-slack-and-binding-kill-gates
status: complete
requirements:
  - GATE-01
  - GATE-02
  - GATE-04
---

# Phase 9 Research Notes

## Recommended Approach

Implement Phase 9 as a lightweight deterministic gate runner, not as a closed-loop experiment suite. The runner should consume the Phase 7 separation JSON and Phase 8 runtime audit helpers to verify two gates:

- Gate A: slack recovery/tie behavior.
- Gate B: binding action separation plus strict one-step constrained objective improvement.

## Existing Patterns to Reuse

- `scripts/run_static_kill_gate.py`: fail-closed required-field validation and JSON artifact style.
- `scripts/run_closed_loop_suite.py`: pure `gates_pass()` style and machine-readable status fields.
- `scripts/run_closed_loop_sumo.py`: `select_finite_storage_action_with_audit`, `FINITE_STORAGE_DECOMPOSITION_FIELDS`, and action audit shape.
- `scripts/finite_storage_schema.py`: `validate_state_objective_sample` for explicit state/objective validation.

## Suggested Files

- New: `scripts/run_slack_binding_gates.py`
- New: `tests/test_slack_binding_gates.py`
- New artifact when command runs: `experiments/dual_sensitivity/phase9_slack_binding_gates.json`

## Implementation Guidance

Core helpers:

- `load_phase7_examples(path)`
- `example_to_two_phase_fixture(example)`
- `validate_explicit_gate_example(example)`
- `validate_action_audit(audit)`
- `evaluate_gate_a_slack(examples)`
- `evaluate_gate_b_binding(examples)`
- `build_payload(examples, input_path)`
- `gates_pass(payload)`
- `write_gate_artifact(path, phase7_path)`

Gate A should filter the `slack_recovery` example, recompute the finite-storage audit, and pass only if the finite-storage action matches the pressure action or the pressure action is in the declared/computed tie set. Tie cases should be reported as ties, not wins.

Gate B should filter binding/separation examples, recompute the finite-storage audit, require `finite_storage_action != pressure_action`, require `changing_terms` to intersect storage/spillback/switching/incident terms, and require strict objective improvement from `objective_totals` or `objective_margin`.

Fail-closed checks should reject missing explicit state, missing objective components, missing action audit fields, missing pressure comparator fields, missing examples, or status-only artifacts.

## Artifact Shape

```json
{
  "experiment": "phase9_slack_binding_gates",
  "status": "PASSED",
  "scope": "static_explicit_state_action_decomposition_only_no_gate_c",
  "requirements_covered": ["GATE-01", "GATE-02", "GATE-04"],
  "inputs": ["experiments/dual_sensitivity/phase7_theory_separation.json"],
  "gate_a_slack_recovery": {},
  "gate_b_binding_separation": {},
  "fail_closed_checks": {},
  "caveats": ["No Gate C, paired-seed dominance, baseline suite, or closed-loop superiority claim."]
}
```

## Open Questions (RESOLVED)

- **Should Phase 9 run SUMO?** No. Use deterministic explicit-state gates only. Closed-loop dominance belongs to Phase 11.
- **Should Phase 9 add baselines/stress scenarios?** No. Phase 10 owns baselines and stress scenarios.
- **Should Gate B claim performance dominance?** No. It may claim static/action-decomposition separation and one-step constrained-objective improvement only.
