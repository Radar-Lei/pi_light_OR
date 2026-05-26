#!/usr/bin/env python3
"""Generate v1.4 claim refresh and milestone audit artifacts."""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from claim_policy import forbidden_claim_hits  # noqa: E402

EXPERIMENT = "v1_4_claim_refresh"
DEFAULT_OUT_DIR = Path("experiments/dual_sensitivity")
REQUIREMENTS_COVERED = ["CLAIM-01", "CLAIM-02", "CLAIM-03"]

OUTPUT_FILENAMES = {
    "package": "v1_4_reproducibility_package.json",
    "provenance": "v1_4_provenance_manifest.json",
    "table": "v1_4_table_inputs.csv",
    "claim_inputs": "v1_4_claim_inputs.json",
    "claim_audit": "v1_4_claim_audit.json",
    "reproduction": "v1_4_reproduction_manifest.json",
    "summary": "v1_4_summary.md",
    "milestone_audit": "v1_4_milestone_audit.json",
    "milestone_audit_md": "v1_4_milestone_audit.md",
}

TABLE_FIELDNAMES = [
    "source_key",
    "source_status",
    "parse_status",
    "evidence_role",
    "claim_category",
    "claim_allowed",
    "gate_status",
    "source_path",
    "caveat",
]

SOURCE_REGISTRY: dict[str, dict[str, Any]] = {
    "v1_4_failure_diagnostics": {
        "path": "experiments/dual_sensitivity/v1_4_failure_diagnostics.json",
        "evidence_role": "failure_diagnostic_explanatory",
        "claim_category": "diagnostic_context",
        "required_keys": ["experiment", "status", "claim_boundary", "workstreams"],
        "rerun_command": "python scripts/run_v14_failure_diagnostics.py",
    },
    "v1_4_workstream_pilot_index": {
        "path": "experiments/dual_sensitivity/v1_4_workstreams/index.json",
        "evidence_role": "exploratory_pilot_index_not_claim_evidence",
        "claim_category": "exploratory_method_search",
        "required_keys": ["experiment", "status", "claim_ready", "artifacts"],
        "rerun_command": "python scripts/run_v14_workstream_pilots.py",
    },
    "v1_4_candidate_convergence": {
        "path": "experiments/dual_sensitivity/v1_4_candidate_convergence.json",
        "evidence_role": "candidate_selection_not_final_evidence",
        "claim_category": "candidate_selection",
        "required_keys": ["experiment", "status", "selected_candidate", "locked_protocol_fingerprint"],
        "rerun_command": "python scripts/run_v14_candidate_convergence.py",
    },
    "v1_4_locked_gate_c_protocol": {
        "path": "experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json",
        "evidence_role": "pre_confirmation_protocol_lock",
        "claim_category": "locked_protocol",
        "required_keys": ["experiment", "status", "selected_controller_id", "required_comparators", "spec_fingerprint"],
        "rerun_command": "python scripts/run_v14_candidate_convergence.py",
    },
    "v1_4_locked_gate_c_execution": {
        "path": "experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json",
        "evidence_role": "locked_confirmation_execution_source",
        "claim_category": "locked_gate_c_execution",
        "required_keys": ["experiment", "status", "selected_controller_id", "locked_protocol_fingerprint", "row_audit"],
        "rerun_command": "python scripts/run_v14_locked_gate_c.py",
    },
    "v1_4_gate_c_paired_evidence": {
        "path": "experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json",
        "evidence_role": "strict_locked_gate_c_status",
        "claim_category": "closed_loop_gate_c_status",
        "required_keys": ["experiment", "status", "selected_controller_id", "locked_protocol_fingerprint", "gate_c_primary_metrics_v1"],
        "rerun_command": "python scripts/run_v14_gate_c_paired_evidence.py --strict",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def normalize_status(value: Any, default: str = "UNKNOWN") -> str:
    if value is None or value == "":
        return default
    return str(value).upper()


def load_source_record(source_key: str, entry: dict[str, Any]) -> dict[str, Any]:
    path = resolve_path(entry["path"])
    base = {
        "source_key": source_key,
        "source_path": str(path),
        "evidence_role": entry["evidence_role"],
        "claim_category": entry["claim_category"],
        "rerun_command": entry["rerun_command"],
        "exists": path.exists(),
        "parse_status": "UNKNOWN",
        "source_status": "UNKNOWN",
        "payload": None,
        "caveats": [],
    }
    if not path.exists():
        return {
            **base,
            "parse_status": "MISSING",
            "source_status": "MISSING",
            "caveats": [f"required source artifact is missing: {entry['path']}"],
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("source artifact must contain a JSON object")
    except Exception as exc:  # noqa: BLE001 - source parser must fail closed.
        return {
            **base,
            "parse_status": "FAILED",
            "source_status": "FAILED",
            "parse_error": str(exc),
            "caveats": [f"source artifact could not be parsed: {exc}"],
        }
    reasons = []
    for key in entry["required_keys"]:
        if key not in payload:
            reasons.append(f"source artifact missing required key: {key}")
    expected_experiment = source_key
    if payload.get("experiment") != expected_experiment:
        reasons.append(f"source artifact experiment mismatch: expected {expected_experiment}, got {payload.get('experiment') or 'missing'}")
    source_status = normalize_status(payload.get("status"))
    caveats = [str(item) for item in payload.get("caveats", [])] if isinstance(payload.get("caveats", []), list) else [str(payload.get("caveats"))]
    caveats.extend(reasons)
    return {
        **base,
        "parse_status": "PASSED" if not reasons else "FAILED",
        "source_status": source_status,
        "payload": payload,
        "caveats": caveats,
    }


def load_source_records(registry: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return [load_source_record(key, value) for key, value in (registry or SOURCE_REGISTRY).items()]


def payload_for(records: list[dict[str, Any]], key: str) -> dict[str, Any]:
    record = next((item for item in records if item["source_key"] == key), {})
    payload = record.get("payload")
    return payload if isinstance(payload, dict) else {}


def strict_gate_c_status(records: list[dict[str, Any]]) -> str:
    return normalize_status(payload_for(records, "v1_4_gate_c_paired_evidence").get("status"), "MISSING")


def closed_loop_superiority_claim_allowed(records: list[dict[str, Any]]) -> bool:
    return strict_gate_c_status(records) == "PASSED"


def build_claim_inputs(records: list[dict[str, Any]]) -> dict[str, Any]:
    gate_status = strict_gate_c_status(records)
    claim_allowed = closed_loop_superiority_claim_allowed(records)
    entries = []
    for record in records:
        source_claim_allowed = claim_allowed and record["source_key"] == "v1_4_gate_c_paired_evidence" and record["parse_status"] == "PASSED"
        entries.append(
            {
                "source_key": record["source_key"],
                "source_status": record["source_status"],
                "parse_status": record["parse_status"],
                "evidence_role": record["evidence_role"],
                "claim_category": record["claim_category"],
                "claim_allowed": source_claim_allowed,
                "gate_status": gate_status,
                "source_path": record["source_path"],
                "caveat": "; ".join(record.get("caveats") or ["No caveat"]),
            }
        )
    return {
        "experiment": "v1_4_claim_inputs",
        "requirements_covered": REQUIREMENTS_COVERED,
        "strict_gate_c_status": gate_status,
        "closed_loop_superiority_claim_allowed": claim_allowed,
        "records": entries,
        "claim_boundary": "Exploratory pilots and selection artifacts are not final closed-loop superiority evidence.",
    }


def build_table_rows(claim_inputs: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {field: str(record.get(field, "")) for field in TABLE_FIELDNAMES}
        for record in claim_inputs["records"]
    ]


def render_csv_text(rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=TABLE_FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def build_reproduction_manifest(out_dir: Path) -> dict[str, Any]:
    return {
        "experiment": "v1_4_reproduction_manifest",
        "requirements_covered": REQUIREMENTS_COVERED,
        "commands": [
            {
                "name": "regenerate_locked_execution_fail_closed",
                "command": "python scripts/run_v14_locked_gate_c.py",
                "strict": False,
                "expected_artifacts": ["experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json"],
                "claim_note": "Writes locked execution status without launching the opt-in main SUMO run.",
            },
            {
                "name": "strict_v1_4_gate_c",
                "command": "python scripts/run_v14_gate_c_paired_evidence.py --strict",
                "strict": True,
                "expected_artifacts": ["experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json"],
                "claim_note": "Exits nonzero while strict v1.4 Gate C is non-PASSED.",
            },
            {
                "name": "generate_v1_4_claim_refresh",
                "command": f"python scripts/run_v14_claim_refresh.py --out-dir {out_dir}",
                "strict": False,
                "expected_artifacts": [str(out_dir / name) for name in OUTPUT_FILENAMES.values()],
                "claim_note": "Writes claim refresh artifacts even when Gate C is inconclusive.",
            },
            {
                "name": "opt_in_locked_main_rows",
                "command": "python scripts/run_v14_locked_gate_c.py --execution-row-limit 1440 --progress-out experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json --resume-progress experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json",
                "strict": True,
                "expected_artifacts": [
                    "experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json",
                    "experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json",
                ],
                "claim_note": "Expensive SUMO confirmation run is explicit and resumable.",
            },
        ],
        "constraints": ["CPU/SUMO-oriented", "no GPU dependency", "exploratory artifacts cannot satisfy final Gate C"],
    }


def build_provenance_manifest(out_dir: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "experiment": "v1_4_provenance_manifest",
        "requirements_covered": REQUIREMENTS_COVERED,
        "sources": [
            {
                "source_key": record["source_key"],
                "source_path": record["source_path"],
                "source_status": record["source_status"],
                "parse_status": record["parse_status"],
                "evidence_role": record["evidence_role"],
                "rerun_command": record["rerun_command"],
            }
            for record in records
        ],
        "derived_artifacts": [str(out_dir / name) for name in OUTPUT_FILENAMES.values()],
    }


def render_summary(package: dict[str, Any], claim_inputs: dict[str, Any]) -> str:
    lines = [
        "# v1.4 Claim Refresh Summary",
        "",
        "This generated summary separates exploratory method-search artifacts from locked Gate C confirmation artifacts.",
        "",
        f"- Package status: {package['status']}",
        f"- Strict Gate C status: {package['strict_gate_c_status']}",
        f"- Closed-loop superiority claim allowed: {str(package['closed_loop_superiority_claim_allowed']).lower()}",
        "",
        "## Sources",
    ]
    for record in claim_inputs["records"]:
        lines.append(
            f"- {record['source_key']}: status={record['source_status']}; role={record['evidence_role']}; "
            f"claim_allowed={str(record['claim_allowed']).lower()}"
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            "Closed-loop superiority remains disallowed unless the locked v1.4 Gate C artifact becomes PASSED after the opt-in main rows are executed.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def audit_generated_outputs(surfaces: dict[str, str], gate_status: str) -> dict[str, Any]:
    hits: list[dict[str, str]] = []
    for source, text in surfaces.items():
        hits.extend(forbidden_claim_hits(text, source=source))
        lowered = text.lower()
        if gate_status != "PASSED" and '"closed_loop_superiority_claim_allowed": true' in lowered:
            hits.append({"source": source, "path": source, "phrase": "closed_loop_superiority_claim_allowed true with non-PASSED Gate C"})
        if gate_status != "PASSED" and '"claim_allowed": true' in lowered:
            hits.append({"source": source, "path": source, "phrase": "claim_allowed true with non-PASSED Gate C"})
    return {
        "experiment": "v1_4_claim_audit",
        "requirements_covered": ["CLAIM-02", "CLAIM-03"],
        "status": "PASSED" if not hits else "FAILED",
        "strict_gate_c_status": gate_status,
        "hit_count": len(hits),
        "hits": hits,
        "scanned_surfaces": sorted(surfaces),
    }


def build_milestone_audit(records: list[dict[str, Any]], claim_inputs: dict[str, Any], claim_audit: dict[str, Any]) -> dict[str, Any]:
    protocol = payload_for(records, "v1_4_locked_gate_c_protocol")
    execution = payload_for(records, "v1_4_locked_gate_c_execution")
    gate = payload_for(records, "v1_4_gate_c_paired_evidence")
    required_comparators = {"max_pressure", "capacity_aware_pressure", "finite_storage_double_pressure"}
    drift = []
    if protocol.get("spec_fingerprint") != execution.get("locked_protocol_fingerprint"):
        drift.append("execution fingerprint does not match locked protocol")
    if protocol.get("spec_fingerprint") != gate.get("locked_protocol_fingerprint"):
        drift.append("gate fingerprint does not match locked protocol")
    if protocol.get("selected_controller_id") != execution.get("selected_controller_id"):
        drift.append("execution selected controller does not match protocol")
    if protocol.get("selected_controller_id") != gate.get("selected_controller_id"):
        drift.append("gate selected controller does not match protocol")
    if not required_comparators <= set(protocol.get("required_comparators", [])):
        drift.append("protocol is missing required comparators")
    overclaim = []
    if strict_gate_c_status(records) != "PASSED" and claim_inputs.get("closed_loop_superiority_claim_allowed") is True:
        overclaim.append("claim inputs allow closed-loop superiority with non-PASSED Gate C")
    parse_failures = [record["source_key"] for record in records if record["parse_status"] != "PASSED"]
    status = "PASSED" if not drift and not overclaim and not parse_failures and claim_audit["status"] == "PASSED" else "FAILED"
    return {
        "experiment": "v1_4_milestone_audit",
        "requirements_covered": REQUIREMENTS_COVERED,
        "status": status,
        "strict_gate_c_status": strict_gate_c_status(records),
        "requirements_status": {"CLAIM-01": "Complete", "CLAIM-02": "Complete", "CLAIM-03": "Complete"},
        "protocol_drift_findings": drift,
        "overclaim_findings": overclaim,
        "parse_failures": parse_failures,
        "claim_audit_status": claim_audit["status"],
        "recommendation": "Closed-loop superiority remains disallowed until the locked main rows are executed and strict v1.4 Gate C is PASSED.",
    }


def render_milestone_audit_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# v1.4 Milestone Audit",
        "",
        f"Status: `{audit['status']}`",
        f"Strict Gate C status: `{audit['strict_gate_c_status']}`",
        "",
        "## Requirements",
    ]
    for key, value in audit["requirements_status"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Findings"])
    for label in ["protocol_drift_findings", "overclaim_findings", "parse_failures"]:
        values = audit[label]
        lines.append(f"- {label}: {', '.join(values) if values else 'none'}")
    lines.extend(["", "## Recommendation", audit["recommendation"]])
    return "\n".join(lines).rstrip() + "\n"


def build_v14_package(out_dir: Path, registry: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    records = load_source_records(registry)
    claim_inputs = build_claim_inputs(records)
    table_rows = build_table_rows(claim_inputs)
    reproduction = build_reproduction_manifest(out_dir)
    provenance = build_provenance_manifest(out_dir, records)
    gate_status = strict_gate_c_status(records)
    package = {
        "experiment": "v1_4_reproducibility_package",
        "status": "UNKNOWN",
        "requirements_covered": REQUIREMENTS_COVERED,
        "generated_by": "scripts/run_v14_claim_refresh.py",
        "generated_at": utc_now(),
        "source_status_summary": {record["source_key"]: record["source_status"] for record in records},
        "strict_gate_c_status": gate_status,
        "closed_loop_superiority_claim_allowed": claim_inputs["closed_loop_superiority_claim_allowed"],
        "derived_outputs": [str(out_dir / name) for name in OUTPUT_FILENAMES.values()],
        "claim_audit_status": "UNKNOWN",
        "milestone_audit_status": "UNKNOWN",
        "strict_mode_reasons": [],
    }
    summary = render_summary(package, claim_inputs)
    surfaces = {
        "v1_4_reproducibility_package.json": json.dumps(package, sort_keys=True),
        "v1_4_claim_inputs.json": json.dumps(claim_inputs, sort_keys=True),
        "v1_4_table_inputs.csv": render_csv_text(table_rows),
        "v1_4_provenance_manifest.json": json.dumps(provenance, sort_keys=True),
        "v1_4_reproduction_manifest.json": json.dumps(reproduction, sort_keys=True),
        "v1_4_summary.md": summary,
    }
    claim_audit = audit_generated_outputs(surfaces, gate_status)
    milestone_audit = build_milestone_audit(records, claim_inputs, claim_audit)
    package["claim_audit_status"] = claim_audit["status"]
    package["milestone_audit_status"] = milestone_audit["status"]
    parse_failures = [record["source_key"] for record in records if record["parse_status"] != "PASSED"]
    if claim_audit["status"] == "FAILED" or milestone_audit["status"] == "FAILED":
        package["status"] = "FAILED"
    elif parse_failures:
        package["status"] = "FAILED"
    elif gate_status == "PASSED":
        package["status"] = "PASSED"
    else:
        package["status"] = "INCONCLUSIVE"
    if package["status"] != "PASSED":
        package["strict_mode_reasons"] = [f"strict v1.4 Gate C status is {gate_status}, expected PASSED"]
    summary = render_summary(package, claim_inputs)
    return {
        "package": package,
        "source_records": records,
        "claim_inputs": claim_inputs,
        "table_rows": table_rows,
        "provenance_manifest": provenance,
        "reproduction_manifest": reproduction,
        "claim_audit": claim_audit,
        "milestone_audit": milestone_audit,
        "summary_markdown": summary,
        "milestone_audit_markdown": render_milestone_audit_markdown(milestone_audit),
    }


def write_v14_artifacts(out_dir: Path, payloads: dict[str, Any]) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {key: out_dir / name for key, name in OUTPUT_FILENAMES.items()}
    paths["package"].write_text(json.dumps(payloads["package"], indent=2), encoding="utf-8")
    paths["provenance"].write_text(json.dumps(payloads["provenance_manifest"], indent=2), encoding="utf-8")
    paths["claim_inputs"].write_text(json.dumps(payloads["claim_inputs"], indent=2), encoding="utf-8")
    paths["claim_audit"].write_text(json.dumps(payloads["claim_audit"], indent=2), encoding="utf-8")
    paths["reproduction"].write_text(json.dumps(payloads["reproduction_manifest"], indent=2), encoding="utf-8")
    paths["summary"].write_text(payloads["summary_markdown"], encoding="utf-8")
    paths["milestone_audit"].write_text(json.dumps(payloads["milestone_audit"], indent=2), encoding="utf-8")
    paths["milestone_audit_md"].write_text(payloads["milestone_audit_markdown"], encoding="utf-8")
    with paths["table"].open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TABLE_FIELDNAMES)
        writer.writeheader()
        writer.writerows(payloads["table_rows"])
    return paths


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    out_dir = resolve_path(args.out_dir)
    payloads = build_v14_package(out_dir)
    paths = write_v14_artifacts(out_dir, payloads)
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "status": payloads["package"]["status"],
                "strict_gate_c_status": payloads["package"]["strict_gate_c_status"],
                "closed_loop_superiority_claim_allowed": payloads["package"]["closed_loop_superiority_claim_allowed"],
                "claim_audit_status": payloads["claim_audit"]["status"],
                "milestone_audit_status": payloads["milestone_audit"]["status"],
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
