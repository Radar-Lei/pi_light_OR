#!/usr/bin/env python3
"""Execute the v1.8 locked holdout protocol.

Reads the locked holdout protocol JSON, builds the execution spec from holdout
seeds/scenarios/demands/controllers, and runs SUMO closed-loop simulations.

Key properties:
  - Fresh seeds NOT used in training (verified at startup)
  - Fixed controller params, baselines, thresholds, objectives all locked
  - No mid-run editing (protocol is HOLDOUT_LOCKED)
  - Protocol fingerprint for auditability

Usage:
  python3 scripts/run_v18_holdout.py
  python3 scripts/run_v18_holdout.py --dry-run
  python3 scripts/run_v18_holdout.py --limit 20
  python3 scripts/run_v18_holdout.py --resume-progress HOLDOUT_PROGRESS.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# Ensure scripts/ is importable when running from project root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_phase11_paired_evidence as phase11

DEFAULT_PROTOCOL = "experiments/dual_sensitivity/v1_8_locked_holdout_protocol.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_8_locked_holdout_execution.json"
DEFAULT_PROGRESS = "experiments/dual_sensitivity/v1_8_locked_holdout_progress.json"
TRAINING_PROTOCOL = "experiments/dual_sensitivity/v1_8_training_protocol.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute v1.8 locked holdout protocol"
    )
    parser.add_argument("--protocol", default=DEFAULT_PROTOCOL)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--progress-out", default=DEFAULT_PROGRESS)
    parser.add_argument("--route-json", default=None)
    parser.add_argument("--scaled-input-dir", default=None)
    parser.add_argument("--resume-progress", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-new-rows", type=int, default=None)
    return parser.parse_args()


def load_protocol(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Protocol {path} must contain a JSON object")
    return payload


def validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("experiment") != "v1_8_locked_holdout_protocol":
        raise ValueError("protocol is not a v1.8 locked holdout protocol")
    if protocol.get("status") != "HOLDOUT_LOCKED":
        raise ValueError("holdout protocol is not HOLDOUT_LOCKED")
    if not protocol.get("locked"):
        raise ValueError("holdout protocol is not marked as locked")
    controller = protocol.get("controller_id")
    if controller != "finite_storage_regime_calibrated_cfs_pd_mpc_v1_8":
        raise ValueError(f"unexpected controller_id: {controller}")
    if controller not in phase11.CONTROLLER_REGISTRY:
        raise ValueError(f"v1.8 controller is not executable: {controller}")

    # Verify seed isolation against training protocol
    grid = protocol.get("holdout_grid", {})
    holdout_seeds = set(grid.get("seeds", []))
    training_seeds = _training_seeds()
    overlap = holdout_seeds & training_seeds
    if overlap:
        raise ValueError(
            f"Holdout seeds overlap with training seeds: {sorted(overlap)}"
        )

    # Verify controller params fingerprint
    cp = protocol.get("controller_params", {})
    param_str = json.dumps(cp, sort_keys=True)
    expected_fp = hashlib.sha256(param_str.encode()).hexdigest()[:16]
    stored_fp = protocol.get("controller_params_fingerprint", "")
    if stored_fp != expected_fp:
        raise ValueError(
            f"Controller params fingerprint mismatch: stored={stored_fp}, "
            f"computed={expected_fp}"
        )


def _training_seeds() -> set[int]:
    tp_path = Path(TRAINING_PROTOCOL)
    if not tp_path.exists():
        raise FileNotFoundError(
            f"Training protocol not found at {tp_path}; "
            "cannot verify seed isolation"
        )
    tp = json.loads(tp_path.read_text(encoding="utf-8"))
    return set(tp.get("training_split", {}).get("seeds", []))


def build_holdout_spec(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    validate_protocol(protocol)
    grid = protocol["holdout_grid"]
    spec = []
    for scenario_tag in grid["scenarios"]:
        for demand_multiplier in grid["demand_multipliers"]:
            contract = phase11.demand_multiplier_contract(float(demand_multiplier))
            for seed in grid["seeds"]:
                for controller in grid["controllers"]:
                    spec.append(
                        {
                            "profile": "holdout",
                            "evidence_role": "v1_8_holdout",
                            "gate_c_eligible": False,
                            "network": "arterial",
                            "scenario_tag": str(scenario_tag),
                            "controller": str(controller),
                            "seed": int(seed),
                            "steps": int(grid["steps"]),
                            "warmup": int(grid["warmup"]),
                            "action_interval": int(grid["action_interval"]),
                            "demand_multiplier": float(demand_multiplier),
                            "demand_multiplier_contract": dict(contract),
                            "controller_params_fingerprint": protocol.get(
                                "controller_params_fingerprint", ""
                            ),
                        }
                    )
    return spec


def build_row_audit(
    rows: list[dict[str, Any]], spec: list[dict[str, Any]]
) -> dict[str, Any]:
    expected_keys = [phase11.row_key(row) for row in spec]
    completed = phase11._completed_rows(rows)
    completed_keys = [phase11.row_key(row) for row in completed]
    row_counts: dict[str, int] = {}
    for row in rows:
        key = phase11.row_key(row)
        row_counts[key] = row_counts.get(key, 0) + 1
    duplicate_keys = sorted(
        key for key, count in row_counts.items() if count > 1
    )
    failed_rows = [
        {
            "row_key": phase11.row_key(row),
            "scenario_status": row.get("scenario_status"),
            "feasibility_status": row.get("feasibility_status"),
            "reason": row.get("unsupported_reason")
            or row.get("placeholder_reason")
            or row.get("error"),
        }
        for row in rows
        if row.get("scenario_status") != "completed"
        or row.get("feasibility_status") not in {"run", "completed"}
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


def _status(
    dry_run: bool,
    rows: list[dict[str, Any]],
    spec: list[dict[str, Any]],
    missing_reasons: list[str],
) -> str:
    if dry_run:
        return "DRY_RUN"
    if missing_reasons or len(phase11._completed_rows(rows)) < len(spec):
        return "IN_PROGRESS"
    return "COMPLETE"


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
        "experiment": "v1_8_locked_holdout_execution",
        "status": _status(dry_run, rows, spec, missing_reasons),
        "holdout_protocol_path": str(protocol_path),
        "controller_id": protocol.get("controller_id"),
        "controller_params": protocol.get("controller_params", {}),
        "controller_params_fingerprint": protocol.get(
            "controller_params_fingerprint", ""
        ),
        "holdout_grid": protocol.get("holdout_grid", {}),
        "seed_isolation": protocol.get("seed_isolation", {}),
        "primary_endpoint": protocol.get("primary_endpoint", {}),
        "safety_guards": protocol.get("safety_guards", {}),
        "profile": "holdout",
        "dry_run": bool(dry_run),
        "execution_mode": execution_mode,
        "execution_row_limit": execution_row_limit,
        "max_new_rows": max_new_rows,
        "expected_row_count": len(spec),
        "actual_row_count": row_audit["completed_row_count"],
        "all_rows_executed": row_audit["completed_row_count"] == len(spec)
        and not missing_reasons,
        "missing_row_reasons": missing_reasons,
        "row_audit": row_audit,
        "route_metadata": route_metadata,
        "scenario_results": rows,
        "claim_scope": {
            "allowed_now": "holdout evidence for v1.8 generalization claim",
            "not_claimed": [
                "closed_loop_superiority_all_conditions",
                "deployment_readiness",
            ],
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    protocol = load_protocol(Path(args.protocol))

    # Resolve defaults from protocol
    route_json = Path(
        args.route_json
        or protocol.get("route_json", "experiments/dual_sensitivity/block3_static_kill_gate.json")
    )
    scaled_input_dir = Path(
        args.scaled_input_dir
        or protocol.get(
            "scaled_input_dir",
            "experiments/dual_sensitivity/v1_8_training_scaled_inputs",
        )
    )
    progress_out = Path(args.progress_out)
    resume_progress = Path(args.resume_progress) if args.resume_progress else None

    payload = write_holdout_execution(
        protocol_path=Path(args.protocol),
        out_path=Path(args.out),
        route_json=route_json,
        scaled_input_dir=scaled_input_dir,
        dry_run=args.dry_run,
        execution_row_limit=args.limit,
        progress_out=progress_out,
        resume_progress=resume_progress,
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
