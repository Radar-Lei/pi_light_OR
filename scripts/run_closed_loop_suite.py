#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from run_closed_loop_sumo import CLAIM_FRAMING, METRIC_FIELDS, load_route_metadata, run_experiment

CORE_BASELINES = {
    "fixed_time",
    "max_pressure",
    "capacity_aware_pressure",
    "raw_neighbor_symbolic",
    "all_neighbor_symbolic",
    "random_permuted_dual",
}
NON_FIXED_CORE_BASELINES = CORE_BASELINES - {"fixed_time"}
DEFAULT_CONTROLLERS = [
    "fixed_time",
    "actuated_local_pressure",
    "max_pressure",
    "capacity_aware_pressure",
    "local_pilight",
    "raw_neighbor_symbolic",
    "all_neighbor_symbolic",
    "random_permuted_dual",
    "full_dual_symbolic",
]
SCENARIOS = [
    ("single_sanity", "single"),
    ("arterial_main", "arterial"),
    ("grid_scalability", "grid_4x4"),
    ("arterial_demand_shift", "arterial"),
    ("arterial_bottleneck_failure_mode", "arterial"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["smoke", "main"], default="smoke")
    parser.add_argument("--controllers", nargs="+", default=DEFAULT_CONTROLLERS)
    parser.add_argument("--arterial-seeds", nargs="+", type=int, default=[20260523, 20260524, 20260525, 20260526, 20260527])
    parser.add_argument("--grid-seeds", nargs="+", type=int, default=[20260601, 20260602, 20260603, 20260604, 20260605])
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--warmup", type=int, default=60)
    parser.add_argument("--action-interval", type=int, default=10)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block4_closed_loop_suite.json")
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    return parser.parse_args()


def build_suite_spec(
    profile: str,
    controllers: list[str],
    arterial_seeds: list[int],
    grid_seeds: list[int],
    steps: int,
    warmup: int,
    action_interval: int,
) -> list[dict[str, Any]]:
    if profile == "smoke":
        seeds_by_scenario = {
            "single_sanity": arterial_seeds[:1],
            "arterial_main": arterial_seeds[:1],
            "grid_scalability": grid_seeds[:1],
            "arterial_demand_shift": arterial_seeds[:1],
            "arterial_bottleneck_failure_mode": arterial_seeds[:1],
        }
        controllers_by_scenario = {name: controllers for name, _ in SCENARIOS}
    else:
        seeds_by_scenario = {
            "single_sanity": arterial_seeds[:1],
            "arterial_main": arterial_seeds[:5],
            "grid_scalability": grid_seeds[:5],
            "arterial_demand_shift": arterial_seeds[:1],
            "arterial_bottleneck_failure_mode": arterial_seeds[:1],
        }
        controllers_by_scenario = {
            "single_sanity": controllers,
            "arterial_main": controllers,
            "grid_scalability": controllers,
            "arterial_demand_shift": [c for c in controllers if c in {"fixed_time", "max_pressure", "capacity_aware_pressure"}],
            "arterial_bottleneck_failure_mode": [c for c in controllers if c in {"max_pressure", "capacity_aware_pressure"}],
        }
    spec = []
    for scenario_tag, network in SCENARIOS:
        for seed in seeds_by_scenario[scenario_tag]:
            for controller in controllers_by_scenario[scenario_tag]:
                spec.append(
                    {
                        "network": network,
                        "scenario_tag": scenario_tag,
                        "controller": controller,
                        "seed": int(seed),
                        "steps": int(steps),
                        "warmup": int(warmup),
                        "action_interval": int(action_interval),
                    }
                )
    return spec


def ci(values: list[float]) -> dict[str, float | int]:
    n = len(values)
    mean = statistics.fmean(values) if values else 0.0
    if n <= 1:
        se = 0.0
    else:
        se = statistics.stdev(values) / math.sqrt(n)
    delta = 1.96 * se
    return {"n_seeds": n, "mean": float(mean), "std_error": float(se), "ci95_low": float(mean - delta), "ci95_high": float(mean + delta)}


def aggregate_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("scenario_status") != "completed" or row.get("feasibility_status") not in {"run", "completed"}:
            continue
        groups[(str(row["network"]), str(row["scenario_tag"]), str(row["controller"]))].append(row)
    aggregates = []
    for (network, scenario_tag, controller), group in sorted(groups.items()):
        item: dict[str, Any] = {"network": network, "scenario_tag": scenario_tag, "controller": controller}
        seeds = sorted({int(row["seed"]) for row in group})
        item["seeds"] = seeds
        item["n_seeds"] = len(seeds)
        for metric in METRIC_FIELDS:
            vals = [float(row.get(metric, 0.0)) for row in group]
            item[metric] = ci(vals)
        aggregates.append(item)
    return aggregates


def baseline_coverage(rows: list[dict[str, Any]], controllers: list[str]) -> dict[str, dict[str, str]]:
    coverage = {}
    for controller in controllers:
        ctrl_rows = [row for row in rows if row.get("controller") == controller]
        run = any(row.get("feasibility_status") in {"run", "completed"} for row in ctrl_rows)
        if run:
            coverage[controller] = {"status": "run"}
        else:
            reason = next((str(row.get("unsupported_reason")) for row in ctrl_rows if row.get("unsupported_reason")), "no rows generated")
            coverage[controller] = {"status": "not_feasible", "unsupported_reason": reason}
    return coverage


def valid_completed_row(row: dict[str, Any]) -> bool:
    return (
        row.get("scenario_status") == "completed"
        and row.get("feasibility_status") in {"run", "completed"}
        and float(row.get("completion_rate", 0.0)) > 0.0
        and int(row.get("completed_vehicles", 0)) > 0
    )


def controller_actuation_evidence(rows: list[dict[str, Any]], scenario: str, controller: str) -> dict[str, Any]:
    if controller == "fixed_time":
        return {"passed": True, "switching_rows": "not_required"}
    relevant = [row for row in rows if row.get("scenario_tag") == scenario and row.get("controller") == controller]
    switching_rows = sum(1 for row in relevant if int(row.get("switching_count", 0)) > 0)
    no_switch_rows = sum(1 for row in relevant if row.get("no_switch_reason"))
    return {"passed": switching_rows > 0 or no_switch_rows == len(relevant), "switching_rows": switching_rows, "no_switch_rows": no_switch_rows}


def completion_gates(rows: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [row for row in rows if valid_completed_row(row)]
    gates: dict[str, Any] = {}
    for scenario in ["arterial_main", "grid_scalability"]:
        gates[scenario] = {}
        for controller in sorted(CORE_BASELINES):
            seeds = {int(row["seed"]) for row in completed if row.get("scenario_tag") == scenario and row.get("controller") == controller}
            actuation = controller_actuation_evidence(completed, scenario, controller)
            gates[scenario][controller] = {"completed_seeds": len(seeds), "actuation": actuation, "passed": len(seeds) >= 5 and bool(actuation["passed"])}
    gates["demand_shift_real_mechanism"] = any(
        row.get("scenario_tag") == "arterial_demand_shift"
        and row.get("demand_shift_mechanism")
        and row.get("demand_shift_mechanism") != "seed_only"
        and int(row.get("demand_shift_inserted_vehicles", 0)) >= max(2, (int(row.get("steps", 0)) - int(row.get("warmup", 0)) + 29) // 30)
        for row in completed
    )
    gates["failure_mode_real_mechanism"] = any(
        row.get("scenario_tag") == "arterial_bottleneck_failure_mode"
        and row.get("failure_mode_mechanism")
        and row.get("failure_mode_target_edge")
        and float(row.get("failure_mode_target_max_vehicles", 0.0)) > 0.0
        for row in completed
    )
    gates["failure_mode_pressure_rows"] = all(
        any(
            row.get("scenario_tag") == "arterial_bottleneck_failure_mode"
            and row.get("controller") == controller
            and row.get("failure_mode_mechanism")
            and row.get("failure_mode_target_edge")
            and float(row.get("failure_mode_target_max_vehicles", 0.0)) > 0.0
            for row in completed
        )
        for controller in ["max_pressure", "capacity_aware_pressure"]
    )
    return gates


def gates_pass(gates: dict[str, Any]) -> bool:
    seed_gates = []
    for scenario in ["arterial_main", "grid_scalability"]:
        seed_gates.extend(item["passed"] for item in gates[scenario].values())
    return all(seed_gates) and bool(gates["demand_shift_real_mechanism"]) and bool(gates["failure_mode_real_mechanism"]) and bool(gates["failure_mode_pressure_rows"])


def main() -> None:
    args = parse_args()
    route_metadata = load_route_metadata(Path(args.route_json))
    spec = build_suite_spec(args.profile, args.controllers, args.arterial_seeds, args.grid_seeds, args.steps, args.warmup, args.action_interval)
    rows = [run_experiment(**item, route_metadata=route_metadata) for item in spec]
    gates = completion_gates(rows)
    completion_gates_passed = gates_pass(gates) if args.profile == "main" else False
    payload = {
        "experiment": "block4_closed_loop_suite",
        "status": "PASSED" if completion_gates_passed else "SMOKE_ONLY" if args.profile == "smoke" else "FAILED",
        **route_metadata,
        "claim_framing": CLAIM_FRAMING,
        "profile": args.profile,
        "scenario_results": rows,
        "aggregates": aggregate_results(rows),
        "baseline_coverage": baseline_coverage(rows, args.controllers),
        "completion_gates": gates,
        "completion_gates_passed": completion_gates_passed,
        "metric_schema": {field: "CLOP-04 metric" for field in METRIC_FIELDS},
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "rows": len(rows), "aggregates": len(payload["aggregates"]), "completion_gates_passed": payload["completion_gates_passed"]}, indent=2))


if __name__ == "__main__":
    main()
