#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r41_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    select_finite_storage_action_with_audit,
)
from run_v15_r2_training import build_training_spec  # noqa: E402
from test_v15_r24_staged_horizon import base_inputs  # noqa: E402


def test_r41_terminal_core_completion_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["route_horizon_pressure_safe_guard"] == 1.0
    assert protocol["controller_params"]["terminal_flush_locks_dynamic"] == 1.0
    assert protocol["controller_params"]["terminal_flush_action"] == "core_completion"


def test_r41_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r41_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r41_terminal_core_completion_lock_suppresses_horizon_override() -> None:
    phase_states, movements, queues, capacities, state, dual_state, route_completion_state = base_inputs()
    queues.update({"up_a": 30.0, "down_a": 25.0, "up_b": 4.0, "down_b": 0.0})
    state["downstream_storage"] = {edge: 30.0 if edge == "down_a" else 10.0 for edge in queues}
    state["residual_receiving_capacity"] = {edge: 0.0 if edge == "down_a" else 10.0 for edge in queues}
    state["spillback_blocking"]["down_a"] = {"spillback": True, "blocking": True, "occupancy_ratio": 1.0}
    route_completion_state["finishable_movement_demand"] = {
        "up_a->down_a": 0.5,
        "up_b->down_b": 8.0,
    }
    route_completion_state["movement_demand"] = {
        "up_a->down_a": 30.0,
        "up_b->down_b": 8.0,
    }
    route_completion_state["movement_remaining_time_sum"] = {
        "up_a->down_a": 3000.0,
        "up_b->down_b": 80.0,
    }
    route_completion_state["remaining_edge_demand"] = {
        "down_a": 30.0,
        "down_b": 8.0,
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
        route_completion_state=route_completion_state,
        step=3280,
        warmup=900,
        steps=3600,
    )

    assert audit["terminal_completion_fallback_used"] is True
    assert audit["route_horizon_completion_filter_used"] is False
    assert audit["selected_action"] == audit["capacity_aware_action"]
    assert audit["selected_action"] == audit["finite_storage_double_action"]
    assert audit["selected_action"] != audit["pressure_action"]
