#!/usr/bin/env python3
"""Central bounded-claim policy for Phase 6 claim-discipline gates."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

POLICY_ARTIFACT = "experiments/dual_sensitivity/phase6_claim_policy.json"
CLAIM_AUDIT_ARTIFACT = "experiments/dual_sensitivity/phase6_claim_audit.json"

FORBIDDEN_CLAIM_PATTERNS: list[str] = [
    "dual universally beats pressure",
    "proves superiority",
    "deployable superiority",
    "static evidence proves closed-loop",
    "universal dominance",
    "universally dominates pressure",
]

DEFAULT_CLAIM_SCAN_PATHS: list[str] = [
    ".planning/PROJECT.md",
    ".planning/REQUIREMENTS.md",
    ".planning/STATE.md",
    "refine-logs",
    "experiments/dual_sensitivity/block3_static_kill_gate_report.md",
    "experiments/dual_sensitivity/block4_closed_loop_suite_report.md",
    "experiments/dual_sensitivity/reproducibility_manifest.json",
    "experiments/dual_sensitivity/paper_artifacts_manifest.json",
    "experiments/dual_sensitivity/paper_tables.csv",
    "experiments/dual_sensitivity/paper_figure_data.csv",
]

PERMITTED_CLAIM = (
    "recover_or_tie_max_pressure_when_constraints_slack; "
    "improvement_claims_only_for_explicit_binding_finite_storage_spillback_switching_service_incident_regimes"
)

REQUIREMENTS_COVERED = ["CLAIM-01", "CLAIM-02"]


def bounded_claim_policy() -> dict[str, Any]:
    return {
        "experiment": "phase6_claim_policy",
        "status": "PASSED",
        "permitted_claim": PERMITTED_CLAIM,
        "allowed_claims": {
            "slack_recovery_or_tie": {
                "description": "When finite-storage and operational constraints are slack, the controller may be described as recovering or tying max-pressure/backpressure.",
                "evidence_prerequisites": [
                    "finite_storage_state",
                    "objective_components",
                    "slack_regime_label",
                    "max_pressure_comparator",
                ],
                "allowed_language": [
                    "recovers max-pressure when constraints are slack",
                    "ties max-pressure in slack regimes",
                    "pressure-equivalent recovery evidence",
                ],
            },
            "binding_regime_improvement_only": {
                "description": "Improvement claims require explicit binding finite-storage, spillback, switching, service, or incident evidence plus objective components.",
                "evidence_prerequisites": [
                    "finite_storage_state",
                    "objective_components",
                    "binding_regime_separation",
                    "closed_loop_binding_stress_or_one_step_objective_improvement",
                    "paired_or_predeclared_baseline_comparator_when_closed_loop",
                ],
                "allowed_language": [
                    "improves only in explicit binding regimes",
                    "binding finite-storage evidence supports this improvement claim",
                    "strict generalization is bounded to binding operational constraints",
                ],
            },
        },
        "evidence_categories": {
            "pressure_equivalent_recovery": {
                "supports": ["slack_recovery_or_tie", "compression_or_equivalence"],
                "does_not_support": ["dual_superiority", "deployment_superiority", "universal_dominance"],
            },
            "binding_regime_separation": {
                "supports": ["action_separation_in_explicit_binding_states"],
                "requires": ["finite_storage_state", "objective_components"],
            },
            "closed_loop_binding_stress": {
                "supports": ["bounded_closed_loop_improvement_in_predeclared_binding_stress_regimes"],
                "requires": ["paired_seeds", "strong_baselines", "explicit_binding_state_or_stress_metadata"],
            },
            "insufficient_historical_v1_0": {
                "applies_to": ["v1.0 static kill gate", "v1.0 closed-loop suite", "pressure-equivalent generalized-pressure recovery"],
                "reason": "Historical v1.0 artifacts are pressure-equivalent recovery evidence and cannot support dual-superiority wording.",
            },
        },
        "forbidden_patterns": FORBIDDEN_CLAIM_PATTERNS,
        "default_scan_paths": DEFAULT_CLAIM_SCAN_PATHS,
        "requirements_covered": REQUIREMENTS_COVERED,
    }


def is_negated_or_bounded_context(lowered: str, phrase: str) -> bool:
    index = lowered.find(phrase)
    if index < 0:
        return False
    context = lowered[max(0, index - 240): index]
    bounded_markers = [
        "not ",
        "no ",
        "without ",
        "must not ",
        "does not ",
        "do not ",
        "cannot ",
        "out of scope",
        "rather than ",
        "the relaxation alone proves ",
    ]
    return any(marker in context for marker in bounded_markers)


def forbidden_claim_hits(text: str, source: str = "<memory>") -> list[dict[str, str]]:
    lowered = text.lower()
    hits: list[dict[str, str]] = []
    for phrase in FORBIDDEN_CLAIM_PATTERNS:
        normalized = phrase.lower()
        if normalized in lowered and not is_negated_or_bounded_context(lowered, normalized):
            hits.append({"source": source, "path": source, "phrase": phrase})
    return hits


def historical_evidence_is_insufficient_for_superiority(payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, sort_keys=True).lower()
    historical_markers = [
        "pressure-equivalent",
        "pressure equivalent",
        "v1.0",
        "block3_static_kill_gate",
        "block4_closed_loop_suite",
        "historical",
    ]
    superiority_markers = [
        "proves superiority",
        "proves dual superiority",
        "universally beats",
        "universally dominates",
        "deployable superiority",
    ]
    has_historical = any(marker in text for marker in historical_markers)
    has_superiority = any(
        marker in text and not is_negated_or_bounded_context(text, marker)
        for marker in superiority_markers
    )
    has_phase6_binding = all(marker in text for marker in ["finite_storage_state", "objective_components"])
    return has_historical and has_superiority and not has_phase6_binding


def write_policy_artifact(path: Path, *, generated_by: str) -> dict[str, Any]:
    payload = bounded_claim_policy()
    payload = {
        **payload,
        "generated_by": generated_by,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_path": str(path),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
