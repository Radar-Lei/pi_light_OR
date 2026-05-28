#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r28_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    select_finite_storage_action_with_audit,
)
from run_v15_r2_training import build_training_spec  # noqa: E402
from test_v15_r24_staged_horizon import base_inputs  # noqa: E402


def test_r28_max_pressure_envelope_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["route_horizon_max_pressure_envelope"] == 1.0
    assert protocol["controller_params"]["route_horizon_max_pressure_margin"] == 0.10


def test_r28_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r28_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r28_reverts_to_max_when_completion_advantage_is_weak() -> None:
    phase_states, movements, queues, capacities, state, dual_state, route_completion_state = base_inputs()
    route_completion_state["finishable_movement_demand"] = {
        "up_a->down_a": 1.0,
        "up_b->down_b": 1.0,
    }
    route_completion_state["movement_demand"] = {
        "up_a->down_a": 20.0,
        "up_b->down_b": 8.0,
    }
    route_completion_state["movement_remaining_time_sum"] = {
        "up_a->down_a": 60.0,
        "up_b->down_b": 60.0,
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
        step=3000,
        warmup=900,
        steps=3600,
    )

    assert audit["route_horizon_completion_filter_used"] is True
    assert audit["route_horizon_max_pressure_envelope_used"] is True
    assert audit["selected_action"] == audit["pressure_action"]


def test_r28_keeps_horizon_action_when_completion_advantage_is_strong() -> None:
    phase_states, movements, queues, capacities, state, dual_state, route_completion_state = base_inputs()

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
        step=3000,
        warmup=900,
        steps=3600,
    )

    assert audit["route_horizon_completion_filter_used"] is True
    assert audit["route_horizon_max_pressure_envelope_used"] is False
    assert audit["selected_action"] == 1
