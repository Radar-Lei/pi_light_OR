#!/usr/bin/env python3
"""Phase 11 long-horizon paired-seed SUMO evidence runner.

This script owns Phase 11 experiment orchestration, demand-multiplier input
materialization, paired primary-metric statistics, and fail-closed Gate C
payloads. It deliberately reuses run_closed_loop_sumo.run_experiment rather than
creating a second TraCI control loop.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

from scipy import stats

from finite_storage_schema import FINITE_STORAGE_STATE_FIELDS, OBJECTIVE_COMPONENT_FIELDS
from run_closed_loop_sumo import CONTROLLER_REGISTRY, METRIC_FIELDS, NOT_FEASIBLE_CONTROLLERS, load_route_metadata, resolve_network, run_experiment

PROPOSED_CONTROLLER = "finite_storage_primal_dual"
BINDING_EVIDENCE_SCENARIOS = (
    "arterial_downstream_blockage",
    "arterial_spillback_stress",
    "arterial_incident_capacity_drop",
    "arterial_oversaturation",
    "arterial_turning_shock",
    "arterial_switching_loss_sensitive",
)
SLACK_CONTEXT_SCENARIOS = (
    "single_sanity",
    "arterial_main",
    "grid_scalability",
)
REQUIRED_GATE_C_COMPARATORS = (
    "max_pressure",
    "capacity_aware_pressure",
    "finite_storage_double_pressure",
)
OPTIONAL_CONTEXT_CONTROLLERS = (
    "cycle_pressure",
    "actuated_local_pressure",
)
DEFAULT_CONTROLLERS = (
    PROPOSED_CONTROLLER,
    *REQUIRED_GATE_C_COMPARATORS,
    *OPTIONAL_CONTEXT_CONTROLLERS,
)
DEFAULT_MAIN_SEEDS = tuple(range(20261101, 20261121))
DEFAULT_PILOT_SEEDS = (20261101, 20261102)
DEFAULT_DEMAND_MULTIPLIERS = (0.8, 1.0, 1.2)
DEFAULT_OUT = "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json"
DEFAULT_SCALED_INPUT_DIR = Path("experiments/dual_sensitivity/phase11_scaled_inputs")
DEFAULT_MAIN_EXECUTION_ROW_LIMIT = 0
DEMAND_SCALING_METHOD = "scaled_route_sumocfg_override"
DEMAND_MULTIPLIER_PROVENANCE_KEYS = (
    "demand_multiplier",
    "demand_scaling_method",
    "requires_actual_sumo_behavior_change",
    "metadata_only_valid",
    "base_demand_total_required",
    "scaled_demand_total_required",
    "demand_source_required",
)
SCENARIO_NETWORKS = {scenario: "arterial" for scenario in BINDING_EVIDENCE_SCENARIOS}
GATE_C_PRIMARY_METRICS = (
    "penalized_avg_travel_time",
    "total_delay",
    "spillback_count",
    "blocking_count",
    "unfinished_vehicle_count",
)
GATE_C_CONDITIONAL_PRIMARY_METRICS = {
    "arterial_switching_loss_sensitive": ("switching_count",),
}
GATE_C_STATISTICAL_FAMILY = "gate_c_primary_metrics_v1"
MIN_GATE_C_PAIRED_SEEDS = 2
LOWER_IS_BETTER_METRICS = set(GATE_C_PRIMARY_METRICS) | {"switching_count", "avg_travel_time", "mean_queue", "max_queue"}
HIGHER_IS_BETTER_METRICS = {"throughput", "completion_rate", "completed_vehicles"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["pilot", "main"], default="main")
    parser.add_argument("--controllers", nargs="+", default=list(DEFAULT_CONTROLLERS))
    parser.add_argument("--proposed-controller", default=PROPOSED_CONTROLLER)
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--warmup", type=int, default=None)
    parser.add_argument("--action-interval", type=int, default=10)
    parser.add_argument("--demand-multipliers", nargs="+", type=float, default=list(DEFAULT_DEMAND_MULTIPLIERS))
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--scaled-input-dir", default=str(DEFAULT_SCALED_INPUT_DIR))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--execution-row-limit",
        type=int,
        default=None,
        help="Safety limit for executed rows; main defaults to fail-closed before expensive full execution.",
    )
    parser.add_argument("--progress-out", default=None, help="Optional row-level JSON progress artifact to update after each attempted row.")
    parser.add_argument("--resume-progress", default=None, help="Optional row-level JSON progress artifact to resume from; missing path cold-starts when progress-out is set.")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    seeds = args.seeds if args.seeds is not None else (DEFAULT_MAIN_SEEDS if args.profile == "main" else DEFAULT_PILOT_SEEDS)
    steps = args.steps if args.steps is not None else (3600 if args.profile == "main" else 300)
    warmup = args.warmup if args.warmup is not None else (900 if args.profile == "main" else 60)
    _validate_profile_inputs(args.profile, args.controllers, seeds, steps, warmup, args.action_interval, args.demand_multipliers)
    out_path = Path(args.out)
    if out_path.suffix != ".json":
        raise ValueError("--out must point to a .json artifact")
    if not Path(args.route_json).exists():
        raise FileNotFoundError(args.route_json)
    if args.execution_row_limit is not None and args.execution_row_limit < 0:
        raise ValueError("--execution-row-limit must be nonnegative")
    if args.resume_progress and not args.progress_out:
        raise ValueError("--resume-progress requires --progress-out so progress can be rewritten after resume")
    for path_arg in [args.progress_out, args.resume_progress]:
        if path_arg is not None and Path(path_arg).suffix != ".json":
            raise ValueError("progress paths must point to .json artifacts")


def set_proposed_controller(controller: str) -> None:
    if controller not in CONTROLLER_REGISTRY:
        raise ValueError(f"Unknown proposed controller: {controller}. Available: {sorted(CONTROLLER_REGISTRY)}")
    globals()["PROPOSED_CONTROLLER"] = str(controller)


def _validate_profile_inputs(
    profile: str,
    controllers: list[str] | tuple[str, ...],
    seeds: list[int] | tuple[int, ...],
    steps: int,
    warmup: int,
    action_interval: int,
    demand_multipliers: list[float] | tuple[float, ...],
) -> None:
    if profile not in {"pilot", "main"}:
        raise ValueError("profile must be 'pilot' or 'main'")
    unknown = sorted(set(controllers) - set(CONTROLLER_REGISTRY))
    if unknown:
        raise ValueError(f"Unknown controllers: {unknown}. Available: {sorted(CONTROLLER_REGISTRY)}")
    required = {PROPOSED_CONTROLLER, *REQUIRED_GATE_C_COMPARATORS}
    missing = sorted(required - set(controllers))
    if missing:
        raise ValueError(f"Phase 11 Gate C spec requires controllers: {missing}")
    if not seeds:
        raise ValueError("At least one paired seed is required")
    if len(set(int(seed) for seed in seeds)) != len(seeds):
        raise ValueError("Paired seeds must be unique")
    if steps <= 0 or warmup < 0 or action_interval <= 0:
        raise ValueError("steps and action_interval must be positive; warmup must be nonnegative")
    if profile == "main" and (steps < 3600 or warmup < 900):
        raise ValueError("main profile must use at least 3600 steps and 900 warmup")
    if profile == "main" and len(set(int(seed) for seed in seeds)) < 2:
        raise ValueError("main profile requires at least two paired seeds for confidence-interval construction")
    if not demand_multipliers:
        raise ValueError("At least one demand multiplier is required")
    if any(float(multiplier) <= 0.0 or not math.isfinite(float(multiplier)) for multiplier in demand_multipliers):
        raise ValueError("Demand multipliers must be positive finite values")
    if profile == "main" and not {0.8, 1.0, 1.2} <= {round(float(multiplier), 10) for multiplier in demand_multipliers}:
        raise ValueError("main profile requires demand multipliers 0.8, 1.0, and 1.2")


def demand_multiplier_contract(demand_multiplier: float) -> dict[str, Any]:
    return {
        "demand_multiplier": float(demand_multiplier),
        "demand_scaling_method": DEMAND_SCALING_METHOD,
        "requires_actual_sumo_behavior_change": True,
        "metadata_only_valid": False,
        "base_demand_total_required": True,
        "scaled_demand_total_required": True,
        "demand_source_required": True,
        "acceptable_methods": [DEMAND_SCALING_METHOD],
    }


def build_phase11_spec(
    profile: str,
    controllers: list[str] | tuple[str, ...] | None = None,
    seeds: list[int] | tuple[int, ...] | None = None,
    steps: int | None = None,
    warmup: int | None = None,
    action_interval: int = 10,
    demand_multipliers: list[float] | tuple[float, ...] | None = None,
) -> list[dict[str, Any]]:
    if controllers is None:
        controllers = DEFAULT_CONTROLLERS
    if seeds is None:
        seeds = DEFAULT_MAIN_SEEDS if profile == "main" else DEFAULT_PILOT_SEEDS
    if steps is None:
        steps = 3600 if profile == "main" else 300
    if warmup is None:
        warmup = 900 if profile == "main" else 60
    if demand_multipliers is None:
        demand_multipliers = DEFAULT_DEMAND_MULTIPLIERS
    controllers = tuple(dict.fromkeys(str(controller) for controller in controllers))
    seeds = tuple(int(seed) for seed in seeds)
    demand_multipliers = tuple(float(multiplier) for multiplier in demand_multipliers)
    _validate_profile_inputs(profile, controllers, seeds, int(steps), int(warmup), int(action_interval), demand_multipliers)

    evidence_role = "gate_c_binding_dominance_candidate" if profile == "main" else "pipeline_validation_not_gate_c_dominance"
    spec = []
    for scenario_tag in BINDING_EVIDENCE_SCENARIOS:
        for demand_multiplier in demand_multipliers:
            contract = demand_multiplier_contract(demand_multiplier)
            for seed in seeds:
                for controller in controllers:
                    spec.append(
                        {
                            "profile": profile,
                            "evidence_role": evidence_role,
                            "gate_c_eligible": profile == "main",
                            "network": SCENARIO_NETWORKS[scenario_tag],
                            "scenario_tag": scenario_tag,
                            "controller": controller,
                            "seed": int(seed),
                            "steps": int(steps),
                            "warmup": int(warmup),
                            "action_interval": int(action_interval),
                            "demand_multiplier": float(demand_multiplier),
                            "demand_multiplier_contract": dict(contract),
                            "phase10_reuse_as_dominance_evidence": False,
                        }
                    )
    return spec


def _safe_multiplier_label(demand_multiplier: float) -> str:
    return str(float(demand_multiplier)).replace("-", "neg").replace(".", "p")


def _sumocfg_child(root: ET.Element, section: str, child: str) -> ET.Element:
    section_node = root.find(section)
    if section_node is None:
        section_node = ET.SubElement(root, section)
    child_node = section_node.find(child)
    if child_node is None:
        child_node = ET.SubElement(section_node, child)
    return child_node


def _route_files_from_sumocfg(sumocfg_path: Path) -> list[Path]:
    root = ET.parse(sumocfg_path).getroot()
    route_node = root.find("./input/route-files")
    if route_node is None or not route_node.get("value"):
        raise ValueError(f"SUMO config {sumocfg_path} is missing input/route-files")
    files = []
    for item in route_node.get("value", "").split(","):
        raw_path = Path(item.strip())
        files.append(raw_path if raw_path.is_absolute() else sumocfg_path.parent / raw_path)
    return files


def _flow_total(flow: ET.Element) -> float:
    if flow.get("number") is not None:
        return float(flow.get("number", "0"))
    begin = float(flow.get("begin", "0"))
    end = float(flow.get("end", flow.get("until", "0")))
    duration = max(end - begin, 0.0)
    if flow.get("period") is not None:
        period = max(float(flow.get("period", "1")), 1e-9)
        return duration / period
    if flow.get("vehsPerHour") is not None:
        return duration * float(flow.get("vehsPerHour", "0")) / 3600.0
    if flow.get("probability") is not None:
        return duration * float(flow.get("probability", "0"))
    return 0.0


def _route_root_demand_total(root: ET.Element) -> float:
    total = float(len(root.findall("vehicle")) + len(root.findall("trip")))
    total += sum(_flow_total(flow) for flow in root.findall("flow"))
    return float(total)


def route_demand_total(route_path: Path) -> float:
    return _route_root_demand_total(ET.parse(route_path).getroot())


def _extend_flow_horizon(flow: ET.Element, steps: int) -> None:
    begin = float(flow.get("begin", "0"))
    if begin >= float(steps):
        return
    if flow.get("end") is not None:
        if float(flow.get("end", "0")) < float(steps):
            flow.set("end", str(int(steps)))
    elif flow.get("until") is not None:
        if float(flow.get("until", "0")) < float(steps):
            flow.set("until", str(int(steps)))


def _scale_flow(flow: ET.Element, demand_multiplier: float) -> None:
    if flow.get("number") is not None:
        original = float(flow.get("number", "0"))
        flow.set("number", f"{original * demand_multiplier:.6g}")
    elif flow.get("period") is not None:
        original = max(float(flow.get("period", "1")), 1e-9)
        flow.set("period", f"{original / demand_multiplier:.6g}")
    elif flow.get("vehsPerHour") is not None:
        original = float(flow.get("vehsPerHour", "0"))
        flow.set("vehsPerHour", f"{original * demand_multiplier:.6g}")
    elif flow.get("probability") is not None:
        original = float(flow.get("probability", "0"))
        flow.set("probability", f"{min(original * demand_multiplier, 1.0):.6g}")
    else:
        raise ValueError(f"Flow {flow.get('id', '<unnamed>')} has no scalable demand attribute")


def generate_scaled_route_and_sumocfg(
    network: str,
    demand_multiplier: float,
    steps: int,
    scaled_input_dir: Path = DEFAULT_SCALED_INPUT_DIR,
) -> dict[str, Any]:
    paths = resolve_network(network)
    route_files = _route_files_from_sumocfg(paths["sumocfg"])
    if len(route_files) != 1:
        raise ValueError(f"Phase 11 demand scaling expects exactly one route file for {network}, got {route_files}")
    base_route = route_files[0]
    if not base_route.exists():
        raise FileNotFoundError(base_route)
    base_route_tree = ET.parse(base_route)
    base_route_root = base_route_tree.getroot()
    for flow in base_route_root.findall("flow"):
        _extend_flow_horizon(flow, int(steps))
    base_demand_total = _route_root_demand_total(base_route_root)
    if base_demand_total <= 0.0:
        raise ValueError(f"Base route {base_route} has no scalable positive demand")

    scaled_input_dir.mkdir(parents=True, exist_ok=True)
    label = _safe_multiplier_label(demand_multiplier)
    route_out = scaled_input_dir / f"phase11_{network}_demand_{label}.rou.xml"
    sumocfg_out = scaled_input_dir / f"phase11_{network}_demand_{label}.sumocfg"

    route_tree = ET.ElementTree(ET.fromstring(ET.tostring(base_route_root)))
    route_root = route_tree.getroot()
    flow_count = 0
    for flow in route_root.findall("flow"):
        _scale_flow(flow, float(demand_multiplier))
        flow_count += 1
    if flow_count == 0:
        raise ValueError(f"Base route {base_route} has no flow entries; metadata-only demand scaling is forbidden")
    route_tree.write(route_out, encoding="utf-8", xml_declaration=True)
    scaled_demand_total = route_demand_total(route_out)

    cfg_tree = ET.parse(paths["sumocfg"])
    cfg_root = cfg_tree.getroot()
    _sumocfg_child(cfg_root, "input", "net-file").set("value", str(paths["net_file"].resolve()))
    _sumocfg_child(cfg_root, "input", "route-files").set("value", str(route_out.resolve()))
    _sumocfg_child(cfg_root, "time", "end").set("value", str(int(steps)))
    cfg_tree.write(sumocfg_out, encoding="utf-8", xml_declaration=True)

    if not route_out.exists() or not sumocfg_out.exists():
        raise FileNotFoundError("Generated demand override files were not written")
    if not math.isclose(scaled_demand_total, base_demand_total * float(demand_multiplier), rel_tol=0.02, abs_tol=0.5):
        raise ValueError("Scaled demand total does not reflect requested multiplier")
    return {
        "demand_multiplier": float(demand_multiplier),
        "demand_scaling_method": DEMAND_SCALING_METHOD,
        "requires_actual_sumo_behavior_change": True,
        "metadata_only_valid": False,
        "base_demand_total": float(base_demand_total),
        "scaled_demand_total": float(scaled_demand_total),
        "demand_source": str(route_out),
        "generated_route_file": str(route_out),
        "generated_sumocfg": str(sumocfg_out),
        "base_sumocfg": str(paths["sumocfg"]),
        "base_route_file": str(base_route),
    }


def materialize_demand_inputs(spec: list[dict[str, Any]], scaled_input_dir: Path = DEFAULT_SCALED_INPUT_DIR) -> list[dict[str, Any]]:
    cache: dict[tuple[str, float, int], dict[str, Any]] = {}
    enriched = []
    for row in spec:
        key = (str(row["network"]), float(row["demand_multiplier"]), int(row["steps"]))
        if key not in cache:
            cache[key] = generate_scaled_route_and_sumocfg(key[0], key[1], key[2], scaled_input_dir)
        provenance = dict(cache[key])
        enriched_row = {**row, **provenance, "demand_multiplier_provenance": provenance}
        enriched.append(enriched_row)
    validate_actual_demand_multiplier_behavior(enriched)
    return enriched


def validate_actual_demand_multiplier_behavior(spec: list[dict[str, Any]]) -> None:
    by_network: dict[str, dict[float, dict[str, Any]]] = defaultdict(dict)
    for row in spec:
        provenance = row.get("demand_multiplier_provenance") or row
        multiplier = float(row.get("demand_multiplier", provenance.get("demand_multiplier", 1.0)))
        method = provenance.get("demand_scaling_method")
        if method != DEMAND_SCALING_METHOD or provenance.get("metadata_only_valid") is not False:
            raise ValueError("metadata-only demand multiplier configurations are forbidden")
        for field in ["base_demand_total", "scaled_demand_total", "generated_route_file", "generated_sumocfg", "base_sumocfg"]:
            if field not in provenance:
                raise ValueError(f"demand multiplier provenance is missing {field}")
        expected_total = float(provenance["base_demand_total"]) * multiplier
        if not math.isclose(float(provenance["scaled_demand_total"]), expected_total, rel_tol=0.02, abs_tol=0.5):
            raise ValueError("scaled demand total does not match base demand total times multiplier")
        for path_field in ["generated_route_file", "generated_sumocfg"]:
            if not Path(str(provenance[path_field])).exists():
                raise FileNotFoundError(str(provenance[path_field]))
        by_network[str(row["network"])][multiplier] = provenance
    for network, entries in by_network.items():
        if len(entries) > 1:
            route_paths = {str(item["generated_route_file"]) for item in entries.values()}
            cfg_paths = {str(item["generated_sumocfg"]) for item in entries.values()}
            totals = {round(float(item["scaled_demand_total"]), 6) for item in entries.values()}
            if len(route_paths) != len(entries) or len(cfg_paths) != len(entries):
                raise ValueError(f"{network} demand multipliers did not generate distinct route/config paths")
            if len(totals) != len(entries):
                raise ValueError(f"{network} demand multipliers did not generate distinct demand totals")


def metric_direction(metric: str) -> str:
    if metric in LOWER_IS_BETTER_METRICS:
        return "lower_is_better"
    if metric in HIGHER_IS_BETTER_METRICS:
        return "higher_is_better"
    raise ValueError(f"Unknown metric direction for {metric}")


def applicable_primary_metrics(scenario_tag: str, rows: list[dict[str, Any]] | None = None) -> tuple[str, ...]:
    metrics = list(GATE_C_PRIMARY_METRICS)
    conditional = list(GATE_C_CONDITIONAL_PRIMARY_METRICS.get(scenario_tag, ()))
    if rows and any("switching_loss" in str(row.get("stress_category", "")) or "switching_loss" in str(row.get("stress_mechanism", "")) for row in rows):
        conditional.append("switching_count")
    for metric in conditional:
        if metric not in metrics:
            metrics.append(metric)
    return tuple(metrics)


def paired_difference(proposed: dict[str, Any], comparator: dict[str, Any], metric: str) -> float:
    direction = metric_direction(metric)
    if metric not in proposed or metric not in comparator:
        raise ValueError(f"Missing metric {metric} for paired comparison")
    proposed_value = float(proposed[metric])
    comparator_value = float(comparator[metric])
    if direction == "lower_is_better":
        return comparator_value - proposed_value
    return proposed_value - comparator_value


def _completed_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row for row in rows
        if row.get("scenario_status") == "completed" and row.get("feasibility_status") in {"run", "completed"}
    ]


def _rows_by_controller_seed(rows: list[dict[str, Any]], scenario_tag: str, demand_multiplier: float) -> dict[str, dict[int, dict[str, Any]]]:
    grouped: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in _completed_rows(rows):
        if row.get("scenario_tag") != scenario_tag:
            continue
        if float(row.get("demand_multiplier", 1.0)) != float(demand_multiplier):
            continue
        grouped[str(row.get("controller"))][int(row["seed"])] = row
    return grouped


def _paired_values(
    rows: list[dict[str, Any]],
    scenario_tag: str,
    demand_multiplier: float,
    comparator: str,
    metric: str,
) -> tuple[list[int], list[float], list[float], list[float]]:
    grouped = _rows_by_controller_seed(rows, scenario_tag, demand_multiplier)
    proposed_rows = grouped.get(PROPOSED_CONTROLLER, {})
    comparator_rows = grouped.get(comparator, {})
    proposed_seeds = set(proposed_rows)
    comparator_seeds = set(comparator_rows)
    if proposed_seeds != comparator_seeds:
        raise ValueError(
            f"unpaired seeds for {scenario_tag}/{demand_multiplier}/{comparator}: "
            f"proposed={sorted(proposed_seeds)} comparator={sorted(comparator_seeds)}"
        )
    if not proposed_seeds:
        raise ValueError(f"no paired seeds for {scenario_tag}/{demand_multiplier}/{comparator}")
    if len(proposed_seeds) < MIN_GATE_C_PAIRED_SEEDS:
        raise ValueError(f"{scenario_tag}/{demand_multiplier}/{comparator} has fewer than {MIN_GATE_C_PAIRED_SEEDS} paired seeds")
    seed_ids = sorted(proposed_seeds)
    proposed_values = []
    comparator_values = []
    differences = []
    for seed in seed_ids:
        proposed = proposed_rows[seed]
        comp = comparator_rows[seed]
        if metric not in proposed or metric not in comp:
            raise ValueError(f"missing {metric} for {scenario_tag}/{demand_multiplier}/{comparator}/seed={seed}")
        proposed_values.append(float(proposed[metric]))
        comparator_values.append(float(comp[metric]))
        differences.append(paired_difference(proposed, comp, metric))
    return seed_ids, proposed_values, comparator_values, differences


def _bootstrap_ci(differences: list[float]) -> tuple[float, float, float]:
    if len(differences) < MIN_GATE_C_PAIRED_SEEDS:
        raise ValueError(f"at least {MIN_GATE_C_PAIRED_SEEDS} paired seeds are required for Gate C confidence intervals")
    if len(set(differences)) == 1:
        value = float(differences[0])
        return value, value, 0.0
    result = stats.bootstrap(
        (differences,),
        lambda data, axis: data.mean(axis=axis),
        paired=True,
        confidence_level=0.95,
        n_resamples=999,
        method="percentile",
        random_state=0,
    )
    return float(result.confidence_interval.low), float(result.confidence_interval.high), float(result.standard_error)


def _effect_size(differences: list[float]) -> float:
    if not differences:
        return 0.0
    if len(differences) <= 1:
        return math.copysign(math.inf, differences[0]) if differences[0] else 0.0
    sd = statistics.stdev(differences)
    if sd == 0.0:
        return math.copysign(math.inf, statistics.fmean(differences)) if statistics.fmean(differences) else 0.0
    return float(statistics.fmean(differences) / sd)


def _diagnostics(proposed_values: list[float], comparator_values: list[float], differences: list[float], metric: str) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {}
    try:
        alternative = "less" if metric_direction(metric) == "lower_is_better" else "greater"
        ttest = stats.ttest_rel(proposed_values, comparator_values, alternative=alternative)
        diagnostics["paired_ttest"] = {"statistic": float(ttest.statistic), "pvalue": float(ttest.pvalue), "alternative": alternative}
    except Exception as exc:
        diagnostics["paired_ttest"] = {"status": "unavailable", "reason": str(exc)}
    try:
        wilcoxon = stats.wilcoxon(differences, alternative="greater", zero_method="zsplit")
        diagnostics["wilcoxon"] = {"statistic": float(wilcoxon.statistic), "pvalue": float(wilcoxon.pvalue), "alternative": "greater"}
    except Exception as exc:
        diagnostics["wilcoxon"] = {"status": "unavailable", "reason": str(exc)}
    return diagnostics


def paired_metric_summary(
    rows: list[dict[str, Any]],
    scenario_tag: str,
    demand_multiplier: float,
    comparator: str,
    metric: str,
) -> dict[str, Any]:
    seed_ids, proposed_values, comparator_values, differences = _paired_values(rows, scenario_tag, demand_multiplier, comparator, metric)
    ci_low, ci_high, standard_error = _bootstrap_ci(differences)
    mean_difference = float(statistics.fmean(differences))
    direction = metric_direction(metric)
    if ci_low == 0.0 and ci_high == 0.0:
        classification = "inconclusive"
    elif ci_low >= 0.0:
        classification = "non_worsening"
    elif ci_high < 0.0:
        classification = "bounded_harm"
    else:
        classification = "inconclusive"
    return {
        "scenario_tag": scenario_tag,
        "demand_multiplier": float(demand_multiplier),
        "comparator": comparator,
        "proposed_controller": PROPOSED_CONTROLLER,
        "metric": metric,
        "metric_direction": direction,
        "difference_definition": "comparator_minus_proposed" if direction == "lower_is_better" else "proposed_minus_comparator",
        "positive_means": "proposed_controller_better",
        "paired_seed_ids": seed_ids,
        "n_seeds": len(seed_ids),
        "paired_differences": [float(value) for value in differences],
        "mean_paired_difference": mean_difference,
        "ci_method": "paired_bootstrap_percentile_95",
        "ci_low": ci_low,
        "ci_high": ci_high,
        "standard_error": standard_error,
        "effect_size": _effect_size(differences),
        "classification": classification,
        "strict_positive_signal": ci_low > 0.0,
        "statistical_family": GATE_C_STATISTICAL_FAMILY,
        "diagnostics": _diagnostics(proposed_values, comparator_values, differences, metric),
    }


def _holm_bonferroni(metric_results: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for idx, result in enumerate(metric_results):
        pvalue = result.get("diagnostics", {}).get("wilcoxon", {}).get("pvalue")
        if pvalue is None or not math.isfinite(float(pvalue)):
            pvalue = 1.0
        entries.append((idx, float(pvalue)))
    m = len(entries)
    adjusted_by_idx = {}
    cumulative = 0.0
    for rank, (idx, pvalue) in enumerate(sorted(entries, key=lambda item: item[1]), start=1):
        adjusted_pvalue = min((m - rank + 1) * pvalue, 1.0)
        cumulative = max(cumulative, adjusted_pvalue)
        adjusted_by_idx[idx] = cumulative
    adjusted = []
    for idx, result in enumerate(metric_results):
        item = {
            "scenario_tag": result["scenario_tag"],
            "demand_multiplier": result["demand_multiplier"],
            "comparator": result["comparator"],
            "metric": result["metric"],
            "adjusted_pvalue": adjusted_by_idx.get(idx, 1.0),
            "reject_at_0_05": adjusted_by_idx.get(idx, 1.0) <= 0.05,
        }
        adjusted.append(item)
    return {
        "family": GATE_C_STATISTICAL_FAMILY,
        "method": "holm_bonferroni",
        "alpha": 0.05,
        "num_comparisons": m,
        "adjusted_diagnostics": adjusted,
    }


def evaluate_gate_c_primary_metric_rule(
    rows: list[dict[str, Any]],
    *,
    scenarios: list[str] | tuple[str, ...] = BINDING_EVIDENCE_SCENARIOS,
    comparators: list[str] | tuple[str, ...] = REQUIRED_GATE_C_COMPARATORS,
    demand_multipliers: list[float] | tuple[float, ...] | None = None,
) -> dict[str, Any]:
    if demand_multipliers is None:
        demand_multipliers = sorted({float(row.get("demand_multiplier", 1.0)) for row in rows}) or [1.0]
    reasons = []
    metric_results = []
    for scenario_tag in scenarios:
        scenario_rows = [row for row in rows if row.get("scenario_tag") == scenario_tag]
        metrics = applicable_primary_metrics(scenario_tag, scenario_rows)
        for demand_multiplier in demand_multipliers:
            for comparator in comparators:
                for metric in metrics:
                    try:
                        metric_results.append(paired_metric_summary(rows, scenario_tag, float(demand_multiplier), comparator, metric))
                    except ValueError as exc:
                        reasons.append(str(exc))
    family_metadata = _holm_bonferroni(metric_results)
    if reasons or any(result["classification"] == "bounded_harm" for result in metric_results):
        status = "FAILED"
    elif not metric_results:
        status = "FAILED"
        reasons.append("no applicable Gate C primary metric results")
    else:
        all_non_worsening = all(result["classification"] == "non_worsening" for result in metric_results)
        grouped: dict[tuple[str, float, str], list[dict[str, Any]]] = defaultdict(list)
        for result in metric_results:
            grouped[(result["scenario_tag"], float(result["demand_multiplier"]), result["comparator"])].append(result)
        strict_by_group = all(any(item["strict_positive_signal"] for item in group) for group in grouped.values())
        status = "PASSED" if all_non_worsening and strict_by_group else "INCONCLUSIVE"
    return {
        "status": status,
        "statistical_family": GATE_C_STATISTICAL_FAMILY,
        "metric_results": metric_results,
        "family_metadata": family_metadata,
        "reasons": reasons,
    }


FORBIDDEN_AFFIRMATIVE_PHRASES = (
    "universal dominance",
    "universal superiority",
    "deployment readiness",
    "final manuscript claim",
    "manuscript claim",
    "superior to max-pressure outside binding regimes",
    "superiority over max-pressure outside binding regimes",
    "broad superiority over max-pressure",
    "phase 10 proves superiority",
    "phase 10 superiority",
    "phase 10 dominance",
)


def _collect_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_collect_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_collect_text(item) for item in value)
    return str(value)


def validate_payload_scope(payload: dict[str, Any]) -> None:
    text = _collect_text({key: value for key, value in payload.items() if key != "caveats"}).lower()
    forbidden = [phrase for phrase in FORBIDDEN_AFFIRMATIVE_PHRASES if phrase in text]
    if forbidden:
        raise ValueError(f"forbidden Phase 11 claim language: {forbidden}")


def _row_id(row: dict[str, Any]) -> str:
    return f"{row.get('scenario_tag')}/{row.get('demand_multiplier', 1.0)}/{row.get('controller')}/seed={row.get('seed')}"


def _normalized_multiplier(value: Any) -> str:
    return f"{float(value):.10g}"


def row_key(row: dict[str, Any]) -> str:
    return f"{row.get('scenario_tag')}/{_normalized_multiplier(row.get('demand_multiplier', 1.0))}/{row.get('controller')}/seed={int(row.get('seed'))}"


def progress_spec_fingerprint(spec: list[dict[str, Any]]) -> str:
    keys = [row_key(row) for row in spec]
    payload = {
        "row_keys": keys,
        "profile": sorted({str(row.get("profile")) for row in spec}),
        "steps": sorted({int(row.get("steps", 0)) for row in spec}),
        "warmup": sorted({int(row.get("warmup", 0)) for row in spec}),
        "action_interval": sorted({int(row.get("action_interval", 0)) for row in spec}),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _progress_metadata(spec: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "experiment": "phase11_row_progress",
        "spec_fingerprint": progress_spec_fingerprint(spec),
        "profile": sorted({str(row.get("profile")) for row in spec})[0] if spec else "unknown",
        "steps": max([int(row.get("steps", 0)) for row in spec], default=0),
        "warmup": max([int(row.get("warmup", 0)) for row in spec], default=0),
        "seeds": sorted({int(row["seed"]) for row in spec}),
        "demand_multipliers": sorted({float(row["demand_multiplier"]) for row in spec}),
        "expected_row_count": len(spec),
        "expected_row_keys": [row_key(row) for row in spec],
    }


def load_progress(progress_path: Path, spec: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        payload = json.loads(progress_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid progress JSON: {progress_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("progress JSON must contain an object")
    expected_fingerprint = progress_spec_fingerprint(spec)
    if payload.get("spec_fingerprint") != expected_fingerprint:
        raise ValueError("progress spec fingerprint mismatch")
    allowed_keys = {row_key(row) for row in spec}
    rows_by_key: dict[str, dict[str, Any]] = {}
    completed_row_keys = []
    for row in payload.get("completed_rows", []):
        if not isinstance(row, dict):
            raise ValueError("progress completed_rows must contain row objects")
        key = row_key(row)
        if key not in allowed_keys:
            raise ValueError(f"progress row outside current spec: {key}")
        existing = rows_by_key.get(key)
        if existing is not None and existing != row:
            raise ValueError(f"progress contains conflicting duplicate row for {key}")
        if existing is None:
            rows_by_key[key] = row
            completed_row_keys.append(key)
    attempted_row_keys = [str(key) for key in payload.get("attempted_row_keys", [])]
    outside_attempts = sorted(set(attempted_row_keys) - allowed_keys)
    if outside_attempts:
        raise ValueError(f"progress attempted row keys outside current spec: {outside_attempts}")
    failure_reasons = [str(reason) for reason in payload.get("failure_reasons", [])]
    return {
        "payload": payload,
        "completed_rows": [rows_by_key[key] for key in completed_row_keys],
        "completed_row_keys": completed_row_keys,
        "attempted_row_keys": attempted_row_keys,
        "failure_reasons": failure_reasons,
    }


def write_progress(
    progress_path: Path,
    spec: list[dict[str, Any]],
    completed_rows: list[dict[str, Any]],
    attempted_row_keys: list[str],
    failure_reasons: list[str],
) -> None:
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **_progress_metadata(spec),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_row_count": len(completed_rows),
        "attempted_row_count": len(attempted_row_keys),
        "completed_row_keys": [row_key(row) for row in completed_rows],
        "attempted_row_keys": list(attempted_row_keys),
        "failure_reasons": list(failure_reasons),
        "completed_rows": completed_rows,
    }
    progress_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _validate_demand_provenance(row: dict[str, Any]) -> list[str]:
    provenance = row.get("demand_multiplier_provenance") or row
    if not isinstance(provenance, dict):
        return [f"{_row_id(row)} missing demand multiplier provenance"]
    if provenance.get("metadata_only_valid") is not False:
        return [f"{_row_id(row)} has metadata-only demand multiplier provenance"]
    if provenance.get("requires_actual_sumo_behavior_change") is not True:
        return [f"{_row_id(row)} demand multiplier does not require actual SUMO behavior change"]
    method = provenance.get("demand_scaling_method")
    if method != DEMAND_SCALING_METHOD:
        return [f"{_row_id(row)} demand multiplier method is invalid"]
    required = ["base_demand_total", "scaled_demand_total", "generated_route_file", "generated_sumocfg", "base_sumocfg"]
    missing = [field for field in required if field not in provenance]
    if missing:
        return [f"{_row_id(row)} demand multiplier lacks actual behavior provenance: {missing}"]
    return []


def _validate_binding_row(row: dict[str, Any]) -> list[str]:
    reasons = []
    row_name = _row_id(row)
    if not row.get("stress_category") or not row.get("stress_mechanism"):
        reasons.append(f"{row_name} missing stress metadata")
    if not isinstance(row.get("finite_storage_state"), dict):
        reasons.append(f"{row_name} missing finite_storage_state")
    if int(row.get("steps", 0) or 0) < 3600:
        reasons.append(f"{row_name} has row-level steps below Gate C minimum 3600")
    if int(row.get("warmup", 0) or 0) < 900:
        reasons.append(f"{row_name} has row-level warmup below Gate C minimum 900")
    if not isinstance(row.get("objective_components"), dict):
        reasons.append(f"{row_name} missing objective_components")
    for metric in applicable_primary_metrics(str(row.get("scenario_tag")), [row]):
        if metric not in row or not isinstance(row.get(metric), (int, float)):
            reasons.append(f"{row_name} missing numeric metric {metric}")
    if row.get("controller") == PROPOSED_CONTROLLER:
        action_decomposition = row.get("action_decomposition")
        if not isinstance(action_decomposition, dict) or not action_decomposition.get("last_decision_by_tls"):
            reasons.append(f"{row_name} missing action_decomposition")
    reasons.extend(_validate_demand_provenance(row))
    return reasons


def _classify_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    sections = {
        "binding_regime_dominance": [],
        "slack_regime_recovery_or_context": [],
        "inconclusive": [],
        "not_evidence": [],
    }
    for row in rows:
        scenario = str(row.get("scenario_tag"))
        entry = {
            "scenario_tag": scenario,
            "controller": row.get("controller"),
            "seed": row.get("seed"),
            "demand_multiplier": row.get("demand_multiplier", 1.0),
        }
        if scenario in BINDING_EVIDENCE_SCENARIOS and row.get("scenario_status") == "completed" and row.get("feasibility_status") in {"run", "completed"}:
            sections["binding_regime_dominance"].append(entry)
        elif scenario in SLACK_CONTEXT_SCENARIOS:
            sections["slack_regime_recovery_or_context"].append(entry)
        elif row.get("scenario_status") != "completed":
            sections["inconclusive"].append(entry)
        else:
            sections["not_evidence"].append(entry)
    return sections


def evaluate_gate_c(payload: dict[str, Any]) -> dict[str, Any]:
    rows = list(payload.get("scenario_results", []))
    reasons = []
    profile = payload.get("profile")
    steps = int(payload.get("steps", max([int(row.get("steps", 0)) for row in rows], default=0)))
    warmup = int(payload.get("warmup", max([int(row.get("warmup", 0)) for row in rows], default=0)))
    dry_run = bool(payload.get("dry_run"))
    if profile != "main" or steps < 3600 or warmup < 900:
        reasons.append("Gate C complete evidence requires main profile with at least 3600 steps and 900 warmup")
    if dry_run:
        reasons.append("dry-run/spec-only artifacts are not Gate C dominance evidence")
    completed = _completed_rows(rows)
    present_scenarios = {str(row.get("scenario_tag")) for row in completed}
    missing_scenarios = sorted(set(BINDING_EVIDENCE_SCENARIOS) - present_scenarios)
    if missing_scenarios and rows:
        reasons.append(f"missing required binding scenarios: {missing_scenarios}")
    for scenario in BINDING_EVIDENCE_SCENARIOS:
        scenario_rows = [row for row in completed if row.get("scenario_tag") == scenario]
        if not scenario_rows:
            continue
        controllers = {str(row.get("controller")) for row in scenario_rows}
        missing_controllers = sorted({PROPOSED_CONTROLLER, *REQUIRED_GATE_C_COMPARATORS} - controllers)
        if missing_controllers:
            reasons.append(f"{scenario} missing required comparator/controller rows: {missing_controllers}")
        for row in scenario_rows:
            reasons.extend(_validate_binding_row(row))
    sections = _classify_rows(rows)
    if reasons:
        status = "INCONCLUSIVE" if any("main profile" in reason or "dry-run" in reason for reason in reasons) else "FAILED"
        rule = {"status": status, "metric_results": [], "family_metadata": _holm_bonferroni([]), "reasons": reasons}
    elif not completed:
        status = "INCONCLUSIVE"
        rule = {"status": "INCONCLUSIVE", "metric_results": [], "family_metadata": _holm_bonferroni([]), "reasons": ["no executed rows available"]}
        reasons.append("no executed rows available")
    else:
        demand_multipliers = sorted({float(row.get("demand_multiplier", 1.0)) for row in completed if row.get("scenario_tag") in BINDING_EVIDENCE_SCENARIOS})
        rule = evaluate_gate_c_primary_metric_rule(
            completed,
            scenarios=BINDING_EVIDENCE_SCENARIOS,
            comparators=REQUIRED_GATE_C_COMPARATORS,
            demand_multipliers=demand_multipliers,
        )
        status = rule["status"]
        reasons.extend(rule.get("reasons", []))
    result = {
        "status": status,
        "binding_regime_dominance": sections["binding_regime_dominance"],
        "slack_regime_recovery_or_context": sections["slack_regime_recovery_or_context"],
        "inconclusive": sections["inconclusive"],
        "not_evidence": sections["not_evidence"],
        "primary_metric_rule": rule,
        "reasons": reasons,
    }
    validate_payload_scope(result)
    return result


def paired_seed_alignment(rows: list[dict[str, Any]], spec: list[dict[str, Any]]) -> dict[str, Any]:
    source = rows if rows else spec
    alignment: dict[str, Any] = {}
    for scenario in BINDING_EVIDENCE_SCENARIOS:
        scenario_entry: dict[str, Any] = {}
        multipliers = sorted({float(row.get("demand_multiplier", 1.0)) for row in source if row.get("scenario_tag") == scenario})
        for multiplier in multipliers:
            by_controller: dict[str, list[int]] = defaultdict(list)
            for row in source:
                if row.get("scenario_tag") == scenario and float(row.get("demand_multiplier", 1.0)) == float(multiplier):
                    by_controller[str(row.get("controller"))].append(int(row["seed"]))
            required = {PROPOSED_CONTROLLER, *REQUIRED_GATE_C_COMPARATORS}
            required_sets = {controller: sorted(set(by_controller.get(controller, []))) for controller in required}
            seed_sets = list(required_sets.values())
            scenario_entry[str(multiplier)] = {
                "seeds_by_controller": required_sets,
                "aligned": bool(seed_sets) and all(seed_set == seed_sets[0] for seed_set in seed_sets),
            }
        alignment[scenario] = scenario_entry
    return alignment


def _missing_row_keys(spec: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[str]:
    completed_keys = {
        (row.get("scenario_tag"), row.get("controller"), int(row.get("seed", -1)), float(row.get("demand_multiplier", 1.0)))
        for row in rows
        if row.get("scenario_status") == "completed"
    }
    missing = []
    for row in spec:
        key = (row.get("scenario_tag"), row.get("controller"), int(row.get("seed", -1)), float(row.get("demand_multiplier", 1.0)))
        if key not in completed_keys:
            missing.append(f"{key[0]}/{key[3]}/{key[1]}/seed={key[2]}")
    return missing


def _status_for_payload(profile: str, dry_run: bool, spec: list[dict[str, Any]], rows: list[dict[str, Any]], gate_c: dict[str, Any], missing_reasons: list[str]) -> str:
    if profile == "pilot" or dry_run:
        return "PILOT_ONLY"
    if missing_reasons:
        return "INCONCLUSIVE"
    if len(rows) < len(spec):
        return "INCONCLUSIVE"
    if gate_c["status"] == "PASSED":
        return "PASSED"
    if gate_c["status"] == "FAILED":
        return "FAILED"
    return "INCONCLUSIVE"


def build_payload(
    *,
    profile: str,
    route_metadata: dict[str, str],
    spec: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    dry_run: bool = False,
    execution_mode: str = "executed",
    missing_row_reasons: list[str] | None = None,
    started_at: str | None = None,
    completed_at: str | None = None,
) -> dict[str, Any]:
    missing_row_reasons = list(missing_row_reasons or [])
    steps = max([int(row.get("steps", 0)) for row in spec], default=0)
    warmup = max([int(row.get("warmup", 0)) for row in spec], default=0)
    action_interval = max([int(row.get("action_interval", 0)) for row in spec], default=0)
    requested_seeds = sorted({int(row["seed"]) for row in spec})
    demand_multipliers = sorted({float(row["demand_multiplier"]) for row in spec})
    executed_rows = _completed_rows(rows)
    actual_seeds = sorted({int(row["seed"]) for row in executed_rows})
    missing_row_keys = _missing_row_keys(spec, executed_rows)
    if missing_row_keys:
        missing_row_reasons.append("missing required executed scenario/controller/seed/demand-multiplier rows")
    demand_provenance = sorted(
        {
            json.dumps(row.get("demand_multiplier_provenance", {key: row.get(key) for key in ["demand_multiplier", "generated_route_file", "generated_sumocfg", "base_demand_total", "scaled_demand_total"]}), sort_keys=True)
            for row in spec
        }
    )
    gate_payload = {"profile": profile, "steps": steps, "warmup": warmup, "dry_run": dry_run, "scenario_results": rows}
    gate_c = evaluate_gate_c(gate_payload)
    status = _status_for_payload(profile, dry_run, spec, executed_rows, gate_c, missing_row_reasons)
    paired_statistics = gate_c.get("primary_metric_rule", {}).get("metric_results", [])
    payload = {
        "experiment": "phase11_long_horizon_paired_seed_evidence",
        "status": status,
        **route_metadata,
        "profile": profile,
        "steps": steps,
        "warmup": warmup,
        "action_interval": action_interval,
        "dry_run": bool(dry_run),
        "execution_mode": execution_mode,
        "started_at": started_at,
        "completed_at": completed_at,
        "main_profile_target": {"min_steps": 3600, "min_warmup": 900, "target_seed_count": 20, "required_demand_multipliers": [0.8, 1.0, 1.2]},
        "actual_seed_count": len(actual_seeds),
        "requested_seed_count": len(requested_seeds),
        "seed_count_limitation": None if len(requested_seeds) >= 20 else "fewer than 20 paired seeds configured; main evidence is inconclusive unless user-approved",
        "seeds": requested_seeds,
        "demand_multipliers": demand_multipliers,
        "demand_scaling_method": DEMAND_SCALING_METHOD,
        "demand_scaling_provenance": [json.loads(item) for item in demand_provenance],
        "paired_seed_design": "same seeds for proposed and comparators within each scenario and demand multiplier",
        "required_binding_scenarios": list(BINDING_EVIDENCE_SCENARIOS),
        "binding_evidence_scenarios": list(BINDING_EVIDENCE_SCENARIOS),
        "slack_context_scenarios": list(SLACK_CONTEXT_SCENARIOS),
        "proposed_controller": PROPOSED_CONTROLLER,
        "required_gate_c_comparators": list(REQUIRED_GATE_C_COMPARATORS),
        "optional_context_controllers": list(OPTIONAL_CONTEXT_CONTROLLERS),
        "controllers": sorted({str(row["controller"]) for row in spec}),
        "statistical_family": GATE_C_STATISTICAL_FAMILY,
        "metric_schema": {field: "CLOP-04 metric" for field in METRIC_FIELDS},
        "objective_component_schema": {
            "row_field": "objective_components",
            "fields": sorted(OBJECTIVE_COMPONENT_FIELDS),
            "component_builder": "build_objective_components_from_metrics",
            "aggregation_note": "Nested objective components remain row-level audit fields and are not CI-aggregated through METRIC_FIELDS.",
        },
        "finite_storage_state_schema": {
            "row_field": "finite_storage_state",
            "fields": sorted(FINITE_STORAGE_STATE_FIELDS),
            "validation_helpers": ["validate_finite_storage_state", "validate_state_objective_sample"],
        },
        "scenario_results": rows,
        "spec": spec,
        "paired_statistics": paired_statistics,
        "paired_seed_alignment": paired_seed_alignment(rows, spec),
        "gate_c": gate_c,
        "actual_row_count": len(executed_rows),
        "raw_row_count": len(rows),
        "expected_row_count": len(spec),
        "all_rows_executed": len(executed_rows) == len(spec) and not dry_run,
        "missing_row_keys": missing_row_keys[:500],
        "missing_row_key_count": len(missing_row_keys),
        "missing_row_reasons": sorted(set(missing_row_reasons)),
        "phase11_scope": "closed-loop paired-seed evidence in predeclared binding stress regimes only",
        "caveats": [
            "Pilot or spec-only artifacts validate plumbing only and are not Gate C dominance evidence.",
            "A main artifact with missing executions is fail-closed as INCONCLUSIVE or FAILED, not a dominance claim.",
            "Phase 12 must regenerate final manuscript inputs and claim templates from raw Phase 11 artifacts.",
            "Phase 10 smoke rows are capability context only and are not imported as paired-seed dominance evidence.",
        ],
    }
    validate_payload_scope(payload)
    return payload


def dry_run_placeholder_rows(spec: list[dict[str, Any]], route_metadata: dict[str, str]) -> list[dict[str, Any]]:
    rows = []
    for item in spec:
        rows.append(
            {
                "network": item["network"],
                "scenario_tag": item["scenario_tag"],
                "controller": item["controller"],
                "seed": int(item["seed"]),
                "steps": int(item["steps"]),
                "warmup": int(item["warmup"]),
                "action_interval": int(item["action_interval"]),
                "profile": item["profile"],
                "scenario_status": "dry_run_placeholder",
                "feasibility_status": "not_executed",
                **route_metadata,
                "sumocfg": item["generated_sumocfg"],
                "base_sumocfg": item["base_sumocfg"],
                "demand_multiplier": item["demand_multiplier"],
                "demand_scaling_method": item["demand_scaling_method"],
                "base_demand_total": item["base_demand_total"],
                "scaled_demand_total": item["scaled_demand_total"],
                "generated_route_file": item["generated_route_file"],
                "generated_sumocfg": item["generated_sumocfg"],
                "demand_multiplier_provenance": item["demand_multiplier_provenance"],
                "placeholder_reason": "dry-run spec-only mode; not executed by SUMO",
            }
        )
    return rows


def execute_spec(
    spec: list[dict[str, Any]],
    route_metadata: dict[str, str],
    *,
    dry_run: bool,
    execution_row_limit: int | None,
    progress_out: Path | None = None,
    resume_progress: Path | None = None,
    max_new_rows: int | None = None,
) -> tuple[list[dict[str, Any]], list[str], str]:
    if dry_run:
        placeholder_rows = dry_run_placeholder_rows(spec, route_metadata)
        if progress_out is not None:
            progress_out.parent.mkdir(parents=True, exist_ok=True)
            progress_payload = {
                "total_rows": len(spec),
                "completed_rows": 0,
                "failed_rows": len(spec),
                "completed_row_keys": [],
                "attempted_row_keys": [],
                "failure_reasons": ["dry-run requested; no SUMO rows executed"],
                "dry_run": True,
            }
            progress_out.write_text(json.dumps(progress_payload, indent=2), encoding="utf-8")
        return placeholder_rows, ["dry-run requested; no SUMO rows executed"], "dry_run_spec_only"
    rows: list[dict[str, Any]] = []
    reasons: list[str] = []
    attempted_row_keys: list[str] = []
    progress_enabled = progress_out is not None
    if execution_row_limit is not None and len(spec) > execution_row_limit:
        spec = spec[:execution_row_limit]
    if resume_progress is not None and resume_progress.exists():
        progress = load_progress(resume_progress, spec)
        rows = list(progress["completed_rows"])
        attempted_row_keys = list(progress["attempted_row_keys"])
        reasons = list(progress["failure_reasons"])
    elif resume_progress is not None and progress_out is None:
        raise FileNotFoundError(resume_progress)
    completed_keys = {row_key(row) for row in rows}
    new_rows_attempted = 0
    for item in spec:
        key = row_key(item)
        if key in completed_keys:
            continue
        if max_new_rows is not None and new_rows_attempted >= max_new_rows:
            break
        if key not in attempted_row_keys:
            attempted_row_keys.append(key)
        new_rows_attempted += 1
        try:
            row = run_experiment(
                item["network"],
                item["controller"],
                item["seed"],
                item["steps"],
                item["warmup"],
                item["action_interval"],
                route_metadata,
                item["scenario_tag"],
                sumocfg_override=item.get("generated_sumocfg"),
            )
            row.update(
                {
                    "profile": item["profile"],
                    "demand_multiplier": item["demand_multiplier"],
                    "demand_scaling_method": item.get("demand_scaling_method", DEMAND_SCALING_METHOD),
                    "base_demand_total": item.get("base_demand_total"),
                    "scaled_demand_total": item.get("scaled_demand_total"),
                    "generated_route_file": item.get("generated_route_file"),
                    "generated_sumocfg": item.get("generated_sumocfg"),
                    "base_sumocfg": item.get("base_sumocfg"),
                    "demand_multiplier_provenance": item.get("demand_multiplier_provenance"),
                }
            )
            rows.append(row)
            completed_keys.add(key)
        except Exception as exc:
            reasons.append(f"{item['scenario_tag']}/{item['demand_multiplier']}/{item['controller']}/seed={item['seed']}: {type(exc).__name__}: {exc}")
        if progress_enabled:
            write_progress(progress_out, spec, rows, attempted_row_keys, reasons)
    if progress_enabled and not progress_out.exists():
        write_progress(progress_out, spec, rows, attempted_row_keys, reasons)
    if max_new_rows is not None:
        mode = "executed_incremental_with_progress" if progress_enabled or resume_progress is not None else "executed_incremental"
    else:
        mode = "executed_with_progress" if progress_enabled or resume_progress is not None else "executed"
    return rows, reasons, mode


def main() -> None:
    args = parse_args()
    validate_args(args)
    set_proposed_controller(args.proposed_controller)
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    spec = build_phase11_spec(
        profile=args.profile,
        controllers=args.controllers,
        seeds=args.seeds,
        steps=args.steps,
        warmup=args.warmup,
        action_interval=args.action_interval,
        demand_multipliers=args.demand_multipliers,
    )
    spec = materialize_demand_inputs(spec, Path(args.scaled_input_dir))
    route_metadata = load_route_metadata(Path(args.route_json))
    if args.execution_row_limit is None:
        execution_row_limit = DEFAULT_MAIN_EXECUTION_ROW_LIMIT if args.profile == "main" else len(spec)
    else:
        execution_row_limit = args.execution_row_limit
    rows, missing_reasons, execution_mode = execute_spec(
        spec,
        route_metadata,
        dry_run=args.dry_run,
        execution_row_limit=execution_row_limit,
        progress_out=Path(args.progress_out) if args.progress_out else None,
        resume_progress=Path(args.resume_progress) if args.resume_progress else None,
    )
    completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload = build_payload(
        profile=args.profile,
        route_metadata=route_metadata,
        spec=spec,
        rows=rows,
        dry_run=args.dry_run,
        execution_mode=execution_mode,
        missing_row_reasons=missing_reasons,
        started_at=started_at,
        completed_at=completed_at,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "profile": args.profile, "spec_rows": len(spec), "result_rows": len(rows), "status": payload["status"], "execution_mode": execution_mode}, indent=2))


if __name__ == "__main__":
    main()
