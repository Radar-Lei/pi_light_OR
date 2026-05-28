#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r110_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_decomposition,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r110_reactivated_dual_high_finishable_count_horizon_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_no_positive_pressure_finishable_count_power"] == 0.5
    assert protocol["controller_params"]["route_horizon_no_positive_pressure_finishable_count_min_count"] == 4.0


def test_r110_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r110_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r110_normalizes_only_high_finishable_count_supported_phase() -> None:
    states = ["GGGG"]
    movements = [
        ("A", "B"),
        ("C", "D"),
        ("E", "F"),
        ("G", "H"),
    ]
    capacities = {"B": 10.0, "D": 10.0, "F": 10.0, "H": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"B": 8.0, "D": 8.0, "F": 8.0, "H": 8.0},
        "downstream_storage": {"B": 10.0, "D": 10.0, "F": 10.0, "H": 10.0},
    }
    route_completion_state = {
        "finishable_movement_demand": {"A->B": 4.0, "C->D": 1.0, "E->F": 1.0, "G->H": 1.0},
        "movement_demand": {"A->B": 4.0, "C->D": 1.0, "E->F": 1.0, "G->H": 1.0},
        "movement_remaining_time_sum": {"A->B": 40.0, "C->D": 10.0, "E->F": 10.0, "G->H": 10.0},
        "remaining_edge_demand": {"B": 12.0, "D": 12.0, "F": 12.0, "H": 12.0},
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
            "route_horizon_time_discount": 0.0,
            "route_horizon_unique_movement_terms": 1.0,
            "route_horizon_finishable_power": 0.5,
        },
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0},
    )
    normalized = phase_route_horizon_completion_decomposition(
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
            "route_horizon_no_positive_pressure_finishable_count_power": 0.5,
            "route_horizon_no_positive_pressure_finishable_count_max_local_pressure_ceiling": 0.0,
            "route_horizon_no_positive_pressure_finishable_count_phase_downstream_pressure_floor": 1.0,
            "route_horizon_no_positive_pressure_finishable_count_min_count": 4.0,
        },
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0, "G": 1.0, "H": 1.0},
    )

    base_details = {detail["movement"]: detail for detail in base["movement_details"]}
    normalized_details = {detail["movement"]: detail for detail in normalized["movement_details"]}

    assert base["components"]["finishable_term"] == 4.0
    assert math.isclose(
        normalized["components"]["finishable_term"],
        4.0 / 2.0,
        rel_tol=1e-9,
    )
    assert normalized_details["A->B"]["effective_finishable_count_scale"] == 2.0
    assert normalized_details["C->D"]["effective_finishable_count_scale"] == 2.0
    assert normalized_details["E->F"]["effective_finishable_count_scale"] == 2.0
    assert normalized_details["G->H"]["effective_finishable_count_scale"] == 2.0
    assert base_details["A->B"]["finishable_term"] > normalized_details["A->B"]["finishable_term"]


def test_r110_skips_count_normalization_below_min_count() -> None:
    states = ["GGG"]
    movements = [
        ("A", "B"),
        ("C", "D"),
        ("E", "F"),
    ]
    capacities = {"B": 10.0, "D": 10.0, "F": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"B": 8.0, "D": 8.0, "F": 8.0},
        "downstream_storage": {"B": 10.0, "D": 10.0, "F": 10.0},
    }
    route_completion_state = {
        "finishable_movement_demand": {"A->B": 4.0, "C->D": 1.0, "E->F": 1.0},
        "movement_demand": {"A->B": 4.0, "C->D": 1.0, "E->F": 1.0},
        "movement_remaining_time_sum": {"A->B": 40.0, "C->D": 10.0, "E->F": 10.0},
        "remaining_edge_demand": {"B": 12.0, "D": 12.0, "F": 12.0},
        "remaining_time": 120.0,
    }

    result = phase_route_horizon_completion_decomposition(
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
            "route_horizon_no_positive_pressure_finishable_count_power": 0.5,
            "route_horizon_no_positive_pressure_finishable_count_max_local_pressure_ceiling": 0.0,
            "route_horizon_no_positive_pressure_finishable_count_phase_downstream_pressure_floor": 1.0,
            "route_horizon_no_positive_pressure_finishable_count_min_count": 4.0,
        },
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0},
    )

    details = {detail["movement"]: detail for detail in result["movement_details"]}
    assert details["A->B"]["effective_finishable_count_scale"] == 1.0
    assert details["C->D"]["effective_finishable_count_scale"] == 1.0
    assert details["E->F"]["effective_finishable_count_scale"] == 1.0
