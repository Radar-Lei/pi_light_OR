#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r114_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_decomposition,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r114_controller_is_registered() -> None:
    protocol = build_training_protocol()
    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_no_positive_pressure_big_finishable_sum_floor"] == 12.0


def test_r114_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)
    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r114_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r114_only_normalizes_big_finishable_sum_when_phase_sum_crosses_floor() -> None:
    states = ["GGG"]
    movements = [("A", "B"), ("C", "D"), ("E", "F")]
    capacities = {"B": 10.0, "D": 10.0, "F": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"B": 3.0, "D": 3.0, "F": 3.0},
        "downstream_storage": {"B": 10.0, "D": 10.0, "F": 10.0},
    }
    route_completion_state = {
        "finishable_movement_demand": {"A->B": 5.0, "C->D": 4.0, "E->F": 4.0},
        "movement_demand": {"A->B": 5.0, "C->D": 4.0, "E->F": 4.0},
        "movement_remaining_time_sum": {"A->B": 50.0, "C->D": 40.0, "E->F": 40.0},
        "remaining_edge_demand": {"B": 12.0, "D": 12.0, "F": 12.0},
        "remaining_time": 120.0,
    }

    baseline = phase_route_horizon_completion_decomposition(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        {"route_horizon_time_discount": 0.0},
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0},
    )
    r114 = phase_route_horizon_completion_decomposition(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        {
            "route_horizon_time_discount": 0.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_power": 0.5,
            "route_horizon_no_positive_pressure_big_finishable_sum_floor": 12.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_max_local_pressure_ceiling": 0.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_phase_downstream_pressure_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_phase_residual_ceiling": 0.4,
        },
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0},
    )
    base_details = {d["movement"]: d for d in baseline["movement_details"]}
    details = {d["movement"]: d for d in r114["movement_details"]}
    expected_scale = math.sqrt((5.0 + 4.0 + 4.0) / 12.0)
    assert math.isclose(details["A->B"]["effective_big_finishable_sum_scale"], expected_scale, rel_tol=1e-9)
    assert math.isclose(details["C->D"]["effective_big_finishable_sum_scale"], expected_scale, rel_tol=1e-9)
    assert math.isclose(details["E->F"]["effective_big_finishable_sum_scale"], expected_scale, rel_tol=1e-9)
    assert details["A->B"]["finishable_term"] < base_details["A->B"]["finishable_term"]


def test_r114_skips_sum_normalization_below_floor() -> None:
    states = ["GGG"]
    movements = [("A", "B"), ("C", "D"), ("E", "F")]
    capacities = {"B": 10.0, "D": 10.0, "F": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"B": 3.0, "D": 3.0, "F": 3.0},
        "downstream_storage": {"B": 10.0, "D": 10.0, "F": 10.0},
    }
    route_completion_state = {
        "finishable_movement_demand": {"A->B": 4.0, "C->D": 4.0, "E->F": 3.0},
        "movement_demand": {"A->B": 4.0, "C->D": 4.0, "E->F": 3.0},
        "movement_remaining_time_sum": {"A->B": 40.0, "C->D": 40.0, "E->F": 30.0},
        "remaining_edge_demand": {"B": 12.0, "D": 12.0, "F": 12.0},
        "remaining_time": 120.0,
    }

    r114 = phase_route_horizon_completion_decomposition(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        {
            "route_horizon_time_discount": 0.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_power": 0.5,
            "route_horizon_no_positive_pressure_big_finishable_sum_floor": 12.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_max_local_pressure_ceiling": 0.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_phase_downstream_pressure_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_movement_finishable_floor": 1.0,
            "route_horizon_no_positive_pressure_big_finishable_sum_phase_residual_ceiling": 0.4,
        },
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0},
    )
    details = {d["movement"]: d for d in r114["movement_details"]}
    assert math.isclose(details["A->B"]["effective_big_finishable_sum_scale"], 1.0, rel_tol=1e-9)
    assert math.isclose(details["C->D"]["effective_big_finishable_sum_scale"], 1.0, rel_tol=1e-9)
    assert math.isclose(details["E->F"]["effective_big_finishable_sum_scale"], 1.0, rel_tol=1e-9)
