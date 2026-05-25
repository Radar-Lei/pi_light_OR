#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_closed_loop_sumo import FINITE_STORAGE_DECOMPOSITION_FIELDS, select_finite_storage_action_with_audit  # noqa: E402
from run_slack_binding_gates import (  # noqa: E402
    build_payload,
    evaluate_gate_a_slack,
    evaluate_gate_b_binding,
    example_to_two_phase_fixture,
    gates_pass,
    load_phase7_examples,
    validate_action_audit,
    validate_explicit_gate_example,
    validate_finite_storage_tie_set,
    validate_payload_scope,
    write_gate_artifact,
)

PHASE7_JSON = ROOT / "experiments/dual_sensitivity/phase7_theory_separation.json"


def canonical_examples() -> list[dict]:
    return load_phase7_examples(PHASE7_JSON)


def slack_example() -> dict:
    return next(example for example in canonical_examples() if example["name"] == "slack_recovery")


def binding_example() -> dict:
    return next(example for example in canonical_examples() if example["name"] == "storage_binding_two_phase_separation")


def recompute_audit(example: dict) -> dict:
    phase_states, tls_movements, queues, capacities, state = example_to_two_phase_fixture(example)
    return select_finite_storage_action_with_audit("J0", 0, phase_states, tls_movements, queues, capacities, state)


def test_gate_a_slack_recovery_passes_without_superiority_language() -> None:
    gate = evaluate_gate_a_slack([slack_example()])
    assert gate["status"] == "PASSED"
    assert gate["action_agreement_rate"] == 1.0
    text = json.dumps(gate).lower()
    assert "superiority" not in text
    assert "dominance" not in text
    assert "win" not in text
    assert "recovery" in text


def test_gate_b_binding_separation_and_objective_improvement_pass() -> None:
    gate = evaluate_gate_b_binding([binding_example()])
    assert gate["status"] == "PASSED"
    assert gate["separation_rate"] == 1.0
    assert gate["objective_improvement_rate"] == 1.0
    assert gate["min_objective_margin"] == 2.0
    changing_terms = set(gate["diagnostics"][0]["changing_terms"])
    assert {"downstream_storage", "spillback", "switching", "incident"} & changing_terms


def test_payload_passes_and_excludes_affirmative_gate_c_outputs() -> None:
    payload = build_payload(canonical_examples(), PHASE7_JSON)
    assert payload["status"] == "PASSED"
    assert gates_pass(payload)
    assert payload["requirements_covered"] == ["GATE-01", "GATE-02", "GATE-04"]
    forbidden_keys = {"gate_c", "gate_c_closed_loop_dominance", "paired_seed_ci", "baseline_coverage", "stress_scenarios"}
    assert not forbidden_keys & set(payload)
    text = json.dumps({key: value for key, value in payload.items() if key != "caveats"}).lower()
    for phrase in ["closed-loop superiority", "universal superiority", "dominance claim", "manuscript"]:
        assert phrase not in text
    assert "no gate c" in " ".join(payload["caveats"]).lower()


def test_missing_finite_storage_state_fails_closed() -> None:
    example = copy.deepcopy(slack_example())
    example.pop("finite_storage_state")
    try:
        validate_explicit_gate_example(example)
    except ValueError as exc:
        assert "finite_storage_state" in str(exc)
    else:
        raise AssertionError("missing finite_storage_state should fail closed")


def test_missing_objective_components_fails_closed() -> None:
    example = copy.deepcopy(slack_example())
    example.pop("objective_components")
    try:
        validate_explicit_gate_example(example)
    except ValueError as exc:
        assert "objective_components" in str(exc)
    else:
        raise AssertionError("missing objective_components should fail closed")


def test_missing_action_audit_field_fails_closed() -> None:
    audit = recompute_audit(slack_example())
    audit.pop("selected_action")
    try:
        validate_action_audit(audit)
    except ValueError as exc:
        assert "selected_action" in str(exc)
    else:
        raise AssertionError("missing action audit field should fail closed")


def test_missing_decomposition_component_fails_closed() -> None:
    audit = recompute_audit(binding_example())
    assert set(audit["selected_component_totals"]) == FINITE_STORAGE_DECOMPOSITION_FIELDS
    audit["selected_component_totals"].pop("incident")
    try:
        validate_action_audit(audit)
    except ValueError as exc:
        assert "decomposition fields" in str(exc)
    else:
        raise AssertionError("missing decomposition component should fail closed")


def test_missing_phase_decomposition_component_fails_closed() -> None:
    audit = recompute_audit(binding_example())
    first_phase = next(iter(audit["phase_scores"].values()))
    first_phase["component_totals"].pop("service")
    try:
        validate_action_audit(audit)
    except ValueError as exc:
        assert "decomposition fields" in str(exc)
    else:
        raise AssertionError("missing phase decomposition component should fail closed")


def test_gate_a_rejects_mismatched_action_outside_finite_storage_tie_set() -> None:
    example = copy.deepcopy(slack_example())
    example["queues"] = {"up_a": 20.0, "down_a": 5.0, "up_b": 25.0, "down_b": 5.0}
    example["pressure_action"] = "phase_a"
    example["pressure_tie_set"] = ["phase_a", "phase_b"]
    example["finite_storage_tie_set"] = ["phase_a"]
    try:
        evaluate_gate_a_slack([example])
    except ValueError as exc:
        assert "finite_storage_tie_set" in str(exc)
    else:
        raise AssertionError("forged finite_storage_tie_set should fail closed")


def test_gate_a_rejects_forged_finite_storage_tie_set() -> None:
    example = copy.deepcopy(slack_example())
    example["finite_storage_tie_set"] = ["phase_a", "phase_b"]
    try:
        evaluate_gate_a_slack([example])
    except ValueError as exc:
        assert "finite_storage_tie_set" in str(exc)
    else:
        raise AssertionError("forged finite_storage_tie_set should fail closed")


def test_gate_a_rejects_unknown_finite_storage_tie_set_phase() -> None:
    example = copy.deepcopy(slack_example())
    example["finite_storage_tie_set"] = ["not_a_phase"]
    try:
        evaluate_gate_a_slack([example])
    except ValueError as exc:
        assert "unknown phases" in str(exc)
    else:
        raise AssertionError("unknown finite_storage_tie_set phase should fail closed")


def test_gate_b_rejects_unknown_finite_storage_tie_set_phase() -> None:
    example = copy.deepcopy(binding_example())
    example["finite_storage_tie_set"] = ["not_a_phase"]
    try:
        build_payload([slack_example(), example], PHASE7_JSON)
    except ValueError as exc:
        assert "unknown phases" in str(exc)
    else:
        raise AssertionError("binding unknown finite_storage_tie_set phase should fail closed")


def test_gate_b_rejects_forged_finite_storage_tie_set() -> None:
    example = copy.deepcopy(binding_example())
    example["finite_storage_tie_set"] = ["phase_a", "phase_b"]
    try:
        build_payload([slack_example(), example], PHASE7_JSON)
    except ValueError as exc:
        assert "finite_storage_tie_set" in str(exc)
    else:
        raise AssertionError("binding forged finite_storage_tie_set should fail closed")


def test_gate_b_rejects_forged_objective_margin() -> None:
    example = copy.deepcopy(binding_example())
    example["objective_margin"] = 999.0
    try:
        evaluate_gate_b_binding([example])
    except ValueError as exc:
        assert "objective_margin" in str(exc)
    else:
        raise AssertionError("forged objective_margin should fail closed")


def test_gate_b_rejects_objective_totals_component_mismatch() -> None:
    example = copy.deepcopy(binding_example())
    example["action_objective_components"]["phase_a"]["delay"] = 0.0
    try:
        evaluate_gate_b_binding([example])
    except ValueError as exc:
        assert "objective_totals" in str(exc)
    else:
        raise AssertionError("objective totals/components mismatch should fail closed")


def test_gate_b_requires_action_objective_components() -> None:
    example = copy.deepcopy(binding_example())
    example.pop("action_objective_components")
    try:
        evaluate_gate_b_binding([example])
    except ValueError as exc:
        assert "action_objective_components" in str(exc)
    else:
        raise AssertionError("missing action_objective_components should fail closed")


def test_payload_rejects_affirmative_forbidden_language_outside_caveats() -> None:
    payload = build_payload(canonical_examples(), PHASE7_JSON)
    payload["gate_b_binding_separation"]["interpretation"] = "closed-loop dominance"
    try:
        validate_payload_scope(payload)
    except ValueError as exc:
        assert "closed-loop dominance" in str(exc)
    else:
        raise AssertionError("affirmative forbidden language should fail closed")


def test_payload_rejects_nested_affirmative_forbidden_keys() -> None:
    payload = build_payload(canonical_examples(), PHASE7_JSON)
    payload["gate_b_binding_separation"]["gate_c_closed_loop_dominance"] = {"status": "PASSED"}
    try:
        validate_payload_scope(payload)
    except ValueError as exc:
        assert "gate_c_closed_loop_dominance" in str(exc) or "gate_c" in str(exc)
    else:
        raise AssertionError("nested forbidden key should fail closed")


def test_missing_pressure_comparator_fails_closed() -> None:
    example = copy.deepcopy(binding_example())
    example.pop("pressure_action")
    try:
        evaluate_gate_b_binding([example])
    except ValueError as exc:
        assert "pressure" in str(exc)
    else:
        raise AssertionError("missing pressure comparator should fail closed")


def test_missing_required_slack_or_binding_examples_fail_closed() -> None:
    assert evaluate_gate_a_slack([binding_example()])["status"] == "FAILED"
    assert evaluate_gate_b_binding([slack_example()])["status"] == "FAILED"


def test_cli_writer_creates_passed_artifact() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "phase9_gate.json"
        payload = write_gate_artifact(out, PHASE7_JSON)
        written = json.loads(out.read_text(encoding="utf-8"))
    assert payload["status"] == "PASSED"
    assert written["status"] == "PASSED"
    assert written["fail_closed_checks"] == {
        "explicit_state_schema": "PASSED",
        "objective_components": "PASSED",
        "action_decomposition": "PASSED",
        "decomposition_components": "PASSED",
        "pressure_comparator": "PASSED",
        "required_examples": "PASSED",
    }


def main() -> None:
    test_gate_a_slack_recovery_passes_without_superiority_language()
    test_gate_b_binding_separation_and_objective_improvement_pass()
    test_payload_passes_and_excludes_affirmative_gate_c_outputs()
    test_missing_finite_storage_state_fails_closed()
    test_missing_objective_components_fails_closed()
    test_missing_action_audit_field_fails_closed()
    test_missing_decomposition_component_fails_closed()
    test_missing_phase_decomposition_component_fails_closed()
    test_gate_a_rejects_mismatched_action_outside_finite_storage_tie_set()
    test_gate_a_rejects_forged_finite_storage_tie_set()
    test_gate_a_rejects_unknown_finite_storage_tie_set_phase()
    test_gate_b_rejects_unknown_finite_storage_tie_set_phase()
    test_gate_b_rejects_forged_finite_storage_tie_set()
    test_gate_b_rejects_forged_objective_margin()
    test_gate_b_rejects_objective_totals_component_mismatch()
    test_gate_b_requires_action_objective_components()
    test_payload_rejects_affirmative_forbidden_language_outside_caveats()
    test_payload_rejects_nested_affirmative_forbidden_keys()
    test_missing_pressure_comparator_fails_closed()
    test_missing_required_slack_or_binding_examples_fail_closed()
    test_cli_writer_creates_passed_artifact()
    print("slack/binding gate tests ok")


if __name__ == "__main__":
    main()
