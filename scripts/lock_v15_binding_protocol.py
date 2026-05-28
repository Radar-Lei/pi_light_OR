#!/usr/bin/env python3
"""Lock a revised v1.5 storage-activation holdout after protocol activation audit failure."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import lock_v15_protocol as base

DEFAULT_OUT = "experiments/dual_sensitivity/v1_5_binding_locked_protocol.json"
REQUIREMENTS_COVERED = ["V15-PROTO-02", "V15-CLAIM-01"]
BINDING_HOLDOUT_SCENARIOS = [
    "arterial_v1_5_storage_activation",
    "arterial_spillback_stress",
    "arterial_downstream_blockage",
    "arterial_incident_capacity_drop",
]
BINDING_HOLDOUT_SEEDS = [20260710 + idx for idx in range(8)]


def build_binding_protocol() -> dict[str, Any]:
    payload = base.build_protocol()
    holdout = payload["locked_holdout"]
    holdout["scenarios"] = list(BINDING_HOLDOUT_SCENARIOS)
    holdout["seeds"] = list(BINDING_HOLDOUT_SEEDS)
    holdout["expected_row_count"] = (
        len(holdout["scenarios"])
        * len(holdout["seeds"])
        * len(holdout["demand_multipliers"])
        * len(holdout["controllers"])
    )
    payload["experiment"] = "v1_5_binding_locked_protocol"
    payload["generated_by"] = "scripts/lock_v15_binding_protocol.py"
    payload["requirements_covered"] = REQUIREMENTS_COVERED
    payload["supersedes_protocol"] = "experiments/dual_sensitivity/v1_5_locked_protocol.json"
    payload["supersession_reason"] = (
        "Early executed rows from the first v1.5 holdout did not enter finite-storage binding states, "
        "so that protocol is unsuitable for the storage-activation claim target."
    )
    payload["diagnostic_prerequisites"] = [
        "experiments/dual_sensitivity/v1_5_dynamic_primal_dual_gates.json",
        "experiments/dual_sensitivity/v1_5_closed_loop_diagnostics.json",
        "experiments/dual_sensitivity/v1_5_protocol_activation_audit.json",
    ]
    core: dict[str, Any] = {
        key: value
        for key, value in payload.items()
        if key
        not in {
            "experiment",
            "status",
            "generated_by",
            "generated_at",
            "requirements_covered",
            "protocol_fingerprint",
            "claim_scope",
        }
    }
    payload["protocol_fingerprint"] = base.stable_fingerprint(core)
    payload["artifact_plan"] = {
        "locked_protocol": DEFAULT_OUT,
        "locked_holdout_execution": "experiments/dual_sensitivity/v1_5_binding_holdout_execution.json",
        "paired_evidence": "experiments/dual_sensitivity/v1_5_binding_paired_evidence.json",
        "claim_refresh": "experiments/dual_sensitivity/v1_5_binding_summary.md",
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args()
    payload = build_binding_protocol()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": str(out), "fingerprint": payload["protocol_fingerprint"]}, indent=2))


if __name__ == "__main__":
    main()
