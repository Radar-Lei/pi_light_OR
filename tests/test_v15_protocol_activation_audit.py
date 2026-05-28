#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_v15_protocol_activation import build_audit  # noqa: E402
from lock_v15_binding_protocol import BINDING_HOLDOUT_SCENARIOS, build_binding_protocol  # noqa: E402
from lock_v15_protocol import CONTROLLER_ID  # noqa: E402
from run_v15_locked_holdout import build_locked_spec  # noqa: E402


def execution_with_summary(summary: dict[str, object]) -> dict[str, object]:
    return {
        "status": "INCONCLUSIVE",
        "locked_protocol_fingerprint": "synthetic",
        "controller_id": CONTROLLER_ID,
        "scenario_results": [
            {
                "scenario_tag": "arterial_downstream_blockage",
                "demand_multiplier": 0.9,
                "seed": 1,
                "controller": CONTROLLER_ID,
                "scenario_status": "completed",
                "feasibility_status": "run",
                "action_decomposition": {"decision_summary": summary},
            }
        ],
    }


def test_activation_audit_fails_when_holdout_rows_do_not_bind() -> None:
    audit = build_audit(
        execution_with_summary(
            {
                "total_decisions": 10,
                "binding_decision_count": 0,
                "action_changed_relative_to_pressure_count": 2,
                "any_phase_component_nonzero_counts": {"storage_price": 0, "cascade_price": 0, "release": 0},
            }
        ),
        Path("synthetic.json"),
    )

    assert audit["status"] == "FAILED"
    assert "supersede" in audit["recommendation"]
    assert any("binding" in reason for reason in audit["reasons"])


def test_activation_audit_passes_when_dynamic_storage_terms_activate() -> None:
    audit = build_audit(
        execution_with_summary(
            {
                "total_decisions": 10,
                "binding_decision_count": 5,
                "action_changed_relative_to_pressure_count": 4,
                "any_phase_component_nonzero_counts": {"storage_price": 5, "cascade_price": 3, "release": 0},
            }
        ),
        Path("synthetic.json"),
    )

    assert audit["status"] == "PASSED"
    assert audit["summary"]["binding_decision_rate"] == 0.5


def test_binding_protocol_supersedes_nonbinding_holdout_and_changes_scenarios() -> None:
    protocol = build_binding_protocol()
    spec = build_locked_spec(protocol)

    assert protocol["experiment"] == "v1_5_binding_locked_protocol"
    assert protocol["supersedes_protocol"].endswith("v1_5_locked_protocol.json")
    assert set(protocol["locked_holdout"]["scenarios"]) == set(BINDING_HOLDOUT_SCENARIOS)
    assert "arterial_v1_5_storage_activation" in protocol["locked_holdout"]["scenarios"]
    assert len(spec) == protocol["locked_holdout"]["expected_row_count"]
