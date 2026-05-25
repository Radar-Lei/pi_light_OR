#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from finite_storage_schema import FINITE_STORAGE_STATE_FIELDS, OBJECTIVE_COMPONENT_FIELDS
from run_closed_loop_sumo import CONTROLLER_REGISTRY, METRIC_FIELDS, NOT_FEASIBLE_CONTROLLERS, load_route_metadata, run_experiment

PHASE10_CLAIM_FRAMING = "Phase 10 is baseline/stress-suite coverage capability evidence only, not Gate C, paired-seed dominance evidence, long-horizon statistics, or manuscript claims."

REQUIRED_STRONG_BASELINES = [
    "fixed_time",
    "actuated_local_pressure",
    "max_pressure",
    "capacity_aware_pressure",
    "cycle_pressure",
    "finite_storage_double_pressure",
    "finite_storage_primal_dual",
]
NOT_FEASIBLE_GUARD_CONTROLLERS = ["local_pilight", "full_dual_symbolic"]

CORE_BASELINES = {
    "fixed_time",
    "actuated_local_pressure",
    "max_pressure",
    "capacity_aware_pressure",
    "cycle_pressure",
    "finite_storage_double_pressure",
    "finite_storage_primal_dual",
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
    "cycle_pressure",
    "finite_storage_double_pressure",
    "finite_storage_primal_dual",
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
    ("arterial_downstream_blockage", "arterial"),
    ("arterial_spillback_stress", "arterial"),
    ("arterial_incident_capacity_drop", "arterial"),
    ("arterial_oversaturation", "arterial"),
    ("arterial_turning_shock", "arterial"),
    ("arterial_switching_loss_sensitive", "arterial"),
]
STRESS_SCENARIO_CATEGORIES = {
    "downstream_blockage": ["arterial_downstream_blockage"],
    "spillback": ["arterial_spillback_stress"],
    "incident_capacity_drop": ["arterial_incident_capacity_drop", "arterial_bottleneck_failure_mode"],
    "oversaturation": ["arterial_oversaturation"],
    "turning_shock": ["arterial_turning_shock", "arterial_demand_shift"],
    "switching_loss_sensitive": ["arterial_switching_loss_sensitive"],
}
STRESS_SCENARIO_MECHANISMS = {
    "arterial_downstream_blockage": "edge_speed_reduction",
    "arterial_spillback_stress": "edge_speed_reduction",
    "arterial_incident_capacity_drop": "edge_speed_reduction",
    "arterial_bottleneck_failure_mode": "edge_speed_reduction",
    "arterial_oversaturation": "traci_vehicle_insertion",
    "arterial_turning_shock": "traci_vehicle_insertion",
    "arterial_demand_shift": "traci_vehicle_insertion",
    "arterial_switching_loss_sensitive": "short_action_interval_switching_audit",
}
PHASE10_SCOPE_CAVEATS = [
    "Phase 10 validates baseline and stress scenario suite capability only; it is not Gate C or paired-seed dominance evidence.",
    "Short smoke rows must not be interpreted as long-horizon performance or manuscript claims.",
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
            scenario_tag: (grid_seeds[:1] if network == "grid_4x4" else arterial_seeds[:1])
            for scenario_tag, network in SCENARIOS
        }
        controllers_by_scenario = {name: controllers for name, _ in SCENARIOS}
    else:
        seeds_by_scenario = {
            scenario_tag: (grid_seeds[:5] if scenario_tag == "grid_scalability" else arterial_seeds[:5] if scenario_tag == "arterial_main" else arterial_seeds[:1])
            for scenario_tag, _network in SCENARIOS
        }
        stress_controllers = [c for c in controllers if c in {"fixed_time", "max_pressure", "capacity_aware_pressure", "cycle_pressure", "finite_storage_double_pressure", "finite_storage_primal_dual"}]
        controllers_by_scenario = {
            scenario_tag: (controllers if scenario_tag in {"single_sanity", "arterial_main", "grid_scalability"} else stress_controllers)
            for scenario_tag, _network in SCENARIOS
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
        elif ctrl_rows:
            reason = next((str(row.get("unsupported_reason")) for row in ctrl_rows if row.get("unsupported_reason")), "not feasible")
            coverage[controller] = {"status": "not_feasible", "unsupported_reason": reason}
        else:
            coverage[controller] = {"status": "not_requested", "unsupported_reason": "no rows generated"}
    return coverage


def strong_baseline_coverage(rows: list[dict[str, Any]], controllers: list[str]) -> dict[str, Any]:
    coverage = baseline_coverage(rows, controllers)
    required = {}
    for controller in REQUIRED_STRONG_BASELINES:
        entry = coverage.get(controller, {"status": "not_requested", "description": CONTROLLER_REGISTRY.get(controller, "")})
        required[controller] = {**entry, "registered": controller in CONTROLLER_REGISTRY, "required": True}
    guarded = {}
    for controller in NOT_FEASIBLE_GUARD_CONTROLLERS:
        entry = coverage.get(controller, {"status": "not_requested", "unsupported_reason": NOT_FEASIBLE_CONTROLLERS.get(controller, "not requested")})
        guarded[controller] = {**entry, "registered": controller in CONTROLLER_REGISTRY, "guarded_not_feasible": controller in NOT_FEASIBLE_CONTROLLERS}
    return {
        "required_feasible_baselines": required,
        "not_feasible_guards": guarded,
        "passed": all(item["registered"] and item["status"] == "run" for item in required.values())
        and all(item["guarded_not_feasible"] and item["status"] == "not_feasible" for item in guarded.values()),
    }


def stress_scenario_coverage(rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    declared_tags = {name for name, _network in SCENARIOS}
    runnable_rows = [row for row in rows or [] if row.get("scenario_status") == "completed" and row.get("feasibility_status") in {"run", "completed"}]
    categories = {}
    for category, scenario_tags in STRESS_SCENARIO_CATEGORIES.items():
        rows_by_tag = {tag: [row for row in runnable_rows if row.get("scenario_tag") == tag] for tag in scenario_tags}
        mechanism_checks = {}
        for tag, tag_rows in rows_by_tag.items():
            expected = STRESS_SCENARIO_MECHANISMS[tag]
            if expected == "edge_speed_reduction":
                mechanism_checks[tag] = any(row.get("failure_mode_mechanism") == expected for row in tag_rows)
            elif expected == "traci_vehicle_insertion":
                mechanism_checks[tag] = any(row.get("demand_shift_mechanism") == expected for row in tag_rows)
            else:
                mechanism_checks[tag] = any(row.get("stress_mechanism") == expected for row in tag_rows)
        categories[category] = {
            "scenario_tags": scenario_tags,
            "declared": all(tag in declared_tags for tag in scenario_tags),
            "rows_present": sorted(tag for tag, tag_rows in rows_by_tag.items() if tag_rows),
            "mechanisms_verified": mechanism_checks,
            "passed": all(tag in declared_tags for tag in scenario_tags) and all(rows_by_tag.values()) and all(mechanism_checks.values()),
        }
    return {"categories": categories, "passed": all(item["passed"] for item in categories.values())}


def grid_fixed_time_counterexample_check(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grid_rows = [row for row in rows if row.get("scenario_tag") == "grid_scalability" and row.get("controller") == "fixed_time"]
    return {
        "status": "represented" if grid_rows else "declared_not_run",
        "scenario_tag": "grid_scalability",
        "controller": "fixed_time",
        "rows": len(grid_rows),
        "scope": "counterexample_check_metadata_only_not_broad_performance_language",
    }


def optimized_fixed_time_metadata() -> dict[str, Any]:
    return {
        "controller_name": "optimized_fixed_time",
        "status": "documented_limit",
        "implemented_in_phase10": False,
        "current_fixed_time_baseline": "deterministic unoptimized cycle baseline",
        "limitation": "Phase 10 records that tuned/grid-searched fixed timing is not implemented and must not be conflated with fixed_time.",
    }


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


def objective_component_schema() -> dict[str, Any]:
    return {
        "row_field": "objective_components",
        "fields": sorted(OBJECTIVE_COMPONENT_FIELDS),
        "component_builder": "build_objective_components_from_metrics",
        "aggregation_note": "Nested objective components remain row-level audit fields and are not CI-aggregated through METRIC_FIELDS.",
    }


def finite_storage_state_schema() -> dict[str, Any]:
    return {
        "row_field": "finite_storage_state",
        "fields": sorted(FINITE_STORAGE_STATE_FIELDS),
        "validation_helpers": ["validate_finite_storage_state", "validate_state_objective_sample"],
    }


def build_payload(
    *,
    profile: str,
    route_metadata: dict[str, str],
    rows: list[dict[str, Any]],
    controllers: list[str],
    completion_gates_passed: bool,
) -> dict[str, Any]:
    gates = completion_gates(rows)
    baseline_scope = strong_baseline_coverage(rows, controllers)
    stress_scope = stress_scenario_coverage(rows)
    return {
        "experiment": "phase10_baselines_stress_suite",
        "status": "SMOKE_ONLY" if profile == "smoke" and baseline_scope["passed"] and stress_scope["passed"] else "PASSED" if completion_gates_passed else "FAILED",
        **route_metadata,
        "claim_framing": PHASE10_CLAIM_FRAMING,
        "profile": profile,
        "scenario_results": rows,
        "aggregates": aggregate_results(rows),
        "baseline_coverage": baseline_coverage(rows, controllers),
        "strong_baseline_coverage": baseline_scope,
        "stress_scenario_coverage": stress_scope,
        "grid_fixed_time_counterexample_check": grid_fixed_time_counterexample_check(rows),
        "optimized_fixed_time_metadata": optimized_fixed_time_metadata(),
        "phase10_scope_caveats": PHASE10_SCOPE_CAVEATS,
        "completion_gates": gates,
        "completion_gates_passed": completion_gates_passed,
        "metric_schema": {field: "CLOP-04 metric" for field in METRIC_FIELDS},
        "objective_component_schema": objective_component_schema(),
        "finite_storage_state_schema": finite_storage_state_schema(),
    }


def main() -> None:
    args = parse_args()
    unknown = sorted(set(args.controllers) - set(CONTROLLER_REGISTRY))
    if unknown:
        raise ValueError(f"Unknown controllers: {unknown}. Available: {sorted(CONTROLLER_REGISTRY)}")
    route_metadata = load_route_metadata(Path(args.route_json))
    spec = build_suite_spec(args.profile, args.controllers, args.arterial_seeds, args.grid_seeds, args.steps, args.warmup, args.action_interval)
    rows = [run_experiment(**item, route_metadata=route_metadata) for item in spec]
    gates = completion_gates(rows)
    completion_gates_passed = gates_pass(gates) if args.profile == "main" else False
    payload = build_payload(
        profile=args.profile,
        route_metadata=route_metadata,
        rows=rows,
        controllers=args.controllers,
        completion_gates_passed=completion_gates_passed,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "rows": len(rows), "aggregates": len(payload["aggregates"]), "completion_gates_passed": payload["completion_gates_passed"]}, indent=2))


if __name__ == "__main__":
    main()
