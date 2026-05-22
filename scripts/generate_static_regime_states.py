#!/usr/bin/env python3
"""Generate labeled static-regime states for the Phase 3 kill gate.

The output deliberately preserves the existing sampled-state schema consumed by
`scenario_from_sample()`: each supported/proxy sample includes time, queues,
vehicle_counts, capacities, and tls_movements. Regimes that the current sample
schema cannot encode as explicit primal constraints are marked as proxy or
unsupported instead of being upgraded into stronger corridor/supply claims.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from sample_sumo_states import build_network_metadata


SCRIPT_NAME = "generate_static_regime_states.py"
DEFAULT_REGIMES = [
    "slack",
    "storage_binding",
    "supply_binding_proxy",
    "corridor_bottleneck_proxy",
    "incident_capacity_drop",
    "demand_shift_proxy",
]
SUPPORTED_REGIMES = set(DEFAULT_REGIMES) | {
    "supply_binding_unsupported",
    "corridor_bottleneck_unsupported",
}
SAMPLE_REQUIRED_FIELDS = {"time", "queues", "vehicle_counts", "capacities", "tls_movements"}


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("--target-per-regime must be positive")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0.0:
        raise argparse.ArgumentTypeError("factors must be positive")
    return parsed


def parse_regimes(raw_regimes: list[str] | None) -> list[str]:
    if not raw_regimes:
        return list(DEFAULT_REGIMES)
    regimes: list[str] = []
    for raw in raw_regimes:
        for part in raw.split(","):
            regime = part.strip()
            if regime:
                regimes.append(regime)
    unknown = sorted(set(regimes) - SUPPORTED_REGIMES)
    if unknown:
        raise ValueError(f"Unknown regimes: {unknown}. Available regimes: {sorted(SUPPORTED_REGIMES)}")
    if not regimes:
        raise ValueError("At least one regime must be requested")
    return regimes


def base_queues(capacities: dict[str, float], fraction: float = 0.05) -> dict[str, float]:
    return {edge: fraction * float(capacity) for edge, capacity in capacities.items()}


def clamp_queue(value: float, capacity: float) -> float:
    return max(0.0, min(float(value), float(capacity)))


def make_sample(
    time: float,
    queues: dict[str, float],
    capacities: dict[str, float],
    tls_movements: dict[str, list[tuple[str, str]]],
    regime: str,
    regime_detail: str,
    generated_by: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_capacities = {edge: float(capacity) for edge, capacity in capacities.items()}
    normalized_queues = {
        edge: clamp_queue(queues.get(edge, 0.0), normalized_capacities.get(edge, 1.0))
        for edge in normalized_capacities
    }
    sample = {
        "time": float(time),
        "queues": normalized_queues,
        "vehicle_counts": {edge: max(value, 0.0) for edge, value in normalized_queues.items()},
        "capacities": normalized_capacities,
        "tls_movements": tls_movements,
        "regime": regime,
        "regime_detail": regime_detail,
        "generated_by": generated_by,
    }
    if extra:
        sample.update(extra)
    missing = SAMPLE_REQUIRED_FIELDS - set(sample)
    if missing:
        raise ValueError(f"Internal sample schema error; missing fields: {sorted(missing)}")
    return sample


def require_tls_movements(tls_movements: dict[str, list[tuple[str, str]]], tls: str) -> list[tuple[str, str]]:
    moves = list(tls_movements.get(tls, []))
    if not moves:
        available = sorted(tls_movements)
        raise ValueError(f"Missing TLS metadata for {tls!r}. Available TLS IDs: {available}")
    return moves


def choose_move(moves: list[tuple[str, str]], rng: random.Random, idx: int) -> tuple[str, str]:
    return moves[(idx + rng.randrange(len(moves))) % len(moves)]


def group_by_upstream(moves: list[tuple[str, str]]) -> dict[str, list[tuple[str, str]]]:
    grouped: dict[str, list[tuple[str, str]]] = {}
    for up, down in moves:
        grouped.setdefault(up, []).append((up, down))
    return grouped


def generated_by(args: argparse.Namespace, regime: str) -> dict[str, Any]:
    return {
        "script": SCRIPT_NAME,
        "regime": regime,
        "seed": args.seed,
        "target_per_regime": args.target_per_regime,
        "net_file": str(args.net_file),
        "tls": args.tls,
    }


def generate_slack(
    capacities: dict[str, float],
    tls_movements: dict[str, list[tuple[str, str]]],
    moves: list[tuple[str, str]],
    target: int,
    args: argparse.Namespace,
    rng: random.Random,
    start_time: float,
) -> list[dict[str, Any]]:
    samples = []
    for idx in range(target):
        q = base_queues(capacities, 0.02 + 0.02 * ((idx % 4) / 3.0))
        up, down = choose_move(moves, rng, idx)
        q[up] = min(0.25 * capacities[up], q[up] + (idx % 3) * 0.03 * capacities[up])
        q[down] = min(0.20 * capacities[down], q[down] + (idx % 2) * 0.02 * capacities[down])
        samples.append(
            make_sample(
                start_time + idx,
                q,
                capacities,
                tls_movements,
                "slack",
                "Low-occupancy queue perturbation; storage constraints intended to be nonbinding.",
                generated_by(args, "slack"),
            )
        )
    return samples


def generate_storage_binding(
    capacities: dict[str, float],
    tls_movements: dict[str, list[tuple[str, str]]],
    moves: list[tuple[str, str]],
    target: int,
    args: argparse.Namespace,
    rng: random.Random,
    start_time: float,
) -> list[dict[str, Any]]:
    samples = []
    by_up = group_by_upstream(moves)
    approaches = sorted(by_up)
    for idx in range(target):
        q = base_queues(capacities, 0.05)
        up, down = choose_move(moves, rng, idx)
        q[up] = 0.60 * capacities[up]
        q[down] = (0.86 + 0.12 * ((idx % 5) / 4.0)) * capacities[down]
        if approaches:
            blocked_up = approaches[idx % len(approaches)]
            for other_up, other_down in by_up[blocked_up]:
                q[other_up] = max(q.get(other_up, 0.0), 0.70 * capacities[other_up])
                q[other_down] = max(q.get(other_down, 0.0), 0.82 * capacities[other_down])
        samples.append(
            make_sample(
                start_time + idx,
                q,
                capacities,
                tls_movements,
                "storage_binding",
                f"Downstream edge {down} filled near storage limit while upstream edge {up} remains queued.",
                generated_by(args, "storage_binding"),
                {"bottleneck_edge": down, "upstream_edge": up},
            )
        )
    return samples


def generate_incident_capacity_drop(
    capacities: dict[str, float],
    tls_movements: dict[str, list[tuple[str, str]]],
    moves: list[tuple[str, str]],
    target: int,
    args: argparse.Namespace,
    rng: random.Random,
    start_time: float,
) -> list[dict[str, Any]]:
    samples = []
    factors = list(args.capacity_drop_factors)
    for idx in range(target):
        up, down = choose_move(moves, rng, idx)
        factor = factors[idx % len(factors)]
        dropped_capacities = dict(capacities)
        dropped_capacities[down] = max(1.0, capacities[down] * factor)
        q = base_queues(dropped_capacities, 0.05)
        q[up] = min(dropped_capacities[up], 0.65 * dropped_capacities[up])
        q[down] = min(dropped_capacities[down], 0.92 * dropped_capacities[down])
        samples.append(
            make_sample(
                start_time + idx,
                q,
                dropped_capacities,
                tls_movements,
                "incident_capacity_drop",
                f"Capacity of downstream edge {down} reduced by factor {factor:.3g} as an incident proxy.",
                generated_by(args, "incident_capacity_drop"),
                {"capacity_drop_edge": down, "capacity_drop_factor": factor},
            )
        )
    return samples


def generate_demand_shift_proxy(
    capacities: dict[str, float],
    tls_movements: dict[str, list[tuple[str, str]]],
    moves: list[tuple[str, str]],
    target: int,
    args: argparse.Namespace,
    rng: random.Random,
    start_time: float,
) -> list[dict[str, Any]]:
    samples = []
    factors = list(args.demand_shift_factors)
    by_up = group_by_upstream(moves)
    approaches = sorted(by_up)
    for idx in range(target):
        factor = factors[idx % len(factors)]
        q = base_queues(capacities, 0.04)
        if approaches:
            dominant_up = approaches[(idx + rng.randrange(len(approaches))) % len(approaches)]
            for up, down in by_up[dominant_up]:
                q[up] = min(capacities[up], (0.25 + 0.18 * factor) * capacities[up])
                q[down] = min(capacities[down], (0.08 + 0.04 * (idx % 3)) * capacities[down])
        else:
            up, _ = choose_move(moves, rng, idx)
            q[up] = min(capacities[up], factor * 0.25 * capacities[up])
        samples.append(
            make_sample(
                start_time + idx,
                q,
                capacities,
                tls_movements,
                "demand_shift_proxy",
                f"Queue-pattern proxy for demand shift with factor {factor:.3g}; no explicit demand field is consumed downstream.",
                generated_by(args, "demand_shift_proxy"),
                {"demand_shift_factor": factor},
            )
        )
    return samples


def generate_supply_binding_proxy(
    capacities: dict[str, float],
    tls_movements: dict[str, list[tuple[str, str]]],
    moves: list[tuple[str, str]],
    target: int,
    args: argparse.Namespace,
    rng: random.Random,
    start_time: float,
) -> list[dict[str, Any]]:
    samples = []
    for idx in range(target):
        up, down = choose_move(moves, rng, idx)
        q = base_queues(capacities, 0.04)
        q[up] = 0.80 * capacities[up]
        q[down] = 0.76 * capacities[down]
        samples.append(
            make_sample(
                start_time + idx,
                q,
                capacities,
                tls_movements,
                "supply_binding_proxy",
                "Proxy only: current sample-to-scenario conversion has no explicit per-movement supply constraint field; encoded as high downstream occupancy.",
                generated_by(args, "supply_binding_proxy"),
                {"proxy_reason": "no explicit downstream supply field in current schema"},
            )
        )
    return samples


def generate_corridor_bottleneck_proxy(
    capacities: dict[str, float],
    tls_movements: dict[str, list[tuple[str, str]]],
    moves: list[tuple[str, str]],
    target: int,
    args: argparse.Namespace,
    rng: random.Random,
    start_time: float,
) -> list[dict[str, Any]]:
    samples = []
    by_up = group_by_upstream(moves)
    approaches = sorted(by_up)
    for idx in range(target):
        q = base_queues(capacities, 0.04)
        if approaches:
            congested_up = approaches[idx % len(approaches)]
            for up, down in by_up[congested_up]:
                q[up] = max(q[up], 0.72 * capacities[up])
                q[down] = max(q[down], 0.78 * capacities[down])
        else:
            up, down = choose_move(moves, rng, idx)
            q[up] = 0.72 * capacities[up]
            q[down] = 0.78 * capacities[down]
        samples.append(
            make_sample(
                start_time + idx,
                q,
                capacities,
                tls_movements,
                "corridor_bottleneck_proxy",
                "Proxy only: current static schema has no corridor-level capacity constraint; encoded as approach/corridor queue concentration.",
                generated_by(args, "corridor_bottleneck_proxy"),
                {"proxy_reason": "no explicit corridor capacity constraint in current schema"},
            )
        )
    return samples


def unsupported_status(regime: str) -> dict[str, Any]:
    return {
        "status": "unsupported_by_current_model",
        "num_samples": 0,
        "rationale": (
            "The current sample schema consumed by scenario_from_sample() does not encode "
            "explicit supply or corridor-level service constraints, so this regime is "
            "recorded as unsupported instead of fabricating binding evidence."
        ),
    }


def generate_payload(args: argparse.Namespace) -> dict[str, Any]:
    metadata = build_network_metadata(args.net_file)
    capacities = {edge: float(capacity) for edge, capacity in metadata["edge_capacity"].items()}
    tls_movements = metadata["tls_movements"]
    moves = require_tls_movements(tls_movements, args.tls)
    rng = random.Random(args.seed)

    generators = {
        "slack": generate_slack,
        "storage_binding": generate_storage_binding,
        "supply_binding_proxy": generate_supply_binding_proxy,
        "corridor_bottleneck_proxy": generate_corridor_bottleneck_proxy,
        "incident_capacity_drop": generate_incident_capacity_drop,
        "demand_shift_proxy": generate_demand_shift_proxy,
    }

    samples: list[dict[str, Any]] = []
    regime_status: dict[str, Any] = {}
    t = 0.0
    for regime in args.regimes:
        if regime in {"supply_binding_unsupported", "corridor_bottleneck_unsupported"}:
            regime_status[regime] = unsupported_status(regime)
            continue
        generated = generators[regime](capacities, tls_movements, moves, args.target_per_regime, args, rng, t)
        samples.extend(generated)
        regime_status[regime] = {
            "status": "proxy" if regime.endswith("_proxy") else "supported_synthetic",
            "num_samples": len(generated),
            "rationale": generated[0]["regime_detail"] if generated else "No samples generated.",
        }
        t += float(len(generated))

    counts_by_regime: dict[str, int] = {}
    for sample in samples:
        counts_by_regime[sample["regime"]] = counts_by_regime.get(sample["regime"], 0) + 1

    return {
        "network": "arterial_static_regime_block3",
        "net_file": str(args.net_file),
        "tls": args.tls,
        "num_samples": len(samples),
        "target_per_regime": args.target_per_regime,
        "counts_by_regime": counts_by_regime,
        "regime_status": regime_status,
        "generation_config": {
            "script": SCRIPT_NAME,
            "seed": args.seed,
            "regimes": args.regimes,
            "target_per_regime": args.target_per_regime,
            "capacity_drop_factors": args.capacity_drop_factors,
            "demand_shift_factors": args.demand_shift_factors,
        },
        "samples": samples,
        "sample_sufficiency_note": (
            "Raw generated sample counts are preliminary. Final KILL-03 sufficiency is "
            "determined by run_static_kill_gate.py after scenario_from_sample() and "
            "build_example() conversion into valid examples."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--net-file", type=Path, default=Path("networks/arterial/arterial.net.xml"))
    parser.add_argument("--tls", default="C3")
    parser.add_argument("--regimes", nargs="*", default=None)
    parser.add_argument("--target-per-regime", type=positive_int, default=200)
    parser.add_argument("--seed", type=int, default=20260523)
    parser.add_argument("--capacity-drop-factors", nargs="+", type=positive_float, default=[0.35, 0.50, 0.70])
    parser.add_argument("--demand-shift-factors", nargs="+", type=positive_float, default=[0.75, 1.00, 1.50])
    parser.add_argument("--out", default="experiments/dual_sensitivity/block3_regime_states.json")
    args = parser.parse_args()

    try:
        args.regimes = parse_regimes(args.regimes)
        payload = generate_payload(args)
    except (KeyError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(out_path),
                "num_samples": payload["num_samples"],
                "counts_by_regime": payload["counts_by_regime"],
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
