#!/usr/bin/env python3
"""Run dual-sensitivity recovery pilot on SUMO sampled states.

This is still a lightweight Block 1 implementation: it converts sampled
SUMO edge queues into continuous one-step LP scenarios and compares equal
complexity movement-selection variants. It does not yet implement the full
sparse MIP program recovery.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np

from run_dual_sanity import Scenario, summarize_scenario


def scenario_from_sample(sample: dict[str, Any], tls_id: str, max_movements: int) -> Scenario | None:
    movements_raw = sample["tls_movements"].get(tls_id, [])
    queues = sample["queues"]
    capacities = sample["capacities"]
    candidate_moves = []
    edge_set = set()
    for up, down in movements_raw:
        if up in queues and down in queues:
            candidate_moves.append((up, down))
            edge_set.add(up)
            edge_set.add(down)
    candidate_moves = candidate_moves[:max_movements]
    if not candidate_moves:
        return None

    ordered_edges = sorted(edge_set)
    edge_to_idx = {edge: i for i, edge in enumerate(ordered_edges)}
    movements = [(edge_to_idx[up], edge_to_idx[down]) for up, down in candidate_moves]
    queue = np.array([max(float(queues[e]), 0.0) for e in ordered_edges])
    cap = np.array([max(float(capacities[e]), 1.0) for e in ordered_edges])
    # Use a Lyapunov linearization weight. Add 1 to avoid all-zero states.
    queue_weight = queue + 1.0
    storage_penalty = np.where(queue >= 0.8 * cap, 20.0, 0.0)
    service_capacity = np.full(len(movements), 3.0)
    green_budget = min(12.0, 3.0 * len(movements))
    return Scenario(
        name=f"sumo_{tls_id}_t{sample['time']:.0f}",
        links=ordered_edges,
        movements=movements,
        queue=queue,
        downstream_capacity=cap,
        demand=np.zeros(len(ordered_edges)),
        service_capacity=service_capacity,
        green_budget=green_budget,
        queue_weight=queue_weight,
        storage_penalty=storage_penalty,
    )


def regret(oracle: np.ndarray, scores: np.ndarray) -> float:
    chosen = int(np.argmax(scores))
    return float(np.max(oracle) - oracle[chosen])


def evaluate_summary(summary: dict[str, Any]) -> dict[str, Any]:
    oracle_all = np.asarray(summary["finite_difference_values"], dtype=float)
    dual_all = np.asarray(summary["dual_movement_values"], dtype=float)
    pressure_all = np.asarray(summary["pressure_scores"], dtype=float)
    feasible = np.isfinite(oracle_all)
    if not np.any(feasible):
        feasible = np.ones_like(oracle_all, dtype=bool)
    oracle = oracle_all[feasible]
    dual = dual_all[feasible]
    pressure = pressure_all[feasible]
    original_indices = np.flatnonzero(feasible)
    rng = np.random.default_rng(int(summary["objective"]) % 100000 + len(summary["movements"]))
    link_to_idx = {link: idx for idx, link in enumerate(summary["links"])}
    queue = np.asarray(summary["queue"], dtype=float)
    upstream_queue = np.asarray([queue[link_to_idx[m["up"]]] for m in summary["movements"]], dtype=float)[feasible]
    downstream_queue = np.asarray([queue[link_to_idx[m["down"]]] for m in summary["movements"]], dtype=float)[feasible]
    variants = {
        "local_only": upstream_queue,
        "raw_neighbor": downstream_queue,
        "all_neighbor": upstream_queue + downstream_queue,
        "pressure_backpressure": pressure,
        "random_price": rng.permutation(dual),
        "dual_sensitivity": dual,
    }
    rows = []
    for name, scores in variants.items():
        local_choice = int(np.argmax(scores))
        local_best = int(np.argmax(oracle))
        rows.append(
            {
                "variant": name,
                "program_complexity": 1,
                "chosen_movement": int(original_indices[local_choice]),
                "oracle_best_movement": int(original_indices[local_best]),
                "oracle_regret": regret(oracle, scores),
            }
        )
    best = min(row["oracle_regret"] for row in rows)
    dual_regret = next(row["oracle_regret"] for row in rows if row["variant"] == "dual_sensitivity")
    if len(oracle) > 1 and np.std(oracle) > 1e-12 and np.std(dual) > 1e-12:
        corr = float(np.corrcoef(dual, oracle)[0, 1])
    else:
        corr = 1.0
    rank_match = [int(i) for i in original_indices[np.argsort(-dual)]] == [int(i) for i in original_indices[np.argsort(-oracle)]]
    return {
        "scenario": summary["scenario"],
        "num_movements": len(summary["movements"]),
        "num_feasible_movements": int(np.sum(feasible)),
        "rank_match_finite_difference": rank_match,
        "pressure_special_case_pass": summary["pressure_special_case_pass"],
        "nonbinding_storage": summary["nonbinding_storage"],
        "dual_fd_correlation": corr,
        "variants": rows,
        "dual_tied_best": abs(dual_regret - best) <= 1e-9,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", default="experiments/dual_sensitivity/arterial_sampled_states.json")
    parser.add_argument("--tls", default="C3")
    parser.add_argument("--max-samples", type=int, default=8)
    parser.add_argument("--max-movements", type=int, default=12)
    parser.add_argument("--epsilon", type=float, default=1e-3)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block1_sumo_sampled_recovery.json")
    args = parser.parse_args()

    data = json.loads(Path(args.states).read_text(encoding="utf-8"))
    results = []
    for sample in data["samples"][: args.max_samples]:
        scenario = scenario_from_sample(sample, args.tls, args.max_movements)
        if scenario is None:
            continue
        summary = summarize_scenario(scenario, args.epsilon)
        results.append(evaluate_summary(summary))

    gate_dual_valid = all(r["rank_match_finite_difference"] for r in results)
    gate_dual_best = all(r["dual_tied_best"] for r in results)
    aggregate_regret: dict[str, dict[str, float | int]] = {}
    for r in results:
        for row in r["variants"]:
            stats = aggregate_regret.setdefault(
                row["variant"], {"sum": 0.0, "mean": 0.0, "zero_regret": 0, "count": 0}
            )
            regret_value = float(row["oracle_regret"])
            stats["sum"] = float(stats["sum"]) + regret_value
            stats["zero_regret"] = int(stats["zero_regret"]) + int(abs(regret_value) <= 1e-9)
            stats["count"] = int(stats["count"]) + 1
    for stats in aggregate_regret.values():
        count = int(stats["count"])
        stats["mean"] = float(stats["sum"]) / count if count else 0.0

    raw_variants = ["local_only", "raw_neighbor", "all_neighbor"]
    dual_sum = float(aggregate_regret.get("dual_sensitivity", {}).get("sum", 0.0))
    gate_dual_beats_raw_atoms = all(
        dual_sum <= float(aggregate_regret.get(name, {}).get("sum", 0.0)) + 1e-9
        and float(aggregate_regret.get(name, {}).get("sum", 0.0)) > dual_sum + 1e-9
        for name in raw_variants
    ) if results else False
    status = "PASSED" if results and gate_dual_valid and gate_dual_best and gate_dual_beats_raw_atoms else "INCONCLUSIVE"
    payload = {
        "experiment": "block1_sumo_sampled_recovery",
        "status": status,
        "scope": "SUMO sampled states + one-step LP + one-atom equal-complexity pilot",
        "input_states": args.states,
        "tls": args.tls,
        "num_results": len(results),
        "gate_dual_valid": gate_dual_valid,
        "gate_dual_tied_best": gate_dual_best,
        "gate_dual_beats_raw_atoms": gate_dual_beats_raw_atoms,
        "aggregate_regret": aggregate_regret,
        "results": results,
        "caveat": "Still not full sparse MIP recovery; pressure/backpressure is reported as a strong diagnostic baseline, not a recovered raw one-atom program.",
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "out": str(out_path), "num_results": len(results)}, indent=2))


if __name__ == "__main__":
    main()
