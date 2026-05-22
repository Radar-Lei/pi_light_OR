#!/usr/bin/env python3
"""Run the Phase 3 static dual-vs-pressure kill gate.

This runner is a thin aggregation layer over the Phase 2 sparse-recovery
core. It groups sampled states by static regime, converts valid examples with
existing SUMO-state and LP-summary functions, solves existing sparse libraries,
and writes static/sample-relative route evidence. It does not run closed-loop
SUMO experiments and does not claim travel-time or throughput superiority.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from run_sparse_recovery import (
    ATOM_REGISTRY,
    LIBRARIES,
    atoms_for_library,
    build_example,
    scenario_from_sample,
    select_library_names,
    solve_library,
    summarize_scenario,
    validate_atom_registry,
)

REQUIRED_SAMPLE_FIELDS = {"time", "queues", "vehicle_counts", "capacities", "tls_movements"}
PRIMARY_DUAL_LIBRARY = "dual_sensitivity"
PRIMARY_PRESSURE_LIBRARY = "pressure_backpressure"
DEFAULT_LIBRARIES = [PRIMARY_DUAL_LIBRARY, PRIMARY_PRESSURE_LIBRARY]
ROUTE_DECISIONS = {"dual-improves-pressure", "pressure-equivalent", "diagnostic"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", action="append", default=[])
    parser.add_argument("--tls", default="C3")
    parser.add_argument("--max-samples", type=int, default=0)
    parser.add_argument("--max-movements", type=int, default=12)
    parser.add_argument("--epsilon", type=float, default=1e-3)
    parser.add_argument("--budgets", nargs="+", type=int, default=[1])
    parser.add_argument("--libraries", nargs="+", default=DEFAULT_LIBRARIES)
    parser.add_argument("--default-regime", default=None)
    parser.add_argument("--min-regime-count", type=int, default=30)
    parser.add_argument("--target-total-states", type=int, default=1000)
    parser.add_argument("--dual-win-threshold", type=float, default=0.55)
    parser.add_argument("--regret-improvement-threshold", type=float, default=0.05)
    parser.add_argument("--equivalence-tolerance", type=float, default=1e-9)
    parser.add_argument("--complexity-penalty", type=float, default=1e-4)
    parser.add_argument("--neighbor-penalty", type=float, default=0.0)
    parser.add_argument("--dual-penalty", type=float, default=0.0)
    parser.add_argument("--placebo-penalty", type=float, default=0.0)
    parser.add_argument("--max-neighbor-atoms", type=int, default=None)
    parser.add_argument("--max-dual-atoms", type=int, default=None)
    parser.add_argument("--max-placebo-atoms", type=int, default=None)
    parser.add_argument("--objective", choices=["oracle_regret", "value_gap"], default="oracle_regret")
    parser.add_argument("--time-limit-sec", type=float, default=60.0)
    parser.add_argument("--min-weight", type=float, default=0.1)
    parser.add_argument("--tie-margin", type=float, default=1e-6)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--csv-out", default="experiments/dual_sensitivity/block3_static_kill_gate.csv")
    parser.add_argument("--rules-out", default="experiments/dual_sensitivity/block3_static_kill_gate_rules.txt")
    parser.add_argument("--report-out", default="experiments/dual_sensitivity/block3_static_kill_gate_report.md")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.max_samples < 0:
        raise ValueError("--max-samples must be nonnegative")
    if args.max_movements <= 0:
        raise ValueError("--max-movements must be positive")
    if args.epsilon <= 0.0:
        raise ValueError("--epsilon must be positive")
    if any(budget <= 0 for budget in args.budgets):
        raise ValueError(f"Atom budgets must be positive: {args.budgets}")
    if args.min_regime_count < 0:
        raise ValueError("--min-regime-count must be nonnegative")
    if args.target_total_states <= 0:
        raise ValueError("--target-total-states must be positive")
    if args.dual_win_threshold < 0.0 or args.dual_win_threshold > 1.0:
        raise ValueError("--dual-win-threshold must be in [0, 1]")
    if args.regret_improvement_threshold < 0.0:
        raise ValueError("--regret-improvement-threshold must be nonnegative")
    if args.equivalence_tolerance < 0.0:
        raise ValueError("--equivalence-tolerance must be nonnegative")
    if args.time_limit_sec <= 0.0:
        raise ValueError("--time-limit-sec must be positive")
    if args.min_weight < 0.0:
        raise ValueError("--min-weight must be nonnegative")
    if args.tie_margin < 0.0:
        raise ValueError("--tie-margin must be nonnegative")
    category_budgets = [args.max_neighbor_atoms, args.max_dual_atoms, args.max_placebo_atoms]
    if any(value is not None and value < 0 for value in category_budgets):
        raise ValueError("Category atom budgets must be nonnegative when supplied")
    penalties = [args.complexity_penalty, args.neighbor_penalty, args.dual_penalty, args.placebo_penalty]
    if any(value < 0.0 for value in penalties):
        raise ValueError("Atom penalties must be nonnegative")


def validate_sample_schema(sample: dict[str, Any], path: Path, sample_idx: int) -> None:
    missing = REQUIRED_SAMPLE_FIELDS - set(sample)
    if missing:
        raise ValueError(f"Sample {sample_idx} in {path} is missing fields: {sorted(missing)}")
    for field in ["queues", "vehicle_counts", "capacities", "tls_movements"]:
        if not isinstance(sample[field], dict):
            raise ValueError(f"Sample {sample_idx} in {path} field {field} must be an object")


def load_and_group_samples(
    paths: list[Path], max_samples: int, default_regime: str | None
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int], list[str], list[str]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    raw_counts: dict[str, int] = {}
    notes: list[str] = []
    input_regime_status: list[str] = []
    remaining = max_samples
    seen = 0

    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        samples = data.get("samples")
        if not isinstance(samples, list):
            raise ValueError(f"State file {path} must contain a samples list")
        file_regime_status = data.get("regime_status")
        if isinstance(file_regime_status, dict):
            for regime, status in file_regime_status.items():
                input_regime_status.append(f"{regime}: {status.get('status', 'unknown')} - {status.get('rationale', '')}")
        selected = samples if remaining <= 0 else samples[:remaining]
        for sample_idx, sample in enumerate(selected):
            if not isinstance(sample, dict):
                raise ValueError(f"Sample {sample_idx} in {path} must be an object")
            validate_sample_schema(sample, path, sample_idx)
            regime = sample.get("regime")
            sample_copy = dict(sample)
            if regime is None:
                if not default_regime:
                    raise ValueError(
                        f"Sample {sample_idx} in {path} has no regime; pass --default-regime for legacy fixtures"
                    )
                regime = default_regime
                sample_copy["regime"] = regime
                sample_copy.setdefault(
                    "regime_detail",
                    "Legacy unlabeled fixture assigned by --default-regime; proxy/static caveat applies.",
                )
                note = (
                    f"{path}: unlabeled samples assigned default regime {default_regime}; "
                    "treat as preliminary/proxy evidence."
                )
                if note not in notes:
                    notes.append(note)
            regime = str(regime)
            sample_copy["_source_path"] = str(path)
            sample_copy["_source_index"] = seen
            sample_copy["_source_label"] = f"{path}#{regime}#{seen}"
            grouped.setdefault(regime, []).append(sample_copy)
            raw_counts[regime] = raw_counts.get(regime, 0) + 1
            seen += 1
        if remaining > 0:
            remaining -= len(selected)
            if remaining <= 0:
                break
    return grouped, raw_counts, notes, input_regime_status


def examples_for_samples(
    samples: list[dict[str, Any]], tls: str, max_movements: int, epsilon: float
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for sample in samples:
        scenario = scenario_from_sample(sample, tls, max_movements)
        if scenario is None:
            continue
        summary = summarize_scenario(scenario, epsilon)
        example = build_example(summary)
        if example is None:
            continue
        example["source"] = str(sample["_source_label"])
        examples.append(example)
    return examples


def best_run(runs: list[dict[str, Any]], library: str) -> dict[str, Any] | None:
    solved = [run for run in runs if run.get("status") == "SOLVED" and run.get("library") == library]
    if not solved:
        return None
    return min(
        solved,
        key=lambda run: (
            float(run.get("realized_total_regret", 0.0)),
            int(run.get("program_complexity", 0)),
            int(run.get("max_atoms", run.get("budget", 0))),
        ),
    )


def solve_regime(
    examples: list[dict[str, Any]],
    libraries: list[str],
    budgets: list[int],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    seen: set[tuple[str, int, tuple[str, ...]]] = set()
    for budget in budgets:
        for library in libraries:
            atoms = atoms_for_library(library)
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
    return runs


def compare_dual_pressure(
    regime: str,
    dual_run: dict[str, Any],
    pressure_run: dict[str, Any],
    num_examples: int,
    min_regime_count: int,
    sample_target_met: bool,
    equivalence_tolerance: float,
    rules_path: Path,
) -> dict[str, Any]:
    dual_by_key = {(row["source"], row["scenario"]): row for row in dual_run.get("results", [])}
    pressure_by_key = {(row["source"], row["scenario"]): row for row in pressure_run.get("results", [])}
    keys = sorted(set(dual_by_key) & set(pressure_by_key))

    disagreements = 0
    dual_wins = 0
    pressure_wins = 0
    ties = 0
    dual_regrets: list[float] = []
    pressure_regrets: list[float] = []
    aligned_rows: list[dict[str, Any]] = []

    for key in keys:
        dual_row = dual_by_key[key]
        pressure_row = pressure_by_key[key]
        dual_regret = float(dual_row["oracle_regret"])
        pressure_regret = float(pressure_row["oracle_regret"])
        dual_regrets.append(dual_regret)
        pressure_regrets.append(pressure_regret)
        disagreement = int(dual_row["chosen_movement"] != pressure_row["chosen_movement"])
        dual_win = int(dual_regret < pressure_regret - equivalence_tolerance)
        pressure_win = int(pressure_regret < dual_regret - equivalence_tolerance)
        tie = int(abs(dual_regret - pressure_regret) <= equivalence_tolerance)
        disagreements += disagreement
        dual_wins += dual_win
        pressure_wins += pressure_win
        ties += tie
        aligned_rows.append(
            {
                "source": key[0],
                "scenario": key[1],
                "dual_chosen_movement": dual_row["chosen_movement"],
                "pressure_chosen_movement": pressure_row["chosen_movement"],
                "dual_oracle_regret": dual_regret,
                "pressure_oracle_regret": pressure_regret,
                "disagreement": bool(disagreement),
                "dual_win": bool(dual_win),
                "pressure_win": bool(pressure_win),
                "tie": bool(tie),
            }
        )

    n = len(keys)
    denominator = max(n, 1)
    dual_mean = sum(dual_regrets) / denominator
    pressure_mean = sum(pressure_regrets) / denominator
    preliminary = (not sample_target_met) or num_examples < min_regime_count
    claim_scope = "preliminary_static_sample_relative" if preliminary else "static_sample_relative"
    recovered_rules = {
        PRIMARY_DUAL_LIBRARY: {
            "selected_atoms": list(dual_run.get("selected_atoms", [])),
            "rule_text_path": str(rules_path),
            "rule_text": str(dual_run.get("rule_text", "")),
        },
        PRIMARY_PRESSURE_LIBRARY: {
            "selected_atoms": list(pressure_run.get("selected_atoms", [])),
            "rule_text_path": str(rules_path),
            "rule_text": str(pressure_run.get("rule_text", "")),
        },
    }
    return {
        "regime": regime,
        "num_examples": int(num_examples),
        "num_aligned_examples": int(n),
        "sample_target_met": bool(sample_target_met and num_examples >= min_regime_count),
        "claim_scope": claim_scope,
        "dual_library": PRIMARY_DUAL_LIBRARY,
        "pressure_library": PRIMARY_PRESSURE_LIBRARY,
        "dual_vs_pressure_disagreement_rate": disagreements / denominator,
        "dual_win_rate": dual_wins / denominator,
        "pressure_win_rate": pressure_wins / denominator,
        "tie_rate": ties / denominator,
        "dual_mean_oracle_regret": dual_mean,
        "pressure_mean_oracle_regret": pressure_mean,
        "mean_oracle_regret_delta_pressure_minus_dual": pressure_mean - dual_mean,
        "dual_worst_case_regret": max(dual_regrets, default=0.0),
        "pressure_worst_case_regret": max(pressure_regrets, default=0.0),
        "selected_atoms_dual": list(dual_run.get("selected_atoms", [])),
        "selected_atoms_pressure": list(pressure_run.get("selected_atoms", [])),
        "recovered_symbolic_rules": recovered_rules,
        "rule_text_path": str(rules_path),
        "aligned_result_diagnostics": aligned_rows,
    }


def decide_route(
    metrics: list[dict[str, Any]],
    sample_target_met: bool,
    dual_win_threshold: float,
    regret_improvement_threshold: float,
    equivalence_tolerance: float,
) -> dict[str, Any]:
    caveats = [
        "Route is based on static/sample-relative one-step recovery metrics only; closed-loop claims are deferred.",
    ]
    if not metrics:
        return {
            "route_decision": "diagnostic",
            "route_confidence": "LOW",
            "route_rationale": "No solved regime metrics were available.",
            "route_caveats": caveats + ["No regime evidence was available for routing."],
        }
    if not sample_target_met:
        return {
            "route_decision": "diagnostic",
            "route_confidence": "LOW",
            "route_rationale": "Valid converted examples are below the configured sample target.",
            "route_caveats": caveats + ["sample target not met; treat all positive route evidence as preliminary."],
        }

    binding_metrics = [m for m in metrics if "slack" not in str(m.get("regime", ""))]
    if not binding_metrics:
        caveats.append("No non-slack binding/proxy regimes were available.")
        return {
            "route_decision": "diagnostic",
            "route_confidence": "LOW",
            "route_rationale": "Only slack or unlabeled evidence was available.",
            "route_caveats": caveats,
        }

    pressure_advantage = any(
        float(m.get("pressure_win_rate", 0.0)) > float(m.get("dual_win_rate", 0.0)) + equivalence_tolerance
        or float(m.get("mean_oracle_regret_delta_pressure_minus_dual", 0.0)) < -regret_improvement_threshold
        for m in binding_metrics
    )
    if pressure_advantage:
        return {
            "route_decision": "diagnostic",
            "route_confidence": "MEDIUM",
            "route_rationale": "At least one binding/proxy regime favors pressure over dual under static metrics.",
            "route_caveats": caveats,
        }

    improving = [
        m
        for m in binding_metrics
        if float(m.get("dual_win_rate", 0.0)) >= dual_win_threshold
        and float(m.get("mean_oracle_regret_delta_pressure_minus_dual", 0.0)) >= regret_improvement_threshold
        and float(m.get("pressure_win_rate", 0.0)) <= equivalence_tolerance
    ]
    if improving and len(improving) == len(binding_metrics):
        return {
            "route_decision": "dual-improves-pressure",
            "route_confidence": "HIGH",
            "route_rationale": "All binding/proxy regimes meet the configured dual win and regret-improvement thresholds.",
            "route_caveats": caveats,
        }

    equivalent = all(
        abs(float(m.get("mean_oracle_regret_delta_pressure_minus_dual", 0.0))) <= max(regret_improvement_threshold, equivalence_tolerance)
        and float(m.get("pressure_win_rate", 0.0)) <= equivalence_tolerance
        and float(m.get("dual_win_rate", 0.0)) <= max(dual_win_threshold, equivalence_tolerance)
        for m in metrics
    )
    if equivalent:
        return {
            "route_decision": "pressure-equivalent",
            "route_confidence": "MEDIUM",
            "route_rationale": "Dual and pressure have tie-equivalent static oracle regret across solved regimes.",
            "route_caveats": caveats,
        }

    return {
        "route_decision": "diagnostic",
        "route_confidence": "MEDIUM",
        "route_rationale": "Static evidence is mixed or below the configured threshold for a dual-improvement route.",
        "route_caveats": caveats,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "experiment",
        "regime",
        "num_examples",
        "num_aligned_examples",
        "sample_target_met",
        "claim_scope",
        "dual_vs_pressure_disagreement_rate",
        "dual_win_rate",
        "pressure_win_rate",
        "tie_rate",
        "dual_mean_oracle_regret",
        "pressure_mean_oracle_regret",
        "mean_oracle_regret_delta_pressure_minus_dual",
        "dual_worst_case_regret",
        "pressure_worst_case_regret",
        "selected_atoms_dual",
        "selected_atoms_pressure",
        "rule_text_path",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_phase3_rules(runs_by_regime: dict[str, list[dict[str, Any]]], note: str) -> str:
    sections = [
        "Phase 3 Static Kill-Gate Rule Text",
        note,
        "Generated rules are finite-dictionary, sample-relative audit artifacts.",
        "Rules are grouped by regime and library; no rendered rule is executed or deployed here.",
    ]
    for regime in sorted(runs_by_regime):
        sections.append("\n---\n")
        sections.append(f"Regime: {regime}")
        for run in runs_by_regime[regime]:
            if run.get("status") != "SOLVED":
                continue
            sections.append("")
            sections.append(f"Library: {run.get('library')} | max_atoms={run.get('max_atoms', run.get('budget'))}")
            sections.append("Selected atoms: " + ", ".join(run.get("selected_atoms", [])))
            sections.append(str(run.get("rule_text", "")))
    return "\n".join(sections).rstrip() + "\n"


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase 3 Static Kill-Gate Report",
        "",
        f"Route decision: `{payload['route_decision']}`",
        f"Route confidence: `{payload['route_confidence']}`",
        "",
        "This report is static/sample-relative only; closed-loop SUMO performance and travel-time claims are deferred.",
        "",
        "## Rationale",
        "",
        str(payload["route_rationale"]),
        "",
        "## Sample Sufficiency",
        "",
        f"- Valid converted examples: {payload['num_examples_total']}",
        f"- Target valid examples: {payload['target_total_states']}",
        f"- Sample target met: {payload['sample_target_met']}",
        f"- Preliminary regimes: {', '.join(payload['preliminary_regimes']) if payload['preliminary_regimes'] else 'None'}",
        "",
        "## Per-Regime Metrics",
        "",
        "| Regime | Examples | Disagreement | Dual win | Pressure win | Tie | Δ regret pressure-dual | Scope |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for metric in payload["regime_metrics"]:
        lines.append(
            "| {regime} | {num_examples} | {disagreement:.6g} | {dual_win:.6g} | {pressure_win:.6g} | {tie:.6g} | {delta:.6g} | {scope} |".format(
                regime=metric["regime"],
                num_examples=metric["num_examples"],
                disagreement=float(metric["dual_vs_pressure_disagreement_rate"]),
                dual_win=float(metric["dual_win_rate"]),
                pressure_win=float(metric["pressure_win_rate"]),
                tie=float(metric["tie_rate"]),
                delta=float(metric["mean_oracle_regret_delta_pressure_minus_dual"]),
                scope=metric["claim_scope"],
            )
        )
    lines.extend(["", "## Caveats", ""])
    for caveat in payload["route_caveats"]:
        lines.append(f"- {caveat}")
    if payload.get("input_labeling_notes"):
        lines.extend(["", "## Input Labeling Notes", ""])
        for note in payload["input_labeling_notes"]:
            lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- JSON: `{payload['out']}`",
            f"- CSV: `{payload['csv_out']}`",
            f"- Rules: `{payload['rules_out']}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    args = parse_args()
    validate_args(args)
    validate_atom_registry()
    library_names = select_library_names(args.libraries)
    if PRIMARY_DUAL_LIBRARY not in library_names:
        library_names.append(PRIMARY_DUAL_LIBRARY)
    if PRIMARY_PRESSURE_LIBRARY not in library_names:
        library_names.append(PRIMARY_PRESSURE_LIBRARY)

    out_path = Path(args.out)
    csv_path = Path(args.csv_out)
    rules_path = Path(args.rules_out)
    report_path = Path(args.report_out)
    state_paths = [Path(p) for p in args.states] or [Path("experiments/dual_sensitivity/block3_regime_states.json")]
    grouped_samples, raw_counts, labeling_notes, input_regime_status = load_and_group_samples(
        state_paths, args.max_samples, args.default_regime
    )

    runs_by_regime: dict[str, list[dict[str, Any]]] = {}
    valid_examples_by_regime: dict[str, int] = {}
    regime_metrics: list[dict[str, Any]] = []

    for regime in sorted(grouped_samples):
        examples = examples_for_samples(grouped_samples[regime], args.tls, args.max_movements, args.epsilon)
        valid_examples_by_regime[regime] = len(examples)
        if not examples:
            runs_by_regime[regime] = []
            continue
        runs = solve_regime(examples, library_names, args.budgets, args)
        runs_by_regime[regime] = runs

    num_examples_total = sum(valid_examples_by_regime.values())
    sample_target_met = num_examples_total >= args.target_total_states
    preliminary_regimes = sorted(
        regime
        for regime, count in valid_examples_by_regime.items()
        if count < args.min_regime_count or not sample_target_met
    )

    for regime in sorted(runs_by_regime):
        dual_run = best_run(runs_by_regime[regime], PRIMARY_DUAL_LIBRARY)
        pressure_run = best_run(runs_by_regime[regime], PRIMARY_PRESSURE_LIBRARY)
        if dual_run is None or pressure_run is None:
            continue
        metric = compare_dual_pressure(
            regime=regime,
            dual_run=dual_run,
            pressure_run=pressure_run,
            num_examples=valid_examples_by_regime.get(regime, 0),
            min_regime_count=args.min_regime_count,
            sample_target_met=sample_target_met,
            equivalence_tolerance=args.equivalence_tolerance,
            rules_path=rules_path,
        )
        regime_metrics.append(metric)

    route = decide_route(
        regime_metrics,
        sample_target_met=sample_target_met,
        dual_win_threshold=args.dual_win_threshold,
        regret_improvement_threshold=args.regret_improvement_threshold,
        equivalence_tolerance=args.equivalence_tolerance,
    )
    if labeling_notes:
        route["route_caveats"] = list(route["route_caveats"]) + [
            "Legacy unlabeled input was assigned a default regime; route evidence is proxy/preliminary."
        ]

    note = (
        "Phase 3 static kill-gate; primary route comparison is dual_sensitivity vs "
        "pressure_backpressure. Evidence is finite-dictionary and sample-relative."
    )
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    rules_path.write_text(render_phase3_rules(runs_by_regime, note), encoding="utf-8")

    csv_rows = []
    for metric in regime_metrics:
        csv_rows.append(
            {
                "experiment": "block3_static_pressure_failure_kill_gate",
                "regime": metric["regime"],
                "num_examples": metric["num_examples"],
                "num_aligned_examples": metric["num_aligned_examples"],
                "sample_target_met": metric["sample_target_met"],
                "claim_scope": metric["claim_scope"],
                "dual_vs_pressure_disagreement_rate": metric["dual_vs_pressure_disagreement_rate"],
                "dual_win_rate": metric["dual_win_rate"],
                "pressure_win_rate": metric["pressure_win_rate"],
                "tie_rate": metric["tie_rate"],
                "dual_mean_oracle_regret": metric["dual_mean_oracle_regret"],
                "pressure_mean_oracle_regret": metric["pressure_mean_oracle_regret"],
                "mean_oracle_regret_delta_pressure_minus_dual": metric[
                    "mean_oracle_regret_delta_pressure_minus_dual"
                ],
                "dual_worst_case_regret": metric["dual_worst_case_regret"],
                "pressure_worst_case_regret": metric["pressure_worst_case_regret"],
                "selected_atoms_dual": ";".join(metric["selected_atoms_dual"]),
                "selected_atoms_pressure": ";".join(metric["selected_atoms_pressure"]),
                "rule_text_path": metric["rule_text_path"],
            }
        )
    write_csv(csv_path, csv_rows)

    runs_by_regime_payload = {regime: runs for regime, runs in sorted(runs_by_regime.items())}
    payload = {
        "experiment": "block3_static_pressure_failure_kill_gate",
        "status": "PASSED" if regime_metrics and route["route_decision"] in ROUTE_DECISIONS else "FAILED",
        "scope": "static_sample_relative_only_no_closed_loop_claims",
        "input_states": [str(path) for path in state_paths],
        "input_regime_status": input_regime_status,
        "input_labeling_notes": labeling_notes,
        "tls": args.tls,
        "target_total_states": args.target_total_states,
        "min_regime_count": args.min_regime_count,
        "raw_samples_by_regime": raw_counts,
        "valid_examples_by_regime": valid_examples_by_regime,
        "num_examples_total": num_examples_total,
        "sample_target_met": sample_target_met,
        "preliminary_regimes": preliminary_regimes,
        "thresholds": {
            "dual_win_threshold": args.dual_win_threshold,
            "regret_improvement_threshold": args.regret_improvement_threshold,
            "equivalence_tolerance": args.equivalence_tolerance,
        },
        "objective_mode": args.objective,
        "budgets": args.budgets,
        "libraries": library_names,
        "atom_registry": ATOM_REGISTRY,
        "regime_metrics": regime_metrics,
        "runs_by_regime": runs_by_regime_payload,
        "csv_out": str(csv_path),
        "rules_out": str(rules_path),
        "report_out": str(report_path),
        "out": str(out_path),
        "note": note,
        **route,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(payload), encoding="utf-8")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "route_decision": payload["route_decision"],
                "out": str(out_path),
                "csv_out": str(csv_path),
                "rules_out": str(rules_path),
                "report_out": str(report_path),
                "num_examples_total": num_examples_total,
                "sample_target_met": sample_target_met,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
