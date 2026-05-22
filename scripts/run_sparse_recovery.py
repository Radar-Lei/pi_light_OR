#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from run_dual_sanity import summarize_scenario
from run_sumo_sampled_recovery import scenario_from_sample


ATOM_REGISTRY: dict[str, dict[str, Any]] = {
    "upstream_queue": {
        "name": "upstream_queue",
        "family": "local",
        "requires_neighbor": False,
        "uses_dual": False,
        "is_placebo": False,
        "expression": "q_up(m)",
        "description": "Local upstream movement queue length.",
    },
    "neg_downstream_queue": {
        "name": "neg_downstream_queue",
        "family": "raw_neighbor",
        "requires_neighbor": True,
        "uses_dual": False,
        "is_placebo": False,
        "expression": "-q_down(m)",
        "description": "Negative downstream queue, a raw neighboring-link congestion signal.",
    },
    "downstream_slack": {
        "name": "downstream_slack",
        "family": "capacity",
        "requires_neighbor": True,
        "uses_dual": False,
        "is_placebo": False,
        "expression": "cap_down(m) - q_down(m)",
        "description": "Downstream residual storage/capacity slack for the receiving link.",
    },
    "neg_downstream_fullness": {
        "name": "neg_downstream_fullness",
        "family": "capacity",
        "requires_neighbor": True,
        "uses_dual": False,
        "is_placebo": False,
        "expression": "-q_down(m) / cap_down(m)",
        "description": "Negative normalized downstream occupancy/fullness.",
    },
    "pressure_backpressure": {
        "name": "pressure_backpressure",
        "family": "pressure",
        "requires_neighbor": True,
        "uses_dual": False,
        "is_placebo": False,
        "expression": "w_up(m) - w_down(m)",
        "description": "Ordinary pressure/backpressure score from the LP summary weights.",
    },
    "dual_sensitivity": {
        "name": "dual_sensitivity",
        "family": "dual",
        "requires_neighbor": True,
        "uses_dual": True,
        "is_placebo": False,
        "expression": "lambda_up(m) - lambda_down(m)",
        "description": "Genuine movement-level dual-sensitivity value from summarize_scenario().",
    },
    "random_price": {
        "name": "random_price",
        "family": "placebo",
        "requires_neighbor": True,
        "uses_dual": True,
        "is_placebo": True,
        "expression": "permutation(dual_sensitivity)(m)",
        "description": "Permuted dual-sensitivity placebo preserving the dual-value distribution.",
    },
}


LIBRARIES: dict[str, list[str]] = {
    "local_only": ["upstream_queue"],
    "raw_neighbor": ["upstream_queue", "neg_downstream_queue"],
    "all_neighbor": ["upstream_queue", "neg_downstream_queue", "downstream_slack", "neg_downstream_fullness"],
    "random_price": ["random_price"],
    "dual_sensitivity": ["dual_sensitivity"],
    "dual_plus_raw": ["dual_sensitivity", "upstream_queue", "neg_downstream_queue"],
    "pressure_backpressure": ["pressure_backpressure"],
}


REQUIRED_METADATA_FIELDS = {
    "name",
    "family",
    "requires_neighbor",
    "uses_dual",
    "is_placebo",
    "expression",
    "description",
}


REQUIRED_ATOM_FAMILIES = {"local", "capacity", "raw_neighbor", "pressure", "dual", "placebo"}


def validate_atom_registry() -> None:
    for atom, metadata in ATOM_REGISTRY.items():
        missing = REQUIRED_METADATA_FIELDS - set(metadata)
        if missing:
            raise ValueError(f"Atom {atom} is missing metadata fields: {sorted(missing)}")
        if metadata["name"] != atom:
            raise ValueError(f"Atom metadata name mismatch for {atom}: {metadata['name']}")
    unknown_by_library = {
        library: [atom for atom in atoms if atom not in ATOM_REGISTRY]
        for library, atoms in LIBRARIES.items()
    }
    unknown_by_library = {name: atoms for name, atoms in unknown_by_library.items() if atoms}
    if unknown_by_library:
        raise ValueError(f"Libraries reference unknown atoms: {unknown_by_library}")
    families = {str(metadata["family"]) for metadata in ATOM_REGISTRY.values()}
    missing_families = REQUIRED_ATOM_FAMILIES - families
    if missing_families:
        raise ValueError(f"Atom registry missing required families: {sorted(missing_families)}")


def metadata_for_atoms(atoms: list[str]) -> list[dict[str, Any]]:
    return [dict(ATOM_REGISTRY[atom]) for atom in atoms]


def load_examples(paths: list[Path], tls: str, max_samples: int, max_movements: int, epsilon: float) -> list[dict[str, Any]]:
    examples = []
    remaining = max_samples
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        samples = data["samples"] if remaining <= 0 else data["samples"][:remaining]
        for sample in samples:
            scenario = scenario_from_sample(sample, tls, max_movements)
            if scenario is None:
                continue
            summary = summarize_scenario(scenario, epsilon)
            example = build_example(summary)
            if example is not None:
                example["source"] = str(path)
                examples.append(example)
        if remaining > 0:
            remaining -= len(samples)
    return examples


def build_example(summary: dict[str, Any]) -> dict[str, Any] | None:
    oracle_all = np.asarray(summary["finite_difference_values"], dtype=float)
    feasible = np.isfinite(oracle_all)
    if not np.any(feasible):
        return None

    link_to_idx = {link: idx for idx, link in enumerate(summary["links"])}
    queue = np.asarray(summary["queue"], dtype=float)
    cap = np.asarray(summary["downstream_capacity"], dtype=float)
    movements = summary["movements"]
    original_indices = np.flatnonzero(feasible)

    up_q = []
    down_q = []
    down_slack = []
    down_fullness = []
    for movement in movements:
        up_idx = link_to_idx[movement["up"]]
        down_idx = link_to_idx[movement["down"]]
        up_q.append(queue[up_idx])
        down_q.append(queue[down_idx])
        down_slack.append(cap[down_idx] - queue[down_idx])
        down_fullness.append(queue[down_idx] / max(cap[down_idx], 1.0))

    dual = np.asarray(summary["dual_movement_values"], dtype=float)
    rng = np.random.default_rng(int(summary["objective"]) % 100000 + len(movements))
    random_price = rng.permutation(dual)
    features_all = {
        "upstream_queue": np.asarray(up_q, dtype=float),
        "neg_downstream_queue": -np.asarray(down_q, dtype=float),
        "downstream_slack": np.asarray(down_slack, dtype=float),
        "neg_downstream_fullness": -np.asarray(down_fullness, dtype=float),
        "random_price": random_price,
        "dual_sensitivity": dual,
        "pressure_backpressure": np.asarray(summary["pressure_scores"], dtype=float),
    }

    oracle = oracle_all[feasible]
    features = {name: values[feasible] for name, values in features_all.items()}
    return {
        "scenario": summary["scenario"],
        "source": "",
        "oracle": oracle,
        "oracle_best_local": int(np.argmax(oracle)),
        "oracle_best_movement": int(original_indices[int(np.argmax(oracle))]),
        "original_indices": original_indices,
        "features": features,
        "rank_match_finite_difference": bool(summary["rank_match_finite_difference"]),
        "nonbinding_storage": bool(summary["nonbinding_storage"]),
    }


def normalized_tensor(examples: list[dict[str, Any]], atoms: list[str]) -> list[np.ndarray]:
    scales = {}
    for atom in atoms:
        values = np.concatenate([ex["features"][atom] for ex in examples])
        scale = float(np.max(np.abs(values))) if values.size else 1.0
        scales[atom] = scale if scale > 1e-12 else 1.0
    return [np.vstack([ex["features"][atom] / scales[atom] for atom in atoms]) for ex in examples]


def solve_library(
    examples: list[dict[str, Any]],
    library: str,
    budget: int,
    complexity_penalty: float,
    min_weight: float,
    tie_margin: float,
) -> dict[str, Any]:
    atoms = LIBRARIES[library]
    budget = min(budget, len(atoms))
    matrices = normalized_tensor(examples, atoms)
    n_atoms = len(atoms)
    y_offsets = []
    n_y = 0
    for ex in examples:
        y_offsets.append(n_atoms * 2 + n_y)
        n_y += len(ex["oracle"])
    n_vars = n_atoms * 2 + n_y
    w_offset = 0
    z_offset = n_atoms

    c = np.zeros(n_vars)
    c[z_offset : z_offset + n_atoms] = complexity_penalty
    for ex_idx, ex in enumerate(examples):
        best = float(np.max(ex["oracle"]))
        for m_idx, value in enumerate(ex["oracle"]):
            c[y_offsets[ex_idx] + m_idx] = best - float(value)

    lb = np.zeros(n_vars)
    ub = np.ones(n_vars)
    integrality = np.zeros(n_vars, dtype=int)
    integrality[z_offset : z_offset + n_atoms] = 1
    integrality[n_atoms * 2 :] = 1

    rows = []
    cols = []
    data = []
    lower = []
    upper = []

    def add(coeffs: dict[int, float], lo: float, hi: float) -> None:
        row = len(lower)
        for col, value in coeffs.items():
            rows.append(row)
            cols.append(col)
            data.append(value)
        lower.append(lo)
        upper.append(hi)

    for j in range(n_atoms):
        add({w_offset + j: 1.0, z_offset + j: -1.0}, -math.inf, 0.0)
        add({w_offset + j: 1.0, z_offset + j: -min_weight}, 0.0, math.inf)
    add({z_offset + j: 1.0 for j in range(n_atoms)}, 1.0, float(budget))

    big_m = 10.0 * budget + 1.0
    for ex_idx, ex in enumerate(examples):
        n_moves = len(ex["oracle"])
        y0 = y_offsets[ex_idx]
        add({y0 + m: 1.0 for m in range(n_moves)}, 1.0, 1.0)
        mat = matrices[ex_idx]
        for m in range(n_moves):
            for k in range(n_moves):
                if m == k:
                    continue
                coeffs = {w_offset + j: float(mat[j, m] - mat[j, k]) for j in range(n_atoms)}
                coeffs[y0 + m] = -big_m
                add(coeffs, -big_m, math.inf)

    a = coo_matrix((data, (rows, cols)), shape=(len(lower), n_vars)).tocsr()
    start = time.perf_counter()
    res = milp(
        c,
        integrality=integrality,
        bounds=Bounds(lb, ub),
        constraints=LinearConstraint(a, np.asarray(lower), np.asarray(upper)),
        options={"time_limit": 60.0},
    )
    solve_time = time.perf_counter() - start
    if not res.success or res.x is None:
        return {
            "library": library,
            "budget": budget,
            "status": "FAILED",
            "message": res.message,
            "solve_time_sec": solve_time,
        }

    weights = np.asarray(res.x[w_offset : w_offset + n_atoms], dtype=float)
    selected = [atoms[j] for j, weight in enumerate(weights) if weight > 1e-6]
    rows_out = []
    total_regret = 0.0
    agreement = 0
    for ex_idx, ex in enumerate(examples):
        scores = weights @ matrices[ex_idx]
        chosen_local = int(np.argmax(scores))
        chosen_movement = int(ex["original_indices"][chosen_local])
        best = float(np.max(ex["oracle"]))
        regret = best - float(ex["oracle"][chosen_local])
        total_regret += regret
        agreement += int(chosen_local == ex["oracle_best_local"])
        rows_out.append(
            {
                "scenario": ex["scenario"],
                "source": ex["source"],
                "chosen_movement": chosen_movement,
                "oracle_best_movement": ex["oracle_best_movement"],
                "oracle_regret": regret,
            }
        )

    return {
        "library": library,
        "budget": budget,
        "status": "PASSED",
        "objective": float(res.fun),
        "solve_time_sec": solve_time,
        "selected_atoms": selected,
        "selected_atom_metadata": metadata_for_atoms(selected),
        "weights": {atom: float(weights[j]) for j, atom in enumerate(atoms)},
        "program_complexity": len(selected),
        "realized_total_regret": total_regret,
        "realized_mean_regret": total_regret / len(examples) if examples else 0.0,
        "action_agreement": agreement / len(examples) if examples else 0.0,
        "results": rows_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", action="append", default=[])
    parser.add_argument("--tls", default="C3")
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument("--max-movements", type=int, default=12)
    parser.add_argument("--epsilon", type=float, default=1e-3)
    parser.add_argument("--budgets", nargs="+", type=int, default=[1, 2])
    parser.add_argument("--complexity-penalty", type=float, default=1e-4)
    parser.add_argument("--min-weight", type=float, default=0.1)
    parser.add_argument("--tie-margin", type=float, default=1e-6)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block1_sparse_recovery.json")
    args = parser.parse_args()

    validate_atom_registry()
    state_paths = [Path(p) for p in args.states] or [Path("experiments/dual_sensitivity/targeted_bottleneck_states.json")]
    examples = load_examples(state_paths, args.tls, args.max_samples, args.max_movements, args.epsilon)
    example_feature_atoms = set(examples[0]["features"]) if examples else set()
    missing_features = sorted(set(ATOM_REGISTRY) - example_feature_atoms)
    if missing_features:
        raise ValueError(f"Atom registry contains atoms without computed features: {missing_features}")

    runs = []
    seen: set[tuple[str, int]] = set()
    for budget in args.budgets:
        for library, atoms in LIBRARIES.items():
            effective_budget = min(budget, len(atoms))
            key = (library, effective_budget)
            if key in seen:
                continue
            seen.add(key)
            runs.append(
                solve_library(
                    examples,
                    library,
                    effective_budget,
                    args.complexity_penalty,
                    args.min_weight,
                    args.tie_margin,
                )
            )

    by_key = {(r["library"], r["budget"]): r for r in runs if r["status"] == "PASSED"}
    best_by_library: dict[str, dict[str, Any]] = {}
    for r in runs:
        if r["status"] != "PASSED":
            continue
        current = best_by_library.get(r["library"])
        if current is None or (
            float(r["realized_total_regret"]), int(r["program_complexity"])
        ) < (
            float(current["realized_total_regret"]), int(current["program_complexity"])
        ):
            best_by_library[r["library"]] = r
    dual_b1 = by_key.get(("dual_sensitivity", 1))
    raw_b1 = [by_key.get((name, 1)) for name in ["local_only", "raw_neighbor", "all_neighbor", "random_price"]]
    gate_dual_budget1_beats_raw = bool(
        dual_b1
        and all(r and dual_b1["realized_total_regret"] < r["realized_total_regret"] - 1e-9 for r in raw_b1)
    )
    gate_dual_lower_or_equal_complexity = False
    if dual_b1:
        dual_regret = float(dual_b1["realized_total_regret"])
        for raw_name in ["raw_neighbor", "all_neighbor"]:
            for budget in args.budgets:
                raw_run = by_key.get((raw_name, budget))
                if raw_run and float(raw_run["realized_total_regret"]) <= dual_regret + 1e-9:
                    gate_dual_lower_or_equal_complexity = int(dual_b1["program_complexity"]) <= int(raw_run["program_complexity"])
                    break
    status = "PASSED" if gate_dual_budget1_beats_raw and dual_b1 and dual_b1["realized_total_regret"] <= 1e-9 else "INCONCLUSIVE"
    compact_summary = [
        {
            "library": r["library"],
            "budget": r["budget"],
            "status": r["status"],
            "selected_atoms": r.get("selected_atoms", []),
            "program_complexity": r.get("program_complexity", 0),
            "realized_total_regret": r.get("realized_total_regret"),
            "realized_mean_regret": r.get("realized_mean_regret"),
            "action_agreement": r.get("action_agreement"),
            "solve_time_sec": r.get("solve_time_sec"),
        }
        for r in runs
    ]
    payload = {
        "experiment": "block1_sparse_recovery",
        "status": status,
        "input_states": [str(p) for p in state_paths],
        "tls": args.tls,
        "num_examples": len(examples),
        "budgets": args.budgets,
        "atom_registry": ATOM_REGISTRY,
        "gate_required_families_present": REQUIRED_ATOM_FAMILIES <= {str(metadata["family"]) for metadata in ATOM_REGISTRY.values()},
        "gate_dual_budget1_beats_raw": gate_dual_budget1_beats_raw,
        "gate_dual_lower_or_equal_complexity": gate_dual_lower_or_equal_complexity,
        "summary": compact_summary,
        "best_by_library": [
            {
                "library": r["library"],
                "budget": r["budget"],
                "selected_atoms": r["selected_atoms"],
                "program_complexity": r["program_complexity"],
                "realized_total_regret": r["realized_total_regret"],
                "realized_mean_regret": r["realized_mean_regret"],
                "action_agreement": r["action_agreement"],
                "solve_time_sec": r["solve_time_sec"],
            }
            for r in best_by_library.values()
        ],
        "runs": runs,
        "note": "SciPy/HiGHS MILP backend; AMPL backend can reuse the same atom/regret matrices if amplpy is installed. Pass/fail gates use external deterministic realized regret, not optimistic internal tie choices.",
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "out": str(out_path), "num_examples": len(examples)}, indent=2))


if __name__ == "__main__":
    main()
