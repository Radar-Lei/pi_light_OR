#!/usr/bin/env python3
"""Lock a post-r79 v1.5 reactivated-dual low-signal thin-margin-cap training protocol."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import lock_v15_protocol as base
from lock_v15_r82_training_protocol import TRAINING_SEEDS as R82_TRAINING_SEEDS
from lock_v15_r83_training_protocol import TRAINING_SEEDS as R83_TRAINING_SEEDS
from lock_v15_r84_training_protocol import TRAINING_SEEDS as R84_TRAINING_SEEDS
from lock_v15_r85_training_protocol import TRAINING_SEEDS as R85_TRAINING_SEEDS
from lock_v15_r86_training_protocol import TRAINING_SEEDS as R86_TRAINING_SEEDS
from lock_v15_r87_training_protocol import TRAINING_SEEDS as R87_TRAINING_SEEDS
from lock_v15_r88_training_protocol import TRAINING_SEEDS as R88_TRAINING_SEEDS
from lock_v15_r63_training_protocol import build_training_protocol as build_r63_training_protocol
from run_closed_loop_sumo import DYNAMIC_V1_5_R89_REACTIVATED_DUAL_LOW_SIGNAL_MARGIN_CAP_PARAMS

DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_r89_training_protocol.json"
CONTROLLER_ID = "finite_storage_dynamic_primal_dual_v1_5_r89_reactivated_dual_low_signal_margin_cap"
REQUIREMENTS_COVERED = ["V15-R89-CTRL-01", "V15-CLAIM-01"]
TRAINING_SEEDS = [20261481 + idx for idx in range(6)]


def build_training_protocol() -> dict[str, Any]:
    r63 = build_r63_training_protocol()
    training_split = dict(r63["training_split"])
    excluded_seed_sets = dict(training_split.get("excluded_seed_sets", {}))
    excluded = (
        set(excluded_seed_sets.get("all_prior_v1_5_training_and_binding", []))
        | set(R82_TRAINING_SEEDS)
        | set(R83_TRAINING_SEEDS)
        | set(R84_TRAINING_SEEDS)
        | set(R85_TRAINING_SEEDS)
        | set(R86_TRAINING_SEEDS)
        | set(R87_TRAINING_SEEDS)
        | set(R88_TRAINING_SEEDS)
    )
    overlap = sorted(set(TRAINING_SEEDS) & excluded)
    if overlap:
        raise ValueError(f"r89 training seeds overlap excluded seeds: {overlap}")

    baselines = list(r63["required_baselines"])
    training_split["seeds"] = list(TRAINING_SEEDS)
    training_split["controllers"] = [CONTROLLER_ID, *baselines]
    training_split["excluded_seed_sets"] = {"all_prior_v1_5_training_and_binding": sorted(excluded)}
    training_split["expected_row_count"] = (
        len(training_split["scenarios"])
        * len(training_split["seeds"])
        * len(training_split["demand_multipliers"])
        * len(training_split["controllers"])
    )
    core: dict[str, Any] = {
        "controller_id": CONTROLLER_ID,
        "required_baselines": baselines,
        "controller_params": DYNAMIC_V1_5_R89_REACTIVATED_DUAL_LOW_SIGNAL_MARGIN_CAP_PARAMS,
        "training_split": training_split,
        "selection_rule": {
            "primary_endpoint": "composite_finite_storage_operating_cost",
            "eligible_for_selection_only_if": [
                "no safety-guard harm against max_pressure",
                "no safety-guard harm against capacity_aware_pressure",
                "no safety-guard harm against finite_storage_double_pressure",
                "negative-total completion-conflict fail-close remains limited to materially negative completion-filter deviations",
                "only thin-margin early-severe low-signal completion outranks are capped; stronger separation wins remain untouched",
                "mean composite signal is positive against each core strong baseline after full training execution",
            ],
            "not_confirmatory_evidence": True,
        },
        "supersedes_candidate": "finite_storage_dynamic_primal_dual_v1_5_r79_reactivated_dual_negative_total_completion_conflict",
        "supersession_trigger": "experiments/dual_sensitivity/v1_5_r79_training_selection.json",
    }
    return {
        "experiment": "v1_5_r89_training_protocol",
        "status": "TRAINING_LOCKED",
        "generated_by": "scripts/lock_v15_r89_training_protocol.py",
        "requirements_covered": REQUIREMENTS_COVERED,
        **core,
        "protocol_fingerprint": base.stable_fingerprint(core),
        "artifact_plan": {
            "training_protocol": DEFAULT_OUT,
            "training_execution": "experiments/dual_sensitivity/v1_5_r89_training_execution.json",
            "training_selection": "experiments/dual_sensitivity/v1_5_r89_training_selection.json",
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
