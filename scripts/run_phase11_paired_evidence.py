#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from scipy import stats

from run_closed_loop_sumo import CONTROLLER_REGISTRY, METRIC_FIELDS, load_route_metadata, run_experiment

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
LOWER_IS_BETTER_METRICS = set(GATE_C_PRIMARY_METRICS) | {"switching_count", "avg_travel_time", "mean_queue", "max_queue"}
HIGHER_IS_BETTER_METRICS = {"throughput", "completion_rate", "completed_vehicles"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["pilot", "main"], default="main")
    parser.add_argument("--controllers", nargs="+", default=list(DEFAULT_CONTROLLERS))
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--warmup", type=int, default=None)
    parser.add_argument("--action-interval", type=int, default=10)
    parser.add_argument("--demand-multipliers", nargs="+", type=float, default=list(DEFAULT_DEMAND_MULTIPLIERS))
    parser.add_argument("--out", default="experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json")
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


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
    if not demand_multipliers:
        raise ValueError("At least one demand multiplier is required")
    if any(float(multiplier) <= 0.0 for multiplier in demand_multipliers):
        raise ValueError("Demand multipliers must be positive")


def demand_multiplier_contract(demand_multiplier: float) -> dict[str, Any]:
    return {
        "demand_multiplier": float(demand_multiplier),
        "demand_scaling_method": "route_demand_scaling",
        "requires_actual_sumo_behavior_change": True,
        "metadata_only_valid": False,
        "base_demand_total_required": True,
        "scaled_demand_total_required": True,
        "demand_source_required": True,
        "acceptable_methods": ["route_demand_scaling", "insertion_intensity_scaling"],
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
    if len(differences) <= 1 or len(set(differences)) == 1:
        value = float(differences[0]) if differences else 0.0
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


def _diagnostics(proposed_values: list[float], comparator_values: list[float], differences: list[float]) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {}
    try:
        alternative = "less"
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
        "diagnostics": _diagnostics(proposed_values, comparator_values, differences),
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
    for rank, (idx, pvalue) in enumerate(sorted(entries, key=lambda item: item[1]), start=1):
        adjusted_by_idx[idx] = min((m - rank + 1) * pvalue, 1.0)
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


def build_payload(*, profile: str, route_metadata: dict[str, str], spec: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "experiment": "phase11_long_horizon_paired_seed_evidence",
        "status": "SPEC_ONLY" if not rows else "INCONCLUSIVE",
        **route_metadata,
        "profile": profile,
        "phase11_scope": "closed-loop paired-seed evidence in predeclared binding stress regimes only",
        "binding_evidence_scenarios": list(BINDING_EVIDENCE_SCENARIOS),
        "slack_context_scenarios": list(SLACK_CONTEXT_SCENARIOS),
        "proposed_controller": PROPOSED_CONTROLLER,
        "required_gate_c_comparators": list(REQUIRED_GATE_C_COMPARATORS),
        "optional_context_controllers": list(OPTIONAL_CONTEXT_CONTROLLERS),
        "metric_schema": {field: "CLOP metric" for field in METRIC_FIELDS},
        "spec": spec,
        "scenario_results": rows,
        "caveats": [
            "Pilot or spec-only artifacts validate plumbing only and are not Gate C dominance evidence.",
            "Phase 12 must regenerate final manuscript inputs and claim templates from raw Phase 11 artifacts.",
        ],
    }


def main() -> None:
    args = parse_args()
    spec = build_phase11_spec(
        profile=args.profile,
        controllers=args.controllers,
        seeds=args.seeds,
        steps=args.steps,
        warmup=args.warmup,
        action_interval=args.action_interval,
        demand_multipliers=args.demand_multipliers,
    )
    route_metadata = load_route_metadata(Path(args.route_json))
    rows = [] if args.dry_run else [run_experiment(**{key: row[key] for key in ["network", "controller", "seed", "steps", "warmup", "action_interval", "scenario_tag"]}, route_metadata=route_metadata) for row in spec]
    payload = build_payload(profile=args.profile, route_metadata=route_metadata, spec=spec, rows=rows)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "profile": args.profile, "spec_rows": len(spec), "result_rows": len(rows), "status": payload["status"]}, indent=2))


if __name__ == "__main__":
    main()
