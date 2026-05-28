#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_closed_loop_sumo as sumo  # noqa: E402
from lock_v15_r66_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    select_finite_storage_action_with_audit,
)
from run_v15_r2_training import build_training_spec  # noqa: E402
from test_v15_r24_staged_horizon import base_inputs  # noqa: E402


def test_r66_reactivated_dual_native_horizon_score_blend_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert "base_score_variant" not in protocol["controller_params"]
    assert protocol["controller_params"]["route_horizon_double_blend"] == 0.0
    assert protocol["controller_params"]["route_horizon_native_score_blend"] == 1.0
    assert protocol["controller_params"]["route_horizon_pressure_blend"] == 0.15


def test_r66_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r66_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r66_route_horizon_blend_uses_native_dynamic_score_when_completion_disagrees(monkeypatch) -> None:
    phase_states, movements, queues, capacities, state, dual_state, route_completion_state = base_inputs()

    def fake_dynamic_phase_decomposition(
        phase_index: int,
        states: list[str],
        movement_list: list[tuple[str, str]],
        queue_state: dict[str, float],
        capacity_state: dict[str, float],
        finite_storage_state: dict[str, object],
        dual_state_snapshot: dict[str, dict[str, float]],
        *,
        current_phase: int | None = None,
        params: dict[str, float] | None = None,
        score_variant: str = "finite_storage_dynamic_primal_dual_v1_5",
    ) -> dict[str, object]:
        total = 0.0 if phase_index == 0 else 100.0
        component_totals = {
            "cascade_price": 0.0,
            "double_pressure_scaffold": 0.0,
            "downstream_storage": 0.0,
            "guardrail": 0.0,
            "incident": 0.0,
            "pressure": total,
            "release": 0.0,
            "service": 0.0,
            "service_age": 0.0,
            "spillback": 0.0,
            "storage_price": 0.0,
            "switching": 0.0,
            "total": total,
        }
        return {
            "phase_index": int(phase_index),
            "score": float(total),
            "component_totals": component_totals,
            "movement_decompositions": [],
            "score_variant": score_variant,
        }

    def fake_phase_score(
        controller: str,
        phase_idx: int,
        states: list[str],
        movement_list: list[tuple[str, str]],
        queue_state: dict[str, float],
        capacity_state: dict[str, float],
        seed: int | None = None,
    ) -> float:
        if controller in {"max_pressure", "capacity_aware_pressure"}:
            return 10.0 if phase_idx == 1 else 0.0
        if controller == "finite_storage_double_pressure":
            return 10.0 if phase_idx == 0 else 0.0
        raise AssertionError(f"unexpected baseline controller: {controller}")

    monkeypatch.setattr(sumo, "dynamic_v1_5_phase_decomposition", fake_dynamic_phase_decomposition)
    monkeypatch.setattr(sumo, "phase_score", fake_phase_score)
    monkeypatch.setattr(
        sumo,
        "phase_route_horizon_completion_score",
        lambda phase_idx, *args, **kwargs: 100.0 if phase_idx == 0 else 90.0,
    )
    monkeypatch.setattr(sumo, "phase_completion_service_score", lambda *args, **kwargs: 0.0)
    monkeypatch.setattr(sumo, "completion_risk_active", lambda *args, **kwargs: True)

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
        step=2500,
        warmup=900,
        steps=3600,
    )

    assert audit["route_horizon_completion_filter_used"] is True
    assert audit["finite_storage_double_action"] == 0
    assert audit["pressure_action"] == audit["capacity_aware_action"] == 1
    assert audit["selected_action"] == 1
