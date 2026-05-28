#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r2_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_v15_r2_training_selection import build_selection_payload  # noqa: E402


def row(controller: str, *, unfinished: int = 0, changed: int = 100, delay: float = 10.0) -> dict[str, object]:
    return {
        "scenario_tag": "arterial_v1_5_storage_activation",
        "demand_multiplier": 0.85,
        "controller": controller,
        "seed": 20260801,
        "scenario_status": "completed",
        "feasibility_status": "run",
        "objective_components": {
            "delay": delay,
            "unfinished_vehicle_penalty": float(unfinished * 2700),
            "spillback_blocking_time": 10.0,
            "switching_lost_time": 10.0,
        },
        "penalized_avg_travel_time": 10.0,
        "total_delay": 10.0,
        "unfinished_vehicle_count": unfinished,
        "action_decomposition": {
            "decision_summary": {
                "total_decisions": 1000,
                "action_changed_relative_to_pressure_count": changed,
                "binding_decision_count": 900,
                "any_phase_component_nonzero_counts": {"guardrail": 500},
            }
        },
    }


def execution_payload(*, r2_unfinished: int = 1, changed: int = 10) -> dict[str, object]:
    protocol = build_training_protocol()
    rows = [row(CONTROLLER_ID, unfinished=r2_unfinished, changed=changed)]
    for baseline in protocol["required_baselines"]:
        rows.append(row(baseline, unfinished=0, changed=0))
    return {
        "experiment": "v1_5_r2_training_execution",
        "status": "IN_PROGRESS",
        "claim_ready": False,
        "training_protocol_fingerprint": protocol["protocol_fingerprint"],
        "controller_id": CONTROLLER_ID,
        "required_baselines": protocol["required_baselines"],
        "all_rows_executed": False,
        "row_audit": {"completed_row_count": len(rows), "missing_row_count": 1},
        "scenario_results": rows,
    }


def test_training_selection_rejects_core_safety_harm_and_low_action_separation() -> None:
    payload = build_selection_payload(execution_payload(), Path("training.json"))

    assert payload["status"] == "REJECTED"
    assert payload["decision"] == f"reject_{CONTROLLER_ID}"
    assert payload["claim_ready"] is False
    assert any("safety-guard harm" in reason for reason in payload["reasons"])
    assert any("below 5%" in reason for reason in payload["reasons"])


def test_training_selection_can_continue_when_partial_rows_have_no_rejection_signal() -> None:
    payload = build_selection_payload(execution_payload(r2_unfinished=0, changed=100), Path("training.json"))

    assert payload["status"] == "INCONCLUSIVE"
    assert payload["decision"] == "continue_training_execution"


def test_training_selection_rejects_full_training_without_positive_core_composite() -> None:
    payload = execution_payload(r2_unfinished=0, changed=100)
    payload["all_rows_executed"] = True

    selected = build_selection_payload(payload, Path("training.json"))

    assert selected["status"] == "REJECTED"
    assert any("composite signal is not positive" in reason for reason in selected["reasons"])
