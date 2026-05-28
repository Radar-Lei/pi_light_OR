#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r70_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    build_completed_finite_storage_state,
    build_downstream_adjacency,
    initialize_dynamic_dual_state,
    update_dynamic_dual_state,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r70_reactivated_dual_descendant_release_native_base_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert "base_score_variant" not in protocol["controller_params"]
    assert protocol["controller_params"]["release_descendant_slack_depth"] == 2.0
    assert protocol["controller_params"]["release_descendant_slack_threshold"] == 0.05


def test_r70_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r70_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r70_release_price_activates_with_grandchild_slack() -> None:
    movements = {
        "J0": [("up_a", "mid_a")],
        "J1": [("mid_a", "down_a")],
    }
    capacities = {"up_a": 20.0, "mid_a": 10.0, "down_a": 10.0}
    queues = {"up_a": 0.0, "mid_a": 0.0, "down_a": 0.0}
    vehicle_counts = {"up_a": 18.0, "mid_a": 10.0, "down_a": 2.0}
    state = build_completed_finite_storage_state(
        queues,
        capacities,
        vehicle_counts=vehicle_counts,
        current_phase=0,
        time_since_switch=30.0,
    )
    params = build_training_protocol()["controller_params"]
    dual_state = initialize_dynamic_dual_state(sorted(capacities))
    update_dynamic_dual_state(
        dual_state,
        state,
        build_downstream_adjacency(movements),
        params=params,
    )

    assert dual_state["up_a"]["release_price"] > 0.0
