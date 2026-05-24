#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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
