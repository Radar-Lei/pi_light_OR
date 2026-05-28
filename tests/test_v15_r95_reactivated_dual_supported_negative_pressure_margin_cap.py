#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_closed_loop_sumo as sumo  # noqa: E402
from lock_v15_r92_training_protocol import CONTROLLER_ID as R92_CONTROLLER_ID  # noqa: E402
from lock_v15_r95_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    DYNAMIC_V1_5_R95_REACTIVATED_DUAL_SUPPORTED_NEGATIVE_PRESSURE_MARGIN_CAP_PARAMS,
    FINITE_STORAGE_CONTROLLER_IDS,
    select_finite_storage_action_with_audit,
)
from run_v15_r2_training import build_training_spec  # noqa: E402
from test_v15_r24_staged_horizon import base_inputs  # noqa: E402


def test_r95_reactivated_dual_supported_negative_pressure_margin_cap_controller_is_registered() -> None:
    protocol = build_training_protocol()

    assert CONTROLLER_ID in CONTROLLER_REGISTRY
    assert CONTROLLER_ID in FINITE_STORAGE_CONTROLLER_IDS
    assert CONTROLLER_ID in DYNAMIC_V1_5_CONTROLLER_IDS
    assert protocol["controller_params"]["route_horizon_supported_negative_pressure_margin_cap"] == 0.15
    assert protocol["controller_params"]["route_horizon_supported_negative_pressure_total_ceiling"] == 2.0


def test_r95_training_spec_is_training_only_and_fresh() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert all(row["evidence_role"] == "v1_5_r95_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert CONTROLLER_ID in {row["controller"] for row in spec}


def test_r95_caps_only_negative_pressure_low_signal_thin_wins(monkeypatch) -> None:
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
        if phase_index == 0:
            component_totals = {
                "cascade_price": 0.0,
                "double_pressure_scaffold": 0.0,
                "downstream_storage": 0.0,
                "guardrail": 0.0,
                "incident": 0.0,
                "pressure": -3.0,
                "release": 0.0,
                "service": 0.0,
                "service_age": 0.0,
                "spillback": 0.0,
                "storage_price": 0.0,
                "switching": 0.0,
                "total": 8.0,
            }
        else:
            component_totals = {
                "cascade_price": 0.0,
                "double_pressure_scaffold": 0.0,
                "downstream_storage": 0.0,
                "guardrail": 0.0,
                "incident": 0.0,
                "pressure": -1.0,
                "release": 2.0,
                "service": 0.0,
                "service_age": 0.0,
                "spillback": 0.0,
                "storage_price": -1.0,
                "switching": 0.0,
                "total": -0.5,
            }
        return {
            "phase_index": int(phase_index),
            "score": float(component_totals["total"]),
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
        if controller in {"max_pressure", "capacity_aware_pressure", "finite_storage_double_pressure"}:
            return 10.0 if phase_idx == 0 else 0.0
        raise AssertionError(f"unexpected baseline controller: {controller}")

    monkeypatch.setattr(sumo, "dynamic_v1_5_phase_decomposition", fake_dynamic_phase_decomposition)
    monkeypatch.setattr(sumo, "phase_score", fake_phase_score)
    monkeypatch.setattr(
        sumo,
        "phase_route_horizon_completion_decomposition",
        lambda phase_idx, *args, **kwargs: {
            "score": 4.8 if phase_idx == 0 else 5.0,
            "components": {
                "finishable_term": 4.8 if phase_idx == 0 else 5.0,
                "downstream_penalty": 0.0,
                "local_pressure_penalty": 0.0,
            },
            "movement_details": [],
        },
    )
    monkeypatch.setattr(sumo, "phase_completion_service_score", lambda *args, **kwargs: 0.0)
    monkeypatch.setattr(sumo, "completion_risk_active", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        sumo,
        "state_storage_summary",
        lambda *args, **kwargs: {"max_occupancy_ratio": 1.10, "min_residual_ratio": 0.0},
    )
    monkeypatch.setitem(
        DYNAMIC_V1_5_R95_REACTIVATED_DUAL_SUPPORTED_NEGATIVE_PRESSURE_MARGIN_CAP_PARAMS,
        "route_horizon_low_signal_margin_core_horizon_floor",
        0.0,
    )
    monkeypatch.setitem(
        DYNAMIC_V1_5_R95_REACTIVATED_DUAL_SUPPORTED_NEGATIVE_PRESSURE_MARGIN_CAP_PARAMS,
        "route_horizon_low_signal_margin_cap",
        2.2,
    )
    monkeypatch.setitem(
        DYNAMIC_V1_5_R95_REACTIVATED_DUAL_SUPPORTED_NEGATIVE_PRESSURE_MARGIN_CAP_PARAMS,
        "route_horizon_supported_negative_pressure_margin_cap",
        2.2,
    )

    r92_audit = select_finite_storage_action_with_audit(
        "J0",
        0,
        phase_states,
        movements,
        queues,
        capacities,
        state,
        controller=R92_CONTROLLER_ID,
        dynamic_dual_state=dual_state,
        route_completion_state=route_completion_state,
        step=950,
        warmup=900,
        steps=3600,
    )
    r95_audit = select_finite_storage_action_with_audit(
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
        step=950,
        warmup=900,
        steps=3600,
    )

    assert "thin_margin_low_signal_capped" not in r92_audit["route_horizon_blended_phase_details"]["1"]
    assert r92_audit["selected_action"] == 1
    assert r95_audit["route_horizon_blended_phase_details"]["1"]["supported_negative_pressure_margin_capped"] == 1.0
    assert r95_audit["selected_action"] == 0


def test_r95_skips_cap_for_nonnegative_pressure_low_signal_wins(monkeypatch) -> None:
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
        if phase_index == 0:
            component_totals = {
                "cascade_price": 0.0,
                "double_pressure_scaffold": 0.0,
                "downstream_storage": 0.0,
                "guardrail": 0.0,
                "incident": 0.0,
                "pressure": -3.0,
                "release": 0.0,
                "service": 0.0,
                "service_age": 0.0,
                "spillback": 0.0,
                "storage_price": 0.0,
                "switching": 0.0,
                "total": 8.0,
            }
        else:
            component_totals = {
                "cascade_price": 0.0,
                "double_pressure_scaffold": 0.0,
                "downstream_storage": 0.0,
                "guardrail": 0.0,
                "incident": 0.0,
                "pressure": 0.0,
                "release": 2.0,
                "service": 0.0,
                "service_age": 0.0,
                "spillback": 0.0,
                "storage_price": -1.0,
                "switching": 0.0,
                "total": -0.5,
            }
        return {
            "phase_index": int(phase_index),
            "score": float(component_totals["total"]),
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
        if controller in {"max_pressure", "capacity_aware_pressure", "finite_storage_double_pressure"}:
            return 10.0 if phase_idx == 0 else 0.0
        raise AssertionError(f"unexpected baseline controller: {controller}")

    monkeypatch.setattr(sumo, "dynamic_v1_5_phase_decomposition", fake_dynamic_phase_decomposition)
    monkeypatch.setattr(sumo, "phase_score", fake_phase_score)
    monkeypatch.setattr(
        sumo,
        "phase_route_horizon_completion_decomposition",
        lambda phase_idx, *args, **kwargs: {
            "score": 4.8 if phase_idx == 0 else 5.0,
            "components": {
                "finishable_term": 4.8 if phase_idx == 0 else 5.0,
                "downstream_penalty": 0.0,
                "local_pressure_penalty": 0.0,
            },
            "movement_details": [],
        },
    )
    monkeypatch.setattr(sumo, "phase_completion_service_score", lambda *args, **kwargs: 0.0)
    monkeypatch.setattr(sumo, "completion_risk_active", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        sumo,
        "state_storage_summary",
        lambda *args, **kwargs: {"max_occupancy_ratio": 1.10, "min_residual_ratio": 0.0},
    )
    monkeypatch.setitem(
        DYNAMIC_V1_5_R95_REACTIVATED_DUAL_SUPPORTED_NEGATIVE_PRESSURE_MARGIN_CAP_PARAMS,
        "route_horizon_low_signal_margin_core_horizon_floor",
        0.0,
    )
    monkeypatch.setitem(
        DYNAMIC_V1_5_R95_REACTIVATED_DUAL_SUPPORTED_NEGATIVE_PRESSURE_MARGIN_CAP_PARAMS,
        "route_horizon_supported_negative_pressure_margin_cap",
        2.2,
    )

    r95_audit = select_finite_storage_action_with_audit(
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
        step=950,
        warmup=900,
        steps=3600,
    )

    assert "supported_negative_pressure_margin_capped" not in r95_audit["route_horizon_blended_phase_details"]["1"]
    assert r95_audit["selected_action"] == 1
