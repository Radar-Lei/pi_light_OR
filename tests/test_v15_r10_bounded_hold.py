#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r10_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import CONTROLLER_REGISTRY, DYNAMIC_V1_5_CONTROLLER_IDS, FINITE_STORAGE_CONTROLLER_IDS, select_finite_storage_action_with_audit  # noqa: E402


def test_r10_bounded_hold_controller_is_registered() -> None:
    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert build_training_protocol()["claim_scope"]["closed_loop_superiority_claim_allowed"] is False


def test_r10_blocks_hold_after_max_hold_time() -> None:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 10.0, "down_a": 0.0, "up_b": 3.0, "down_b": 0.0}
    capacities = {edge: 10.0 for edge in queues}
    state = {
        "downstream_storage": {edge: 10.0 for edge in queues},
        "residual_receiving_capacity": {edge: 10.0 for edge in queues},
        "spillback_blocking": {edge: {"spillback": False, "blocking": False, "occupancy_ratio": 0.0} for edge in queues},
        "switching_loss_state": {"current_phase": 1, "time_since_switch": 30.0},
        "service_urgency": {edge: 0.0 for edge in queues},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
    dual_state = {
        "up_a": {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0},
        "down_a": {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0},
        "up_b": {"storage_price": 0.0, "release_price": 100.0, "cascade_price": 0.0, "service_age": 100.0},
        "down_b": {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0},
    }

    audit = select_finite_storage_action_with_audit(
        "J0", 1, phase_states, movements, queues, capacities, state, controller=CONTROLLER_ID, dynamic_dual_state=dual_state
    )

    assert audit["max_hold_safety_filter_used"] is True
    assert audit["selected_action"] == audit["pressure_action"]
