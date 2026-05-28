#!/usr/bin/env python3
"""Select or reject the guarded v1.5-r2 candidate from training-only rows."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import lock_v15_protocol as base

DEFAULT_INPUT = "experiments/dual_sensitivity/v1_5_r2_training_execution.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_r2_training_selection.json"
REQUIREMENTS_COVERED = ["V15-R2-TRAIN-02", "V15-CLAIM-01"]
CORE_STRONG_BASELINES = {
    "max_pressure",
    "capacity_aware_pressure",
    "finite_storage_double_pressure",
}


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


def row_group_key(row: dict[str, Any]) -> tuple[str, float, int]:
    return (str(row.get("scenario_tag")), float(row.get("demand_multiplier", 1.0)), int(row["seed"]))


def composite_cost(row: dict[str, Any]) -> float:
    weights = base.build_protocol()["primary_endpoint"]["weights"]
    components = row.get("objective_components", {})
    return float(sum(float(components.get(field, 0.0)) * float(weight) for field, weight in weights.items()))


def summarize_training_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    rows = completed_rows(payload)
    controller = str(payload.get("controller_id"))
    baselines = [str(item) for item in payload.get("required_baselines", [])]
    guards = base.build_protocol()["safety_guards"]
    grouped: dict[tuple[str, float, int], dict[str, dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row_group_key(row), {})[str(row.get("controller"))] = row

    composite = []
    harms = []
    reasons = []
    for key, by_controller in sorted(grouped.items()):
        proposed = by_controller.get(controller)
        if proposed is None:
            reasons.append(f"missing proposed row for {key}")
            continue
        proposed_cost = composite_cost(proposed)
        for baseline in baselines:
            comparator = by_controller.get(baseline)
            if comparator is None:
                reasons.append(f"missing comparator {baseline} for {key}")
                continue
            baseline_cost = composite_cost(comparator)
            composite.append(
                {
                    "scenario_tag": key[0],
                    "demand_multiplier": key[1],
                    "seed": key[2],
                    "baseline": baseline,
                    "difference_definition": "baseline_composite_minus_candidate_composite",
                    "positive_means": "candidate_lower_composite_cost",
                    "candidate_composite": proposed_cost,
                    "r2_composite": proposed_cost,
                    "baseline_composite": baseline_cost,
                    "paired_difference": float(baseline_cost - proposed_cost),
                }
            )
            for metric, config in dict(guards).items():
                tolerance = float(dict(config).get("practical_harm_tolerance", 0.0))
                if metric not in proposed or metric not in comparator:
                    reasons.append(f"missing safety metric {metric} for {key}/{baseline}")
                    continue
                prop = float(proposed[metric])
                comp = float(comparator[metric])
                allowed = comp * (1.0 + tolerance)
                if prop > allowed + 1e-9:
                    harms.append(
                        {
                            "scenario_tag": key[0],
                            "demand_multiplier": key[1],
                            "seed": key[2],
                            "baseline": baseline,
                            "metric": metric,
                            "r2": prop,
                            "baseline_value": comp,
                            "allowed": allowed,
                            "practical_harm_tolerance": tolerance,
                        }
                    )
    return composite, harms, reasons


def mechanism_summary(payload: dict[str, Any]) -> dict[str, Any]:
    controller = str(payload.get("controller_id"))
    controller_rows = [row for row in completed_rows(payload) if row.get("controller") == controller]
    total_decisions = 0
    changed = 0
    binding = 0
    guardrail = 0
    double_fallback = 0
    terminal_fallback = 0
    double_score_filter = 0
    multi_filter = 0
    hold_only_filter = 0
    max_hold_filter = 0
    completion_risk_filter = 0
    route_completion_filter = 0
    route_demand_filter = 0
    route_demand_veto = 0
    route_horizon_filter = 0
    route_horizon_dominance_filter = 0
    terminal_exit_guard = 0
    route_horizon_max_envelope = 0
    route_horizon_core_envelope = 0
    route_horizon_double_envelope = 0
    route_horizon_core_minimax_guard = 0
    route_horizon_capacity_rescue_guard = 0
    route_horizon_capacity_score_envelope = 0
    route_horizon_native_capacity_score_rescue_guard = 0
    route_horizon_severe_double_guard = 0
    route_horizon_pressure_double_conflict_guard = 0
    route_horizon_completion_conflict_guard = 0
    route_horizon_capacity_completion_conflict_guard = 0
    route_horizon_early_capacity_completion_conflict_guard = 0
    route_horizon_negative_total_completion_conflict_guard = 0
    route_horizon_low_total_consensus_completion_guard = 0
    route_horizon_negative_total_raw_consensus_guard = 0
    route_horizon_core_consensus_guard = 0
    route_horizon_raw_consensus_guard = 0
    post_completion_veto_double_conflict_guard = 0
    route_horizon_pressure_safe_guard = 0
    route_horizon_tail_completion_rescue = 0
    completion_safety_veto = 0
    for row in controller_rows:
        summary = row.get("action_decomposition", {}).get("decision_summary", {})
        total_decisions += int(summary.get("total_decisions", 0) or 0)
        changed += int(summary.get("action_changed_relative_to_pressure_count", 0) or 0)
        binding += int(summary.get("binding_decision_count", 0) or 0)
        guardrail += int(summary.get("any_phase_component_nonzero_counts", {}).get("guardrail", 0) or 0)
        double_fallback += int(summary.get("double_safety_fallback_count", 0) or 0)
        terminal_fallback += int(summary.get("terminal_completion_fallback_count", 0) or 0)
        double_score_filter += int(summary.get("double_score_safety_filter_count", 0) or 0)
        multi_filter += int(summary.get("multi_baseline_safety_filter_count", 0) or 0)
        hold_only_filter += int(summary.get("hold_only_safety_filter_count", 0) or 0)
        max_hold_filter += int(summary.get("max_hold_safety_filter_count", 0) or 0)
        completion_risk_filter += int(summary.get("completion_risk_filter_count", 0) or 0)
        route_completion_filter += int(summary.get("route_completion_prediction_filter_count", 0) or 0)
        route_demand_filter += int(summary.get("route_demand_completion_filter_count", 0) or 0)
        route_demand_veto += int(summary.get("route_demand_double_score_veto_count", 0) or 0)
        route_horizon_filter += int(summary.get("route_horizon_completion_filter_count", 0) or 0)
        route_horizon_dominance_filter += int(summary.get("route_horizon_dominance_filter_count", 0) or 0)
        terminal_exit_guard += int(summary.get("terminal_exit_protection_guard_count", 0) or 0)
        route_horizon_max_envelope += int(summary.get("route_horizon_max_pressure_envelope_count", 0) or 0)
        route_horizon_core_envelope += int(summary.get("route_horizon_core_baseline_envelope_count", 0) or 0)
        route_horizon_double_envelope += int(summary.get("route_horizon_double_pressure_envelope_count", 0) or 0)
        route_horizon_core_minimax_guard += int(summary.get("route_horizon_core_minimax_guard_count", 0) or 0)
        route_horizon_capacity_rescue_guard += int(summary.get("route_horizon_capacity_rescue_guard_count", 0) or 0)
        route_horizon_capacity_score_envelope += int(summary.get("route_horizon_capacity_score_envelope_count", 0) or 0)
        route_horizon_native_capacity_score_rescue_guard += int(summary.get("route_horizon_native_capacity_score_rescue_guard_count", 0) or 0)
        route_horizon_severe_double_guard += int(summary.get("route_horizon_severe_double_guard_count", 0) or 0)
        route_horizon_pressure_double_conflict_guard += int(summary.get("route_horizon_pressure_double_conflict_guard_count", 0) or 0)
        route_horizon_completion_conflict_guard += int(summary.get("route_horizon_completion_conflict_guard_count", 0) or 0)
        route_horizon_capacity_completion_conflict_guard += int(summary.get("route_horizon_capacity_completion_conflict_guard_count", 0) or 0)
        route_horizon_early_capacity_completion_conflict_guard += int(summary.get("route_horizon_early_capacity_completion_conflict_guard_count", 0) or 0)
        route_horizon_negative_total_completion_conflict_guard += int(summary.get("route_horizon_negative_total_completion_conflict_guard_count", 0) or 0)
        route_horizon_low_total_consensus_completion_guard += int(summary.get("route_horizon_low_total_consensus_completion_guard_count", 0) or 0)
        route_horizon_negative_total_raw_consensus_guard += int(summary.get("route_horizon_negative_total_raw_consensus_guard_count", 0) or 0)
        route_horizon_core_consensus_guard += int(summary.get("route_horizon_core_consensus_guard_count", 0) or 0)
        route_horizon_raw_consensus_guard += int(summary.get("route_horizon_raw_consensus_guard_count", 0) or 0)
        post_completion_veto_double_conflict_guard += int(summary.get("post_completion_veto_double_conflict_guard_count", 0) or 0)
        route_horizon_pressure_safe_guard += int(summary.get("route_horizon_pressure_safe_guard_count", 0) or 0)
        route_horizon_tail_completion_rescue += int(summary.get("route_horizon_tail_completion_rescue_count", 0) or 0)
        completion_safety_veto += int(summary.get("completion_safety_veto_count", 0) or 0)
    return {
        "controller_rows": len(controller_rows),
        "total_decisions": total_decisions,
        "action_changed_relative_to_pressure_count": changed,
        "binding_decision_count": binding,
        "guardrail_activation_count": guardrail,
        "double_safety_fallback_count": double_fallback,
        "terminal_completion_fallback_count": terminal_fallback,
        "double_score_safety_filter_count": double_score_filter,
        "multi_baseline_safety_filter_count": multi_filter,
        "hold_only_safety_filter_count": hold_only_filter,
        "max_hold_safety_filter_count": max_hold_filter,
        "completion_risk_filter_count": completion_risk_filter,
        "route_completion_prediction_filter_count": route_completion_filter,
        "route_demand_completion_filter_count": route_demand_filter,
        "route_demand_double_score_veto_count": route_demand_veto,
        "route_horizon_completion_filter_count": route_horizon_filter,
        "route_horizon_dominance_filter_count": route_horizon_dominance_filter,
        "terminal_exit_protection_guard_count": terminal_exit_guard,
        "route_horizon_max_pressure_envelope_count": route_horizon_max_envelope,
        "route_horizon_core_baseline_envelope_count": route_horizon_core_envelope,
        "route_horizon_double_pressure_envelope_count": route_horizon_double_envelope,
        "route_horizon_core_minimax_guard_count": route_horizon_core_minimax_guard,
        "route_horizon_capacity_rescue_guard_count": route_horizon_capacity_rescue_guard,
        "route_horizon_capacity_score_envelope_count": route_horizon_capacity_score_envelope,
        "route_horizon_native_capacity_score_rescue_guard_count": route_horizon_native_capacity_score_rescue_guard,
        "route_horizon_severe_double_guard_count": route_horizon_severe_double_guard,
        "route_horizon_pressure_double_conflict_guard_count": route_horizon_pressure_double_conflict_guard,
        "route_horizon_completion_conflict_guard_count": route_horizon_completion_conflict_guard,
        "route_horizon_capacity_completion_conflict_guard_count": route_horizon_capacity_completion_conflict_guard,
        "route_horizon_early_capacity_completion_conflict_guard_count": route_horizon_early_capacity_completion_conflict_guard,
        "route_horizon_negative_total_completion_conflict_guard_count": route_horizon_negative_total_completion_conflict_guard,
        "route_horizon_low_total_consensus_completion_guard_count": route_horizon_low_total_consensus_completion_guard,
        "route_horizon_negative_total_raw_consensus_guard_count": route_horizon_negative_total_raw_consensus_guard,
        "route_horizon_core_consensus_guard_count": route_horizon_core_consensus_guard,
        "route_horizon_raw_consensus_guard_count": route_horizon_raw_consensus_guard,
        "post_completion_veto_double_conflict_guard_count": post_completion_veto_double_conflict_guard,
        "route_horizon_pressure_safe_guard_count": route_horizon_pressure_safe_guard,
        "route_horizon_tail_completion_rescue_count": route_horizon_tail_completion_rescue,
        "completion_safety_veto_count": completion_safety_veto,
        "action_change_rate": float(changed / total_decisions) if total_decisions else 0.0,
        "binding_decision_rate": float(binding / total_decisions) if total_decisions else 0.0,
    }


def build_selection_payload(input_payload: dict[str, Any], input_path: Path) -> dict[str, Any]:
    reasons = []
    if input_payload.get("experiment") not in {
        "v1_5_r2_training_execution",
        "v1_5_r3_training_execution",
        "v1_5_r4_training_execution",
        "v1_5_r5_training_execution",
        "v1_5_r6_training_execution",
        "v1_5_r7_training_execution",
        "v1_5_r8_training_execution",
        "v1_5_r9_training_execution",
        "v1_5_r10_training_execution",
        "v1_5_r11_training_execution",
        "v1_5_r12_training_execution",
        "v1_5_r13_training_execution",
        "v1_5_r14_training_execution",
        "v1_5_r15_training_execution",
        "v1_5_r16_training_execution",
        "v1_5_r17_training_execution",
        "v1_5_r18_training_execution",
        "v1_5_r19_training_execution",
        "v1_5_r20_training_execution",
        "v1_5_r21_training_execution",
        "v1_5_r22_training_execution",
        "v1_5_r23_training_execution",
        "v1_5_r24_training_execution",
        "v1_5_r25_training_execution",
        "v1_5_r26_training_execution",
        "v1_5_r27_training_execution",
        "v1_5_r28_training_execution",
        "v1_5_r29_training_execution",
        "v1_5_r30_training_execution",
        "v1_5_r31_training_execution",
        "v1_5_r32_training_execution",
        "v1_5_r33_training_execution",
        "v1_5_r34_training_execution",
        "v1_5_r35_training_execution",
        "v1_5_r36_training_execution",
        "v1_5_r37_training_execution",
        "v1_5_r38_training_execution",
        "v1_5_r39_training_execution",
        "v1_5_r40_training_execution",
        "v1_5_r41_training_execution",
        "v1_5_r42_training_execution",
        "v1_5_r43_training_execution",
        "v1_5_r44_training_execution",
        "v1_5_r45_training_execution",
        "v1_5_r46_training_execution",
        "v1_5_r47_training_execution",
        "v1_5_r48_training_execution",
        "v1_5_r49_training_execution",
        "v1_5_r50_training_execution",
        "v1_5_r51_training_execution",
        "v1_5_r52_training_execution",
        "v1_5_r53_training_execution",
        "v1_5_r54_training_execution",
        "v1_5_r55_training_execution",
        "v1_5_r56_training_execution",
        "v1_5_r57_training_execution",
        "v1_5_r58_training_execution",
        "v1_5_r59_training_execution",
        "v1_5_r60_training_execution",
        "v1_5_r61_training_execution",
        "v1_5_r62_training_execution",
        "v1_5_r63_training_execution",
        "v1_5_r64_training_execution",
        "v1_5_r65_training_execution",
        "v1_5_r66_training_execution",
        "v1_5_r67_training_execution",
        "v1_5_r68_training_execution",
        "v1_5_r69_training_execution",
        "v1_5_r70_training_execution",
        "v1_5_r71_training_execution",
        "v1_5_r72_training_execution",
        "v1_5_r73_training_execution",
        "v1_5_r74_training_execution",
        "v1_5_r75_training_execution",
        "v1_5_r76_training_execution",
        "v1_5_r77_training_execution",
        "v1_5_r78_training_execution",
        "v1_5_r79_training_execution",
        "v1_5_r80_training_execution",
        "v1_5_r81_training_execution",
        "v1_5_r82_training_execution",
        "v1_5_r83_training_execution",
        "v1_5_r84_training_execution",
        "v1_5_r85_training_execution",
        "v1_5_r86_training_execution",
        "v1_5_r87_training_execution",
        "v1_5_r88_training_execution",
        "v1_5_r89_training_execution",
        "v1_5_r90_training_execution",
        "v1_5_r91_training_execution",
        "v1_5_r92_training_execution",
        "v1_5_r93_training_execution",
        "v1_5_r94_training_execution",
        "v1_5_r95_training_execution",
        "v1_5_r96_training_execution",
        "v1_5_r97_training_execution",
        "v1_5_r98_training_execution",
        "v1_5_r99_training_execution",
        "v1_5_r100_training_execution",
        "v1_5_r101_training_execution",
        "v1_5_r102_training_execution",
        "v1_5_r103_training_execution",
        "v1_5_r104_training_execution",
        "v1_5_r105_training_execution",
        "v1_5_r106_training_execution",
        "v1_5_r107_training_execution",
        "v1_5_r108_training_execution",
        "v1_5_r109_training_execution",
        "v1_5_r110_training_execution",
        "v1_5_r111_training_execution",
        "v1_5_r112_training_execution",
        "v1_5_r113_training_execution",
        "v1_5_r114_training_execution",
    }:
        reasons.append("input artifact is not a supported v1.5 training execution")
    if input_payload.get("claim_ready"):
        reasons.append("training input unexpectedly reports claim_ready=true")
    row_audit = input_payload.get("row_audit", {}) if isinstance(input_payload.get("row_audit"), dict) else {}
    composite, harms, row_reasons = summarize_training_rows(input_payload)
    reasons.extend(row_reasons)
    mechanism = mechanism_summary(input_payload)
    core_harms = [harm for harm in harms if str(harm.get("baseline")) in CORE_STRONG_BASELINES]
    core_composite_by_baseline: dict[str, list[float]] = {baseline: [] for baseline in sorted(CORE_STRONG_BASELINES)}
    for item in composite:
        baseline = str(item.get("baseline"))
        if baseline in core_composite_by_baseline:
            core_composite_by_baseline[baseline].append(float(item.get("paired_difference", 0.0)))
    core_composite_means = {
        baseline: float(sum(values) / len(values))
        for baseline, values in core_composite_by_baseline.items()
        if values
    }
    missing_core_composite = sorted(
        baseline for baseline in CORE_STRONG_BASELINES if baseline not in core_composite_means
    )
    nonpositive_core_composite = sorted(
        baseline
        for baseline, mean in core_composite_means.items()
        if mean <= 0.0
    )
    low_action_separation = mechanism["controller_rows"] > 0 and mechanism["action_change_rate"] < 0.05
    if core_harms:
        reasons.append("training rows show safety-guard harm against strong baselines")
    if low_action_separation:
        reasons.append("guarded r2 action separation from pressure is below 5% on completed training rows")

    if core_harms or low_action_separation:
        status = "REJECTED"
        decision = f"reject_{str(input_payload.get('controller_id', 'candidate'))}"
    elif input_payload.get("all_rows_executed") is True and missing_core_composite:
        reasons.append(f"training rows are missing core composite comparisons: {missing_core_composite}")
        status = "REJECTED"
        decision = f"reject_{str(input_payload.get('controller_id', 'candidate'))}"
    elif input_payload.get("all_rows_executed") is True and nonpositive_core_composite:
        reasons.append(f"training composite signal is not positive against core baselines: {nonpositive_core_composite}")
        status = "REJECTED"
        decision = f"reject_{str(input_payload.get('controller_id', 'candidate'))}"
    elif input_payload.get("all_rows_executed") is True and not reasons:
        status = "SELECTED_PENDING_CONFIRMATORY_PROTOCOL"
        decision = f"select_{str(input_payload.get('controller_id', 'candidate'))}_for_fresh_confirmatory_protocol"
    else:
        status = "INCONCLUSIVE"
        decision = "continue_training_execution"

    selection_experiment = str(input_payload.get("experiment", "v1_5_r2_training_execution")).replace(
        "_execution",
        "_selection",
    )
    return {
        "experiment": selection_experiment,
        "status": status,
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": False,
        "input_artifact": str(input_path),
        "input_status": input_payload.get("status"),
        "training_protocol_fingerprint": input_payload.get("training_protocol_fingerprint"),
        "controller_id": input_payload.get("controller_id"),
        "row_audit": row_audit,
        "decision": decision,
        "mechanism_summary": mechanism,
        "core_composite_mean_differences": core_composite_means,
        "primary_composite_training_results": composite,
        "safety_harms": harms,
        "reasons": list(dict.fromkeys(reasons)),
        "claim_scope": {
            "closed_loop_superiority_claim_allowed": False,
            "why": "training selection can reject or select a candidate for a future protocol, but cannot itself prove a claim",
        },
    }


def write_selection(input_path: Path, out_path: Path) -> dict[str, Any]:
    payload = build_selection_payload(load_input(input_path), input_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_selection(Path(args.input), Path(args.out))
    print(json.dumps({"status": payload["status"], "out": args.out, "decision": payload["decision"]}, indent=2))
    if args.strict and payload["status"] != "SELECTED_PENDING_CONFIRMATORY_PROTOCOL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
