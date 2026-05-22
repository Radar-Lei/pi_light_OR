#!/usr/bin/env python3
"""Block 0 sanity checks for dual-sensitivity-guided signal control.

This script uses a continuous one-step store-and-forward LP relaxation.
It validates whether dual/reduced-cost movement values match finite
objective perturbations and whether the nonbinding-storage special case
recovers a pressure-like ranking.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linprog


@dataclass(frozen=True)
class Scenario:
    name: str
    links: list[str]
    movements: list[tuple[int, int]]
    queue: np.ndarray
    downstream_capacity: np.ndarray
    demand: np.ndarray
    service_capacity: np.ndarray
    green_budget: float
    queue_weight: np.ndarray
    storage_penalty: np.ndarray


def build_scenario(name: str) -> Scenario:
    if name == "toy_nonbinding":
        links = ["up_a", "up_b", "down_a", "down_b"]
        movements = [(0, 2), (1, 3)]
        return Scenario(
            name=name,
            links=links,
            movements=movements,
            queue=np.array([18.0, 9.0, 4.0, 3.0]),
            downstream_capacity=np.array([80.0, 80.0, 80.0, 80.0]),
            demand=np.zeros(4),
            service_capacity=np.array([10.0, 10.0]),
            green_budget=10.0,
            queue_weight=np.array([18.0, 9.0, 4.0, 3.0]),
            storage_penalty=np.zeros(4),
        )
    if name == "toy_storage_binding":
        links = ["up_a", "up_b", "down_a", "down_b"]
        movements = [(0, 2), (1, 3)]
        return Scenario(
            name=name,
            links=links,
            movements=movements,
            queue=np.array([18.0, 9.0, 80.0, 3.0]),
            downstream_capacity=np.array([80.0, 80.0, 80.0, 80.0]),
            demand=np.zeros(4),
            service_capacity=np.array([10.0, 10.0]),
            green_budget=10.0,
            queue_weight=np.array([18.0, 9.0, 80.0, 3.0]),
            storage_penalty=np.array([0.0, 0.0, 25.0, 0.0]),
        )
    if name == "single_intersection_proxy":
        links = ["N_in", "S_in", "E_in", "W_in", "N_out", "S_out", "E_out", "W_out"]
        movements = [(0, 5), (1, 4), (2, 7), (3, 6)]
        return Scenario(
            name=name,
            links=links,
            movements=movements,
            queue=np.array([20.0, 16.0, 8.0, 7.0, 5.0, 6.0, 4.0, 4.0]),
            downstream_capacity=np.array([90.0] * 8),
            demand=np.zeros(8),
            service_capacity=np.array([12.0, 12.0, 12.0, 12.0]),
            green_budget=18.0,
            queue_weight=np.array([20.0, 16.0, 8.0, 7.0, 5.0, 6.0, 4.0, 4.0]),
            storage_penalty=np.zeros(8),
        )
    if name == "arterial_bottleneck_proxy":
        links = ["C1C2", "C2C3", "C3C4", "C4C5", "C2_side", "C3_side", "C5_out"]
        movements = [(0, 1), (1, 2), (2, 3), (3, 6), (4, 1), (5, 2)]
        return Scenario(
            name=name,
            links=links,
            movements=movements,
            queue=np.array([35.0, 28.0, 18.0, 12.0, 11.0, 10.0, 80.0]),
            downstream_capacity=np.array([90.0, 90.0, 90.0, 90.0, 70.0, 70.0, 80.0]),
            demand=np.zeros(7),
            service_capacity=np.array([10.0, 10.0, 10.0, 10.0, 7.0, 7.0]),
            green_budget=24.0,
            queue_weight=np.array([35.0, 28.0, 18.0, 12.0, 11.0, 10.0, 80.0]),
            storage_penalty=np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 30.0]),
        )
    raise ValueError(f"Unknown scenario: {name}")


def solve_relaxation(s: Scenario, service_bonus: np.ndarray | None = None) -> dict[str, Any]:
    n_links = len(s.links)
    n_movements = len(s.movements)
    n_vars = n_links + n_movements + n_links
    x_slice = slice(0, n_links)
    u_slice = slice(n_links, n_links + n_movements)
    z_slice = slice(n_links + n_movements, n_vars)

    c = np.zeros(n_vars)
    c[x_slice] = s.queue_weight
    c[z_slice] = s.storage_penalty
    if service_bonus is not None:
        c[u_slice] -= service_bonus

    a_eq = []
    b_eq = []
    for link_idx in range(n_links):
        row = np.zeros(n_vars)
        row[link_idx] = 1.0
        rhs = s.queue[link_idx] + s.demand[link_idx]
        for m_idx, (up, down) in enumerate(s.movements):
            if up == link_idx:
                row[n_links + m_idx] += 1.0
            if down == link_idx:
                row[n_links + m_idx] -= 1.0
        a_eq.append(row)
        b_eq.append(rhs)

    a_ub = []
    b_ub = []
    row = np.zeros(n_vars)
    row[u_slice] = 1.0
    a_ub.append(row)
    b_ub.append(s.green_budget)

    for link_idx in range(n_links):
        row = np.zeros(n_vars)
        row[link_idx] = 1.0
        row[z_slice.start + link_idx] = -1.0
        a_ub.append(row)
        b_ub.append(s.downstream_capacity[link_idx])

    bounds: list[tuple[float, float | None]] = []
    bounds.extend((0.0, None) for _ in range(n_links))
    bounds.extend((0.0, float(cap)) for cap in s.service_capacity)
    bounds.extend((0.0, None) for _ in range(n_links))

    res = linprog(
        c,
        A_ub=np.array(a_ub),
        b_ub=np.array(b_ub),
        A_eq=np.array(a_eq),
        b_eq=np.array(b_eq),
        bounds=bounds,
        method="highs",
    )
    if not res.success:
        raise RuntimeError(f"LP failed for {s.name}: {res.message}")

    x = res.x[x_slice]
    u = res.x[u_slice]
    z = res.x[z_slice]
    equality_duals = np.asarray(res.eqlin.marginals)
    upper_duals = np.asarray(res.ineqlin.marginals)
    lower_marginals = np.asarray(res.lower.marginals)
    upper_marginals = np.asarray(res.upper.marginals)

    movement_values = []
    pressure_scores = []
    for m_idx, (up, down) in enumerate(s.movements):
        value = equality_duals[up] - equality_duals[down]
        movement_values.append(value)
        pressure_scores.append(s.queue_weight[up] - s.queue_weight[down])

    return {
        "objective": float(res.fun),
        "x_next": x.tolist(),
        "service": u.tolist(),
        "overflow": z.tolist(),
        "queue_duals": equality_duals.tolist(),
        "green_budget_dual": float(upper_duals[0]),
        "storage_duals": upper_duals[1:].tolist(),
        "movement_values": movement_values,
        "pressure_scores": pressure_scores,
        "lower_marginals": lower_marginals.tolist(),
        "upper_marginals": upper_marginals.tolist(),
    }


def forced_service_objective(s: Scenario, movement_idx: int, eps: float) -> float:
    n_links = len(s.links)
    n_movements = len(s.movements)
    n_vars = n_links + n_movements + n_links
    x_slice = slice(0, n_links)
    u_slice = slice(n_links, n_links + n_movements)
    z_slice = slice(n_links + n_movements, n_vars)

    c = np.zeros(n_vars)
    c[x_slice] = s.queue_weight
    c[z_slice] = s.storage_penalty

    a_eq = []
    b_eq = []
    for link_idx in range(n_links):
        row = np.zeros(n_vars)
        row[link_idx] = 1.0
        rhs = s.queue[link_idx] + s.demand[link_idx]
        for m_idx, (up, down) in enumerate(s.movements):
            if up == link_idx:
                row[n_links + m_idx] += 1.0
            if down == link_idx:
                row[n_links + m_idx] -= 1.0
        a_eq.append(row)
        b_eq.append(rhs)

    for m_idx in range(n_movements):
        row = np.zeros(n_vars)
        row[n_links + m_idx] = 1.0
        a_eq.append(row)
        b_eq.append(eps if m_idx == movement_idx else 0.0)

    a_ub = []
    b_ub = []
    row = np.zeros(n_vars)
    row[u_slice] = 1.0
    a_ub.append(row)
    b_ub.append(s.green_budget)

    for link_idx in range(n_links):
        row = np.zeros(n_vars)
        row[link_idx] = 1.0
        row[z_slice.start + link_idx] = -1.0
        a_ub.append(row)
        b_ub.append(s.downstream_capacity[link_idx])

    bounds: list[tuple[float, float | None]] = []
    bounds.extend((0.0, None) for _ in range(n_links))
    bounds.extend((0.0, float(cap)) for cap in s.service_capacity)
    bounds.extend((0.0, None) for _ in range(n_links))

    res = linprog(
        c,
        A_ub=np.array(a_ub),
        b_ub=np.array(b_ub),
        A_eq=np.array(a_eq),
        b_eq=np.array(b_eq),
        bounds=bounds,
        method="highs",
    )
    if not res.success:
        return math.inf
    return float(res.fun)


def no_service_scenario(s: Scenario) -> Scenario:
    return Scenario(
        name=s.name,
        links=s.links,
        movements=s.movements,
        queue=s.queue,
        downstream_capacity=s.downstream_capacity,
        demand=s.demand,
        service_capacity=np.zeros(len(s.movements)),
        green_budget=0.0,
        queue_weight=s.queue_weight,
        storage_penalty=s.storage_penalty,
    )


def finite_difference_service_values(s: Scenario, eps: float) -> list[float]:
    no_service = no_service_scenario(s)
    base = solve_relaxation(no_service)["objective"]
    values = []
    for m_idx in range(len(s.movements)):
        obj = forced_service_objective(s, m_idx, eps)
        values.append((base - obj) / eps if math.isfinite(obj) else -math.inf)
    return values


def ranking(values: list[float]) -> list[int]:
    return sorted(range(len(values)), key=lambda i: values[i], reverse=True)


def summarize_scenario(s: Scenario, eps: float) -> dict[str, Any]:
    solved = solve_relaxation(no_service_scenario(s))
    fd_values = finite_difference_service_values(s, eps)
    dual_values = solved["movement_values"]
    pressure_scores = solved["pressure_scores"]

    dual_rank = ranking(dual_values)
    fd_rank = ranking(fd_values)
    pressure_rank = ranking(pressure_scores)
    rank_match_fd = dual_rank == fd_rank
    rank_match_pressure = dual_rank == pressure_rank

    if len(dual_values) > 1 and np.std(dual_values) > 1e-12 and np.std(fd_values) > 1e-12:
        corr = float(np.corrcoef(dual_values, fd_values)[0, 1])
    else:
        corr = 1.0 if rank_match_fd else 0.0

    nonbinding_storage = all(abs(v) < 1e-8 for v in solved["storage_duals"])
    pressure_special_case_pass = (not nonbinding_storage) or rank_match_pressure

    return {
        "scenario": s.name,
        "links": s.links,
        "movements": [
            {"up": s.links[up], "down": s.links[down]} for up, down in s.movements
        ],
        "queue": s.queue.tolist(),
        "downstream_capacity": s.downstream_capacity.tolist(),
        "objective": solved["objective"],
        "service": solved["service"],
        "queue_duals": solved["queue_duals"],
        "storage_duals": solved["storage_duals"],
        "green_budget_dual": solved["green_budget_dual"],
        "dual_movement_values": dual_values,
        "finite_difference_values": fd_values,
        "pressure_scores": pressure_scores,
        "dual_rank": dual_rank,
        "finite_difference_rank": fd_rank,
        "pressure_rank": pressure_rank,
        "dual_fd_correlation": corr,
        "rank_match_finite_difference": rank_match_fd,
        "nonbinding_storage": nonbinding_storage,
        "pressure_special_case_pass": pressure_special_case_pass,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=[
            "toy_nonbinding",
            "toy_storage_binding",
            "single_intersection_proxy",
            "arterial_bottleneck_proxy",
        ],
    )
    parser.add_argument("--epsilon", type=float, default=1e-3)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block0_dual_sanity.json")
    args = parser.parse_args()

    results = [summarize_scenario(build_scenario(name), args.epsilon) for name in args.scenarios]
    gate_a_pass = all(
        r["rank_match_finite_difference"] and r["pressure_special_case_pass"] for r in results
    )
    payload = {
        "experiment": "block0_dual_sanity",
        "status": "PASSED" if gate_a_pass else "FAILED",
        "epsilon": args.epsilon,
        "criteria": {
            "dual_rank_matches_finite_difference_rank": True,
            "pressure_rank_matches_dual_rank_when_storage_nonbinding": True,
        },
        "results": results,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": str(out_path)}, indent=2))
    if not gate_a_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
