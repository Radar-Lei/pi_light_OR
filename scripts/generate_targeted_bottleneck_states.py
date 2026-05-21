#!/usr/bin/env python3
"""Generate targeted bottleneck/spillback states for Block 1.

These states are deliberately synthetic but use the arterial edge names and
movement topology. They are designed to expose cases where downstream scarcity
changes the ranking relative to ordinary local pressure.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sumolib

from sample_sumo_states import build_network_metadata


def make_sample(time: float, queues: dict[str, float], capacities: dict[str, float], tls_movements: dict) -> dict:
    vehicle_counts = {edge: max(q, 0.0) for edge, q in queues.items()}
    return {
        "time": time,
        "queues": queues,
        "vehicle_counts": vehicle_counts,
        "capacities": capacities,
        "tls_movements": tls_movements,
    }


def base_queues(capacities: dict[str, float]) -> dict[str, float]:
    return {edge: 0.05 * cap for edge, cap in capacities.items()}


def generate(net_file: Path, tls: str) -> dict:
    metadata = build_network_metadata(net_file)
    capacities = metadata["edge_capacity"]
    tls_movements = metadata["tls_movements"]
    moves = tls_movements[tls]

    samples = []
    t = 0.0
    for idx, (up, down) in enumerate(moves[:12]):
        q = base_queues(capacities)
        q[up] = 0.65 * capacities[up]
        q[down] = 0.98 * capacities[down]
        for other_up, other_down in moves[:12]:
            if other_up != up:
                q[other_up] = max(q.get(other_up, 0.0), 0.35 * capacities[other_up])
            if other_down != down:
                q[other_down] = min(q.get(other_down, 0.0), 0.20 * capacities[other_down])
        samples.append(make_sample(t, q, capacities, tls_movements))
        t += 1.0

    # Conflict cases by incoming approach: all turns from the high-pressure approach
    # feed storage-constrained downstream links, while a lower-pressure approach has one open turn.
    by_up: dict[str, list[tuple[str, str]]] = {}
    for up, down in moves[:12]:
        by_up.setdefault(up, []).append((up, down))
    approaches = sorted(by_up)
    for idx, blocked_up in enumerate(approaches):
        open_up = approaches[(idx + 1) % len(approaches)]
        q = base_queues(capacities)
        for other_up, other_down in moves[:12]:
            q[other_up] = 0.05 * capacities[other_up]
            q[other_down] = 0.05 * capacities[other_down]

        q[blocked_up] = 1.00 * capacities[blocked_up]
        blocked_downs = {blocked_down for _, blocked_down in by_up[blocked_up]}
        for blocked_down in blocked_downs:
            q[blocked_down] = 0.82 * capacities[blocked_down]

        open_down = next(
            (down for _, down in by_up[open_up] if down not in blocked_downs),
            by_up[open_up][0][1],
        )
        q[open_down] = 0.05 * capacities[open_down]
        q[open_up] = min(capacities[open_up], q[open_down] + 14.0)
        samples.append(make_sample(t, q, capacities, tls_movements))
        t += 1.0

    return {
        "network": "arterial_targeted_bottleneck",
        "net_file": str(net_file),
        "tls": tls,
        "num_samples": len(samples),
        "samples": samples,
        "note": "Synthetic targeted states using arterial topology; designed to stress downstream scarcity vs pressure.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--net-file", default="networks/arterial/arterial.net.xml")
    parser.add_argument("--tls", default="C3")
    parser.add_argument("--out", default="experiments/dual_sensitivity/targeted_bottleneck_states.json")
    args = parser.parse_args()

    payload = generate(Path(args.net_file), args.tls)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "num_samples": payload["num_samples"]}, indent=2))


if __name__ == "__main__":
    main()
