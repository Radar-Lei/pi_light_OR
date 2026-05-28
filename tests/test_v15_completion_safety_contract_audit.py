#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_v15_completion_safety_contract import build_audit, write_audit  # noqa: E402


def write_selection(
    path: Path,
    *,
    status: str = "REJECTED",
    controller_id: str,
    action_change_rate: float,
    core_means: dict[str, float],
    harms: list[dict[str, float | str]],
) -> None:
    path.write_text(
        json.dumps(
            {
                "experiment": path.stem,
                "status": status,
                "claim_ready": False,
                "controller_id": controller_id,
                "decision": f"reject_{controller_id}",
                "mechanism_summary": {"action_change_rate": action_change_rate},
                "core_composite_mean_differences": core_means,
                "safety_harms": harms,
                "reasons": ["training rows show safety-guard harm against strong baselines"] if harms else [],
            }
        ),
        encoding="utf-8",
    )


def test_contract_audit_rejects_revision_when_positive_candidates_still_have_completion_harm(tmp_path: Path) -> None:
    positive = tmp_path / "positive.json"
    low_sep = tmp_path / "low_sep.json"
    write_selection(
        positive,
        controller_id="finite_storage_dynamic_primal_dual_v1_5_r19_horizon_double_anchored",
        action_change_rate=0.14,
        core_means={"max_pressure": 10.0, "capacity_aware_pressure": 9.0, "finite_storage_double_pressure": 8.0},
        harms=[
            {
                "baseline": "max_pressure",
                "metric": "unfinished_vehicle_count",
                "r2": 122.0,
                "allowed": 121.0,
            }
        ],
    )
    write_selection(
        low_sep,
        controller_id="finite_storage_dynamic_primal_dual_v1_5_r22_horizon_completion_safety",
        action_change_rate=0.03,
        core_means={"max_pressure": -1.0, "capacity_aware_pressure": -1.0, "finite_storage_double_pressure": -1.0},
        harms=[],
    )

    audit = build_audit([positive, low_sep])

    assert audit["status"] == "REVISION_REQUIRED"
    assert audit["positive_core_composite_candidate_count"] == 1
    assert audit["positive_core_safety_guard_pass_count"] == 0
    assert audit["near_miss_count"] == 1
    assert audit["contract_assessment"]["completion_safety_guard_passed"] is False
    assert audit["contract_assessment"]["formal_contract_revision_supported_by_current_evidence"] is False
    assert audit["claim_scope"]["confirmatory_holdout_allowed"] is False


def test_contract_audit_marks_guard_pass_without_claim_ready(tmp_path: Path) -> None:
    passing = tmp_path / "passing.json"
    write_selection(
        passing,
        status="INCONCLUSIVE",
        controller_id="finite_storage_dynamic_primal_dual_v1_5_candidate",
        action_change_rate=0.12,
        core_means={"max_pressure": 5.0, "capacity_aware_pressure": 4.0, "finite_storage_double_pressure": 3.0},
        harms=[],
    )
    out = tmp_path / "audit.json"

    audit = write_audit([passing], out)

    assert audit["status"] == "GUARD_PASSED_PENDING_FULL_TRAINING_SELECTION"
    assert audit["claim_ready"] is False
    assert audit["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert out.exists()
