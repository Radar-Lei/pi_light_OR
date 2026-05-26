#!/usr/bin/env python3
"""Execute or resume the locked v1.4 Gate C protocol."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_phase11_paired_evidence as phase11

DEFAULT_PROTOCOL = "experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json"
DEFAULT_OUT = "experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json"
DEFAULT_PROGRESS = "experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json"
REQUIREMENTS_COVERED = ["LOCK-02", "LOCK-03"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", default=DEFAULT_PROTOCOL)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--progress-out", default=None)
    parser.add_argument("--resume-progress", default=None)
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--scaled-input-dir", default=str(phase11.DEFAULT_SCALED_INPUT_DIR))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--execution-row-limit",
        type=int,
        default=None,
        help="Safety limit for executed rows; omit to use the fail-closed main guard.",
    )
    return parser.parse_args()


def load_protocol(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Protocol {path} must contain a JSON object")
    return payload


def validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("experiment") != "v1_4_locked_gate_c_protocol":
        raise ValueError("protocol is not v1_4_locked_gate_c_protocol")
    if protocol.get("status") != "LOCKED":
        raise ValueError("v1.4 Gate C protocol is not LOCKED")
    if protocol.get("pre_confirmation_lock") is not True:
        raise ValueError("v1.4 Gate C protocol is missing pre_confirmation_lock=true")
    selected = protocol.get("selected_controller_id")
    if not selected:
        raise ValueError("v1.4 Gate C protocol has no selected_controller_id")
    if selected not in phase11.CONTROLLER_REGISTRY:
        raise ValueError(f"selected controller is not executable: {selected}")
    required = set(phase11.REQUIRED_GATE_C_COMPARATORS)
    actual = set(protocol.get("required_comparators", []))
    missing = sorted(required - actual)
    if missing:
        raise ValueError(f"v1.4 Gate C protocol is missing required comparators: {missing}")
    for field in ["binding_scenarios", "primary_metrics", "demand_multipliers", "seeds", "spec_fingerprint"]:
        if not protocol.get(field):
            raise ValueError(f"v1.4 Gate C protocol is missing {field}")


def build_locked_spec(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    selected = str(protocol["selected_controller_id"])
    phase11.set_proposed_controller(selected)
    controllers = [selected, *[str(item) for item in protocol["required_comparators"]]]
    spec = phase11.build_phase11_spec(
        profile=str(protocol.get("profile", "main")),
        controllers=controllers,
        seeds=[int(seed) for seed in protocol["seeds"]],
        steps=int(protocol.get("steps", 3600)),
        warmup=int(protocol.get("warmup", 900)),
        demand_multipliers=[float(item) for item in protocol["demand_multipliers"]],
    )
    allowed_scenarios = set(str(item) for item in protocol["binding_scenarios"])
    filtered = [row for row in spec if str(row.get("scenario_tag")) in allowed_scenarios]
    if len(filtered) != len(spec):
        raise ValueError("protocol scenarios do not match the generated locked spec")
    return filtered


def _bounded(items: list[Any], limit: int = 50) -> list[Any]:
    return items[:limit]


def build_row_audit(rows: list[dict[str, Any]], spec: list[dict[str, Any]]) -> dict[str, Any]:
    completed = phase11._completed_rows(rows)
    expected_keys = [phase11.row_key(row) for row in spec]
    completed_keys = [phase11.row_key(row) for row in completed]
    row_counts: dict[str, int] = {}
    row_examples: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = phase11.row_key(row)
        row_counts[key] = row_counts.get(key, 0) + 1
        row_examples.setdefault(key, []).append(row)
    duplicate = [
        {"row_key": key, "count": count, "conflicting": len({json.dumps(row, sort_keys=True) for row in row_examples[key]}) > 1}
        for key, count in sorted(row_counts.items())
        if count > 1
    ]
    failed = [
        {
            "row_key": phase11.row_key(row),
            "scenario_status": row.get("scenario_status"),
            "feasibility_status": row.get("feasibility_status"),
            "reason": row.get("unsupported_reason") or row.get("error") or row.get("placeholder_reason"),
        }
        for row in rows
        if row.get("scenario_status") != "completed" or row.get("feasibility_status") not in {"run", "completed"}
    ]
    bad_provenance = []
    schema_invalid = []
    for row in completed:
        provenance_reasons = phase11._validate_demand_provenance(row)
        if provenance_reasons:
            bad_provenance.append({"row_key": phase11.row_key(row), "reasons": provenance_reasons})
        schema_reasons = phase11._validate_binding_row(row)
        if schema_reasons:
            schema_invalid.append({"row_key": phase11.row_key(row), "reasons": schema_reasons})
    alignment = phase11.paired_seed_alignment(completed, spec)
    unpaired = []
    for scenario, by_multiplier in alignment.items():
        for multiplier, entry in by_multiplier.items():
            if not entry.get("aligned"):
                unpaired.append({"scenario_tag": scenario, "demand_multiplier": multiplier, "seeds_by_controller": entry.get("seeds_by_controller", {})})
    missing = sorted(set(expected_keys) - set(completed_keys))
    return {
        "expected_row_count": len(spec),
        "raw_row_count": len(rows),
        "completed_row_count": len(completed),
        "missing_row_count": len(missing),
        "failed_row_count": len(failed),
        "duplicate_row_count": len(duplicate),
        "unpaired_group_count": len(unpaired),
        "bad_provenance_row_count": len(bad_provenance),
        "schema_invalid_row_count": len(schema_invalid),
        "completed_rows": _bounded([{"row_key": key} for key in sorted(set(completed_keys))]),
        "missing_rows": _bounded([{"row_key": key} for key in missing]),
        "failed_rows": _bounded(failed),
        "duplicate_rows": _bounded(duplicate),
        "unpaired_groups": _bounded(unpaired),
        "bad_provenance_rows": _bounded(bad_provenance),
        "schema_invalid_rows": _bounded(schema_invalid),
    }


def write_locked_execution(
    *,
    protocol_path: Path,
    out_path: Path,
    route_json: Path,
    scaled_input_dir: Path,
    dry_run: bool = False,
    execution_row_limit: int | None = None,
    progress_out: Path | None = None,
    resume_progress: Path | None = None,
) -> dict[str, Any]:
    protocol = load_protocol(protocol_path)
    validate_protocol(protocol)
    spec = build_locked_spec(protocol)
    spec = phase11.materialize_demand_inputs(spec, scaled_input_dir)
    route_metadata = phase11.load_route_metadata(route_json)
    if execution_row_limit is None:
        execution_row_limit = phase11.DEFAULT_MAIN_EXECUTION_ROW_LIMIT
    rows, missing_reasons, execution_mode = phase11.execute_spec(
        spec,
        route_metadata,
        dry_run=dry_run,
        execution_row_limit=execution_row_limit,
        progress_out=progress_out,
        resume_progress=resume_progress,
    )
    payload = phase11.build_payload(
        profile=str(protocol.get("profile", "main")),
        route_metadata=route_metadata,
        spec=spec,
        rows=rows,
        dry_run=dry_run,
        execution_mode=execution_mode,
        missing_row_reasons=missing_reasons,
    )
    payload.update(
        {
            "experiment": "v1_4_locked_gate_c_execution",
            "requirements_covered": REQUIREMENTS_COVERED,
            "claim_ready": False,
            "locked_protocol_path": str(protocol_path),
            "locked_protocol_status": protocol.get("status"),
            "locked_protocol_fingerprint": protocol.get("spec_fingerprint"),
            "selected_candidate_id": protocol.get("selected_candidate_id"),
            "selected_controller_id": protocol.get("selected_controller_id"),
            "required_comparators": list(protocol.get("required_comparators", [])),
            "primary_metrics": list(protocol.get("primary_metrics", [])),
            "row_audit": build_row_audit(rows, spec),
            "v1_4_caveat": "This artifact is locked confirmation evidence only when status is PASSED and all rows are executed.",
        }
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_locked_execution(
        protocol_path=Path(args.protocol),
        out_path=Path(args.out),
        route_json=Path(args.route_json),
        scaled_input_dir=Path(args.scaled_input_dir),
        dry_run=args.dry_run,
        execution_row_limit=args.execution_row_limit,
        progress_out=Path(args.progress_out) if args.progress_out else None,
        resume_progress=Path(args.resume_progress) if args.resume_progress else None,
    )
    print(
        json.dumps(
            {
                "out": args.out,
                "status": payload["status"],
                "selected_controller_id": payload["selected_controller_id"],
                "expected_rows": payload["row_audit"]["expected_row_count"],
                "completed_rows": payload["row_audit"]["completed_row_count"],
                "execution_mode": payload["execution_mode"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
