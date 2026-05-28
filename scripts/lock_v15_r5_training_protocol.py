#!/usr/bin/env python3
"""Lock a post-r4 v1.5-r5 training protocol with fresh seeds."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import lock_v15_protocol as base
from lock_v15_binding_protocol import BINDING_HOLDOUT_SEEDS
from lock_v15_r2_training_protocol import TRAINING_SEEDS as R2_TRAINING_SEEDS
from lock_v15_r3_training_protocol import TRAINING_SEEDS as R3_TRAINING_SEEDS
from lock_v15_r4_training_protocol import TRAINING_SEEDS as R4_TRAINING_SEEDS
from run_closed_loop_sumo import DYNAMIC_V1_5_R5_DOUBLE_SAFE_PARAMS

DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_r5_training_protocol.json"
CONTROLLER_ID = "finite_storage_dynamic_primal_dual_v1_5_r5_double_safe"
REQUIREMENTS_COVERED = ["V15-R5-TRAIN-01", "V15-CLAIM-01"]
TRAINING_SCENARIOS = [
    "arterial_v1_5_storage_activation",
    "arterial_spillback_stress",
    "arterial_downstream_blockage",
]
TRAINING_SEEDS = [20260831 + idx for idx in range(6)]
TRAINING_DEMAND_MULTIPLIERS = [0.85, 1.0, 1.15]


def build_training_protocol() -> dict[str, Any]:
    excluded = set(BINDING_HOLDOUT_SEEDS) | set(R2_TRAINING_SEEDS) | set(R3_TRAINING_SEEDS) | set(R4_TRAINING_SEEDS)
    overlap = sorted(set(TRAINING_SEEDS) & excluded)
    if overlap:
        raise ValueError(f"r5 training seeds overlap excluded seeds: {overlap}")
    baselines = list(base.REQUIRED_BASELINES)
    controllers = [CONTROLLER_ID, *baselines]
    training_split = {
        "profile": "training",
        "scenarios": list(TRAINING_SCENARIOS),
        "seeds": list(TRAINING_SEEDS),
        "excluded_seed_sets": {
            "v1_5_binding_locked_protocol": list(BINDING_HOLDOUT_SEEDS),
            "v1_5_r2_training_protocol": list(R2_TRAINING_SEEDS),
            "v1_5_r3_training_protocol": list(R3_TRAINING_SEEDS),
            "v1_5_r4_training_protocol": list(R4_TRAINING_SEEDS),
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
        "controller_params": DYNAMIC_V1_5_R5_DOUBLE_SAFE_PARAMS,
        "training_split": training_split,
        "selection_rule": {
            "primary_endpoint": "composite_finite_storage_operating_cost",
            "eligible_for_selection_only_if": [
                "no safety-guard harm against max_pressure",
                "no safety-guard harm against capacity_aware_pressure",
                "no safety-guard harm against finite_storage_double_pressure",
                "action separation from pressure remains nonzero on binding training rows",
                "finite-storage-double fallback prevents completion-risk regressions",
            ],
            "not_confirmatory_evidence": True,
        },
        "supersedes_candidate": "finite_storage_dynamic_primal_dual_v1_5_r4_release_service",
        "supersession_trigger": "experiments/dual_sensitivity/v1_5_r4_training_selection.json",
    }
    payload: dict[str, Any] = {
        "experiment": "v1_5_r5_training_protocol",
        "status": "TRAINING_LOCKED",
        "generated_by": "scripts/lock_v15_r5_training_protocol.py",
        "requirements_covered": REQUIREMENTS_COVERED,
        **core,
        "protocol_fingerprint": base.stable_fingerprint(core),
        "artifact_plan": {
            "training_protocol": DEFAULT_OUT,
            "training_execution": "experiments/dual_sensitivity/v1_5_r5_training_execution.json",
            "training_selection": "experiments/dual_sensitivity/v1_5_r5_training_selection.json",
            "future_confirmatory_protocol": "experiments/dual_sensitivity/v1_5_r5_locked_protocol.json",
        },
        "claim_scope": {
            "claim_ready": False,
            "closed_loop_superiority_claim_allowed": False,
            "why": "training protocol can select or reject a revised method but cannot confirm a superiority claim",
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
