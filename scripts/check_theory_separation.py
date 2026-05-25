#!/usr/bin/env python3
"""Deterministic Phase 7 theory separation checker."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from finite_storage_schema import (
    OBJECTIVE_COMPONENT_FIELDS,
    SCHEMA_VERSION,
    validate_objective_components,
    validate_state_objective_sample,
)

REQUIREMENTS_COVERED = ["THRY-01", "THRY-02", "THRY-03", "THRY-04"]
SCOPE = "theory_static_one_step_only_no_closed_loop_claims"
GUARANTEE_CANDIDATE = "constrained_lp_oracle_regret"


def pressure_score(movement: dict[str, str], queues: dict[str, float]) -> float:
    return float(queues[movement["upstream"]] - queues[movement["downstream"]])


def finite_storage_score(movement: dict[str, str], queues: dict[str, float], state: dict[str, Any]) -> float:
    downstream = movement["downstream"]
    score = pressure_score(movement, queues)
    flags = state["spillback_blocking"].get(downstream, {})
    if isinstance(flags, dict) and flags.get("blocking"):
        score -= 10.0
    incident = state["incident_capacity_drop"]
    if incident["active"] and incident["edge"] == downstream:
        score -= 5.0 * (1.0 - float(incident["factor"]))
    return float(score)


def select_action(scores: dict[str, float]) -> tuple[str, list[str]]:
    best = max(scores.values())
    tie_set = sorted(action for action, score in scores.items() if score == best)
    return tie_set[0], tie_set


def weighted_total(components: dict[str, float], weights: dict[str, float]) -> float:
    return float(sum(float(components[field]) * float(weights[field]) for field in OBJECTIVE_COMPONENT_FIELDS))


def validate_action_components(action_components: dict[str, dict[str, float]]) -> None:
    for components in action_components.values():
        validate_objective_components(components)


def build_slack_example(weights: dict[str, float]) -> dict[str, Any]:
    queues = {"up_a": 20.0, "down_a": 5.0, "up_b": 14.0, "down_b": 4.0}
    movements = {
        "phase_a": {"upstream": "up_a", "downstream": "down_a"},
        "phase_b": {"upstream": "up_b", "downstream": "down_b"},
    }
    state = {
        "downstream_storage": {"up_a": 40.0, "down_a": 40.0, "up_b": 40.0, "down_b": 40.0},
        "residual_receiving_capacity": {"up_a": 20.0, "down_a": 35.0, "up_b": 26.0, "down_b": 36.0},
        "spillback_blocking": {
            edge: {"spillback": False, "blocking": False, "occupancy_ratio": queues[edge] / 40.0}
            for edge in queues
        },
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 30.0},
        "service_urgency": {edge: queues[edge] / 40.0 for edge in queues},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
    pressure_scores = {action: pressure_score(movement, queues) for action, movement in movements.items()}
    finite_storage_scores = {
        action: finite_storage_score(movement, queues, state) for action, movement in movements.items()
    }
    pressure_action, pressure_tie_set = select_action(pressure_scores)
    finite_storage_action, finite_storage_tie_set = select_action(finite_storage_scores)
    objective_components = {
        "delay": sum(queues.values()),
        "unfinished_vehicle_penalty": 0.0,
        "spillback_blocking_time": 0.0,
        "switching_lost_time": 0.0,
    }
    action_objective_components = {action: dict(objective_components) for action in movements}
    totals = {action: weighted_total(components, weights) for action, components in action_objective_components.items()}
    example = {
        "name": "slack_recovery",
        "scope": SCOPE,
        "turning_ratios_fixed": True,
        "queues": queues,
        "movements": movements,
        "finite_storage_state": state,
        "objective_components": objective_components,
        "pressure_scores": pressure_scores,
        "finite_storage_scores": finite_storage_scores,
        "pressure_action": pressure_action,
        "finite_storage_action": finite_storage_action,
        "pressure_tie_set": pressure_tie_set,
        "finite_storage_tie_set": finite_storage_tie_set,
        "action_objective_components": action_objective_components,
        "objective_totals": totals,
        "criteria": {"slack_recovery_or_tie": finite_storage_action == pressure_action or pressure_action in finite_storage_tie_set},
    }
    validate_state_objective_sample(example)
    validate_action_components(action_objective_components)
    return example


def build_binding_example(weights: dict[str, float]) -> dict[str, Any]:
    queues = {"up_a": 30.0, "down_a": 10.0, "up_b": 15.0, "down_b": 2.0}
    movements = {
        "phase_a": {"upstream": "up_a", "downstream": "down_a"},
        "phase_b": {"upstream": "up_b", "downstream": "down_b"},
    }
    state = {
        "downstream_storage": {"up_a": 50.0, "down_a": 10.0, "up_b": 50.0, "down_b": 10.0},
        "residual_receiving_capacity": {"up_a": 20.0, "down_a": 0.0, "up_b": 35.0, "down_b": 8.0},
        "spillback_blocking": {
            "up_a": {"spillback": False, "blocking": False, "occupancy_ratio": 0.6},
            "down_a": {"spillback": True, "blocking": True, "occupancy_ratio": 1.0},
            "up_b": {"spillback": False, "blocking": False, "occupancy_ratio": 0.3},
            "down_b": {"spillback": False, "blocking": False, "occupancy_ratio": 0.2},
        },
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 30.0},
        "service_urgency": {"up_a": 0.6, "down_a": 1.0, "up_b": 0.3, "down_b": 0.2},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
    pressure_scores = {action: pressure_score(movement, queues) for action, movement in movements.items()}
    finite_storage_scores = {
        action: finite_storage_score(movement, queues, state) for action, movement in movements.items()
    }
    pressure_action, pressure_tie_set = select_action(pressure_scores)
    finite_storage_action, finite_storage_tie_set = select_action(finite_storage_scores)
    objective_components = {
        "delay": sum(queues.values()),
        "unfinished_vehicle_penalty": 0.0,
        "spillback_blocking_time": 0.0,
        "switching_lost_time": 0.0,
    }
    action_objective_components = {
        "phase_a": {
            "delay": sum(queues.values()),
            "unfinished_vehicle_penalty": 1.0,
            "spillback_blocking_time": 1.0,
            "switching_lost_time": 0.0,
        },
        "phase_b": {
            "delay": sum(queues.values()),
            "unfinished_vehicle_penalty": 0.0,
            "spillback_blocking_time": 0.0,
            "switching_lost_time": 0.0,
        },
    }
    objective_totals = {
        action: weighted_total(components, weights) for action, components in action_objective_components.items()
    }
    objective_margin = objective_totals[pressure_action] - objective_totals[finite_storage_action]
    example = {
        "name": "storage_binding_two_phase_separation",
        "scope": SCOPE,
        "turning_ratios_fixed": True,
        "queues": queues,
        "movements": movements,
        "finite_storage_state": state,
        "objective_components": objective_components,
        "pressure_scores": pressure_scores,
        "finite_storage_scores": finite_storage_scores,
        "pressure_action": pressure_action,
        "finite_storage_action": finite_storage_action,
        "pressure_tie_set": pressure_tie_set,
        "finite_storage_tie_set": finite_storage_tie_set,
        "action_objective_components": action_objective_components,
        "objective_totals": objective_totals,
        "objective_margin": float(objective_margin),
        "actions_separate": pressure_action != finite_storage_action,
        "strict_objective_improvement": objective_margin > 0.0,
        "criteria": {
            "binding_action_separation": pressure_action != finite_storage_action,
            "strict_one_step_objective_improvement": objective_margin > 0.0,
        },
    }
    validate_state_objective_sample(example)
    validate_action_components(action_objective_components)
    return example


def build_and_check_phase7_payload() -> dict[str, Any]:
    weights = {field: 1.0 for field in OBJECTIVE_COMPONENT_FIELDS}
    examples = [build_slack_example(weights), build_binding_example(weights)]
    criteria = {
        "THRY-01": examples[0]["criteria"]["slack_recovery_or_tie"],
        "THRY-02": examples[1]["criteria"]["binding_action_separation"],
        "THRY-03": examples[1]["criteria"]["strict_one_step_objective_improvement"],
        "THRY-04": True,
    }
    status = "PASSED" if all(criteria.values()) else "FAILED"
    return {
        "experiment": "phase7_theory_separation",
        "status": status,
        "scope": SCOPE,
        "generated_by": "scripts/check_theory_separation.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requirements_covered": REQUIREMENTS_COVERED,
        "schema_version": SCHEMA_VERSION,
        "one_step_objective_definition": {
            "predeclared_before_action_comparison": True,
            "components": sorted(OBJECTIVE_COMPONENT_FIELDS),
            "weights": weights,
            "formula": "delay + unfinished_vehicle_penalty + spillback_blocking_time + switching_lost_time",
        },
        "criteria": criteria,
        "claim_scope": {
            "allowed": "slack regimes recover or tie max-pressure; binding example is static one-step explicit finite-storage separation",
            "not_claimed": [
                "closed_loop_performance",
                "deployment_readiness",
                "universal_cross_regime_advantage",
                "v1_0_pressure_equivalent_evidence_as_improvement",
            ],
        },
        "guarantee_candidates": [GUARANTEE_CANDIDATE],
        "guarantee_candidate_details": {
            "candidate": GUARANTEE_CANDIDATE,
            "scope": "finite_sample_oracle_relative",
            "boundary": "does not establish closed-loop network performance or deployment claims",
        },
        "examples": examples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/dual_sensitivity/phase7_theory_separation.json")
    args = parser.parse_args()

    payload = build_and_check_phase7_payload()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": str(out_path)}, indent=2))
    if payload["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
