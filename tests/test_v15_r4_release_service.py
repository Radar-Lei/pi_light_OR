#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_binding_protocol import BINDING_HOLDOUT_SEEDS  # noqa: E402
from lock_v15_r2_training_protocol import TRAINING_SEEDS as R2_TRAINING_SEEDS  # noqa: E402
from lock_v15_r3_training_protocol import TRAINING_SEEDS as R3_TRAINING_SEEDS  # noqa: E402
from lock_v15_r4_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import CONTROLLER_REGISTRY, DYNAMIC_V1_5_CONTROLLER_IDS, FINITE_STORAGE_CONTROLLER_IDS  # noqa: E402


def test_r4_release_service_controller_is_registered() -> None:
    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS


def test_r4_training_protocol_uses_fresh_seeds_and_is_not_claim_ready() -> None:
    protocol = build_training_protocol()
    split = protocol["training_split"]

    assert protocol["status"] == "TRAINING_LOCKED"
    assert protocol["controller_id"] == CONTROLLER_ID
    assert set(split["seeds"]).isdisjoint(BINDING_HOLDOUT_SEEDS)
    assert set(split["seeds"]).isdisjoint(R2_TRAINING_SEEDS)
    assert set(split["seeds"]).isdisjoint(R3_TRAINING_SEEDS)
    assert split["expected_row_count"] == (
        len(split["scenarios"])
        * len(split["seeds"])
        * len(split["demand_multipliers"])
        * len(split["controllers"])
    )
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
