# Phase 13 Research: Complete Predeclared Gate C Evidence

## RESEARCH COMPLETE

Phase 13 should be planned as an evidence-execution and fail-closed validation phase, not a feature expansion phase. The relevant machinery already exists from Phases 11, 12, and 12.1; the work is to preflight it, resume the full main profile, audit completeness, rerun strict Gate C, and refresh derived Phase 12 artifacts.

## Source of Truth

- `scripts/run_phase11_paired_evidence.py` owns the Phase 11 evidence spec, demand-multiplier materialization, row execution, row-level progress/resume, paired statistics, and source evidence artifact.
- `scripts/run_gate_c_paired_evidence.py` recomputes strict Gate C from the Phase 11 artifact and writes the companion Gate C artifact.
- `scripts/run_phase12_reproducibility_inputs.py` regenerates Phase 12 package, provenance, claim inputs, table inputs, reproduction manifest, summary, and claim audit from raw source artifacts.
- Existing evidence artifacts are under `experiments/dual_sensitivity/`.
- The current progress artifact is `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.progress.json`.

## Current Artifact State

- Phase 11 progress currently reports `completed_row_count=57`, `attempted_row_count=57`, and `expected_row_count=2160`.
- Phase 11 source artifact currently reports `status=INCONCLUSIVE`, `actual_row_count=57`, `expected_row_count=2160`, `all_rows_executed=false`, `missing_row_key_count=2103`, and `execution_mode=interrupted_with_progress_fail_closed`.
- Gate C currently reports `status=INCONCLUSIVE` with `input_status=INCONCLUSIVE`.
- Phase 12 package currently reports `status=INCONCLUSIVE`; claim audit reports `PASSED`; strict blockers are the non-PASSED Phase 11 and Gate C sources.

## Locked Phase 11 Protocol

`run_phase11_paired_evidence.py` locks the main profile through constants and validators:

- Binding scenarios: `arterial_downstream_blockage`, `arterial_spillback_stress`, `arterial_incident_capacity_drop`, `arterial_oversaturation`, `arterial_turning_shock`, `arterial_switching_loss_sensitive`.
- Controllers: `finite_storage_primal_dual`, `max_pressure`, `capacity_aware_pressure`, `finite_storage_double_pressure`, `cycle_pressure`, and `actuated_local_pressure`.
- Required Gate C comparators: `max_pressure`, `capacity_aware_pressure`, and `finite_storage_double_pressure`.
- Main seeds: `20261101` through `20261120`.
- Demand multipliers: `0.8`, `1.0`, and `1.2`.
- Main horizon: at least `3600` steps and `900` warmup.
- Expected main-profile row count: `6 scenarios x 6 controllers x 20 seeds x 3 demand multipliers = 2160`.

The validator rejects missing required comparators, duplicate seeds, missing demand multipliers, sub-main horizon, and invalid output/progress paths.

## Resume and Execution Mechanics

The supported full main-profile resume command is:

```bash
python scripts/run_phase11_paired_evidence.py \
  --profile main \
  --execution-row-limit 2160 \
  --progress-out experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.progress.json \
  --resume-progress experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.progress.json \
  --out experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json
```

Important mechanics:

- Without an explicit row limit, main profile defaults to `DEFAULT_MAIN_EXECUTION_ROW_LIMIT = 0`, which fail-closes before expensive execution.
- `--resume-progress` requires `--progress-out`.
- Progress JSON is rejected on invalid JSON, spec fingerprint mismatch, row keys outside the current spec, conflicting duplicate completed rows, or attempted row keys outside the current spec.
- Completed rows are skipped on resume using `row_key(row) = scenario_tag/demand_multiplier/controller/seed`.
- Runtime failures are collected as explicit `failure_reasons` and do not silently pass.

## Coverage and Failure Audits Needed

Before and after execution, Phase 13 should inspect:

- Spec fingerprint compatibility between expected spec and progress.
- Completed row keys, attempted row keys, missing row keys, and duplicate/conflicting rows.
- Failed/runtime-error rows from `failure_reasons`.
- Required comparator alignment and paired seeds for each scenario/demand multiplier.
- Required row-level metadata: `stress_category`, `stress_mechanism`, finite-storage state, objective components, and action decomposition for `finite_storage_primal_dual`.
- Required numeric primary metrics: `penalized_avg_travel_time`, `total_delay`, `spillback_count`, `blocking_count`, `unfinished_vehicle_count`, plus `switching_count` for switching-loss rows.
- Demand multiplier provenance: actual scaled route/config files, no metadata-only multipliers, valid base/scaled demand totals.

## Strict Gate C Behavior

The strict command is:

```bash
python scripts/run_gate_c_paired_evidence.py \
  --input experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json \
  --out experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json \
  --strict
```

Expected behavior:

- The script writes the Gate C artifact even when status is not `PASSED`.
- `--strict` exits nonzero unless the generated Gate C status is `PASSED`.
- If Phase 11 source status is not `PASSED`, Gate C status is `INCONCLUSIVE`.
- If source is complete but structural/provenance failures exist, Gate C can be `FAILED`.
- Gate C primary metric rule passes only when every applicable metric is non-worsening and every scenario/demand/comparator group has at least one strict positive signal.

## Phase 12 Refresh Behavior

The non-strict refresh command is:

```bash
python scripts/run_phase12_reproducibility_inputs.py --out-dir experiments/dual_sensitivity
```

The strict validation command is:

```bash
python scripts/run_phase12_reproducibility_inputs.py --out-dir experiments/dual_sensitivity --strict
```

Expected behavior:

- Non-strict generation should always write auditable outputs unless source parsing or claim audit fails.
- Strict mode exits nonzero unless the package status is `PASSED`.
- If Phase 11 or Gate C remains `INCONCLUSIVE` or `FAILED`, Phase 12 must preserve that status and keep Phase 11/Gate C claim inputs `claim_allowed=false`.
- The claim audit must remain `PASSED`, with no forbidden universal, deployment, manuscript, or superiority-overclaim phrases.

## Validation Architecture

Phase 13 verification should combine source-level checks and script-level commands:

- Fast unit/script tests: `python tests/test_phase11_paired_evidence.py` and `python tests/test_phase12_reproducibility_inputs.py`.
- Preflight JSON inspection should assert current/progress row counts, expected row count, spec fingerprint compatibility, and absence of conflicting duplicate rows.
- Execution completeness inspection should assert either all 2160 expected rows are completed or every missing/failed row is explicitly reported fail-closed.
- Strict Gate C rerun should produce one of `PASSED`, `FAILED`, or `INCONCLUSIVE`; nonzero strict exit is acceptable when the artifact explicitly records a non-PASSED status.
- Phase 12 refresh should regenerate package outputs from raw artifacts and preserve conservative claim eligibility.
- Final planning/status surfaces must quote generated JSON fields rather than infer claim readiness.

## Planning Implications

Recommended plan sequence:

1. Preflight existing Phase 11 resume state, spec fingerprint, environment, command contract, and row coverage.
2. Resume or execute the full Phase 11 main profile until all rows complete or explicit fail-closed reasons remain.
3. Rerun strict Gate C and preserve the generated status without retuning or evidence-family narrowing.
4. Regenerate Phase 12 artifacts and update final Phase 13 verification/status surfaces.

The long-horizon SUMO command can exceed a single agent window. Plans should preserve resumability and treat interruption as a controlled fail-closed state, while still attempting to complete the full predeclared row family.
