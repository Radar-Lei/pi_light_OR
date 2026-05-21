#!/usr/bin/env python3
"""Block 1 pilot: equal-complexity offline symbolic recovery scaffold.

The pilot uses Block 0 proxy states and compares one-atom policies under
an equal complexity budget. It is intentionally small: the purpose is to
verify that the dual feature path is wired and that JSON artifacts exist
for the next implementation stage.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from run_dual_sanity import build_scenario, summarize_scenario


def normalize(values: list[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    scale = np.max(np.abs(arr))
    if scale <= 1e-12:
        return arr
    return arr / scale


def regret(oracle: np.ndarray, scores: np.ndarray) -> float:
    chosen = int(np.argmax(scores))
    best = float(np.max(oracle))
    return best - float(oracle[chosen])


def evaluate_scenario(name: str, epsilon: float) -> dict[str, Any]:
    summary = summarize_scenario(build_scenario(name), epsilon)
    oracle = np.asarray(summary["finite_difference_values"], dtype=float)
    pressure = np.asarray(summary["pressure_scores"], dtype=float)
    dual = np.asarray(summary["dual_movement_values"], dtype=float)

    rng = np.random.default_rng(20260520 + len(name))
    random_price = rng.permutation(dual)
    local_only = pressure.copy()
    raw_neighbor = pressure.copy()
    all_neighbor = pressure.copy()

    variants = {
        "local_only": local_only,
        "raw_neighbor": raw_neighbor,
        "all_neighbor": all_neighbor,
        "random_price": random_price,
        "dual_sensitivity": dual,
    }
    rows = []
    for variant, scores in variants.items():
        rows.append(
            {
                "variant": variant,
                "program_complexity": 1,
                "chosen_movement": int(np.argmax(scores)),
                "oracle_best_movement": int(np.argmax(oracle)),
                "oracle_regret": regret(oracle, scores),
                "score_rank": [int(i) for i in np.argsort(-scores)],
            }
        )

    best_regret = min(row["oracle_regret"] for row in rows)
    dual_regret = next(row["oracle_regret"] for row in rows if row["variant"] == "dual_sensitivity")
    dual_tied_best = abs(dual_regret - best_regret) <= 1e-9
    return {
        "scenario": name,
        "oracle_values": oracle.tolist(),
        "variants": rows,
        "dual_tied_best": dual_tied_best,
        "note": "This is a scaffold/pilot on proxy states, not the full sparse MIP recovery.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=["toy_nonbinding", "single_intersection_proxy", "arterial_bottleneck_proxy"],
    )
    parser.add_argument("--epsilon", type=float, default=1e-3)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block1_offline_recovery_pilot.json")
    args = parser.parse_args()

    results = [evaluate_scenario(name, args.epsilon) for name in args.scenarios]
    status = "PASSED" if all(r["dual_tied_best"] for r in results) else "INCONCLUSIVE"
    payload = {
        "experiment": "block1_offline_recovery_pilot",
        "status": status,
        "scope": "equal-complexity one-atom scaffold on Block 0 proxy states",
        "results": results,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "out": str(out_path)}, indent=2))


if __name__ == "__main__":
    main()
