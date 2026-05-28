#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r73_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r73_reactivated_dual_release_risk_late_conflict_safe_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["route_horizon_release_component_blend"] == 1.0
    assert protocol["controller_params"]["route_horizon_storage_risk_component_blend"] == 1.0
    assert protocol["controller_params"]["route_horizon_completion_conflict_start_fraction"] == 0.10
    assert protocol["controller_params"]["route_horizon_completion_conflict_occupancy_threshold"] == 1.10
    assert protocol["controller_params"]["route_horizon_completion_conflict_residual_threshold"] == 0.0
    assert protocol["controller_params"]["route_horizon_pressure_safe_start_fraction"] == 0.78
    assert protocol["controller_params"]["route_horizon_pressure_safe_min_completion_gain"] == 0.05


def test_r73_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r73_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}
