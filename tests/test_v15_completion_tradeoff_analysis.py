#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from analyze_v15_completion_tradeoffs import build_analysis, write_analysis  # noqa: E402


def row(controller: str, unfinished: int, cost: float) -> dict[str, object]:
    return {
        "scenario_status": "completed",
        "feasibility_status": "run",
        "scenario_tag": "arterial_v1_5_storage_activation",
        "seed": 1,
        "demand_multiplier": 0.85,
        "controller": controller,
        "unfinished_vehicle_count": unfinished,
        "objective_components": {"delay": cost},
    }


def write_execution(path: Path) -> None:
    controller = "finite_storage_dynamic_primal_dual_v1_5_candidate"
    path.write_text(
        json.dumps(
            {
                "experiment": path.stem,
                "controller_id": controller,
                "scenario_results": [
                    row(controller, 121, 90.0),
                    row("max_pressure", 120, 100.0),
                    row("capacity_aware_pressure", 122, 80.0),
                    row("finite_storage_double_pressure", 125, 110.0),
                ],
            }
        ),
        encoding="utf-8",
    )


def test_tradeoff_analysis_detects_safety_and_oracle_conflicts(tmp_path: Path) -> None:
    execution = tmp_path / "v1_5_r99_training_execution.json"
    write_execution(execution)

    payload = build_analysis([execution])

    assert payload["status"] == "ANALYZED"
    assert payload["case_count"] == 1
    assert payload["unsafe_case_count"] == 1
    assert payload["composite_win_case_count"] == 0
    assert payload["oracle_conflict_count"] == 1
    case = payload["executions"][0]["cases"][0]
    assert case["candidate_safety_excess_vs_best_core"] == 1.0
    assert case["core_unfinished_oracle"] == "max_pressure"
    assert case["core_composite_oracle"] == "capacity_aware_pressure"
    assert payload["claim_scope"]["closed_loop_superiority_claim_allowed"] is False


def test_tradeoff_analysis_writes_artifact(tmp_path: Path) -> None:
    execution = tmp_path / "v1_5_r99_training_execution.json"
    out = tmp_path / "analysis.json"
    write_execution(execution)

    payload = write_analysis([execution], out)

    assert payload["input_count"] == 1
    assert out.exists()
