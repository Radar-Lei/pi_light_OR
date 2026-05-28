#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r24_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    select_finite_storage_action_with_audit,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def base_inputs() -> tuple[
    dict[str, list[str]],
    dict[str, list[tuple[str, str]]],
    dict[str, float],
    dict[str, float],
    dict[str, object],
    dict[str, dict[str, float]],
    dict[str, object],
]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 20.0, "down_a": 0.0, "up_b": 4.0, "down_b": 0.0}
    capacities = {edge: 10.0 for edge in queues}
    state = {
        "downstream_storage": {edge: 10.0 for edge in queues},
        "residual_receiving_capacity": {edge: 10.0 for edge in queues},
        "spillback_blocking": {
            edge: {"spillback": False, "blocking": False, "occupancy_ratio": 0.0}
            for edge in queues
        },
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 40.0},
        "service_urgency": {edge: 0.0 for edge in queues},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
    dual_state = {
        edge: {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0}
        for edge in queues
    }
    route_completion_state = {
        "movement_demand": {"up_a->down_a": 20.0, "up_b->down_b": 8.0},
        "finishable_movement_demand": {"up_b->down_b": 8.0},
        "movement_remaining_time_sum": {"up_a->down_a": 4000.0, "up_b->down_b": 80.0},
        "remaining_edge_demand": {"down_a": 20.0, "down_b": 8.0},
        "active_vehicle_count": 28,
        "remaining_time": 60.0,
    }
    return phase_states, movements, queues, capacities, state, dual_state, route_completion_state


def test_r24_staged_horizon_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["completion_risk_start_fraction"] == 0.55


def test_r24_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r24_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r24_horizon_filter_is_delayed_until_late_horizon() -> None:
    phase_states, movements, queues, capacities, state, dual_state, route_completion_state = base_inputs()

    early = select_finite_storage_action_with_audit(
        "J0",
        0,
        phase_states,
        movements,
        queues,
        capacities,
        state,
        controller=CONTROLLER_ID,
        dynamic_dual_state=dual_state,
        route_completion_state=route_completion_state,
        step=1200,
        warmup=900,
        steps=3600,
    )
    late = select_finite_storage_action_with_audit(
        "J0",
        0,
        phase_states,
        movements,
        queues,
        capacities,
        state,
        controller=CONTROLLER_ID,
        dynamic_dual_state=dual_state,
        route_completion_state=route_completion_state,
        step=3000,
        warmup=900,
        steps=3600,
    )

    assert early["route_horizon_completion_filter_used"] is False
    assert late["route_horizon_completion_filter_used"] is True
