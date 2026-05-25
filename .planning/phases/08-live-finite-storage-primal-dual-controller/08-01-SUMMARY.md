---
phase: 08-live-finite-storage-primal-dual-controller
plan: 01
status: complete
completed: 2026-05-24
requirements:
  - CTRL-01
  - CTRL-02
  - CTRL-03
  - CTRL-04
---

# Phase 8 Plan 01 Summary

## Files Modified

- `scripts/run_closed_loop_sumo.py`
- `tests/test_closed_loop_sumo.py`

## What Changed

- Added `finite_storage_primal_dual` to `CONTROLLER_REGISTRY` while keeping `full_dual_symbolic` in `NOT_FEASIBLE_CONTROLLERS`.
- Added finite-storage decomposition helpers with exact components: `pressure`, `downstream_storage`, `spillback`, `switching`, `service`, `incident`, `total`.
- Added audited finite-storage action selection with pressure action, finite-storage action, selected action, phase scores, component totals, action-change flag, and changing terms.
- Wired `finite_storage_primal_dual` into closed-loop SUMO action selection without changing `choose_controller_action(...) -> int` for existing call sites.
- Added completed-row `action_decomposition` for the new controller only, preserving `finite_storage_state`, `objective_components`, `METRIC_FIELDS`, and aggregate behavior.
- Preserved `full_dual_symbolic` not-feasible honesty; not-feasible rows remain schema-valid and do not include successful action audit data.

## Tests Added

- Registry/guard tests for `finite_storage_primal_dual` and `full_dual_symbolic`.
- Exact decomposition key and component-total tests.
- Isolated nonzero correction tests for downstream storage, spillback, switching, service urgency, and incident/capacity-drop terms.
- Slack fixture test showing finite-storage selection recovers pressure behavior.
- Binding fixture test showing finite-storage action differs from pressure and reports storage/spillback changing terms.
- Mandatory short `run_experiment()` row-audit test proving the new controller completes and emits nonempty `action_decomposition.last_decision_by_tls`.
- Script-style `tests/test_closed_loop_sumo.py` entrypoint now invokes Phase 8 tests.

## Review Fixes

Initial review found issues in first-decision switching timing, incident edge matching, empty action audit validation, and script-style test coverage. All were fixed before final verification.

## Verification Results

- `python3 -m py_compile scripts/run_closed_loop_sumo.py tests/test_closed_loop_sumo.py` — passed.
- `python3 -m pytest tests/test_closed_loop_sumo.py -q` — 27 passed.
- `python3 -m pytest tests/test_closed_loop_sumo.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q` — 42 passed.
- `python3 tests/test_closed_loop_sumo.py` — passed.
- `python3 scripts/run_closed_loop_sumo.py --network single --controllers finite_storage_primal_dual full_dual_symbolic --seeds 20260524 --steps 80 --warmup 20 --action-interval 10 --out /tmp/phase8_controller_smoke.json` — passed, 2 rows.

## Scope Boundaries Preserved

- No Gate A/B/C implementation.
- No new baselines or stress suite.
- No long-horizon paired-seed evidence.
- No manuscript drafting or closed-loop dominance claim.
- No relabeling of unsafe `full_dual_symbolic` as the proposed method.
