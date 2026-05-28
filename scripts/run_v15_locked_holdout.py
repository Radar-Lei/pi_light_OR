#!/usr/bin/env python3
"""Execute or resume the locked v1.5 holdout protocol."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_phase11_paired_evidence as phase11

DEFAULT_PROTOCOL = "experiments/dual_sensitivity/v1_5_locked_protocol.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_locked_holdout_execution.json"
DEFAULT_PROGRESS = "experiments/dual_sensitivity/v1_5_locked_holdout_execution.progress.json"
DEFAULT_SCALED_INPUT_DIR = "experiments/dual_sensitivity/v1_5_scaled_inputs"
REQUIREMENTS_COVERED = ["V15-HOLDOUT-01", "V15-CLAIM-01"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", default=DEFAULT_PROTOCOL)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--scaled-input-dir", default=DEFAULT_SCALED_INPUT_DIR)
    parser.add_argument("--progress-out", default=None)
    parser.add_argument("--resume-progress", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execution-row-limit", type=int, default=None)
    parser.add_argument("--max-new-rows", type=int, default=None, help="Execute at most this many new pending rows while preserving the full locked spec progress fingerprint.")
    return parser.parse_args()


def load_protocol(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Protocol {path} must contain a JSON object")
    return payload


def validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("experiment") not in {"v1_5_locked_protocol", "v1_5_binding_locked_protocol"}:
        raise ValueError("protocol is not a supported v1.5 locked protocol")
    if protocol.get("status") != "LOCKED":
        raise ValueError("v1.5 protocol is not LOCKED")
    controller = protocol.get("controller_id")
    if controller not in phase11.CONTROLLER_REGISTRY:
        raise ValueError(f"v1.5 controller is not executable: {controller}")
    holdout = protocol.get("locked_holdout")
    if not isinstance(holdout, dict):
        raise ValueError("v1.5 protocol is missing locked_holdout")
    required = set(protocol.get("required_baselines", []))
    controllers = set(holdout.get("controllers", []))
    missing = sorted({controller, *required} - controllers)
    if missing:
        raise ValueError(f"v1.5 holdout is missing required controllers: {missing}")
    for field in ["scenarios", "seeds", "demand_multipliers", "steps", "warmup", "action_interval", "expected_row_count"]:
        if not holdout.get(field):
            raise ValueError(f"v1.5 locked_holdout is missing {field}")


def build_locked_spec(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    validate_protocol(protocol)
    holdout = protocol["locked_holdout"]
    spec = []
    for scenario_tag in holdout["scenarios"]:
        for demand_multiplier in holdout["demand_multipliers"]:
            contract = phase11.demand_multiplier_contract(float(demand_multiplier))
            for seed in holdout["seeds"]:
                for controller in holdout["controllers"]:
                    spec.append(
                        {
                            "profile": str(holdout.get("profile", "main")),
                            "evidence_role": "v1_5_locked_holdout",
                            "gate_c_eligible": True,
                            "network": "arterial",
                            "scenario_tag": str(scenario_tag),
                            "controller": str(controller),
                            "seed": int(seed),
                            "steps": int(holdout["steps"]),
                            "warmup": int(holdout["warmup"]),
                            "action_interval": int(holdout["action_interval"]),
                            "demand_multiplier": float(demand_multiplier),
                            "demand_multiplier_contract": dict(contract),
                            "v1_5_protocol_fingerprint": protocol["protocol_fingerprint"],
                        }
                    )
    expected = int(holdout["expected_row_count"])
    if len(spec) != expected:
        raise ValueError(f"v1.5 spec row count {len(spec)} does not match protocol expected_row_count={expected}")
    return spec


def build_row_audit(rows: list[dict[str, Any]], spec: list[dict[str, Any]]) -> dict[str, Any]:
    expected_keys = [phase11.row_key(row) for row in spec]
    completed = phase11._completed_rows(rows)
    completed_keys = [phase11.row_key(row) for row in completed]
    row_counts: dict[str, int] = {}
    for row in rows:
        key = phase11.row_key(row)
        row_counts[key] = row_counts.get(key, 0) + 1
    duplicate_keys = sorted(key for key, count in row_counts.items() if count > 1)
    failed_rows = [
        {
            "row_key": phase11.row_key(row),
            "scenario_status": row.get("scenario_status"),
            "feasibility_status": row.get("feasibility_status"),
            "reason": row.get("unsupported_reason") or row.get("placeholder_reason") or row.get("error"),
        }
        for row in rows
        if row.get("scenario_status") != "completed" or row.get("feasibility_status") not in {"run", "completed"}
    ]
    missing = sorted(set(expected_keys) - set(completed_keys))
    return {
        "expected_row_count": len(spec),
        "raw_row_count": len(rows),
        "completed_row_count": len(completed),
        "missing_row_count": len(missing),
        "failed_row_count": len(failed_rows),
        "duplicate_row_count": len(duplicate_keys),
        "missing_rows": [{"row_key": key} for key in missing[:50]],
        "failed_rows": failed_rows[:50],
        "duplicate_rows": [{"row_key": key} for key in duplicate_keys[:50]],
    }


def _status(dry_run: bool, rows: list[dict[str, Any]], spec: list[dict[str, Any]], missing_reasons: list[str]) -> str:
    if dry_run:
        return "PILOT_ONLY"
    if missing_reasons or len(phase11._completed_rows(rows)) < len(spec):
        return "INCONCLUSIVE"
    return "COMPLETE_PENDING_PAIRED_EVIDENCE"


def write_locked_execution(
    *,
    protocol_path: Path,
    out_path: Path,
    route_json: Path,
    scaled_input_dir: Path,
    dry_run: bool = False,
    execution_row_limit: int | None = None,
    progress_out: Path | None = None,
    resume_progress: Path | None = None,
    max_new_rows: int | None = None,
) -> dict[str, Any]:
    protocol = load_protocol(protocol_path)
    spec = build_locked_spec(protocol)
    spec = phase11.materialize_demand_inputs(spec, scaled_input_dir)
    route_metadata = phase11.load_route_metadata(route_json)
    if execution_row_limit is None:
        execution_row_limit = 0 if not dry_run else len(spec)
    rows, missing_reasons, execution_mode = phase11.execute_spec(
        spec,
        route_metadata,
        dry_run=dry_run,
        execution_row_limit=execution_row_limit,
        progress_out=progress_out,
        resume_progress=resume_progress,
        max_new_rows=max_new_rows,
    )
    row_audit = build_row_audit(rows, spec)
    payload = {
        "experiment": "v1_5_locked_holdout_execution",
        "status": _status(dry_run, rows, spec, missing_reasons),
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": False,
        "locked_protocol_path": str(protocol_path),
        "locked_protocol_status": protocol.get("status"),
        "locked_protocol_fingerprint": protocol.get("protocol_fingerprint"),
        "controller_id": protocol.get("controller_id"),
        "required_baselines": list(protocol.get("required_baselines", [])),
        "primary_endpoint": protocol.get("primary_endpoint"),
        "safety_guards": protocol.get("safety_guards"),
        "profile": protocol["locked_holdout"].get("profile", "main"),
        "steps": int(protocol["locked_holdout"]["steps"]),
        "warmup": int(protocol["locked_holdout"]["warmup"]),
        "action_interval": int(protocol["locked_holdout"]["action_interval"]),
        "dry_run": bool(dry_run),
        "execution_mode": execution_mode,
        "execution_row_limit": execution_row_limit,
        "max_new_rows": max_new_rows,
        "expected_row_count": len(spec),
        "actual_row_count": row_audit["completed_row_count"],
        "all_rows_executed": row_audit["completed_row_count"] == len(spec) and not missing_reasons,
        "missing_row_reasons": missing_reasons,
        "row_audit": row_audit,
        "route_metadata": route_metadata,
        "scenario_results": rows,
        "claim_scope": {
            "allowed_now": "execution/provenance artifact only",
            "not_claimed": [
                "closed_loop_superiority",
                "paired_holdout_passed",
                "deployment_readiness",
            ],
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_locked_execution(
        protocol_path=Path(args.protocol),
        out_path=Path(args.out),
        route_json=Path(args.route_json),
        scaled_input_dir=Path(args.scaled_input_dir),
        dry_run=args.dry_run,
        execution_row_limit=args.execution_row_limit,
        progress_out=Path(args.progress_out) if args.progress_out else None,
        resume_progress=Path(args.resume_progress) if args.resume_progress else None,
        max_new_rows=args.max_new_rows,
    )
    print(
        json.dumps(
            {
                "out": args.out,
                "status": payload["status"],
                "expected_rows": payload["expected_row_count"],
                "completed_rows": payload["actual_row_count"],
                "execution_mode": payload["execution_mode"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
