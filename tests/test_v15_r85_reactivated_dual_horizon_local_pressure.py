#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r85_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    phase_route_horizon_completion_score,
    select_finite_storage_action_with_audit,
)
from run_v15_r2_training import build_training_spec  # noqa: E402


def test_r85_reactivated_dual_horizon_local_pressure_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_local_pressure_penalty"] == 0.35
    assert protocol["controller_params"]["route_horizon_local_pressure_floor"] == 0.5


def test_r85_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r85_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r85_horizon_score_penalizes_nonpositive_local_pressure() -> None:
    states = ["Gr", "rG"]
    movements = [("up_a", "down_a"), ("up_b", "down_b")]
    capacities = {"down_a": 10.0, "down_b": 10.0}
    finite_storage_state = {
        "residual_receiving_capacity": {"down_a": 10.0, "down_b": 10.0},
        "downstream_storage": {"down_a": 10.0, "down_b": 10.0},
        "spillback_blocking": {
            "down_a": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
            "down_b": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0},
        },
    }
    route_completion_state = {
        "finishable_movement_demand": {"up_a->down_a": 1.0, "up_b->down_b": 1.0},
        "movement_demand": {"up_a->down_a": 1.0, "up_b->down_b": 1.0},
        "movement_remaining_time_sum": {"up_a->down_a": 0.0, "up_b->down_b": 0.0},
        "remaining_edge_demand": {"down_a": 0.0, "down_b": 0.0},
        "remaining_time": 100.0,
    }
    params = {"route_horizon_local_pressure_penalty": 0.35, "route_horizon_local_pressure_floor": 0.5}

    positive_pressure_score = phase_route_horizon_completion_score(
        0,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        params,
        queues={"up_a": 10.0, "down_a": 0.0, "up_b": 0.0, "down_b": 0.0},
    )
    nonpositive_pressure_score = phase_route_horizon_completion_score(
        1,
        states,
        movements,
        capacities,
        finite_storage_state,
        route_completion_state,
        params,
        queues={"up_a": 0.0, "down_a": 0.0, "up_b": 3.0, "down_b": 3.0},
    )

    assert positive_pressure_score > nonpositive_pressure_score


def test_r85_controller_demotes_weak_nonpositive_pressure_completion_candidate(monkeypatch) -> None:
    import run_closed_loop_sumo as sumo  # noqa: E402

    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 10.0, "down_a": 0.0, "up_b": 3.0, "down_b": 3.0}
    capacities = {edge: 10.0 for edge in {"up_a": 0, "down_a": 0, "up_b": 0, "down_b": 0}}
    state = {
        "downstream_storage": {"up_a": 10.0, "down_a": 10.0, "up_b": 10.0, "down_b": 10.0},
        "residual_receiving_capacity": {"up_a": 10.0, "down_a": 10.0, "up_b": 10.0, "down_b": 10.0},
        "spillback_blocking": {
            edge: {"spillback": False, "blocking": False, "occupancy_ratio": 0.0}
            for edge in {"up_a", "down_a", "up_b", "down_b"}
        },
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 10.0},
        "service_urgency": {edge: 0.0 for edge in {"up_a", "down_a", "up_b", "down_b"}},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
    dual_state = {
        edge: {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0}
        for edge in {"up_a", "down_a", "up_b", "down_b"}
    }

    def fake_dynamic_phase_decomposition(phase_index, *args, **kwargs):
        if phase_index == 0:
            c = {"cascade_price": 0.0, "double_pressure_scaffold": 0.0, "downstream_storage": 0.0, "guardrail": 0.0, "incident": 0.0, "pressure": 8.0, "release": 0.0, "service": 0.0, "service_age": 0.0, "spillback": 0.0, "storage_price": 0.0, "switching": 0.0, "total": 8.0}
        else:
            c = {"cascade_price": 0.0, "double_pressure_scaffold": 0.0, "downstream_storage": 0.0, "guardrail": 0.0, "incident": 0.0, "pressure": 0.0, "release": 1.5, "service": 0.0, "service_age": 0.0, "spillback": 0.0, "storage_price": -0.2, "switching": 0.0, "total": 1.3}
        return {"phase_index": int(phase_index), "score": float(c["total"]), "component_totals": c, "movement_decompositions": [], "score_variant": "finite_storage_dynamic_primal_dual_v1_5"}

    def fake_phase_score(controller, phase_idx, *args, **kwargs):
        if controller in {"max_pressure", "capacity_aware_pressure", "finite_storage_double_pressure"}:
            return 10.0 if phase_idx == 0 else 0.0
        raise AssertionError(controller)

    monkeypatch.setattr(sumo, "dynamic_v1_5_phase_decomposition", fake_dynamic_phase_decomposition)
    monkeypatch.setattr(sumo, "phase_score", fake_phase_score)
    monkeypatch.setattr(sumo, "phase_route_horizon_completion_score", phase_route_horizon_completion_score)
    monkeypatch.setattr(
        sumo,
        "build_active_route_completion_state",
        lambda *args, **kwargs: {
            "finishable_movement_demand": {"up_a->down_a": 1.0, "up_b->down_b": 1.0},
            "movement_demand": {"up_a->down_a": 1.0, "up_b->down_b": 1.0},
            "movement_remaining_time_sum": {"up_a->down_a": 0.0, "up_b->down_b": 0.0},
            "remaining_edge_demand": {"down_a": 0.0, "down_b": 0.0},
            "remaining_time": 100.0,
            "active_vehicle_count": 2,
        },
    )
    monkeypatch.setattr(sumo, "completion_risk_active", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        sumo,
        "state_storage_summary",
        lambda *args, **kwargs: {"max_occupancy_ratio": 1.1, "min_residual_ratio": 0.0},
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
        route_completion_state={
            "finishable_movement_demand": {"up_a->down_a": 1.0, "up_b->down_b": 1.0},
            "movement_demand": {"up_a->down_a": 1.0, "up_b->down_b": 1.0},
            "movement_remaining_time_sum": {"up_a->down_a": 0.0, "up_b->down_b": 0.0},
            "remaining_edge_demand": {"down_a": 0.0, "down_b": 0.0},
            "remaining_time": 100.0,
            "active_vehicle_count": 2,
        },
        step=950,
        warmup=900,
        steps=3600,
    )

    assert audit["route_horizon_completion_filter_used"] is True
    assert audit["selected_action"] == 0
