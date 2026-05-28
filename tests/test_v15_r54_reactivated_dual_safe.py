#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r54_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    build_completed_finite_storage_state,
    build_downstream_adjacency,
    initialize_dynamic_dual_state,
    select_finite_storage_action_with_audit,
    update_dynamic_dual_state,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r54_reactivated_dual_safe_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert protocol["controller_params"]["dual_step_size"] > 0.0
    assert protocol["controller_params"]["beta_storage"] > 0.0
    assert protocol["controller_params"]["gamma_cascade"] > 0.0


def test_r54_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r54_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r54_reactivated_dual_terms_separate_storage_binding() -> None:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 30.0, "down_a": 0.0, "up_b": 18.0, "down_b": 0.0}
    capacities = {"up_a": 50.0, "down_a": 10.0, "up_b": 50.0, "down_b": 10.0}
    vehicle_counts = {"up_a": 3.0, "down_a": 10.0, "up_b": 2.0, "down_b": 1.0}
    state = build_completed_finite_storage_state(
        queues,
        capacities,
        vehicle_counts=vehicle_counts,
        current_phase=0,
        time_since_switch=30.0,
    )
    dual_state = initialize_dynamic_dual_state(sorted(capacities))
    update_dynamic_dual_state(
        dual_state,
        state,
        build_downstream_adjacency(movements),
        params=build_training_protocol()["controller_params"],
    )

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
    )

    assert audit["pressure_action"] == 0
    assert audit["selected_action"] == 1
    assert dual_state["down_a"]["storage_price"] > 0.0
