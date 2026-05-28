#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_binding_protocol import BINDING_HOLDOUT_SEEDS  # noqa: E402
from lock_v15_r2_training_protocol import TRAINING_SEEDS as R2_TRAINING_SEEDS  # noqa: E402
from lock_v15_r3_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    DYNAMIC_V1_5_R3_DOUBLE_RELEASE_PARAMS,
    FINITE_STORAGE_CONTROLLER_IDS,
    dynamic_v1_5_phase_decomposition,
)


def test_r3_double_release_controller_is_registered() -> None:
    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS


def test_r3_uses_double_pressure_scaffold_without_guarding_it_away() -> None:
    states = ["G"]
    movements = [("up", "down")]
    queues = {"up": 10.0, "down": 0.0}
    capacities = {"up": 10.0, "down": 10.0}
    state = {
        "downstream_storage": {"up": 10.0, "down": 10.0},
        "residual_receiving_capacity": {"up": 10.0, "down": 10.0},
        "spillback_blocking": {
            "up": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
            "down": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
        },
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 10.0},
        "service_urgency": {"up": 0.0, "down": 0.0},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
    dual_state = {
        "up": {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0},
        "down": {"storage_price": 100.0, "release_price": 0.0, "cascade_price": 100.0, "service_age": 0.0},
    }

    result = dynamic_v1_5_phase_decomposition(
        0,
        states,
        movements,
        queues,
        capacities,
        state,
        dual_state,
        params=DYNAMIC_V1_5_R3_DOUBLE_RELEASE_PARAMS,
        score_variant=CONTROLLER_ID,
    )
    totals = result["component_totals"]

    assert result["score_variant"] == CONTROLLER_ID
    assert totals["double_pressure_scaffold"] > 0.0
    assert totals["guardrail"] > 0.0
    assert totals["total"] < totals["pressure"] + totals["double_pressure_scaffold"]
    cap = DYNAMIC_V1_5_R3_DOUBLE_RELEASE_PARAMS["correction_cap_ratio"] * max(
        abs(totals["pressure"]),
        DYNAMIC_V1_5_R3_DOUBLE_RELEASE_PARAMS["correction_cap_floor"],
        1.0,
    )
    assert totals["total"] == totals["pressure"] + totals["double_pressure_scaffold"] - cap


def test_r3_training_protocol_uses_fresh_seeds_and_is_not_claim_ready() -> None:
    protocol = build_training_protocol()
    split = protocol["training_split"]

    assert protocol["status"] == "TRAINING_LOCKED"
    assert protocol["controller_id"] == CONTROLLER_ID
    assert set(split["seeds"]).isdisjoint(BINDING_HOLDOUT_SEEDS)
    assert set(split["seeds"]).isdisjoint(R2_TRAINING_SEEDS)
    assert split["expected_row_count"] == (
        len(split["scenarios"])
        * len(split["seeds"])
        * len(split["demand_multipliers"])
        * len(split["controllers"])
    )
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
