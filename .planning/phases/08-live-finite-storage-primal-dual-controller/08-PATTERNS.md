# Phase 8: Live Finite-Storage Primal-Dual Controller - Pattern Map

**Mapped:** 2026-05-24  
**Files analyzed:** 2 new/modified implementation files  
**Analogs found:** 2 / 2  
**Scope:** 只读源码映射；除本 PATTERNS artifact 外不修改源码。

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/run_closed_loop_sumo.py` | utility / live SUMO controller runner / controller scoring helpers | request-response action selection + TraCI event loop + row JSON audit | `scripts/run_closed_loop_sumo.py` existing controller registry, `movement_score()`, `phase_score()`, `choose_controller_action()`, row builders; secondary analog `scripts/check_theory_separation.py` score separation helpers | exact in-place extension |
| `tests/test_closed_loop_sumo.py` | test | pure function assertions + schema validation + not-feasible row contract | `tests/test_closed_loop_sumo.py` existing registry/action/schema tests; secondary analog `tests/test_theory_separation.py` deterministic slack/binding separation assertions | exact in-place extension |

## Pattern Assignments

### `scripts/run_closed_loop_sumo.py` (utility/controller runner, request-response + event-loop row audit)

**Primary analog:** existing `scripts/run_closed_loop_sumo.py`  
**Secondary analog:** `scripts/check_theory_separation.py` for Phase 7 finite-storage separation scoring.

#### Imports / schema dependency pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 13-21

```python
from claim_policy import forbidden_claim_hits
from finite_storage_schema import (
    OBJECTIVE_COMPONENT_FIELDS,
    build_finite_storage_state,
    build_objective_components_from_metrics,
    validate_finite_storage_state,
    validate_state_objective_sample,
)
from sample_sumo_states import build_network_metadata
```

**Copy/adapt:** 新 finite-storage controller 不应新增独立 schema。继续从 `finite_storage_schema` 复用 `build_finite_storage_state()`, `validate_finite_storage_state()`, `validate_state_objective_sample()`，并让 row audit 与 `OBJECTIVE_COMPONENT_FIELDS` 对齐。

#### Controller registry pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 37-47

```python
CONTROLLER_REGISTRY = {
    "fixed_time": "Deterministic cycle through green phases.",
    "actuated_local_pressure": "Queue-triggered local pressure with fixed-time fallback.",
    "max_pressure": "Movement score q_up - q_down.",
    "capacity_aware_pressure": "Pressure with downstream fullness penalty.",
    "local_pilight": "Real PI-Light/DSL baseline if adaptable; otherwise explicit not_feasible.",
    "raw_neighbor_symbolic": "Symbolic upstream queue minus downstream queue.",
    "all_neighbor_symbolic": "Symbolic pressure with downstream slack/fullness terms.",
    "random_permuted_dual": "Deterministic seed-based placebo movement score.",
    "full_dual_symbolic": "Per-TLS dual policy where feasible; otherwise explicit not_feasible.",
}
```

**Copy/adapt:** add `finite_storage_primal_dual` here with an honest description such as “Live finite-storage pressure with downstream storage, spillback, switching, service, and incident corrections.” Keep the description bounded to controller mechanics/auditability; do not claim dominance.

#### Unsafe controller guard pattern to preserve

**Source:** `scripts/run_closed_loop_sumo.py` lines 62-65

```python
NOT_FEASIBLE_CONTROLLERS = {
    "local_pilight": "No safely adaptable PI-Light local DSL baseline is present in the SUMO runner interface.",
    "full_dual_symbolic": "Closed-loop per-TLS dual Scenario conversion is not yet safe for live SUMO actuation.",
}
```

**Required Phase 8 rule:** do **not** reuse the unsafe old `full_dual_symbolic` path by simply removing this guard. Add a new `finite_storage_primal_dual` controller that is not listed in `NOT_FEASIBLE_CONTROLLERS`. Keep `full_dual_symbolic` not feasible unless a later explicit alias plan proves it delegates to the new safe scoring/decomposition path.

#### Argument validation / unknown controller pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 86-93

```python
def validate_args(args: argparse.Namespace) -> None:
    unknown = sorted(set(args.controllers) - set(CONTROLLER_REGISTRY))
    if unknown:
        raise ValueError(f"Unknown controllers: {unknown}. Available: {sorted(CONTROLLER_REGISTRY)}")
    if args.steps <= 0 or args.warmup < 0 or args.action_interval <= 0:
        raise ValueError("--steps and --action-interval must be positive; --warmup must be nonnegative")
    if not args.seeds:
        raise ValueError("At least one seed is required")
```

**Copy/adapt:** once `finite_storage_primal_dual` is in `CONTROLLER_REGISTRY`, this validation automatically allows CLI selection. Add tests that verify it is known and not blocked by `NOT_FEASIBLE_CONTROLLERS`.

#### Existing movement score pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 160-184

```python
def movement_score(
    controller: str,
    movement: tuple[str, str],
    queues: dict[str, float],
    capacities: dict[str, float],
    seed: int = 0,
) -> float:
    upstream, downstream = movement
    up_q = float(queues.get(upstream, 0.0))
    down_q = float(queues.get(downstream, 0.0))
    pressure = up_q - down_q
    if controller in {"max_pressure", "raw_neighbor_symbolic"}:
        return pressure
    if controller == "actuated_local_pressure":
        return up_q if sum(queues.values()) >= 1.0 else 0.0
    if controller in {"capacity_aware_pressure", "all_neighbor_symbolic"}:
        cap = max(float(capacities.get(downstream, 1.0)), 1.0)
        fullness = down_q / cap
        slack = cap - down_q
        blocked_penalty = cap if fullness >= 0.85 else 0.0
        return pressure + 0.05 * slack - fullness * up_q - blocked_penalty
    if controller == "random_permuted_dual":
        key = sum(ord(ch) for ch in upstream + downstream) + int(seed)
        return pressure * (1.0 if key % 2 == 0 else -0.5)
    return 0.0
```

**Copy/adapt:** do not overload this with opaque queue heuristics only. Prefer adding pure helpers:

- `finite_storage_movement_decomposition(...) -> dict[str, float]`
- `finite_storage_movement_score(...) -> float` or use `decomposition["total"]`
- optionally `finite_storage_phase_decomposition(...) -> dict[str, Any]`

The new controller’s total should be auditable as additive components, not a hidden scalar.

#### Phase score aggregation pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 187-204

```python
def phase_score(
    controller: str,
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
    capacities: dict[str, float],
    seed: int = 0,
) -> float:
    if not states:
        return 0.0
    state = states[phase_index % len(states)]
    score = 0.0
    for move_idx, movement in enumerate(movements):
        signal = state[move_idx] if move_idx < len(state) else "r"
        if signal in "Gg":
            score += movement_score(controller, movement, queues, capacities, seed)
    return score
```

**Copy/adapt:** for `finite_storage_primal_dual`, aggregate per-movement decompositions over green movements. Keep existing `Gg` logic and deterministic fallback. The phase-level object should contain per-component totals and optionally per-movement components.

#### Action selection pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 207-227

```python
def choose_controller_action(
    controller: str,
    tls_id: str,
    current_phase: int,
    step: int,
    action_interval: int,
    phase_states: dict[str, list[str]],
    tls_movements: dict[str, list[tuple[str, str]]],
    queues: dict[str, float],
    capacities: dict[str, float],
    seed: int = 0,
) -> int:
    states = phase_states.get(tls_id, [])
    greens = green_phases(states)
    if controller == "fixed_time" or (controller == "actuated_local_pressure" and sum(queues.values()) < 1.0):
        return greens[(step // action_interval) % len(greens)]
    scored = [
        (phase_score(controller, phase_idx, states, tls_movements.get(tls_id, []), queues, capacities, seed), -phase_idx, phase_idx)
        for phase_idx in greens
    ]
    return max(scored)[2] if scored else current_phase
```

**Copy/adapt:** retain deterministic tie-breaking by tuple `(score, -phase_idx, phase_idx)`. For audit, either:

1. keep this function returning `int` for backward compatibility and add a sibling `choose_controller_action_with_audit(...) -> tuple[int, dict[str, Any]]`; or
2. add an optional `return_audit: bool = False` parameter that preserves old call sites.

Do not break existing tests that expect `choose_controller_action(...)` to return an integer.

#### Metric row / objective component pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 230-277

```python
def aggregate_metrics(
    observations: list[dict[str, float]],
    steps: int,
    warmup: int,
    departed: dict[str, float],
    arrived_times: list[float],
    waiting_delay: float,
    runtime: float,
    switching_count: int,
) -> dict[str, Any]:
    ...
    metrics["objective_components"] = build_objective_components_from_metrics(
        {
            "total_delay": metrics["total_delay"],
            "unfinished_vehicle_count": metrics["unfinished_vehicle_count"],
            "spillback_count": spillback_count,
            "blocking_count": blocking_count,
            "switching_count": switching_count,
        },
        horizon=float(horizon),
    )
    return metrics
```

**Copy/adapt:** keep `objective_components` generated via `build_objective_components_from_metrics()`. The new score decomposition should be a separate row field, not mixed into objective components.

#### Completed / not-feasible finite-storage state pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 280-313

```python
def unavailable_finite_storage_state(reason: str) -> dict[str, Any]:
    state = {
        "downstream_storage": {"unavailable": 0.0},
        "residual_receiving_capacity": {"unavailable": 0.0},
        "spillback_blocking": {
            "unavailable": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0}
        },
        "switching_loss_state": {"current_phase": None, "time_since_switch": 0.0, "status_reason": reason},
        "service_urgency": {"unavailable": 0.0},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0, "status_reason": reason},
    }
    validate_finite_storage_state(state)
    return state
```

```python
def build_completed_finite_storage_state(
    queues: dict[str, float],
    capacities: dict[str, float],
    *,
    current_phase: int | None,
    time_since_switch: float,
    incident_edge: str | None = None,
    capacity_drop_factor: float | None = None,
) -> dict[str, Any]:
    state = build_finite_storage_state(
        queues,
        capacities,
        current_phase=current_phase,
        time_since_switch=time_since_switch,
        incident_edge=incident_edge,
        capacity_drop_factor=capacity_drop_factor,
    )
    validate_finite_storage_state(state)
    return state
```

**Copy/adapt:** new live controller should score against the same state contract. Build state once per decision or row using current `queues`, `capacities`, `current_phase`, `time_since_switch`, and failure-mode incident metadata.

#### Closed-loop row validation pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 316-319

```python
def validate_closed_loop_row(row: dict[str, Any]) -> None:
    validate_finite_storage_state(row["finite_storage_state"])
    validate_state_objective_sample(row)
```

**Copy/adapt:** extend validation only if needed to check optional `score_decomposition` shape for `finite_storage_primal_dual` rows. Do not relax existing schema checks.

#### Not-feasible row pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 321-356

```python
def infeasible_row(
    network: str,
    controller: str,
    seed: int,
    steps: int,
    warmup: int,
    action_interval: int,
    route_metadata: dict[str, str],
    scenario_tag: str,
    reason: str,
) -> dict[str, Any]:
    row = {
        "network": network,
        "scenario_tag": scenario_tag,
        "controller": controller,
        "seed": int(seed),
        "steps": int(steps),
        "warmup": int(warmup),
        "action_interval": int(action_interval),
        "scenario_status": "not_feasible",
        "feasibility_status": "not_feasible",
        "unsupported_reason": reason,
        **route_metadata,
        **{field: 0.0 for field in METRIC_FIELDS},
        "completed_vehicles": 0,
        "completion_rate": 0.0,
        "spillback_count": 0,
        "blocking_count": 0,
        "switching_count": 0,
        "travel_time_source": "not_feasible",
        "unfinished_vehicle_count": 0,
        "objective_components": {field: 0.0 for field in OBJECTIVE_COMPONENT_FIELDS},
        "finite_storage_state": unavailable_finite_storage_state(reason),
    }
    validate_closed_loop_row(row)
    return row
```

**Copy/adapt:** preserve honest not-feasible rows for `full_dual_symbolic`. Do not attach a fake successful `score_decomposition` to not-feasible old controllers. If adding decomposition to infeasible rows, mark it unavailable explicitly; safer default is no decomposition on not-feasible rows.

#### Runtime action loop / row construction pattern

**Source:** `scripts/run_closed_loop_sumo.py` lines 412-550

Key places to copy:

```python
if controller in NOT_FEASIBLE_CONTROLLERS:
    return infeasible_row(network, controller, seed, steps, warmup, action_interval, route_metadata, scenario_tag, NOT_FEASIBLE_CONTROLLERS[controller])
```

```python
action = choose_controller_action(controller, tls_id, current_phase, step, action_interval, phase_states, tls_movements, queues, capacities, seed)
```

```python
"finite_storage_state": build_completed_finite_storage_state(
    latest_queues,
    capacities,
    current_phase=latest_current_phase,
    time_since_switch=latest_time_since_switch,
    incident_edge=target_edge if failure_mode_mechanism else None,
    capacity_drop_factor=0.35 if failure_mode_mechanism else None,
),
```

**Copy/adapt:**

- keep the not-feasible short circuit before SUMO startup;
- capture the latest decision audit during the action loop only for `finite_storage_primal_dual`;
- add row-level `score_decomposition` or `action_decomposition` after metrics aggregation;
- call `validate_closed_loop_row(row)` after adding the audit field.

### `tests/test_closed_loop_sumo.py` (test, pure function + schema validation)

**Primary analog:** existing `tests/test_closed_loop_sumo.py`  
**Secondary analog:** `tests/test_theory_separation.py` for Phase 7 slack/binding proof structure.

#### Test import pattern

**Source:** `tests/test_closed_loop_sumo.py` lines 1-37

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from finite_storage_schema import (  # noqa: E402
    FINITE_STORAGE_STATE_FIELDS,
    OBJECTIVE_COMPONENT_FIELDS,
    validate_finite_storage_state,
    validate_state_objective_sample,
)
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    aggregate_metrics,
    apply_failure_mode,
    build_completed_finite_storage_state,
    choose_controller_action,
    load_route_metadata,
    resolve_network,
    run_experiment,
)
```

**Copy/adapt:** import any new pure helpers from `run_closed_loop_sumo`, e.g. `finite_storage_movement_decomposition`, `finite_storage_phase_decomposition`, `choose_controller_action_with_audit`, and `NOT_FEASIBLE_CONTROLLERS` if testing the guard directly.

#### Registry smoke test pattern

**Source:** `tests/test_closed_loop_sumo.py` lines 40-53

```python
def test_controller_registry_smoke_names() -> None:
    expected = {
        "fixed_time",
        "actuated_local_pressure",
        "max_pressure",
        "capacity_aware_pressure",
        "local_pilight",
        "raw_neighbor_symbolic",
        "all_neighbor_symbolic",
        "random_permuted_dual",
        "full_dual_symbolic",
    }
    assert expected <= set(CONTROLLER_REGISTRY)
```

**Copy/adapt:** extend `expected` with `finite_storage_primal_dual`. Add a separate assertion that `full_dual_symbolic` is still not feasible unless explicitly aliased, and `finite_storage_primal_dual` is not in `NOT_FEASIBLE_CONTROLLERS`.

#### Action selection fixture pattern

**Source:** `tests/test_closed_loop_sumo.py` lines 55-73

```python
def test_choose_controller_action_prefers_pressure_phase() -> None:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("in_a", "out_a"), ("in_b", "out_b")]}
    queues = {"in_a": 1.0, "out_a": 0.0, "in_b": 10.0, "out_b": 0.0}
    capacities = {"out_a": 20.0, "out_b": 20.0}

    action = choose_controller_action(
        "max_pressure",
        "J0",
        current_phase=0,
        step=20,
        action_interval=10,
        phase_states=phase_states,
        tls_movements=movements,
        queues=queues,
        capacities=capacities,
    )

    assert action == 1
```

**Copy/adapt:** create analogous deterministic fixtures for:

- slack recovery: `finite_storage_primal_dual` action equals or ties `max_pressure`;
- binding separation: pressure-preferred phase uses blocked downstream edge, finite-storage action switches to the nonblocked phase;
- audit keys: selected action, pressure action, finite-storage action, phase scores, component totals.

#### Capacity-aware binding pattern

**Source:** `tests/test_closed_loop_sumo.py` lines 76-95

```python
def test_capacity_aware_penalizes_full_downstream() -> None:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("in_a", "out_a"), ("in_b", "out_b")]}
    queues = {"in_a": 10.0, "out_a": 10.0, "in_b": 8.0, "out_b": 0.0}
    capacities = {"out_a": 10.0, "out_b": 20.0}

    action = choose_controller_action(
        "capacity_aware_pressure",
        "J0",
        current_phase=0,
        step=20,
        action_interval=10,
        phase_states=phase_states,
        tls_movements=movements,
        queues=queues,
        capacities=capacities,
    )

    assert action == 1
```

**Copy/adapt:** use this exact two-phase shape for the Phase 8 binding fixture, but assert via finite-storage decomposition fields instead of only scalar action.

#### Metric aggregation schema pattern

**Source:** `tests/test_closed_loop_sumo.py` lines 97-140

```python
def test_metric_aggregation_schema() -> None:
    metrics = aggregate_metrics(
        observations=[
            {"total_queue": 2.0, "max_queue": 2.0, "active_vehicles": 4.0, "spillback": 0.0, "blocking": 0.0},
            {"total_queue": 4.0, "max_queue": 3.0, "active_vehicles": 5.0, "spillback": 1.0, "blocking": 1.0},
        ],
        steps=10,
        warmup=2,
        departed={"veh3": 2.0},
        arrived_times=[4.0, 6.0],
        waiting_delay=7.0,
        runtime=0.25,
        switching_count=3,
    )
    ...
    assert set(metrics["objective_components"]) == OBJECTIVE_COMPONENT_FIELDS
    assert metrics["objective_components"]["delay"] == 7.0
    assert metrics["objective_components"]["unfinished_vehicle_penalty"] == 8.0
    assert metrics["objective_components"]["spillback_blocking_time"] == 16.0
    assert metrics["objective_components"]["switching_lost_time"] == 6.0
```

**Copy/adapt:** add row-audit tests without changing this metric contract. Objective components remain aggregate performance components; score decomposition remains decision-audit data.

#### State schema validation pattern

**Source:** `tests/test_closed_loop_sumo.py` lines 143-157

```python
def test_completed_finite_storage_state_schema() -> None:
    state = build_completed_finite_storage_state(
        queues={"edge_a": 2.0, "edge_b": 9.0},
        capacities={"edge_a": 10.0, "edge_b": 10.0},
        current_phase=1,
        time_since_switch=5.0,
        incident_edge="edge_b",
        capacity_drop_factor=0.35,
    )

    assert set(state) == FINITE_STORAGE_STATE_FIELDS
    validate_finite_storage_state(state, path=Path("row.json"), sample_idx=0)
    row = {"finite_storage_state": state, "objective_components": {field: 0.0 for field in OBJECTIVE_COMPONENT_FIELDS}}
    validate_state_objective_sample(row, path=Path("row.json"), sample_idx=0)
```

**Copy/adapt:** tests for decomposition should build state with `build_completed_finite_storage_state()` rather than hand-rolling incompatible field names.

#### Not-feasible guard test pattern

**Source:** `tests/test_closed_loop_sumo.py` lines 159-177 and 207-222

```python
def test_not_feasible_controller_has_explicit_state_and_objective_components() -> None:
    row = run_experiment(
        network="single",
        controller="full_dual_symbolic",
        seed=1,
        steps=10,
        warmup=0,
        action_interval=5,
        route_metadata={"route_decision": "pressure-equivalent", "route_confidence": "MEDIUM", "route_json": "route.json"},
        scenario_tag="single_sanity",
    )

    assert row["feasibility_status"] == "not_feasible"
    assert set(row["finite_storage_state"]) == FINITE_STORAGE_STATE_FIELDS
    assert set(row["objective_components"]) == OBJECTIVE_COMPONENT_FIELDS
    assert all(value == 0.0 for value in row["objective_components"].values())
    assert "finite_storage_state_summary" not in row
    validate_finite_storage_state(row["finite_storage_state"], path=Path("row.json"), sample_idx=0)
    validate_state_objective_sample(row, path=Path("row.json"), sample_idx=0)
```

**Copy/adapt:** keep these tests green. Add test that `full_dual_symbolic` remains not-feasible and `finite_storage_primal_dual` is the safe live successor, not a relabel of the old guarded controller.

### `scripts/check_theory_separation.py` as secondary scoring analog

Use this file only for deterministic finite-storage scoring semantics, not for live SUMO plumbing.

#### Pressure / finite-storage score pattern

**Source:** `scripts/check_theory_separation.py` lines 22-35

```python
def pressure_score(movement: dict[str, str], queues: dict[str, float]) -> float:
    return float(queues[movement["upstream"]] - queues[movement["downstream"]])


def finite_storage_score(movement: dict[str, str], queues: dict[str, float], state: dict[str, Any]) -> float:
    downstream = movement["downstream"]
    score = pressure_score(movement, queues)
    flags = state["spillback_blocking"].get(downstream, {})
    if isinstance(flags, dict) and flags.get("blocking"):
        score -= 10.0
    incident = state["incident_capacity_drop"]
    if incident["active"] and incident["edge"] == downstream:
        score -= 5.0 * (1.0 - float(incident["factor"]))
    return float(score)
```

**Copy/adapt:** Phase 8 live helper should expand this from scalar to decomposition. Preserve sign convention: `pressure = upstream queue - downstream queue`; storage/spillback/incident corrections penalize constrained downstream destinations.

#### Tie-set action selection pattern

**Source:** `scripts/check_theory_separation.py` lines 38-41

```python
def select_action(scores: dict[str, float]) -> tuple[str, list[str]]:
    best = max(scores.values())
    tie_set = sorted(action for action, score in scores.items() if score == best)
    return tie_set[0], tie_set
```

**Copy/adapt:** for row audit, record tie sets or deterministic tie policy when possible. In `run_closed_loop_sumo.py`, numeric phase tie-breaking already uses lower phase index via `(score, -phase_idx, phase_idx)`.

#### Slack fixture pattern

**Source:** `scripts/check_theory_separation.py` lines 53-104

```python
def build_slack_example(weights: dict[str, float]) -> dict[str, Any]:
    queues = {"up_a": 20.0, "down_a": 5.0, "up_b": 14.0, "down_b": 4.0}
    movements = {
        "phase_a": {"upstream": "up_a", "downstream": "down_a"},
        "phase_b": {"upstream": "up_b", "downstream": "down_b"},
    }
    state = {
        "downstream_storage": {"up_a": 40.0, "down_a": 40.0, "up_b": 40.0, "down_b": 40.0},
        "residual_receiving_capacity": {"up_a": 20.0, "down_a": 35.0, "up_b": 26.0, "down_b": 36.0},
        "spillback_blocking": {
            edge: {"spillback": False, "blocking": False, "occupancy_ratio": queues[edge] / 40.0}
            for edge in queues
        },
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 30.0},
        "service_urgency": {edge: queues[edge] / 40.0 for edge in queues},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
```

**Copy/adapt:** Phase 8 tests can use the same values translated to TLS phases `{"J0": ["Gr", "rG"]}` and movements list. Expected result: finite-storage action matches pressure or pressure is in finite-storage tie set.

#### Binding fixture pattern

**Source:** `scripts/check_theory_separation.py` lines 107-182

```python
def build_binding_example(weights: dict[str, float]) -> dict[str, Any]:
    queues = {"up_a": 30.0, "down_a": 10.0, "up_b": 15.0, "down_b": 2.0}
    movements = {
        "phase_a": {"upstream": "up_a", "downstream": "down_a"},
        "phase_b": {"upstream": "up_b", "downstream": "down_b"},
    }
    state = {
        "downstream_storage": {"up_a": 50.0, "down_a": 10.0, "up_b": 50.0, "down_b": 10.0},
        "residual_receiving_capacity": {"up_a": 20.0, "down_a": 0.0, "up_b": 35.0, "down_b": 8.0},
        "spillback_blocking": {
            "up_a": {"spillback": False, "blocking": False, "occupancy_ratio": 0.6},
            "down_a": {"spillback": True, "blocking": True, "occupancy_ratio": 1.0},
            "up_b": {"spillback": False, "blocking": False, "occupancy_ratio": 0.3},
            "down_b": {"spillback": False, "blocking": False, "occupancy_ratio": 0.2},
        },
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 30.0},
        "service_urgency": {"up_a": 0.6, "down_a": 1.0, "up_b": 0.3, "down_b": 0.2},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
```

**Copy/adapt:** use this as the canonical Phase 8 binding test. The audit should show that `phase_a` wins under pressure but loses under finite-storage because `downstream_storage` / `spillback` corrections bind.

## Shared Patterns to Reuse

### 1. Registry / controller naming

**Source:** `scripts/run_closed_loop_sumo.py` lines 37-47, 62-65.  
**Apply to:** `scripts/run_closed_loop_sumo.py`, `tests/test_closed_loop_sumo.py`.

Rules:

- Add `finite_storage_primal_dual` to `CONTROLLER_REGISTRY`.
- Do not remove `full_dual_symbolic` from `NOT_FEASIBLE_CONTROLLERS` in Phase 8.
- Add test coverage that the new controller is selectable and old `full_dual_symbolic` remains explicitly not feasible.

### 2. Action selection / phase scoring

**Source:** `scripts/run_closed_loop_sumo.py` lines 154-227.  
**Apply to:** finite-storage helper and action selection tests.

Rules:

- Keep `green_phases()` behavior: use phases with `Gg`; fallback to all phases if no green phase exists.
- Keep deterministic tie-breaking compatible with `(score, -phase_idx, phase_idx)`.
- Preserve existing return type of `choose_controller_action()` unless an optional audit mode is backward-compatible.

### 3. Metric row and schema validation

**Source:** `scripts/run_closed_loop_sumo.py` lines 230-319; `scripts/finite_storage_schema.py` lines 9-23, 82-167, 170-216, 226-255.  
**Apply to:** completed rows, not-feasible rows, finite-storage audit tests.

Required state fields:

```python
FINITE_STORAGE_STATE_FIELDS = {
    "downstream_storage",
    "residual_receiving_capacity",
    "spillback_blocking",
    "switching_loss_state",
    "service_urgency",
    "incident_capacity_drop",
}
OBJECTIVE_COMPONENT_FIELDS = {
    "delay",
    "unfinished_vehicle_penalty",
    "spillback_blocking_time",
    "switching_lost_time",
}
```

Rules:

- `objective_components` must remain the Phase 6 aggregate objective contract.
- Use `build_finite_storage_state()` / `build_completed_finite_storage_state()` for row state.
- Use `validate_state_objective_sample(row)` for completed and not-feasible rows.

### 4. Score decomposition fields

**Source:** Phase 8 context decisions D-08-02 and existing Phase 7 scoring in `scripts/check_theory_separation.py` lines 22-35.

Recommended movement-level decomposition keys:

```python
{
    "pressure": float,
    "downstream_storage": float,
    "spillback": float,
    "switching": float,
    "service": float,
    "incident": float,
    "total": float,
}
```

Rules:

- `total == pressure + downstream_storage + spillback + switching + service + incident` should be tested with exact arithmetic for deterministic fixtures or tolerance for live float values.
- Use negative values for penalties and positive values only for explicit service/urgency bonuses when intended.
- Preserve slack recovery: when residual capacity is positive, spillback/blocking false, no incident, switching neutral, and service neutral, non-pressure components should be zero or ranking-neutral.

### 5. Row audit field naming

**Recommended row field:** `score_decomposition`  
**Alternative acceptable field:** `action_decomposition` if planner chooses a stronger action-centric name.

Recommended shape:

```python
"score_decomposition": {
    "controller": "finite_storage_primal_dual",
    "audit_scope": "last_decision_per_tls",
    "tls_decisions": {
        "J0": {
            "tls_id": "J0",
            "step": 120,
            "current_phase": 0,
            "selected_phase": 1,
            "pressure_action": 0,
            "finite_storage_action": 1,
            "pressure_phase_scores": {"0": 20.0, "1": 13.0},
            "finite_storage_phase_scores": {"0": 10.0, "1": 13.0},
            "phase_component_totals": {
                "0": {"pressure": 20.0, "downstream_storage": 0.0, "spillback": -10.0, "switching": 0.0, "service": 0.0, "incident": 0.0, "total": 10.0},
                "1": {"pressure": 13.0, "downstream_storage": 0.0, "spillback": 0.0, "switching": 0.0, "service": 0.0, "incident": 0.0, "total": 13.0}
            },
            "selected_component_totals": {"pressure": 13.0, "downstream_storage": 0.0, "spillback": 0.0, "switching": 0.0, "service": 0.0, "incident": 0.0, "total": 13.0},
            "changed_action_relative_to_pressure": true,
            "changing_terms": ["spillback"]
        }
    }
}
```

Field naming recommendations:

- Use `pressure_action`, `finite_storage_action`, `selected_phase`, not ambiguous `old_action` / `new_action`.
- Use `pressure_phase_scores` and `finite_storage_phase_scores` for scalar comparisons.
- Use `phase_component_totals` for additive decomposition by phase.
- Use `selected_component_totals` for the selected phase’s components.
- Use `changed_action_relative_to_pressure` and `changing_terms` for auditability.
- Store phase keys as strings in JSON-facing dictionaries if the row is serialized; tests may compare using `str(phase_idx)`.

### 6. Test patterns

**Sources:** `tests/test_closed_loop_sumo.py` lines 40-177; `tests/test_theory_separation.py` lines 60-108, 111-132, 179-190.

Recommended Phase 8 tests:

1. `test_controller_registry_includes_finite_storage_primal_dual` — new controller registered, old `full_dual_symbolic` remains guarded.
2. `test_finite_storage_decomposition_keys_and_total` — component keys exactly match recommended set and sum to `total`.
3. `test_finite_storage_slack_recovers_pressure_action_or_tie` — deterministic slack fixture.
4. `test_finite_storage_binding_separates_from_pressure_action` — Phase 7 binding values or direct equivalent.
5. `test_choose_controller_action_selects_finite_storage_primal_dual` — new controller works through action selection and returns expected phase.
6. `test_finite_storage_action_audit_identifies_changing_terms` — `changing_terms` includes `spillback` or `downstream_storage` in binding fixture.
7. `test_closed_loop_row_includes_score_decomposition_for_new_controller` — if a cheap live run is not used, unit-test row assembly helper or a synthetic row; always validate `finite_storage_state` and `objective_components`.
8. `test_full_dual_symbolic_remains_not_feasible_until_safe_alias` — preserves safety boundary.

## Patterns Not to Reuse

### Unsafe `full_dual_symbolic` not-feasible path as proposed method

**Do not copy as implementation shortcut:** `scripts/run_closed_loop_sumo.py` lines 62-65 and 422-423 currently short-circuit `full_dual_symbolic` as not feasible.

Reason:

- Phase 8 requires a safe live finite-storage successor, not relabeling the old unsafe per-TLS dual Scenario conversion.
- The new path must expose score decomposition and schema-valid state/objective rows.
- `full_dual_symbolic` should remain unavailable unless a later explicit alias decision is tested.

### Do not hide finite-storage logic inside `capacity_aware_pressure`

**Source to avoid overusing:** `movement_score()` capacity-aware branch lines 175-180.

Reason:

- It is a scalar heuristic: `pressure + 0.05 * slack - fullness * up_q - blocked_penalty`.
- Phase 8 requires explicit components: `downstream_storage`, `spillback`, `switching`, `service`, `incident`.
- Tests must prove the new method is not merely the old queue heuristic under a new label.

### Do not create parallel schema names

Avoid new row fields such as:

- `finite_storage_state_summary`
- `storage_state`
- `objective_terms`
- `dual_components`

Use the established row fields `finite_storage_state`, `objective_components`, and one audit field `score_decomposition` / `action_decomposition`.

## Risks and Verification Hooks

| Risk | Pattern-based mitigation | Verification hook |
|---|---|---|
| `finite_storage_primal_dual` accidentally blocked as not feasible | Add to `CONTROLLER_REGISTRY`, do not add to `NOT_FEASIBLE_CONTROLLERS`. | Unit test registry membership and not-feasible exclusion. |
| Unsafe `full_dual_symbolic` relabeled as proposed method | Preserve old not-feasible guard; implement new explicit controller name. | `run_experiment(..., controller="full_dual_symbolic")` still returns `feasibility_status == "not_feasible"`. |
| Score decomposition total inconsistent with selected scalar | Compute scalar from decomposition `total`. | Unit test component sum equals `total` and chosen phase matches max of `finite_storage_phase_scores`. |
| Slack fixture breaks max-pressure equivalence | Keep non-pressure components zero/ranking-neutral under slack state. | Deterministic test: finite-storage action equals max-pressure action or includes it in tie set. |
| Binding fixture does not separate | Use Phase 7 `storage_binding_two_phase_separation` values and sufficiently large storage/spillback penalty. | Deterministic test: `pressure_action != finite_storage_action`; `changing_terms` includes `spillback` / `downstream_storage`. |
| Row audit grows too large | Store last decision per TLS, not every step. | Assert `score_decomposition["audit_scope"] == "last_decision_per_tls"`. |
| Schema drift in completed/not-feasible rows | Reuse Phase 6 validators. | `validate_state_objective_sample(row)` in tests; existing `test_not_feasible_controller_has_explicit_state_and_objective_components` remains green. |
| Existing action-selection tests break due return-type change | Preserve `choose_controller_action()` returning `int`; add sibling/optional audit function. | Existing tests `test_choose_controller_action_prefers_pressure_phase` and `test_capacity_aware_penalizes_full_downstream` pass unchanged. |
| Closed-loop dominance claim creep | Keep row/payload language auditability-only. | Avoid forbidden unbounded phrases; optional run of claim audit if artifacts mention claims. |

## Recommended Verification Commands

```bash
python3 -m pytest tests/test_closed_loop_sumo.py -q
python3 -m pytest tests/test_theory_separation.py tests/test_closed_loop_sumo.py -q
python3 scripts/run_closed_loop_sumo.py --network single --controllers finite_storage_primal_dual --seeds 20260523 --steps 30 --warmup 0 --action-interval 10 --out experiments/dual_sensitivity/phase8_finite_storage_smoke.json
```

The first two are pure/local tests except existing imports. The SUMO smoke command is optional for planning but useful once implementation is complete.

## No Analog Found

None. The Phase 8 changes are in-place extensions of existing closed-loop SUMO and theory-separation patterns.

## Metadata

**Analog search scope:** `scripts/run_closed_loop_sumo.py`, `tests/test_closed_loop_sumo.py`, `scripts/finite_storage_schema.py`, `scripts/check_theory_separation.py`, `tests/test_theory_separation.py`, Phase 7 pattern artifact, project `CLAUDE.md`.  
**Files scanned/read:** 8 required/project files plus phase context.  
**Project skills:** `.claude/skills/` and `.agents/skills/` absent in project root.  
**Pattern extraction date:** 2026-05-24
