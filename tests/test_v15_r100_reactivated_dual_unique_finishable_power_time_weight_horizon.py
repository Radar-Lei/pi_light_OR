#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r100_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_decomposition,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r100_reactivated_dual_unique_finishable_power_time_weight_horizon_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_finishable_power"] == 0.5
    assert protocol["controller_params"]["route_horizon_time_weight_power"] == 2.0


def test_r100_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r100_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_route_horizon_time_weight_power_sharpens_slow_completion_penalty() -> None:
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
        "finishable_movement_demand": {"A->B": 4.0, "C->D": 4.0},
        "movement_demand": {"A->B": 4.0, "C->D": 4.0},
        "movement_remaining_time_sum": {"A->B": 40.0, "C->D": 160.0},
        "remaining_edge_demand": {"B": 0.0, "D": 0.0},
        "remaining_time": 120.0,
    }

    base = phase_route_horizon_completion_decomposition(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        {
            "route_horizon_time_discount": 1.0,
            "route_horizon_unique_movement_terms": 1.0,
            "route_horizon_finishable_power": 0.5,
        },
        queues={"A": 1.0, "B": 0.0, "C": 1.0, "D": 0.0},
    )
    sharpened = phase_route_horizon_completion_decomposition(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        {
            "route_horizon_time_discount": 1.0,
            "route_horizon_unique_movement_terms": 1.0,
            "route_horizon_finishable_power": 0.5,
            "route_horizon_time_weight_power": 2.0,
        },
        queues={"A": 1.0, "B": 0.0, "C": 1.0, "D": 0.0},
    )

    base_details = {detail["movement"]: detail for detail in base["movement_details"]}
    sharp_details = {detail["movement"]: detail for detail in sharpened["movement_details"]}

    assert base_details["A->B"]["time_weight"] > base_details["C->D"]["time_weight"]
    assert sharp_details["A->B"]["effective_time_weight"] > sharp_details["C->D"]["effective_time_weight"]
    assert sharp_details["C->D"]["finishable_term"] < base_details["C->D"]["finishable_term"]
