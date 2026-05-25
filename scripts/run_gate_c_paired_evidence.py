#!/usr/bin/env python3
"""Strict Phase 11 Gate C paired-evidence checker.

The checker consumes a Phase 11 paired-seed evidence artifact, recomputes Gate C
from raw scenario rows through the shared Phase 11 helpers, and writes a separate
machine-readable Gate C result. Pilot, dry-run, spec-only, or missing-execution
artifacts are fail-closed as INCONCLUSIVE/FAILED rather than dominance evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_phase11_paired_evidence import (
    BINDING_EVIDENCE_SCENARIOS,
    GATE_C_CONDITIONAL_PRIMARY_METRICS,
    GATE_C_PRIMARY_METRICS,
    GATE_C_STATISTICAL_FAMILY,
    REQUIRED_GATE_C_COMPARATORS,
    SLACK_CONTEXT_SCENARIOS,
    evaluate_gate_c,
    validate_payload_scope,
)

DEFAULT_INPUT = "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json"
DEFAULT_OUT = "experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json"
REQUIREMENTS_COVERED = ["GATE-03", "EXP-05"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def load_input_payload(path: Path) -> dict[str, Any]:
    if path.suffix != ".json":
        raise ValueError("--input must point to a .json Phase 11 artifact")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Input artifact {path} must contain a JSON object")
    validate_payload_scope(payload)
    return payload


def _profile_eligibility(payload: dict[str, Any]) -> dict[str, Any]:
    profile = payload.get("profile")
    steps = int(payload.get("steps", 0) or 0)
    warmup = int(payload.get("warmup", 0) or 0)
    dry_run = bool(payload.get("dry_run"))
    rows = list(payload.get("scenario_results", []))
    completed_rows = [
        row for row in rows
        if row.get("scenario_status") == "completed" and row.get("feasibility_status") in {"run", "completed"}
    ]
    actual_row_count = int(payload.get("actual_row_count", len(completed_rows)) or 0)
    expected_row_count = int(payload.get("expected_row_count", 0) or 0)
    all_rows_executed = payload.get("all_rows_executed")
    reasons = []
    if payload.get("experiment") != "phase11_long_horizon_paired_seed_evidence":
        reasons.append("input artifact is not phase11_long_horizon_paired_seed_evidence")
    if profile != "main":
        reasons.append("pilot-only artifacts cannot complete Gate C evidence")
    if steps < 3600:
        reasons.append("main-profile Gate C requires at least 3600 steps")
    if warmup < 900:
        reasons.append("main-profile Gate C requires at least 900 warmup steps")
    if dry_run:
        reasons.append("dry-run/spec-only artifacts cannot complete Gate C evidence")
    if actual_row_count == 0:
        reasons.append("input artifact has no executed raw scenario rows")
    if all_rows_executed is not True:
        reasons.append("input artifact reports missing required executed rows")
    if actual_row_count != len(completed_rows):
        reasons.append("input artifact actual_row_count does not match completed raw scenario rows")
    if expected_row_count <= 0:
        reasons.append("input artifact is missing a positive expected_row_count")
    elif actual_row_count != expected_row_count:
        reasons.append("input artifact actual_row_count does not match expected_row_count")
    return {
        "eligible": not reasons,
        "profile": profile,
        "steps": steps,
        "warmup": warmup,
        "dry_run": dry_run,
        "actual_row_count": actual_row_count,
        "expected_row_count": expected_row_count,
        "completed_row_count": len(completed_rows),
        "all_rows_executed": all_rows_executed is True,
        "reasons": reasons,
    }


def _demand_multiplier_provenance_summary(payload: dict[str, Any]) -> dict[str, Any]:
    provenance = payload.get("demand_scaling_provenance", [])
    row_provenance = []
    for row in payload.get("scenario_results", []):
        item = row.get("demand_multiplier_provenance")
        if isinstance(item, dict):
            row_provenance.append(item)
    all_provenance = list(provenance) + row_provenance
    metadata_only = [item for item in all_provenance if isinstance(item, dict) and item.get("metadata_only_valid") is not False]
    methods = sorted({str(item.get("demand_scaling_method")) for item in all_provenance if isinstance(item, dict) and item.get("demand_scaling_method")})
    multipliers = sorted({float(item.get("demand_multiplier")) for item in all_provenance if isinstance(item, dict) and item.get("demand_multiplier") is not None})
    missing_actual_fields = []
    for item in all_provenance:
        if not isinstance(item, dict):
            continue
        missing = [field for field in ["base_demand_total", "scaled_demand_total", "generated_route_file", "generated_sumocfg", "base_sumocfg"] if field not in item]
        if missing:
            missing_actual_fields.append({"demand_multiplier": item.get("demand_multiplier"), "missing": missing})
            continue
        expected_total = float(item["base_demand_total"]) * float(item.get("demand_multiplier", 1.0))
        scaled_total = float(item["scaled_demand_total"])
        if abs(scaled_total - expected_total) > max(0.5, abs(expected_total) * 0.02):
            missing_actual_fields.append({"demand_multiplier": item.get("demand_multiplier"), "invalid_scaled_total": scaled_total, "expected_scaled_total": expected_total})
    return {
        "method": payload.get("demand_scaling_method"),
        "methods_seen": methods,
        "demand_multipliers": multipliers or payload.get("demand_multipliers", []),
        "provenance_entry_count": len(all_provenance),
        "metadata_only_entry_count": len(metadata_only),
        "missing_actual_behavior_fields": missing_actual_fields,
        "valid_actual_behavior": bool(all_provenance) and not metadata_only and not missing_actual_fields,
    }


def _extract_rule(gate_c: dict[str, Any]) -> dict[str, Any]:
    return gate_c.get("primary_metric_rule", {}) if isinstance(gate_c.get("primary_metric_rule"), dict) else {}


def build_gate_payload(input_payload: dict[str, Any], input_artifact: Path) -> dict[str, Any]:
    rows = list(input_payload.get("scenario_results", []))
    gate_input = {
        "profile": input_payload.get("profile"),
        "steps": input_payload.get("steps", 0),
        "warmup": input_payload.get("warmup", 0),
        "dry_run": input_payload.get("dry_run", False),
        "scenario_results": rows,
    }
    gate_c = evaluate_gate_c(gate_input)
    profile_eligibility = _profile_eligibility(input_payload)
    demand_summary = _demand_multiplier_provenance_summary(input_payload)
    demand_reasons = [] if demand_summary["valid_actual_behavior"] else ["input artifact lacks valid actual demand multiplier behavior provenance"]
    input_status = str(input_payload.get("status", "")).upper()
    source_reasons = [] if input_status == "PASSED" else [f"input artifact status is {input_status or 'missing'}, not PASSED"]
    combined_reasons = list(dict.fromkeys(profile_eligibility["reasons"] + demand_reasons + source_reasons + gate_c.get("reasons", [])))
    if input_status != "PASSED":
        status = "INCONCLUSIVE"
    elif gate_c["status"] == "PASSED" and not profile_eligibility["eligible"]:
        status = "INCONCLUSIVE"
    elif demand_reasons and profile_eligibility["eligible"]:
        status = "FAILED"
    else:
        status = gate_c["status"]
    rule = _extract_rule(gate_c)
    payload = {
        "experiment": "phase11_gate_c_paired_evidence",
        "status": status,
        "requirements_covered": REQUIREMENTS_COVERED,
        "input_artifact": str(input_artifact),
        "input_status": input_payload.get("status"),
        "profile_eligibility": profile_eligibility,
        "binding_regime_dominance": gate_c["binding_regime_dominance"],
        "slack_regime_recovery_or_context": gate_c["slack_regime_recovery_or_context"],
        "inconclusive": gate_c["inconclusive"],
        "not_evidence": gate_c["not_evidence"],
        "required_binding_scenarios": list(BINDING_EVIDENCE_SCENARIOS),
        "slack_context_scenarios": list(SLACK_CONTEXT_SCENARIOS),
        "required_gate_c_comparators": list(REQUIRED_GATE_C_COMPARATORS),
        "gate_c_primary_metrics": list(GATE_C_PRIMARY_METRICS),
        "gate_c_conditional_primary_metrics": {key: list(value) for key, value in GATE_C_CONDITIONAL_PRIMARY_METRICS.items()},
        "statistical_family": GATE_C_STATISTICAL_FAMILY,
        "gate_c_primary_metrics_v1": {
            "status": rule.get("status", status),
            "statistical_family": rule.get("statistical_family", GATE_C_STATISTICAL_FAMILY),
            "metric_results": rule.get("metric_results", []),
            "family_metadata": rule.get("family_metadata", {}),
            "reasons": rule.get("reasons", []),
        },
        "demand_multiplier_provenance_summary": demand_summary,
        "recomputed_gate_c": gate_c,
        "reasons": combined_reasons,
        "caveats": [
            "Gate C is limited to Phase 11 predeclared binding stress regimes and required pressure/storage-aware comparators.",
            "Slack/control rows are context only and cannot satisfy dominance evidence.",
            "Pilot, dry-run, spec-only, metadata-only-demand, or missing-execution artifacts are not completed Gate C evidence.",
            "Phase 12 must regenerate final manuscript inputs and claim templates from raw artifacts.",
        ],
    }
    validate_payload_scope(payload)
    return payload


def write_gate_artifact(input_path: Path, out_path: Path) -> dict[str, Any]:
    input_payload = load_input_payload(input_path)
    payload = build_gate_payload(input_payload, input_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    out_path = Path(args.out)
    payload = write_gate_artifact(input_path, out_path)
    print(json.dumps({"out": str(out_path), "status": payload["status"], "requirements_covered": payload["requirements_covered"]}, indent=2))
    if args.strict and payload["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
