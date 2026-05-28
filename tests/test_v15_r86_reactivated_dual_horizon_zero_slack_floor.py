#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r86_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_score,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r86_reactivated_dual_horizon_zero_slack_floor_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_zero_slack_floor_for_nonpositive_pressure"] == 1.0
    assert protocol["controller_params"]["route_horizon_zero_slack_floor_pressure_ceiling"] == 0.0


def test_r86_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r86_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r86_horizon_score_removes_slack_floor_credit_for_nonpositive_pressure() -> None:
    states = ["Gr", "rG"]
    movements = [("up_a", "down_a"), ("up_b", "down_b")]
    capacities = {"down_a": 10.0, "down_b": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"down_a": 0.0, "down_b": 0.0},
        "downstream_storage": {"down_a": 10.0, "down_b": 10.0},
        "spillback_blocking": {
            "down_a": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
            "down_b": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
        },
    }
    route_completion_state = {
        "finishable_movement_demand": {"up_a->down_a": 5.0, "up_b->down_b": 5.0},
        "movement_demand": {"up_a->down_a": 5.0, "up_b->down_b": 5.0},
        "movement_remaining_time_sum": {"up_a->down_a": 0.0, "up_b->down_b": 0.0},
        "remaining_edge_demand": {"down_a": 0.0, "down_b": 0.0},
        "remaining_time": 100.0,
    }
    params = {
        "route_horizon_slack_floor": 0.02,
        "route_horizon_zero_slack_floor_for_nonpositive_pressure": 1.0,
        "route_horizon_zero_slack_floor_pressure_ceiling": 0.0,
    }

    positive_pressure_score = phase_route_horizon_completion_score(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        params,
        queues={"up_a": 10.0, "down_a": 0.0, "up_b": 0.0, "down_b": 0.0},
    )
    nonpositive_pressure_score = phase_route_horizon_completion_score(
        1,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        params,
        queues={"up_a": 0.0, "down_a": 0.0, "up_b": 3.0, "down_b": 3.0},
    )

    assert positive_pressure_score > 0.0
    assert nonpositive_pressure_score == 0.0
