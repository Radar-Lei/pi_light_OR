#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_v15_dynamic_primal_dual import build_payload  # noqa: E402
from finite_storage_schema import SCHEMA_VERSION, validate_finite_storage_state  # noqa: E402

SCRIPT = SCRIPTS / "check_v15_dynamic_primal_dual.py"


def cases_by_name(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    cases = payload["cases"]
    assert isinstance(cases, list)
    return {str(case["name"]): case for case in cases if isinstance(case, dict)}


def test_v15_payload_passes_all_deterministic_gates() -> None:
    payload = build_payload()

    assert payload["status"] == "PASSED"
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["controller_id"] == "finite_storage_dynamic_primal_dual_v1_5"
    assert all(payload["criteria"].values())
    assert set(cases_by_name(payload)) == {
        "slack_pressure_recovery",
        "occupancy_storage_separation",
        "cascade_spillback_separation",
        "upstream_release_value",
    }


def test_v15_slack_case_recovers_pressure_with_zero_dual_prices() -> None:
    case = cases_by_name(build_payload())["slack_pressure_recovery"]

    assert case["criteria"]["dynamic_matches_pressure"] is True
    assert case["criteria"]["dual_prices_zero"] is True
    assert case["audit"]["selected_action"] == case["audit"]["pressure_action"]


def test_v15_occupancy_case_separates_queue_and_vehicle_storage() -> None:
    case = cases_by_name(build_payload())["occupancy_storage_separation"]

    validate_finite_storage_state(case["finite_storage_state"])
    assert case["criteria"]["storage_uses_vehicle_count"] is True
    assert case["criteria"]["queue_ablation_misses_storage_fullness"] is True
    assert case["criteria"]["dynamic_matches_occupancy_ablation"] is True
    assert case["dual_state"]["down_a"]["storage_price"] > 0.0


def test_v15_cascade_case_activates_descendant_shadow_price() -> None:
    case = cases_by_name(build_payload())["cascade_spillback_separation"]

    assert case["criteria"]["descendant_storage_price_active"] is True
    assert case["criteria"]["intermediate_cascade_price_active"] is True
    assert case["criteria"]["dynamic_avoids_cascade_path"] is True
    assert "cascade_price" in case["audit"]["changing_terms"]


def test_v15_release_case_serves_upstream_storage_pressure() -> None:
    case = cases_by_name(build_payload())["upstream_release_value"]

    assert case["criteria"]["release_price_active"] is True
    assert case["criteria"]["dynamic_serves_release_movement"] is True
    assert "release" in case["audit"]["changing_terms"]


def test_v15_checker_cli_writes_parseable_artifact(tmp_path: Path) -> None:
    out = tmp_path / "v1_5_dynamic_primal_dual_gates.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["status"] == "PASSED"
    assert payload["controller_id"] == "finite_storage_dynamic_primal_dual_v1_5"
