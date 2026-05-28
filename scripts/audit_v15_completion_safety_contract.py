#!/usr/bin/env python3
"""Audit whether current v1.5 training evidence supports a completion-safety contract change."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import summarize_v15_revision_candidates as summary

DEFAULT_INPUTS = list(summary.DEFAULT_INPUTS)
DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_completion_safety_contract_audit.json"
REQUIREMENTS_COVERED = ["V15-SAFETY-CONTRACT-01", "V15-CLAIM-01"]
CORE_BASELINES = {"max_pressure", "capacity_aware_pressure", "finite_storage_double_pressure"}
ACTION_SEPARATION_FLOOR = 0.05


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", default=DEFAULT_INPUTS)
    parser.add_argument("--out", default=DEFAULT_OUT)
    return parser.parse_args()


def load_selection(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def core_composite_means(payload: dict[str, Any]) -> dict[str, float]:
    means = payload.get("core_composite_mean_differences")
    if isinstance(means, dict) and means:
        return {str(key): float(value) for key, value in means.items()}
    grouped: dict[str, list[float]] = {baseline: [] for baseline in CORE_BASELINES}
    for item in payload.get("primary_composite_training_results", []):
        if not isinstance(item, dict):
            continue
        baseline = str(item.get("baseline"))
        if baseline in grouped:
            grouped[baseline].append(float(item.get("paired_difference", 0.0)))
    return {
        baseline: float(sum(values) / len(values))
        for baseline, values in grouped.items()
        if values
    }


def unfinished_harms(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        harm
        for harm in payload.get("safety_harms", [])
        if isinstance(harm, dict) and str(harm.get("metric")) == "unfinished_vehicle_count"
    ]


def max_unfinished_excess(harms: list[dict[str, Any]]) -> float:
    if not harms:
        return 0.0
    return float(max(float(harm.get("r2", 0.0)) - float(harm.get("allowed", harm.get("baseline_value", 0.0))) for harm in harms))


def summarize_selection(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    means = core_composite_means(payload)
    harms = unfinished_harms(payload)
    mechanism = payload.get("mechanism_summary", {}) if isinstance(payload.get("mechanism_summary"), dict) else {}
    action_change_rate = float(mechanism.get("action_change_rate", 0.0) or 0.0)
    all_core_positive = CORE_BASELINES.issubset(means) and all(means[baseline] > 0.0 for baseline in CORE_BASELINES)
    return {
        "input": str(path),
        "experiment": payload.get("experiment"),
        "controller_id": payload.get("controller_id"),
        "status": payload.get("status"),
        "decision": payload.get("decision"),
        "action_change_rate": action_change_rate,
        "passes_action_separation_floor": action_change_rate >= ACTION_SEPARATION_FLOOR,
        "core_composite_mean_differences": means,
        "all_core_composite_means_positive": all_core_positive,
        "unfinished_vehicle_harm_count": len(harms),
        "max_unfinished_vehicle_excess": max_unfinished_excess(harms),
        "safety_harm_baselines": sorted({str(harm.get("baseline")) for harm in harms}),
        "reasons": payload.get("reasons", []),
    }


def build_audit(paths: list[Path]) -> dict[str, Any]:
    candidates = [summarize_selection(load_selection(path), path) for path in paths]
    selected = [item for item in candidates if item.get("status") == "SELECTED_PENDING_CONFIRMATORY_PROTOCOL"]
    positive_core = [item for item in candidates if item["all_core_composite_means_positive"]]
    positive_core_with_action = [
        item for item in positive_core if item["passes_action_separation_floor"]
    ]
    positive_core_safe = [
        item for item in positive_core_with_action if int(item["unfinished_vehicle_harm_count"]) == 0
    ]
    safety_filter_failures = [
        item
        for item in candidates
        if any(token in str(item.get("controller_id")) for token in ["filter", "safe", "safety", "terminal", "completion"])
        and int(item["unfinished_vehicle_harm_count"]) > 0
    ]
    low_separation_candidates = [
        item for item in candidates if not item["passes_action_separation_floor"]
    ]
    near_misses = [
        item
        for item in positive_core_with_action
        if int(item["unfinished_vehicle_harm_count"]) > 0
        and float(item["max_unfinished_vehicle_excess"]) <= 1.0
    ]
    top_positive = sorted(
        positive_core,
        key=lambda item: (
            item["passes_action_separation_floor"],
            -int(item["unfinished_vehicle_harm_count"]),
            min(item["core_composite_mean_differences"].get(baseline, float("-inf")) for baseline in CORE_BASELINES),
        ),
        reverse=True,
    )[:6]

    guard_passed = bool(positive_core_safe)
    revision_supported = False
    if guard_passed:
        status = "GUARD_PASSED_PENDING_FULL_TRAINING_SELECTION"
        recommendation = "continue full training execution for guard-passing candidate before any confirmatory holdout"
    else:
        status = "REVISION_REQUIRED"
        recommendation = (
            "do not lock confirmatory holdout; current evidence does not support weakening unfinished-vehicle safety, "
            "and the next method change should rebuild completion modeling rather than add another marginal horizon filter"
        )
    return {
        "experiment": "v1_5_completion_safety_contract_audit",
        "status": status,
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": False,
        "candidate_count": len(candidates),
        "selected_candidate_count": len(selected),
        "positive_core_composite_candidate_count": len(positive_core),
        "positive_core_with_action_separation_count": len(positive_core_with_action),
        "positive_core_safety_guard_pass_count": len(positive_core_safe),
        "unfinished_safety_blocker_count": len([item for item in candidates if int(item["unfinished_vehicle_harm_count"]) > 0]),
        "low_action_separation_count": len(low_separation_candidates),
        "safety_filter_failure_count": len(safety_filter_failures),
        "near_miss_count": len(near_misses),
        "top_positive_core_candidates": top_positive,
        "near_miss_candidates": near_misses,
        "contract_assessment": {
            "current_contract": "zero_tolerance_unfinished_vehicle_harm_against_core_strong_baselines",
            "completion_safety_guard_passed": guard_passed,
            "formal_contract_revision_supported_by_current_evidence": revision_supported,
            "why_revision_not_supported": (
                "Candidates with useful composite/action signal still show unfinished harms, while stronger safety filters "
                "collapse action separation and can turn composite means negative; this is insufficient evidence to weaken "
                "the strong-baseline safety contract."
            ),
        },
        "claim_scope": {
            "closed_loop_superiority_claim_allowed": False,
            "confirmatory_holdout_allowed": False,
            "why": "no training candidate passes both core composite/action-separation requirements and unfinished-vehicle safety guards",
        },
        "recommendation": recommendation,
    }


def write_audit(inputs: list[Path], out: Path) -> dict[str, Any]:
    payload = build_audit(inputs)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_audit([Path(path) for path in args.inputs], Path(args.out))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "out": args.out,
                "guard_passed": payload["contract_assessment"]["completion_safety_guard_passed"],
                "revision_supported": payload["contract_assessment"]["formal_contract_revision_supported_by_current_evidence"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
