#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from finite_storage_schema import validate_state_objective_sample
from run_closed_loop_sumo import FINITE_STORAGE_DECOMPOSITION_FIELDS, select_finite_storage_action_with_audit

GATE_SCOPE = "static_explicit_state_action_decomposition_only_no_gate_c"
REQUIREMENTS_COVERED = ["GATE-01", "GATE-02", "GATE-04"]
BINDING_TERMS = {"downstream_storage", "spillback", "switching", "incident"}
FORBIDDEN_AFFIRMATIVE_PAYLOAD_KEYS = {
    "gate_c",
    "gate_c_closed_loop_dominance",
    "paired_seed_ci",
    "baseline_coverage",
    "stress_scenarios",
    "long_horizon_dominance",
}
FORBIDDEN_AFFIRMATIVE_PHRASES = [
    "universal superiority",
    "closed-loop superiority",
    "closed-loop dominance",
    "deployment readiness",
    "manuscript claim",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase7-json", default="experiments/dual_sensitivity/phase7_theory_separation.json")
    parser.add_argument("--out", default="experiments/dual_sensitivity/phase9_slack_binding_gates.json")
    return parser.parse_args()


def load_phase7_examples(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "PASSED":
        raise ValueError(f"Phase 7 source artifact {path} must have status PASSED")
    examples = payload.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ValueError(f"Phase 7 source artifact {path} must contain nonempty examples")
    return examples


def _phase_names(example: dict[str, Any]) -> list[str]:
    movements = example.get("movements")
    if not isinstance(movements, dict) or not movements:
        raise ValueError(f"Example {example.get('name', '<unnamed>')} is missing movements")
    return list(movements)


def _phase_index_map(example: dict[str, Any]) -> dict[str, int]:
    return {name: idx for idx, name in enumerate(_phase_names(example))}


def _phase_states(count: int) -> list[str]:
    states = []
    for idx in range(count):
        signals = ["r"] * count
        signals[idx] = "G"
        states.append("".join(signals))
    return states


def example_to_two_phase_fixture(
    example: dict[str, Any],
) -> tuple[dict[str, list[str]], dict[str, list[tuple[str, str]]], dict[str, float], dict[str, float], dict[str, Any]]:
    validate_explicit_gate_example(example)
    phase_names = _phase_names(example)
    movements_by_phase = example["movements"]
    tls_movements = []
    for phase_name in phase_names:
        movement = movements_by_phase[phase_name]
        if "upstream" not in movement or "downstream" not in movement:
            raise ValueError(f"Example {example.get('name', '<unnamed>')} movement {phase_name} is incomplete")
        tls_movements.append((str(movement["upstream"]), str(movement["downstream"])))
    queues = {str(edge): float(value) for edge, value in example["queues"].items()}
    state = example["finite_storage_state"]
    capacities = {str(edge): float(value) for edge, value in state["downstream_storage"].items()}
    return {"J0": _phase_states(len(phase_names))}, {"J0": tls_movements}, queues, capacities, state


def validate_explicit_gate_example(example: dict[str, Any]) -> None:
    if "queues" not in example:
        raise ValueError(f"Example {example.get('name', '<unnamed>')} is missing queues")
    if "finite_storage_state" not in example:
        raise ValueError(f"Example {example.get('name', '<unnamed>')} is missing finite_storage_state")
    if "objective_components" not in example:
        raise ValueError(f"Example {example.get('name', '<unnamed>')} is missing objective_components")
    validate_state_objective_sample(
        {
            "finite_storage_state": example["finite_storage_state"],
            "objective_components": example["objective_components"],
        }
    )


def _require_component_totals(value: Any, field: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"Action audit field {field} must be an object")
    if set(value) != FINITE_STORAGE_DECOMPOSITION_FIELDS:
        raise ValueError(
            f"Action audit field {field} must contain exact decomposition fields: {sorted(FINITE_STORAGE_DECOMPOSITION_FIELDS)}"
        )


def validate_action_audit(audit: dict[str, Any]) -> None:
    required = {
        "pressure_action",
        "finite_storage_action",
        "selected_action",
        "pressure_phase_scores",
        "phase_scores",
        "selected_component_totals",
        "changing_terms",
    }
    missing = required - set(audit)
    if missing:
        raise ValueError(f"Action audit is missing fields: {sorted(missing)}")
    if audit["selected_action"] != audit["finite_storage_action"]:
        raise ValueError("Action audit selected_action must equal finite_storage_action")
    if not isinstance(audit["pressure_phase_scores"], dict) or not audit["pressure_phase_scores"]:
        raise ValueError("Action audit requires nonempty pressure_phase_scores")
    if not isinstance(audit["phase_scores"], dict) or not audit["phase_scores"]:
        raise ValueError("Action audit requires nonempty phase_scores")
    _require_component_totals(audit["selected_component_totals"], "selected_component_totals")
    for phase, phase_audit in audit["phase_scores"].items():
        if not isinstance(phase_audit, dict):
            raise ValueError(f"Action audit phase_scores.{phase} must be an object")
        _require_component_totals(phase_audit.get("component_totals"), f"phase_scores.{phase}.component_totals")
    if not isinstance(audit["changing_terms"], list):
        raise ValueError("Action audit changing_terms must be a list")


def _audit_example(example: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    phase_states, tls_movements, queues, capacities, state = example_to_two_phase_fixture(example)
    index_by_name = _phase_index_map(example)
    current_phase = index_by_name.get(str(example.get("pressure_action", _phase_names(example)[0])), 0)
    audit = select_finite_storage_action_with_audit("J0", current_phase, phase_states, tls_movements, queues, capacities, state)
    validate_action_audit(audit)
    validate_finite_storage_tie_set(example, index_by_name, audit)
    return audit, index_by_name


def _diagnostic(name: str, status: str, **values: Any) -> dict[str, Any]:
    return {"example": name, "status": status, **values}


def _computed_finite_storage_tie_set(audit: dict[str, Any]) -> set[int]:
    scores = {int(phase): float(phase_audit["score"]) for phase, phase_audit in audit["phase_scores"].items()}
    if not scores:
        raise ValueError("Action audit phase_scores must be nonempty to compute tie set")
    best = max(scores.values())
    return {phase for phase, score in scores.items() if abs(score - best) <= 1e-9}


def validate_finite_storage_tie_set(example: dict[str, Any], index_by_name: dict[str, int], audit: dict[str, Any]) -> set[int]:
    declared_names = example.get("finite_storage_tie_set")
    if not isinstance(declared_names, list) or not declared_names:
        raise ValueError(f"Example {example.get('name')} requires nonempty finite_storage_tie_set")
    unknown_names = [name for name in declared_names if name not in index_by_name]
    if unknown_names:
        raise ValueError(f"Example {example.get('name')} finite_storage_tie_set contains unknown phases: {unknown_names}")
    declared_tie_set = {index_by_name[name] for name in declared_names}
    computed_tie_set = _computed_finite_storage_tie_set(audit)
    if declared_tie_set != computed_tie_set:
        raise ValueError(f"Example {example.get('name')} finite_storage_tie_set does not match recomputed phase scores")
    return computed_tie_set


def evaluate_gate_a_slack(examples: list[dict[str, Any]]) -> dict[str, Any]:
    slack_examples = [example for example in examples if example.get("name") == "slack_recovery"]
    if not slack_examples:
        return {"status": "FAILED", "num_examples": 0, "action_agreement_rate": 0.0, "tie_rate": 0.0, "diagnostics": [{"status": "FAILED", "reason": "missing slack_recovery example"}]}
    diagnostics = []
    agreements = 0
    ties = 0
    for example in slack_examples:
        audit, index_by_name = _audit_example(example)
        pressure_name = str(example.get("pressure_action"))
        pressure_action = index_by_name.get(pressure_name)
        if pressure_action is None:
            raise ValueError(f"Example {example.get('name')} is missing pressure comparator action")
        computed_tie_set = validate_finite_storage_tie_set(example, index_by_name, audit)
        action_matches = audit["finite_storage_action"] == pressure_action
        tie_expected = pressure_action in computed_tie_set and audit["finite_storage_action"] in computed_tie_set
        if action_matches:
            agreements += 1
        if tie_expected:
            ties += 1
        diagnostics.append(
            _diagnostic(
                str(example.get("name")),
                "PASSED" if action_matches or tie_expected else "FAILED",
                pressure_action=pressure_action,
                finite_storage_action=audit["finite_storage_action"],
                both_actions_in_finite_storage_tie_set=tie_expected,
            )
        )
    passed = all(item["status"] == "PASSED" for item in diagnostics)
    return {
        "status": "PASSED" if passed else "FAILED",
        "num_examples": len(slack_examples),
        "action_agreement_rate": agreements / len(slack_examples),
        "tie_rate": ties / len(slack_examples),
        "diagnostics": diagnostics,
        "interpretation": "slack recovery or expected tie, not a performance advantage claim",
    }


def _objective_margin(example: dict[str, Any], index_by_name: dict[str, int], audit: dict[str, Any]) -> float:
    totals = example.get("objective_totals")
    action_components = example.get("action_objective_components")
    if not isinstance(totals, dict) or not isinstance(action_components, dict):
        raise ValueError(f"Example {example.get('name')} requires objective_totals and action_objective_components")
    component_fields = ["delay", "unfinished_vehicle_penalty", "spillback_blocking_time", "switching_lost_time"]
    component_totals = {}
    for phase, components in action_components.items():
        missing = [field for field in component_fields if field not in components]
        if missing:
            raise ValueError(f"Example {example.get('name')} action_objective_components.{phase} missing fields: {missing}")
        component_totals[phase] = sum(float(components[field]) for field in component_fields)
    if set(component_totals) != set(totals):
        raise ValueError(f"Example {example.get('name')} objective_totals phases do not match action_objective_components")
    for phase, value in component_totals.items():
        if abs(float(totals[phase]) - value) > 1e-9:
            raise ValueError(f"Example {example.get('name')} objective_totals do not match action_objective_components")
    totals = component_totals
    phase_by_index = {idx: name for name, idx in index_by_name.items()}
    pressure_phase = phase_by_index[audit["pressure_action"]]
    finite_phase = phase_by_index[audit["finite_storage_action"]]
    recomputed_margin = float(totals[pressure_phase]) - float(totals[finite_phase])
    if "objective_margin" in example and abs(float(example["objective_margin"]) - recomputed_margin) > 1e-9:
        raise ValueError(f"Example {example.get('name')} objective_margin does not match objective totals")
    return recomputed_margin


def evaluate_gate_b_binding(examples: list[dict[str, Any]]) -> dict[str, Any]:
    binding_examples = [example for example in examples if "binding" in str(example.get("name", "")) or example.get("actions_separate")]
    if not binding_examples:
        return {"status": "FAILED", "num_examples": 0, "separation_rate": 0.0, "objective_improvement_rate": 0.0, "min_objective_margin": 0.0, "diagnostics": [{"status": "FAILED", "reason": "missing binding separation example"}]}
    diagnostics = []
    separations = 0
    improvements = 0
    margins = []
    for example in binding_examples:
        audit, index_by_name = _audit_example(example)
        if "pressure_action" not in example or "finite_storage_action" not in example:
            raise ValueError(f"Example {example.get('name')} is missing pressure/finite-storage comparator fields")
        expected_pressure = index_by_name[str(example["pressure_action"])]
        expected_finite = index_by_name[str(example["finite_storage_action"])]
        if audit["pressure_action"] != expected_pressure:
            raise ValueError(f"Example {example.get('name')} pressure comparator changed unexpectedly")
        margin = _objective_margin(example, index_by_name, audit)
        terms = set(audit["changing_terms"])
        separated = audit["finite_storage_action"] != audit["pressure_action"] and audit["finite_storage_action"] == expected_finite
        improved = margin > 0.0
        term_hit = bool(terms & BINDING_TERMS)
        separations += int(separated)
        improvements += int(improved)
        margins.append(margin)
        diagnostics.append(
            _diagnostic(
                str(example.get("name")),
                "PASSED" if separated and improved and term_hit else "FAILED",
                pressure_action=audit["pressure_action"],
                finite_storage_action=audit["finite_storage_action"],
                objective_margin=margin,
                changing_terms=sorted(terms),
                binding_term_hit=term_hit,
            )
        )
    passed = all(item["status"] == "PASSED" for item in diagnostics)
    return {
        "status": "PASSED" if passed else "FAILED",
        "num_examples": len(binding_examples),
        "separation_rate": separations / len(binding_examples),
        "objective_improvement_rate": improvements / len(binding_examples),
        "min_objective_margin": min(margins),
        "diagnostics": diagnostics,
        "interpretation": "binding action separation with strict one-step constrained-objective improvement only",
    }


def fail_closed_checks(examples: list[dict[str, Any]]) -> dict[str, str]:
    for example in examples:
        validate_explicit_gate_example(example)
        audit, _index_by_name = _audit_example(example)
        validate_action_audit(audit)
        if "pressure_action" not in example:
            raise ValueError(f"Example {example.get('name')} is missing pressure_action")
    return {
        "explicit_state_schema": "PASSED",
        "objective_components": "PASSED",
        "action_decomposition": "PASSED",
        "decomposition_components": "PASSED",
        "pressure_comparator": "PASSED",
        "required_examples": "PASSED",
    }


def gates_pass(payload: dict[str, Any]) -> bool:
    return (
        payload.get("gate_a_slack_recovery", {}).get("status") == "PASSED"
        and payload.get("gate_b_binding_separation", {}).get("status") == "PASSED"
        and all(value == "PASSED" for value in payload.get("fail_closed_checks", {}).values())
    )


def _collect_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys |= _collect_keys(item)
        return keys
    if isinstance(value, list):
        keys = set()
        for item in value:
            keys |= _collect_keys(item)
        return keys
    return set()


def _normalize_key(key: str) -> str:
    return key.lower().replace("-", "_")


def validate_payload_scope(payload: dict[str, Any]) -> None:
    payload_without_caveats = {key: value for key, value in payload.items() if key != "caveats"}
    normalized_keys = {_normalize_key(key) for key in _collect_keys(payload_without_caveats)}
    forbidden_present = {_normalize_key(key) for key in FORBIDDEN_AFFIRMATIVE_PAYLOAD_KEYS} & normalized_keys
    if forbidden_present:
        raise ValueError(f"Payload contains out-of-scope affirmative keys: {sorted(forbidden_present)}")
    non_caveat_text = json.dumps(payload_without_caveats).lower()
    forbidden_phrases = [phrase for phrase in FORBIDDEN_AFFIRMATIVE_PHRASES if phrase in non_caveat_text]
    if forbidden_phrases:
        raise ValueError(f"Payload contains out-of-scope affirmative language: {forbidden_phrases}")


def build_payload(examples: list[dict[str, Any]], input_path: Path) -> dict[str, Any]:
    gate_a = evaluate_gate_a_slack(examples)
    gate_b = evaluate_gate_b_binding(examples)
    checks = fail_closed_checks(examples)
    payload = {
        "experiment": "phase9_slack_binding_gates",
        "scope": GATE_SCOPE,
        "requirements_covered": REQUIREMENTS_COVERED,
        "inputs": [str(input_path)],
        "gate_a_slack_recovery": gate_a,
        "gate_b_binding_separation": gate_b,
        "fail_closed_checks": checks,
        "caveats": [
            "No Gate C, paired-seed dominance, baseline suite, stress scenarios, long-horizon evidence, or closed-loop superiority claim."
        ],
    }
    validate_payload_scope(payload)
    payload["status"] = "PASSED" if gates_pass(payload) else "FAILED"
    return payload


def write_gate_artifact(out_path: Path, phase7_path: Path) -> dict[str, Any]:
    examples = load_phase7_examples(phase7_path)
    payload = build_payload(examples, phase7_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_gate_artifact(Path(args.out), Path(args.phase7_json))
    print(json.dumps({"out": args.out, "status": payload["status"], "requirements_covered": payload["requirements_covered"]}, indent=2))


if __name__ == "__main__":
    main()
