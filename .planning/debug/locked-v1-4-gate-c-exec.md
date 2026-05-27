---
status: resolved
trigger: "Let locked v1.4 Gate C truly execute 1440 rows; user is unsure about other symptoms."
created: "2026-05-26T18:12:12+08:00"
updated: "2026-05-26T23:27:36+08:00"
---

# Debug Session: locked-v1-4-gate-c-exec

## Symptoms

- expected_behavior: locked v1.4 Gate C executes all 1440 predeclared rows and produces eligible paired evidence.
- actual_behavior: current evidence reports 0 executed rows out of 1440 expected rows.
- error_messages: unknown.
- timeline: unknown.
- reproduction: use the locked v1.4 Gate C execution and paired-evidence commands if feasible.

## Current Focus

- hypothesis: v1.4 locked execution is using the inherited main-profile fail-closed runtime guard (`DEFAULT_MAIN_EXECUTION_ROW_LIMIT=0`) unless an explicit full row limit is passed.
- test: ran locked Gate C with `--execution-row-limit 1440 --progress-out ...` and then regenerated strict paired evidence.
- expecting: execution artifact reports 1440 completed rows, `all_rows_executed=true`; strict paired evidence no longer fails because of 0 executed rows.
- next_action: treat the remaining issue as a research/statistical Gate C failure, not an execution failure.
- reasoning_checkpoint:
- tdd_checkpoint:

## Evidence

- timestamp: 2026-05-26T18:20:00+08:00
  observation: `scripts/run_phase11_paired_evidence.py` defines `DEFAULT_MAIN_EXECUTION_ROW_LIMIT = 0`; `scripts/run_v14_locked_gate_c.py` assigns that default when `--execution-row-limit` is omitted.
  implication: The default v1.4 main execution command intentionally fails closed before starting any of the 1440 rows.
- timestamp: 2026-05-26T18:21:00+08:00
  observation: Current `v1_4_locked_gate_c_execution.json` reports `expected_row_count=1440`, `actual_row_count=0`, `all_rows_executed=false`, `execution_mode=fail_closed_runtime_guard`.
  implication: The 0-row paired evidence is caused upstream by the execution artifact, not by the strict Gate C checker.
- timestamp: 2026-05-26T18:22:00+08:00
  observation: `experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json` exists and reports `completed_row_count=1`, `attempted_row_count=1`, `expected_row_count=1440`, with no failures.
  implication: SUMO execution can start successfully; the fix is to resume with an explicit full execution limit.
- timestamp: 2026-05-26T18:24:00+08:00
  observation: User instructed this session manager to stop starting any new v1.4 Gate C execution/resume commands because the main orchestrator already has a runner writing `experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json`.
  implication: This session must avoid concurrent writes to the same progress/out artifacts and limit itself to read-only diagnostics plus debug-session notes.
- timestamp: 2026-05-26T18:25:00+08:00
  observation: Read-only process check found one active `python scripts/run_v14_locked_gate_c.py ... --progress-out experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json --execution-row-limit 1440` process; progress read showed `completed_row_count=8`, `attempted_row_count=8`, `expected_row_count=1440`, `failure_count=0`.
  implication: A full 1440-row runner is currently active elsewhere; do not launch or resume another one.
- timestamp: 2026-05-26T23:18:00+08:00
  observation: The locked Gate C runner exited successfully after writing `experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json`; the artifact reports `expected_row_count=1440`, `actual_row_count=1440`, `all_rows_executed=true`, and clean row audit counts (`missing=0`, `failed=0`, `duplicate=0`, `unpaired=0`, `bad_provenance=0`, `schema_invalid=0`).
  implication: The concrete execution blocker is resolved; the 0/1440 failure mode is no longer present in the execution artifact.
- timestamp: 2026-05-26T23:21:00+08:00
  observation: Strict paired-evidence regeneration wrote `experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json` but exited nonzero because the strict status is `INCONCLUSIVE`; profile eligibility is true with 1440/1440 rows, and the reason is `input artifact status is FAILED, not PASSED`.
  implication: The paired checker now sees a complete eligible row set. The remaining failure is the locked Gate C statistical result, not row execution/provenance/schema coverage.
- timestamp: 2026-05-26T23:23:00+08:00
  observation: `gate_c_primary_metrics_v1.status` is `FAILED` under Holm-Bonferroni correction (`num_comparisons=279`, `alpha=0.05`).
  implication: Closed-loop superiority remains disallowed even though the 1440-row confirmation run executed completely.

## Eliminated

- Gate C checker-only bug: strict checker correctly reports no eligible evidence because the input execution artifact has no completed raw rows.
- SUMO environment failure: all 1440 rows completed with no failed rows.
- Locked protocol/controller registry failure: the selected controller ran across the full expected row set.
- Row audit/schema/provenance failure: final audit counts are clean after the full run.

## Resolution

- root_cause: the original 0-row v1.4 evidence came from omitting an explicit execution row limit on the locked main-profile runner. `scripts/run_v14_locked_gate_c.py` inherits `DEFAULT_MAIN_EXECUTION_ROW_LIMIT=0`, so the default main guard fails closed before executing rows.
- fix: reran the locked protocol with explicit `--execution-row-limit 1440` and `--progress-out experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json`, then regenerated strict paired evidence from the completed execution artifact.
- verification: `v1_4_locked_gate_c_execution.json` now has `actual_row_count == expected_row_count == 1440`, `row_audit.completed_row_count == 1440`, `all_rows_executed=true`, and clean row audit counts. `v1_4_gate_c_paired_evidence.json` has eligible profile coverage and clean row audit, but status remains `INCONCLUSIVE` because the input execution artifact's Gate C status is `FAILED`.
- files_changed: `.planning/debug/locked-v1-4-gate-c-exec.md`; `experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json`; `experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json`; `experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json`.
