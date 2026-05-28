#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r12_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    select_finite_storage_action_with_audit,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r12_route_completion_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["route_completion_prediction_filter"] == 1.0


def test_r12_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r12_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}
    assert not set(protocol["training_split"]["seeds"]) & set(
        protocol["training_split"]["excluded_seed_sets"]["all_prior_v1_5_training_and_binding"]
    )


def test_r12_prefers_receiver_constrained_completion_over_raw_service() -> None:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_full", "down_full"), ("up_slack", "down_slack")]}
    queues = {"up_full": 20.0, "down_full": 0.0, "up_slack": 12.0, "down_slack": 0.0}
    capacities = {edge: 10.0 for edge in queues}
    state = {
        "downstream_storage": {edge: 10.0 for edge in queues},
        "residual_receiving_capacity": {
            "up_full": 10.0,
            "down_full": 0.0,
            "up_slack": 10.0,
            "down_slack": 10.0,
        },
        "spillback_blocking": {
            "up_full": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
            "down_full": {"spillback": True, "blocking": True, "occupancy_ratio": 1.0},
            "up_slack": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
            "down_slack": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
        },
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 40.0},
        "service_urgency": {edge: 0.0 for edge in queues},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
    dual_state = {
        edge: {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0}
        for edge in queues
    }

    audit = select_finite_storage_action_with_audit(
        "J0",
        0,
        phase_states,
        movements,
        queues,
        capacities,
        state,
        controller=CONTROLLER_ID,
        dynamic_dual_state=dual_state,
        step=900,
        warmup=900,
        steps=3600,
    )

    assert audit["route_completion_prediction_filter_used"] is True
    assert audit["selected_action"] == 1
    assert audit["completion_service_phase_scores"]["0"] > audit["completion_service_phase_scores"]["1"]
    assert audit["route_completion_prediction_phase_scores"]["1"] > audit["route_completion_prediction_phase_scores"]["0"]
