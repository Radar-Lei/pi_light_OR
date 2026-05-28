#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r47_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    completion_safety_veto_active,
    select_finite_storage_action_with_audit,
)
from run_v15_r2_training import build_training_spec  # noqa: E402
from test_v15_r24_staged_horizon import base_inputs  # noqa: E402


def _risk_case_inputs(occupancy_ratio: float) -> tuple[dict[str, list[str]], dict[str, list[tuple[str, str]]], dict[str, float], dict[str, float], dict[str, object], dict[str, dict[str, float]], dict[str, object]]:
    phase_states, movements, queues, capacities, state, dual_state, route_completion_state = base_inputs()
    queues.update({"up_a": 20.0, "up_b": 4.0, "down_a": 2.0, "down_b": 0.0})
    state["spillback_blocking"]["down_a"] = {
        "spillback": occupancy_ratio >= 0.85,
        "blocking": occupancy_ratio >= 0.90,
        "occupancy_ratio": occupancy_ratio,
    }
    state["residual_receiving_capacity"]["down_a"] = 10.0 * (1.0 - occupancy_ratio)
    route_completion_state["finishable_movement_demand"] = {
        "up_a->down_a": 1.0,
        "up_b->down_b": 8.0,
    }
    route_completion_state["movement_demand"] = {
        "up_a->down_a": 20.0,
        "up_b->down_b": 8.0,
    }
    route_completion_state["movement_remaining_time_sum"] = {
        "up_a->down_a": 3000.0,
        "up_b->down_b": 80.0,
    }
    route_completion_state["remaining_edge_demand"] = {
        "down_a": 20.0,
        "down_b": 8.0,
    }
    return phase_states, movements, queues, capacities, state, dual_state, route_completion_state


def test_r47_staged_severe_double_safe_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["route_horizon_severe_double_guard"] == 1.0
    assert protocol["controller_params"]["route_horizon_severe_double_start_fraction"] == 0.60
    assert protocol["controller_params"]["completion_safety_start_fraction"] == 0.85
    assert protocol["controller_params"]["completion_safety_occupancy_threshold"] > protocol["controller_params"]["route_horizon_severe_double_occupancy_threshold"]


def test_r47_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r47_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r47_severe_double_guard_reverts_midseverity_risk_before_emergency_veto() -> None:
    phase_states, movements, queues, capacities, state, dual_state, route_completion_state = _risk_case_inputs(0.80)

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
        step=2900,
        warmup=900,
        steps=3600,
    )

    assert audit["route_horizon_pressure_safe_guard_used"] is True
    assert audit["route_horizon_severe_double_guard_used"] is True
    assert audit["completion_safety_veto_used"] is False
    assert audit["completion_risk_filter_used"] is False
    assert audit["pressure_action"] == 0
    assert audit["finite_storage_double_action"] == 1
    assert audit["selected_action"] == 1


def test_r47_completion_safety_veto_still_exists_for_extreme_emergency() -> None:
    _phase_states, _movements, queues, _capacities, state, _dual_state, _route_completion_state = _risk_case_inputs(0.95)
    params = build_training_protocol()["controller_params"]

    assert completion_safety_veto_active(
        params,
        state,
        queues,
        step=3300,
        warmup=900,
        steps=3600,
    ) is True
