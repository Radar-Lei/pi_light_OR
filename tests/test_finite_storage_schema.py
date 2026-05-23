#!/usr/bin/env python3
"""Behavior checks for explicit finite-storage state and objective schema."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from finite_storage_schema import (  # noqa: E402
    FINITE_STORAGE_STATE_FIELDS,
    OBJECTIVE_COMPONENT_FIELDS,
    build_objective_components_from_metrics,
    schema_artifact_payload,
    validate_finite_storage_state,
    validate_objective_components,
    validate_state_objective_sample,
)

GENERATOR = SCRIPTS / "generate_static_regime_states.py"

EXPECTED_STATE_FIELDS = {
    "downstream_storage",
    "residual_receiving_capacity",
    "spillback_blocking",
    "switching_loss_state",
    "service_urgency",
    "incident_capacity_drop",
}
EXPECTED_OBJECTIVE_FIELDS = {
    "delay",
    "unfinished_vehicle_penalty",
    "spillback_blocking_time",
    "switching_lost_time",
}


def explicit_state() -> dict[str, Any]:
    return {
        "downstream_storage": {"edge_a": 10.0, "edge_b": 8.0},
        "residual_receiving_capacity": {"edge_a": 7.0, "edge_b": 1.0},
        "spillback_blocking": {
            "edge_a": {"spillback": False, "blocking": False, "occupancy_ratio": 0.3},
            "edge_b": {"spillback": True, "blocking": True, "occupancy_ratio": 0.9},
        },
        "switching_loss_state": {"current_phase": 1, "time_since_switch": 5.0},
        "service_urgency": {"edge_a": 3.0, "edge_b": 9.0},
        "incident_capacity_drop": {"active": True, "edge": "edge_b", "factor": 0.5},
    }


def explicit_objective() -> dict[str, float]:
    return {
        "delay": 12.0,
        "unfinished_vehicle_penalty": 3.0,
        "spillback_blocking_time": 2.0,
        "switching_lost_time": 4.0,
    }


def run_generator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GENERATOR), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_explicit_finite_storage_state_required_fields() -> None:
    assert FINITE_STORAGE_STATE_FIELDS == EXPECTED_STATE_FIELDS
    validate_finite_storage_state(explicit_state(), path=Path("fixture.json"), sample_idx=0)

    for missing_field in EXPECTED_STATE_FIELDS:
        invalid = explicit_state()
        invalid.pop(missing_field)
        try:
            validate_finite_storage_state(invalid, path=Path("fixture.json"), sample_idx=7)
        except ValueError as exc:
            message = str(exc)
            assert missing_field in message
            assert "fixture.json" in message
            assert "Sample 7" in message
        else:  # pragma: no cover - exercised only when implementation is broken
            raise AssertionError(f"missing {missing_field} was accepted")

    proxy_only = {"regime": "storage_binding_proxy", "proxy_reason": "high downstream occupancy"}
    try:
        validate_state_objective_sample(proxy_only, path=Path("proxy.json"), sample_idx=2)
    except ValueError as exc:
        assert "finite_storage_state" in str(exc)
        assert "proxy.json" in str(exc)
        assert "Sample 2" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("proxy-only sample was accepted as explicit finite-storage evidence")


def test_objective_components_required_keys() -> None:
    assert OBJECTIVE_COMPONENT_FIELDS == EXPECTED_OBJECTIVE_FIELDS
    validate_objective_components(explicit_objective(), path=Path("fixture.json"), sample_idx=1)

    for missing_field in EXPECTED_OBJECTIVE_FIELDS:
        invalid = explicit_objective()
        invalid.pop(missing_field)
        try:
            validate_objective_components(invalid, path=Path("fixture.json"), sample_idx=5)
        except ValueError as exc:
            message = str(exc)
            assert missing_field in message
            assert "fixture.json" in message
            assert "Sample 5" in message
        else:  # pragma: no cover
            raise AssertionError(f"missing {missing_field} was accepted")

    invalid_numeric = explicit_objective()
    invalid_numeric["switching_lost_time"] = float("inf")
    try:
        validate_objective_components(invalid_numeric, path=Path("objective.json"), sample_idx=3)
    except ValueError as exc:
        message = str(exc)
        assert "switching_lost_time" in message
        assert "finite number" in message
    else:  # pragma: no cover
        raise AssertionError("non-finite objective component was accepted")


def test_objective_components_from_metrics_contract() -> None:
    static_components = build_objective_components_from_metrics(
        {
            "total_delay": 11.5,
            "unfinished_vehicles": 2,
            "spillback_count": 3,
            "blocking_count": 4,
            "switching_count": 2,
        },
        horizon=10.0,
        switching_lost_time_per_switch=1.5,
    )
    closed_loop_components = build_objective_components_from_metrics(
        {
            "delay": 8.0,
            "unfinished_vehicle_count": 1,
            "spillback_blocking_count": 5,
            "switching_count": 3,
        },
        horizon=20.0,
        switching_lost_time_per_switch=2.0,
    )

    assert set(static_components) == EXPECTED_OBJECTIVE_FIELDS
    assert set(closed_loop_components) == EXPECTED_OBJECTIVE_FIELDS
    assert static_components["delay"] == 11.5
    assert static_components["unfinished_vehicle_penalty"] == 20.0
    assert static_components["spillback_blocking_time"] == 70.0
    assert static_components["switching_lost_time"] == 3.0
    assert closed_loop_components["delay"] == 8.0
    assert closed_loop_components["unfinished_vehicle_penalty"] == 20.0
    assert closed_loop_components["spillback_blocking_time"] == 100.0
    assert closed_loop_components["switching_lost_time"] == 6.0


def test_phase6_fixture_generation_and_validation(tmp_path: Path) -> None:
    out = tmp_path / "phase6_state_objective_fixtures.json"
    schema_out = tmp_path / "phase6_explicit_state_schema.json"
    result = run_generator(
        "--target-per-regime",
        "3",
        "--out",
        str(out),
        "--schema-out",
        str(schema_out),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    schema = json.loads(schema_out.read_text(encoding="utf-8"))

    assert payload["status"] == "PASSED"
    assert payload["experiment"] == "phase6_state_objective_fixtures"
    assert payload["generated_by"].startswith("generate_static_regime_states.py")
    assert payload["schema_version"] == "phase6_explicit_state_v1"
    assert {"STATE-01", "STATE-02"} <= set(payload["requirements_covered"])
    assert payload["objective_formula_metadata"]["shared_builder"] == "build_objective_components_from_metrics"
    assert "historical/insufficient" in payload["legacy_proxy_note"]
    assert payload["num_samples"] == len(payload["samples"])
    assert payload["samples"]
    assert schema["status"] == "PASSED"
    assert {"STATE-01", "STATE-02"} <= set(schema["requirements_covered"])
    assert set(schema["finite_storage_state_fields"]) == EXPECTED_STATE_FIELDS
    assert set(schema["objective_component_fields"]) == EXPECTED_OBJECTIVE_FIELDS
    assert schema["objective_formula_metadata"]["shared_builder"] == "build_objective_components_from_metrics"

    for idx, sample in enumerate(payload["samples"]):
        validate_state_objective_sample(sample, path=out, sample_idx=idx)
        assert set(sample["finite_storage_state"]) == EXPECTED_STATE_FIELDS
        assert set(sample["objective_components"]) == EXPECTED_OBJECTIVE_FIELDS


def test_schema_artifact_payload_documents_state_and_objective_contracts() -> None:
    payload = schema_artifact_payload()

    assert payload["experiment"] == "phase6_explicit_state_schema"
    assert payload["status"] == "PASSED"
    assert {"STATE-01", "STATE-02"} <= set(payload["requirements_covered"])
    assert set(payload["finite_storage_state_fields"]) == EXPECTED_STATE_FIELDS
    assert set(payload["objective_component_fields"]) == EXPECTED_OBJECTIVE_FIELDS
    assert payload["objective_formula_metadata"]["shared_builder"] == "build_objective_components_from_metrics"
    assert "historical/insufficient" in payload["legacy_proxy_note"]


def test_validation_error_messages_include_field_path_and_sample_index() -> None:
    state = explicit_state()
    del state["downstream_storage"]
    try:
        validate_finite_storage_state(state, path=Path("fixtures.json"), sample_idx=4)
    except ValueError as exc:
        message = str(exc)
        assert "downstream_storage" in message
        assert "fixtures.json" in message
        assert "Sample 4" in message
    else:  # pragma: no cover
        raise AssertionError("missing downstream_storage was accepted")

    components = explicit_objective()
    del components["switching_lost_time"]
    try:
        validate_objective_components(components, path=Path("objectives.json"), sample_idx=9)
    except ValueError as exc:
        message = str(exc)
        assert "switching_lost_time" in message
        assert "objectives.json" in message
        assert "Sample 9" in message
    else:  # pragma: no cover
        raise AssertionError("missing switching_lost_time was accepted")


def main() -> None:
    test_explicit_finite_storage_state_required_fields()
    test_objective_components_required_keys()
    test_objective_components_from_metrics_contract()
    with tempfile.TemporaryDirectory() as raw_tmp:
        test_phase6_fixture_generation_and_validation(Path(raw_tmp))
    test_schema_artifact_payload_documents_state_and_objective_contracts()
    test_validation_error_messages_include_field_path_and_sample_index()
    print("finite-storage schema tests ok")


if __name__ == "__main__":
    main()
