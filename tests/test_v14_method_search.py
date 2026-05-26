#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_v14_candidate_convergence import write_outputs as write_convergence  # noqa: E402
from run_v14_failure_diagnostics import write_outputs as write_diagnostics  # noqa: E402
from run_v14_workstream_pilots import write_pilots  # noqa: E402


def test_v14_failure_diagnostics_summarizes_gate_c_and_workstreams(tmp_path: Path) -> None:
    out = tmp_path / "diag.json"
    report = tmp_path / "diag.md"
    payload = write_diagnostics(
        ROOT / "experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json",
        ROOT / "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json",
        out,
        report,
    )

    assert payload["status"] == "PASSED"
    assert payload["source_artifacts"]["gate_c_status"] == "INCONCLUSIVE"
    assert payload["overall_classification_counts"]["bounded_harm"] > 0
    assert payload["overall_classification_counts"]["inconclusive"] > 0
    assert payload["claim_boundary"]["claim_ready"] is False
    assert len(payload["workstreams"]) == 4
    assert all(item["claim_ready"] is False for item in payload["workstreams"])
    assert payload["metric_bucket_summary"]
    assert report.read_text(encoding="utf-8").startswith("# v1.4 Failure Diagnostics")


def test_v14_workstream_pilots_are_exploratory_and_evaluated(tmp_path: Path) -> None:
    diagnostics_path = tmp_path / "diag.json"
    write_diagnostics(
        ROOT / "experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json",
        ROOT / "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json",
        diagnostics_path,
        tmp_path / "diag.md",
    )
    index_path = tmp_path / "workstreams" / "index.json"
    index = write_pilots(diagnostics_path, "all", tmp_path / "workstreams", index_path)

    assert index["status"] == "PASSED"
    assert index["claim_ready"] is False
    assert len(index["artifacts"]) == 4
    statuses = set()
    for item in index["artifacts"]:
        payload = json.loads((ROOT / item["path"]).read_text(encoding="utf-8")) if not Path(item["path"]).is_absolute() and not str(item["path"]).startswith(str(tmp_path)) else json.loads(Path(item["path"]).read_text(encoding="utf-8"))
        statuses.add(payload["status"])
        assert payload["claim_ready"] is False
        assert payload["final_gate_c_import_allowed"] is False
        assert payload["candidate_id"]
        assert payload["selection_criteria_results"]
        assert payload["action_decomposition"]["required_components"]
    assert {"candidate", "rejected", "archived"} <= statuses


def test_v14_convergence_locks_at_most_one_protocol_candidate(tmp_path: Path) -> None:
    diagnostics_path = tmp_path / "diag.json"
    write_diagnostics(
        ROOT / "experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json",
        ROOT / "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json",
        diagnostics_path,
        tmp_path / "diag.md",
    )
    index_path = tmp_path / "workstreams" / "index.json"
    write_pilots(diagnostics_path, "all", tmp_path / "workstreams", index_path)
    convergence = write_convergence(
        diagnostics_path,
        index_path,
        tmp_path / "convergence.json",
        tmp_path / "protocol.json",
        tmp_path / "convergence.md",
    )
    protocol = json.loads((tmp_path / "protocol.json").read_text(encoding="utf-8"))

    assert convergence["status"] == "PASSED"
    assert convergence["at_most_one_candidate_promoted"] is True
    assert convergence["selected_candidate"] is not None
    assert protocol["status"] == "LOCKED"
    assert protocol["pre_confirmation_lock"] is True
    assert protocol["spec_fingerprint"] == convergence["locked_protocol_fingerprint"]
    assert "max_pressure" in protocol["required_comparators"]
    assert protocol["claim_ready"] is False
