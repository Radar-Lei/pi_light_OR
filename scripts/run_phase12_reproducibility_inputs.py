#!/usr/bin/env python3
"""Generate Phase 12 reproducibility and bounded future-claim inputs.

This script consumes existing Phase 7/9/10/11 JSON artifacts, preserves
source status, emits derived JSON/CSV/Markdown artifacts, and fails closed in
strict mode when required evidence is missing, inconclusive, or overclaimed.
It does not run SUMO experiments or draft manuscript prose.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from claim_policy import PERMITTED_CLAIM, forbidden_claim_hits  # noqa: E402

EXPERIMENT = "phase12_reproducibility_and_future_claim_inputs"
REQUIREMENTS_COVERED = ["CLAIM-03", "REPRO-01", "REPRO-02", "REPRO-03"]
DEFAULT_OUT_DIR = Path("experiments/dual_sensitivity")

OUTPUT_FILENAMES = {
    "package": "phase12_reproducibility_package.json",
    "provenance": "phase12_provenance_manifest.json",
    "table": "phase12_table_inputs.csv",
    "claim_inputs": "phase12_claim_inputs.json",
    "claim_audit": "phase12_claim_audit.json",
    "reproduction": "phase12_reproduction_manifest.json",
    "summary": "phase12_summary.md",
}

TABLE_FIELDNAMES = [
    "claim_category",
    "claim_allowed",
    "source_key",
    "source_experiment",
    "source_path",
    "source_status",
    "parse_status",
    "evidence_role",
    "simulator",
    "network",
    "horizon_steps",
    "warmup_steps",
    "seed_count",
    "profile",
    "gate_status",
    "demand_multiplier",
    "metric",
    "value",
    "requirements_covered",
    "caveat",
]

SOURCE_REGISTRY: dict[str, dict[str, Any]] = {
    "phase7_theory_separation": {
        "path": "experiments/dual_sensitivity/phase7_theory_separation.json",
        "evidence_role": "static_theory_separation",
        "requirements": ["CLAIM-03", "REPRO-01", "REPRO-03"],
        "accepted_statuses": ["PASSED"],
        "rerun_command": "python scripts/check_theory_separation.py --out experiments/dual_sensitivity/phase7_theory_separation.json",
        "caveat_policy": "static theory/separation only; no closed-loop or deployment claim",
    },
    "phase9_slack_binding_gates": {
        "path": "experiments/dual_sensitivity/phase9_slack_binding_gates.json",
        "evidence_role": "static_gate_a_b_slack_binding",
        "requirements": ["CLAIM-03", "REPRO-01", "REPRO-03"],
        "accepted_statuses": ["PASSED"],
        "rerun_command": "python scripts/run_slack_binding_gates.py --out experiments/dual_sensitivity/phase9_slack_binding_gates.json",
        "caveat_policy": "Gate A/B static checks only; no Gate C paired-seed closed-loop evidence",
    },
    "phase10_baselines_stress_suite": {
        "path": "experiments/dual_sensitivity/phase10_baselines_stress_suite.json",
        "evidence_role": "baseline_stress_capability_context",
        "requirements": ["CLAIM-03", "REPRO-01", "REPRO-02", "REPRO-03"],
        "accepted_statuses": ["SMOKE_ONLY", "PASSED"],
        "strict_statuses": ["SMOKE_ONLY", "PASSED"],
        "rerun_command": "python scripts/run_closed_loop_suite.py --profile smoke --out experiments/dual_sensitivity/phase10_baselines_stress_suite.json",
        "caveat_policy": "smoke/spec capability context only; not dominance or superiority evidence",
    },
    "phase11_long_horizon_paired_seed_evidence": {
        "path": "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json",
        "evidence_role": "closed_loop_paired_seed_gate_c_source",
        "requirements": ["CLAIM-03", "REPRO-01", "REPRO-02", "REPRO-03"],
        "accepted_statuses": ["PASSED"],
        "rerun_command": "python scripts/run_phase11_paired_evidence.py --out experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json",
        "caveat_policy": "long-horizon rows must be fully executed before supporting Gate C claims",
    },
    "phase11_gate_c_paired_evidence": {
        "path": "experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json",
        "evidence_role": "closed_loop_gate_c_binding_regime_status",
        "requirements": ["CLAIM-03", "REPRO-01", "REPRO-02", "REPRO-03"],
        "accepted_statuses": ["PASSED"],
        "rerun_command": "python scripts/run_gate_c_paired_evidence.py --input experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json --out experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json --strict",
        "caveat_policy": "Gate C must be PASSED before binding-regime closed-loop superiority inputs are claim-eligible",
    },
}

SOURCE_REQUIRED_KEYS: dict[str, tuple[str, ...]] = {
    "phase7_theory_separation": (
        "generated_by",
        "requirements_covered",
        "one_step_objective_definition",
        "criteria",
        "claim_scope",
        "guarantee_candidates",
        "examples",
    ),
    "phase9_slack_binding_gates": (
        "requirements_covered",
        "inputs",
        "gate_a_slack_recovery",
        "gate_b_binding_separation",
        "fail_closed_checks",
        "caveats",
    ),
    "phase10_baselines_stress_suite": (
        "route_decision",
        "claim_framing",
        "profile",
        "scenario_results",
        "aggregates",
        "baseline_coverage",
        "strong_baseline_coverage",
        "stress_scenario_coverage",
    ),
    "phase11_long_horizon_paired_seed_evidence": (
        "route_decision",
        "profile",
        "steps",
        "warmup",
        "execution_mode",
        "scenario_results",
        "actual_row_count",
        "expected_row_count",
        "all_rows_executed",
    ),
    "phase11_gate_c_paired_evidence": (
        "requirements_covered",
        "input_artifact",
        "input_status",
        "profile_eligibility",
        "binding_regime_dominance",
        "slack_regime_recovery_or_context",
        "inconclusive",
        "not_evidence",
        "required_binding_scenarios",
        "required_gate_c_comparators",
        "gate_c_primary_metrics_v1",
    ),
}

REQUIRED_PHASE11_PROFILE = "main"
REQUIRED_PHASE11_STEPS = 3600
REQUIRED_PHASE11_WARMUP = 900
REQUIRED_PHASE11_ROW_COUNT = 2160
REQUIRED_GATE_C_SCENARIOS = {
    "arterial_downstream_blockage",
    "arterial_spillback_stress",
    "arterial_incident_capacity_drop",
    "arterial_oversaturation",
    "arterial_turning_shock",
    "arterial_switching_loss_sensitive",
}
REQUIRED_GATE_C_COMPARATORS = {
    "max_pressure",
    "capacity_aware_pressure",
    "finite_storage_double_pressure",
}

PHASE12_FORBIDDEN_PHRASES = (
    "deployment dominance",
    "universal deployment dominance",
    "manuscript drafting",
    "final manuscript prose",
    "phase 10 proves superiority",
    "phase 10 dominance",
    "phase 11 inconclusive dominance",
    "phase 11 proves dominance",
    "smoke_only superiority",
    "inconclusive evidence of superiority",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_status(value: Any, default: str = "UNKNOWN") -> str:
    if value is None or value == "":
        return default
    return str(value).upper()


def resolve_path(path: Path | str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def registry_with_overrides(overrides: dict[str, Path] | None = None) -> dict[str, dict[str, Any]]:
    registry = {key: dict(value) for key, value in SOURCE_REGISTRY.items()}
    for key, path in (overrides or {}).items():
        if key not in registry:
            raise KeyError(f"unknown source override: {key}")
        registry[key]["path"] = str(path)
    return registry


def _source_record_base(source_key: str, entry: dict[str, Any], path: Path) -> dict[str, Any]:
    return {
        "source_key": source_key,
        "source_path": str(path),
        "evidence_role": entry["evidence_role"],
        "requirements": list(entry["requirements"]),
        "accepted_statuses": list(entry["accepted_statuses"]),
        "rerun_command": entry["rerun_command"],
        "caveat_policy": entry["caveat_policy"],
        "exists": path.exists(),
        "parse_status": "UNKNOWN",
        "source_status": "UNKNOWN",
        "input_status": "UNKNOWN",
        "generated_at": "unknown",
        "parse_error": "",
        "payload": None,
        "caveats": [],
        "claim_ready": False,
    }


def _artifact_validation_reasons(source_key: str, entry: dict[str, Any], payload: dict[str, Any], source_status: str) -> list[str]:
    reasons = []
    expected_experiment = source_key
    if payload.get("experiment") != expected_experiment:
        reasons.append(f"source artifact experiment mismatch: expected {expected_experiment}, got {payload.get('experiment') or 'missing'}")
    for key in SOURCE_REQUIRED_KEYS[source_key]:
        if key not in payload:
            reasons.append(f"source artifact missing required key: {key}")

    if source_key == "phase7_theory_separation":
        if payload.get("generated_by") != "scripts/check_theory_separation.py":
            reasons.append("phase7 generated_by does not match checker script")
        raw_examples = payload.get("examples")
        if isinstance(raw_examples, dict):
            example_names = set(raw_examples)
        elif isinstance(raw_examples, list):
            example_names = {str(item.get("name")) for item in raw_examples if isinstance(item, dict)}
        else:
            example_names = set()
        if "slack_recovery" not in example_names:
            reasons.append("phase7 examples.slack_recovery is missing")
        if "storage_binding_two_phase_separation" not in example_names:
            reasons.append("phase7 examples.storage_binding_two_phase_separation is missing")

    if source_key == "phase10_baselines_stress_suite":
        rows = payload.get("scenario_results")
        if not isinstance(rows, list) or not rows:
            reasons.append("phase10 scenario_results are missing or empty")
        for key in ("baseline_coverage", "strong_baseline_coverage", "stress_scenario_coverage"):
            if not isinstance(payload.get(key), dict):
                reasons.append(f"{key} is missing or not an object")

    if source_key == "phase9_slack_binding_gates":
        for gate_key in ("gate_a_slack_recovery", "gate_b_binding_separation"):
            gate = payload.get(gate_key)
            if not isinstance(gate, dict) or normalize_status(gate.get("status")) != "PASSED":
                reasons.append(f"{gate_key} is not PASSED")

    if source_key == "phase11_long_horizon_paired_seed_evidence":
        rows = payload.get("scenario_results")
        if not isinstance(rows, list):
            reasons.append("phase11 scenario_results are missing or not a list")
        actual = payload.get("actual_row_count")
        expected = payload.get("expected_row_count")
        try:
            actual_int = int(actual)
            expected_int = int(expected)
        except (TypeError, ValueError):
            actual_int = -1
            expected_int = -1
            reasons.append("phase11 row counts are missing or non-integer")
        if source_status == "PASSED":
            if payload.get("profile") != REQUIRED_PHASE11_PROFILE:
                reasons.append("phase11 profile is not main")
            if int(payload.get("steps", 0) or 0) != REQUIRED_PHASE11_STEPS:
                reasons.append("phase11 steps is not 3600")
            if int(payload.get("warmup", 0) or 0) != REQUIRED_PHASE11_WARMUP:
                reasons.append("phase11 warmup is not 900")
            if payload.get("all_rows_executed") is not True:
                reasons.append("phase11 all_rows_executed is not true")
            if actual_int != expected_int:
                reasons.append("phase11 actual_row_count does not match expected_row_count")
            if expected_int < REQUIRED_PHASE11_ROW_COUNT:
                reasons.append("phase11 expected_row_count is below required main-profile count 2160")
            if isinstance(rows, list) and len(rows) != actual_int:
                reasons.append("phase11 scenario_results length does not match actual_row_count")

    if source_key == "phase11_gate_c_paired_evidence":
        eligibility = payload.get("profile_eligibility") if isinstance(payload.get("profile_eligibility"), dict) else {}
        metrics = payload.get("gate_c_primary_metrics_v1") if isinstance(payload.get("gate_c_primary_metrics_v1"), dict) else {}
        required_scenarios = payload.get("required_binding_scenarios") if isinstance(payload.get("required_binding_scenarios"), list) else []
        required_comparators = payload.get("required_gate_c_comparators") if isinstance(payload.get("required_gate_c_comparators"), list) else []
        metric_results = metrics.get("metric_results") if isinstance(metrics.get("metric_results"), list) else []
        if source_status == "PASSED":
            if normalize_status(payload.get("input_status")) != "PASSED":
                reasons.append("gate c input_status is not PASSED")
            if eligibility.get("profile") != REQUIRED_PHASE11_PROFILE:
                reasons.append("gate c profile_eligibility.profile is not main")
            if int(eligibility.get("steps", 0) or 0) != REQUIRED_PHASE11_STEPS:
                reasons.append("gate c profile_eligibility.steps is not 3600")
            if int(eligibility.get("warmup", 0) or 0) != REQUIRED_PHASE11_WARMUP:
                reasons.append("gate c profile_eligibility.warmup is not 900")
            if eligibility.get("eligible") is not True:
                reasons.append("gate c profile_eligibility.eligible is not true")
            if eligibility.get("all_rows_executed") is not True:
                reasons.append("gate c profile_eligibility.all_rows_executed is not true")
            try:
                actual = int(eligibility.get("actual_row_count"))
                expected = int(eligibility.get("expected_row_count"))
            except (TypeError, ValueError):
                actual = -1
                expected = -1
                reasons.append("gate c row counts are missing or non-integer")
            if actual != expected:
                reasons.append("gate c actual_row_count does not match expected_row_count")
            if expected < REQUIRED_PHASE11_ROW_COUNT:
                reasons.append("gate c expected_row_count is below required main-profile count 2160")
            if normalize_status(metrics.get("status")) != "PASSED":
                reasons.append("gate c primary metrics status is not PASSED")
            missing_scenarios = sorted(REQUIRED_GATE_C_SCENARIOS - set(required_scenarios))
            if missing_scenarios:
                reasons.append(f"gate c required binding scenarios are missing: {missing_scenarios}")
            missing_comparators = sorted(REQUIRED_GATE_C_COMPARATORS - set(required_comparators))
            if missing_comparators:
                reasons.append(f"gate c required comparators are missing: {missing_comparators}")
            if not metric_results:
                reasons.append("gate c primary metric_results are empty")
    return reasons


def load_source_record(source_key: str, entry: dict[str, Any]) -> dict[str, Any]:
    path = resolve_path(entry["path"])
    record = _source_record_base(source_key, entry, path)
    if not path.exists():
        record.update(
            {
                "parse_status": "MISSING",
                "source_status": "MISSING",
                "input_status": "INCONCLUSIVE",
                "caveats": [f"required source artifact is missing: {path}"],
            }
        )
        return record

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("source artifact must contain a JSON object")
    except Exception as exc:  # noqa: BLE001 - artifact parser must not crash non-strict generation.
        record.update(
            {
                "parse_status": "FAILED",
                "source_status": "FAILED",
                "input_status": "FAILED",
                "parse_error": str(exc),
                "caveats": [f"source artifact could not be parsed: {exc}"],
            }
        )
        return record

    source_status = normalize_status(payload.get("status"))
    input_status = normalize_status(payload.get("input_status", source_status))
    accepted = set(entry.get("accepted_statuses", []))
    payload_caveats = payload.get("caveats", [])
    if not isinstance(payload_caveats, list):
        payload_caveats = [str(payload_caveats)]
    validation_reasons = _artifact_validation_reasons(source_key, entry, payload, source_status)
    caveats = [entry["caveat_policy"], *[str(item) for item in payload_caveats]]
    if source_status not in accepted:
        caveats.append(f"source status {source_status} is not accepted for claim-ready evidence")
    caveats.extend(validation_reasons)

    record.update(
        {
            "parse_status": "PASSED" if not validation_reasons else "FAILED",
            "source_status": source_status,
            "input_status": input_status,
            "generated_at": payload.get("generated_at", "unknown"),
            "payload": payload,
            "caveats": caveats,
            "claim_ready": source_status in accepted and not validation_reasons,
            "validation_reasons": validation_reasons,
        }
    )
    return record


def load_source_records(registry: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return [load_source_record(key, entry) for key, entry in (registry or SOURCE_REGISTRY).items()]


def _payload(record: dict[str, Any]) -> dict[str, Any]:
    payload = record.get("payload")
    return payload if isinstance(payload, dict) else {}


def _unique_values(rows: list[dict[str, Any]], key: str) -> list[Any]:
    values = []
    seen = set()
    for row in rows:
        value = row.get(key)
        marker = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
        if value is not None and marker not in seen:
            values.append(value)
            seen.add(marker)
    return values


def _qualifiers(record: dict[str, Any]) -> dict[str, Any]:
    payload = _payload(record)
    scenario_rows = payload.get("scenario_results") or payload.get("rows") or payload.get("raw_rows") or []
    if not isinstance(scenario_rows, list):
        scenario_rows = []
    networks = _unique_values([row for row in scenario_rows if isinstance(row, dict)], "network")
    seed_values = _unique_values([row for row in scenario_rows if isinstance(row, dict)], "seed")
    demand_values = _unique_values([row for row in scenario_rows if isinstance(row, dict)], "demand_multiplier")
    profile = payload.get("profile", "unknown")
    if record["source_key"] == "phase11_gate_c_paired_evidence":
        eligibility = payload.get("profile_eligibility", {}) if isinstance(payload.get("profile_eligibility"), dict) else {}
        profile = eligibility.get("profile", profile)
        horizon = eligibility.get("steps", payload.get("steps", "unknown"))
        warmup = eligibility.get("warmup", payload.get("warmup", "unknown"))
        seed_count = payload.get("seed_count", "unknown")
    else:
        horizon = payload.get("steps") or (scenario_rows[0].get("steps") if scenario_rows and isinstance(scenario_rows[0], dict) else "unknown")
        warmup = payload.get("warmup") or (scenario_rows[0].get("warmup") if scenario_rows and isinstance(scenario_rows[0], dict) else "unknown")
        seed_count = len(seed_values) if seed_values else payload.get("seed_count", "unknown")
    if record["source_key"] == "phase11_long_horizon_paired_seed_evidence":
        seed_count = payload.get("seed_count") or len(payload.get("seeds", [])) or payload.get("actual_row_count", "unknown")
        demand_values = payload.get("demand_multipliers", demand_values)
    return {
        "simulator": payload.get("simulator", "SUMO" if record["source_key"] in {"phase10_baselines_stress_suite", "phase11_long_horizon_paired_seed_evidence", "phase11_gate_c_paired_evidence"} else "analytic/static"),
        "network": ",".join(str(item) for item in networks) if networks else payload.get("network", "unknown"),
        "horizon_steps": horizon if horizon is not None else "unknown",
        "warmup_steps": warmup if warmup is not None else "unknown",
        "seed_count": seed_count if seed_count is not None else "unknown",
        "profile": profile if profile is not None else "unknown",
        "gate_status": payload.get("gate_c_primary_metrics_v1", {}).get("status", payload.get("status", record["source_status"])) if isinstance(payload.get("gate_c_primary_metrics_v1", {}), dict) else payload.get("status", record["source_status"]),
        "demand_multiplier": ",".join(str(item) for item in demand_values) if demand_values else "unknown",
    }


def _claim_category(record: dict[str, Any]) -> str:
    return {
        "phase7_theory_separation": "static_binding_separation_and_slack_recovery",
        "phase9_slack_binding_gates": "slack_recovery_tie_and_static_binding_separation",
        "phase10_baselines_stress_suite": "baseline_stress_capability_context",
        "phase11_long_horizon_paired_seed_evidence": "limitations_and_reproduction_notes",
        "phase11_gate_c_paired_evidence": "closed_loop_gate_c_status",
    }[record["source_key"]]


def _claim_allowed(record: dict[str, Any]) -> bool:
    if record["parse_status"] != "PASSED":
        return False
    if record["source_key"] == "phase10_baselines_stress_suite":
        return False
    if record["source_key"] in {"phase11_long_horizon_paired_seed_evidence", "phase11_gate_c_paired_evidence"}:
        return record["claim_ready"] is True
    return record["claim_ready"] is True


def build_claim_inputs(source_records: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    for record in source_records:
        qualifiers = _qualifiers(record)
        allowed = _claim_allowed(record)
        caveat = "; ".join(record.get("caveats") or [record["caveat_policy"]])
        if not allowed and record["source_key"].startswith("phase11"):
            caveat = f"limitation/context only because source status is {record['source_status']}; {caveat}"
        records.append(
            {
                "claim_category": _claim_category(record),
                "claim_allowed": allowed,
                "source_key": record["source_key"],
                "source_status": record["source_status"],
                "parse_status": record["parse_status"],
                "evidence_role": record["evidence_role"],
                "simulator": qualifiers["simulator"],
                "network": qualifiers["network"],
                "horizon_steps": qualifiers["horizon_steps"],
                "warmup_steps": qualifiers["warmup_steps"],
                "seed_count": qualifiers["seed_count"],
                "profile": qualifiers["profile"],
                "gate_status": qualifiers["gate_status"],
                "demand_multiplier": qualifiers["demand_multiplier"],
                "requirements_covered": list(record["requirements"]),
                "permitted_claim_boundary": PERMITTED_CLAIM,
                "caveat": caveat,
            }
        )
    return {
        "experiment": "phase12_claim_inputs",
        "requirements_covered": REQUIREMENTS_COVERED,
        "records": records,
        "claim_discipline": "bounded machine-readable inputs only; no manuscript prose or universal/deployment claim",
    }


def build_table_rows(claim_inputs: dict[str, Any], source_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {record["source_key"]: record for record in source_records}
    rows = []
    for claim in claim_inputs["records"]:
        source = by_key[claim["source_key"]]
        payload = _payload(source)
        metric = "status"
        value = source["source_status"]
        if source["source_key"] == "phase9_slack_binding_gates":
            metric = "gate_a_gate_b_status"
            value = f"{payload.get('gate_a_slack_recovery', {}).get('status', 'unknown')}/{payload.get('gate_b_binding_separation', {}).get('status', 'unknown')}"
        elif source["source_key"] == "phase11_long_horizon_paired_seed_evidence":
            metric = "actual_vs_expected_rows"
            value = f"{payload.get('actual_row_count', 'unknown')}/{payload.get('expected_row_count', 'unknown')}"
        rows.append(
            {
                "claim_category": claim["claim_category"],
                "claim_allowed": str(claim["claim_allowed"]).lower(),
                "source_key": claim["source_key"],
                "source_experiment": payload.get("experiment", claim["source_key"]),
                "source_path": source["source_path"],
                "source_status": source["source_status"],
                "parse_status": source["parse_status"],
                "evidence_role": claim["evidence_role"],
                "simulator": claim["simulator"],
                "network": claim["network"],
                "horizon_steps": claim["horizon_steps"],
                "warmup_steps": claim["warmup_steps"],
                "seed_count": claim["seed_count"],
                "profile": claim["profile"],
                "gate_status": claim["gate_status"],
                "demand_multiplier": claim["demand_multiplier"],
                "metric": metric,
                "value": value,
                "requirements_covered": ";".join(claim["requirements_covered"]),
                "caveat": claim["caveat"],
            }
        )
    return rows


def build_reproduction_manifest(out_dir: Path, source_records: list[dict[str, Any]]) -> dict[str, Any]:
    commands = [
        {
            "name": "fast_phase12_direct_tests",
            "command": "python tests/test_phase12_reproducibility_inputs.py",
            "runtime_profile": "fast_cpu",
            "strict": True,
            "gpu_required": False,
            "requirements": REQUIREMENTS_COVERED,
            "expected_artifacts": [],
            "claim_note": "validates source loading, provenance, claim audit, and strict mode with synthetic artifacts",
        },
        {
            "name": "regenerate_phase7_theory_separation",
            "command": SOURCE_REGISTRY["phase7_theory_separation"]["rerun_command"],
            "runtime_profile": "fast_cpu_static",
            "strict": True,
            "gpu_required": False,
            "requirements": ["REPRO-01", "REPRO-03"],
            "expected_artifacts": [SOURCE_REGISTRY["phase7_theory_separation"]["path"]],
            "claim_note": "static theory/separation artifact regeneration",
        },
        {
            "name": "regenerate_phase9_slack_binding_gates",
            "command": SOURCE_REGISTRY["phase9_slack_binding_gates"]["rerun_command"],
            "runtime_profile": "fast_cpu_static",
            "strict": True,
            "gpu_required": False,
            "requirements": ["REPRO-01", "REPRO-03"],
            "expected_artifacts": [SOURCE_REGISTRY["phase9_slack_binding_gates"]["path"]],
            "claim_note": "Gate A/B static artifact regeneration",
        },
        {
            "name": "summarize_phase11_fail_closed_or_completed_rows",
            "command": "python scripts/run_phase11_paired_evidence.py --out experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json",
            "runtime_profile": "cpu_sumo_summary_fail_closed",
            "strict": False,
            "gpu_required": False,
            "requirements": ["REPRO-02", "REPRO-03"],
            "expected_artifacts": [SOURCE_REGISTRY["phase11_long_horizon_paired_seed_evidence"]["path"]],
            "claim_note": "packages Phase 11 status; does not require default completion of opt-in long-horizon suite",
        },
        {
            "name": "strict_gate_c_validation",
            "command": SOURCE_REGISTRY["phase11_gate_c_paired_evidence"]["rerun_command"],
            "runtime_profile": "fast_cpu_gate_check",
            "strict": True,
            "gpu_required": False,
            "requirements": ["CLAIM-03", "REPRO-03"],
            "expected_artifacts": [SOURCE_REGISTRY["phase11_gate_c_paired_evidence"]["path"]],
            "claim_note": "expected to exit nonzero while Gate C source remains non-PASSED",
        },
        {
            "name": "generate_phase12_non_strict_package",
            "command": f"python scripts/run_phase12_reproducibility_inputs.py --out-dir {out_dir}",
            "runtime_profile": "fast_cpu_packaging",
            "strict": False,
            "gpu_required": False,
            "requirements": REQUIREMENTS_COVERED,
            "expected_artifacts": [str(out_dir / name) for name in OUTPUT_FILENAMES.values()],
            "claim_note": "writes auditable package even when upstream evidence is inconclusive",
        },
        {
            "name": "validate_phase12_strict_package",
            "command": f"python scripts/run_phase12_reproducibility_inputs.py --out-dir {out_dir} --strict",
            "runtime_profile": "fast_cpu_packaging",
            "strict": True,
            "gpu_required": False,
            "requirements": REQUIREMENTS_COVERED,
            "expected_artifacts": [str(out_dir / name) for name in OUTPUT_FILENAMES.values()],
            "claim_note": "fails nonzero unless source statuses and generated claim audit pass",
        },
        {
            "name": "opt_in_long_horizon_phase11_execution",
            "command": "python scripts/run_phase11_paired_evidence.py --profile main --execution-row-limit 2160 --progress-out experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.progress.json --resume-progress experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.progress.json --out experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json",
            "runtime_profile": "opt_in_cpu_sumo_long_horizon",
            "strict": True,
            "gpu_required": False,
            "requirements": ["REPRO-02", "REPRO-03"],
            "expected_artifacts": [
                SOURCE_REGISTRY["phase11_long_horizon_paired_seed_evidence"]["path"],
                "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.progress.json",
            ],
            "claim_note": "expensive SUMO execution is opt-in/fail-closed, uses row-level progress/resume, and is not run by Phase 12 generation",
        },
    ]
    return {
        "experiment": "phase12_reproduction_manifest",
        "requirements_covered": REQUIREMENTS_COVERED,
        "source_statuses": {record["source_key"]: record["source_status"] for record in source_records},
        "commands": commands,
        "constraints": ["CPU/SUMO-oriented", "no GPU dependency", "no package installation command", "long-horizon execution opt-in only"],
    }


def build_provenance_manifest(out_dir: Path, source_records: list[dict[str, Any]], reproduction_manifest: dict[str, Any]) -> dict[str, Any]:
    generated_artifacts = [str(out_dir / name) for name in OUTPUT_FILENAMES.values()]
    sources = [
        {
            "source_key": record["source_key"],
            "source_path": record["source_path"],
            "source_status": record["source_status"],
            "parse_status": record["parse_status"],
            "evidence_role": record["evidence_role"],
            "requirements": record["requirements"],
            "generated_at": record["generated_at"],
            "rerun_command": record["rerun_command"],
            "caveats": record["caveats"],
        }
        for record in source_records
    ]
    entries = []
    for artifact in generated_artifacts:
        entries.append(
            {
                "derived_artifact": artifact,
                "raw_sources": [record["source_path"] for record in source_records],
                "source_statuses": {record["source_key"]: record["source_status"] for record in source_records},
                "generation_command": f"python scripts/run_phase12_reproducibility_inputs.py --out-dir {out_dir}",
                "requirements": REQUIREMENTS_COVERED,
                "caveats": sorted({caveat for record in source_records for caveat in record.get("caveats", [])}),
            }
        )
    return {
        "experiment": "phase12_provenance_manifest",
        "requirements_covered": REQUIREMENTS_COVERED,
        "sources": sources,
        "derived_artifacts": entries,
        "reproduction_command_names": [command["name"] for command in reproduction_manifest["commands"]],
    }


def render_summary(package: dict[str, Any], claim_inputs: dict[str, Any]) -> str:
    lines = [
        "# Phase 12 Reproducibility and Future-Claim Input Summary",
        "",
        "This audit summary is generated from raw Phase 7/9/10/11 artifacts and is not manuscript prose.",
        "",
        f"- Package status: {package['status']}",
        f"- Requirements covered: {', '.join(package['requirements_covered'])}",
        f"- Claim audit status: {package['claim_audit_status']}",
        "",
        "## Source Statuses",
    ]
    for key, status in package["source_status_summary"].items():
        lines.append(f"- {key}: {status}")
    lines.extend(["", "## Claim Inputs"])
    for row in claim_inputs["records"]:
        lines.append(
            f"- {row['source_key']}: category={row['claim_category']}; allowed={row['claim_allowed']}; "
            f"status={row['source_status']}; network={row['network']}; horizon={row['horizon_steps']}; "
            f"seeds={row['seed_count']}; profile={row['profile']}; gate_status={row['gate_status']}"
        )
    lines.extend(["", "## Caveats"])
    for caveat in package["caveats"]:
        lines.append(f"- {caveat}")
    return "\n".join(lines).rstrip() + "\n"


def _phase12_specific_hits(text: str, source: str, gate_c_status: str) -> list[dict[str, str]]:
    lowered = text.lower()
    hits = [
        {"source": source, "path": source, "phrase": phrase}
        for phrase in PHASE12_FORBIDDEN_PHRASES
        if phrase in lowered
    ]
    if gate_c_status != "PASSED" and "gate c passed" in lowered:
        hits.append({"source": source, "path": source, "phrase": "Gate C passed"})
    return hits


def audit_generated_outputs(surfaces: dict[str, str], gate_c_status: str) -> dict[str, Any]:
    hits: list[dict[str, str]] = []
    for source, text in surfaces.items():
        hits.extend(forbidden_claim_hits(text, source=source))
        hits.extend(_phase12_specific_hits(text, source, gate_c_status))
    return {
        "experiment": "phase12_claim_audit",
        "requirements_covered": ["CLAIM-03", "REPRO-03"],
        "status": "PASSED" if not hits else "FAILED",
        "hit_count": len(hits),
        "hits": hits,
        "scanned_surfaces": sorted(surfaces),
    }


def strict_reasons(source_records: list[dict[str, Any]], claim_audit: dict[str, Any]) -> list[str]:
    reasons = []
    for record in source_records:
        if record["parse_status"] != "PASSED":
            reasons.append(f"{record['source_key']} parse status is {record['parse_status']}")
            continue
        strict_statuses = set(SOURCE_REGISTRY[record["source_key"]].get("strict_statuses", SOURCE_REGISTRY[record["source_key"]]["accepted_statuses"]))
        if record["source_status"] not in strict_statuses:
            reasons.append(f"{record['source_key']} source status is {record['source_status']}, expected one of {sorted(strict_statuses)}")
    if claim_audit["status"] != "PASSED":
        reasons.append("generated claim audit contains forbidden claim hits")
    return reasons


def package_status(source_records: list[dict[str, Any]], claim_audit: dict[str, Any]) -> str:
    if claim_audit["status"] != "PASSED" or any(record["parse_status"] == "FAILED" for record in source_records):
        return "FAILED"
    if any(record["parse_status"] != "PASSED" for record in source_records):
        return "INCONCLUSIVE"
    if any(
        record["source_status"] not in set(SOURCE_REGISTRY[record["source_key"]].get("strict_statuses", SOURCE_REGISTRY[record["source_key"]]["accepted_statuses"]))
        for record in source_records
    ):
        return "INCONCLUSIVE"
    return "PASSED"


def _audit_surfaces(
    package: dict[str, Any],
    claim_inputs: dict[str, Any],
    table_rows: list[dict[str, Any]],
    provenance_manifest: dict[str, Any],
    reproduction_manifest: dict[str, Any],
    summary_text: str,
) -> dict[str, str]:
    return {
        "phase12_reproducibility_package.json": json.dumps(package, sort_keys=True),
        "phase12_claim_inputs.json": json.dumps(claim_inputs, sort_keys=True),
        "phase12_provenance_manifest.json": json.dumps(provenance_manifest, sort_keys=True),
        "phase12_reproduction_manifest.json": json.dumps(reproduction_manifest, sort_keys=True),
        "phase12_table_inputs.csv": render_csv_text(table_rows),
        "phase12_summary.md": summary_text,
    }


def build_phase12_package(out_dir: Path, registry: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    source_records = load_source_records(registry)
    claim_inputs = build_claim_inputs(source_records)
    table_rows = build_table_rows(claim_inputs, source_records)
    reproduction_manifest = build_reproduction_manifest(out_dir, source_records)
    provenance_manifest = build_provenance_manifest(out_dir, source_records, reproduction_manifest)

    gate_c_record = next(record for record in source_records if record["source_key"] == "phase11_gate_c_paired_evidence")
    package = {
        "experiment": EXPERIMENT,
        "status": "UNKNOWN",
        "requirements_covered": REQUIREMENTS_COVERED,
        "generated_by": "scripts/run_phase12_reproducibility_inputs.py",
        "generated_at": utc_now(),
        "source_status_summary": {record["source_key"]: record["source_status"] for record in source_records},
        "derived_outputs": [str(out_dir / name) for name in OUTPUT_FILENAMES.values()],
        "claim_eligibility_summary": {
            row["source_key"]: row["claim_allowed"] for row in claim_inputs["records"]
        },
        "claim_audit_status": "UNKNOWN",
        "strict_mode_reasons": [],
        "caveats": sorted({caveat for record in source_records for caveat in record.get("caveats", [])}),
    }
    placeholder_audit = {"status": "PASSED", "hits": []}
    package["status"] = package_status(source_records, placeholder_audit)
    package["strict_mode_reasons"] = strict_reasons(source_records, placeholder_audit)
    summary_text = render_summary(package, claim_inputs)
    surfaces = _audit_surfaces(package, claim_inputs, table_rows, provenance_manifest, reproduction_manifest, summary_text)
    claim_audit = audit_generated_outputs(surfaces, gate_c_record["source_status"])
    package["claim_audit_status"] = claim_audit["status"]
    package["status"] = package_status(source_records, claim_audit)
    package["strict_mode_reasons"] = strict_reasons(source_records, claim_audit)
    summary_text = render_summary(package, claim_inputs)
    final_surfaces = _audit_surfaces(package, claim_inputs, table_rows, provenance_manifest, reproduction_manifest, summary_text)
    claim_audit = audit_generated_outputs(final_surfaces, gate_c_record["source_status"])
    package["claim_audit_status"] = claim_audit["status"]
    package["status"] = package_status(source_records, claim_audit)
    package["strict_mode_reasons"] = strict_reasons(source_records, claim_audit)
    summary_text = render_summary(package, claim_inputs)

    return {
        "package": package,
        "source_records": source_records,
        "claim_inputs": claim_inputs,
        "table_rows": table_rows,
        "provenance_manifest": provenance_manifest,
        "reproduction_manifest": reproduction_manifest,
        "claim_audit": claim_audit,
        "summary_markdown": summary_text,
    }


def render_csv_text(rows: list[dict[str, Any]]) -> str:
    import io

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=TABLE_FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def write_phase12_artifacts(out_dir: Path, payloads: dict[str, Any]) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {key: out_dir / name for key, name in OUTPUT_FILENAMES.items()}
    paths["package"].write_text(json.dumps(payloads["package"], indent=2), encoding="utf-8")
    paths["provenance"].write_text(json.dumps(payloads["provenance_manifest"], indent=2), encoding="utf-8")
    paths["claim_inputs"].write_text(json.dumps(payloads["claim_inputs"], indent=2), encoding="utf-8")
    paths["claim_audit"].write_text(json.dumps(payloads["claim_audit"], indent=2), encoding="utf-8")
    paths["reproduction"].write_text(json.dumps(payloads["reproduction_manifest"], indent=2), encoding="utf-8")
    paths["summary"].write_text(payloads["summary_markdown"], encoding="utf-8")
    with paths["table"].open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TABLE_FIELDNAMES)
        writer.writeheader()
        writer.writerows(payloads["table_rows"])
    return paths


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--strict", action="store_true")
    for key in SOURCE_REGISTRY:
        parser.add_argument(f"--{key.replace('_', '-')}", dest=key, default=None, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    out_dir = resolve_path(args.out_dir)
    overrides = {key: Path(value) for key in SOURCE_REGISTRY if (value := getattr(args, key))}
    payloads = build_phase12_package(out_dir, registry_with_overrides(overrides))
    paths = write_phase12_artifacts(out_dir, payloads)
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "status": payloads["package"]["status"],
                "claim_audit_status": payloads["claim_audit"]["status"],
                "generated_files": [str(path) for path in paths.values()],
                "strict_mode_reasons": payloads["package"]["strict_mode_reasons"],
            },
            indent=2,
        )
    )
    if args.strict and payloads["package"]["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
