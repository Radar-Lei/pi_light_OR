#!/usr/bin/env python3
"""Rank v1.4 workstream pilots and lock at most one Gate C candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_phase11_paired_evidence import (
    BINDING_EVIDENCE_SCENARIOS,
    DEFAULT_DEMAND_MULTIPLIERS,
    DEFAULT_MAIN_SEEDS,
    GATE_C_PRIMARY_METRICS,
    PROPOSED_CONTROLLER,
    REQUIRED_GATE_C_COMPARATORS,
)
from run_v14_failure_diagnostics import DEFAULT_OUT as DEFAULT_DIAGNOSTICS
from run_v14_failure_diagnostics import load_json
from run_v14_workstream_pilots import DEFAULT_INDEX

DEFAULT_OUT = "experiments/dual_sensitivity/v1_4_candidate_convergence.json"
DEFAULT_PROTOCOL = "experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json"
DEFAULT_REPORT = "experiments/dual_sensitivity/v1_4_candidate_convergence.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnostics", default=DEFAULT_DIAGNOSTICS)
    parser.add_argument("--pilot-index", default=DEFAULT_INDEX)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--protocol", default=DEFAULT_PROTOCOL)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def load_pilot_artifacts(index: dict[str, Any]) -> list[dict[str, Any]]:
    pilots = []
    for item in index.get("artifacts", []):
        path = item.get("path")
        if path:
            pilots.append(load_json(path))
    return pilots


def score_pilot(pilot: dict[str, Any]) -> dict[str, Any]:
    criteria = pilot.get("selection_criteria_results", {})
    spec = pilot.get("spec", {}) if isinstance(pilot.get("spec"), dict) else {}
    action_decomposition = pilot.get("action_decomposition", {}) if isinstance(pilot.get("action_decomposition"), dict) else {}
    provenance = pilot.get("provenance", {}) if isinstance(pilot.get("provenance"), dict) else {}
    points = 0
    points += 3 if criteria.get("non_worsening_behavior") == "pass" else 1 if criteria.get("non_worsening_behavior") == "partial" else 0
    points += 2 if criteria.get("strict_positive_signal") == "pass" else 1 if criteria.get("strict_positive_signal") == "partial" else 0
    points += 3 if criteria.get("binding_activation") == "pass" else 1 if criteria.get("binding_activation") == "partial" else 0
    points += 2 if criteria.get("auditability") == "pass" else 0
    points += 2 if criteria.get("implementation_reproducibility") == "pass" else 1 if criteria.get("implementation_reproducibility") == "partial" else 0
    eligible = (
        pilot.get("status") == "candidate"
        and pilot.get("claim_ready") is False
        and criteria.get("non_worsening_behavior") == "pass"
        and criteria.get("binding_activation") in {"pass", "partial"}
        and criteria.get("auditability") == "pass"
        and criteria.get("implementation_reproducibility") == "pass"
    )
    return {
        "workstream_id": pilot.get("workstream_id"),
        "candidate_id": pilot.get("candidate_id"),
        "candidate_controller_id": pilot.get("candidate_controller_id"),
        "status": pilot.get("status"),
        "score": points,
        "eligible_for_lock": eligible,
        "criteria": criteria,
        "reasons": pilot.get("reasons", []),
        "mechanism_description": spec.get("scope"),
        "changed_score_or_objective_terms": spec.get("changed_score_or_objective_terms", []),
        "action_decomposition_schema": action_decomposition.get("schema"),
        "reproducible_implementation_pointer": provenance.get("command"),
        "artifact": provenance.get("output_artifact"),
    }


def protocol_fingerprint(protocol: dict[str, Any]) -> str:
    encoded = json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_protocol(selected: dict[str, Any] | None, diagnostics: dict[str, Any]) -> dict[str, Any]:
    candidate_controller = selected.get("candidate_controller_id") if selected else None
    candidate_id = selected.get("candidate_id") if selected else None
    protocol = {
        "experiment": "v1_4_locked_gate_c_protocol",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "LOCKED" if selected else "NO_CANDIDATE_LOCKED",
        "claim_ready": False,
        "selected_candidate_id": candidate_id,
        "selected_controller_id": candidate_controller,
        "fallback_controller_id": PROPOSED_CONTROLLER,
        "required_comparators": list(REQUIRED_GATE_C_COMPARATORS),
        "binding_scenarios": list(BINDING_EVIDENCE_SCENARIOS),
        "primary_metrics": list(GATE_C_PRIMARY_METRICS),
        "demand_multipliers": list(DEFAULT_DEMAND_MULTIPLIERS),
        "seeds": list(DEFAULT_MAIN_SEEDS),
        "profile": "main",
        "steps": 3600,
        "warmup": 900,
        "pre_confirmation_lock": True,
        "source_diagnostics": diagnostics.get("source_artifacts", {}),
        "fail_closed_rules": [
            "missing required comparator",
            "non-PASSED source artifact",
            "bounded harm in any primary metric family",
            "missing or malformed action decomposition",
            "pilot artifact imported as final evidence",
        ],
    }
    stable = dict(protocol)
    stable.pop("generated_at", None)
    protocol["spec_fingerprint"] = protocol_fingerprint(stable)
    return protocol


def build_outputs(diagnostics: dict[str, Any], pilot_index: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    pilots = load_pilot_artifacts(pilot_index)
    rankings = sorted((score_pilot(pilot) for pilot in pilots), key=lambda item: (-item["score"], str(item["workstream_id"])))
    eligible = [item for item in rankings if item["eligible_for_lock"]]
    selected = eligible[0] if eligible else None
    rejected = []
    for item in rankings:
        if selected and item["candidate_id"] == selected["candidate_id"]:
            continue
        rejected.append(
            {
                "candidate_id": item["candidate_id"],
                "workstream_id": item["workstream_id"],
                "reason": "lower ranked than locked candidate" if item["eligible_for_lock"] else "did not satisfy required lock criteria",
                "score": item["score"],
            }
        )
    protocol = build_protocol(selected, diagnostics)
    convergence = {
        "experiment": "v1_4_candidate_convergence",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASSED",
        "requirements_covered": ["SELECT-01", "SELECT-02", "SELECT-03", "LOCK-01"],
        "claim_ready": False,
        "selection_rule": "Promote at most one candidate before Phase 17 confirmation; pilots remain exploratory.",
        "rankings": rankings,
        "selected_candidate": selected,
        "rejected_routes": rejected,
        "locked_protocol_path": DEFAULT_PROTOCOL,
        "locked_protocol_fingerprint": protocol["spec_fingerprint"],
        "at_most_one_candidate_promoted": len([selected] if selected else []) <= 1,
    }
    return convergence, protocol


def render_report(convergence: dict[str, Any], protocol: dict[str, Any]) -> str:
    lines = [
        "# v1.4 Candidate Convergence",
        "",
        f"Status: `{convergence['status']}`",
        f"Protocol status: `{protocol['status']}`",
        f"Fingerprint: `{protocol['spec_fingerprint']}`",
        "",
        "## Rankings",
        "",
        "| Rank | Workstream | Candidate | Status | Score | Lock Eligible |",
        "|---:|---|---|---|---:|---|",
    ]
    for idx, item in enumerate(convergence["rankings"], start=1):
        lines.append(
            f"| {idx} | {item['workstream_id']} | {item['candidate_id']} | {item['status']} | {item['score']} | {item['eligible_for_lock']} |"
        )
    lines.extend(["", "## Selected Candidate", "", json.dumps(convergence["selected_candidate"], indent=2), ""])
    return "\n".join(lines)


def write_outputs(diagnostics_path: Path, pilot_index_path: Path, out_path: Path, protocol_path: Path, report_path: Path) -> dict[str, Any]:
    diagnostics = load_json(diagnostics_path)
    pilot_index = load_json(pilot_index_path)
    convergence, protocol = build_outputs(diagnostics, pilot_index)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    protocol_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(convergence, indent=2), encoding="utf-8")
    protocol_path.write_text(json.dumps(protocol, indent=2), encoding="utf-8")
    report_path.write_text(render_report(convergence, protocol), encoding="utf-8")
    return convergence


def main() -> None:
    args = parse_args()
    convergence = write_outputs(Path(args.diagnostics), Path(args.pilot_index), Path(args.out), Path(args.protocol), Path(args.report))
    print(json.dumps({"out": args.out, "status": convergence["status"], "selected": convergence["selected_candidate"]}, indent=2))


if __name__ == "__main__":
    main()
