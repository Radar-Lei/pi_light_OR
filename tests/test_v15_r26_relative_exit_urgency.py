#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r26_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_score,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r26_relative_exit_urgency_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["route_horizon_relative_time_urgency"] == 1.0
    assert protocol["controller_params"]["route_horizon_urgency_power"] == 2.0


def test_r26_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r26_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_relative_exit_urgency_prefers_soon_finishable_movement() -> None:
    states = ["Gr", "rG"]
    movements = [("up_a", "down_a"), ("up_b", "down_b")]
    capacities = {"down_a": 10.0, "down_b": 10.0}
    finite_storage_state = {
        "downstream_storage": {"down_a": 10.0, "down_b": 10.0},
        "residual_receiving_capacity": {"down_a": 10.0, "down_b": 10.0},
    }
    route_completion_state = {
        "movement_demand": {"up_a->down_a": 10.0, "up_b->down_b": 10.0},
        "finishable_movement_demand": {"up_a->down_a": 10.0, "up_b->down_b": 10.0},
        "movement_remaining_time_sum": {"up_a->down_a": 500.0, "up_b->down_b": 100.0},
        "remaining_edge_demand": {"down_a": 0.0, "down_b": 0.0},
        "remaining_time": 60.0,
    }
    params = {
        "route_horizon_relative_time_urgency": 1.0,
        "route_horizon_urgency_power": 2.0,
    }

    late_exit_score = phase_route_horizon_completion_score(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        params,
    )
    soon_exit_score = phase_route_horizon_completion_score(
        1,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        params,
    )

    assert soon_exit_score > late_exit_score
