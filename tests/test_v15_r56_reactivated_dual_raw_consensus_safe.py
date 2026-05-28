#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r56_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import CONTROLLER_REGISTRY, DYNAMIC_V1_5_CONTROLLER_IDS, FINITE_STORAGE_CONTROLLER_IDS  # noqa: E402
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r56_reactivated_dual_raw_consensus_safe_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["route_horizon_raw_consensus_guard"] == 1.0
    assert protocol["controller_params"]["dual_step_size"] > 0.0
    assert "correction_cap_ratio" not in protocol["controller_params"]


def test_r56_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r56_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}
