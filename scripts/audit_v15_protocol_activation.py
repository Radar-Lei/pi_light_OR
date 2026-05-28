#!/usr/bin/env python3
"""Audit whether v1.5 locked execution rows actually exercise storage binding."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_INPUT = "experiments/dual_sensitivity/v1_5_locked_holdout_execution.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_protocol_activation_audit.json"
REQUIREMENTS_COVERED = ["V15-PROTO-AUDIT-01", "V15-CLAIM-01"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--out", default=DEFAULT_OUT)
    return parser.parse_args()


def load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def summarize_activation(payload: dict[str, Any]) -> dict[str, Any]:
    controller = str(payload.get("controller_id"))
    controller_rows = [
        row
        for row in payload.get("scenario_results", [])
        if isinstance(row, dict)
        and row.get("controller") == controller
        and row.get("scenario_status") == "completed"
        and row.get("feasibility_status") in {"run", "completed"}
    ]
    total_decisions = 0
    binding_decisions = 0
    action_changes = 0
    dynamic_term_counts = {"storage_price": 0, "cascade_price": 0, "release": 0}
    row_summaries = []
    for row in controller_rows:
        summary = row.get("action_decomposition", {}).get("decision_summary", {})
        if not isinstance(summary, dict):
            summary = {}
        total = int(summary.get("total_decisions", 0))
        binding = int(summary.get("binding_decision_count", 0))
        changes = int(summary.get("action_changed_relative_to_pressure_count", 0))
        any_counts = summary.get("any_phase_component_nonzero_counts", {})
        if not isinstance(any_counts, dict):
            any_counts = {}
        total_decisions += total
        binding_decisions += binding
        action_changes += changes
        for term in dynamic_term_counts:
            dynamic_term_counts[term] += int(any_counts.get(term, 0))
        row_summaries.append(
            {
                "scenario_tag": row.get("scenario_tag"),
                "demand_multiplier": row.get("demand_multiplier"),
                "seed": row.get("seed"),
                "total_decisions": total,
                "binding_decision_count": binding,
                "action_change_rate": float(summary.get("action_change_rate", 0.0)),
                "binding_decision_rate": float(summary.get("binding_decision_rate", 0.0)),
                "max_occupancy_ratio_observed": float(summary.get("max_occupancy_ratio_observed", 0.0)),
                "min_residual_ratio_observed": float(summary.get("min_residual_ratio_observed", 1.0)),
                "dynamic_term_counts": {term: int(any_counts.get(term, 0)) for term in dynamic_term_counts},
            }
        )
    criteria = {
        "controller_rows_present": bool(controller_rows),
        "binding_decisions_present": binding_decisions > 0,
        "storage_price_active": dynamic_term_counts["storage_price"] > 0,
        "cascade_or_release_active": dynamic_term_counts["cascade_price"] > 0 or dynamic_term_counts["release"] > 0,
    }
    return {
        "controller_rows": len(controller_rows),
        "total_decisions": total_decisions,
        "binding_decision_count": binding_decisions,
        "binding_decision_rate": float(binding_decisions / total_decisions) if total_decisions else 0.0,
        "action_changed_relative_to_pressure_count": action_changes,
        "action_change_rate": float(action_changes / total_decisions) if total_decisions else 0.0,
        "dynamic_term_counts": dynamic_term_counts,
        "criteria": criteria,
        "row_summaries": row_summaries,
    }


def build_audit(payload: dict[str, Any], input_path: Path) -> dict[str, Any]:
    summary = summarize_activation(payload)
    passed = all(bool(value) for value in summary["criteria"].values())
    reasons = []
    if not passed:
        if not summary["criteria"]["binding_decisions_present"]:
            reasons.append("executed v1.5 rows did not enter finite-storage binding states")
        if not summary["criteria"]["storage_price_active"]:
            reasons.append("storage shadow price did not activate in executed v1.5 rows")
        if not summary["criteria"]["cascade_or_release_active"]:
            reasons.append("cascade or release dynamic terms did not activate in executed v1.5 rows")
    return {
        "experiment": "v1_5_protocol_activation_audit",
        "status": "PASSED" if passed else "FAILED",
        "generated_by": "scripts/audit_v15_protocol_activation.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requirements_covered": REQUIREMENTS_COVERED,
        "input_artifact": str(input_path),
        "input_status": payload.get("status"),
        "locked_protocol_fingerprint": payload.get("locked_protocol_fingerprint"),
        "summary": summary,
        "reasons": reasons,
        "recommendation": (
            "continue locked holdout execution"
            if passed
            else "supersede this holdout protocol with a storage-activation holdout before any claim-eligible run"
        ),
        "claim_scope": {
            "allowed_now": "protocol activation audit only",
            "not_claimed": ["closed_loop_superiority", "locked_holdout_passed"],
        },
    }


def write_audit(input_path: Path, out_path: Path) -> dict[str, Any]:
    audit = build_audit(load_payload(input_path), input_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return audit


def main() -> None:
    args = parse_args()
    audit = write_audit(Path(args.input), Path(args.out))
    print(json.dumps({"status": audit["status"], "out": args.out, "recommendation": audit["recommendation"]}, indent=2))
    if audit["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
