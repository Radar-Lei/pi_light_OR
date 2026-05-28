#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r49_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_R48_PRESSURE_DOUBLE_CONFLICT_SAFE_PARAMS,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    fraction_gate_active,
    select_finite_storage_action_with_audit,
)
from run_v15_r2_training import build_training_spec  # noqa: E402
from test_v15_r47_staged_severe_double_safe import _risk_case_inputs  # noqa: E402


def test_r49_early_pressure_double_conflict_safe_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["route_horizon_pressure_double_conflict_guard"] == 1.0
    assert protocol["controller_params"]["route_horizon_pressure_double_conflict_start_fraction"] == 0.0


def test_r49_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r49_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r49_conflict_guard_gate_opens_immediately_after_warmup() -> None:
    params = build_training_protocol()["controller_params"]

    assert (
        fraction_gate_active(
            DYNAMIC_V1_5_R48_PRESSURE_DOUBLE_CONFLICT_SAFE_PARAMS,
            "route_horizon_pressure_double_conflict_start_fraction",
            step=950,
            warmup=900,
            steps=3600,
        )
        is False
    )
    assert (
        fraction_gate_active(
            params,
            "route_horizon_pressure_double_conflict_start_fraction",
            step=950,
            warmup=900,
            steps=3600,
        )
        is True
    )


def test_r49_conflict_guard_preserves_high_risk_revert_behavior() -> None:
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

    assert audit["route_horizon_pressure_double_conflict_guard_used"] is True
    assert audit["selected_action"] == audit["finite_storage_double_action"]
