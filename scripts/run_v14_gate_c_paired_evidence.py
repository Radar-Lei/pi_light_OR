#!/usr/bin/env python3
"""Strict v1.4 Gate C checker for locked confirmation artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_phase11_paired_evidence as phase11
from run_gate_c_paired_evidence import _demand_multiplier_provenance_summary, _extract_rule

DEFAULT_INPUT = "experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json"
REQUIREMENTS_COVERED = ["LOCK-02", "LOCK-04"]
VALID_STATUSES = {"PASSED", "FAILED", "INCONCLUSIVE"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def load_input_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Input artifact {path} must contain a JSON object")
    phase11.validate_payload_scope(payload)
    return payload


def _profile_eligibility(payload: dict[str, Any]) -> dict[str, Any]:
    rows = list(payload.get("scenario_results", []))
    completed_rows = phase11._completed_rows(rows)
    actual_row_count = int(payload.get("actual_row_count", len(completed_rows)) or 0)
    expected_row_count = int(payload.get("expected_row_count", 0) or 0)
    reasons = []
    if payload.get("experiment") != "v1_4_locked_gate_c_execution":
        reasons.append("input artifact is not v1_4_locked_gate_c_execution")
    if payload.get("locked_protocol_status") != "LOCKED":
        reasons.append("locked protocol status is not LOCKED")
    if payload.get("profile") != "main":
        reasons.append("v1.4 Gate C requires main profile")
    if int(payload.get("steps", 0) or 0) < 3600:
        reasons.append("v1.4 Gate C requires at least 3600 steps")
    if int(payload.get("warmup", 0) or 0) < 900:
        reasons.append("v1.4 Gate C requires at least 900 warmup steps")
    if payload.get("dry_run"):
        reasons.append("dry-run/spec-only artifacts cannot complete v1.4 Gate C")
    if actual_row_count == 0:
        reasons.append("input artifact has no executed raw scenario rows")
    if payload.get("all_rows_executed") is not True:
        reasons.append("input artifact reports missing required executed rows")
    if actual_row_count != len(completed_rows):
        reasons.append("input artifact actual_row_count does not match completed raw scenario rows")
    if expected_row_count <= 0:
        reasons.append("input artifact is missing a positive expected_row_count")
    elif actual_row_count != expected_row_count:
        reasons.append("input artifact actual_row_count does not match expected_row_count")
    row_audit = payload.get("row_audit", {}) if isinstance(payload.get("row_audit"), dict) else {}
    for key in ["duplicate_row_count", "unpaired_group_count", "bad_provenance_row_count", "schema_invalid_row_count"]:
        if int(row_audit.get(key, 0) or 0) > 0:
            reasons.append(f"row audit reports {key}={row_audit.get(key)}")
    return {
        "eligible": not reasons,
        "profile": payload.get("profile"),
        "steps": int(payload.get("steps", 0) or 0),
        "warmup": int(payload.get("warmup", 0) or 0),
        "dry_run": bool(payload.get("dry_run")),
        "actual_row_count": actual_row_count,
        "expected_row_count": expected_row_count,
        "completed_row_count": len(completed_rows),
        "all_rows_executed": payload.get("all_rows_executed") is True,
        "reasons": reasons,
    }


def build_gate_payload(input_payload: dict[str, Any], input_artifact: Path) -> dict[str, Any]:
    selected = str(input_payload.get("selected_controller_id") or "")
    if selected:
        phase11.set_proposed_controller(selected)
    rows = list(input_payload.get("scenario_results", []))
    gate_input = {
        "profile": input_payload.get("profile"),
        "steps": input_payload.get("steps", 0),
        "warmup": input_payload.get("warmup", 0),
        "dry_run": input_payload.get("dry_run", False),
        "scenario_results": rows,
    }
    gate_c = phase11.evaluate_gate_c(gate_input)
    profile_eligibility = _profile_eligibility(input_payload)
    demand_summary = _demand_multiplier_provenance_summary(input_payload)
    demand_reasons = [] if demand_summary["valid_actual_behavior"] else ["input artifact lacks valid actual demand multiplier behavior provenance"]
    input_status = str(input_payload.get("status", "")).upper()
    source_reasons = [] if input_status == "PASSED" else [f"input artifact status is {input_status or 'missing'}, not PASSED"]
    required_comparators = set(phase11.REQUIRED_GATE_C_COMPARATORS)
    comparator_reasons = []
    if not required_comparators <= set(input_payload.get("required_comparators", [])):
        comparator_reasons.append("input artifact is missing required v1.4 comparators")
    combined_reasons = list(
        dict.fromkeys(
            profile_eligibility["reasons"]
            + demand_reasons
            + source_reasons
            + comparator_reasons
            + gate_c.get("reasons", [])
        )
    )
    if input_status != "PASSED":
        status = "INCONCLUSIVE"
    elif profile_eligibility["eligible"] and not demand_reasons and not comparator_reasons:
        status = gate_c["status"]
    else:
        status = "FAILED"
    if status not in VALID_STATUSES:
        status = "INCONCLUSIVE"
        combined_reasons.append("internal status normalized to INCONCLUSIVE")
    rule = _extract_rule(gate_c)
    payload = {
        "experiment": "v1_4_gate_c_paired_evidence",
        "status": status,
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": False,
        "input_artifact": str(input_artifact),
        "input_status": input_payload.get("status"),
        "locked_protocol_fingerprint": input_payload.get("locked_protocol_fingerprint"),
        "selected_controller_id": selected,
        "profile_eligibility": profile_eligibility,
        "binding_regime_dominance": gate_c["binding_regime_dominance"],
        "slack_regime_recovery_or_context": gate_c["slack_regime_recovery_or_context"],
        "inconclusive": gate_c["inconclusive"],
        "not_evidence": gate_c["not_evidence"],
        "required_binding_scenarios": list(phase11.BINDING_EVIDENCE_SCENARIOS),
        "required_gate_c_comparators": list(phase11.REQUIRED_GATE_C_COMPARATORS),
        "gate_c_primary_metrics": list(phase11.GATE_C_PRIMARY_METRICS),
        "gate_c_primary_metrics_v1": {
            "status": rule.get("status", status),
            "statistical_family": rule.get("statistical_family", phase11.GATE_C_STATISTICAL_FAMILY),
            "metric_results": rule.get("metric_results", []),
            "family_metadata": rule.get("family_metadata", {}),
            "reasons": rule.get("reasons", []),
        },
        "demand_multiplier_provenance_summary": demand_summary,
        "row_audit": input_payload.get("row_audit", {}),
        "recomputed_gate_c": gate_c,
        "reasons": combined_reasons,
        "caveats": [
            "v1.4 Gate C is limited to the locked Phase 16 protocol.",
            "Closed-loop superiority remains disallowed unless this artifact is PASSED.",
            "Exploratory workstream pilot rows are not final Gate C evidence.",
        ],
    }
    phase11.validate_payload_scope(payload)
    return payload


def write_gate_artifact(input_path: Path, out_path: Path) -> dict[str, Any]:
    input_payload = load_input_payload(input_path)
    payload = build_gate_payload(input_payload, input_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_gate_artifact(Path(args.input), Path(args.out))
    print(json.dumps({"out": args.out, "status": payload["status"], "requirements_covered": payload["requirements_covered"]}, indent=2))
    if args.strict and payload["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
