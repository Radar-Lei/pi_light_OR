#!/usr/bin/env python3
"""Lock the v1.5 dynamic finite-storage primal-dual holdout protocol."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from finite_storage_schema import OBJECTIVE_COMPONENT_FIELDS
from run_closed_loop_sumo import DYNAMIC_V1_5_PARAMS

DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_locked_protocol.json"
CONTROLLER_ID = "finite_storage_dynamic_primal_dual_v1_5"
REQUIREMENTS_COVERED = ["V15-PROTO-01", "V15-EVID-01", "V15-CLAIM-01"]
REQUIRED_BASELINES = [
    "max_pressure",
    "capacity_aware_pressure",
    "occupancy_capacity_aware_pressure",
    "finite_storage_double_pressure",
    "finite_storage_primal_dual_v1_4_score",
]
TRAINING_SCENARIOS = [
    "arterial_v1_5_storage_activation",
    "arterial_spillback_stress",
    "arterial_downstream_blockage",
]
HOLDOUT_SCENARIOS = [
    "arterial_downstream_blockage",
    "arterial_spillback_stress",
    "arterial_incident_capacity_drop",
    "arterial_oversaturation",
    "arterial_turning_shock",
    "arterial_switching_loss_sensitive",
]
TRAINING_SEEDS = [20260527, 20260528, 20260529]
HOLDOUT_SEEDS = [20260610 + idx for idx in range(10)]
DEMAND_MULTIPLIERS = [0.9, 1.0, 1.1]
COMPOSITE_WEIGHTS = {
    "delay": 1.0,
    "unfinished_vehicle_penalty": 1.0,
    "spillback_blocking_time": 1.0,
    "switching_lost_time": 1.0,
}


def stable_fingerprint(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_protocol() -> dict[str, Any]:
    protocol_core: dict[str, Any] = {
        "controller_id": CONTROLLER_ID,
        "controller_params": {key: float(value) for key, value in sorted(DYNAMIC_V1_5_PARAMS.items())},
        "required_baselines": REQUIRED_BASELINES,
        "training_split": {
            "role": "pilot_and_parameter_selection_only",
            "scenarios": TRAINING_SCENARIOS,
            "seeds": TRAINING_SEEDS,
            "not_claim_evidence": True,
        },
        "locked_holdout": {
            "role": "claim_eligible_only_if_executed_after_protocol_lock",
            "profile": "main",
            "steps": 3600,
            "warmup": 900,
            "action_interval": 10,
            "scenarios": HOLDOUT_SCENARIOS,
            "seeds": HOLDOUT_SEEDS,
            "demand_multipliers": DEMAND_MULTIPLIERS,
            "controllers": [CONTROLLER_ID, *REQUIRED_BASELINES],
            "expected_row_count": len(HOLDOUT_SCENARIOS) * len(HOLDOUT_SEEDS) * len(DEMAND_MULTIPLIERS) * (1 + len(REQUIRED_BASELINES)),
        },
        "primary_endpoint": {
            "name": "composite_finite_storage_operating_cost",
            "components": sorted(OBJECTIVE_COMPONENT_FIELDS),
            "weights": COMPOSITE_WEIGHTS,
            "formula": "delay + unfinished_vehicle_penalty + spillback_blocking_time + switching_lost_time",
            "paired_seed_comparison": True,
            "required_result": "lower_is_better_against_each_required_baseline",
        },
        "safety_guards": {
            "penalized_avg_travel_time": {"practical_harm_tolerance": 0.05, "direction": "lower_is_better"},
            "total_delay": {"practical_harm_tolerance": 0.05, "direction": "lower_is_better"},
            "unfinished_vehicle_count": {"practical_harm_tolerance": 0.0, "direction": "lower_is_better"},
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
            "experiments/dual_sensitivity/v1_5_dynamic_primal_dual_gates.json",
            "experiments/dual_sensitivity/v1_5_closed_loop_diagnostics.json",
        ],
        "artifact_plan": {
            "locked_protocol": DEFAULT_OUT,
            "training_pilot": "experiments/dual_sensitivity/v1_5_training_pilot.json",
            "locked_holdout_execution": "experiments/dual_sensitivity/v1_5_locked_holdout_execution.json",
            "paired_evidence": "experiments/dual_sensitivity/v1_5_paired_evidence.json",
            "claim_refresh": "experiments/dual_sensitivity/v1_5_summary.md",
        },
    }
    fingerprint = stable_fingerprint(protocol_core)
    return {
        "experiment": "v1_5_locked_protocol",
        "status": "LOCKED",
        "generated_by": "scripts/lock_v15_protocol.py",
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()

    payload = build_protocol()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": str(out_path), "fingerprint": payload["protocol_fingerprint"]}, indent=2))


if __name__ == "__main__":
    main()
