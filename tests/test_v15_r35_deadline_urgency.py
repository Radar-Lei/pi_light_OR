#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r35_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_score,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def deadline_inputs() -> tuple[
    dict[str, list[str]],
    dict[str, list[tuple[str, str]]],
    dict[str, float],
    dict[str, object],
]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_near", "down_near"), ("up_slack", "down_slack")]}
    capacities = {"down_near": 10.0, "down_slack": 10.0}
    state = {
        "downstream_storage": {"down_near": 10.0, "down_slack": 10.0},
        "residual_receiving_capacity": {"down_near": 10.0, "down_slack": 10.0},
        "spillback_blocking": {
            "down_near": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
            "down_slack": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
        },
    }
    route_completion_state = {
        "movement_demand": {"up_near->down_near": 1.0, "up_slack->down_slack": 1.0},
        "finishable_movement_demand": {"up_near->down_near": 1.0, "up_slack->down_slack": 1.0},
        "movement_remaining_time_sum": {"up_near->down_near": 95.0, "up_slack->down_slack": 10.0},
        "remaining_edge_demand": {"down_near": 0.0, "down_slack": 0.0},
        "active_vehicle_count": 2,
        "remaining_time": 100.0,
    }
    return phase_states, movements, capacities, state, route_completion_state


def test_r35_deadline_urgency_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["route_horizon_deadline_time_urgency"] == 1.0
    assert protocol["controller_params"]["route_horizon_deadline_base_weight"] == 0.05


def test_r35_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r35_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_deadline_urgency_prioritizes_low_slack_finishable_movement() -> None:
    phase_states, movements, capacities, state, route_completion_state = deadline_inputs()
    params = {
        "route_horizon_deadline_time_urgency": 1.0,
        "route_horizon_urgency_power": 2.0,
        "route_horizon_deadline_base_weight": 0.05,
    }

    near_score = phase_route_horizon_completion_score(
        0,
        phase_states["J0"],
        movements["J0"],
        capacities,
        state,
        route_completion_state,
        params,
    )
    slack_score = phase_route_horizon_completion_score(
        1,
        phase_states["J0"],
        movements["J0"],
        capacities,
        state,
        route_completion_state,
        params,
    )

    assert near_score > slack_score


def test_old_relative_urgency_keeps_historical_high_slack_semantics() -> None:
    phase_states, movements, capacities, state, route_completion_state = deadline_inputs()
    params = {
        "route_horizon_relative_time_urgency": 1.0,
        "route_horizon_urgency_power": 2.0,
    }

    near_score = phase_route_horizon_completion_score(
        0,
        phase_states["J0"],
        movements["J0"],
        capacities,
        state,
        route_completion_state,
        params,
    )
    slack_score = phase_route_horizon_completion_score(
        1,
        phase_states["J0"],
        movements["J0"],
        capacities,
        state,
        route_completion_state,
        params,
    )

    assert slack_score > near_score
