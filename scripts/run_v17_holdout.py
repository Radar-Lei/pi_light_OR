#!/usr/bin/env python3
"""Execute or resume the v1.7 CFS-PD-MPC locked holdout protocol.

Reads the locked holdout configuration from the protocol JSON, builds the
execution spec, and runs SUMO closed-loop simulations for each row
(scenario x seed x demand x controller).

The holdout split uses claim-eligible evidence_role and gate_c_eligible=True,
as holdout results are the basis for post-lock superiority claims.

Supports:
  --dry-run          Build the spec without executing SUMO.
  --resume-progress  Resume from a previous progress checkpoint.
  --max-new-rows     Limit the number of new rows attempted in this run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_phase11_paired_evidence as phase11

DEFAULT_PROTOCOL = "experiments/dual_sensitivity/v1_7_training_protocol.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_7_locked_holdout_execution.json"
DEFAULT_PROGRESS = "experiments/dual_sensitivity/v1_7_locked_holdout_execution.progress.json"
DEFAULT_SCALED_INPUT_DIR = "experiments/dual_sensitivity/v1_7_holdout_scaled_inputs"
REQUIREMENTS_COVERED = ["V17-HOLDOUT-01", "V17-CLAIM-01"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute v1.7 CFS-PD-MPC locked holdout protocol")
    parser.add_argument("--protocol", default=DEFAULT_PROTOCOL)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--scaled-input-dir", default=DEFAULT_SCALED_INPUT_DIR)
    parser.add_argument("--progress-out", default=None)
    parser.add_argument("--resume-progress", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execution-row-limit", type=int, default=None)
    parser.add_argument("--max-new-rows", type=int, default=None)
    return parser.parse_args()


def load_protocol(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Protocol {path} must contain a JSON object")
    return payload


def validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("experiment") != "v1_7_training_protocol":
        raise ValueError("protocol is not a v1.7 training protocol")
    if protocol.get("status") != "TRAINING_LOCKED":
        raise ValueError("v1.7 training protocol is not TRAINING_LOCKED")
    controller = protocol.get("controller_id")
    if controller != "finite_storage_completion_primal_dual_v1_7":
        raise ValueError(f"unexpected controller_id: {controller}")
    if controller not in phase11.CONTROLLER_REGISTRY:
        raise ValueError(f"v1.7 controller is not executable: {controller}")
    holdout = protocol.get("locked_holdout")
    if not isinstance(holdout, dict):
        raise ValueError("v1.7 protocol is missing locked_holdout")
    holdout_role = holdout.get("role")
    if "claim_eligible" not in str(holdout_role):
        raise ValueError(f"locked_holdout role does not indicate claim eligibility: {holdout_role}")
    controllers = set(holdout.get("controllers", []))
    missing = sorted({controller, *protocol.get("required_baselines", [])} - controllers)
    if missing:
        raise ValueError(f"v1.7 locked_holdout is missing required controllers: {missing}")
    for field in ["scenarios", "seeds", "demand_multipliers", "steps", "warmup", "action_interval", "expected_row_count"]:
        if not holdout.get(field):
            raise ValueError(f"v1.7 locked_holdout is missing {field}")


def build_holdout_spec(protocol: dict[str, Any]) -> list[dict[str, Any]]:
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
                            "profile": "holdout",
                            "evidence_role": "locked_holdout_claim_eligible",
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
                            "training_protocol_fingerprint": protocol["protocol_fingerprint"],
                        }
                    )
    expected = int(holdout["expected_row_count"])
    if len(spec) != expected:
        raise ValueError(
            f"v1.7 holdout spec row count {len(spec)} does not match expected_row_count={expected}"
        )
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
        return "DRY_RUN"
    if missing_reasons or len(phase11._completed_rows(rows)) < len(spec):
        return "IN_PROGRESS"
    return "COMPLETE_PENDING_CLAIM"


def write_holdout_execution(
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

    spec = build_holdout_spec(protocol)

    spec = phase11.materialize_demand_inputs(spec, scaled_input_dir)
    route_metadata = phase11.load_route_metadata(route_json)

    if execution_row_limit is None:
        execution_row_limit = len(spec) if not dry_run else 0

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
        "experiment": "v1_7_locked_holdout_execution",
        "status": _status(dry_run, rows, spec, missing_reasons),
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": row_audit["completed_row_count"] == len(spec) and not missing_reasons,
        "training_protocol_path": str(protocol_path),
        "training_protocol_status": protocol.get("status"),
        "training_protocol_fingerprint": protocol.get("protocol_fingerprint"),
        "controller_id": protocol.get("controller_id"),
        "required_baselines": list(protocol.get("required_baselines", [])),
        "controller_params": protocol.get("controller_params", {}),
        "selection_rule": protocol.get("selection_rule", {}),
        "profile": "holdout",
        "holdout_role": protocol["locked_holdout"].get("role"),
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
            "allowed_now": "locked_holdout claim-eligible evidence (post training selection)",
            "not_claimed": [
                "deployment_readiness",
                "generalization_beyond_holdout_scenarios",
            ],
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_holdout_execution(
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
                "claim_ready": payload["claim_ready"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
