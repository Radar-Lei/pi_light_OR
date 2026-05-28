#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_v15_closed_loop_diagnostics import CONTROLLER_ID, build_payload, summarize_rows  # noqa: E402

SCRIPT = SCRIPTS / "run_v15_closed_loop_diagnostics.py"


def synthetic_rows() -> list[dict[str, object]]:
    return [
        {
            "scenario_tag": "arterial_spillback_stress",
            "controller": CONTROLLER_ID,
            "seed": 1,
            "action_decomposition": {
                "decision_summary": {
                    "total_decisions": 10,
                    "action_changed_relative_to_pressure_count": 3,
                    "binding_decision_count": 6,
                    "binding_action_changed_count": 3,
                    "action_change_rate": 0.3,
                    "binding_decision_rate": 0.6,
                    "binding_action_change_rate": 0.5,
                    "selected_component_nonzero_counts": {
                        "downstream_storage": 2,
                        "spillback": 2,
                        "switching": 0,
                        "service": 0,
                        "incident": 0,
                        "storage_price": 3,
                        "cascade_price": 1,
                        "release": 1,
                        "service_age": 0,
                    },
                    "any_phase_component_nonzero_counts": {
                        "downstream_storage": 4,
                        "spillback": 3,
                        "switching": 0,
                        "service": 0,
                        "incident": 0,
                        "storage_price": 5,
                        "cascade_price": 2,
                        "release": 1,
                        "service_age": 0,
                    },
                    "max_occupancy_ratio_observed": 0.95,
                    "min_residual_ratio_observed": 0.05,
                }
            },
        }
    ]


def test_v15_closed_loop_diagnostic_summary_passes_with_activation() -> None:
    summary = summarize_rows(synthetic_rows())

    assert summary["total_decisions"] == 10
    assert summary["action_change_rate"] == 0.3
    assert summary["binding_action_change_rate"] == 0.5
    assert all(summary["criteria"].values())
    assert summary["any_phase_component_nonzero_counts"]["storage_price"] == 5


def test_v15_closed_loop_diagnostic_payload_preserves_claim_boundary() -> None:
    payload = build_payload(synthetic_rows(), source="synthetic")

    assert payload["status"] == "PASSED"
    assert payload["controller_id"] == CONTROLLER_ID
    assert "locked_holdout_superiority" in payload["claim_scope"]["not_claimed"]
    assert payload["summary"]["criteria"]["action_change_rate_target_met"] is True


def test_v15_closed_loop_diagnostic_fails_closed_without_action_difference() -> None:
    rows = synthetic_rows()
    summary = rows[0]["action_decomposition"]["decision_summary"]  # type: ignore[index]
    summary["action_changed_relative_to_pressure_count"] = 0  # type: ignore[index]
    summary["binding_action_changed_count"] = 0  # type: ignore[index]
    payload = build_payload(rows, source="synthetic")

    assert payload["status"] == "FAILED"
    assert payload["summary"]["criteria"]["action_change_rate_target_met"] is False


def test_v15_closed_loop_diagnostic_cli_reads_input(tmp_path: Path) -> None:
    input_path = tmp_path / "input.json"
    out_path = tmp_path / "diagnostics.json"
    input_path.write_text(json.dumps({"scenario_results": synthetic_rows()}), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(input_path), "--out", str(out_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASSED"
    assert payload["summary"]["total_decisions"] == 10
