#!/usr/bin/env python3
"""Execute or resume the v1.8 RC-CFS-PD-MPC training protocol.

Reads the locked training protocol JSON, builds the execution spec, and runs
SUMO closed-loop simulations for each row (scenario x seed x demand x controller).

Key differences from v1.7:
  - Controller: finite_storage_regime_calibrated_cfs_pd_mpc_v1_8
  - 5 training scenarios, 6 seeds, 3 demand levels, 7 controllers
  - 15-row screen subset (5 scenarios x 1 seed x 1 demand x 5 controllers)
  - Gate reference: v1_8_rc_cfs_pd_mpc_gates.json
  - Eligibility gates for regime balance, action separation, safety

Supports:
  --dry-run          Build the spec without executing SUMO.
  --screen-only      Execute only the 15-row screen subset (5 scenarios x 1 seed
                     x 1 demand x 5 controllers) for early smoke testing.
  --limit N          Run only N rows (useful for incremental execution).
  --resume-progress  Resume from a previous progress checkpoint.
  --max-new-rows     Limit the number of new rows attempted in this run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Ensure scripts/ is importable when running from project root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_phase11_paired_evidence as phase11

DEFAULT_PROTOCOL = "experiments/dual_sensitivity/v1_8_training_protocol.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_8_training_execution.json"
DEFAULT_PROGRESS = "experiments/dual_sensitivity/v1_8_training_execution.progress.json"
DEFAULT_SCREEN_OUT = "experiments/dual_sensitivity/v1_8_screen_execution.json"
DEFAULT_SCREEN_PROGRESS = "experiments/dual_sensitivity/v1_8_screen_progress.json"
DEFAULT_SCALED_INPUT_DIR = "experiments/dual_sensitivity/v1_8_training_scaled_inputs"
DEFAULT_ROUTE_JSON = "experiments/dual_sensitivity/block3_static_kill_gate.json"
REQUIREMENTS_COVERED = ["V18-PROTO-01", "V18-EVID-01", "V18-CLAIM-01"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute v1.8 RC-CFS-PD-MPC training protocol"
    )
    parser.add_argument("--protocol", default=DEFAULT_PROTOCOL)
    parser.add_argument("--out", default=None,
                        help="Output path. Defaults to screen or training path based on mode.")
    parser.add_argument("--route-json", default=DEFAULT_ROUTE_JSON)
    parser.add_argument("--scaled-input-dir", default=DEFAULT_SCALED_INPUT_DIR)
    parser.add_argument("--progress-out", default=None)
    parser.add_argument("--resume-progress", default=None)
    parser.add_argument("--dry-run", action="store_true",
                        help="Build spec without executing SUMO rows.")
    parser.add_argument("--screen-only", action="store_true",
                        help="Execute only the 15-row screen subset for smoke testing.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Run only N rows of the spec.")
    parser.add_argument("--max-new-rows", type=int, default=None,
                        help="Limit new rows attempted in this run (for incremental execution).")
    return parser.parse_args()


def load_protocol(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Protocol {path} must contain a JSON object")
    return payload


def validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("experiment") != "v1_8_training_protocol":
        raise ValueError("protocol is not a v1.8 training protocol")
    if protocol.get("status") != "TRAINING_LOCKED":
        raise ValueError("v1.8 training protocol is not TRAINING_LOCKED")
    controller = protocol.get("controller_id")
    if controller != "finite_storage_regime_calibrated_cfs_pd_mpc_v1_8":
        raise ValueError(f"unexpected controller_id: {controller}")
    if controller not in phase11.CONTROLLER_REGISTRY:
        raise ValueError(f"v1.8 controller is not executable: {controller}")
    split = protocol.get("training_split")
    if not isinstance(split, dict):
        raise ValueError("v1.8 training protocol is missing training_split")
    controllers = set(split.get("controllers", []))
    missing = sorted({controller, *protocol.get("required_baselines", [])} - controllers)
    if missing:
        raise ValueError(f"v1.8 training_split is missing required controllers: {missing}")
    for field in ["scenarios", "seeds", "demand_multipliers", "steps", "warmup",
                  "action_interval", "screen_row_count"]:
        if not split.get(field):
            raise ValueError(f"v1.8 training_split is missing {field}")


def build_training_spec(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    validate_protocol(protocol)
    split = protocol["training_split"]
    spec = []
    for scenario_tag in split["scenarios"]:
        for demand_multiplier in split["demand_multipliers"]:
            contract = phase11.demand_multiplier_contract(float(demand_multiplier))
            for seed in split["seeds"]:
                for controller in split["controllers"]:
                    spec.append(
                        {
                            "profile": str(split.get("profile", "training")),
                            "evidence_role": "v1_8_training_only",
                            "gate_c_eligible": False,
                            "network": "arterial",
                            "scenario_tag": str(scenario_tag),
                            "controller": str(controller),
                            "seed": int(seed),
                            "steps": int(split["steps"]),
                            "warmup": int(split["warmup"]),
                            "action_interval": int(split["action_interval"]),
                            "demand_multiplier": float(demand_multiplier),
                            "demand_multiplier_contract": dict(contract),
                            "training_protocol_fingerprint": protocol.get("protocol_fingerprint", ""),
                        }
                    )
    return spec


def build_screen_spec(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the 15-row screen subset from the training protocol.

    Screen: 5 scenarios x 1 seed x 1 demand x 5 controllers = 25 rows by
    default, but the protocol declares screen_row_count=15, meaning only 3
    scenarios are used for screen.  We build from the protocol's screen_subset
    definition which specifies the seeds, demands, and controllers to use.
    """
    split = protocol["training_split"]
    subset = split.get("screen_subset", {})
    screen_seeds = subset.get("seeds", [split["seeds"][0]])
    screen_demands = subset.get("demand_multipliers", [1.0])
    screen_controllers = subset.get("controllers", [
        protocol["controller_id"],
        "max_pressure",
        "capacity_aware_pressure",
        "finite_storage_double_pressure",
        "switching_loss_max_pressure",
    ])
    spec = []
    for scenario_tag in split["scenarios"]:
        for demand_multiplier in screen_demands:
            contract = phase11.demand_multiplier_contract(float(demand_multiplier))
            for seed in screen_seeds:
                for controller in screen_controllers:
                    spec.append(
                        {
                            "profile": "screen",
                            "evidence_role": "v1_8_screen_only",
                            "gate_c_eligible": False,
                            "network": "arterial",
                            "scenario_tag": str(scenario_tag),
                            "controller": str(controller),
                            "seed": int(seed),
                            "steps": int(split["steps"]),
                            "warmup": int(split["warmup"]),
                            "action_interval": int(split["action_interval"]),
                            "demand_multiplier": float(demand_multiplier),
                            "demand_multiplier_contract": dict(contract),
                            "training_protocol_fingerprint": protocol.get("protocol_fingerprint", ""),
                        }
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


def _status(dry_run: bool, rows: list[dict[str, Any]],
            spec: list[dict[str, Any]], missing_reasons: list[str]) -> str:
    if dry_run:
        return "DRY_RUN"
    if missing_reasons or len(phase11._completed_rows(rows)) < len(spec):
        return "IN_PROGRESS"
    return "COMPLETE_PENDING_SELECTION"


def write_training_execution(
    *,
    protocol_path: Path,
    out_path: Path,
    route_json: Path,
    scaled_input_dir: Path,
    dry_run: bool = False,
    screen_only: bool = False,
    execution_row_limit: int | None = None,
    progress_out: Path | None = None,
    resume_progress: Path | None = None,
    max_new_rows: int | None = None,
) -> dict[str, Any]:
    protocol = load_protocol(protocol_path)

    if screen_only:
        spec = build_screen_spec(protocol)
    else:
        spec = build_training_spec(protocol)

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
        "experiment": "v1_8_training_execution",
        "status": _status(dry_run, rows, spec, missing_reasons),
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": False,
        "training_protocol_path": str(protocol_path),
        "training_protocol_status": protocol.get("status"),
        "training_protocol_fingerprint": protocol.get("protocol_fingerprint", ""),
        "controller_id": protocol.get("controller_id"),
        "required_baselines": list(protocol.get("required_baselines", [])),
        "controller_params": protocol.get("controller_params", {}),
        "training_grid": protocol.get("training_grid", {}),
        "eligibility_requirements": protocol.get("eligibility_requirements", {}),
        "selection_rule": protocol.get("selection_rule", {}),
        "safety_guards": protocol.get("safety_guards", {}),
        "profile": protocol["training_split"].get("profile", "training"),
        "screen_only": screen_only,
        "steps": int(protocol["training_split"]["steps"]),
        "warmup": int(protocol["training_split"]["warmup"]),
        "action_interval": int(protocol["training_split"]["action_interval"]),
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
            "allowed_now": "training-only method selection evidence",
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

    # Resolve output path defaults based on mode.
    if args.out is None:
        out_default = DEFAULT_SCREEN_OUT if args.screen_only else DEFAULT_OUT
        out_path = Path(out_default)
    else:
        out_path = Path(args.out)

    if args.progress_out is None and not args.dry_run:
        progress_default = DEFAULT_SCREEN_PROGRESS if args.screen_only else DEFAULT_PROGRESS
        progress_out = Path(progress_default)
    else:
        progress_out = Path(args.progress_out) if args.progress_out else None

    resume_progress = Path(args.resume_progress) if args.resume_progress else None

    payload = write_training_execution(
        protocol_path=Path(args.protocol),
        out_path=out_path,
        route_json=Path(args.route_json),
        scaled_input_dir=Path(args.scaled_input_dir),
        dry_run=args.dry_run,
        screen_only=args.screen_only,
        execution_row_limit=args.limit,
        progress_out=progress_out,
        resume_progress=resume_progress,
        max_new_rows=args.max_new_rows,
    )
    print(
        json.dumps(
            {
                "out": str(out_path),
                "status": payload["status"],
                "expected_rows": payload["expected_row_count"],
                "completed_rows": payload["actual_row_count"],
                "execution_mode": payload["execution_mode"],
                "screen_only": payload["screen_only"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
