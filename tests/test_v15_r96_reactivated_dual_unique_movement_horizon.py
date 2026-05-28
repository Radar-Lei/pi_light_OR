#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r96_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_decomposition,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r96_reactivated_dual_unique_movement_horizon_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_unique_movement_terms"] == 1.0


def test_r96_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r96_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_route_horizon_unique_movement_terms_deduplicates_repeated_movement_keys() -> None:
    states = ["GGG"]
    movements = [
        ("A", "B"),
        ("A", "B"),
        ("A", "B"),
    ]
    capacities = {"B": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"B": 5.0},
        "downstream_storage": {"B": 10.0},
    }
    route_completion_state = {
        "finishable_movement_demand": {"A->B": 6.0},
        "movement_demand": {"A->B": 6.0},
        "movement_remaining_time_sum": {"A->B": 60.0},
        "remaining_edge_demand": {"B": 0.0},
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
        queues={"A": 2.0, "B": 0.0},
    )
    deduped = phase_route_horizon_completion_decomposition(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        {"route_horizon_time_discount": 0.0, "route_horizon_unique_movement_terms": 1.0},
        queues={"A": 2.0, "B": 0.0},
    )

    assert len(baseline["movement_details"]) == 3
    assert len(deduped["movement_details"]) == 1
    assert baseline["components"]["finishable_term"] == 9.0
    assert deduped["components"]["finishable_term"] == 3.0
    assert baseline["score"] == 9.0
    assert deduped["score"] == 3.0
