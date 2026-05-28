#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_protocol import CONTROLLER_ID, REQUIRED_BASELINES, build_protocol  # noqa: E402
from run_v15_locked_holdout import build_locked_spec, build_row_audit, write_locked_execution  # noqa: E402


def test_v15_locked_holdout_spec_matches_protocol_count_and_controllers() -> None:
    protocol = build_protocol()
    spec = build_locked_spec(protocol)
    holdout = protocol["locked_holdout"]

    assert len(spec) == holdout["expected_row_count"]
    assert {row["controller"] for row in spec} == {CONTROLLER_ID, *REQUIRED_BASELINES}
    assert {row["scenario_tag"] for row in spec} == set(holdout["scenarios"])
    assert {float(row["demand_multiplier"]) for row in spec} == set(holdout["demand_multipliers"])


def test_v15_row_audit_reports_missing_and_duplicates() -> None:
    protocol = build_protocol()
    spec = build_locked_spec(protocol)[:3]
    rows = [
        {
            **spec[0],
            "scenario_status": "completed",
            "feasibility_status": "run",
        },
        {
            **spec[0],
            "scenario_status": "completed",
            "feasibility_status": "run",
        },
        {
            **spec[1],
            "scenario_status": "not_run",
            "feasibility_status": "not_run",
            "placeholder_reason": "test",
        },
    ]

    audit = build_row_audit(rows, spec)
    assert audit["completed_row_count"] == 2
    assert audit["duplicate_row_count"] == 1
    assert audit["failed_row_count"] == 1
    assert audit["missing_row_count"] >= 1


def test_v15_locked_holdout_dry_run_writes_fail_closed_execution(tmp_path: Path) -> None:
    protocol_path = tmp_path / "protocol.json"
    out_path = tmp_path / "holdout.json"
    protocol = build_protocol()
    protocol_path.write_text(__import__("json").dumps(protocol, indent=2), encoding="utf-8")

    payload = write_locked_execution(
        protocol_path=protocol_path,
        out_path=out_path,
        route_json=ROOT / "experiments/dual_sensitivity/block3_static_kill_gate.json",
        scaled_input_dir=tmp_path / "scaled",
        dry_run=True,
    )

    assert out_path.exists()
    assert payload["experiment"] == "v1_5_locked_holdout_execution"
    assert payload["status"] == "PILOT_ONLY"
    assert payload["claim_ready"] is False
    assert payload["expected_row_count"] == protocol["locked_holdout"]["expected_row_count"]
    assert payload["actual_row_count"] == 0
    assert payload["all_rows_executed"] is False
    assert payload["row_audit"]["missing_row_count"] == payload["expected_row_count"]


def test_v15_locked_holdout_incremental_execution_preserves_progress_fingerprint(tmp_path: Path, monkeypatch) -> None:
    protocol_path = tmp_path / "protocol.json"
    out_path = tmp_path / "holdout.json"
    progress_path = tmp_path / "progress.json"
    protocol = build_protocol()
    protocol_path.write_text(__import__("json").dumps(protocol, indent=2), encoding="utf-8")

    def fake_run_experiment(network, controller, seed, steps, warmup, action_interval, route_metadata, scenario_tag, sumocfg_override=None):
        return {
            "network": network,
            "scenario_tag": scenario_tag,
            "controller": controller,
            "seed": seed,
            "steps": steps,
            "warmup": warmup,
            "action_interval": action_interval,
            "scenario_status": "completed",
            "feasibility_status": "run",
            "objective_components": {
                "delay": 1.0,
                "unfinished_vehicle_penalty": 0.0,
                "spillback_blocking_time": 0.0,
                "switching_lost_time": 0.0,
            },
            "penalized_avg_travel_time": 1.0,
            "total_delay": 1.0,
            "unfinished_vehicle_count": 0,
            "finite_storage_state": {},
        }

    monkeypatch.setattr("run_phase11_paired_evidence.run_experiment", fake_run_experiment)
    payload = write_locked_execution(
        protocol_path=protocol_path,
        out_path=out_path,
        route_json=ROOT / "experiments/dual_sensitivity/block3_static_kill_gate.json",
        scaled_input_dir=tmp_path / "scaled",
        execution_row_limit=protocol["locked_holdout"]["expected_row_count"],
        progress_out=progress_path,
        max_new_rows=2,
    )
    progress = __import__("json").loads(progress_path.read_text(encoding="utf-8"))

    assert payload["status"] == "INCONCLUSIVE"
    assert payload["actual_row_count"] == 2
    assert payload["max_new_rows"] == 2
    assert payload["execution_mode"] == "executed_incremental_with_progress"
    assert progress["expected_row_count"] == protocol["locked_holdout"]["expected_row_count"]
    assert progress["completed_row_count"] == 2
