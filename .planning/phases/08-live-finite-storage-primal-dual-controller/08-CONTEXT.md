---
phase: 08-live-finite-storage-primal-dual-controller
status: ready_for_research_and_planning
generated: 2026-05-24
requirements:
  - CTRL-01
  - CTRL-02
  - CTRL-03
  - CTRL-04
depends_on:
  - phase: 07-theory-and-separation-package
    provides: deterministic finite-storage scoring/separation artifact and bounded theory memo
  - phase: 06-claim-discipline-and-explicit-state-foundation
    provides: finite_storage_state schema, objective_components schema, closed-loop row contract, and claim policy
---

# Phase 8: Live Finite-Storage Primal-Dual Controller — Context

## Phase Boundary

This phase implements a safe live finite-storage primal-dual controller path for closed-loop SUMO selection and row-level audit. It must convert the Phase 7 static separation logic into a runtime controller that computes movement/phase scores from current queues, capacities, switching state, service urgency, and incident metadata.

This phase must not claim closed-loop dominance, build kill gates, add stress scenarios, add strong baseline suites, run journal-grade paired-seed evidence, or draft manuscript text. Those belong to later phases.

## Required Outcomes

- **CTRL-01:** A live finite-storage primal-dual pressure controller computes movement/phase scores using queue pressure plus downstream storage, spillback, switching, service, and incident shadow-price corrections.
- **CTRL-02:** A safe `full_dual_symbolic` successor is wired into closed-loop SUMO without relabeling the existing unsafe queue heuristic as the proposed method.
- **CTRL-03:** Deterministic slack fixtures show the controller reduces to existing pressure-equivalent behavior when finite-storage/operational constraints are slack.
- **CTRL-04:** Controller outputs include auditable score decompositions showing which shadow-price terms changed the action in binding regimes.

## Existing Runtime Interfaces

Relevant files:

- `scripts/run_closed_loop_sumo.py`
- `tests/test_closed_loop_sumo.py`
- `scripts/finite_storage_schema.py`
- `scripts/check_theory_separation.py`
- `experiments/dual_sensitivity/phase7_theory_separation.json`

Current closed-loop action selection lives in `choose_controller_action()` and delegates movement scoring to `movement_score()` / `phase_score()`.

Existing controllers include:

- `max_pressure`
- `capacity_aware_pressure`
- `raw_neighbor_symbolic`
- `all_neighbor_symbolic`
- `random_permuted_dual`
- `full_dual_symbolic` — currently listed in `NOT_FEASIBLE_CONTROLLERS` with reason: closed-loop per-TLS dual Scenario conversion is not yet safe for live SUMO actuation.

Phase 8 should not simply remove that guard and reuse the unsafe old label. The safe path should either:

1. add a new explicit controller name such as `finite_storage_primal_dual`, or
2. make `full_dual_symbolic` an alias only after the new safe scoring/decomposition path exists and tests prove it is not the old unsafe queue heuristic.

The recommended default is a new explicit `finite_storage_primal_dual` controller while keeping old `full_dual_symbolic` not feasible until a deliberate alias decision is tested.

## Upstream Theory and Schema Contracts

### Phase 7 scoring/separation contract

`phase7_theory_separation.json` contains:

- `slack_recovery`: pressure and finite-storage scores/actions match under slack state.
- `storage_binding_two_phase_separation`: pressure selects blocked downstream `phase_a`; finite-storage scoring penalizes storage/spillback and selects `phase_b` with lower one-step objective.
- finite-storage score pattern: pressure plus explicit storage/scarcity correction terms.

Phase 8 can reuse the concept but must implement runtime score decomposition rather than just static JSON checking.

### Phase 6 state/objective contract

Every completed or not-feasible closed-loop row must carry:

- `finite_storage_state`
- `objective_components`

Required `finite_storage_state` keys:

- `downstream_storage`
- `residual_receiving_capacity`
- `spillback_blocking`
- `switching_loss_state`
- `service_urgency`
- `incident_capacity_drop`

Required objective components:

- `delay`
- `unfinished_vehicle_penalty`
- `spillback_blocking_time`
- `switching_lost_time`

Phase 8 action-decomposition outputs must align with this schema rather than introducing unrelated field names.

## Design Decisions

### D-08-01 Controller Naming

Default to adding `finite_storage_primal_dual` as the safe live successor. Keep `full_dual_symbolic` marked `not_feasible` unless a plan explicitly and safely aliases it to the new path with tests. This prevents relabeling unsafe queue heuristics as the proposed method.

### D-08-02 Score Decomposition

A movement score should decompose into auditable terms:

- `pressure`: upstream queue minus downstream queue.
- `downstream_storage`: penalty or correction when residual receiving capacity is low.
- `spillback`: penalty when downstream spillback/blocking flags bind.
- `switching`: penalty for switching away from current phase when switching loss applies.
- `service`: service urgency correction, preferably favoring high upstream urgency while preserving slack recovery when neutral.
- `incident`: penalty when downstream incident/capacity-drop metadata lowers effective capacity.
- `total`: sum of components.

Phase scores should aggregate movement decompositions for green movements in each candidate phase and expose enough detail to show which term changed action relative to `max_pressure` in binding fixtures.

### D-08-03 Slack Reduction

When residual receiving capacity is positive, spillback/blocking is false, incident inactive, switching penalty neutral/zero, and service correction is ranking-neutral, finite-storage action must match or tie `max_pressure` on deterministic fixtures.

### D-08-04 Binding Separation

When a pressure-preferred phase sends flow into a blocked or capacity-constrained downstream link, finite-storage scoring should select a different feasible phase if the correction exceeds the pressure gap. Tests should reuse the Phase 7 example values or a direct equivalent.

### D-08-05 Runtime Row Audit

Closed-loop rows for the new controller should include score decomposition audit data. Prefer a compact row-level field such as `score_decomposition` or `action_decomposition` that records at least the last action decision per TLS, including pressure action, finite-storage action, selected action, selected phase scores, and component totals.

## Implementation Expectations

Expected implementation should be lightweight and testable without requiring full SUMO execution for core behavior:

- Add pure helper functions for finite-storage movement/phase score decomposition.
- Add deterministic fixture tests for slack recovery and binding action separation.
- Wire the new controller name into `CONTROLLER_REGISTRY` and `choose_controller_action()`.
- Ensure `NOT_FEASIBLE_CONTROLLERS` does not block the new controller.
- Add row-level audit decomposition for completed rows when the new controller is used.
- Keep not-feasible rows schema-valid and honest.

## Out of Scope

- Gate A/B/C implementation — Phase 9 and Phase 11.
- Strong baselines and stress scenario suite — Phase 10.
- Long-horizon paired-seed evidence — Phase 11.
- Future manuscript-input templates — Phase 12.
- Any broad closed-loop dominance claim.
- Removing `full_dual_symbolic` safety guard without a tested safe successor.

## Verification Expectations

Phase 8 planning should include checks such as:

- Unit tests for finite-storage movement decomposition component keys and totals.
- Unit tests showing slack fixture action matches max-pressure.
- Unit tests showing binding fixture action differs from max-pressure and identifies the changing correction terms.
- Tests that `finite_storage_primal_dual` is selectable through `choose_controller_action()` and registered in `CONTROLLER_REGISTRY`.
- Tests that `full_dual_symbolic` remains not-feasible unless safely aliased by explicit plan decision.
- Tests that closed-loop rows include schema-valid `finite_storage_state`, `objective_components`, and auditable score/action decomposition for the new controller path.

## Resolved Decisions by Autonomous Defaults

- **Controller name:** use `finite_storage_primal_dual` as the safe successor; keep `full_dual_symbolic` not feasible for now.
- **Initial correction formula:** mirror Phase 7 analytic storage/spillback correction and extend with switching/service/incident terms as explicit additive components.
- **SUMO dependency in tests:** core controller behavior should be pure unit tests; only existing lightweight `run_experiment` not-feasible patterns should be used unless a smoke run is already cheap and reliable.
- **Claim language:** controller implementation supports auditability only; no dominance claim in Phase 8.
