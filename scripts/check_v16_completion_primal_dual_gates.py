#!/usr/bin/env python3
"""Deterministic v1.6 completion-safe primal-dual gates.

Five one-step gates that verify the v1.6 controller's key behavioral
mechanisms using synthetic traffic states.  No closed-loop claims are
made; each gate checks a specific structural property of the
completion-safe controller and its dual-price decomposition.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from finite_storage_schema import SCHEMA_VERSION
from run_closed_loop_sumo import (
    build_completed_finite_storage_state,
    build_downstream_adjacency,
    choose_controller_action,
    initialize_dynamic_dual_state,
    select_finite_storage_action_with_audit,
    update_completion_dual_state,
    update_dynamic_dual_state,
    DYNAMIC_V1_6_PARAMS,
)

REQUIREMENTS_COVERED = [
    "V16-STATE-01",
    "V16-CTRL-01",
    "V16-GATE-01",
    "V16-GATE-02",
    "V16-GATE-03",
    "V16-GATE-04",
    "V16-GATE-05",
    "V16-CLAIM-01",
]
CONTROLLER_ID = "finite_storage_completion_safe_primal_dual_v1_6"
SCOPE = "deterministic_one_step_v16_completion_primal_dual_gates_no_closed_loop_claims"


def _select_v16(
    phase_states: dict[str, list[str]],
    movements: dict[str, list[tuple[str, str]]],
    queues: dict[str, float],
    capacities: dict[str, float],
    vehicle_counts: dict[str, float],
    *,
    step: int | None = None,
    warmup: int | None = None,
    steps: int | None = None,
) -> dict[str, Any]:
    """Build state, initialize and update duals, then run v1.6 audit."""
    state = build_completed_finite_storage_state(
        queues,
        capacities,
        vehicle_counts=vehicle_counts,
        current_phase=0,
        time_since_switch=30.0,
    )
    dual_state = initialize_dynamic_dual_state(sorted(capacities))
    update_dynamic_dual_state(dual_state, state, build_downstream_adjacency(movements))
    update_completion_dual_state(
        dual_state,
        state,
        step=step,
        warmup=warmup,
        steps=steps,
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
        step=step,
        warmup=warmup,
        steps=steps,
    )
    return {
        "finite_storage_state": state,
        "dual_state": dual_state,
        "audit": audit,
    }


# ---------------------------------------------------------------------------
# Gate 1: Pressure recovery — when storage/completion slack is abundant,
# v1.6 must agree with max-pressure.
# ---------------------------------------------------------------------------
def pressure_recovery_gate() -> dict[str, Any]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 20.0, "down_a": 5.0, "up_b": 14.0, "down_b": 4.0}
    capacities = {"up_a": 40.0, "down_a": 40.0, "up_b": 40.0, "down_b": 40.0}
    vehicle_counts = {"up_a": 8.0, "down_a": 5.0, "up_b": 7.0, "down_b": 4.0}
    result = _select_v16(phase_states, movements, queues, capacities, vehicle_counts)
    audit = result["audit"]
    zero_prices = all(
        abs(float(edge_state.get(field, 0.0))) < 1e-12
        for edge_state in result["dual_state"].values()
        for field in [
            "storage_price",
            "release_price",
            "cascade_price",
            "service_age",
            "completion_price",
        ]
    )
    return {
        "name": "pressure_recovery",
        "criteria": {
            "v16_matches_pressure": audit["selected_action"] == audit["pressure_action"],
            "dual_prices_zero": zero_prices,
        },
        **result,
    }


# ---------------------------------------------------------------------------
# Gate 2: Storage separation — when downstream storage is nearly full,
# v1.6 must avoid the unsafe receiving movement that pressure would choose.
# ---------------------------------------------------------------------------
def storage_separation_gate() -> dict[str, Any]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 30.0, "down_a": 0.0, "up_b": 18.0, "down_b": 0.0}
    capacities = {"up_a": 50.0, "down_a": 10.0, "up_b": 50.0, "down_b": 10.0}
    vehicle_counts = {"up_a": 3.0, "down_a": 10.0, "up_b": 2.0, "down_b": 1.0}
    result = _select_v16(phase_states, movements, queues, capacities, vehicle_counts)
    occupancy_capacity_action = choose_controller_action(
        "occupancy_capacity_aware_pressure",
        "J0",
        0,
        20,
        10,
        phase_states,
        movements,
        queues,
        capacities,
        vehicle_counts=vehicle_counts,
    )
    audit = result["audit"]
    return {
        "name": "storage_separation",
        "occupancy_capacity_action": occupancy_capacity_action,
        "criteria": {
            "residual_receiving_zero_down_a": result["finite_storage_state"]["residual_receiving_capacity"]["down_a"] == 0.0,
            "v16_changes_from_pressure": audit["selected_action"] != audit["pressure_action"],
            "v16_matches_occupancy_ablation": audit["selected_action"] == occupancy_capacity_action,
            "storage_price_active": result["dual_state"]["down_a"]["storage_price"] > 0.0,
        },
        **result,
    }


# ---------------------------------------------------------------------------
# Gate 3: Cascade separation — immediate downstream is available but a
# descendant has high shadow price; v1.6 must pre-emptively avoid the
# cascade path.
# ---------------------------------------------------------------------------
def cascade_separation_gate() -> dict[str, Any]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {
        "J0": [("up_a", "mid_a"), ("up_b", "mid_b")],
        "J1": [("mid_a", "down_full")],
    }
    queues = {
        "up_a": 20.0,
        "mid_a": 0.0,
        "up_b": 19.0,
        "mid_b": 0.0,
        "down_full": 0.0,
    }
    capacities = {
        "up_a": 40.0,
        "mid_a": 20.0,
        "up_b": 40.0,
        "mid_b": 20.0,
        "down_full": 10.0,
    }
    vehicle_counts = {
        "up_a": 3.0,
        "mid_a": 1.0,
        "up_b": 3.0,
        "mid_b": 1.0,
        "down_full": 10.0,
    }
    result = _select_v16(phase_states, movements, queues, capacities, vehicle_counts)
    audit = result["audit"]
    return {
        "name": "cascade_separation",
        "criteria": {
            "descendant_storage_price_active": result["dual_state"]["down_full"]["storage_price"] > 0.0,
            "intermediate_cascade_price_active": result["dual_state"]["mid_a"]["cascade_price"] > 0.0,
            "v16_avoids_cascade_path": audit["selected_action"] == 1 and audit["pressure_action"] == 0,
        },
        **result,
    }


# ---------------------------------------------------------------------------
# Gate 4: Release value — upstream has high occupancy while downstream
# path has slack; v1.6 must release the upstream queue.
# ---------------------------------------------------------------------------
def release_value_gate() -> dict[str, Any]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 10.0, "down_a": 0.0, "up_b": 9.0, "down_b": 0.0}
    capacities = {"up_a": 20.0, "down_a": 20.0, "up_b": 20.0, "down_b": 20.0}
    vehicle_counts = {"up_a": 2.0, "down_a": 1.0, "up_b": 20.0, "down_b": 1.0}
    result = _select_v16(phase_states, movements, queues, capacities, vehicle_counts)
    audit = result["audit"]
    return {
        "name": "release_value",
        "criteria": {
            "release_price_active": result["dual_state"]["up_b"]["release_price"] > 0.0,
            "v16_serves_release_movement": audit["selected_action"] == 1 and audit["pressure_action"] == 0,
        },
        **result,
    }


# ---------------------------------------------------------------------------
# Gate 5: Terminal completion — two actions have similar storage benefit
# but one creates terminal unfinished risk; v1.6 picks the
# completion-safe action via the completion-price mechanism.
#
# Design: down_a is nearly full (vehicle_count ~ capacity) so it has high
# completion deficit; down_b has plenty of slack.  The completion price
# penalises routing traffic toward down_a, causing v1.6 to prefer phase 1
# (serving up_b -> down_b) over phase 0 (serving up_a -> down_a).
# ---------------------------------------------------------------------------
def terminal_completion_gate() -> dict[str, Any]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    # Symmetric upstream queues so pure pressure gives equal scores.
    # down_a is nearly full (vehicle_count 28/30), down_b has slack (4/30).
    queues = {"up_a": 15.0, "down_a": 5.0, "up_b": 15.0, "down_b": 5.0}
    capacities = {"up_a": 30.0, "down_a": 30.0, "up_b": 30.0, "down_b": 30.0}
    vehicle_counts = {"up_a": 8.0, "down_a": 28.0, "up_b": 8.0, "down_b": 4.0}
    # Place us deep in the completion zone so completion_price activates.
    # horizon_frac = 0.70 => in_completion_zone when remaining/total <= 0.30
    warmup = 100
    steps = 300
    step = 300  # remaining = 0, in_completion_zone = True
    result = _select_v16(
        phase_states,
        movements,
        queues,
        capacities,
        vehicle_counts,
        step=step,
        warmup=warmup,
        steps=steps,
    )
    audit = result["audit"]
    down_a_completion = float(result["dual_state"]["down_a"].get("completion_price", 0.0))
    down_b_completion = float(result["dual_state"]["down_b"].get("completion_price", 0.0))
    # down_a: high vehicle count (28/30), low residual => completion deficit > 0.
    # down_b: low vehicle count (4/30), high residual => no deficit.
    # completion_price penalises movements toward down_a, favouring phase 1.
    return {
        "name": "terminal_completion",
        "criteria": {
            "completion_price_asymmetric": down_a_completion > down_b_completion,
            "down_a_completion_price_positive": down_a_completion > 0.0,
            "v16_selects_completion_safe_action": audit["selected_action"] == 1,
        },
        **result,
    }


def build_payload() -> dict[str, Any]:
    cases = [
        pressure_recovery_gate(),
        storage_separation_gate(),
        cascade_separation_gate(),
        release_value_gate(),
        terminal_completion_gate(),
    ]
    criteria = {
        case["name"]: all(bool(value) for value in case["criteria"].values())
        for case in cases
    }
    return {
        "experiment": "v1_6_completion_primal_dual_gates",
        "status": "PASSED" if all(criteria.values()) else "FAILED",
        "generated_by": "scripts/check_v16_completion_primal_dual_gates.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": SCOPE,
        "requirements_covered": REQUIREMENTS_COVERED,
        "schema_version": SCHEMA_VERSION,
        "controller_id": CONTROLLER_ID,
        "criteria": criteria,
        "claim_scope": {
            "allowed": (
                "deterministic v1.6 method-gate evidence for pressure recovery, "
                "storage separation, cascade separation, release value, and "
                "terminal completion safety mechanisms"
            ),
            "not_claimed": [
                "closed_loop_superiority",
                "deployment_readiness",
                "universal_cross_regime_advantage",
                "locked_holdout_performance",
            ],
        },
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run deterministic v1.6 completion-safe primal-dual gate checks.",
    )
    parser.add_argument(
        "--out",
        default="experiments/dual_sensitivity/v1_6_completion_primal_dual_gates.json",
    )
    args = parser.parse_args()

    payload = build_payload()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": str(out_path)}, indent=2))
    if payload["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
