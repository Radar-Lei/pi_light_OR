---
phase: 10-strong-baselines-and-stress-scenario-suite
status: ready_for_planning
requirements:
  - EXP-01
  - EXP-02
  - EXP-04
depends_on:
  - phase: 09-slack-and-binding-kill-gates
    provides: fail-closed Gate A/B artifact and explicit state/action-decomposition preconditions
  - phase: 08-live-finite-storage-primal-dual-controller
    provides: finite_storage_primal_dual controller and completed-row action audit
---

# Phase 10: Strong Baselines and Stress Scenario Suite — Context

## Phase Boundary

Phase 10 adds honest operational/pressure baselines and explicit finite-storage stress scenario scaffolding. It should make the experiment suite capable of running the new controller against stronger comparators under explicit downstream blockage, spillback, incident/capacity-drop, oversaturation, turning-shock, and switching-loss-sensitive regimes.

This phase must not run journal-grade long-horizon paired-seed dominance evidence, compute paired confidence intervals, implement Gate C, or write manuscript claims. Phase 11 owns paired-seed dominance/statistics.

## Required Outcomes

- **EXP-01:** Suite includes optimized fixed-time, actuated/semi-actuated or local actuation, classical max-pressure, capacity-aware pressure, and feasible cycle-based or finite-storage/double-pressure variants where feasible.
- **EXP-02:** Suite explains/tests the current grid fixed-time counterexample before any broad performance language is used.
- **EXP-04:** Stress scenarios include downstream blockage, spillback, incident/lane capacity drop, oversaturation, turning shock, and switching-loss-sensitive regimes.

## Current Implementation

- `scripts/run_closed_loop_sumo.py` already supports controllers: `fixed_time`, `actuated_local_pressure`, `max_pressure`, `capacity_aware_pressure`, `finite_storage_primal_dual`, and symbolic variants.
- `scripts/run_closed_loop_suite.py` currently runs scenarios: `single_sanity`, `arterial_main`, `grid_scalability`, `arterial_demand_shift`, `arterial_bottleneck_failure_mode`.
- Existing failure mode reduces speed on a selected edge for bottleneck/failure scenarios.
- Existing demand shift inserts vehicles periodically.
- Phase 8 completed-row `finite_storage_state`, `objective_components`, and `action_decomposition` are available for `finite_storage_primal_dual`.

## Design Decisions

### D-10-01 Baseline Scope

Add only lightweight feasible baselines in the current runner:

- retain `fixed_time`, `actuated_local_pressure`, `max_pressure`, `capacity_aware_pressure`
- include `finite_storage_primal_dual` as the proposed/controller-under-test
- add one or two simple operational pressure variants if lightweight, e.g. `cycle_pressure` and `finite_storage_double_pressure`, without external optimization packages
- keep `local_pilight` and old `full_dual_symbolic` honest if not feasible

### D-10-02 Stress Scenario Scope

Add scenario tags and metadata for explicit stress types. Smoke tests may use short horizons only to prove selectability and schema/scenario mechanics, not dominance.

Candidate tags:

- `arterial_downstream_blockage`
- `arterial_spillback_stress`
- `arterial_incident_capacity_drop`
- `arterial_oversaturation`
- `arterial_turning_shock`
- `arterial_switching_loss_sensitive`
- keep existing `grid_scalability` and add metadata explaining grid fixed-time counterexample checks

### D-10-03 Artifact Scope

Produce a Phase 10 suite/spec artifact such as `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` that documents controller coverage, stress scenario coverage, explicit state/audit availability, and scope caveats. It may contain smoke rows, but must not be described as performance dominance evidence.

## Out of Scope

- Gate C.
- Long-horizon paired-seed evidence.
- Paired bootstrap/t/Wilcoxon statistics.
- Broad dominance or deployment claims.
- Manuscript drafting.
- Neural/RL benchmark expansion.
