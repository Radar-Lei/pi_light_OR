#!/usr/bin/env python3
"""Execute v1.7 CFS-PD-MPC ablation experiments.

Runs SUMO closed-loop simulations for the v1.7 controller plus four ablation
variants, each removing one component to prove component-level contribution.

Ablation variants:
  - v17_ablation_no_completion:           kappa_completion=0
  - v17_ablation_no_capacity_correction:  capacity_correction_activation=inf
  - v17_ablation_always_correct:          capacity_correction_activation=0
  - v17_ablation_no_safety:               bypass safe-set fallback

Design:
  - 5 variants (full v1.7 + 4 ablations) x 3 scenarios x 3 seeds x 1 demand
    = 45 rows
  - Uses the same arterial training scenarios as v1.7 training protocol.
  - Outputs auditable JSON to experiments/dual_sensitivity/v1_7_ablation_evidence.json

Supports:
  --dry-run          Build the spec without executing SUMO.
  --resume-progress  Resume from a previous progress checkpoint.
  --max-new-rows     Limit the number of new rows attempted in this run.
  --screen-only      Run only the 5-row screen (1 scenario, 1 seed).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_phase11_paired_evidence as phase11

DEFAULT_OUT = "experiments/dual_sensitivity/v1_7_ablation_evidence.json"
DEFAULT_PROGRESS = "experiments/dual_sensitivity/v1_7_ablation_evidence.progress.json"
DEFAULT_ROUTE_JSON = "experiments/dual_sensitivity/block3_static_kill_gate.json"
DEFAULT_SCALED_INPUT_DIR = "experiments/dual_sensitivity/v1_7_training_scaled_inputs"

ABLATION_VARIANTS = [
    "finite_storage_completion_primal_dual_v1_7",
    "v17_ablation_no_completion",
    "v17_ablation_no_capacity_correction",
    "v17_ablation_always_correct",
    "v17_ablation_no_safety",
]

ABLATION_SCENARIOS = [
    "arterial_v1_5_storage_activation",
    "arterial_spillback_stress",
    "arterial_downstream_blockage",
]

ABLATION_SEEDS = [20261701, 20261702, 20261703]
ABLATION_DEMAND = 1.0

ABLATION_STEPS = 3600
ABLATION_WARMUP = 900
ABLATION_ACTION_INTERVAL = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute v1.7 ablation experiments")
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--route-json", default=DEFAULT_ROUTE_JSON)
    parser.add_argument("--scaled-input-dir", default=DEFAULT_SCALED_INPUT_DIR)
    parser.add_argument("--progress-out", default=None)
    parser.add_argument("--resume-progress", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--screen-only", action="store_true",
                        help="Execute only 5-row screen subset (1 scenario x 1 seed x 1 demand x 5 variants)")
    parser.add_argument("--execution-row-limit", type=int, default=None)
    parser.add_argument("--max-new-rows", type=int, default=None)
    return parser.parse_args()


def build_ablation_spec(
    *,
    screen_only: bool = False,
) -> list[dict[str, Any]]:
    """Build the 45-row (or 5-row screen) ablation spec."""
    scenarios = ABLATION_SCENARIOS[:1] if screen_only else ABLATION_SCENARIOS
    seeds = ABLATION_SEEDS[:1] if screen_only else ABLATION_SEEDS
    controllers = ABLATION_VARIANTS

    contract = phase11.demand_multiplier_contract(ABLATION_DEMAND)
    spec: list[dict[str, Any]] = []
    for scenario_tag in scenarios:
        for seed in seeds:
            for controller in controllers:
                spec.append({
                    "profile": "ablation",
                    "evidence_role": "v1_7_ablation",
                    "gate_c_eligible": False,
                    "network": "arterial",
                    "scenario_tag": str(scenario_tag),
                    "controller": str(controller),
                    "seed": int(seed),
                    "steps": ABLATION_STEPS,
                    "warmup": ABLATION_WARMUP,
                    "action_interval": ABLATION_ACTION_INTERVAL,
                    "demand_multiplier": ABLATION_DEMAND,
                    "demand_multiplier_contract": dict(contract),
                })

    expected = len(scenarios) * len(seeds) * len(controllers)
    if len(spec) != expected:
        raise ValueError(
            f"ablation spec row count {len(spec)} does not match expected {expected}"
        )
    return spec


def build_row_audit(
    rows: list[dict[str, Any]],
    spec: list[dict[str, Any]],
) -> dict[str, Any]:
    """Audit completed vs expected rows."""
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


def write_ablation_execution(
    *,
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
    """Build spec, execute rows, and write ablation evidence JSON."""
    spec = build_ablation_spec(screen_only=screen_only)
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

    # --- Build per-variant summary ---
    variant_summary: dict[str, dict[str, Any]] = {}
    completed = phase11._completed_rows(rows)
    for variant in ABLATION_VARIANTS:
        variant_rows = [r for r in completed if r.get("controller") == variant]
        metric_fields = [
            "delay", "throughput", "unfinished_vehicle_count",
            "spillback_count", "blocking_count", "switching_count",
        ]
        metrics_agg: dict[str, dict[str, float]] = {}
        for mf in metric_fields:
            values = [float(r[mf]) for r in variant_rows if mf in r and r[mf] is not None]
            if values:
                metrics_agg[mf] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }
        variant_summary[variant] = {
            "completed_rows": len(variant_rows),
            "total_rows_expected": len(spec) // len(ABLATION_VARIANTS),
            "metrics": metrics_agg,
        }

    payload = {
        "experiment": "v1_7_ablation_evidence",
        "status": _status(dry_run, rows, spec, missing_reasons),
        "screen_only": screen_only,
        "dry_run": dry_run,
        "execution_mode": execution_mode,
        "variants": ABLATION_VARIANTS,
        "scenarios": ABLATION_SCENARIOS,
        "seeds": ABLATION_SEEDS,
        "demand_multiplier": ABLATION_DEMAND,
        "steps": ABLATION_STEPS,
        "warmup": ABLATION_WARMUP,
        "action_interval": ABLATION_ACTION_INTERVAL,
        "expected_row_count": len(spec),
        "actual_row_count": row_audit["completed_row_count"],
        "all_rows_executed": row_audit["completed_row_count"] == len(spec) and not missing_reasons,
        "missing_row_reasons": missing_reasons,
        "row_audit": row_audit,
        "variant_summary": variant_summary,
        "route_metadata": route_metadata,
        "scenario_results": rows,
        "claim_scope": {
            "allowed_now": "ablation component-contribution evidence only",
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
    payload = write_ablation_execution(
        out_path=Path(args.out),
        route_json=Path(args.route_json),
        scaled_input_dir=Path(args.scaled_input_dir),
        dry_run=args.dry_run,
        screen_only=args.screen_only,
        execution_row_limit=args.execution_row_limit,
        progress_out=Path(args.progress_out) if args.progress_out else None,
        resume_progress=Path(args.resume_progress) if args.resume_progress else None,
        max_new_rows=args.max_new_rows,
    )
    print(json.dumps(
        {
            "out": args.out,
            "status": payload["status"],
            "expected_rows": payload["expected_row_count"],
            "completed_rows": payload["actual_row_count"],
            "execution_mode": payload["execution_mode"],
            "screen_only": payload["screen_only"],
            "variants": payload["variants"],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
