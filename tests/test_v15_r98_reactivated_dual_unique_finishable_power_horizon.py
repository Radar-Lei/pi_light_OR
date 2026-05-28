#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r98_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_decomposition,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r98_reactivated_dual_unique_finishable_power_horizon_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_unique_movement_terms"] == 1.0
    assert protocol["controller_params"]["route_horizon_finishable_power"] == 0.5


def test_r98_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r98_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_route_horizon_finishable_power_dampens_large_finishable_volume() -> None:
    states = ["GG"]
    movements = [
        ("A", "B"),
        ("C", "D"),
    ]
    capacities = {"B": 10.0, "D": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"B": 8.0, "D": 8.0},
        "downstream_storage": {"B": 10.0, "D": 10.0},
    }
    route_completion_state = {
        "finishable_movement_demand": {"A->B": 4.0, "C->D": 1.0},
        "movement_demand": {"A->B": 4.0, "C->D": 1.0},
        "movement_remaining_time_sum": {"A->B": 40.0, "C->D": 10.0},
        "remaining_edge_demand": {"B": 0.0, "D": 0.0},
        "remaining_time": 120.0,
    }

    linear = phase_route_horizon_completion_decomposition(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        {"route_horizon_time_discount": 0.0, "route_horizon_unique_movement_terms": 1.0},
        queues={"A": 1.0, "B": 0.0, "C": 1.0, "D": 0.0},
    )
    damped = phase_route_horizon_completion_decomposition(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        {
            "route_horizon_time_discount": 0.0,
            "route_horizon_unique_movement_terms": 1.0,
            "route_horizon_finishable_power": 0.5,
        },
        queues={"A": 1.0, "B": 0.0, "C": 1.0, "D": 0.0},
    )

    linear_details = {detail["movement"]: detail for detail in linear["movement_details"]}
    damped_details = {detail["movement"]: detail for detail in damped["movement_details"]}

    assert linear_details["A->B"]["finishable_term"] == 3.2
    assert linear_details["C->D"]["finishable_term"] == 0.8
    assert damped_details["A->B"]["effective_finishable_demand"] == 2.0
    assert damped_details["A->B"]["finishable_term"] == 1.6
    assert damped_details["C->D"]["finishable_term"] == 0.8
