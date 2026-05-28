#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r106_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_decomposition,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r106_reactivated_dual_unique_finishable_power_secondary_time_weight_horizon_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_secondary_phase_time_weight_power"] == 1.5
    assert protocol["controller_params"]["route_horizon_secondary_phase_time_weight_movement_residual_ceiling"] == 0.4


def test_r106_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r106_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r106_secondary_time_weight_hits_moderate_residual_band_only() -> None:
    states = ["GGG"]
    movements = [
        ("A", "B"),
        ("C", "D"),
        ("E", "F"),
    ]
    capacities = {"B": 10.0, "D": 10.0, "F": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"B": 1.5, "D": 3.0, "F": 5.0},
        "downstream_storage": {"B": 10.0, "D": 10.0, "F": 10.0},
    }
    route_completion_state = {
        "finishable_movement_demand": {"A->B": 4.0, "C->D": 4.0, "E->F": 4.0},
        "movement_demand": {"A->B": 4.0, "C->D": 4.0, "E->F": 4.0},
        "movement_remaining_time_sum": {"A->B": 40.0, "C->D": 40.0, "E->F": 40.0},
        "remaining_edge_demand": {"B": 12.0, "D": 12.0, "F": 12.0},
        "remaining_time": 120.0,
    }
    params = {
        "route_horizon_time_discount": 1.0,
        "route_horizon_unique_movement_terms": 1.0,
        "route_horizon_finishable_power": 0.5,
        "route_horizon_conditional_phase_time_weight_power": 2.0,
        "route_horizon_conditional_phase_time_weight_max_local_pressure_ceiling": 0.0,
        "route_horizon_conditional_phase_time_weight_phase_residual_ceiling": 0.2,
        "route_horizon_conditional_phase_time_weight_local_pressure_ceiling": 0.0,
        "route_horizon_conditional_phase_time_weight_movement_residual_ceiling": 0.2,
        "route_horizon_conditional_phase_time_weight_movement_downstream_pressure_floor": 1.0,
        "route_horizon_secondary_phase_time_weight_power": 1.5,
        "route_horizon_secondary_phase_time_weight_max_local_pressure_ceiling": 0.0,
        "route_horizon_secondary_phase_time_weight_phase_residual_ceiling": 0.4,
        "route_horizon_secondary_phase_time_weight_local_pressure_ceiling": 0.0,
        "route_horizon_secondary_phase_time_weight_movement_residual_floor": 0.2,
        "route_horizon_secondary_phase_time_weight_movement_residual_ceiling": 0.4,
        "route_horizon_secondary_phase_time_weight_movement_downstream_pressure_floor": 1.0,
    }

    result = phase_route_horizon_completion_decomposition(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        params,
        queues={"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0, "E": 1.0, "F": 1.0},
    )

    details = {detail["movement"]: detail for detail in result["movement_details"]}

    assert details["A->B"]["effective_time_weight_power"] == 2.0
    assert details["C->D"]["effective_time_weight_power"] == 1.5
    assert details["E->F"]["effective_time_weight_power"] == 1.0
