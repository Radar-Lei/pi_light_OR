#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from claim_policy import FORBIDDEN_CLAIM_PATTERNS, forbidden_claim_hits
from finite_storage_schema import (
    FINITE_STORAGE_STATE_FIELDS,
    OBJECTIVE_COMPONENT_FIELDS,
    SCHEMA_VERSION,
    validate_state_objective_sample,
)

SCRIPT = SCRIPTS / "check_theory_separation.py"
AUDIT_SCRIPT = SCRIPTS / "audit_claim_discipline.py"
MEMO = ROOT / "refine-logs/THEORY_AND_SEPARATION.md"
ARTIFACT = ROOT / "experiments/dual_sensitivity/phase7_theory_separation.json"


def phase7_payload() -> dict[str, object]:
    from check_theory_separation import build_and_check_phase7_payload

    payload = build_and_check_phase7_payload()
    assert isinstance(payload, dict)
    return payload


def examples_by_name(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    examples = payload["examples"]
    assert isinstance(examples, list)
    return {str(example["name"]): example for example in examples if isinstance(example, dict)}


def run_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def objective_total(components: dict[str, object], weights: dict[str, object]) -> float:
    return sum(float(components[field]) * float(weights[field]) for field in OBJECTIVE_COMPONENT_FIELDS)


def test_slack_recovery_matches_pressure_or_tie() -> None:
    payload = phase7_payload()
    slack = examples_by_name(payload)["slack_recovery"]

    assert "THRY-01" in payload["requirements_covered"]
    assert slack["pressure_action"] == slack["finite_storage_action"] or slack["pressure_action"] in slack.get(
        "finite_storage_tie_set", []
    )
    assert slack["criteria"]["slack_recovery_or_tie"] is True
    assert slack["scope"] == "theory_static_one_step_only_no_closed_loop_claims"


def test_binding_example_separates_actions_with_explicit_state() -> None:
    payload = phase7_payload()
    binding = examples_by_name(payload)["storage_binding_two_phase_separation"]

    assert "THRY-02" in payload["requirements_covered"]
    validate_state_objective_sample(binding)
    assert set(binding["finite_storage_state"]) == FINITE_STORAGE_STATE_FIELDS
    assert set(binding["objective_components"]) == OBJECTIVE_COMPONENT_FIELDS
    assert binding["pressure_action"] != binding["finite_storage_action"]
    assert binding["actions_separate"] is True

    state = binding["finite_storage_state"]
    assert state["residual_receiving_capacity"]["down_a"] == 0.0
    assert state["spillback_blocking"]["down_a"]["spillback"] is True
    assert state["spillback_blocking"]["down_a"]["blocking"] is True
    assert state["residual_receiving_capacity"]["down_b"] > 0.0


def test_binding_example_strictly_improves_predeclared_objective() -> None:
    payload = phase7_payload()
    binding = examples_by_name(payload)["storage_binding_two_phase_separation"]
    objective = payload["one_step_objective_definition"]

    assert "THRY-03" in payload["requirements_covered"]
    assert objective["predeclared_before_action_comparison"] is True
    assert set(objective["components"]) == OBJECTIVE_COMPONENT_FIELDS
    assert set(objective["weights"]) == OBJECTIVE_COMPONENT_FIELDS

    action_components = binding["action_objective_components"]
    pressure_total = objective_total(action_components[binding["pressure_action"]], objective["weights"])
    finite_storage_total = objective_total(action_components[binding["finite_storage_action"]], objective["weights"])

    assert binding["objective_totals"][binding["pressure_action"]] == pressure_total
    assert binding["objective_totals"][binding["finite_storage_action"]] == finite_storage_total
    assert binding["objective_margin"] > 0.0
    assert binding["strict_objective_improvement"] is True
    assert pressure_total > finite_storage_total


def test_phase7_checker_cli_writes_parseable_artifact(tmp_path: Path) -> None:
    out = tmp_path / "phase7_theory_separation.json"

    result = run_checker("--out", str(out))

    assert result.returncode == 0, result.stderr
    payload = read_json(out)
    assert payload["status"] == "PASSED"
    assert payload["requirements_covered"] == ["THRY-01", "THRY-02", "THRY-03", "THRY-04"]
    assert payload["schema_version"] == SCHEMA_VERSION
    assert set(examples_by_name(payload)) == {"slack_recovery", "storage_binding_two_phase_separation"}


def test_checked_in_phase7_artifact_exists_and_validates() -> None:
    assert ARTIFACT.exists()
    payload = read_json(ARTIFACT)

    assert payload["status"] == "PASSED"
    assert payload["requirements_covered"] == ["THRY-01", "THRY-02", "THRY-03", "THRY-04"]
    assert payload["schema_version"] == SCHEMA_VERSION
    for example in payload["examples"]:
        validate_state_objective_sample(example)


def test_memo_requirement_markers_and_claim_safe_language() -> None:
    assert MEMO.exists()
    text = MEMO.read_text(encoding="utf-8")

    for requirement in ["THRY-01", "THRY-02", "THRY-03", "THRY-04"]:
        assert requirement in text
    assert "phase7_theory_separation.json" in text
    assert "lambda_up - lambda_down" in text
    assert "v1.0" in text and "insufficient" in text.lower()
    assert forbidden_claim_hits(text, source=str(MEMO)) == []
    for phrase in FORBIDDEN_CLAIM_PATTERNS:
        assert phrase not in text.lower()


def test_phase7_surfaces_pass_claim_audit(tmp_path: Path) -> None:
    policy_out = tmp_path / "phase7_claim_policy.json"
    audit_out = tmp_path / "phase7_claim_audit.json"
    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--root",
            str(ROOT),
            "--paths",
            "refine-logs/THEORY_AND_SEPARATION.md",
            "experiments/dual_sensitivity/phase7_theory_separation.json",
            "--policy-out",
            str(policy_out),
            "--audit-out",
            str(audit_out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    audit = read_json(audit_out)
    assert audit["status"] == "PASSED"
    assert audit["missing_paths"] == []
    assert audit["forbidden_hits"] == []


def test_guarantee_candidate_is_constrained_lp_oracle_regret() -> None:
    payload = phase7_payload()
    candidates = payload["guarantee_candidates"]

    assert "THRY-04" in payload["requirements_covered"]
    assert candidates == ["constrained_lp_oracle_regret"]
    assert payload["guarantee_candidate_details"]["scope"] == "finite_sample_oracle_relative"

    memo_text = MEMO.read_text(encoding="utf-8")
    assert "constrained LP oracle regret" in memo_text
    assert "finite-sample" in memo_text
    assert "oracle-relative" in memo_text
