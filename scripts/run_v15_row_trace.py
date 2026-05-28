#!/usr/bin/env python3
"""Rerun one executed v1.5 row and capture a per-decision trace."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_closed_loop_sumo import run_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--controller", required=True)
    parser.add_argument("--scenario-tag", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--demand-multiplier", type=float, required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def load_execution(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def find_row(
    payload: dict[str, Any],
    *,
    controller: str,
    scenario_tag: str,
    seed: int,
    demand_multiplier: float,
) -> dict[str, Any]:
    for row in payload.get("scenario_results", []):
        if not isinstance(row, dict):
            continue
        if row.get("controller") != controller:
            continue
        if row.get("scenario_tag") != scenario_tag:
            continue
        if int(row.get("seed", -1)) != seed:
            continue
        if float(row.get("demand_multiplier", 0.0)) != demand_multiplier:
            continue
        return row
    raise ValueError("target row not found in input artifact")


def main() -> None:
    args = parse_args()
    payload = load_execution(Path(args.input))
    row = find_row(
        payload,
        controller=args.controller,
        scenario_tag=args.scenario_tag,
        seed=args.seed,
        demand_multiplier=args.demand_multiplier,
    )
    route_metadata = {
        "route_decision": str(row.get("route_decision", "")),
        "route_confidence": str(row.get("route_confidence", "")),
        "route_json": str(row.get("route_json", "")),
    }
    traced = run_experiment(
        network=str(row["network"]),
        controller=str(row["controller"]),
        seed=int(row["seed"]),
        steps=int(row["steps"]),
        warmup=int(row["warmup"]),
        action_interval=int(row["action_interval"]),
        route_metadata=route_metadata,
        scenario_tag=str(row["scenario_tag"]),
        sumocfg_override=str(row["generated_sumocfg"]),
        collect_decision_trace=True,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(traced, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": traced["scenario_status"],
                "out": str(out),
                "decision_trace_count": len(traced.get("decision_trace", [])),
                "unfinished_vehicle_count": traced.get("unfinished_vehicle_count"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
