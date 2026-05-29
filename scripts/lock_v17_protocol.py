#!/usr/bin/env python3
"""Lock the v1.7 CFS-PD-MPC training and holdout protocol.

Generates a locked protocol JSON that defines training scenarios, holdout
scenarios, seeds, baselines, endpoints, and safety guards for the v1.7
Completion-aware Finite-Storage Primal-Dual MPC controller.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from finite_storage_schema import OBJECTIVE_COMPONENT_FIELDS
from run_closed_loop_sumo import DYNAMIC_V1_7_CFS_PD_MPC_PARAMS

DEFAULT_OUT = "experiments/dual_sensitivity/v1_7_training_protocol.json"
CONTROLLER_ID = "finite_storage_completion_primal_dual_v1_7"
REQUIREMENTS_COVERED = ["V17-PROTO-01", "V17-EVID-01", "V17-CLAIM-01"]
REQUIRED_BASELINES = [
    "max_pressure",
    "capacity_aware_pressure",
    "occupancy_capacity_aware_pressure",
    "finite_storage_double_pressure",
    "delay_based_max_pressure",
    "switching_loss_max_pressure",
]
TRAINING_SCENARIOS = [
    "arterial_v1_5_storage_activation",
    "arterial_spillback_stress",
    "arterial_downstream_blockage",
]
HOLDOUT_SCENARIOS = [
    "arterial_downstream_blockage",
    "arterial_spillback_stress",
    "arterial_oversaturation",
    "arterial_turning_shock",
    "arterial_incident_capacity_drop",
    "arterial_switching_loss_sensitive",
]
TRAINING_SEEDS = [20261701 + idx for idx in range(6)]
HOLDOUT_SEEDS = [20261707 + idx for idx in range(4)]
DEMAND_MULTIPLIERS = [0.85, 1.0, 1.15]
COMPOSITE_WEIGHTS = {
    "delay": 1.0,
    "unfinished_vehicle_penalty": 1.0,
    "spillback_blocking_time": 1.0,
    "switching_lost_time": 1.0,
}

# Seeds used by prior protocol versions — must not overlap with v1.7.
_PRIOR_SEED_RANGES = {
    "v1_5_original_training": [20260527, 20260528, 20260529],
    "v1_5_original_holdout": list(range(20260610, 20260620)),
    "v1_5_r2_training": list(range(20260801, 20260807)),
    "v1_5_binding_holdout": list(range(20260710, 20260718)),
}


def stable_fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _check_seed_isolation() -> None:
    v17_seeds = set(TRAINING_SEEDS) | set(HOLDOUT_SEEDS)
    for label, prior in _PRIOR_SEED_RANGES.items():
        overlap = sorted(v17_seeds & set(prior))
        if overlap:
            raise ValueError(
                f"v1.7 seeds overlap with {label}: {overlap}"
            )


def build_protocol() -> dict[str, Any]:
    _check_seed_isolation()

    controllers = [CONTROLLER_ID, *REQUIRED_BASELINES]

    training_split = {
        "profile": "training",
        "scenarios": list(TRAINING_SCENARIOS),
        "seeds": list(TRAINING_SEEDS),
        "demand_multipliers": list(DEMAND_MULTIPLIERS),
        "controllers": list(controllers),
        "steps": 3600,
        "warmup": 900,
        "action_interval": 10,
        "not_claim_evidence": True,
    }
    training_split["expected_row_count"] = (
        len(training_split["scenarios"])
        * len(training_split["seeds"])
        * len(training_split["demand_multipliers"])
        * len(training_split["controllers"])
    )
    # Screen subset: 3 scenarios x 1 seed x 1 demand x 4 controllers = 12 rows
    training_split["screen_row_count"] = (
        len(training_split["scenarios"])
        * 1  # first seed only
        * 1  # demand=1.0 only
        * 4  # candidate + 3 core baselines
    )
    training_split["screen_subset"] = {
        "seeds": [TRAINING_SEEDS[0]],
        "demand_multipliers": [1.0],
        "controllers": [
            CONTROLLER_ID,
            "max_pressure",
            "capacity_aware_pressure",
            "finite_storage_double_pressure",
        ],
    }

    holdout_split = {
        "role": "claim_eligible_only_if_executed_after_protocol_lock",
        "profile": "main",
        "scenarios": list(HOLDOUT_SCENARIOS),
        "seeds": list(HOLDOUT_SEEDS),
        "demand_multipliers": list(DEMAND_MULTIPLIERS),
        "controllers": list(controllers),
        "steps": 3600,
        "warmup": 900,
        "action_interval": 10,
    }
    holdout_split["expected_row_count"] = (
        len(holdout_split["scenarios"])
        * len(holdout_split["seeds"])
        * len(holdout_split["demand_multipliers"])
        * len(holdout_split["controllers"])
    )

    protocol_core: dict[str, Any] = {
        "controller_id": CONTROLLER_ID,
        "controller_params": {key: float(value) for key, value in sorted(DYNAMIC_V1_7_CFS_PD_MPC_PARAMS.items())},
        "required_baselines": list(REQUIRED_BASELINES),
        "training_split": training_split,
        "locked_holdout": holdout_split,
        "primary_endpoint": {
            "name": "composite_finite_storage_operating_cost",
            "components": sorted(OBJECTIVE_COMPONENT_FIELDS),
            "weights": dict(COMPOSITE_WEIGHTS),
            "formula": "delay + unfinished_vehicle_penalty + spillback_blocking_time + switching_lost_time",
            "paired_seed_comparison": True,
            "required_result": "lower_is_better_against_each_required_baseline",
        },
        "safety_guards": {
            "penalized_avg_travel_time": {"practical_harm_tolerance": 0.05, "direction": "lower_is_better"},
            "total_delay": {"practical_harm_tolerance": 0.05, "direction": "lower_is_better"},
            "unfinished_vehicle_count": {"practical_harm_tolerance": 0.0, "direction": "lower_is_better"},
        },
        "selection_rule": {
            "objective": "minimax_regret",
            "formula": "min over candidate params of max over baselines of [J(candidate, s) - J(baseline, s)]_+",
            "eligible_for_selection_only_if": [
                "no safety-guard harm against max_pressure",
                "no safety-guard harm against capacity_aware_pressure",
                "no safety-guard harm against finite_storage_double_pressure",
                "advantage_gate_activation_rate > 0",
                "action_separation_rate > 0.05",
            ],
            "not_confirmatory_evidence": True,
        },
        "secondary_metrics": [
            "spillback_count",
            "blocking_count",
            "switching_count",
            "throughput",
            "completion_rate",
        ],
        "failure_rules": {
            "training_rows_not_claim_evidence": True,
            "missing_required_baseline_fails_closed": True,
            "missing_paired_seed_fails_closed": True,
            "post_lock_controller_param_change_fails_closed": True,
            "closed_loop_superiority_allowed_only_if_locked_holdout_passes": True,
        },
        "diagnostic_prerequisites": [
            "experiments/dual_sensitivity/v1_7_cfs_pd_mpc_gates.json",
        ],
        "artifact_plan": {
            "training_protocol": DEFAULT_OUT,
            "training_execution": "experiments/dual_sensitivity/v1_7_training_execution.json",
            "training_selection": "experiments/dual_sensitivity/v1_7_training_selection.json",
            "locked_holdout_execution": "experiments/dual_sensitivity/v1_7_locked_holdout_execution.json",
            "paired_evidence": "experiments/dual_sensitivity/v1_7_paired_evidence.json",
        },
    }
    fingerprint = stable_fingerprint(protocol_core)
    return {
        "experiment": "v1_7_training_protocol",
        "status": "TRAINING_LOCKED",
        "generated_by": "scripts/lock_v17_protocol.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requirements_covered": REQUIREMENTS_COVERED,
        "protocol_fingerprint": fingerprint,
        "claim_scope": {
            "allowed_now": "protocol lock and future-evidence contract only",
            "not_claimed": [
                "closed_loop_superiority",
                "locked_holdout_passed",
                "deployment_readiness",
            ],
        },
        **protocol_core,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Lock v1.7 CFS-PD-MPC training protocol")
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()

    payload = build_protocol()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "out": str(out_path),
                "fingerprint": payload["protocol_fingerprint"],
                "training_rows": payload["training_split"]["expected_row_count"],
                "screen_rows": payload["training_split"]["screen_row_count"],
                "holdout_rows": payload["locked_holdout"]["expected_row_count"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
