#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from claim_policy import FORBIDDEN_CLAIM_PATTERNS, forbidden_claim_hits

REPRO_FORBIDDEN_PHRASES = ["max-pressure strawman"]
FORBIDDEN_PHRASES = list(dict.fromkeys([*FORBIDDEN_CLAIM_PATTERNS, *REPRO_FORBIDDEN_PHRASES]))
TEXT_CLAIM_CHECKS = [
    "README.md",
    "experiments/dual_sensitivity/block3_static_kill_gate_report.md",
    "experiments/dual_sensitivity/block4_closed_loop_suite_report.md",
]
EXPECTED_JSON_WITHOUT_STATUS = set[str]()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def build_block_registry() -> list[dict[str, Any]]:
    return [
        {
            "block": "block0",
            "description": "Block 0 dual finite-difference sanity checks",
            "commands": [["python3", "scripts/run_dual_sanity.py", "--out", "experiments/dual_sensitivity/block0_dual_sanity.json"]],
            "expected_artifacts": ["experiments/dual_sensitivity/block0_dual_sanity.json"],
            "runtime_profile": "short",
            "requirements": ["REPR-03", "REPR-04"],
            "claim_note": "Dual sanity only; not closed-loop evidence.",
        },
        {
            "block": "sparse_recovery",
            "description": "Block 2 sparse symbolic recovery from targeted bottleneck states",
            "commands": [[
                "python3",
                "scripts/run_sparse_recovery.py",
                "--states",
                "experiments/dual_sensitivity/targeted_bottleneck_states.json",
                "--out",
                "experiments/dual_sensitivity/block2_sparse_recovery.json",
            ]],
            "expected_artifacts": [
                "experiments/dual_sensitivity/block2_sparse_recovery.json",
                "experiments/dual_sensitivity/block2_sparse_recovery.csv",
                "experiments/dual_sensitivity/block2_sparse_recovery_rules.txt",
            ],
            "runtime_profile": "short",
            "requirements": ["REPR-03", "REPR-04"],
            "claim_note": "Plain-text symbolic recovery audit output; Phase 3 owns claim routing.",
        },
        {
            "block": "static_kill_gate",
            "description": "Block 3 static pressure-failure route decision",
            "commands": [[
                "python3",
                "scripts/run_static_kill_gate.py",
                "--states",
                "experiments/dual_sensitivity/block3_regime_states.json",
                "--out",
                "experiments/dual_sensitivity/block3_static_kill_gate.json",
                "--csv-out",
                "experiments/dual_sensitivity/block3_static_kill_gate.csv",
                "--rules-out",
                "experiments/dual_sensitivity/block3_static_kill_gate_rules.txt",
                "--report-out",
                "experiments/dual_sensitivity/block3_static_kill_gate_report.md",
            ]],
            "expected_artifacts": [
                "experiments/dual_sensitivity/block3_static_kill_gate.json",
                "experiments/dual_sensitivity/block3_static_kill_gate.csv",
                "experiments/dual_sensitivity/block3_static_kill_gate_rules.txt",
                "experiments/dual_sensitivity/block3_static_kill_gate_report.md",
            ],
            "runtime_profile": "short",
            "requirements": ["REPR-03", "REPR-04"],
            "claim_note": "Route decision source of truth; current route is pressure-equivalent.",
        },
        {
            "block": "closed_loop_smoke",
            "description": "Short closed-loop SUMO smoke suite",
            "commands": [[
                "python3",
                "scripts/run_closed_loop_suite.py",
                "--profile",
                "smoke",
                "--out",
                "experiments/dual_sensitivity/block4_closed_loop_suite_smoke.json",
            ]],
            "expected_artifacts": ["experiments/dual_sensitivity/block4_closed_loop_suite_smoke.json"],
            "runtime_profile": "SUMO smoke",
            "requirements": ["REPR-03", "REPR-04"],
            "claim_note": "Smoke rerun path only; main closed-loop evidence is audited separately.",
        },
        {
            "block": "closed_loop_main",
            "description": "Main closed-loop SUMO suite and report artifacts",
            "commands": [
                [
                    "python3",
                    "scripts/run_closed_loop_suite.py",
                    "--profile",
                    "main",
                    "--steps",
                    "300",
                    "--warmup",
                    "60",
                    "--action-interval",
                    "10",
                    "--out",
                    "experiments/dual_sensitivity/block4_closed_loop_suite.json",
                ],
                [
                    "python3",
                    "scripts/render_closed_loop_report.py",
                    "--input",
                    "experiments/dual_sensitivity/block4_closed_loop_suite.json",
                    "--out",
                    "experiments/dual_sensitivity/block4_closed_loop_suite_report.md",
                    "--csv-out",
                    "experiments/dual_sensitivity/block4_closed_loop_suite.csv",
                ],
            ],
            "expected_artifacts": [
                "experiments/dual_sensitivity/block4_closed_loop_suite.json",
                "experiments/dual_sensitivity/block4_closed_loop_suite.csv",
                "experiments/dual_sensitivity/block4_closed_loop_suite_report.md",
            ],
            "runtime_profile": "SUMO main",
            "requirements": ["REPR-03", "REPR-04"],
            "claim_note": "Closed-loop SUMO evidence is simulator-, network-, horizon-, and seed-relative.",
        },
        {
            "block": "paper_artifacts",
            "description": "Paper-facing table and figure-data generation",
            "commands": [["python3", "scripts/render_paper_artifacts.py", "--out-dir", "experiments/dual_sensitivity"]],
            "expected_artifacts": [
                "experiments/dual_sensitivity/paper_tables.csv",
                "experiments/dual_sensitivity/paper_figure_data.csv",
                "experiments/dual_sensitivity/paper_artifacts_manifest.json",
            ],
            "runtime_profile": "short",
            "requirements": ["REPR-04", "REPR-05"],
            "claim_note": "Generated paper-facing tables and figure data must trace to raw artifacts.",
        },
        {
            "block": "phase6_claim_state_guards",
            "description": "Phase 6 claim policy, claim audit, explicit state schema, and state/objective fixture guards",
            "commands": [
                [
                    "python3",
                    "scripts/audit_claim_discipline.py",
                    "--policy-out",
                    "experiments/dual_sensitivity/phase6_claim_policy.json",
                    "--audit-out",
                    "experiments/dual_sensitivity/phase6_claim_audit.json",
                ],
                [
                    "python3",
                    "scripts/generate_static_regime_states.py",
                    "--target-per-regime",
                    "3",
                    "--out",
                    "experiments/dual_sensitivity/phase6_state_objective_fixtures.json",
                    "--schema-out",
                    "experiments/dual_sensitivity/phase6_explicit_state_schema.json",
                ],
            ],
            "expected_artifacts": [
                "experiments/dual_sensitivity/phase6_claim_policy.json",
                "experiments/dual_sensitivity/phase6_claim_audit.json",
                "experiments/dual_sensitivity/phase6_explicit_state_schema.json",
                "experiments/dual_sensitivity/phase6_state_objective_fixtures.json",
            ],
            "runtime_profile": "short",
            "requirements": ["CLAIM-01", "CLAIM-02", "STATE-01", "STATE-02", "STATE-03"],
            "claim_note": "Phase 6 guard artifacts bound v1.0 evidence to pressure-equivalent claims and require explicit finite-storage/objective schemas.",
        },
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List known reproduction blocks")
    parser.add_argument("--audit", action="store_true", help="Audit expected artifacts and write a manifest")
    parser.add_argument("--run", action="store_true", help="Run one selected block")
    parser.add_argument("--block", default=None, help="Block name to run, or all")
    parser.add_argument("--manifest-out", default="experiments/dual_sensitivity/reproducibility_manifest.json")
    return parser.parse_args()


def command_text(command: list[str]) -> str:
    return " ".join(command)


def commands_text(commands: list[list[str]]) -> list[str]:
    return [command_text(command) for command in commands]


def list_blocks(registry: list[dict[str, Any]]) -> None:
    for item in registry:
        print(f"{item['block']}: {item['description']}")
        print(f"  runtime: {item['runtime_profile']}")
        for command in item["commands"]:
            print(f"  command: {command_text(command)}")
        print(f"  artifacts: {', '.join(item['expected_artifacts'])}")


def run_blocks(registry: list[dict[str, Any]], block: str | None, root: Path) -> None:
    if not block:
        raise ValueError("--run requires --block")
    selected = registry if block == "all" else [item for item in registry if item["block"] == block]
    if not selected:
        raise ValueError(f"Unknown block {block!r}; available: {[item['block'] for item in registry]}")
    for item in selected:
        for command in item["commands"]:
            subprocess.run(command, cwd=root, check=True)


def json_count(payload: Any) -> dict[str, int]:
    if isinstance(payload, list):
        return {"item_count": len(payload)}
    if not isinstance(payload, dict):
        return {}
    counts = {}
    for key in ["results", "runs", "summary", "best_by_library", "scenario_results", "aggregates", "artifact_checks"]:
        value = payload.get(key)
        if isinstance(value, list):
            counts[f"{key}_count"] = len(value)
    return counts


def audit_file(path: Path, rel_path: str, expected_paths: set[str]) -> dict[str, Any]:
    check: dict[str, Any] = {
        "path": rel_path,
        "exists": path.exists(),
        "expected": rel_path in expected_paths,
        "status_required": rel_path in expected_paths and path.suffix == ".json" and rel_path not in EXPECTED_JSON_WITHOUT_STATUS,
    }
    if not path.exists():
        check["parse_status"] = "missing"
        return check
    try:
        if path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            check.update({"parse_status": "ok", **json_count(payload)})
            if isinstance(payload, dict):
                for key in ["experiment", "status", "route_decision"]:
                    if key in payload:
                        check[key] = payload[key]
        elif path.suffix == ".csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            check.update({"parse_status": "ok", "row_count": len(rows)})
        else:
            text = path.read_text(encoding="utf-8")
            check.update({"parse_status": "ok", "byte_length": len(text.encode("utf-8"))})
    except Exception as exc:  # noqa: BLE001
        check.update({"parse_status": "error", "error": str(exc)})
    return check


def artifact_passed(check: dict[str, Any]) -> bool:
    if not check.get("exists") or check.get("parse_status") != "ok":
        return False
    if check.get("status_required") and check.get("status") != "PASSED":
        return False
    return True


def forbidden_phrase_hits(root: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for rel_path in TEXT_CLAIM_CHECKS:
        path = root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        hits.extend(forbidden_claim_hits(text, source=rel_path))
        lowered = text.lower()
        hits.extend(
            {"source": rel_path, "path": rel_path, "phrase": phrase}
            for phrase in REPRO_FORBIDDEN_PHRASES
            if phrase in lowered
        )
    return hits


def audit_artifacts(registry: list[dict[str, Any]], root: Path) -> dict[str, Any]:
    expected_paths = {path for item in registry for path in item["expected_artifacts"]}
    artifact_paths = sorted(expected_paths | set(TEXT_CLAIM_CHECKS))
    checks = [audit_file(root / rel_path, rel_path, expected_paths) for rel_path in artifact_paths]
    expected_ok = all(artifact_passed(check) for check in checks if check.get("expected"))
    hits = forbidden_phrase_hits(root)
    status = "PASSED" if expected_ok and not hits else "FAILED"
    return {
        "experiment": "reproducibility_manifest",
        "status": status,
        "generated_by": "scripts/reproduce_blocks.py --audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "blocks": [
            {
                "block": item["block"],
                "description": item["description"],
                "commands": commands_text(item["commands"]),
                "command": " && ".join(commands_text(item["commands"])),
                "expected_artifacts": item["expected_artifacts"],
                "runtime_profile": item["runtime_profile"],
                "requirements": item["requirements"],
                "claim_note": item["claim_note"],
            }
            for item in registry
        ],
        "artifact_checks": checks,
        "claim_discipline": {
            "route_decision": "pressure-equivalent",
            "framing": "pressure-equivalent generalized-pressure symbolic recovery",
            "forbidden_phrases": FORBIDDEN_PHRASES,
            "forbidden_phrases_present": hits,
        },
        "requirements_covered": ["REPR-03", "REPR-04"],
    }


def write_manifest(manifest: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = repo_root()
    registry = build_block_registry()
    if args.list or not (args.audit or args.run):
        list_blocks(registry)
    if args.run:
        run_blocks(registry, args.block, root)
    if args.audit:
        manifest = audit_artifacts(registry, root)
        write_manifest(manifest, root / args.manifest_out)
        print(json.dumps({"manifest_out": args.manifest_out, "status": manifest["status"]}, indent=2))
        if manifest["status"] != "PASSED":
            raise SystemExit(1)


if __name__ == "__main__":
    main()
