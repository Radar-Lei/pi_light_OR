---
phase: 13-complete-predeclared-gate-c-evidence
plan: 04
status: complete
completed: 2026-05-25
---

# Plan 13-04 Summary: Phase 12 Refresh and Phase 13 Closeout

## Outcome

Plan 04 regenerated the Phase 12 reproducibility and claim-status artifact family from the refreshed Phase 11 and strict Gate C outputs.

The generated package status is `INCONCLUSIVE`; claim audit status is `PASSED`. Closed-loop superiority remains disallowed because the Phase 11 source artifact is `FAILED` and strict Gate C is `INCONCLUSIVE`.

## Commands

```bash
python scripts/run_phase12_reproducibility_inputs.py --out-dir experiments/dual_sensitivity
python tests/test_phase12_reproducibility_inputs.py
python scripts/run_phase12_reproducibility_inputs.py --out-dir experiments/dual_sensitivity --strict
```

Strict mode exited nonzero as expected, with generated reasons:

```json
[
  "phase11_long_horizon_paired_seed_evidence source status is FAILED, expected one of ['PASSED']",
  "phase11_gate_c_paired_evidence source status is INCONCLUSIVE, expected one of ['PASSED']"
]
```

## Refreshed Statuses

```json
{
  "phase11_long_horizon_paired_seed_evidence": {
    "status": "FAILED",
    "actual_row_count": 2160,
    "expected_row_count": 2160,
    "all_rows_executed": true
  },
  "phase11_gate_c_paired_evidence": {
    "status": "INCONCLUSIVE",
    "input_status": "FAILED"
  },
  "phase12_reproducibility_package": {
    "status": "INCONCLUSIVE",
    "claim_audit_status": "PASSED"
  },
  "phase12_claim_audit": {
    "status": "PASSED"
  }
}
```

## Claim Inputs

- `phase11_long_horizon_paired_seed_evidence`: `claim_allowed=false`, `source_status=FAILED`, `gate_status=FAILED`.
- `phase11_gate_c_paired_evidence`: `claim_allowed=false`, `source_status=INCONCLUSIVE`, `gate_status=FAILED`.
- Phase 7 and Phase 9 static/theory inputs remain claim-allowed only within their bounded static/slack-binding scope.
- Phase 10 remains `SMOKE_ONLY` and not dominance evidence.

## Generated Files

- `experiments/dual_sensitivity/phase12_reproducibility_package.json`
- `experiments/dual_sensitivity/phase12_provenance_manifest.json`
- `experiments/dual_sensitivity/phase12_table_inputs.csv`
- `experiments/dual_sensitivity/phase12_claim_inputs.json`
- `experiments/dual_sensitivity/phase12_claim_audit.json`
- `experiments/dual_sensitivity/phase12_reproduction_manifest.json`
- `experiments/dual_sensitivity/phase12_summary.md`

## Verification

- Phase 12 non-strict regeneration: passed.
- `python tests/test_phase12_reproducibility_inputs.py`: passed.
- Phase 12 strict validation: fail-closed nonzero with explicit upstream status reasons.
- Final Phase 11 and Phase 12 fast suites are covered in `13-VERIFICATION.md`.

## Final Phase 13 Result

Phase 13 completed the predeclared Gate C evidence closure. The result is not a positive closed-loop superiority result:

- Evidence coverage is complete: 2160/2160 rows.
- Phase 11 generated status: `FAILED`.
- Strict Gate C generated status: `INCONCLUSIVE`.
- Phase 12 package generated status: `INCONCLUSIVE`.
- Claim audit generated status: `PASSED`.
- Closed-loop superiority claim eligibility: disallowed.
