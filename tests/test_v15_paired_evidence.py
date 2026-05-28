#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_protocol import CONTROLLER_ID, REQUIRED_BASELINES, build_protocol  # noqa: E402
from run_v15_paired_evidence import build_evidence_payload, composite_cost  # noqa: E402

SCRIPT = SCRIPTS / "run_v15_paired_evidence.py"


def row(controller: str, seed: int, *, good: bool) -> dict[str, object]:
    value = 5.0 if good else 10.0
    return {
        "scenario_tag": "arterial_spillback_stress",
        "demand_multiplier": 1.0,
        "controller": controller,
        "seed": seed,
        "scenario_status": "completed",
        "feasibility_status": "run",
        "objective_components": {
            "delay": value,
            "unfinished_vehicle_penalty": value,
            "spillback_blocking_time": value,
            "switching_lost_time": value,
        },
        "penalized_avg_travel_time": value,
        "total_delay": value,
        "unfinished_vehicle_count": 0.0 if good else 1.0,
    }


def synthetic_execution(*, proposed_good: bool = True, status: str = "COMPLETE_PENDING_PAIRED_EVIDENCE") -> dict[str, object]:
    protocol = build_protocol()
    rows = []
    for seed in [1, 2, 3]:
        rows.append(row(CONTROLLER_ID, seed, good=proposed_good))
        for baseline in REQUIRED_BASELINES:
            rows.append(row(baseline, seed, good=not proposed_good))
    return {
        "experiment": "v1_5_locked_holdout_execution",
        "status": status,
        "locked_protocol_status": "LOCKED",
        "locked_protocol_fingerprint": protocol["protocol_fingerprint"],
        "controller_id": CONTROLLER_ID,
        "required_baselines": REQUIRED_BASELINES,
        "primary_endpoint": protocol["primary_endpoint"],
        "safety_guards": protocol["safety_guards"],
        "dry_run": False,
        "all_rows_executed": True,
        "row_audit": {"missing_row_count": 0, "failed_row_count": 0, "duplicate_row_count": 0},
        "scenario_results": rows,
    }


def test_composite_cost_uses_protocol_weights() -> None:
    protocol = build_protocol()
    assert composite_cost(row(CONTROLLER_ID, 1, good=True), protocol["primary_endpoint"]["weights"]) == 20.0


def test_v15_paired_evidence_passes_for_strict_composite_improvement() -> None:
    payload = build_evidence_payload(synthetic_execution(proposed_good=True), Path("synthetic.json"))

    assert payload["status"] == "PASSED"
    assert payload["claim_ready"] is True
    assert payload["primary_composite_results"]
    assert all(result["classification"] == "strict_positive" for result in payload["primary_composite_results"])
    assert all(result["passed"] for result in payload["safety_guard_results"])


def test_v15_paired_evidence_fails_for_bounded_harm() -> None:
    payload = build_evidence_payload(synthetic_execution(proposed_good=False), Path("synthetic.json"))

    assert payload["status"] == "FAILED"
    assert payload["claim_ready"] is False
    assert any(result["classification"] == "bounded_harm" for result in payload["primary_composite_results"])


def test_v15_paired_evidence_inconclusive_for_dry_run_input(tmp_path: Path) -> None:
    execution = synthetic_execution()
    execution["dry_run"] = True
    execution["status"] = "PILOT_ONLY"
    execution["all_rows_executed"] = False
    execution["row_audit"] = {"missing_row_count": 1, "failed_row_count": 0, "duplicate_row_count": 0}
    input_path = tmp_path / "execution.json"
    out_path = tmp_path / "evidence.json"
    input_path.write_text(json.dumps(execution, indent=2), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input", str(input_path), "--out", str(out_path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["status"] == "INCONCLUSIVE"
    assert payload["claim_ready"] is False
    assert any("dry-run" in reason for reason in payload["reasons"])
