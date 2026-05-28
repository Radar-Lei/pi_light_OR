#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from finite_storage_schema import OBJECTIVE_COMPONENT_FIELDS  # noqa: E402
from lock_v15_protocol import CONTROLLER_ID, REQUIRED_BASELINES, build_protocol, stable_fingerprint  # noqa: E402

SCRIPT = SCRIPTS / "lock_v15_protocol.py"


def test_v15_protocol_locks_controller_baselines_and_holdout_count() -> None:
    protocol = build_protocol()
    holdout = protocol["locked_holdout"]

    assert protocol["status"] == "LOCKED"
    assert protocol["controller_id"] == CONTROLLER_ID
    assert protocol["required_baselines"] == REQUIRED_BASELINES
    assert set(holdout["controllers"]) == {CONTROLLER_ID, *REQUIRED_BASELINES}
    assert holdout["expected_row_count"] == (
        len(holdout["scenarios"])
        * len(holdout["seeds"])
        * len(holdout["demand_multipliers"])
        * len(holdout["controllers"])
    )


def test_v15_protocol_primary_endpoint_is_composite_cost() -> None:
    protocol = build_protocol()
    endpoint = protocol["primary_endpoint"]

    assert endpoint["name"] == "composite_finite_storage_operating_cost"
    assert set(endpoint["components"]) == OBJECTIVE_COMPONENT_FIELDS
    assert set(endpoint["weights"]) == OBJECTIVE_COMPONENT_FIELDS
    assert endpoint["paired_seed_comparison"] is True
    assert "unfinished_vehicle_penalty" in endpoint["formula"]
    assert protocol["failure_rules"]["closed_loop_superiority_allowed_only_if_locked_holdout_passes"] is True


def test_v15_protocol_fingerprint_is_stable_over_core_contract() -> None:
    protocol = build_protocol()
    core = {
        key: value
        for key, value in protocol.items()
        if key
        not in {
            "experiment",
            "status",
            "generated_by",
            "generated_at",
            "requirements_covered",
            "protocol_fingerprint",
            "claim_scope",
        }
    }

    assert protocol["protocol_fingerprint"] == stable_fingerprint(core)
    assert len(protocol["protocol_fingerprint"]) == 64


def test_v15_protocol_cli_writes_parseable_artifact(tmp_path: Path) -> None:
    out = tmp_path / "v1_5_locked_protocol.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    protocol = json.loads(out.read_text(encoding="utf-8"))
    assert protocol["status"] == "LOCKED"
    assert protocol["controller_id"] == CONTROLLER_ID
    assert protocol["claim_scope"]["not_claimed"]
