#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r113_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_decomposition,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r113_reactivated_dual_no_positive_pressure_multi_big_finishable_power_horizon_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_no_positive_pressure_multi_big_finishable_power"] == 0.25


def test_r113_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r113_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r113_only_adds_extra_concavity_when_multiple_big_finishable_movements_coexist() -> None:
    states = ["GGG"]
    movements = [("A", "B"), ("C", "D"), ("E", "F")]
    capacities = {"B": 10.0, "D": 10.0, "F": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"B": 8.0, "D": 8.0, "F": 8.0},
        "downstream_storage": {"B": 10.0, "D": 10.0, "F": 10.0},
    }
    route_completion_state = {
        "finishable_movement_demand": {"A->B": 4.0, "C->D": 1.0, "E->F": 3.0},
        "movement_demand": {"A->B": 4.0, "C->D": 1.0, "E->F": 3.0},
        "movement_remaining_time_sum": {"A->B": 40.0, "C->D": 10.0, "E->F": 30.0},
        "remaining_edge_demand": {"B": 12.0, "D": 12.0, "F": 12.0},
        "remaining_time": 120.0,
    }

    r112_like = phase_route_horizon_completion_decomposition(
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
            "route_horizon_conditional_movement_finishable_power": 0.35,
            "route_horizon_conditional_movement_finishable_power_max_local_pressure_ceiling": 0.0,
            "route_horizon_conditional_movement_finishable_power_phase_downstream_pressure_floor": 1.0,
            "route_horizon_conditional_movement_finishable_power_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_count_power": 0.5,
            "route_horizon_no_positive_pressure_big_finishable_count_max_local_pressure_ceiling": 0.0,
            "route_horizon_no_positive_pressure_big_finishable_count_phase_downstream_pressure_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_count_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_count_min_count": 2.0,
        },
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0},
    )
    r113 = phase_route_horizon_completion_decomposition(
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
            "route_horizon_conditional_movement_finishable_power": 0.35,
            "route_horizon_conditional_movement_finishable_power_max_local_pressure_ceiling": 0.0,
            "route_horizon_conditional_movement_finishable_power_phase_downstream_pressure_floor": 1.0,
            "route_horizon_conditional_movement_finishable_power_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_count_power": 0.5,
            "route_horizon_no_positive_pressure_big_finishable_count_max_local_pressure_ceiling": 0.0,
            "route_horizon_no_positive_pressure_big_finishable_count_phase_downstream_pressure_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_count_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_count_min_count": 2.0,
            "route_horizon_no_positive_pressure_multi_big_finishable_power": 0.25,
            "route_horizon_no_positive_pressure_multi_big_finishable_power_max_local_pressure_ceiling": 0.0,
            "route_horizon_no_positive_pressure_multi_big_finishable_power_phase_downstream_pressure_floor": 1.0,
            "route_horizon_no_positive_pressure_multi_big_finishable_power_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_multi_big_finishable_power_min_count": 2.0,
        },
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0},
    )

    r112_details = {detail["movement"]: detail for detail in r112_like["movement_details"]}
    r113_details = {detail["movement"]: detail for detail in r113["movement_details"]}

    assert math.isclose(r112_details["C->D"]["effective_finishable_power"], 0.5, rel_tol=1e-9)
    assert math.isclose(r113_details["C->D"]["effective_finishable_power"], 0.5, rel_tol=1e-9)
    assert math.isclose(r113_details["A->B"]["effective_finishable_power"], 0.25, rel_tol=1e-9)
    assert math.isclose(r113_details["E->F"]["effective_finishable_power"], 0.25, rel_tol=1e-9)
    assert r113_details["A->B"]["finishable_term"] < r112_details["A->B"]["finishable_term"]
    assert r113_details["E->F"]["finishable_term"] < r112_details["E->F"]["finishable_term"]


def test_r113_skips_extra_concavity_when_only_one_big_finishable_movement_exists() -> None:
    states = ["GGG"]
    movements = [("A", "B"), ("C", "D"), ("E", "F")]
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
            "route_horizon_conditional_movement_finishable_power": 0.35,
            "route_horizon_conditional_movement_finishable_power_max_local_pressure_ceiling": 0.0,
            "route_horizon_conditional_movement_finishable_power_phase_downstream_pressure_floor": 1.0,
            "route_horizon_conditional_movement_finishable_power_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_count_power": 0.5,
            "route_horizon_no_positive_pressure_big_finishable_count_max_local_pressure_ceiling": 0.0,
            "route_horizon_no_positive_pressure_big_finishable_count_phase_downstream_pressure_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_count_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_count_min_count": 2.0,
            "route_horizon_no_positive_pressure_multi_big_finishable_power": 0.25,
            "route_horizon_no_positive_pressure_multi_big_finishable_power_max_local_pressure_ceiling": 0.0,
            "route_horizon_no_positive_pressure_multi_big_finishable_power_phase_downstream_pressure_floor": 1.0,
            "route_horizon_no_positive_pressure_multi_big_finishable_power_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_multi_big_finishable_power_min_count": 2.0,
        },
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0},
    )

    details = {detail["movement"]: detail for detail in result["movement_details"]}
    assert math.isclose(details["A->B"]["effective_finishable_power"], 0.35, rel_tol=1e-9)
    assert math.isclose(details["C->D"]["effective_finishable_power"], 0.5, rel_tol=1e-9)
    assert math.isclose(details["E->F"]["effective_finishable_power"], 0.5, rel_tol=1e-9)
