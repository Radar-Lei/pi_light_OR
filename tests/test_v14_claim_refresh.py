from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_v14_claim_refresh import (  # noqa: E402
    SOURCE_REGISTRY,
    audit_generated_outputs,
    build_milestone_audit,
    build_v14_package,
    closed_loop_superiority_claim_allowed,
    load_source_records,
    write_v14_artifacts,
)


def test_v14_claim_refresh_keeps_claim_disallowed_for_inconclusive_gate(tmp_path: Path) -> None:
    payloads = build_v14_package(tmp_path)
    paths = write_v14_artifacts(tmp_path, payloads)

    assert payloads["package"]["status"] == "INCONCLUSIVE"
    assert payloads["package"]["strict_gate_c_status"] == "INCONCLUSIVE"
    assert payloads["package"]["closed_loop_superiority_claim_allowed"] is False
    assert payloads["claim_audit"]["status"] == "PASSED"
    assert payloads["milestone_audit"]["status"] == "PASSED"
    assert paths["package"].exists()
    assert paths["table"].read_text(encoding="utf-8").startswith("source_key,")


def test_claim_allowed_only_when_strict_gate_c_passes() -> None:
    records = load_source_records()
    assert closed_loop_superiority_claim_allowed(records) is False
    gate_record = next(record for record in records if record["source_key"] == "v1_4_gate_c_paired_evidence")
    gate_record["payload"]["status"] = "PASSED"
    gate_record["source_status"] = "PASSED"
    assert closed_loop_superiority_claim_allowed(records) is True


def test_claim_audit_flags_overclaim_when_gate_is_not_passed() -> None:
    audit = audit_generated_outputs(
        {"bad.json": json.dumps({"closed_loop_superiority_claim_allowed": True, "claim_allowed": True})},
        "INCONCLUSIVE",
    )
    assert audit["status"] == "FAILED"
    assert audit["hit_count"] >= 1


def test_milestone_audit_detects_protocol_drift() -> None:
    records = load_source_records()
    claim_inputs = build_v14_package(Path("unused"))["claim_inputs"]
    claim_audit = {"status": "PASSED"}
    execution = next(record for record in records if record["source_key"] == "v1_4_locked_gate_c_execution")
    execution["payload"]["locked_protocol_fingerprint"] = "drifted"
    audit = build_milestone_audit(records, claim_inputs, claim_audit)
    assert audit["status"] == "FAILED"
    assert audit["protocol_drift_findings"]


def test_source_registry_paths_are_v1_4_specific() -> None:
    assert set(SOURCE_REGISTRY) == {
        "v1_4_failure_diagnostics",
        "v1_4_workstream_pilot_index",
        "v1_4_candidate_convergence",
        "v1_4_locked_gate_c_protocol",
        "v1_4_locked_gate_c_execution",
        "v1_4_gate_c_paired_evidence",
    }
    assert all("v1_4" in entry["path"] for entry in SOURCE_REGISTRY.values())
