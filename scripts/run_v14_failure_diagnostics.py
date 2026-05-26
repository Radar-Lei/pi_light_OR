#!/usr/bin/env python3
"""Build v1.4 diagnostics from the failed v1.3 Gate C artifacts."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_phase11_paired_evidence import (
    BINDING_EVIDENCE_SCENARIOS,
    GATE_C_PRIMARY_METRICS,
    PROPOSED_CONTROLLER,
    REQUIRED_GATE_C_COMPARATORS,
)

DEFAULT_GATE_C = "experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json"
DEFAULT_PHASE11 = "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_4_failure_diagnostics.json"
DEFAULT_REPORT = "experiments/dual_sensitivity/v1_4_failure_diagnostics.md"

WORKSTREAMS = {
    "v1-4-score-controller": {
        "scope": "Change the live controller score decomposition while preserving auditable action components.",
        "candidate_controller_id": "finite_storage_primal_dual_v1_4_score",
        "artifact_path": "experiments/dual_sensitivity/v1_4_workstreams/v1-4-score-controller-pilot.json",
    },
    "v1-4-objective-weights": {
        "scope": "Retune objective component weights and penalties without changing the confirmation protocol after lock.",
        "candidate_controller_id": "finite_storage_primal_dual_v1_4_weighted",
        "artifact_path": "experiments/dual_sensitivity/v1_4_workstreams/v1-4-objective-weights-pilot.json",
    },
    "v1-4-scenario-diagnostics": {
        "scope": "Audit whether scenario design or binding activation explains the v1.3 failure.",
        "candidate_controller_id": None,
        "artifact_path": "experiments/dual_sensitivity/v1_4_workstreams/v1-4-scenario-diagnostics-pilot.json",
    },
    "v1-4-symbolic-policy": {
        "scope": "Test whether a compressed symbolic policy can keep auditability while improving action choices.",
        "candidate_controller_id": "finite_storage_symbolic_v1_4",
        "artifact_path": "experiments/dual_sensitivity/v1_4_workstreams/v1-4-symbolic-policy-pilot.json",
    },
}

SELECTION_CRITERIA = [
    {
        "id": "non_worsening_behavior",
        "description": "Pilot must reduce bounded-harm counts or show no new bounded harm against strong baselines.",
        "required_for_promotion": True,
    },
    {
        "id": "strict_positive_signal",
        "description": "Strict-positive signals are useful only when paired with non-worsening primary metrics.",
        "required_for_promotion": False,
    },
    {
        "id": "binding_activation",
        "description": "Action decomposition must show finite-storage/spillback/switching terms changing decisions.",
        "required_for_promotion": True,
    },
    {
        "id": "auditability",
        "description": "Pilot artifacts must expose score/objective terms and action decomposition.",
        "required_for_promotion": True,
    },
    {
        "id": "implementation_reproducibility",
        "description": "Candidate must have deterministic command, inputs, and artifact paths.",
        "required_for_promotion": True,
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-c", default=DEFAULT_GATE_C)
    parser.add_argument("--phase11", default=DEFAULT_PHASE11)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def metric_results(gate_c: dict[str, Any]) -> list[dict[str, Any]]:
    rule = gate_c.get("gate_c_primary_metrics_v1")
    if not isinstance(rule, dict):
        raise ValueError("Gate C artifact is missing gate_c_primary_metrics_v1")
    rows = rule.get("metric_results")
    if not isinstance(rows, list):
        raise ValueError("Gate C artifact is missing metric_results")
    return [row for row in rows if isinstance(row, dict)]


def bucket_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, float, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            str(row.get("scenario_tag")),
            float(row.get("demand_multiplier")),
            str(row.get("comparator")),
            str(row.get("metric")),
        )
        grouped[key].append(row)

    summary = []
    for (scenario, demand, comparator, metric), items in sorted(grouped.items()):
        classifications = Counter(str(item.get("classification", "unknown")) for item in items)
        strict_positive = sum(1 for item in items if item.get("strict_positive_signal") is True)
        mean_diffs = [float(item.get("mean_paired_difference", 0.0)) for item in items if item.get("mean_paired_difference") is not None]
        summary.append(
            {
                "scenario_tag": scenario,
                "demand_multiplier": demand,
                "comparator": comparator,
                "metric": metric,
                "classification_counts": dict(sorted(classifications.items())),
                "strict_positive_signal_count": strict_positive,
                "mean_paired_difference_avg": sum(mean_diffs) / len(mean_diffs) if mean_diffs else None,
                "evidence_role": "claim_informative_gate_c_metric",
            }
        )
    return summary


def action_activation_summary(phase11: dict[str, Any]) -> dict[str, Any]:
    proposed_rows = [
        row
        for row in phase11.get("scenario_results", [])
        if isinstance(row, dict) and row.get("controller") == PROPOSED_CONTROLLER
    ]
    decisions = 0
    finite_storage_changed = 0
    nonzero_components: Counter[str] = Counter()
    for row in proposed_rows:
        action = row.get("action_decomposition")
        if not isinstance(action, dict):
            continue
        tls_map = action.get("last_decision_by_tls")
        if not isinstance(tls_map, dict):
            continue
        for tls in tls_map.values():
            if not isinstance(tls, dict):
                continue
            decisions += 1
            if tls.get("pressure_action") != tls.get("finite_storage_action"):
                finite_storage_changed += 1
            for phase in (tls.get("phase_scores") or {}).values():
                totals = phase.get("component_totals") if isinstance(phase, dict) else None
                if not isinstance(totals, dict):
                    continue
                for key, value in totals.items():
                    if key != "total" and isinstance(value, (int, float)) and abs(float(value)) > 1e-9:
                        nonzero_components[str(key)] += 1
    return {
        "proposed_rows": len(proposed_rows),
        "audited_tls_decisions": decisions,
        "finite_storage_decision_changes": finite_storage_changed,
        "finite_storage_change_rate": finite_storage_changed / decisions if decisions else 0.0,
        "nonzero_component_counts": dict(sorted(nonzero_components.items())),
    }


def infer_failure_drivers(rows: list[dict[str, Any]], activation: dict[str, Any]) -> list[dict[str, Any]]:
    classifications = Counter(str(row.get("classification", "unknown")) for row in rows)
    metrics_by_class: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        metrics_by_class[str(row.get("classification", "unknown"))][str(row.get("metric"))] += 1

    drivers = []
    bounded_harm = classifications.get("bounded_harm", 0)
    non_worsening = classifications.get("non_worsening", 0)
    inconclusive = classifications.get("inconclusive", 0)
    strict_positive = sum(1 for row in rows if row.get("strict_positive_signal") is True)
    change_rate = float(activation.get("finite_storage_change_rate", 0.0))
    component_counts = activation.get("nonzero_component_counts", {})

    drivers.append(
        {
            "driver": "controller_action_weakness",
            "level": "high" if bounded_harm > non_worsening else "medium",
            "evidence": f"{bounded_harm} bounded-harm metric comparisons versus {non_worsening} non-worsening comparisons.",
        }
    )
    drivers.append(
        {
            "driver": "objective_mismatch",
            "level": "medium" if metrics_by_class["bounded_harm"].get("total_delay", 0) or metrics_by_class["bounded_harm"].get("penalized_avg_travel_time", 0) else "low",
            "evidence": "Bounded harm appears in travel-time/delay metrics, so objective tuning remains a plausible route.",
        }
    )
    drivers.append(
        {
            "driver": "insufficient_binding_activation",
            "level": "high" if change_rate < 0.05 else "medium",
            "evidence": f"Finite-storage decisions differed from pressure in {change_rate:.3%} of audited TLS decisions; nonzero components: {component_counts}.",
        }
    )
    drivers.append(
        {
            "driver": "scenario_design",
            "level": "medium" if inconclusive > bounded_harm else "low",
            "evidence": f"{inconclusive} metric comparisons were inconclusive, so scenario or metric sensitivity remains unresolved.",
        }
    )
    drivers.append(
        {
            "driver": "baseline_parity",
            "level": "medium" if strict_positive < 10 else "low",
            "evidence": f"Only {strict_positive} strict-positive signals were present against strong max-pressure-style comparators.",
        }
    )
    return drivers


def build_payload(gate_c: dict[str, Any], phase11: dict[str, Any], gate_path: Path, phase11_path: Path) -> dict[str, Any]:
    rows = metric_results(gate_c)
    classifications = Counter(str(row.get("classification", "unknown")) for row in rows)
    activation = action_activation_summary(phase11)
    workstreams = []
    for workstream_id, spec in WORKSTREAMS.items():
        workstreams.append(
            {
                "workstream_id": workstream_id,
                "scope": spec["scope"],
                "status": "ready_for_pilot",
                "candidate_controller_id": spec["candidate_controller_id"],
                "artifact_path": spec["artifact_path"],
                "claim_ready": False,
                "evidence_boundary": "exploratory_pilot_only_not_gate_c_evidence",
            }
        )
    return {
        "experiment": "v1_4_failure_diagnostics",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASSED",
        "requirements_covered": ["DIAG-01", "DIAG-02", "DIAG-03", "WS-01"],
        "source_artifacts": {
            "phase11_gate_c": str(gate_path),
            "phase11_long_horizon": str(phase11_path),
            "gate_c_status": gate_c.get("status"),
            "phase11_status": phase11.get("status"),
        },
        "overall_classification_counts": dict(sorted(classifications.items())),
        "strict_positive_signal_count": sum(1 for row in rows if row.get("strict_positive_signal") is True),
        "required_binding_scenarios": list(BINDING_EVIDENCE_SCENARIOS),
        "required_comparators": list(REQUIRED_GATE_C_COMPARATORS),
        "primary_metrics": list(GATE_C_PRIMARY_METRICS),
        "metric_bucket_summary": bucket_rows(rows),
        "action_activation_summary": activation,
        "failure_driver_assessment": infer_failure_drivers(rows, activation),
        "claim_boundary": {
            "claim_ready": False,
            "claim_informative_rows": len(rows),
            "context_only_rows": len(gate_c.get("slack_regime_recovery_or_context", [])),
            "non_evidence_rows": len(gate_c.get("not_evidence", [])),
            "rule": "v1.3 failed Gate C; diagnostics and v1.4 pilots cannot be imported as final superiority evidence.",
        },
        "workstreams": workstreams,
        "selection_criteria": SELECTION_CRITERIA,
        "validation_commands": [
            "python scripts/run_v14_failure_diagnostics.py",
            "python scripts/run_v14_workstream_pilots.py --workstream all",
            "python scripts/run_v14_candidate_convergence.py",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# v1.4 Failure Diagnostics",
        "",
        f"Status: `{payload['status']}`",
        f"Source Gate C status: `{payload['source_artifacts']['gate_c_status']}`",
        f"Source Phase 11 status: `{payload['source_artifacts']['phase11_status']}`",
        "",
        "## Classification Summary",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    for key, value in payload["overall_classification_counts"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            f"Strict-positive signals: {payload['strict_positive_signal_count']}",
            "",
            "## Failure Drivers",
            "",
            "| Driver | Level | Evidence |",
            "|---|---|---|",
        ]
    )
    for item in payload["failure_driver_assessment"]:
        lines.append(f"| {item['driver']} | {item['level']} | {item['evidence']} |")
    lines.extend(["", "## Workstreams", "", "| Workstream | Status | Claim Ready | Artifact |", "|---|---|---|---|"])
    for item in payload["workstreams"]:
        lines.append(f"| {item['workstream_id']} | {item['status']} | {item['claim_ready']} | `{item['artifact_path']}` |")
    lines.extend(["", "## Claim Boundary", "", payload["claim_boundary"]["rule"], ""])
    return "\n".join(lines)


def write_outputs(gate_path: Path, phase11_path: Path, out_path: Path, report_path: Path) -> dict[str, Any]:
    gate_c = load_json(gate_path)
    phase11 = load_json(phase11_path)
    payload = build_payload(gate_c, phase11, gate_path, phase11_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_outputs(Path(args.gate_c), Path(args.phase11), Path(args.out), Path(args.report))
    print(json.dumps({"out": args.out, "report": args.report, "status": payload["status"]}, indent=2))


if __name__ == "__main__":
    main()
