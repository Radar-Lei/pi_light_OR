#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lock_v15_r2_training_protocol import CONTROLLER_ID, build_training_protocol  # noqa: E402
from run_v15_r2_training import build_training_spec, write_training_execution  # noqa: E402


def test_r2_training_spec_marks_rows_as_training_only() -> None:
    protocol = build_training_protocol()
    spec = build_training_spec(protocol)

    assert len(spec) == protocol["training_split"]["expected_row_count"]
    assert {row["controller"] for row in spec} == set(protocol["training_split"]["controllers"])
    assert all(row["evidence_role"] == "v1_5_r2_training_only" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert any(row["controller"] == CONTROLLER_ID for row in spec)


def test_r2_training_dry_run_writes_non_claim_ready_execution(tmp_path: Path) -> None:
    protocol_path = tmp_path / "protocol.json"
    out_path = tmp_path / "training.json"
    protocol = build_training_protocol()
    protocol_path.write_text(json.dumps(protocol, indent=2), encoding="utf-8")

    payload = write_training_execution(
        protocol_path=protocol_path,
        out_path=out_path,
        route_json=ROOT / "experiments/dual_sensitivity/block3_static_kill_gate.json",
        scaled_input_dir=tmp_path / "scaled",
        dry_run=True,
    )

    assert out_path.exists()
    assert payload["experiment"] == "v1_5_r2_training_execution"
    assert payload["status"] == "DRY_RUN"
    assert payload["claim_ready"] is False
    assert payload["expected_row_count"] == protocol["training_split"]["expected_row_count"]
    assert payload["actual_row_count"] == 0
    assert payload["all_rows_executed"] is False
    assert payload["row_audit"]["missing_row_count"] == payload["expected_row_count"]
