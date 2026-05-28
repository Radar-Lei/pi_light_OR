#!/usr/bin/env python3
"""Audit early v1.5 holdout rows for fail-closed method risk signals."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_EVIDENCE = "experiments/dual_sensitivity/v1_5_binding_paired_evidence.json"
DEFAULT_ACTIVATION_AUDIT = "experiments/dual_sensitivity/v1_5_binding_protocol_activation_audit.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_binding_early_holdout_risk.json"
REQUIREMENTS_COVERED = ["V15-EARLY-01", "V15-CLAIM-01"]
CORE_STRONG_BASELINES = {
    "max_pressure",
    "capacity_aware_pressure",
    "finite_storage_double_pressure",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", default=DEFAULT_EVIDENCE)
    parser.add_argument("--activation-audit", default=DEFAULT_ACTIVATION_AUDIT)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--min-harm-seeds", type=int, default=2)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _harm_seed_count(result: dict[str, Any]) -> int:
    seeds = {int(item["seed"]) for item in result.get("harms", []) if isinstance(item, dict) and "seed" in item}
    return len(seeds)


def summarize_safety_harms(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for result in evidence.get("safety_guard_results", []):
        if not isinstance(result, dict) or result.get("passed") is True:
            continue
        summaries.append(
            {
                "scenario_tag": result.get("scenario_tag"),
                "demand_multiplier": result.get("demand_multiplier"),
                "baseline": result.get("baseline"),
                "metric": result.get("metric"),
                "harm_count": int(result.get("harm_count", 0) or 0),
                "harm_seed_count": _harm_seed_count(result),
                "practical_harm_tolerance": result.get("practical_harm_tolerance"),
            }
        )
    return summaries


def summarize_primary_results(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for result in evidence.get("primary_composite_results", []):
        if not isinstance(result, dict):
            continue
        summaries.append(
            {
                "scenario_tag": result.get("scenario_tag"),
                "demand_multiplier": result.get("demand_multiplier"),
                "baseline": result.get("baseline"),
                "n_seeds": result.get("n_seeds"),
                "mean_paired_difference": result.get("mean_paired_difference"),
                "classification": result.get("classification"),
                "strict_positive_signal": result.get("strict_positive_signal"),
            }
        )
    return summaries


def build_risk_payload(
    evidence: dict[str, Any],
    activation_audit: dict[str, Any],
    evidence_path: Path,
    activation_path: Path,
    *,
    min_harm_seeds: int = 2,
) -> dict[str, Any]:
    safety_harms = summarize_safety_harms(evidence)
    primary = summarize_primary_results(evidence)
    harmful_core_baselines = sorted(
        {
            str(item["baseline"])
            for item in safety_harms
            if str(item.get("baseline")) in CORE_STRONG_BASELINES and int(item.get("harm_seed_count", 0)) >= min_harm_seeds
        }
    )
    by_baseline_metric: dict[tuple[str, str], int] = defaultdict(int)
    for item in safety_harms:
        by_baseline_metric[(str(item.get("baseline")), str(item.get("metric")))] += int(item.get("harm_count", 0))

    activation_passed = activation_audit.get("status") == "PASSED"
    early_safety_failure = bool(harmful_core_baselines)
    reasons = []
    if activation_passed:
        reasons.append("storage-binding mechanism audit passed, so harms are not explained by a non-binding protocol")
    else:
        reasons.append(f"activation audit status is {activation_audit.get('status')}, not PASSED")
    if early_safety_failure:
        reasons.append(
            "safety guards show repeated practical harm against strong baselines before full holdout completion"
        )
    if evidence.get("claim_ready"):
        reasons.append("paired evidence unexpectedly reports claim_ready=true")

    status = "FAILED" if activation_passed and early_safety_failure else "INCONCLUSIVE"
    recommendation = (
        "stop current full binding holdout for method revision; do not tune on these holdout seeds and reuse the same protocol"
        if status == "FAILED"
        else "continue evidence collection or inspect activation before making method changes"
    )

    return {
        "experiment": "v1_5_binding_early_holdout_risk",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requirements_covered": REQUIREMENTS_COVERED,
        "claim_ready": False,
        "input_evidence": str(evidence_path),
        "input_activation_audit": str(activation_path),
        "evidence_status": evidence.get("status"),
        "activation_status": activation_audit.get("status"),
        "locked_protocol_fingerprint": evidence.get("locked_protocol_fingerprint"),
        "min_harm_seeds": min_harm_seeds,
        "activation_summary": activation_audit.get("summary", {}),
        "primary_composite_summary": primary,
        "safety_harm_summary": safety_harms,
        "harm_totals_by_baseline_metric": [
            {"baseline": baseline, "metric": metric, "harm_count": count}
            for (baseline, metric), count in sorted(by_baseline_metric.items())
        ],
        "harmful_core_baselines": harmful_core_baselines,
        "reasons": reasons,
        "recommendation": recommendation,
        "claim_scope": {
            "closed_loop_superiority_claim_allowed": False,
            "why": "early locked-holdout rows show repeated safety-guard harm against strong baselines",
            "required_before_new_claim": [
                "method revision outside this holdout evidence",
                "new or explicitly superseding locked protocol",
                "fresh paired evidence with passing safety guards and primary endpoint",
            ],
        },
    }


def write_audit(evidence_path: Path, activation_path: Path, out_path: Path, *, min_harm_seeds: int) -> dict[str, Any]:
    payload = build_risk_payload(
        load_json(evidence_path),
        load_json(activation_path),
        evidence_path,
        activation_path,
        min_harm_seeds=min_harm_seeds,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_audit(
        Path(args.evidence),
        Path(args.activation_audit),
        Path(args.out),
        min_harm_seeds=args.min_harm_seeds,
    )
    print(json.dumps({"status": payload["status"], "out": args.out, "claim_ready": payload["claim_ready"]}, indent=2))
    if args.strict and payload["status"] != "FAILED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
