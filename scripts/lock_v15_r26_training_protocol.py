#!/usr/bin/env python3
"""Lock a post-r25 v1.5-r26 relative-exit-urgency training protocol."""
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
from lock_v15_r5_training_protocol import TRAINING_SEEDS as R5_TRAINING_SEEDS
from lock_v15_r6_training_protocol import TRAINING_SEEDS as R6_TRAINING_SEEDS
from lock_v15_r7_training_protocol import TRAINING_SEEDS as R7_TRAINING_SEEDS
from lock_v15_r8_training_protocol import TRAINING_SEEDS as R8_TRAINING_SEEDS
from lock_v15_r9_training_protocol import TRAINING_SEEDS as R9_TRAINING_SEEDS
from lock_v15_r10_training_protocol import TRAINING_SEEDS as R10_TRAINING_SEEDS
from lock_v15_r11_training_protocol import TRAINING_SEEDS as R11_TRAINING_SEEDS
from lock_v15_r12_training_protocol import TRAINING_SEEDS as R12_TRAINING_SEEDS
from lock_v15_r13_training_protocol import TRAINING_SEEDS as R13_TRAINING_SEEDS
from lock_v15_r14_training_protocol import TRAINING_SEEDS as R14_TRAINING_SEEDS
from lock_v15_r15_training_protocol import TRAINING_SEEDS as R15_TRAINING_SEEDS
from lock_v15_r16_training_protocol import TRAINING_SEEDS as R16_TRAINING_SEEDS
from lock_v15_r17_training_protocol import TRAINING_SEEDS as R17_TRAINING_SEEDS
from lock_v15_r18_training_protocol import TRAINING_SEEDS as R18_TRAINING_SEEDS
from lock_v15_r19_training_protocol import TRAINING_SEEDS as R19_TRAINING_SEEDS
from lock_v15_r20_training_protocol import TRAINING_SEEDS as R20_TRAINING_SEEDS
from lock_v15_r21_training_protocol import TRAINING_SEEDS as R21_TRAINING_SEEDS
from lock_v15_r22_training_protocol import TRAINING_SEEDS as R22_TRAINING_SEEDS
from lock_v15_r23_training_protocol import TRAINING_SEEDS as R23_TRAINING_SEEDS
from lock_v15_r24_training_protocol import TRAINING_SEEDS as R24_TRAINING_SEEDS
from lock_v15_r25_training_protocol import TRAINING_SEEDS as R25_TRAINING_SEEDS
from run_closed_loop_sumo import DYNAMIC_V1_5_R26_RELATIVE_EXIT_URGENCY_PARAMS

DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_r26_training_protocol.json"
CONTROLLER_ID = "finite_storage_dynamic_primal_dual_v1_5_r26_relative_exit_urgency"
REQUIREMENTS_COVERED = ["V15-R26-CTRL-01", "V15-CLAIM-01"]
TRAINING_SCENARIOS = ["arterial_v1_5_storage_activation", "arterial_spillback_stress", "arterial_downstream_blockage"]
TRAINING_SEEDS = [20261041 + idx for idx in range(6)]
TRAINING_DEMAND_MULTIPLIERS = [0.85, 1.0, 1.15]


def build_training_protocol() -> dict[str, Any]:
    excluded = (
        set(BINDING_HOLDOUT_SEEDS)
        | set(R2_TRAINING_SEEDS)
        | set(R3_TRAINING_SEEDS)
        | set(R4_TRAINING_SEEDS)
        | set(R5_TRAINING_SEEDS)
        | set(R6_TRAINING_SEEDS)
        | set(R7_TRAINING_SEEDS)
        | set(R8_TRAINING_SEEDS)
        | set(R9_TRAINING_SEEDS)
        | set(R10_TRAINING_SEEDS)
        | set(R11_TRAINING_SEEDS)
        | set(R12_TRAINING_SEEDS)
        | set(R13_TRAINING_SEEDS)
        | set(R14_TRAINING_SEEDS)
        | set(R15_TRAINING_SEEDS)
        | set(R16_TRAINING_SEEDS)
        | set(R17_TRAINING_SEEDS)
        | set(R18_TRAINING_SEEDS)
        | set(R19_TRAINING_SEEDS)
        | set(R20_TRAINING_SEEDS)
        | set(R21_TRAINING_SEEDS)
        | set(R22_TRAINING_SEEDS)
        | set(R23_TRAINING_SEEDS)
        | set(R24_TRAINING_SEEDS)
        | set(R25_TRAINING_SEEDS)
    )
    overlap = sorted(set(TRAINING_SEEDS) & excluded)
    if overlap:
        raise ValueError(f"r26 training seeds overlap excluded seeds: {overlap}")
    baselines = list(base.REQUIRED_BASELINES)
    controllers = [CONTROLLER_ID, *baselines]
    training_split = {
        "profile": "training",
        "scenarios": list(TRAINING_SCENARIOS),
        "seeds": list(TRAINING_SEEDS),
        "excluded_seed_sets": {"all_prior_v1_5_training_and_binding": sorted(excluded)},
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
        "controller_params": DYNAMIC_V1_5_R26_RELATIVE_EXIT_URGENCY_PARAMS,
        "training_split": training_split,
        "selection_rule": {
            "primary_endpoint": "composite_finite_storage_operating_cost",
            "eligible_for_selection_only_if": [
                "no safety-guard harm against max_pressure",
                "no safety-guard harm against capacity_aware_pressure",
                "no safety-guard harm against finite_storage_double_pressure",
                "route horizon score weights exit urgency relative to remaining simulation time",
                "mean composite signal is positive against each core strong baseline after full training execution",
            ],
            "not_confirmatory_evidence": True,
        },
        "supersedes_candidate": "finite_storage_dynamic_primal_dual_v1_5_r25_staged_horizon_late_max",
        "supersession_trigger": "experiments/dual_sensitivity/v1_5_r25_training_selection.json",
    }
    return {
        "experiment": "v1_5_r26_training_protocol",
        "status": "TRAINING_LOCKED",
        "generated_by": "scripts/lock_v15_r26_training_protocol.py",
        "requirements_covered": REQUIREMENTS_COVERED,
        **core,
        "protocol_fingerprint": base.stable_fingerprint(core),
        "artifact_plan": {
            "training_protocol": DEFAULT_OUT,
            "training_execution": "experiments/dual_sensitivity/v1_5_r26_training_execution.json",
            "training_selection": "experiments/dual_sensitivity/v1_5_r26_training_selection.json",
        },
        "claim_scope": {"claim_ready": False, "closed_loop_superiority_claim_allowed": False},
    }


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
