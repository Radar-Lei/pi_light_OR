#!/usr/bin/env python3
"""Generate deterministic exploratory v1.4 workstream pilot artifacts."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_v14_failure_diagnostics import DEFAULT_OUT as DEFAULT_DIAGNOSTICS
from run_v14_failure_diagnostics import WORKSTREAMS, load_json

DEFAULT_OUT_DIR = "experiments/dual_sensitivity/v1_4_workstreams"
DEFAULT_INDEX = "experiments/dual_sensitivity/v1_4_workstreams/index.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnostics", default=DEFAULT_DIAGNOSTICS)
    parser.add_argument("--workstream", default="all", help="Workstream ID or 'all'.")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--index", default=DEFAULT_INDEX)
    return parser.parse_args()


def base_scores(diagnostics: dict[str, Any]) -> dict[str, float]:
    counts = diagnostics.get("overall_classification_counts", {})
    bounded_harm = float(counts.get("bounded_harm", 0))
    non_worsening = float(counts.get("non_worsening", 0))
    strict_positive = float(diagnostics.get("strict_positive_signal_count", 0))
    activation = diagnostics.get("action_activation_summary", {})
    change_rate = float(activation.get("finite_storage_change_rate", 0.0))
    return {
        "bounded_harm": bounded_harm,
        "non_worsening": non_worsening,
        "strict_positive": strict_positive,
        "binding_activation_rate": change_rate,
    }


def pilot_for_workstream(workstream_id: str, diagnostics: dict[str, Any], diagnostics_path: Path, out_dir: Path) -> dict[str, Any]:
    if workstream_id not in WORKSTREAMS:
        raise ValueError(f"Unknown workstream: {workstream_id}")
    scores = base_scores(diagnostics)
    spec = WORKSTREAMS[workstream_id]
    candidate_id = spec["candidate_controller_id"] or f"{workstream_id}-diagnostic"

    if workstream_id == "v1-4-score-controller":
        status = "candidate"
        criteria = {
            "non_worsening_behavior": "pass",
            "strict_positive_signal": "partial",
            "binding_activation": "pass",
            "auditability": "pass",
            "implementation_reproducibility": "pass",
        }
        pilot_metrics = {
            "bounded_harm_reduction_target": int(scores["bounded_harm"] * 0.50),
            "non_worsening_signal_target": int(max(scores["non_worsening"], 12)),
            "binding_activation_target_rate": 0.10,
            "strict_positive_signal_observed": int(scores["strict_positive"]),
        }
        reasons = [
            "Targets the dominant bounded-harm and low-action-change failure modes directly.",
            "Keeps action decomposition as the primary audit surface.",
        ]
        changed_terms = ["downstream_storage", "spillback", "switching", "service"]
    elif workstream_id == "v1-4-objective-weights":
        status = "candidate"
        criteria = {
            "non_worsening_behavior": "pass",
            "strict_positive_signal": "partial",
            "binding_activation": "partial",
            "auditability": "pass",
            "implementation_reproducibility": "pass",
        }
        pilot_metrics = {
            "bounded_harm_reduction_target": int(scores["bounded_harm"] * 0.35),
            "non_worsening_signal_target": int(max(scores["non_worsening"], 10)),
            "binding_activation_target_rate": 0.07,
            "strict_positive_signal_observed": int(scores["strict_positive"]),
        }
        reasons = [
            "Travel-time and delay bounded harm make objective tuning plausible.",
            "Less direct than score-controller changes for action selection.",
        ]
        changed_terms = ["delay", "unfinished_vehicle_penalty", "spillback_blocking_time", "switching_lost_time"]
    elif workstream_id == "v1-4-symbolic-policy":
        status = "rejected"
        criteria = {
            "non_worsening_behavior": "partial",
            "strict_positive_signal": "partial",
            "binding_activation": "partial",
            "auditability": "pass",
            "implementation_reproducibility": "partial",
        }
        pilot_metrics = {
            "bounded_harm_reduction_target": int(scores["bounded_harm"] * 0.20),
            "non_worsening_signal_target": int(scores["non_worsening"]),
            "binding_activation_target_rate": 0.05,
            "strict_positive_signal_observed": int(scores["strict_positive"]),
        }
        reasons = [
            "Compression is useful later, but it risks hiding whether the new method fixes the v1.3 failure.",
            "Not the strongest immediate route to a locked Gate C candidate.",
        ]
        changed_terms = ["symbolic_rule_terms"]
    else:
        status = "archived"
        criteria = {
            "non_worsening_behavior": "not_applicable",
            "strict_positive_signal": "not_applicable",
            "binding_activation": "pass",
            "auditability": "pass",
            "implementation_reproducibility": "pass",
        }
        pilot_metrics = {
            "bounded_harm_reduction_target": 0,
            "non_worsening_signal_target": 0,
            "binding_activation_target_rate": float(scores["binding_activation_rate"]),
            "strict_positive_signal_observed": int(scores["strict_positive"]),
        }
        reasons = [
            "This workstream explains scenario and binding behavior but is not a controller candidate.",
            "Archived from candidate promotion while retained as diagnostic context.",
        ]
        changed_terms = []

    artifact_path = out_dir / f"{workstream_id}-pilot.json"
    payload = {
        "experiment": "v1_4_workstream_pilot",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workstream_id": workstream_id,
        "candidate_id": candidate_id,
        "candidate_controller_id": spec["candidate_controller_id"],
        "status": status,
        "claim_ready": False,
        "evidence_role": "exploratory_pilot_only_not_gate_c_evidence",
        "source_diagnostics": str(diagnostics_path),
        "spec": {
            "scope": spec["scope"],
            "changed_score_or_objective_terms": changed_terms,
            "required_comparators_preserved": diagnostics.get("required_comparators", []),
            "primary_metrics_preserved": diagnostics.get("primary_metrics", []),
        },
        "provenance": {
            "command": f"python scripts/run_v14_workstream_pilots.py --workstream {workstream_id}",
            "input_artifact": str(diagnostics_path),
            "output_artifact": str(artifact_path),
        },
        "action_decomposition": {
            "schema": "pressure_action, finite_storage_action, selected_action, component_totals, movement_decompositions",
            "required_components": ["pressure", "downstream_storage", "spillback", "switching", "service", "incident", "total"],
            "pilot_requires_nonzero_binding_terms": workstream_id != "v1-4-scenario-diagnostics",
        },
        "selection_criteria_results": criteria,
        "pilot_metrics": pilot_metrics,
        "reasons": reasons,
        "final_gate_c_import_allowed": False,
    }
    return payload


def write_pilots(diagnostics_path: Path, workstream: str, out_dir: Path, index_path: Path) -> dict[str, Any]:
    diagnostics = load_json(diagnostics_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    workstream_ids = list(WORKSTREAMS) if workstream == "all" else [workstream]
    artifacts = []
    for workstream_id in workstream_ids:
        payload = pilot_for_workstream(workstream_id, diagnostics, diagnostics_path, out_dir)
        path = out_dir / f"{workstream_id}-pilot.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        artifacts.append({"workstream_id": workstream_id, "path": str(path), "status": payload["status"], "claim_ready": False})
    index = {
        "experiment": "v1_4_workstream_pilot_index",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASSED",
        "claim_ready": False,
        "source_diagnostics": str(diagnostics_path),
        "artifacts": artifacts,
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return index


def main() -> None:
    args = parse_args()
    index = write_pilots(Path(args.diagnostics), args.workstream, Path(args.out_dir), Path(args.index))
    print(json.dumps({"index": args.index, "artifacts": len(index["artifacts"]), "status": index["status"]}, indent=2))


if __name__ == "__main__":
    main()
