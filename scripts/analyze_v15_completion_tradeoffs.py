#!/usr/bin/env python3
"""Analyze v1.5 training execution tradeoffs between completion safety and composite cost."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CORE_BASELINES = ("max_pressure", "capacity_aware_pressure", "finite_storage_double_pressure")
DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_completion_tradeoff_analysis.json"
REQUIREMENTS_COVERED = ["V15-COMPLETION-TRADEOFF-01", "V15-CLAIM-01"]


def training_execution_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"v1_5_r(\d+)_training_execution\.json$", path.name)
    return (int(match.group(1)) if match else 10_000, str(path))


def default_inputs() -> list[str]:
    root = Path("experiments/dual_sensitivity")
    return [
        str(path)
        for path in sorted(root.glob("v1_5_r*_training_execution.json"), key=training_execution_sort_key)
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", default=default_inputs())
    parser.add_argument("--out", default=DEFAULT_OUT)
    return parser.parse_args()


def load_execution(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def objective_cost(row: dict[str, Any]) -> float | None:
    components = row.get("objective_components")
    if isinstance(components, dict) and components:
        return float(sum(float(value) for value in components.values()))
    value = row.get("composite_finite_storage_operating_cost")
    return float(value) if value is not None else None


def completed_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("scenario_results", [])
    return [
        row
        for row in rows
        if isinstance(row, dict)
        and row.get("scenario_status") == "completed"
        and row.get("feasibility_status") in {"run", "completed"}
    ]


def scenario_key(row: dict[str, Any]) -> tuple[str, int, float]:
    return (
        str(row.get("scenario_tag")),
        int(row.get("seed")),
        float(row.get("demand_multiplier", 1.0)),
    )


def analyze_execution(path: Path) -> dict[str, Any]:
    payload = load_execution(path)
    controller_id = str(payload.get("controller_id"))
    grouped: dict[tuple[str, int, float], dict[str, dict[str, Any]]] = {}
    for row in completed_rows(payload):
        grouped.setdefault(scenario_key(row), {})[str(row.get("controller"))] = row

    cases = []
    for key, rows_by_controller in sorted(grouped.items()):
        candidate = rows_by_controller.get(controller_id)
        if candidate is None:
            continue
        baselines = {
            name: rows_by_controller.get(name)
            for name in CORE_BASELINES
            if rows_by_controller.get(name) is not None
        }
        if set(baselines) != set(CORE_BASELINES):
            continue
        candidate_unfinished = float(candidate.get("unfinished_vehicle_count", 0.0))
        candidate_cost = objective_cost(candidate)
        baseline_unfinished = {
            name: float(row.get("unfinished_vehicle_count", 0.0))
            for name, row in baselines.items()
        }
        baseline_cost = {
            name: objective_cost(row)
            for name, row in baselines.items()
        }
        unfinished_oracle = min(baseline_unfinished, key=lambda name: (baseline_unfinished[name], name))
        composite_oracle = min(
            (name for name, value in baseline_cost.items() if value is not None),
            key=lambda name: (float(baseline_cost[name]), name),
        )
        min_unfinished = baseline_unfinished[unfinished_oracle]
        max_unfinished = max(baseline_unfinished.values())
        finite_storage_safe = all(candidate_unfinished <= value for value in baseline_unfinished.values())
        composite_beats_all_core = (
            candidate_cost is not None
            and all(candidate_cost < float(value) for value in baseline_cost.values() if value is not None)
        )
        cases.append(
            {
                "scenario_tag": key[0],
                "seed": key[1],
                "demand_multiplier": key[2],
                "controller_id": controller_id,
                "candidate_unfinished_vehicle_count": candidate_unfinished,
                "candidate_composite_cost": candidate_cost,
                "baseline_unfinished_vehicle_count": baseline_unfinished,
                "baseline_composite_cost": baseline_cost,
                "candidate_safety_excess_vs_best_core": candidate_unfinished - min_unfinished,
                "candidate_safe_against_all_core_unfinished": finite_storage_safe,
                "candidate_composite_beats_all_core": composite_beats_all_core,
                "core_unfinished_oracle": unfinished_oracle,
                "core_composite_oracle": composite_oracle,
                "core_unfinished_range": max_unfinished - min_unfinished,
                "core_oracles_disagree": unfinished_oracle != composite_oracle,
            }
        )

    unsafe = [case for case in cases if not case["candidate_safe_against_all_core_unfinished"]]
    composite_wins = [case for case in cases if case["candidate_composite_beats_all_core"]]
    oracle_conflicts = [case for case in cases if case["core_oracles_disagree"]]
    return {
        "input": str(path),
        "experiment": payload.get("experiment"),
        "controller_id": controller_id,
        "case_count": len(cases),
        "unsafe_case_count": len(unsafe),
        "composite_win_case_count": len(composite_wins),
        "oracle_conflict_count": len(oracle_conflicts),
        "max_candidate_safety_excess_vs_best_core": max(
            (float(case["candidate_safety_excess_vs_best_core"]) for case in cases),
            default=0.0,
        ),
        "cases": cases,
    }


def build_analysis(paths: list[Path]) -> dict[str, Any]:
    executions = [analyze_execution(path) for path in paths]
    cases = [case for execution in executions for case in execution["cases"]]
    unsafe = [case for case in cases if not case["candidate_safe_against_all_core_unfinished"]]
    composite_wins = [case for case in cases if case["candidate_composite_beats_all_core"]]
    both = [
        case
        for case in cases
        if case["candidate_safe_against_all_core_unfinished"] and case["candidate_composite_beats_all_core"]
    ]
    oracle_conflicts = [case for case in cases if case["core_oracles_disagree"]]
    return {
        "experiment": "v1_5_completion_tradeoff_analysis",
        "status": "ANALYZED",
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": False,
        "input_count": len(paths),
        "execution_count": len(executions),
        "case_count": len(cases),
        "unsafe_case_count": len(unsafe),
        "composite_win_case_count": len(composite_wins),
        "safe_and_composite_win_case_count": len(both),
        "oracle_conflict_count": len(oracle_conflicts),
        "executions": executions,
        "interpretation": {
            "completion_safety_is_not_solved": bool(unsafe),
            "core_baselines_have_completion_composite_tradeoff": bool(oracle_conflicts),
            "why_no_claim": "execution tradeoff analysis is diagnostic training evidence, not confirmatory holdout evidence",
        },
        "claim_scope": {
            "closed_loop_superiority_claim_allowed": False,
            "confirmatory_holdout_allowed": False,
        },
    }


def write_analysis(inputs: list[Path], out: Path) -> dict[str, Any]:
    payload = build_analysis(inputs)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_analysis([Path(path) for path in args.inputs], Path(args.out))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "out": args.out,
                "case_count": payload["case_count"],
                "unsafe_case_count": payload["unsafe_case_count"],
                "oracle_conflict_count": payload["oracle_conflict_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
