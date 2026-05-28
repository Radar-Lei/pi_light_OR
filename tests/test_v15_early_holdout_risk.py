#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_v15_early_holdout_risk import build_risk_payload  # noqa: E402


def activation(status: str = "PASSED") -> dict[str, object]:
    return {
        "status": status,
        "summary": {
            "controller_rows": 3,
            "binding_decision_rate": 0.97,
            "dynamic_term_counts": {"storage_price": 3, "cascade_price": 3, "release": 3},
        },
    }


def evidence_with_harms() -> dict[str, object]:
    return {
        "status": "INCONCLUSIVE",
        "claim_ready": False,
        "locked_protocol_fingerprint": "abc",
        "primary_composite_results": [
            {
                "scenario_tag": "arterial_v1_5_storage_activation",
                "demand_multiplier": 0.9,
                "baseline": "max_pressure",
                "n_seeds": 3,
                "mean_paired_difference": 1.0,
                "classification": "inconclusive",
                "strict_positive_signal": False,
            }
        ],
        "safety_guard_results": [
            {
                "scenario_tag": "arterial_v1_5_storage_activation",
                "demand_multiplier": 0.9,
                "baseline": "max_pressure",
                "metric": "total_delay",
                "harm_count": 3,
                "passed": False,
                "practical_harm_tolerance": 0.05,
                "harms": [
                    {"seed": 1, "v1_5": 11.0, "baseline": 10.0, "allowed": 10.5},
                    {"seed": 2, "v1_5": 12.0, "baseline": 10.0, "allowed": 10.5},
                    {"seed": 3, "v1_5": 13.0, "baseline": 10.0, "allowed": 10.5},
                ],
            }
        ],
    }


def test_early_risk_fails_when_binding_audit_passes_and_core_baseline_harms_repeat() -> None:
    payload = build_risk_payload(evidence_with_harms(), activation(), Path("evidence.json"), Path("activation.json"))

    assert payload["status"] == "FAILED"
    assert payload["claim_ready"] is False
    assert payload["harmful_core_baselines"] == ["max_pressure"]
    assert payload["claim_scope"]["closed_loop_superiority_claim_allowed"] is False
    assert "do not tune" in payload["recommendation"]


def test_early_risk_stays_inconclusive_when_activation_did_not_pass() -> None:
    payload = build_risk_payload(evidence_with_harms(), activation("FAILED"), Path("evidence.json"), Path("activation.json"))

    assert payload["status"] == "INCONCLUSIVE"
    assert payload["harmful_core_baselines"] == ["max_pressure"]
