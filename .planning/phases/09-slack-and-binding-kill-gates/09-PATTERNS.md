---
phase: 09-slack-and-binding-kill-gates
status: complete
requirements:
  - GATE-01
  - GATE-02
  - GATE-04
---

# Phase 9 Pattern Map

## Closest Existing Patterns

| New Need | Existing Analog | Reuse Pattern |
|---|---|---|
| JSON gate runner | `scripts/run_static_kill_gate.py` | argparse defaults, fail-closed validation, deterministic artifact write |
| Machine-readable pass/fail gates | `scripts/run_closed_loop_suite.py` | `completion_gates`, `gates_pass`, payload status fields |
| Explicit state/objective validation | `scripts/finite_storage_schema.py` | `validate_state_objective_sample` |
| Runtime action audit | `scripts/run_closed_loop_sumo.py` | `select_finite_storage_action_with_audit` and exact decomposition fields |
| Tests for gate failures | `tests/test_run_static_kill_gate.py` and `tests/test_closed_loop_sumo.py` | Pure fixture mutations that assert `ValueError` or `FAILED` status |

## New File Mapping

### `scripts/run_slack_binding_gates.py`

Place next to the other experiment runners. Keep it stdlib-only and deterministic.

Closest analogs:

- Parse/write structure from `run_static_kill_gate.py`.
- Gate payload style from `run_closed_loop_suite.py`.
- Helper imports from `run_closed_loop_sumo.py` and `finite_storage_schema.py`.

Expected exported helpers:

- `load_phase7_examples`
- `example_to_two_phase_fixture`
- `validate_explicit_gate_example`
- `validate_action_audit`
- `evaluate_gate_a_slack`
- `evaluate_gate_b_binding`
- `build_payload`
- `gates_pass`
- `write_gate_artifact`

### `tests/test_slack_binding_gates.py`

Closest analogs:

- Import style from `tests/test_theory_separation.py` and `tests/test_closed_loop_sumo.py`.
- Negative fixture mutation style from `tests/test_run_static_kill_gate.py`.

Required test groups:

1. Gate A passes on Phase 7 slack fixture and reports recovery/tie rather than superiority.
2. Gate B passes on Phase 7 binding fixture and reports action separation plus strict objective improvement.
3. Missing `finite_storage_state` fails closed.
4. Missing `objective_components` fails closed.
5. Missing action audit fields fails closed.
6. Missing pressure comparator fields fails closed.
7. Payload excludes Gate C / paired-seed dominance / baseline-suite claims.
8. CLI writes parseable JSON artifact with `status: PASSED` on canonical inputs.

## Guardrails

- Do not add to `run_closed_loop_suite.py` in Phase 9.
- Do not call SUMO from Phase 9 tests.
- Do not create Gate C, paired-seed confidence intervals, baseline coverage, stress scenarios, or long-horizon statistics.
- Do not make broad closed-loop dominance claims.
