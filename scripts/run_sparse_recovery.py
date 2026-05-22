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
    "full_symbolic": list(ATOM_REGISTRY),
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


def select_library_names(requested_libraries: list[str] | None) -> list[str]:
    if not requested_libraries:
        return list(LIBRARIES)
    unknown = [name for name in requested_libraries if name not in LIBRARIES]
    if unknown:
        raise ValueError(f"Unknown libraries: {unknown}. Available libraries: {sorted(LIBRARIES)}")
    return requested_libraries


def validate_atom_families(requested_families: list[str] | None) -> set[str] | None:
    if not requested_families:
        return None
    known_families = {str(metadata["family"]) for metadata in ATOM_REGISTRY.values()}
    unknown = sorted(set(requested_families) - known_families)
    if unknown:
        raise ValueError(f"Unknown atom families: {unknown}. Available families: {sorted(known_families)}")
    return set(requested_families)


def atoms_for_library(library: str, allowed_families: set[str] | None = None) -> list[str]:
    atoms = LIBRARIES[library]
    if allowed_families is None:
        return list(atoms)
    return [atom for atom in atoms if str(ATOM_REGISTRY[atom]["family"]) in allowed_families]


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


def atom_indices_by_metadata(atoms: list[str]) -> dict[str, list[int]]:
    indices: dict[str, list[int]] = {
        "neighbor": [],
        "dual": [],
        "placebo": [],
        "pressure": [],
        "raw_neighbor": [],
        "capacity": [],
    }
    for j, atom in enumerate(atoms):
        metadata = ATOM_REGISTRY[atom]
        family = str(metadata["family"])
        if bool(metadata["requires_neighbor"]):
            indices["neighbor"].append(j)
        if bool(metadata["uses_dual"]) and not bool(metadata["is_placebo"]):
            indices["dual"].append(j)
        if bool(metadata["is_placebo"]):
            indices["placebo"].append(j)
        if family in indices:
            indices[family].append(j)
    return indices


def count_selected(indices: list[int], selected_mask: np.ndarray) -> int:
    return int(sum(bool(selected_mask[j]) for j in indices))


def render_rule_text(library: str, max_atoms: int, selected_atoms: list[str], weights: np.ndarray, atoms: list[str]) -> str:
    if not selected_atoms:
        expression = "0.0"
    else:
        terms = []
        for atom in selected_atoms:
            weight = float(weights[atoms.index(atom)])
            atom_expr = str(ATOM_REGISTRY[atom]["expression"])
            terms.append(f"{weight:.6g} * ({atom_expr})")
        expression = " + ".join(terms)
    return (
        f"library={library}; max_atoms={max_atoms}; "
        "choose movement m maximizing normalized score(m); "
        f"score(m) = {expression}"
    )


def solve_library(
    examples: list[dict[str, Any]],
    library: str,
    atoms: list[str],
    budget: int,
    complexity_penalty: float,
    neighbor_penalty: float,
    dual_penalty: float,
    placebo_penalty: float,
    max_neighbor_atoms: int | None,
    max_dual_atoms: int | None,
    max_placebo_atoms: int | None,
    objective_mode: str,
    time_limit_sec: float,
    min_weight: float,
    tie_margin: float,
) -> dict[str, Any]:
    budget = min(budget, len(atoms))
    category_indices = atom_indices_by_metadata(atoms)
    effective_max_neighbor = budget if max_neighbor_atoms is None else min(max_neighbor_atoms, budget)
    effective_max_dual = budget if max_dual_atoms is None else min(max_dual_atoms, budget)
    effective_max_placebo = budget if max_placebo_atoms is None else min(max_placebo_atoms, budget)
    base_payload = {
        "library": library,
        "budget": budget,
        "max_atoms": budget,
        "max_neighbor_atoms": effective_max_neighbor,
        "max_dual_atoms": effective_max_dual,
        "max_placebo_atoms": effective_max_placebo,
        "objective_mode": objective_mode,
    }

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
    for j in category_indices["neighbor"]:
        c[z_offset + j] += neighbor_penalty
    for j in category_indices["dual"]:
        c[z_offset + j] += dual_penalty
    for j in category_indices["placebo"]:
        c[z_offset + j] += placebo_penalty
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
    if category_indices["neighbor"]:
        add({z_offset + j: 1.0 for j in category_indices["neighbor"]}, 0.0, float(effective_max_neighbor))
    if category_indices["dual"]:
        add({z_offset + j: 1.0 for j in category_indices["dual"]}, 0.0, float(effective_max_dual))
    if category_indices["placebo"]:
        add({z_offset + j: 1.0 for j in category_indices["placebo"]}, 0.0, float(effective_max_placebo))

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
        options={"time_limit": float(time_limit_sec)},
    )
    solve_time = time.perf_counter() - start
    if not res.success or res.x is None:
        return {
            **base_payload,
            "status": "FAILED",
            "solver_status": int(res.status),
            "message": res.message,
            "solve_time_sec": solve_time,
        }

    weights = np.asarray(res.x[w_offset : w_offset + n_atoms], dtype=float)
    selected_mask = weights > 1e-6
    selected = [atoms[j] for j, is_selected in enumerate(selected_mask) if is_selected]
    neighbor_count = count_selected(category_indices["neighbor"], selected_mask)
    dual_count = count_selected(category_indices["dual"], selected_mask)
    placebo_count = count_selected(category_indices["placebo"], selected_mask)
    pressure_count = count_selected(category_indices["pressure"], selected_mask)
    raw_neighbor_count = count_selected(category_indices["raw_neighbor"], selected_mask)
    capacity_count = count_selected(category_indices["capacity"], selected_mask)
    penalty_breakdown = {
        "complexity_penalty": float(complexity_penalty * len(selected)),
        "neighbor_penalty": float(neighbor_penalty * neighbor_count),
        "dual_penalty": float(dual_penalty * dual_count),
        "placebo_penalty": float(placebo_penalty * placebo_count),
    }
    penalty_breakdown["total_penalty"] = float(sum(penalty_breakdown.values()))
    rule_text = render_rule_text(library, budget, selected, weights, atoms)

    rows_out = []
    total_regret = 0.0
    max_regret = 0.0
    agreement = 0
    for ex_idx, ex in enumerate(examples):
        scores = weights @ matrices[ex_idx]
        chosen_local = int(np.argmax(scores))
        chosen_movement = int(ex["original_indices"][chosen_local])
        best = float(np.max(ex["oracle"]))
        oracle_value_chosen = float(ex["oracle"][chosen_local])
        regret = best - oracle_value_chosen
        max_regret = max(max_regret, regret)
        total_regret += regret
        matched = chosen_local == ex["oracle_best_local"]
        agreement += int(matched)
        rows_out.append(
            {
                "scenario": ex["scenario"],
                "source": ex["source"],
                "chosen_movement": chosen_movement,
                "oracle_best_movement": ex["oracle_best_movement"],
                "oracle_value_chosen": oracle_value_chosen,
                "oracle_value_best": best,
                "oracle_regret": regret,
                "action_agreement": bool(matched),
                "score_chosen": float(scores[chosen_local]),
                "score_oracle_best": float(scores[int(ex["oracle_best_local"])]),
            }
        )

    return {
        **base_payload,
        "status": "SOLVED",
        "solver_status": int(res.status),
        "objective": float(res.fun),
        "objective_value_with_penalties": float(res.fun),
        "solve_time_sec": solve_time,
        "selected_atoms": selected,
        "selected_atom_metadata": metadata_for_atoms(selected),
        "weights": {atom: float(weights[j]) for j, atom in enumerate(atoms)},
        "program_complexity": len(selected),
        "neighbor_atom_count": neighbor_count,
        "dual_atom_count": dual_count,
        "placebo_atom_count": placebo_count,
        "pressure_atom_count": pressure_count,
        "raw_neighbor_atom_count": raw_neighbor_count,
        "capacity_atom_count": capacity_count,
        "realized_total_regret": total_regret,
        "realized_mean_regret": total_regret / len(examples) if examples else 0.0,
        "max_regret": max_regret,
        "action_agreement": agreement / len(examples) if examples else 0.0,
        "penalty_breakdown": penalty_breakdown,
        "rule_text": rule_text,
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
    parser.add_argument("--max-atoms", type=int, default=0)
    parser.add_argument("--libraries", nargs="+", default=None)
    parser.add_argument("--atom-families", nargs="+", default=None)
    parser.add_argument("--complexity-penalty", type=float, default=1e-4)
    parser.add_argument("--neighbor-penalty", type=float, default=0.0)
    parser.add_argument("--dual-penalty", type=float, default=0.0)
    parser.add_argument("--placebo-penalty", type=float, default=0.0)
    parser.add_argument("--max-neighbor-atoms", type=int, default=None)
    parser.add_argument("--max-dual-atoms", type=int, default=None)
    parser.add_argument("--max-placebo-atoms", type=int, default=None)
    parser.add_argument("--time-limit-sec", type=float, default=60.0)
    parser.add_argument("--objective", choices=["oracle_regret", "value_gap"], default="oracle_regret")
    parser.add_argument("--min-weight", type=float, default=0.1)
    parser.add_argument("--tie-margin", type=float, default=1e-6)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block1_sparse_recovery.json")
    args = parser.parse_args()

    validate_atom_registry()
    library_names = select_library_names(args.libraries)
    allowed_families = validate_atom_families(args.atom_families)
    budgets = [args.max_atoms] if args.max_atoms > 0 else args.budgets
    if any(budget <= 0 for budget in budgets):
        raise ValueError(f"Atom budgets must be positive: {budgets}")
    category_budgets = [args.max_neighbor_atoms, args.max_dual_atoms, args.max_placebo_atoms]
    if any(value is not None and value < 0 for value in category_budgets):
        raise ValueError("Category atom budgets must be nonnegative when supplied")
    penalties = [args.complexity_penalty, args.neighbor_penalty, args.dual_penalty, args.placebo_penalty]
    if any(value < 0.0 for value in penalties):
        raise ValueError("Atom penalties must be nonnegative")
    if args.time_limit_sec <= 0.0:
        raise ValueError("--time-limit-sec must be positive")
    if args.min_weight < 0.0:
        raise ValueError("--min-weight must be nonnegative")
    if args.tie_margin < 0.0:
        raise ValueError("--tie-margin must be nonnegative")
    selected_library_atoms = {
        atom for library in library_names for atom in atoms_for_library(library, allowed_families)
    }
    if not selected_library_atoms:
        raise ValueError(
            f"No atoms selected by libraries {library_names} and families "
            f"{sorted(allowed_families) if allowed_families is not None else 'all'}"
        )

    state_paths = [Path(p) for p in args.states] or [Path("experiments/dual_sensitivity/targeted_bottleneck_states.json")]
    examples = load_examples(state_paths, args.tls, args.max_samples, args.max_movements, args.epsilon)
    example_feature_atoms = set(examples[0]["features"]) if examples else set()
    missing_features = sorted(set(ATOM_REGISTRY) - example_feature_atoms)
    if missing_features:
        raise ValueError(f"Atom registry contains atoms without computed features: {missing_features}")

    runs = []
    seen: set[tuple[str, int, tuple[str, ...]]] = set()
    for budget in budgets:
        for library in library_names:
            atoms = atoms_for_library(library, allowed_families)
            if not atoms:
                continue
            effective_budget = min(budget, len(atoms))
            key = (library, effective_budget, tuple(atoms))
            if key in seen:
                continue
            seen.add(key)
            runs.append(
                solve_library(
                    examples,
                    library,
                    atoms,
                    effective_budget,
                    args.complexity_penalty,
                    args.neighbor_penalty,
                    args.dual_penalty,
                    args.placebo_penalty,
                    args.max_neighbor_atoms,
                    args.max_dual_atoms,
                    args.max_placebo_atoms,
                    args.objective,
                    args.time_limit_sec,
                    args.min_weight,
                    args.tie_margin,
                )
            )

    by_key = {(r["library"], r["budget"]): r for r in runs if r["status"] == "SOLVED"}
    best_by_library: dict[str, dict[str, Any]] = {}
    for r in runs:
        if r["status"] != "SOLVED":
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
            "max_atoms": r.get("max_atoms", r["budget"]),
            "status": r["status"],
            "selected_atoms": r.get("selected_atoms", []),
            "program_complexity": r.get("program_complexity", 0),
            "neighbor_atom_count": r.get("neighbor_atom_count", 0),
            "dual_atom_count": r.get("dual_atom_count", 0),
            "placebo_atom_count": r.get("placebo_atom_count", 0),
            "realized_total_regret": r.get("realized_total_regret"),
            "realized_mean_regret": r.get("realized_mean_regret"),
            "max_regret": r.get("max_regret"),
            "action_agreement": r.get("action_agreement"),
            "solve_time_sec": r.get("solve_time_sec"),
            "rule_text": r.get("rule_text"),
        }
        for r in runs
    ]
    solved_runs = [r for r in runs if r["status"] == "SOLVED"]
    gate_k_gt_one_attempted = any(int(r.get("max_atoms", r.get("budget", 0))) > 1 for r in runs)
    gate_k_gt_one_solved = any(int(r.get("max_atoms", r.get("budget", 0))) > 1 for r in solved_runs)
    gate_regret_first_objective = args.objective in {"oracle_regret", "value_gap"}
    status = "PASSED" if gate_k_gt_one_solved and gate_regret_first_objective else "INCONCLUSIVE"
    payload = {
        "experiment": "block2_sparse_recovery",
        "status": status,
        "input_states": [str(p) for p in state_paths],
        "tls": args.tls,
        "num_examples": len(examples),
        "objective_mode": args.objective,
        "budgets": budgets,
        "max_atoms": budgets[0] if len(budgets) == 1 else None,
        "max_neighbor_atoms": args.max_neighbor_atoms,
        "max_dual_atoms": args.max_dual_atoms,
        "max_placebo_atoms": args.max_placebo_atoms,
        "penalties": {
            "complexity_penalty": args.complexity_penalty,
            "neighbor_penalty": args.neighbor_penalty,
            "dual_penalty": args.dual_penalty,
            "placebo_penalty": args.placebo_penalty,
        },
        "libraries": library_names,
        "atom_families": sorted(allowed_families) if allowed_families is not None else "all",
        "atom_registry": ATOM_REGISTRY,
        "gate_required_families_present": REQUIRED_ATOM_FAMILIES <= {str(metadata["family"]) for metadata in ATOM_REGISTRY.values()},
        "gate_regret_first_objective": gate_regret_first_objective,
        "gate_k_gt_one_attempted": gate_k_gt_one_attempted,
        "gate_k_gt_one_solved": gate_k_gt_one_solved,
        "gate_dual_budget1_beats_raw": gate_dual_budget1_beats_raw,
        "gate_dual_lower_or_equal_complexity": gate_dual_lower_or_equal_complexity,
        "summary": compact_summary,
        "best_by_library": [
            {
                "library": r["library"],
                "budget": r["budget"],
                "max_atoms": r["max_atoms"],
                "selected_atoms": r["selected_atoms"],
                "program_complexity": r["program_complexity"],
                "neighbor_atom_count": r["neighbor_atom_count"],
                "dual_atom_count": r["dual_atom_count"],
                "placebo_atom_count": r["placebo_atom_count"],
                "realized_total_regret": r["realized_total_regret"],
                "realized_mean_regret": r["realized_mean_regret"],
                "max_regret": r["max_regret"],
                "action_agreement": r["action_agreement"],
                "solve_time_sec": r["solve_time_sec"],
                "rule_text": r["rule_text"],
            }
            for r in best_by_library.values()
        ],
        "runs": runs,
        "note": "SciPy/HiGHS MILP backend; Phase 2 artifacts are finite-dictionary and sample-relative. Action agreement is diagnostic only; dual-vs-pressure empirical claim routing is deferred to Phase 3.",
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "out": str(out_path), "num_examples": len(examples)}, indent=2))


if __name__ == "__main__":
    main()
