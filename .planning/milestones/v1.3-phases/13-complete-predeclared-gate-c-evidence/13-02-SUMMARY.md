---
phase: 13-complete-predeclared-gate-c-evidence
plan: 02
status: complete
completed: 2026-05-25
---

# Plan 13-02 Summary: Full Phase 11 Main Execution

## Outcome

Plan 02 completed the locked Phase 11 main profile through the supported resume command. The refreshed source artifact contains all 2160 predeclared rows and reports generated status `FAILED`.

This is a fail-closed result, not a closed-loop superiority claim. Completeness is now resolved; dominance is not.

## Command

```bash
python scripts/run_phase11_paired_evidence.py --profile main --execution-row-limit 2160 --progress-out experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.progress.json --resume-progress experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.progress.json --out experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json
```

Generated output:

```json
{
  "out": "experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json",
  "profile": "main",
  "spec_rows": 2160,
  "result_rows": 2160,
  "status": "FAILED",
  "execution_mode": "executed_with_progress"
}
```

## Refreshed Artifact State

```json
{
  "status": "FAILED",
  "actual_row_count": 2160,
  "expected_row_count": 2160,
  "all_rows_executed": true,
  "missing_row_key_count": 0,
  "execution_mode": "executed_with_progress"
}
```

Progress artifact:

```json
{
  "completed_row_count": 2160,
  "attempted_row_count": 2160,
  "expected_row_count": 2160
}
```

## Row Coverage Audit

- Main profile cardinality: 6 scenarios x 6 controllers x 20 seeds x 3 demand multipliers = 2160 rows.
- Row key uniqueness: passed.
- Required Gate C comparator coverage: passed for complete scenario/demand/seed groups.
- Primary metric numeric schema: passed.
- `finite_storage_primal_dual` rows include `finite_storage_state`, `objective_components`, and `action_decomposition`.
- Missing row key count: 0.

## Generated Gate C Snapshot

- Embedded Phase 11 `gate_c.status`: `FAILED`
- Embedded primary metric rule status: `FAILED`
- Paired-statistic classifications: 48 `bounded_harm`, 221 `inconclusive`, 10 `non_worsening`

## Verification

- Phase 11 source artifact smoke check: passed.
- Row coverage and schema audit: passed.

## Next

Plan 03 should rerun strict Gate C from the refreshed complete Phase 11 artifact and preserve the generated status exactly as `PASSED`, `FAILED`, or `INCONCLUSIVE`.
