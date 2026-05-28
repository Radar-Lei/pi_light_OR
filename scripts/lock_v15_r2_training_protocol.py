#!/usr/bin/env python3
"""Lock a post-holdout v1.5-r2 training protocol without reusing binding holdout seeds."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import lock_v15_protocol as base
from lock_v15_binding_protocol import BINDING_HOLDOUT_SEEDS
from run_closed_loop_sumo import DYNAMIC_V1_5_R2_GUARDED_PARAMS

DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_r2_training_protocol.json"
CONTROLLER_ID = "finite_storage_dynamic_primal_dual_v1_5_r2_guarded"
REQUIREMENTS_COVERED = ["V15-R2-TRAIN-01", "V15-CLAIM-01"]
TRAINING_SCENARIOS = [
    "arterial_v1_5_storage_activation",
    "arterial_spillback_stress",
    "arterial_downstream_blockage",
]
TRAINING_SEEDS = [20260801 + idx for idx in range(6)]
TRAINING_DEMAND_MULTIPLIERS = [0.85, 1.0, 1.15]


def build_training_protocol() -> dict[str, Any]:
    overlap = sorted(set(TRAINING_SEEDS) & set(BINDING_HOLDOUT_SEEDS))
    if overlap:
        raise ValueError(f"training seeds overlap current binding holdout seeds: {overlap}")
    baselines = list(base.REQUIRED_BASELINES)
    controllers = [CONTROLLER_ID, *baselines]
    training_split = {
        "profile": "training",
        "scenarios": list(TRAINING_SCENARIOS),
        "seeds": list(TRAINING_SEEDS),
        "excluded_holdout_seed_sets": {
            "v1_5_binding_locked_protocol": list(BINDING_HOLDOUT_SEEDS),
        },
        "demand_multipliers": list(TRAINING_DEMAND_MULTIPLIERS),
        "controllers": controllers,
        "steps": 3600,
        "warmup": 900,
        "action_interval": 10,
    }
    training_split["expected_row_count"] = (
        len(training_split["scenarios"])
        * len(training_split["seeds"])
        * len(training_split["demand_multipliers"])
        * len(training_split["controllers"])
    )
    core = {
        "controller_id": CONTROLLER_ID,
        "required_baselines": baselines,
        "controller_params": DYNAMIC_V1_5_R2_GUARDED_PARAMS,
        "training_split": training_split,
        "selection_rule": {
            "primary_endpoint": "composite_finite_storage_operating_cost",
            "eligible_for_selection_only_if": [
                "no safety-guard harm against max_pressure",
                "no safety-guard harm against capacity_aware_pressure",
                "no safety-guard harm against finite_storage_double_pressure",
                "mechanism activation remains present",
            ],
            "not_confirmatory_evidence": True,
        },
        "supersedes_candidate": "finite_storage_dynamic_primal_dual_v1_5",
        "supersession_trigger": "experiments/dual_sensitivity/v1_5_binding_early_holdout_risk.json",
    }
    payload: dict[str, Any] = {
        "experiment": "v1_5_r2_training_protocol",
        "status": "TRAINING_LOCKED",
        "generated_by": "scripts/lock_v15_r2_training_protocol.py",
        "requirements_covered": REQUIREMENTS_COVERED,
        **core,
        "protocol_fingerprint": base.stable_fingerprint(core),
        "artifact_plan": {
            "training_protocol": DEFAULT_OUT,
            "training_execution": "experiments/dual_sensitivity/v1_5_r2_training_execution.json",
            "training_selection": "experiments/dual_sensitivity/v1_5_r2_training_selection.json",
            "future_confirmatory_protocol": "experiments/dual_sensitivity/v1_5_r2_locked_protocol.json",
        },
        "claim_scope": {
            "claim_ready": False,
            "closed_loop_superiority_claim_allowed": False,
            "why": "training protocol can select or reject a revised method but cannot confirm a superiority claim",
            "required_before_claim": [
                "freeze selected r2 method after training",
                "lock a fresh/superseding confirmatory protocol",
                "execute confirmatory holdout on non-training seeds",
                "pass strict paired evidence and safety guards",
            ],
        },
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()
    payload = build_training_protocol()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "out": str(out),
                "fingerprint": payload["protocol_fingerprint"],
                "expected_rows": payload["training_split"]["expected_row_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
