# Phase 12: Reproducibility and Future Claim Inputs - Pattern Map

**Mapped:** 2026-05-24
**Files analyzed:** 8 planned files/artifact families
**Analogs found:** 8 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/run_phase12_reproducibility_inputs.py` | utility / config-like artifact generator | file-I/O, transform, batch | `scripts/run_gate_c_paired_evidence.py` + `scripts/render_closed_loop_report.py` | exact |
| `tests/test_phase12_reproducibility_inputs.py` | test | direct assertions, file-I/O fixtures | `tests/test_phase11_paired_evidence.py` | exact |
| `experiments/dual_sensitivity/phase12_reproducibility_package.json` | generated artifact | transform / status aggregation | `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` schema via `scripts/run_phase11_paired_evidence.py` | role-match |
| `experiments/dual_sensitivity/phase12_provenance_manifest.json` | generated artifact | raw-to-derived traceability | `scripts/run_phase11_paired_evidence.py` provenance fields | role-match |
| `experiments/dual_sensitivity/phase12_table_inputs.csv` | generated artifact | CSV transform | `scripts/render_closed_loop_report.py` | exact |
| `experiments/dual_sensitivity/phase12_claim_inputs.json` | generated artifact | claim-template transform | `scripts/claim_policy.py` + `scripts/run_gate_c_paired_evidence.py` | exact |
| `experiments/dual_sensitivity/phase12_claim_audit.json` | generated artifact | claim audit / fail-closed | `scripts/claim_policy.py` + `scripts/render_closed_loop_report.py` | exact |
| `experiments/dual_sensitivity/phase12_reproduction_manifest.json` | generated artifact | CPU/SUMO command manifest | CLI command patterns in Phase 7/9/11 scripts | role-match |

## Pattern Assignments

### `scripts/run_phase12_reproducibility_inputs.py` (utility, file-I/O transform)

**Primary analogs:**
- `scripts/run_gate_c_paired_evidence.py` for strict/non-strict status propagation and source refusal.
- `scripts/render_closed_loop_report.py` for JSON/CSV/Markdown rendering and generated-output claim audit.
- `scripts/run_phase11_paired_evidence.py` for Phase 11 source schema and INCONCLUSIVE/PILOT_ONLY semantics.

**Imports pattern** (`scripts/run_gate_c_paired_evidence.py` lines 10-23):
```python
import argparse
import json
from pathlib import Path
from typing import Any

from run_phase11_paired_evidence import (
    BINDING_EVIDENCE_SCENARIOS,
    GATE_C_CONDITIONAL_PRIMARY_METRICS,
    GATE_C_PRIMARY_METRICS,
    GATE_C_STATISTICAL_FAMILY,
    REQUIRED_GATE_C_COMPARATORS,
    SLACK_CONTEXT_SCENARIOS,
    evaluate_gate_c,
    validate_payload_scope,
)
```

**CLI pattern** (`scripts/run_gate_c_paired_evidence.py` lines 31-36; `scripts/render_closed_loop_report.py` lines 45-51):
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()
```

For Phase 12, copy this style with `--out-dir experiments/dual_sensitivity`, optional `--strict`, and explicit source override flags only if needed. Use `Path` for all path parameters.

**Output/write pattern** (`scripts/run_gate_c_paired_evidence.py` lines 198-203; `scripts/render_closed_loop_report.py` lines 383-392):
```python
def write_gate_artifact(input_path: Path, out_path: Path) -> dict[str, Any]:
    input_payload = load_input_payload(input_path)
    payload = build_gate_payload(input_payload, input_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
```

```python
print(json.dumps({"out": str(out_path), "status": payload["status"], "requirements_covered": payload["requirements_covered"]}, indent=2))
if args.strict and payload["status"] != "PASSED":
    raise SystemExit(1)
```

Phase 12 should write one complete JSON object per artifact via `json.dumps(..., indent=2)`, write CSV with `csv.DictWriter`, then print a compact JSON status object listing `out_dir`, package status, claim-audit status, and generated files.

**Source loading and validation pattern** (`scripts/run_gate_c_paired_evidence.py` lines 39-47):
```python
def load_input_payload(path: Path) -> dict[str, Any]:
    if path.suffix != ".json":
        raise ValueError("--input must point to a .json Phase 11 artifact")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Input artifact {path} must contain a JSON object")
    validate_payload_scope(payload)
    return payload
```

For Phase 12, generalize this into a fixed source registry for Phase 7/9/10/11 artifacts. Missing/unparseable sources should become explicit `FAILED` or `INCONCLUSIVE` source records, not silent omissions.

**Fail-closed status propagation pattern** (`scripts/run_gate_c_paired_evidence.py` lines 145-159):
```python
input_status = str(input_payload.get("status", "")).upper()
source_reasons = [] if input_status == "PASSED" else [f"input artifact status is {input_status or 'missing'}, not PASSED"]
combined_reasons = list(dict.fromkeys(profile_eligibility["reasons"] + demand_reasons + source_reasons + gate_c.get("reasons", [])))
if input_status != "PASSED":
    status = "INCONCLUSIVE"
elif gate_c["status"] == "PASSED" and not profile_eligibility["eligible"]:
    status = "INCONCLUSIVE"
elif demand_reasons and profile_eligibility["eligible"]:
    status = "FAILED"
else:
    status = gate_c["status"]
```

Apply this directly: any Phase 11 or Gate C source not `PASSED` must remain `INCONCLUSIVE`/limitation in Phase 12. Phase 10 `SMOKE_ONLY` may be accepted only as capability/context, never dominance evidence.

**Gate/status artifact shape** (`scripts/run_gate_c_paired_evidence.py` lines 160-193):
```python
payload = {
    "experiment": "phase11_gate_c_paired_evidence",
    "status": status,
    "requirements_covered": REQUIREMENTS_COVERED,
    "input_artifact": str(input_artifact),
    "input_status": input_payload.get("status"),
    "profile_eligibility": profile_eligibility,
    "binding_regime_dominance": gate_c["binding_regime_dominance"],
    "slack_regime_recovery_or_context": gate_c["slack_regime_recovery_or_context"],
    "inconclusive": gate_c["inconclusive"],
    "not_evidence": gate_c["not_evidence"],
    "reasons": combined_reasons,
    "caveats": [...],
}
```

Phase 12 package should include top-level `experiment`, `status`, `requirements_covered`, `generated_by`, `generated_at`, `source_statuses`, `derived_outputs`, `reproduction_manifest`, `claim_audit`, `reasons`, and `caveats`.

**CSV/Markdown rendering pattern** (`scripts/render_closed_loop_report.py` lines 346-380 and 383-392):
```python
def write_csv(payload: dict[str, Any], csv_path: Path) -> None:
    validate_payload(payload)
    fieldnames = [
        "row_type",
        "network",
        "scenario_tag",
        "controller",
        "seed",
        "status",
        ...
    ]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows(payload))
```

Phase 12 table rows should add mandatory provenance/status fields: `source_experiment`, `source_path`, `source_status`, `evidence_role`, `claim_allowed`, `gate_status`, `profile`, `steps`, `warmup`, `seed_count`, `caveat`.

### `tests/test_phase12_reproducibility_inputs.py` (test, direct assertions)

**Analog:** `tests/test_phase11_paired_evidence.py` and `tests/test_slack_binding_gates.py`.

**Import/bootstrap pattern** (`tests/test_phase11_paired_evidence.py` lines 11-38):
```python
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_phase11_paired_evidence import (...)
from run_gate_c_paired_evidence import (...)
```

Copy this exactly for importing pure helpers from `run_phase12_reproducibility_inputs.py`.

**Synthetic fixture + direct assertion pattern** (`tests/test_phase11_paired_evidence.py` lines 250-318):
```python
def make_row(... ) -> dict[str, Any]:
    row = {
        "network": "arterial",
        "scenario_tag": scenario,
        "controller": controller,
        "seed": seed,
        "profile": "main",
        "steps": 3600,
        "warmup": 900,
        "demand_multiplier": demand_multiplier,
        "scenario_status": "completed",
        "feasibility_status": "run",
        "finite_storage_state": finite_storage_state(),
        "objective_components": objective_components(),
        ...
    }
    return row
```

For Phase 12, use synthetic source payloads for statuses `PASSED`, `FAILED`, `INCONCLUSIVE`, `PILOT_ONLY`, and `SMOKE_ONLY` instead of running SUMO.

**Fail-closed tests to copy** (`tests/test_phase11_paired_evidence.py` lines 546-565, 567-584):
```python
def test_gate_checker_refuses_to_upgrade_inconclusive_source_artifact() -> None:
    ...
    payload = {"status": "INCONCLUSIVE", ...}
    result = build_gate_payload(payload, Path("synthetic_phase11.json"))
    assert result["status"] == "INCONCLUSIVE"
    assert any("input artifact status" in reason for reason in result["reasons"])
```

```python
def test_gate_checker_requires_complete_execution_metadata() -> None:
    ...
    result = build_gate_payload(payload, Path("missing_all_rows_executed.json"))
    assert result["status"] == "INCONCLUSIVE"
    assert any("missing required executed rows" in reason for reason in result["reasons"])
```

Add equivalent Phase 12 tests for: missing source artifact, unparseable JSON, non-`PASSED` source propagation, Phase 10 `SMOKE_ONLY` not claim-eligible, Phase 11 `INCONCLUSIVE` not dominance evidence, forbidden claim text, strict nonzero behavior, and provenance entries for every derived file.

**Direct main runner pattern** (`tests/test_phase11_paired_evidence.py` lines 677-708; `tests/test_slack_binding_gates.py` lines 285-311):
```python
def main() -> None:
    test_main_spec_enforces_long_horizon_seed_and_multiplier_contracts()
    ...
    print("phase11 paired evidence tests ok")

if __name__ == "__main__":
    main()
```

No pytest config is required; tests should be runnable as `python tests/test_phase12_reproducibility_inputs.py`.

## Shared Patterns

### Existing script CLI/output conventions

**Source:** `scripts/check_theory_separation.py` lines 229-240.
```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/dual_sensitivity/phase7_theory_separation.json")
    args = parser.parse_args()

    payload = build_and_check_phase7_payload()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": str(out_path)}, indent=2))
    if payload["status"] != "PASSED":
        raise SystemExit(1)
```

Use for Phase 12: `argparse`, `Path`, `json.dumps(..., indent=2)`, parent directory creation, compact JSON stdout, `SystemExit(1)` only for strict/gate failure.

### Existing fail-closed status propagation patterns

**Phase 11 payload status:** `scripts/run_phase11_paired_evidence.py` lines 854-865.
```python
def _status_for_payload(profile: str, dry_run: bool, spec: list[dict[str, Any]], rows: list[dict[str, Any]], gate_c: dict[str, Any], missing_reasons: list[str]) -> str:
    if profile == "pilot" or dry_run:
        return "PILOT_ONLY"
    if missing_reasons:
        return "INCONCLUSIVE"
    if len(rows) < len(spec):
        return "INCONCLUSIVE"
    if gate_c["status"] == "PASSED":
        return "PASSED"
    if gate_c["status"] == "FAILED":
        return "FAILED"
    return "INCONCLUSIVE"
```

**Phase 9 gate pass composition:** `scripts/run_slack_binding_gates.py` lines 305-310.
```python
def gates_pass(payload: dict[str, Any]) -> bool:
    return (
        payload.get("gate_a_slack_recovery", {}).get("status") == "PASSED"
        and payload.get("gate_b_binding_separation", {}).get("status") == "PASSED"
        and all(value == "PASSED" for value in payload.get("fail_closed_checks", {}).values())
    )
```

Phase 12 strict status should be composed similarly: source eligibility + generated-output claim audit + provenance completeness. Non-strict may write `INCONCLUSIVE` packages for audit.

### Existing claim-audit patterns

**Central forbidden-claim scanner:** `scripts/claim_policy.py` lines 12-19 and 142-149.
```python
FORBIDDEN_CLAIM_PATTERNS: list[str] = [
    "dual universally beats pressure",
    "proves superiority",
    "deployable superiority",
    "static evidence proves closed-loop",
    "universal dominance",
    "universally dominates pressure",
]
```

```python
def forbidden_claim_hits(text: str, source: str = "<memory>") -> list[dict[str, str]]:
    lowered = text.lower()
    hits: list[dict[str, str]] = []
    for phrase in FORBIDDEN_CLAIM_PATTERNS:
        normalized = phrase.lower()
        if has_unbounded_phrase(lowered, normalized):
            hits.append({"source": source, "path": source, "phrase": phrase})
    return hits
```

**Generated report scan:** `scripts/render_closed_loop_report.py` lines 265-275.
```python
report = "\n".join(lines).rstrip() + "\n"
forbidden = forbidden_claim_hits(report)
lowered = report.lower()
forbidden.extend(
    {"source": "rendered_report", "path": "rendered_report", "phrase": phrase}
    for phrase in RENDERER_FORBIDDEN_PHRASES
    if phrase in lowered
)
if forbidden:
    raise ValueError(f"Rendered report contains forbidden overclaim language: {forbidden}")
return report
```

**Phase-specific forbidden language:** `scripts/run_phase11_paired_evidence.py` lines 659-686.
```python
FORBIDDEN_AFFIRMATIVE_PHRASES = (
    "universal dominance",
    "universal superiority",
    "deployment readiness",
    "final manuscript claim",
    "manuscript claim",
    "superior to max-pressure outside binding regimes",
    "superiority over max-pressure outside binding regimes",
    "broad superiority over max-pressure",
    "phase 10 proves superiority",
    "phase 10 superiority",
    "phase 10 dominance",
)
```

Phase 12 should reuse `forbidden_claim_hits` and add source-upgrade phrases such as `Phase 11 proves dominance`, `Gate C passed` when Gate C source status is not `PASSED`, `Phase 10 dominance`, `SMOKE_ONLY superiority`, and `INCONCLUSIVE evidence of superiority`.

### Existing direct-test patterns

**Forbidden language direct test:** `tests/test_phase11_paired_evidence.py` lines 483-497.
```python
def test_validate_payload_scope_rejects_forbidden_claim_language() -> None:
    validate_payload_scope({"claim": "closed-loop paired-seed evidence in predeclared binding stress regimes"})
    for phrase in [
        "universal dominance",
        "deployment readiness",
        "final manuscript claim",
        "superior to max-pressure outside binding regimes",
        "Phase 10 proves superiority",
    ]:
        try:
            validate_payload_scope({"claim": phrase})
        except ValueError as exc:
            assert phrase.lower().split()[0] in str(exc).lower() or "forbidden" in str(exc).lower()
        else:
            raise AssertionError(f"forbidden claim language should fail: {phrase}")
```

**CLI writer test:** `tests/test_slack_binding_gates.py` lines 268-282.
```python
def test_cli_writer_creates_passed_artifact() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "phase9_gate.json"
        payload = write_gate_artifact(out, PHASE7_JSON)
        written = json.loads(out.read_text(encoding="utf-8"))
    assert payload["status"] == "PASSED"
    assert written["status"] == "PASSED"
    assert written["fail_closed_checks"] == {...}
```

Phase 12 should use `tempfile.TemporaryDirectory()` to verify generated JSON/CSV/Markdown/manifest files and avoid touching real experiment artifacts in unit tests.

## Recommended Mapping from Phase 12 Functions to Closest Analogs

| Phase 12 Function / Responsibility | Closest Analog | Copy Pattern |
|---|---|---|
| `parse_args()` | `scripts/run_gate_c_paired_evidence.py` lines 31-36 | `argparse`, `--strict`, default paths |
| `load_source_artifact(path, registry_entry)` | `scripts/run_gate_c_paired_evidence.py` lines 39-47 | `.json` check, JSON object validation, scope/claim validation |
| `build_source_registry()` / module constant | `scripts/run_phase11_paired_evidence.py` lines 26-83 and 56-59 | module-level constants for scenarios, outputs, accepted statuses |
| `derive_source_statuses()` | `scripts/run_gate_c_paired_evidence.py` lines 145-159 | non-`PASSED` source remains non-claim-ready |
| `build_reproducibility_package()` | `scripts/run_phase11_paired_evidence.py` lines 868-963 | top-level experiment/status/schema/caveats/source rows |
| `build_claim_inputs()` | `scripts/claim_policy.py` lines 42-99 | allowed claims, evidence prerequisites, forbidden patterns |
| `audit_generated_outputs()` | `scripts/render_closed_loop_report.py` lines 265-275 | scan rendered text and raise/fail on hits |
| `csv_rows()` / `write_table_inputs()` | `scripts/render_closed_loop_report.py` lines 278-343 and 346-380 | row builders + `csv.DictWriter` fieldnames |
| `build_reproduction_manifest()` | Phase 7/9/11 CLI lines above | structured commands for fast tests, regeneration, strict Gate C, opt-in long-horizon |
| `write_outputs(out_dir, strict)` | `scripts/run_gate_c_paired_evidence.py` lines 198-213 | write artifact, print JSON, strict exits nonzero on non-PASSED |
| Phase 12 synthetic tests | `tests/test_phase11_paired_evidence.py` lines 500-674 | temporary JSON sources, assert non-upgrade and forbidden language rejection |

## Pitfalls Specific to Phase 10 and Phase 11

### Phase 10 smoke-only evidence

- Treat Phase 10 source status `SMOKE_ONLY` as `baseline_stress_capability_context` only.
- Do not place Phase 10 rows in a `binding_regime_superiority` or `dominance` claim category.
- Add `claim_allowed=false` for dominance language in derived rows sourced from Phase 10.
- Scan for phrases already forbidden by Phase 11: `phase 10 proves superiority`, `phase 10 superiority`, `phase 10 dominance` (`scripts/run_phase11_paired_evidence.py` lines 668-670).

### Phase 11 inconclusive evidence

- Current Phase 11 main/Gate C artifacts are expected `INCONCLUSIVE`; Phase 12 must preserve `actual_row_count`, `expected_row_count`, `all_rows_executed`, `execution_mode`, `profile_eligibility`, and `reasons` when available.
- Copy the refusal-to-upgrade rule from `scripts/run_gate_c_paired_evidence.py` lines 148-153: non-`PASSED` input status forces `INCONCLUSIVE`.
- Strict Phase 12 mode should exit nonzero while Gate C remains non-`PASSED`; non-strict mode may emit a package marked `INCONCLUSIVE`.
- Slack/control rows are context only and cannot satisfy dominance evidence (`scripts/run_gate_c_paired_evidence.py` lines 187-190 caveats).

## No Analog Found

None. The Phase 12 work is fully covered by existing artifact-generator, gate-checker, claim-policy, renderer, and direct-test patterns.

## Metadata

**Analog search scope:** required Phase 7/9/11 scripts, renderer, claim policy, Phase 9/11 tests, project `CLAUDE.md`.
**Files scanned:** 13 required/context files plus project instructions and skills directory check.
**Pattern extraction date:** 2026-05-24
