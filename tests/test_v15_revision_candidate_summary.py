#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from summarize_v15_revision_candidates import build_summary  # noqa: E402


def test_revision_summary_reports_no_selected_candidate_and_completion_blocker(tmp_path: Path) -> None:
    selection = tmp_path / "selection.json"
    selection.write_text(
        """{
  "experiment": "v1_5_r5_training_selection",
  "status": "REJECTED",
  "claim_ready": false,
  "controller_id": "candidate",
  "decision": "reject_candidate",
  "mechanism_summary": {"action_change_rate": 0.1, "binding_decision_rate": 1.0},
  "primary_composite_training_results": [
    {"baseline": "max_pressure", "paired_difference": 1.0},
    {"baseline": "capacity_aware_pressure", "paired_difference": 2.0},
    {"baseline": "finite_storage_double_pressure", "paired_difference": 3.0}
  ],
  "safety_harms": [{"metric": "unfinished_vehicle_count"}],
  "reasons": ["training rows show safety-guard harm against strong baselines"]
}""",
        encoding="utf-8",
    )

    payload = build_summary([selection])

    assert payload["status"] == "NO_CANDIDATE_SELECTED"
    assert payload["completion_safety_blocker_count"] == 1
    assert payload["dominant_blocker"] == "unfinished_vehicle_count_safety_guard"
    assert payload["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
