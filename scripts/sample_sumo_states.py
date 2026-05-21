#!/usr/bin/env python3
"""Sample queue states from existing SUMO networks for Block 1 recovery.

The sampler records edge-level halting counts and estimated capacities. It
also infers simple movements from incoming to outgoing edges at traffic-light
junctions using SUMO connection metadata.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import sumolib
import traci


def estimate_edge_capacity(edge: Any, jam_spacing_m: float) -> float:
    length = max(float(edge.getLength()), 1.0)
    lanes = max(len(edge.getLanes()), 1)
    return max(1.0, length * lanes / jam_spacing_m)


def build_network_metadata(net_file: Path) -> dict[str, Any]:
    net = sumolib.net.readNet(str(net_file), withInternal=False)
    edge_capacity = {}
    for edge in net.getEdges():
        edge_id = edge.getID()
        if edge_id.startswith(":"):
            continue
        edge_capacity[edge_id] = estimate_edge_capacity(edge, jam_spacing_m=7.5)

    tls_movements: dict[str, set[tuple[str, str]]] = {}
    root = ET.parse(net_file).getroot()
    for conn in root.findall("connection"):
        tls_id = conn.get("tl")
        from_edge = conn.get("from")
        to_edge = conn.get("to")
        if not tls_id or not from_edge or not to_edge:
            continue
        if from_edge.startswith(":") or to_edge.startswith(":"):
            continue
        tls_movements.setdefault(tls_id, set()).add((from_edge, to_edge))
    return {
        "edge_capacity": edge_capacity,
        "tls_movements": {tls: sorted(moves) for tls, moves in tls_movements.items()},
    }


def sample_states(
    sumocfg: Path,
    net_file: Path,
    steps: int,
    sample_every: int,
    warmup: int,
    seed: int,
) -> list[dict[str, Any]]:
    metadata = build_network_metadata(net_file)
    edge_capacity = metadata["edge_capacity"]
    tls_movements = metadata["tls_movements"]
    edge_ids = sorted(edge_capacity)

    cmd = [
        "sumo",
        "-c",
        str(sumocfg),
        "--seed",
        str(seed),
        "--no-step-log",
        "true",
        "--duration-log.disable",
        "true",
    ]
    traci.start(cmd)
    samples: list[dict[str, Any]] = []
    try:
        for step in range(steps + 1):
            traci.simulationStep()
            if step < warmup or (step - warmup) % sample_every != 0:
                continue
            queues = {edge_id: float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids}
            vehicle_counts = {edge_id: float(traci.edge.getLastStepVehicleNumber(edge_id)) for edge_id in edge_ids}
            samples.append(
                {
                    "time": float(traci.simulation.getTime()),
                    "queues": queues,
                    "vehicle_counts": vehicle_counts,
                    "capacities": edge_capacity,
                    "tls_movements": tls_movements,
                }
            )
    finally:
        traci.close(False)
    return samples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", choices=["single", "arterial"], default="arterial")
    parser.add_argument("--steps", type=int, default=900)
    parser.add_argument("--sample-every", type=int, default=60)
    parser.add_argument("--warmup", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260520)
    parser.add_argument("--out", default="experiments/dual_sensitivity/sumo_sampled_states.json")
    args = parser.parse_args()

    if args.network == "single":
        base = Path("networks/single_intersection")
        sumocfg = base / "single_intersection.sumocfg"
        net_file = base / "single_intersection.net.xml"
    else:
        base = Path("networks/arterial")
        sumocfg = base / "arterial.sumocfg"
        net_file = base / "arterial.net.xml"

    samples = sample_states(sumocfg, net_file, args.steps, args.sample_every, args.warmup, args.seed)
    payload = {
        "network": args.network,
        "sumocfg": str(sumocfg),
        "net_file": str(net_file),
        "seed": args.seed,
        "steps": args.steps,
        "sample_every": args.sample_every,
        "warmup": args.warmup,
        "num_samples": len(samples),
        "samples": samples,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "num_samples": len(samples)}, indent=2))


if __name__ == "__main__":
    main()
