---
phase: 08-live-finite-storage-primal-dual-controller
status: draft
requirements:
  - CTRL-01
  - CTRL-02
  - CTRL-03
  - CTRL-04
---

# Phase 8 Validation Strategy

## Goal

Verify that Phase 8 adds a safe live finite-storage primal-dual controller path with auditable score decompositions, while preserving `full_dual_symbolic` not-feasible honesty and avoiding closed-loop dominance claims.

## Required Truths

1. `finite_storage_primal_dual` is registered, selectable, and not blocked by `NOT_FEASIBLE_CONTROLLERS`.
2. `full_dual_symbolic` remains explicitly `not_feasible` unless a future plan safely aliases it; Phase 8 must not relabel it as the proposed method.
3. Finite-storage movement/phase decomposition exposes exactly `pressure`, `downstream_storage`, `spillback`, `switching`, `service`, `incident`, and `total`, with `total` equal to the component sum.
4. Slack deterministic fixtures recover or tie max-pressure behavior.
5. Binding deterministic fixtures change action relative to pressure and identify the storage/spillback terms responsible.
6. Completed rows for the new controller include schema-valid `finite_storage_state`, `objective_components`, and compact `action_decomposition` audit data.

## Expected Modified Files

- `scripts/run_closed_loop_sumo.py`
- `tests/test_closed_loop_sumo.py`

## Verification Commands

Targeted compile/test:

```bash
cd /home/samuel/projects/pi_light_OR && python3 -m py_compile scripts/run_closed_loop_sumo.py tests/test_closed_loop_sumo.py
cd /home/samuel/projects/pi_light_OR && python3 -m pytest tests/test_closed_loop_sumo.py -q
```

Relevant regression tests:

```bash
cd /home/samuel/projects/pi_light_OR && python3 -m pytest tests/test_closed_loop_sumo.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q
```

Optional SUMO smoke after pure tests pass:

```bash
cd /home/samuel/projects/pi_light_OR && python3 scripts/run_closed_loop_sumo.py --network single --controllers finite_storage_primal_dual full_dual_symbolic --seeds 20260524 --steps 80 --warmup 20 --action-interval 10 --out /tmp/phase8_controller_smoke.json
```

The optional smoke verifies selectability and not-feasible honesty only. It must not be described as performance evidence.

## Scope Guards

- Do not remove the `full_dual_symbolic` not-feasible guard unless explicitly replaced by a tested safe alias.
- Do not add Gate A/B/C logic; Phase 9 owns gates.
- Do not add new baselines or stress scenarios; Phase 10 owns those.
- Do not run long-horizon paired-seed evidence; Phase 11 owns that.
- Do not write final manuscript sections or broad dominance claims.
