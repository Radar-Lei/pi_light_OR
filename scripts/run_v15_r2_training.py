#!/usr/bin/env python3
"""Execute or resume the v1.5-r2 training protocol."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_phase11_paired_evidence as phase11

DEFAULT_PROTOCOL = "experiments/dual_sensitivity/v1_5_r2_training_protocol.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_r2_training_execution.json"
DEFAULT_PROGRESS = "experiments/dual_sensitivity/v1_5_r2_training_execution.progress.json"
DEFAULT_SCALED_INPUT_DIR = "experiments/dual_sensitivity/v1_5_r2_training_scaled_inputs"
REQUIREMENTS_COVERED = ["V15-R2-TRAIN-02", "V15-CLAIM-01"]


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
    parser.add_argument("--max-new-rows", type=int, default=None)
    return parser.parse_args()


def load_protocol(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Protocol {path} must contain a JSON object")
    return payload


def validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("experiment") not in {
        "v1_5_r2_training_protocol",
        "v1_5_r3_training_protocol",
        "v1_5_r4_training_protocol",
        "v1_5_r5_training_protocol",
        "v1_5_r6_training_protocol",
        "v1_5_r7_training_protocol",
        "v1_5_r8_training_protocol",
        "v1_5_r9_training_protocol",
        "v1_5_r10_training_protocol",
        "v1_5_r11_training_protocol",
        "v1_5_r12_training_protocol",
        "v1_5_r13_training_protocol",
        "v1_5_r14_training_protocol",
        "v1_5_r15_training_protocol",
        "v1_5_r16_training_protocol",
        "v1_5_r17_training_protocol",
        "v1_5_r18_training_protocol",
        "v1_5_r19_training_protocol",
        "v1_5_r20_training_protocol",
        "v1_5_r21_training_protocol",
        "v1_5_r22_training_protocol",
        "v1_5_r23_training_protocol",
        "v1_5_r24_training_protocol",
        "v1_5_r25_training_protocol",
        "v1_5_r26_training_protocol",
        "v1_5_r27_training_protocol",
        "v1_5_r28_training_protocol",
        "v1_5_r29_training_protocol",
        "v1_5_r30_training_protocol",
        "v1_5_r31_training_protocol",
        "v1_5_r32_training_protocol",
        "v1_5_r33_training_protocol",
        "v1_5_r34_training_protocol",
        "v1_5_r35_training_protocol",
        "v1_5_r36_training_protocol",
        "v1_5_r37_training_protocol",
        "v1_5_r38_training_protocol",
        "v1_5_r39_training_protocol",
        "v1_5_r40_training_protocol",
        "v1_5_r41_training_protocol",
        "v1_5_r42_training_protocol",
        "v1_5_r43_training_protocol",
        "v1_5_r44_training_protocol",
        "v1_5_r45_training_protocol",
        "v1_5_r46_training_protocol",
        "v1_5_r47_training_protocol",
        "v1_5_r48_training_protocol",
        "v1_5_r49_training_protocol",
        "v1_5_r50_training_protocol",
        "v1_5_r51_training_protocol",
        "v1_5_r52_training_protocol",
        "v1_5_r53_training_protocol",
        "v1_5_r54_training_protocol",
        "v1_5_r55_training_protocol",
        "v1_5_r56_training_protocol",
        "v1_5_r57_training_protocol",
        "v1_5_r58_training_protocol",
        "v1_5_r59_training_protocol",
        "v1_5_r60_training_protocol",
        "v1_5_r61_training_protocol",
        "v1_5_r62_training_protocol",
        "v1_5_r63_training_protocol",
        "v1_5_r64_training_protocol",
        "v1_5_r65_training_protocol",
        "v1_5_r66_training_protocol",
        "v1_5_r67_training_protocol",
        "v1_5_r68_training_protocol",
        "v1_5_r69_training_protocol",
        "v1_5_r70_training_protocol",
        "v1_5_r71_training_protocol",
        "v1_5_r72_training_protocol",
        "v1_5_r73_training_protocol",
        "v1_5_r74_training_protocol",
        "v1_5_r75_training_protocol",
        "v1_5_r76_training_protocol",
        "v1_5_r77_training_protocol",
        "v1_5_r78_training_protocol",
        "v1_5_r79_training_protocol",
        "v1_5_r80_training_protocol",
        "v1_5_r81_training_protocol",
        "v1_5_r82_training_protocol",
        "v1_5_r83_training_protocol",
        "v1_5_r84_training_protocol",
        "v1_5_r85_training_protocol",
        "v1_5_r86_training_protocol",
        "v1_5_r87_training_protocol",
        "v1_5_r88_training_protocol",
        "v1_5_r89_training_protocol",
        "v1_5_r90_training_protocol",
        "v1_5_r91_training_protocol",
        "v1_5_r92_training_protocol",
        "v1_5_r93_training_protocol",
        "v1_5_r94_training_protocol",
        "v1_5_r95_training_protocol",
        "v1_5_r96_training_protocol",
        "v1_5_r97_training_protocol",
        "v1_5_r98_training_protocol",
        "v1_5_r99_training_protocol",
        "v1_5_r100_training_protocol",
        "v1_5_r101_training_protocol",
        "v1_5_r102_training_protocol",
        "v1_5_r103_training_protocol",
        "v1_5_r104_training_protocol",
        "v1_5_r105_training_protocol",
        "v1_5_r106_training_protocol",
        "v1_5_r107_training_protocol",
        "v1_5_r108_training_protocol",
        "v1_5_r109_training_protocol",
        "v1_5_r110_training_protocol",
        "v1_5_r111_training_protocol",
        "v1_5_r112_training_protocol",
        "v1_5_r113_training_protocol",
        "v1_5_r114_training_protocol",
    }:
        raise ValueError("protocol is not a supported v1.5 training protocol")
    if protocol.get("status") != "TRAINING_LOCKED":
        raise ValueError("v1.5 training protocol is not TRAINING_LOCKED")
    controller = protocol.get("controller_id")
    if controller not in phase11.CONTROLLER_REGISTRY:
        raise ValueError(f"v1.5-r2 controller is not executable: {controller}")
    split = protocol.get("training_split")
    if not isinstance(split, dict):
        raise ValueError("v1.5 training protocol is missing training_split")
    controllers = set(split.get("controllers", []))
    missing = sorted({controller, *protocol.get("required_baselines", [])} - controllers)
    if missing:
        raise ValueError(f"v1.5 training split is missing required controllers: {missing}")
    for field in ["scenarios", "seeds", "demand_multipliers", "steps", "warmup", "action_interval", "expected_row_count"]:
        if not split.get(field):
            raise ValueError(f"v1.5 training_split is missing {field}")


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
                            "evidence_role": f"{protocol['experiment'].replace('_protocol', '')}_only",
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
                            "training_protocol_fingerprint": protocol["protocol_fingerprint"],
                        }
                    )
    expected = int(split["expected_row_count"])
    if len(spec) != expected:
        raise ValueError(f"v1.5 training spec row count {len(spec)} does not match expected_row_count={expected}")
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
    return "COMPLETE_PENDING_SELECTION"


def write_training_execution(
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
    spec = build_training_spec(protocol)
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
        "experiment": str(protocol.get("experiment", "v1_5_r2_training_protocol")).replace("_protocol", "_execution"),
        "status": _status(dry_run, rows, spec, missing_reasons),
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": False,
        "training_protocol_path": str(protocol_path),
        "training_protocol_status": protocol.get("status"),
        "training_protocol_fingerprint": protocol.get("protocol_fingerprint"),
        "controller_id": protocol.get("controller_id"),
        "required_baselines": list(protocol.get("required_baselines", [])),
        "controller_params": protocol.get("controller_params", {}),
        "selection_rule": protocol.get("selection_rule", {}),
        "profile": protocol["training_split"].get("profile", "training"),
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
    payload = write_training_execution(
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
