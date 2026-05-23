#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from claim_policy import bounded_claim_policy, forbidden_claim_hits

SCRIPT = SCRIPTS / "audit_claim_discipline.py"


def run_audit(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_claim_policy_encodes_bounded_claim() -> None:
    policy = bounded_claim_policy()

    assert policy["status"] == "PASSED"
    assert policy["permitted_claim"] == (
        "recover_or_tie_max_pressure_when_constraints_slack; "
        "improvement_claims_only_for_explicit_binding_finite_storage_spillback_switching_service_incident_regimes"
    )
    allowed_claims = policy["allowed_claims"]
    assert "slack_recovery_or_tie" in allowed_claims
    assert "binding_regime_improvement_only" in allowed_claims
    assert "finite_storage_state" in allowed_claims["slack_recovery_or_tie"]["evidence_prerequisites"]
    assert "objective_components" in allowed_claims["binding_regime_improvement_only"]["evidence_prerequisites"]
    assert "pressure_equivalent_recovery" in policy["evidence_categories"]
    assert "binding_regime_separation" in policy["evidence_categories"]
    assert "closed_loop_binding_stress" in policy["evidence_categories"]
    assert "insufficient_historical_v1_0" in policy["evidence_categories"]


def test_forbidden_claim_hits_flags_broad_superiority_phrases() -> None:
    text = "\n".join(
        [
            "dual universally beats pressure in this draft",
            "static evidence proves closed-loop outcomes",
            "historical pressure-equivalent evidence proves superiority",
            "this is deployable superiority over max-pressure",
        ]
    )

    hits = forbidden_claim_hits(text, source="draft.md")
    phrases = {hit["phrase"] for hit in hits}

    assert "dual universally beats pressure" in phrases
    assert "static evidence proves closed-loop" in phrases
    assert "proves superiority" in phrases
    assert "deployable superiority" in phrases
    assert all(hit["source"] == "draft.md" for hit in hits)


def test_v1_pressure_equivalent_superiority_wording_fails_closed(tmp_path: Path) -> None:
    report = tmp_path / "report.md"
    policy_out = tmp_path / "phase6_claim_policy.json"
    audit_out = tmp_path / "phase6_claim_audit.json"
    report.write_text(
        "Historical pressure-equivalent evidence proves superiority without Phase 6 binding evidence.",
        encoding="utf-8",
    )

    result = run_audit(
        "--root",
        str(tmp_path),
        "--paths",
        "report.md",
        "--policy-out",
        str(policy_out),
        "--audit-out",
        str(audit_out),
    )

    assert result.returncode != 0
    assert policy_out.exists()
    assert audit_out.exists()
    audit = read_json(audit_out)
    assert audit["status"] == "FAILED"
    assert audit["requirements_covered"] == ["CLAIM-01", "CLAIM-02"]
    assert audit["checked_paths"] == ["report.md"]
    assert audit["claim_policy"]
    assert audit["historical_evidence_quarantine"]["category"] == "insufficient_historical_v1_0"
    assert any(hit["phrase"] == "proves superiority" for hit in audit["forbidden_hits"])


def test_bounded_claim_language_passes_claim_audit(tmp_path: Path) -> None:
    report = tmp_path / "bounded.md"
    policy_out = tmp_path / "phase6_claim_policy.json"
    audit_out = tmp_path / "phase6_claim_audit.json"
    report.write_text(
        "Slack regimes recover/tie max-pressure. Binding improvement needs explicit finite-storage "
        "evidence with objective components before any improvement claim.",
        encoding="utf-8",
    )

    result = run_audit(
        "--root",
        str(tmp_path),
        "--paths",
        "bounded.md",
        "--policy-out",
        str(policy_out),
        "--audit-out",
        str(audit_out),
    )

    assert result.returncode == 0, result.stderr
    audit = read_json(audit_out)
    policy = read_json(policy_out)
    assert policy["status"] == "PASSED"
    assert audit["status"] == "PASSED"
    assert audit["requirements_covered"] == ["CLAIM-01", "CLAIM-02"]
    assert audit["forbidden_hits"] == []
    assert audit["checked_paths"] == ["bounded.md"]
    assert "claim_policy" in audit


def main() -> None:
    test_claim_policy_encodes_bounded_claim()
    test_forbidden_claim_hits_flags_broad_superiority_phrases()
    tmp = Path("/tmp/test_claim_discipline_manual")
    tmp.mkdir(parents=True, exist_ok=True)
    test_v1_pressure_equivalent_superiority_wording_fails_closed(tmp)
    test_bounded_claim_language_passes_claim_audit(tmp)
    print("claim discipline tests ok")


if __name__ == "__main__":
    main()
