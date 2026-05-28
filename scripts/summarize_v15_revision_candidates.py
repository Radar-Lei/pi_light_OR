#!/usr/bin/env python3
"""Summarize post-holdout v1.5 revision candidates from training-only selection artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_INPUTS = [
    "experiments/dual_sensitivity/v1_5_r2_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r3_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r4_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r5_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r6_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r7_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r8_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r9_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r10_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r11_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r12_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r13_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r14_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r15_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r16_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r17_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r18_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r19_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r20_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r21_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r22_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r23_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r24_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r25_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r26_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r27_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r28_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r29_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r30_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r31_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r32_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r33_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r34_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r35_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r36_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r37_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r38_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r39_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r40_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r41_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r42_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r43_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r44_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r45_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r46_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r47_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r48_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r49_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r50_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r51_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r52_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r53_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r54_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r55_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r56_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r57_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r58_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r59_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r60_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r61_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r62_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r63_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r64_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r65_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r66_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r67_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r68_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r69_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r70_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r71_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r72_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r73_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r74_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r75_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r76_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r77_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r78_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r79_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r80_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r81_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r82_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r83_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r84_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r85_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r86_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r87_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r88_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r89_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r90_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r91_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r92_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r93_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r94_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r95_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r96_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r97_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r98_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r99_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r100_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r101_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r102_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r103_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r104_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r105_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r106_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r107_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r108_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r109_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r110_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r111_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r112_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r113_training_selection.json",
    "experiments/dual_sensitivity/v1_5_r114_training_selection.json",
]
DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_revision_candidate_summary.json"
REQUIREMENTS_COVERED = ["V15-REVISION-01", "V15-CLAIM-01"]


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


def summarize_candidate(payload: dict[str, Any], path: Path) -> dict[str, Any]:
    composite = payload.get("primary_composite_training_results", [])
    strong_results = [
        item
        for item in composite
        if isinstance(item, dict)
        and str(item.get("baseline")) in {"max_pressure", "capacity_aware_pressure", "finite_storage_double_pressure"}
    ]
    positive_strong = [
        float(item.get("paired_difference", 0.0))
        for item in strong_results
        if float(item.get("paired_difference", 0.0)) > 0.0
    ]
    harms = payload.get("safety_harms", [])
    unfinished_harms = [
        item
        for item in harms
        if isinstance(item, dict) and str(item.get("metric")) == "unfinished_vehicle_count"
    ]
    return {
        "input": str(path),
        "experiment": payload.get("experiment"),
        "controller_id": payload.get("controller_id"),
        "status": payload.get("status"),
        "decision": payload.get("decision"),
        "claim_ready": bool(payload.get("claim_ready", False)),
        "action_change_rate": payload.get("mechanism_summary", {}).get("action_change_rate"),
        "binding_decision_rate": payload.get("mechanism_summary", {}).get("binding_decision_rate"),
        "strong_baseline_positive_composite_count": len(positive_strong),
        "strong_baseline_result_count": len(strong_results),
        "min_strong_baseline_composite_difference": min(positive_strong) if positive_strong else None,
        "safety_harm_count": len(harms),
        "unfinished_vehicle_harm_count": len(unfinished_harms),
        "reasons": payload.get("reasons", []),
    }


def build_summary(paths: list[Path]) -> dict[str, Any]:
    candidates = [summarize_candidate(load_selection(path), path) for path in paths]
    selected = [item for item in candidates if str(item.get("status")) == "SELECTED_PENDING_CONFIRMATORY_PROTOCOL"]
    rejected = [item for item in candidates if str(item.get("status")) == "REJECTED"]
    completion_blockers = [
        item
        for item in candidates
        if int(item.get("unfinished_vehicle_harm_count", 0) or 0) > 0
    ]
    status = "CANDIDATE_SELECTED" if selected else "NO_CANDIDATE_SELECTED"
    recommendation = (
        "lock fresh confirmatory protocol for selected candidate"
        if selected
        else "horizon-modeled variants remain non-selected under zero-tolerance unfinished guards: tune only on fresh training seeds or revisit the safety contract before any confirmatory holdout"
    )
    return {
        "experiment": "v1_5_revision_candidate_summary",
        "status": status,
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": False,
        "candidate_count": len(candidates),
        "selected_candidate_count": len(selected),
        "rejected_candidate_count": len(rejected),
        "completion_safety_blocker_count": len(completion_blockers),
        "candidates": candidates,
        "dominant_blocker": "unfinished_vehicle_count_safety_guard" if completion_blockers else None,
        "recommendation": recommendation,
        "claim_scope": {
            "closed_loop_superiority_claim_allowed": False,
            "why": "training-only candidate convergence is not confirmatory evidence",
        },
    }


def write_summary(inputs: list[Path], out: Path) -> dict[str, Any]:
    payload = build_summary(inputs)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_summary([Path(path) for path in args.inputs], Path(args.out))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "out": args.out,
                "recommendation": payload["recommendation"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
