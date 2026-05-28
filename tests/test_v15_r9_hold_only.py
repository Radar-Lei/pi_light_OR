#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_binding_protocol import BINDING_HOLDOUT_SEEDS  # noqa: E402
from lock_v15_r8_training_protocol import TRAINING_SEEDS as R8_TRAINING_SEEDS  # noqa: E402
from lock_v15_r9_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import CONTROLLER_REGISTRY, DYNAMIC_V1_5_CONTROLLER_IDS, FINITE_STORAGE_CONTROLLER_IDS, select_finite_storage_action_with_audit  # noqa: E402


def test_r9_hold_only_controller_is_registered() -> None:
    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS


def test_r9_training_protocol_uses_fresh_seeds_and_is_not_claim_ready() -> None:
    protocol = build_training_protocol()
    assert protocol["status"] == "TRAINING_LOCKED"
    assert protocol["controller_id"] == CONTROLLER_ID
    assert set(protocol["training_split"]["seeds"]).isdisjoint(BINDING_HOLDOUT_SEEDS)
    assert set(protocol["training_split"]["seeds"]).isdisjoint(R8_TRAINING_SEEDS)
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False


def test_r9_blocks_dynamic_switch_but_allows_dynamic_hold() -> None:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 10.0, "down_a": 0.0, "up_b": 3.0, "down_b": 0.0}
    capacities = {edge: 10.0 for edge in queues}
    state = {
        "downstream_storage": {edge: 10.0 for edge in queues},
        "residual_receiving_capacity": {edge: 10.0 for edge in queues},
        "spillback_blocking": {edge: {"spillback": False, "blocking": False, "occupancy_ratio": 0.0} for edge in queues},
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 10.0},
        "service_urgency": {edge: 0.0 for edge in queues},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
    dual_state = {
        "up_a": {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0},
        "down_a": {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0},
        "up_b": {"storage_price": 0.0, "release_price": 100.0, "cascade_price": 0.0, "service_age": 100.0},
        "down_b": {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0},
    }

    blocked = select_finite_storage_action_with_audit(
        "J0",
        0,
        phase_states,
        movements,
        queues,
        capacities,
        state,
        controller=CONTROLLER_ID,
        dynamic_dual_state=dual_state,
    )

    assert blocked["selected_action"] == blocked["pressure_action"]
    assert blocked["hold_only_safety_filter_used"] is True
