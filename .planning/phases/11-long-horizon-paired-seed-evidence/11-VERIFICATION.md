---
phase: 11-long-horizon-paired-seed-evidence
verified: 2026-05-24T11:43:04Z
status: passed
score: "4/4 must-haves verified"
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: "1/4 must-haves verified"
  gaps_closed:
    - "Gate C now rejects single-seed evidence and requires at least two paired seeds for confidence intervals."
    - "Standalone Gate C no longer upgrades an INCONCLUSIVE input artifact to PASSED."
    - "Strict Gate C exits nonzero for INCONCLUSIVE as well as FAILED."
    - "Generated 7200-step demand inputs now extend route flow end times to the requested horizon."
    - "Final finite_storage_state uses active incident state rather than stale incident metadata after the temporary capacity-drop window."
  gaps_remaining: []
  regressions: []
---

# Phase 11: Long-Horizon Paired-Seed Evidence Verification Report

**Phase Goal:** Researchers can evaluate closed-loop dominance only in predeclared binding stress regimes using long horizons, paired seeds, and statistical uncertainty.  
**Verified:** 2026-05-24T11:43:04Z  
**Status:** passed  
**Re-verification:** Yes — after gap closure

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | User can run long-horizon closed-loop experiments with 3600–7200s horizons, appropriate warmup, demand multiplier sweeps, and paired seeds where computationally feasible. | VERIFIED | `build_phase11_spec(profile="main")` produces 2160 rows: 6 binding scenarios × 6 controllers × 20 seeds × 3 demand multipliers, with 3600 steps and 900 warmup. `generate_scaled_route_and_sumocfg('arterial', 1.0, 7200, ...)` produced `cfg_end=7200` and route `min_flow_end=7200.0`. The current main artifact honestly records runtime-guard non-execution rather than false dominance. |
| 2 | User can inspect paired statistical reports with confidence intervals, effect sizes, and multiple-comparison handling where relevant. | VERIFIED | `paired_metric_summary` and `evaluate_gate_c_primary_metric_rule` cover all D-11-04 primary metrics, conditional `switching_count`, paired bootstrap CI, effect size, paired diagnostics, and Holm-Bonferroni metadata. Tests pass and include single-seed rejection via `MIN_GATE_C_PAIRED_SEEDS == 2`. Current artifact has `paired_statistics=[]` because `actual_row_count=0`, which is honest for INCONCLUSIVE evidence. |
| 3 | User can run Gate C and see closed-loop dominance evaluated only in predeclared binding stress regimes against the strongest feasible baselines. | VERIFIED | `scripts/run_gate_c_paired_evidence.py` imports shared Phase 11 constants/evaluator, reports only the six binding scenarios and required comparators (`max_pressure`, `capacity_aware_pressure`, `finite_storage_double_pressure`), refuses non-PASSED source artifacts from being upgraded, and strict mode exited `1` for current INCONCLUSIVE input. |
| 4 | User can distinguish slack-regime ties/recovery from binding-regime wins in the experiment summaries. | VERIFIED | `evaluate_gate_c` and Gate C output expose separate `binding_regime_dominance`, `slack_regime_recovery_or_context`, `inconclusive`, and `not_evidence` sections. Synthetic tests verify slack rows do not populate binding dominance. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `scripts/run_phase11_paired_evidence.py` | Phase 11 runner, demand scaling, paired statistics, shared Gate C evaluator, payload writer | VERIFIED | Exists and substantive. Uses `run_experiment(..., sumocfg_override=...)`, extends route flows to requested horizon, requires paired seeds, computes all-primary-metric statistics, and writes fail-closed main artifacts. |
| `scripts/run_gate_c_paired_evidence.py` | Standalone fail-closed Gate C checker | VERIFIED | Exists and substantive. Imports shared constants/evaluator, validates input status/profile/execution/demand provenance, writes Gate C artifact, and exits nonzero in strict mode unless status is `PASSED`. |
| `scripts/run_closed_loop_sumo.py` | SUMO primitive with `sumocfg_override` and active incident state | VERIFIED | `run_experiment` exposes `sumocfg_override`, uses it in the SUMO command, records `sumocfg` and `base_sumocfg`, and passes active incident state into final finite-storage state. |
| `tests/test_phase11_paired_evidence.py` | Fast synthetic tests for Phase 11 contracts and regressions | VERIFIED | `python /home/samuel/projects/pi_light_OR/tests/test_phase11_paired_evidence.py` exited 0 with `phase11 paired evidence tests ok`. Tests cover demand horizon extension, one-seed rejection, strict checker behavior, and source-status non-upgrade. |
| `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` | Main Phase 11 artifact or honest fail-closed artifact | VERIFIED | Current artifact is `profile=main`, `status=INCONCLUSIVE`, `steps=3600`, `warmup=900`, `expected_row_count=2160`, `actual_row_count=0`, `all_rows_executed=false`, `execution_mode=fail_closed_runtime_guard`, with explicit missing-row reasons. |
| `experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json` | Machine-readable Gate C output | VERIFIED | Non-strict checker writes `status=INCONCLUSIVE`, `input_status=INCONCLUSIVE`, no binding dominance rows, explicit no-executed-row reasons, and valid actual demand multiplier provenance summary. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `tests/test_phase11_paired_evidence.py` | `scripts/run_phase11_paired_evidence.py` | direct imports and direct assertions | VERIFIED | Test file imports and exercises spec construction, demand materialization, paired statistics, Gate C rule, and payload validation. |
| `tests/test_phase11_paired_evidence.py` | `scripts/run_gate_c_paired_evidence.py` | direct imports | VERIFIED | Test file imports `build_gate_payload`, `load_input_payload`, and `write_gate_artifact`; regression tests cover strict checker semantics. |
| `scripts/run_phase11_paired_evidence.py` | `scripts/run_closed_loop_sumo.py` | `sumocfg_override` call | VERIFIED | `execute_spec` calls `run_experiment(..., sumocfg_override=item["generated_sumocfg"])`; no duplicate TraCI loop is introduced. |
| `scripts/run_gate_c_paired_evidence.py` | Phase 11 evidence artifact | `--input` / JSON load | VERIFIED | Checker reads `phase11_long_horizon_paired_seed_evidence.json`, validates scope, recomputes Gate C from raw rows, and records source status. |
| `scripts/run_gate_c_paired_evidence.py` | Gate C artifact | `--out` / JSON write | VERIFIED | Non-strict invocation rewrote `phase11_gate_c_paired_evidence.json` with current INCONCLUSIVE status and exit 0. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `phase11_long_horizon_paired_seed_evidence.json` | `scenario_results`, `actual_row_count`, `expected_row_count` | `build_payload` over `execute_spec`; main default runtime guard has row limit 0 | Produces honest no-row INCONCLUSIVE artifact, not dominance evidence | VERIFIED |
| `phase11_gate_c_paired_evidence.json` | `status`, `reasons`, section tables | `build_gate_payload` over current Phase 11 artifact and shared `evaluate_gate_c` | Produces INCONCLUSIVE Gate C output with explicit no-executed-row and source-status reasons | VERIFIED |
| `phase11_scaled_inputs/*.rou.xml` and `.sumocfg` | demand multiplier route/config files | `generate_scaled_route_and_sumocfg` | Provenance has 0.8/1.0/1.2 distinct scaled totals and existing generated files; 7200 probe extended flows to 7200 | VERIFIED |
| `finite_storage_state.incident_capacity_drop` | active incident flag/factor | `run_closed_loop_sumo.run_experiment` final `failure_mode_active` | Active flag is used for final state, preventing stale incident state after the temporary window | VERIFIED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Phase 11 test suite passes | `python /home/samuel/projects/pi_light_OR/tests/test_phase11_paired_evidence.py` | Exit 0; `phase11 paired evidence tests ok` | PASS |
| Current main artifact is honest INCONCLUSIVE | Python JSON inspection of `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` | `status=INCONCLUSIVE`, `actual_row_count=0`, `expected_row_count=2160`, runtime guard reasons present | PASS |
| Strict Gate C fails closed for INCONCLUSIVE | `python /home/samuel/projects/pi_light_OR/scripts/run_gate_c_paired_evidence.py --input ...phase11_long_horizon...json --out ...phase11_gate_c...json --strict` | Printed `status=INCONCLUSIVE`; captured `EXIT_CODE=1` | PASS |
| Non-strict Gate C writes INCONCLUSIVE artifact | Same command without `--strict` | Printed `status=INCONCLUSIVE`; captured `EXIT_CODE=0`; artifact written | PASS |
| 7200-step demand scaling covers full horizon | Focused Python probe calling `generate_scaled_route_and_sumocfg('arterial', 1.0, 7200, tmp)` | `cfg_end="7200"`, `min_flow_end=7200.0` | PASS |
| Gate checker refuses to upgrade INCONCLUSIVE source artifact | Synthetic passing rows wrapped in `status=INCONCLUSIVE` input to `build_gate_payload` | Output status `INCONCLUSIVE` | PASS |

### Probe Execution

| Probe | Command | Result | Status |
|---|---|---|---|
| Conventional probes | `find /home/samuel/projects/pi_light_OR/scripts -path '*/tests/probe-*.sh' -type f` | No `probe-*.sh` scripts found for this phase | SKIPPED |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| GATE-03 | 11-01, 11-02, 11-03 | Gate C verifies closed-loop dominance only in predeclared binding stress regimes using paired-seed CIs against strongest feasible baselines. | SATISFIED | Gate C is machine-readable, binding-only, strongest-comparator-scoped, shared-rule based, strict fail-closed for INCONCLUSIVE, and does not pass with missing rows. |
| EXP-03 | 11-01, 11-02 | Long-horizon closed-loop experiments use 3600–7200s horizons, appropriate warmup, demand multiplier sweeps, and paired seeds where feasible. | SATISFIED | Main spec and artifact target 3600/900, 20 seeds, 0.8/1.0/1.2 multipliers; 7200 demand extension probe passes; current no-row execution is explicitly INCONCLUSIVE due runtime guard. |
| EXP-05 | 11-01, 11-02, 11-03 | Statistical reports include paired bootstrap or paired t/Wilcoxon confidence intervals, effect sizes, and multiple-comparison handling where relevant. | SATISFIED | Shared helpers compute paired bootstrap CIs, diagnostics, effect sizes, and Holm-Bonferroni metadata; tests cover all primary metrics and reject one-seed evidence. |

No additional Phase 11 requirement IDs were found in `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md` beyond GATE-03, EXP-03, and EXP-05.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `scripts/run_closed_loop_sumo.py` | 612 | `return {}` for unknown stress metadata | INFO | Not a Phase 11 blocker; known fallback for non-stress scenario tags, while Phase 11 binding scenarios are mapped. |
| `scripts/run_phase11_paired_evidence.py` | 967-1006 | dry-run placeholder rows | INFO | Intended dry-run/spec-only path; artifacts are classified `PILOT_ONLY`/`INCONCLUSIVE`, not dominance evidence. |
| `scripts/run_phase11_paired_evidence.py` | 1010 | runtime guard returns no rows | INFO | Intended fail-closed guard; current main artifact records INCONCLUSIVE with explicit row counts and reasons. |

No unreferenced `TBD`, `FIXME`, or `XXX` blockers were found in the Phase 11 modified files scanned.

### Human Verification Required

None. The scoped expected behavior is verifiable from code, tests, JSON artifacts, and CLI exit codes.

### Gaps Summary

No blocking gaps remain for the scoped Phase 11 goal. The current artifact is not dominance evidence; it is an honest main-profile `INCONCLUSIVE` artifact because the runtime guard prevented all 2160 requested rows from executing. This is the expected current behavior and is fail-closed through Gate C: strict mode exits nonzero, while non-strict mode writes the INCONCLUSIVE Gate C artifact.

---

_Verified: 2026-05-24T11:43:04Z_  
_Verifier: Claude (gsd-verifier)_
