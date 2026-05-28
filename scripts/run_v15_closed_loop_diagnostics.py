#!/usr/bin/env python3
"""Closed-loop v1.5 storage-activation diagnostics."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_closed_loop_sumo import load_route_metadata, run_experiment

DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_closed_loop_diagnostics.json"
DEFAULT_ROUTE_JSON = "experiments/dual_sensitivity/block3_static_kill_gate.json"
CONTROLLER_ID = "finite_storage_dynamic_primal_dual_v1_5"
DEFAULT_SCENARIOS = ["arterial_v1_5_storage_activation", "arterial_downstream_blockage"]
REQUIREMENTS_COVERED = ["V15-DIAG-01", "V15-DIAG-02", "V15-CLAIM-01"]
ACTION_CHANGE_TARGET = 0.20


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None, help="Existing suite/diagnostic JSON to analyze instead of running SUMO.")
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--route-json", default=DEFAULT_ROUTE_JSON)
    parser.add_argument("--scenarios", nargs="+", default=DEFAULT_SCENARIOS)
    parser.add_argument("--seed", type=int, default=20260527)
    parser.add_argument("--steps", type=int, default=120)
    parser.add_argument("--warmup", type=int, default=20)
    parser.add_argument("--action-interval", type=int, default=10)
    return parser.parse_args()


def _scenario_network(scenario_tag: str) -> str:
    if scenario_tag == "grid_scalability":
        return "grid_4x4"
    if scenario_tag == "single_sanity":
        return "single"
    return "arterial"


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    if isinstance(payload.get("diagnostic_rows"), list):
        rows = payload["diagnostic_rows"]
    else:
        rows = payload.get("scenario_results", [])
    if not isinstance(rows, list):
        raise ValueError(f"{path} is missing diagnostic_rows or scenario_results")
    return [row for row in rows if isinstance(row, dict)]


def run_diagnostic_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    route_metadata = load_route_metadata(Path(args.route_json))
    rows = []
    for scenario_tag in args.scenarios:
        rows.append(
            run_experiment(
                network=_scenario_network(scenario_tag),
                controller=CONTROLLER_ID,
                seed=args.seed,
                steps=args.steps,
                warmup=args.warmup,
                action_interval=args.action_interval,
                route_metadata=route_metadata,
                scenario_tag=scenario_tag,
            )
        )
    return rows


def _empty_counts() -> dict[str, int]:
    return {
        "downstream_storage": 0,
        "spillback": 0,
        "switching": 0,
        "service": 0,
        "incident": 0,
        "storage_price": 0,
        "cascade_price": 0,
        "release": 0,
        "service_age": 0,
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    diagnostic_rows = [row for row in rows if row.get("controller") == CONTROLLER_ID]
    total_decisions = 0
    changed = 0
    binding = 0
    binding_changed = 0
    selected_counts = _empty_counts()
    any_phase_counts = _empty_counts()
    max_occupancy = 0.0
    min_residual = 1.0
    row_summaries = []

    for row in diagnostic_rows:
        action = row.get("action_decomposition", {})
        summary = action.get("decision_summary", {}) if isinstance(action, dict) else {}
        if not isinstance(summary, dict):
            summary = {}
        row_total = int(summary.get("total_decisions", 0))
        row_changed = int(summary.get("action_changed_relative_to_pressure_count", 0))
        row_binding = int(summary.get("binding_decision_count", 0))
        row_binding_changed = int(summary.get("binding_action_changed_count", 0))
        total_decisions += row_total
        changed += row_changed
        binding += row_binding
        binding_changed += row_binding_changed
        max_occupancy = max(max_occupancy, float(summary.get("max_occupancy_ratio_observed", 0.0)))
        min_residual = min(min_residual, float(summary.get("min_residual_ratio_observed", 1.0)))
        for key, target in [
            ("selected_component_nonzero_counts", selected_counts),
            ("any_phase_component_nonzero_counts", any_phase_counts),
        ]:
            counts = summary.get(key, {})
            if isinstance(counts, dict):
                for field in target:
                    target[field] += int(counts.get(field, 0))
        row_summaries.append(
            {
                "scenario_tag": row.get("scenario_tag"),
                "seed": row.get("seed"),
                "total_decisions": row_total,
                "action_change_rate": float(summary.get("action_change_rate", 0.0)),
                "binding_decision_rate": float(summary.get("binding_decision_rate", 0.0)),
                "binding_action_change_rate": float(summary.get("binding_action_change_rate", 0.0)),
                "max_occupancy_ratio_observed": float(summary.get("max_occupancy_ratio_observed", 0.0)),
                "min_residual_ratio_observed": float(summary.get("min_residual_ratio_observed", 1.0)),
            }
        )

    action_change_rate = changed / total_decisions if total_decisions else 0.0
    binding_action_change_rate = binding_changed / binding if binding else 0.0
    binding_decision_rate = binding / total_decisions if total_decisions else 0.0
    criteria = {
        "diagnostic_rows_present": bool(diagnostic_rows),
        "decision_summary_present": total_decisions > 0,
        "binding_state_observed": binding > 0 and max_occupancy >= 0.85 and min_residual <= 0.15,
        "action_change_rate_target_met": action_change_rate >= ACTION_CHANGE_TARGET,
        "storage_or_spillback_terms_active": any_phase_counts["downstream_storage"] > 0 or any_phase_counts["spillback"] > 0 or any_phase_counts["storage_price"] > 0,
        "dynamic_terms_active": any_phase_counts["storage_price"] > 0 and (any_phase_counts["cascade_price"] > 0 or any_phase_counts["release"] > 0),
    }
    return {
        "rows_analyzed": len(diagnostic_rows),
        "total_decisions": total_decisions,
        "action_changed_relative_to_pressure_count": changed,
        "binding_decision_count": binding,
        "binding_action_changed_count": binding_changed,
        "action_change_rate": float(action_change_rate),
        "binding_action_change_rate": float(binding_action_change_rate),
        "binding_decision_rate": float(binding_decision_rate),
        "selected_component_nonzero_counts": selected_counts,
        "any_phase_component_nonzero_counts": any_phase_counts,
        "max_occupancy_ratio_observed": float(max_occupancy),
        "min_residual_ratio_observed": float(min_residual),
        "criteria": criteria,
        "row_summaries": row_summaries,
    }


def build_payload(rows: list[dict[str, Any]], *, source: str) -> dict[str, Any]:
    summary = summarize_rows(rows)
    status = "PASSED" if all(bool(value) for value in summary["criteria"].values()) else "FAILED"
    return {
        "experiment": "v1_5_closed_loop_diagnostics",
        "status": status,
        "generated_by": "scripts/run_v15_closed_loop_diagnostics.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "controller_id": CONTROLLER_ID,
        "requirements_covered": REQUIREMENTS_COVERED,
        "action_change_target": ACTION_CHANGE_TARGET,
        "summary": summary,
        "claim_scope": {
            "allowed": "closed-loop diagnostic evidence for storage activation and action-separation readiness",
            "not_claimed": [
                "locked_holdout_superiority",
                "journal_grade_performance_evidence",
                "deployment_readiness",
            ],
        },
        "diagnostic_rows": rows,
    }


def main() -> None:
    args = parse_args()
    if args.input:
        input_path = Path(args.input)
        rows = load_rows(input_path)
        source = str(input_path)
    else:
        rows = run_diagnostic_rows(args)
        source = "executed_short_sumo_diagnostic"
    payload = build_payload(rows, source=source)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": str(out_path), "total_decisions": payload["summary"]["total_decisions"]}, indent=2))
    if payload["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
