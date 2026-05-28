#!/usr/bin/env python3
"""Deterministic v1.5 dynamic finite-storage primal-dual gates."""
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
    update_dynamic_dual_state,
)

REQUIREMENTS_COVERED = ["V15-STATE-01", "V15-CTRL-01", "V15-GATE-01", "V15-CLAIM-01"]
CONTROLLER_ID = "finite_storage_dynamic_primal_dual_v1_5"
SCOPE = "deterministic_one_step_v15_method_gates_no_closed_loop_claims"


def _select_dynamic(
    phase_states: dict[str, list[str]],
    movements: dict[str, list[tuple[str, str]]],
    queues: dict[str, float],
    capacities: dict[str, float],
    vehicle_counts: dict[str, float],
) -> dict[str, Any]:
    state = build_completed_finite_storage_state(
        queues,
        capacities,
        vehicle_counts=vehicle_counts,
        current_phase=0,
        time_since_switch=30.0,
    )
    dual_state = initialize_dynamic_dual_state(sorted(capacities))
    update_dynamic_dual_state(dual_state, state, build_downstream_adjacency(movements))
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
    return {"finite_storage_state": state, "dual_state": dual_state, "audit": audit}


def slack_recovery_case() -> dict[str, Any]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 20.0, "down_a": 5.0, "up_b": 14.0, "down_b": 4.0}
    capacities = {"up_a": 40.0, "down_a": 40.0, "up_b": 40.0, "down_b": 40.0}
    vehicle_counts = {"up_a": 8.0, "down_a": 5.0, "up_b": 7.0, "down_b": 4.0}
    result = _select_dynamic(phase_states, movements, queues, capacities, vehicle_counts)
    audit = result["audit"]
    zero_prices = all(
        abs(float(edge_state.get(field, 0.0))) < 1e-12
        for edge_state in result["dual_state"].values()
        for field in ["storage_price", "release_price", "cascade_price", "service_age"]
    )
    return {
        "name": "slack_pressure_recovery",
        "criteria": {
            "dynamic_matches_pressure": audit["selected_action"] == audit["pressure_action"],
            "dual_prices_zero": zero_prices,
        },
        **result,
    }


def occupancy_storage_separation_case() -> dict[str, Any]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 30.0, "down_a": 0.0, "up_b": 18.0, "down_b": 0.0}
    capacities = {"up_a": 50.0, "down_a": 10.0, "up_b": 50.0, "down_b": 10.0}
    vehicle_counts = {"up_a": 3.0, "down_a": 10.0, "up_b": 2.0, "down_b": 1.0}
    result = _select_dynamic(phase_states, movements, queues, capacities, vehicle_counts)
    queue_capacity_action = choose_controller_action(
        "capacity_aware_pressure",
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
        "name": "occupancy_storage_separation",
        "queue_capacity_action": queue_capacity_action,
        "occupancy_capacity_action": occupancy_capacity_action,
        "criteria": {
            "storage_uses_vehicle_count": result["finite_storage_state"]["residual_receiving_capacity"]["down_a"] == 0.0,
            "dynamic_changes_from_pressure": audit["selected_action"] != audit["pressure_action"],
            "dynamic_matches_occupancy_ablation": audit["selected_action"] == occupancy_capacity_action,
            "queue_ablation_misses_storage_fullness": queue_capacity_action != occupancy_capacity_action,
            "storage_price_active": result["dual_state"]["down_a"]["storage_price"] > 0.0,
        },
        **result,
    }


def cascade_spillback_case() -> dict[str, Any]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {
        "J0": [("up_a", "mid_a"), ("up_b", "mid_b")],
        "J1": [("mid_a", "down_full")],
    }
    queues = {"up_a": 20.0, "mid_a": 0.0, "up_b": 19.0, "mid_b": 0.0, "down_full": 0.0}
    capacities = {"up_a": 40.0, "mid_a": 20.0, "up_b": 40.0, "mid_b": 20.0, "down_full": 10.0}
    vehicle_counts = {"up_a": 3.0, "mid_a": 1.0, "up_b": 3.0, "mid_b": 1.0, "down_full": 10.0}
    result = _select_dynamic(phase_states, movements, queues, capacities, vehicle_counts)
    audit = result["audit"]
    return {
        "name": "cascade_spillback_separation",
        "criteria": {
            "descendant_storage_price_active": result["dual_state"]["down_full"]["storage_price"] > 0.0,
            "intermediate_cascade_price_active": result["dual_state"]["mid_a"]["cascade_price"] > 0.0,
            "dynamic_avoids_cascade_path": audit["selected_action"] == 1 and audit["pressure_action"] == 0,
        },
        **result,
    }


def upstream_release_case() -> dict[str, Any]:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}
    queues = {"up_a": 10.0, "down_a": 0.0, "up_b": 9.0, "down_b": 0.0}
    capacities = {"up_a": 20.0, "down_a": 20.0, "up_b": 20.0, "down_b": 20.0}
    vehicle_counts = {"up_a": 2.0, "down_a": 1.0, "up_b": 20.0, "down_b": 1.0}
    result = _select_dynamic(phase_states, movements, queues, capacities, vehicle_counts)
    audit = result["audit"]
    return {
        "name": "upstream_release_value",
        "criteria": {
            "release_price_active": result["dual_state"]["up_b"]["release_price"] > 0.0,
            "dynamic_serves_release_movement": audit["selected_action"] == 1 and audit["pressure_action"] == 0,
        },
        **result,
    }


def build_payload() -> dict[str, Any]:
    cases = [slack_recovery_case(), occupancy_storage_separation_case(), cascade_spillback_case(), upstream_release_case()]
    criteria = {
        case["name"]: all(bool(value) for value in case["criteria"].values())
        for case in cases
    }
    return {
        "experiment": "v1_5_dynamic_primal_dual_gates",
        "status": "PASSED" if all(criteria.values()) else "FAILED",
        "generated_by": "scripts/check_v15_dynamic_primal_dual.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": SCOPE,
        "requirements_covered": REQUIREMENTS_COVERED,
        "schema_version": SCHEMA_VERSION,
        "controller_id": CONTROLLER_ID,
        "criteria": criteria,
        "claim_scope": {
            "allowed": "deterministic v1.5 method-gate evidence for state truth, slack recovery, and action separation mechanisms",
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/dual_sensitivity/v1_5_dynamic_primal_dual_gates.json")
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
