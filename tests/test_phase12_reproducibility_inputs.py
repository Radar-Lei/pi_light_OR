#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_phase12_reproducibility_inputs import (  # noqa: E402
    OUTPUT_FILENAMES,
    REQUIRED_GATE_C_COMPARATORS,
    REQUIRED_GATE_C_SCENARIOS,
    SOURCE_REGISTRY,
    audit_generated_outputs,
    build_claim_inputs,
    build_phase12_package,
    build_reproduction_manifest,
    load_source_record,
    load_source_records,
    registry_with_overrides,
    write_phase12_artifacts,
)


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def source_payload(status: str, *, experiment: str = "synthetic", profile: str = "main") -> dict:
    return {
        "experiment": experiment,
        "status": status,
        "generated_at": "2026-05-24T00:00:00+00:00",
        "requirements_covered": ["CLAIM-03"],
        "profile": profile,
        "steps": 3600,
        "warmup": 900,
        "seed_count": 2,
        "scenario_results": [
            {
                "network": "arterial",
                "scenario_tag": "arterial_spillback_stress",
                "seed": 7,
                "steps": 3600,
                "warmup": 900,
                "demand_multiplier": 1.2,
            },
            {
                "network": "arterial",
                "scenario_tag": "arterial_spillback_stress",
                "seed": 8,
                "steps": 3600,
                "warmup": 900,
                "demand_multiplier": 1.2,
            },
        ],
        "caveats": ["synthetic bounded caveat"],
    }


def phase7_payload(status: str) -> dict:
    return {
        **source_payload(status, experiment="phase7_theory_separation"),
        "generated_by": "scripts/check_theory_separation.py",
        "requirements_covered": ["THRY-01", "THRY-02", "THRY-03", "THRY-04"],
        "one_step_objective_definition": {},
        "criteria": {},
        "claim_scope": {},
        "guarantee_candidates": [],
        "examples": {
            "slack_recovery": {"status": "PASSED"},
            "storage_binding_two_phase_separation": {"status": "PASSED"},
        },
    }


def phase11_rows(count: int) -> list[dict]:
    return [
        {
            "network": "arterial",
            "scenario_tag": "arterial_spillback_stress",
            "seed": idx,
            "steps": 3600,
            "warmup": 900,
            "demand_multiplier": 1.2,
        }
        for idx in range(count)
    ]


def synthetic_sources(tmp: Path, *, gate_c_status: str = "INCONCLUSIVE", phase11_status: str = "INCONCLUSIVE") -> dict[str, Path]:
    phase11_count = 2160 if phase11_status == "PASSED" else 0
    paths = {
        "phase7_theory_separation": write_json(tmp / "phase7.json", phase7_payload("PASSED")),
        "phase9_slack_binding_gates": write_json(
            tmp / "phase9.json",
            {
                **source_payload("PASSED", experiment="phase9_slack_binding_gates"),
                "requirements_covered": ["GATE-01", "GATE-02", "GATE-04"],
                "inputs": {},
                "gate_a_slack_recovery": {"status": "PASSED"},
                "gate_b_binding_separation": {"status": "PASSED"},
                "fail_closed_checks": [],
            },
        ),
        "phase10_baselines_stress_suite": write_json(
            tmp / "phase10.json",
            {
                **source_payload("SMOKE_ONLY", experiment="phase10_baselines_stress_suite", profile="smoke"),
                "route_decision": "finite-storage-context",
                "claim_framing": "smoke/spec capability context only",
                "aggregates": {},
                "baseline_coverage": {},
                "strong_baseline_coverage": {},
                "stress_scenario_coverage": {},
            },
        ),
        "phase11_long_horizon_paired_seed_evidence": write_json(
            tmp / "phase11.json",
            {
                **source_payload(phase11_status, experiment="phase11_long_horizon_paired_seed_evidence"),
                "route_decision": "finite-storage-context",
                "execution_mode": "synthetic_complete" if phase11_status == "PASSED" else "fail_closed_runtime_guard",
                "scenario_results": phase11_rows(phase11_count),
                "actual_row_count": phase11_count,
                "expected_row_count": 2160,
                "all_rows_executed": phase11_status == "PASSED",
                "demand_multipliers": [0.8, 1.0, 1.2],
                "gate_c_evaluation": {},
            },
        ),
        "phase11_gate_c_paired_evidence": write_json(
            tmp / "gate_c.json",
            {
                **source_payload(gate_c_status, experiment="phase11_gate_c_paired_evidence"),
                "requirements_covered": ["GATE-03", "EXP-05"],
                "input_artifact": str(tmp / "phase11.json"),
                "input_status": phase11_status,
                "profile_eligibility": {
                    "profile": "main",
                    "steps": 3600,
                    "warmup": 900,
                    "eligible": phase11_status == "PASSED" and gate_c_status == "PASSED",
                    "actual_row_count": phase11_count,
                    "expected_row_count": 2160,
                    "all_rows_executed": phase11_status == "PASSED",
                },
                "binding_regime_dominance": [],
                "slack_regime_recovery_or_context": [],
                "inconclusive": [],
                "not_evidence": [],
                "required_binding_scenarios": sorted(REQUIRED_GATE_C_SCENARIOS),
                "required_gate_c_comparators": sorted(REQUIRED_GATE_C_COMPARATORS),
                "gate_c_primary_metrics_v1": {
                    "status": gate_c_status,
                    "metric_results": [{"metric": "penalized_avg_travel_time", "status": gate_c_status}]
                    if gate_c_status == "PASSED"
                    else [],
                },
            },
        ),
    }
    return paths


def test_source_registry_has_exact_required_sources_and_commands() -> None:
    assert set(SOURCE_REGISTRY) == {
        "phase7_theory_separation",
        "phase9_slack_binding_gates",
        "phase10_baselines_stress_suite",
        "phase11_long_horizon_paired_seed_evidence",
        "phase11_gate_c_paired_evidence",
    }
    for entry in SOURCE_REGISTRY.values():
        assert entry["path"].endswith(".json")
        assert entry["evidence_role"]
        assert entry["requirements"]
        assert entry["accepted_statuses"]
        assert entry["rerun_command"].startswith("python scripts/")
        assert entry["caveat_policy"]


def test_wrong_experiment_identity_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        path = write_json(tmp / "fake.json", {"experiment": "wrong", "status": "PASSED"})
        entry = dict(SOURCE_REGISTRY["phase7_theory_separation"])
        entry["path"] = str(path)
        record = load_source_record("phase7_theory_separation", entry)
        assert record["parse_status"] == "FAILED"
        assert record["claim_ready"] is False
        assert any("experiment mismatch" in caveat for caveat in record["caveats"])


def test_correct_experiment_but_minimal_passed_json_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        for key in SOURCE_REGISTRY:
            path = write_json(tmp / f"{key}.json", {"experiment": key, "status": "PASSED"})
            entry = dict(SOURCE_REGISTRY[key])
            entry["path"] = str(path)
            record = load_source_record(key, entry)
            assert record["parse_status"] == "FAILED", key
            assert record["claim_ready"] is False, key
            assert any("missing required key" in caveat for caveat in record["caveats"]), key


def test_missing_and_invalid_sources_fail_closed_without_silent_skip() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        missing_entry = dict(SOURCE_REGISTRY["phase7_theory_separation"])
        missing_entry["path"] = str(tmp / "missing.json")
        missing = load_source_record("phase7_theory_separation", missing_entry)
        assert missing["exists"] is False
        assert missing["parse_status"] == "MISSING"
        assert missing["source_status"] == "MISSING"
        assert missing["input_status"] == "INCONCLUSIVE"
        assert "missing" in missing["caveats"][0].lower()

        invalid_path = tmp / "invalid.json"
        invalid_path.write_text("{not json", encoding="utf-8")
        invalid_entry = dict(SOURCE_REGISTRY["phase9_slack_binding_gates"])
        invalid_entry["path"] = str(invalid_path)
        invalid = load_source_record("phase9_slack_binding_gates", invalid_entry)
        assert invalid["exists"] is True
        assert invalid["parse_status"] == "FAILED"
        assert invalid["source_status"] == "FAILED"
        assert invalid["input_status"] == "FAILED"
        assert invalid["parse_error"]


def test_status_propagation_for_passed_failed_inconclusive_pilot_and_smoke() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        statuses = ["PASSED", "FAILED", "INCONCLUSIVE", "PILOT_ONLY", "SMOKE_ONLY"]
        records = []
        for status in statuses:
            path = write_json(tmp / f"{status}.json", phase7_payload(status))
            entry = dict(SOURCE_REGISTRY["phase7_theory_separation"])
            entry["path"] = str(path)
            records.append(load_source_record("phase7_theory_separation", entry))
        by_status = {record["source_status"]: record for record in records}
        assert by_status["PASSED"]["claim_ready"] is True
        for status in ["FAILED", "INCONCLUSIVE", "PILOT_ONLY", "SMOKE_ONLY"]:
            assert by_status[status]["parse_status"] == "PASSED"
            assert by_status[status]["claim_ready"] is False
            assert any("not accepted" in caveat for caveat in by_status[status]["caveats"])


def test_phase11_passed_status_requires_complete_execution_metadata() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        path = write_json(
            tmp / "phase11_bad.json",
            {
                **source_payload("PASSED", experiment="phase11_long_horizon_paired_seed_evidence"),
                "actual_row_count": 1,
                "expected_row_count": 2160,
                "all_rows_executed": False,
            },
        )
        entry = dict(SOURCE_REGISTRY["phase11_long_horizon_paired_seed_evidence"])
        entry["path"] = str(path)
        record = load_source_record("phase11_long_horizon_paired_seed_evidence", entry)
        assert record["parse_status"] == "FAILED"
        assert record["claim_ready"] is False
        assert any("all_rows_executed" in caveat for caveat in record["caveats"])


def test_gate_c_passed_status_requires_internal_passed_inputs_and_metrics() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        path = write_json(
            tmp / "gate_bad.json",
            {
                **source_payload("PASSED", experiment="phase11_gate_c_paired_evidence"),
                "requirements_covered": ["GATE-03", "EXP-05"],
                "input_artifact": str(tmp / "phase11.json"),
                "input_status": "INCONCLUSIVE",
                "profile_eligibility": {
                    "profile": "main",
                    "steps": 3600,
                    "warmup": 900,
                    "eligible": False,
                    "actual_row_count": 0,
                    "expected_row_count": 2160,
                    "all_rows_executed": False,
                },
                "binding_regime_dominance": [],
                "slack_regime_recovery_or_context": [],
                "inconclusive": [],
                "not_evidence": [],
                "required_binding_scenarios": sorted(REQUIRED_GATE_C_SCENARIOS),
                "required_gate_c_comparators": sorted(REQUIRED_GATE_C_COMPARATORS),
                "gate_c_primary_metrics_v1": {"status": "INCONCLUSIVE", "metric_results": []},
            },
        )
        entry = dict(SOURCE_REGISTRY["phase11_gate_c_paired_evidence"])
        entry["path"] = str(path)
        record = load_source_record("phase11_gate_c_paired_evidence", entry)
        assert record["parse_status"] == "FAILED"
        assert record["claim_ready"] is False
        assert any("input_status" in caveat for caveat in record["caveats"])
        assert any("primary metrics" in caveat for caveat in record["caveats"])


def test_lowercase_passed_status_still_runs_internal_phase11_validation() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        path = write_json(
            tmp / "phase11_lowercase.json",
            {
                **source_payload("passed", experiment="phase11_long_horizon_paired_seed_evidence"),
                "route_decision": "finite-storage-context",
                "execution_mode": "fake",
                "scenario_results": phase11_rows(1),
                "actual_row_count": 1,
                "expected_row_count": 1,
                "all_rows_executed": True,
                "gate_c_evaluation": {},
            },
        )
        entry = dict(SOURCE_REGISTRY["phase11_long_horizon_paired_seed_evidence"])
        entry["path"] = str(path)
        record = load_source_record("phase11_long_horizon_paired_seed_evidence", entry)
        assert record["parse_status"] == "FAILED"
        assert record["claim_ready"] is False
        assert any("2160" in caveat for caveat in record["caveats"])


def test_gate_c_passed_with_empty_metric_results_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        path = write_json(
            tmp / "gate_empty_metrics.json",
            {
                **source_payload("PASSED", experiment="phase11_gate_c_paired_evidence"),
                "requirements_covered": ["GATE-03", "EXP-05"],
                "input_artifact": str(tmp / "phase11.json"),
                "input_status": "PASSED",
                "profile_eligibility": {
                    "profile": "main",
                    "steps": 3600,
                    "warmup": 900,
                    "eligible": True,
                    "actual_row_count": 2160,
                    "expected_row_count": 2160,
                    "all_rows_executed": True,
                },
                "binding_regime_dominance": [],
                "slack_regime_recovery_or_context": [],
                "inconclusive": [],
                "not_evidence": [],
                "required_binding_scenarios": sorted(REQUIRED_GATE_C_SCENARIOS),
                "required_gate_c_comparators": sorted(REQUIRED_GATE_C_COMPARATORS),
                "gate_c_primary_metrics_v1": {"status": "PASSED", "metric_results": []},
            },
        )
        entry = dict(SOURCE_REGISTRY["phase11_gate_c_paired_evidence"])
        entry["path"] = str(path)
        record = load_source_record("phase11_gate_c_paired_evidence", entry)
        assert record["parse_status"] == "FAILED"
        assert record["claim_ready"] is False
        assert any("metric_results" in caveat for caveat in record["caveats"])


def test_phase11_passed_requires_main_profile_horizon_and_warmup() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        path = write_json(
            tmp / "phase11_wrong_profile.json",
            {
                **source_payload("PASSED", experiment="phase11_long_horizon_paired_seed_evidence", profile="pilot"),
                "route_decision": "finite-storage-context",
                "execution_mode": "fake",
                "scenario_results": phase11_rows(2160),
                "actual_row_count": 2160,
                "expected_row_count": 2160,
                "all_rows_executed": True,
                "gate_c_evaluation": {},
            },
        )
        entry = dict(SOURCE_REGISTRY["phase11_long_horizon_paired_seed_evidence"])
        entry["path"] = str(path)
        record = load_source_record("phase11_long_horizon_paired_seed_evidence", entry)
        assert record["parse_status"] == "FAILED"
        assert record["claim_ready"] is False
        assert any("profile is not main" in caveat for caveat in record["caveats"])


def test_gate_c_passed_requires_main_profile_and_required_scope() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        path = write_json(
            tmp / "gate_wrong_scope.json",
            {
                **source_payload("PASSED", experiment="phase11_gate_c_paired_evidence"),
                "requirements_covered": ["GATE-03", "EXP-05"],
                "input_artifact": str(tmp / "phase11.json"),
                "input_status": "PASSED",
                "profile_eligibility": {
                    "profile": "pilot",
                    "steps": 3600,
                    "warmup": 900,
                    "eligible": True,
                    "actual_row_count": 2160,
                    "expected_row_count": 2160,
                    "all_rows_executed": True,
                },
                "binding_regime_dominance": [],
                "slack_regime_recovery_or_context": [],
                "inconclusive": [],
                "not_evidence": [],
                "required_binding_scenarios": ["wrong_scenario"],
                "required_gate_c_comparators": ["weak_baseline"],
                "gate_c_primary_metrics_v1": {
                    "status": "PASSED",
                    "metric_results": [{"metric": "penalized_avg_travel_time", "status": "PASSED"}],
                },
            },
        )
        entry = dict(SOURCE_REGISTRY["phase11_gate_c_paired_evidence"])
        entry["path"] = str(path)
        record = load_source_record("phase11_gate_c_paired_evidence", entry)
        assert record["parse_status"] == "FAILED"
        assert record["claim_ready"] is False
        assert any("profile_eligibility.profile" in caveat for caveat in record["caveats"])
        assert any("required binding scenarios" in caveat for caveat in record["caveats"])
        assert any("required comparators" in caveat for caveat in record["caveats"])


def test_claim_inputs_preserve_qualifiers_and_refuse_phase10_phase11_upgrades() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        paths = synthetic_sources(tmp, gate_c_status="INCONCLUSIVE", phase11_status="INCONCLUSIVE")
        records = load_source_records(registry_with_overrides(paths))
        claims = build_claim_inputs(records)
    by_key = {row["source_key"]: row for row in claims["records"]}
    phase10 = by_key["phase10_baselines_stress_suite"]
    assert phase10["source_status"] == "SMOKE_ONLY"
    assert phase10["claim_category"] == "baseline_stress_capability_context"
    assert phase10["claim_allowed"] is False
    assert "dominance" in phase10["caveat"].lower()

    phase11 = by_key["phase11_long_horizon_paired_seed_evidence"]
    assert phase11["source_status"] == "INCONCLUSIVE"
    assert phase11["claim_allowed"] is False
    assert phase11["simulator"] == "SUMO"
    assert phase11["network"] == "unknown"
    assert phase11["horizon_steps"] == 3600
    assert phase11["warmup_steps"] == 900
    assert phase11["seed_count"] == 2
    assert phase11["profile"] == "main"
    assert phase11["demand_multiplier"] == "0.8,1.0,1.2"

    gate_c = by_key["phase11_gate_c_paired_evidence"]
    assert gate_c["gate_status"] == "INCONCLUSIVE"
    assert gate_c["claim_allowed"] is False
    assert "limitation/context" in gate_c["caveat"]


def test_provenance_and_reproduction_manifest_cover_outputs_without_gpu_or_installs() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        paths = synthetic_sources(tmp)
        out_dir = tmp / "out"
        payloads = build_phase12_package(out_dir, registry_with_overrides(paths))
    provenance = payloads["provenance_manifest"]
    expected_outputs = {str(out_dir / name) for name in OUTPUT_FILENAMES.values()}
    derived_outputs = {entry["derived_artifact"] for entry in provenance["derived_artifacts"]}
    assert expected_outputs == derived_outputs
    for entry in provenance["derived_artifacts"]:
        assert set(paths.values()) <= {Path(path) for path in entry["raw_sources"]}
        assert entry["generation_command"].startswith("python scripts/run_phase12_reproducibility_inputs.py")
        assert entry["requirements"]
        assert entry["source_statuses"]
        assert entry["caveats"]

    reproduction = build_reproduction_manifest(out_dir, payloads["source_records"])
    joined = json.dumps(reproduction).lower()
    assert "gpu_required" in joined
    assert "pip install" not in joined
    assert "npm install" not in joined
    assert "conda install" not in joined
    assert "gpu_required\": true" not in joined
    assert "python tests/test_phase12_reproducibility_inputs.py" in joined
    assert "python scripts/check_theory_separation.py" in joined
    assert "python scripts/run_slack_binding_gates.py" in joined
    assert "python scripts/run_phase11_paired_evidence.py" in joined
    assert "python scripts/run_gate_c_paired_evidence.py" in joined
    assert "--execution-row-limit 2160" in joined
    assert "phase11_long_horizon_paired_seed_evidence.progress.json" in joined
    assert "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json" in joined
    assert "--allow-long-horizon" not in joined


def test_claim_audit_detects_policy_and_phase12_specific_forbidden_language() -> None:
    audit = audit_generated_outputs(
        {
            "json": "dual universally beats pressure",
            "markdown": "Gate C passed",
            "csv": "Phase 11 inconclusive dominance",
        },
        gate_c_status="INCONCLUSIVE",
    )
    assert audit["status"] == "FAILED"
    phrases = {hit["phrase"] for hit in audit["hits"]}
    assert "dual universally beats pressure" in phrases
    assert "Gate C passed" in phrases
    assert "phase 11 inconclusive dominance" in phrases


def test_cli_non_strict_writes_all_outputs_and_strict_fails_for_inconclusive_gate_c() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        paths = synthetic_sources(tmp, gate_c_status="INCONCLUSIVE", phase11_status="INCONCLUSIVE")
        out_dir = tmp / "out"
        args = [
            sys.executable,
            str(SCRIPTS / "run_phase12_reproducibility_inputs.py"),
            "--out-dir",
            str(out_dir),
        ]
        for key, path in paths.items():
            args.extend([f"--{key.replace('_', '-')}", str(path)])
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stderr
        for name in OUTPUT_FILENAMES.values():
            assert (out_dir / name).exists(), name
        package = json.loads((out_dir / "phase12_reproducibility_package.json").read_text(encoding="utf-8"))
        assert package["status"] == "INCONCLUSIVE"
        assert any("phase11_gate_c" in reason for reason in package["strict_mode_reasons"])

        strict = subprocess.run([*args, "--strict"], cwd=ROOT, text=True, capture_output=True, check=False)
        assert strict.returncode != 0


def test_cli_strict_passes_for_synthetic_all_passed_bounded_sources() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        paths = synthetic_sources(tmp, gate_c_status="PASSED", phase11_status="PASSED")
        out_dir = tmp / "out"
        args = [
            sys.executable,
            str(SCRIPTS / "run_phase12_reproducibility_inputs.py"),
            "--out-dir",
            str(out_dir),
            "--strict",
        ]
        for key, path in paths.items():
            args.extend([f"--{key.replace('_', '-')}", str(path)])
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stderr
        package = json.loads((out_dir / "phase12_reproducibility_package.json").read_text(encoding="utf-8"))
        audit = json.loads((out_dir / "phase12_claim_audit.json").read_text(encoding="utf-8"))
        assert package["status"] == "PASSED"
        assert audit["status"] == "PASSED"
        assert package["strict_mode_reasons"] == []


def test_written_json_csv_markdown_are_valid_and_without_forbidden_hits() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp = Path(raw_tmp)
        paths = synthetic_sources(tmp, gate_c_status="PASSED", phase11_status="PASSED")
        out_dir = tmp / "out"
        payloads = build_phase12_package(out_dir, registry_with_overrides(paths))
        written = write_phase12_artifacts(out_dir, payloads)
        for key in ["package", "provenance", "claim_inputs", "claim_audit", "reproduction"]:
            loaded = json.loads(written[key].read_text(encoding="utf-8"))
            assert isinstance(loaded, dict)
        csv_text = written["table"].read_text(encoding="utf-8")
        assert "source_status" in csv_text
        assert "claim_allowed" in csv_text
        summary = written["summary"].read_text(encoding="utf-8")
        assert "not manuscript prose" in summary
        assert payloads["claim_audit"]["status"] == "PASSED"


def test_real_default_outputs_have_required_shape_when_present() -> None:
    out_dir = ROOT / "experiments" / "dual_sensitivity"
    package_path = out_dir / "phase12_reproducibility_package.json"
    if not package_path.exists():
        return

    package = json.loads(package_path.read_text(encoding="utf-8"))
    assert package["requirements_covered"] == ["CLAIM-03", "REPRO-01", "REPRO-02", "REPRO-03"]
    assert set(package["source_status_summary"]) == set(SOURCE_REGISTRY)
    assert package["source_status_summary"]["phase10_baselines_stress_suite"] in {"SMOKE_ONLY", "PASSED"}
    if package["source_status_summary"]["phase11_gate_c_paired_evidence"] != "PASSED":
        assert package["status"] != "PASSED"
        assert any("phase11_gate_c_paired_evidence" in reason for reason in package["strict_mode_reasons"])
    if package["source_status_summary"]["phase11_long_horizon_paired_seed_evidence"] != "PASSED":
        assert package["status"] != "PASSED"
        assert any("phase11_long_horizon_paired_seed_evidence" in reason for reason in package["strict_mode_reasons"])

    provenance = json.loads((out_dir / "phase12_provenance_manifest.json").read_text(encoding="utf-8"))
    derived_outputs = {entry["derived_artifact"] for entry in provenance["derived_artifacts"]}
    assert set(package["derived_outputs"]) == derived_outputs
    for entry in provenance["derived_artifacts"]:
        assert entry["raw_sources"]
        assert entry["source_statuses"]
        assert entry["generation_command"]
        assert entry["requirements"] == package["requirements_covered"]
        assert entry["caveats"]

    table_rows = list(csv.DictReader((out_dir / "phase12_table_inputs.csv").open(encoding="utf-8", newline="")))
    required_columns = {
        "source_path",
        "source_status",
        "evidence_role",
        "network",
        "horizon_steps",
        "warmup_steps",
        "seed_count",
        "profile",
        "gate_status",
        "claim_allowed",
        "caveat",
    }
    assert required_columns <= set(table_rows[0])
    assert {row["source_key"] for row in table_rows} == set(SOURCE_REGISTRY)

    claim_inputs = json.loads((out_dir / "phase12_claim_inputs.json").read_text(encoding="utf-8"))
    phase11_rows = [row for row in claim_inputs["records"] if row["source_key"].startswith("phase11")]
    assert phase11_rows
    for row in phase11_rows:
        if row["source_status"] != "PASSED":
            assert row["claim_allowed"] is False
            assert "limitation/context" in row["caveat"]

    claim_audit = json.loads((out_dir / "phase12_claim_audit.json").read_text(encoding="utf-8"))
    assert claim_audit["status"] == "PASSED" or claim_audit["hits"]

    reproduction = json.loads((out_dir / "phase12_reproduction_manifest.json").read_text(encoding="utf-8"))
    joined_commands = "\n".join(command["command"] for command in reproduction["commands"]).lower()
    for forbidden in ["pip install", "conda install", "npm install", "cuda"]:
        assert forbidden not in joined_commands
    assert "--execution-row-limit 2160" in joined_commands
    assert "phase11_long_horizon_paired_seed_evidence.progress.json" in joined_commands
    assert "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json" in joined_commands
    assert "--allow-long-horizon" not in joined_commands
    assert any("opt_in" in command["runtime_profile"] for command in reproduction["commands"])


def main() -> None:
    test_source_registry_has_exact_required_sources_and_commands()
    test_wrong_experiment_identity_fails_closed()
    test_correct_experiment_but_minimal_passed_json_fails_closed()
    test_missing_and_invalid_sources_fail_closed_without_silent_skip()
    test_status_propagation_for_passed_failed_inconclusive_pilot_and_smoke()
    test_phase11_passed_status_requires_complete_execution_metadata()
    test_gate_c_passed_status_requires_internal_passed_inputs_and_metrics()
    test_lowercase_passed_status_still_runs_internal_phase11_validation()
    test_gate_c_passed_with_empty_metric_results_fails_closed()
    test_phase11_passed_requires_main_profile_horizon_and_warmup()
    test_gate_c_passed_requires_main_profile_and_required_scope()
    test_claim_inputs_preserve_qualifiers_and_refuse_phase10_phase11_upgrades()
    test_provenance_and_reproduction_manifest_cover_outputs_without_gpu_or_installs()
    test_claim_audit_detects_policy_and_phase12_specific_forbidden_language()
    test_cli_non_strict_writes_all_outputs_and_strict_fails_for_inconclusive_gate_c()
    test_cli_strict_passes_for_synthetic_all_passed_bounded_sources()
    test_written_json_csv_markdown_are_valid_and_without_forbidden_hits()
    test_real_default_outputs_have_required_shape_when_present()
    print("phase12 reproducibility input tests ok")


if __name__ == "__main__":
    main()
