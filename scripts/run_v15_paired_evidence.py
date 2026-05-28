#!/usr/bin/env python3
"""Strict v1.5 paired evidence checker for locked holdout artifacts."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from scipy import stats

DEFAULT_INPUT = "experiments/dual_sensitivity/v1_5_locked_holdout_execution.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_paired_evidence.json"
REQUIREMENTS_COVERED = ["V15-EVID-02", "V15-CLAIM-01"]
VALID_STATUSES = {"PASSED", "FAILED", "INCONCLUSIVE"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def load_input(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def completed_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in payload.get("scenario_results", [])
        if isinstance(row, dict)
        and row.get("scenario_status") == "completed"
        and row.get("feasibility_status") in {"run", "completed"}
    ]


def composite_cost(row: dict[str, Any], weights: dict[str, float]) -> float:
    components = row.get("objective_components", {})
    if not isinstance(components, dict):
        raise ValueError("row missing objective_components")
    return float(sum(float(components[field]) * float(weights[field]) for field in weights))


def _ci(differences: list[float]) -> tuple[float, float, float]:
    if len(differences) < 2:
        raise ValueError("at least two paired seeds are required")
    if len(set(float(value) for value in differences)) == 1:
        value = float(differences[0])
        return value, value, 0.0
    result = stats.bootstrap(
        (differences,),
        lambda data, axis: data.mean(axis=axis),
        paired=True,
        confidence_level=0.95,
        n_resamples=999,
        method="percentile",
        random_state=0,
    )
    return float(result.confidence_interval.low), float(result.confidence_interval.high), float(result.standard_error)


def grouped_rows(rows: list[dict[str, Any]]) -> dict[tuple[str, float, str], dict[int, dict[str, Any]]]:
    grouped: dict[tuple[str, float, str], dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        key = (str(row.get("scenario_tag")), float(row.get("demand_multiplier", 1.0)), str(row.get("controller")))
        grouped[key][int(row["seed"])] = row
    return grouped


def paired_composite_results(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    rows = completed_rows(payload)
    grouped = grouped_rows(rows)
    controller = str(payload.get("controller_id"))
    baselines = [str(item) for item in payload.get("required_baselines", [])]
    endpoint = payload.get("primary_endpoint", {})
    weights = {str(key): float(value) for key, value in dict(endpoint.get("weights", {})).items()}
    scenarios = sorted({key[0] for key in grouped if key[2] == controller})
    multipliers = sorted({key[1] for key in grouped if key[2] == controller})
    results = []
    reasons = []
    for scenario in scenarios:
        for multiplier in multipliers:
            proposed = grouped.get((scenario, multiplier, controller), {})
            for baseline in baselines:
                comparator = grouped.get((scenario, multiplier, baseline), {})
                if set(proposed) != set(comparator):
                    reasons.append(f"unpaired seeds for {scenario}/{multiplier}/{baseline}")
                    continue
                if len(proposed) < 2:
                    reasons.append(f"fewer than two paired seeds for {scenario}/{multiplier}/{baseline}")
                    continue
                diffs = []
                proposed_costs = []
                baseline_costs = []
                for seed in sorted(proposed):
                    proposed_cost = composite_cost(proposed[seed], weights)
                    baseline_cost = composite_cost(comparator[seed], weights)
                    proposed_costs.append(proposed_cost)
                    baseline_costs.append(baseline_cost)
                    diffs.append(baseline_cost - proposed_cost)
                ci_low, ci_high, se = _ci(diffs)
                mean = float(statistics.fmean(diffs))
                try:
                    wilcoxon = stats.wilcoxon(diffs, alternative="greater", zero_method="zsplit")
                    pvalue = float(wilcoxon.pvalue)
                except Exception:
                    pvalue = 1.0
                if ci_low > 0.0:
                    classification = "strict_positive"
                elif ci_low >= 0.0:
                    classification = "non_worsening"
                elif ci_high < 0.0:
                    classification = "bounded_harm"
                else:
                    classification = "inconclusive"
                results.append(
                    {
                        "scenario_tag": scenario,
                        "demand_multiplier": multiplier,
                        "baseline": baseline,
                        "paired_seed_ids": sorted(proposed),
                        "n_seeds": len(proposed),
                        "difference_definition": "baseline_composite_minus_v1_5_composite",
                        "positive_means": "v1_5_lower_composite_cost",
                        "paired_differences": [float(value) for value in diffs],
                        "mean_paired_difference": mean,
                        "ci_low": ci_low,
                        "ci_high": ci_high,
                        "standard_error": se,
                        "wilcoxon_pvalue": pvalue,
                        "classification": classification,
                        "strict_positive_signal": ci_low > 0.0,
                        "mean_v1_5_composite": float(statistics.fmean(proposed_costs)),
                        "mean_baseline_composite": float(statistics.fmean(baseline_costs)),
                    }
                )
    return results, reasons


def safety_guard_results(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    rows = completed_rows(payload)
    grouped = grouped_rows(rows)
    controller = str(payload.get("controller_id"))
    baselines = [str(item) for item in payload.get("required_baselines", [])]
    guards = payload.get("safety_guards", {})
    scenarios = sorted({key[0] for key in grouped if key[2] == controller})
    multipliers = sorted({key[1] for key in grouped if key[2] == controller})
    results = []
    reasons = []
    for scenario in scenarios:
        for multiplier in multipliers:
            proposed = grouped.get((scenario, multiplier, controller), {})
            for baseline in baselines:
                comparator = grouped.get((scenario, multiplier, baseline), {})
                shared = sorted(set(proposed) & set(comparator))
                for metric, config in dict(guards).items():
                    tolerance = float(dict(config).get("practical_harm_tolerance", 0.0))
                    harms = []
                    for seed in shared:
                        if metric not in proposed[seed] or metric not in comparator[seed]:
                            reasons.append(f"missing safety metric {metric} for {scenario}/{multiplier}/{baseline}/seed={seed}")
                            continue
                        prop = float(proposed[seed][metric])
                        comp = float(comparator[seed][metric])
                        allowed = comp * (1.0 + tolerance)
                        if prop > allowed + 1e-9:
                            harms.append({"seed": seed, "v1_5": prop, "baseline": comp, "allowed": allowed})
                    results.append(
                        {
                            "scenario_tag": scenario,
                            "demand_multiplier": multiplier,
                            "baseline": baseline,
                            "metric": metric,
                            "practical_harm_tolerance": tolerance,
                            "harm_count": len(harms),
                            "passed": len(harms) == 0,
                            "harms": harms[:20],
                        }
                    )
    return results, reasons


def build_evidence_payload(input_payload: dict[str, Any], input_path: Path) -> dict[str, Any]:
    reasons = []
    if input_payload.get("experiment") != "v1_5_locked_holdout_execution":
        reasons.append("input artifact is not v1_5_locked_holdout_execution")
    if input_payload.get("locked_protocol_status") != "LOCKED":
        reasons.append("locked protocol status is not LOCKED")
    if input_payload.get("dry_run"):
        reasons.append("dry-run execution cannot support paired evidence")
    if input_payload.get("all_rows_executed") is not True:
        reasons.append("input artifact does not report all_rows_executed=true")
    if input_payload.get("status") != "COMPLETE_PENDING_PAIRED_EVIDENCE":
        reasons.append(f"input artifact status is {input_payload.get('status')}, not COMPLETE_PENDING_PAIRED_EVIDENCE")
    row_audit = input_payload.get("row_audit", {}) if isinstance(input_payload.get("row_audit"), dict) else {}
    for key in ["missing_row_count", "failed_row_count", "duplicate_row_count"]:
        if int(row_audit.get(key, 0) or 0) > 0:
            reasons.append(f"row audit reports {key}={row_audit.get(key)}")

    primary_results, primary_reasons = paired_composite_results(input_payload)
    safety_results, safety_reasons = safety_guard_results(input_payload)
    reasons.extend(primary_reasons)
    reasons.extend(safety_reasons)
    primary_passed = bool(primary_results) and all(result["classification"] == "strict_positive" for result in primary_results)
    safety_passed = bool(safety_results) and all(result["passed"] for result in safety_results)
    if reasons:
        status = "INCONCLUSIVE"
    elif primary_passed and safety_passed:
        status = "PASSED"
    elif any(result["classification"] == "bounded_harm" for result in primary_results) or not safety_passed:
        status = "FAILED"
    else:
        status = "INCONCLUSIVE"
    if status not in VALID_STATUSES:
        status = "INCONCLUSIVE"
    return {
        "experiment": "v1_5_paired_evidence",
        "status": status,
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": status == "PASSED",
        "input_artifact": str(input_path),
        "input_status": input_payload.get("status"),
        "locked_protocol_fingerprint": input_payload.get("locked_protocol_fingerprint"),
        "controller_id": input_payload.get("controller_id"),
        "required_baselines": input_payload.get("required_baselines", []),
        "primary_endpoint": input_payload.get("primary_endpoint"),
        "primary_composite_results": primary_results,
        "safety_guard_results": safety_results,
        "row_audit": row_audit,
        "reasons": list(dict.fromkeys(reasons)),
        "claim_scope": {
            "allowed": "bounded closed-loop superiority claim only if status is PASSED",
            "not_claimed_when_non_passed": [
                "closed_loop_superiority",
                "deployment_readiness",
            ],
        },
    }


def write_evidence(input_path: Path, out_path: Path) -> dict[str, Any]:
    payload = build_evidence_payload(load_input(input_path), input_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_evidence(Path(args.input), Path(args.out))
    print(json.dumps({"status": payload["status"], "out": args.out, "claim_ready": payload["claim_ready"]}, indent=2))
    if args.strict and payload["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
