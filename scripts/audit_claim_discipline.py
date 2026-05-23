#!/usr/bin/env python3
"""Fail-closed Phase 6 claim-discipline audit CLI."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from claim_policy import (
    CLAIM_AUDIT_ARTIFACT,
    DEFAULT_CLAIM_SCAN_PATHS,
    POLICY_ARTIFACT,
    REQUIREMENTS_COVERED,
    bounded_claim_policy,
    forbidden_claim_hits,
    historical_evidence_is_insufficient_for_superiority,
    write_policy_artifact,
)

SKIP_FORBIDDEN_KEYS = {
    "forbidden_patterns",
    "forbidden_phrases",
    "forbidden_phrases_present",
    "forbidden_hits",
    "allowed_claims",
    "claim_policy",
    "description",
    "does_not_support",
    "historical_evidence_quarantine",
    "permitted_claim",
    "reason",
}
TEXT_SUFFIXES = {".md", ".txt", ".csv"}
JSON_SUFFIXES = {".json"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root for relative claim scan paths")
    parser.add_argument("--paths", nargs="*", default=None, help="Files or directories to scan; defaults to policy paths")
    parser.add_argument("--policy-out", default=POLICY_ARTIFACT)
    parser.add_argument("--audit-out", default=CLAIM_AUDIT_ARTIFACT)
    parser.add_argument("--allow-missing-paths", action="store_true", default=True)
    parser.add_argument("--no-allow-missing-paths", dest="allow_missing_paths", action="store_false")
    return parser.parse_args()


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def iter_scan_files(root: Path, rel_path: str, *, allow_missing_paths: bool) -> tuple[list[Path], list[str]]:
    path = (root / rel_path).resolve() if not Path(rel_path).is_absolute() else Path(rel_path).resolve()
    missing: list[str] = []
    if not path.exists():
        if allow_missing_paths:
            return [], missing
        missing.append(rel_path)
        return [], missing
    if path.is_file():
        if path.suffix.lower() in TEXT_SUFFIXES | JSON_SUFFIXES:
            return [path], missing
        return [], missing
    files = [
        candidate
        for candidate in sorted(path.rglob("*"))
        if candidate.is_file() and candidate.suffix.lower() in TEXT_SUFFIXES | JSON_SUFFIXES
    ]
    return files, missing


def prose_from_json(value: Any, parent_key: str = "") -> list[str]:
    if parent_key in SKIP_FORBIDDEN_KEYS:
        return []
    if isinstance(value, dict):
        chunks: list[str] = []
        for key, item in value.items():
            chunks.extend(prose_from_json(item, str(key)))
        return chunks
    if isinstance(value, list):
        chunks = []
        for item in value:
            chunks.extend(prose_from_json(item, parent_key))
        return chunks
    if isinstance(value, str):
        return [value]
    return []


def read_claim_text(path: Path) -> tuple[str, dict[str, Any] | None, str | None]:
    try:
        if path.suffix.lower() in JSON_SUFFIXES:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return "\n".join(prose_from_json(payload)), payload if isinstance(payload, dict) else None, None
        return path.read_text(encoding="utf-8"), None, None
    except Exception as exc:  # noqa: BLE001
        return "", None, str(exc)


def validate_policy_artifact(policy: dict[str, Any]) -> list[str]:
    errors = []
    if policy.get("status") != "PASSED":
        errors.append("claim policy status must be PASSED")
    if policy.get("requirements_covered") != REQUIREMENTS_COVERED:
        errors.append("claim policy requirements_covered must be CLAIM-01 and CLAIM-02")
    allowed = policy.get("allowed_claims")
    if not isinstance(allowed, dict) or not {"slack_recovery_or_tie", "binding_regime_improvement_only"} <= set(allowed):
        errors.append("claim policy allowed_claims missing bounded categories")
    evidence = policy.get("evidence_categories")
    required_evidence = {
        "pressure_equivalent_recovery",
        "binding_regime_separation",
        "closed_loop_binding_stress",
        "insufficient_historical_v1_0",
    }
    if not isinstance(evidence, dict) or not required_evidence <= set(evidence):
        errors.append("claim policy evidence_categories missing required categories")
    return errors


def audit_claim_paths(root: Path, paths: list[str], *, policy_path: Path | None = None, allow_missing_paths: bool = True) -> dict[str, Any]:
    root = root.resolve()
    policy_target = policy_path or (root / POLICY_ARTIFACT)
    generated_by = "scripts/audit_claim_discipline.py"
    policy = write_policy_artifact(policy_target if policy_target.is_absolute() else root / policy_target, generated_by=generated_by)
    checked_paths: list[str] = []
    forbidden_hits: list[dict[str, str]] = []
    missing_paths: list[str] = []
    parse_errors: list[dict[str, str]] = []
    historical_quarantine_hits: list[dict[str, str]] = []
    historical_superiority_violations: list[dict[str, str]] = []

    for rel_path in paths:
        files, missing = iter_scan_files(root, rel_path, allow_missing_paths=allow_missing_paths)
        missing_paths.extend(missing)
        for path in files:
            rel = relative_to_root(path, root)
            checked_paths.append(rel)
            text, payload, error = read_claim_text(path)
            if error:
                parse_errors.append({"path": rel, "error": error})
                continue
            path_for_quarantine = False
            path_for_violation = False
            if historical_evidence_is_insufficient_for_superiority({"path": rel, "text": text}):
                path_for_violation = True
            if any(marker in text.lower() for marker in ["pressure-equivalent", "pressure equivalent", "v1.0", "block3_static_kill_gate", "block4_closed_loop_suite"]):
                path_for_quarantine = True
            hits = forbidden_claim_hits(text, source=rel)
            forbidden_hits.extend(hits)
            if path_for_violation:
                historical_superiority_violations.append({"path": rel, "category": "insufficient_historical_v1_0"})
                if "proves superiority" in text.lower() and not any(hit.get("path") == rel and hit.get("phrase") == "proves superiority" for hit in forbidden_hits):
                    forbidden_hits.append({"source": rel, "path": rel, "phrase": "proves superiority"})
            if path_for_quarantine or path_for_violation:
                historical_quarantine_hits.append({"path": rel, "category": "insufficient_historical_v1_0"})

    policy_errors = validate_policy_artifact(policy)
    status = "PASSED"
    if forbidden_hits or historical_superiority_violations or missing_paths or parse_errors or policy_errors:
        status = "FAILED"
    audit = {
        "experiment": "phase6_claim_audit",
        "status": status,
        "generated_by": generated_by,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requirements_covered": REQUIREMENTS_COVERED,
        "checked_paths": sorted(dict.fromkeys(checked_paths)),
        "missing_paths": missing_paths,
        "parse_errors": parse_errors,
        "forbidden_hits": forbidden_hits,
        "claim_policy": policy,
        "policy_validation_errors": policy_errors,
        "historical_evidence_quarantine": {
            "category": "insufficient_historical_v1_0",
            "rule": "v1.0 pressure-equivalent static or closed-loop evidence cannot support superiority claims",
            "hits": historical_quarantine_hits,
            "superiority_violations": historical_superiority_violations,
        },
        "scan_contract": {
            "forbidden_phrase_scope": "report prose, configured content files, CSV text, and JSON prose fields",
            "metadata_exclusions": sorted(SKIP_FORBIDDEN_KEYS),
            "artifact_validation": "claim policy and claim audit required fields are validated separately from forbidden text scanning",
            "deferred_to_plan_06_03": [
                "phase6_explicit_state_schema.json",
                "phase6_state_objective_fixtures.json",
            ],
        },
    }
    return audit


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    paths = args.paths if args.paths is not None else DEFAULT_CLAIM_SCAN_PATHS
    policy_out = Path(args.policy_out)
    audit_out = Path(args.audit_out)
    policy_path = policy_out if policy_out.is_absolute() else root / policy_out
    audit_path = audit_out if audit_out.is_absolute() else root / audit_out
    audit = audit_claim_paths(root, paths, policy_path=policy_path, allow_missing_paths=args.allow_missing_paths)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps({"status": audit["status"], "audit_out": str(audit_path)}, indent=2))
    if audit["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
