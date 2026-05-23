---
phase: 02-full-sparse-symbolic-recovery
verified: 2026-05-22T18:15:36Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 2: Full Sparse Symbolic Recovery Verification Report

**Phase Goal:** The code can recover compact, auditable symbolic signal-control policies from dual-guided oracle targets while explicitly trading off regret, program size, neighbor use, and dual-price dependence.
**Verified:** 2026-05-22T18:15:36Z
**Status:** passed
**Re-verification:** No — initial goal-backward verification; no previous `02-VERIFICATION.md` existed.

## Goal Achievement

Phase 2 is verified against ROADMAP Phase 2 success criteria and RECV-01 through RECV-05. SUMMARY.md claims were treated as non-evidence; verification used `scripts/run_sparse_recovery.py`, generated JSON/CSV/rule artifacts, and an independent quick validation command.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The recovery pipeline can solve K-atom symbolic policies beyond one-atom pilots. | VERIFIED | `scripts/run_sparse_recovery.py` supports `--budgets` / `--max-atoms` and applies total atom budget constraints in `solve_library()`; `block2_sparse_recovery.json` has `gate_k_gt_one_solved: true`, budgets `[1, 2, 3]`, and 7 solved runs with `max_atoms > 1`. Independent quick validation also returned `status: PASSED` with `gate_k_gt_one_solved: true`. |
| 2 | Recovery selection is driven by oracle regret or value gap rather than imitation accuracy alone. | VERIFIED | `objective_mode` is `oracle_regret`; `solve_library()` objective coefficients use `best - value` oracle regret on action-choice variables, while `action_agreement` is only reported in run/results payloads. Public `objective_value_with_penalties` equals `realized_total_regret + penalty_breakdown.total_penalty` for all solved artifact runs; no mismatches found. |
| 3 | Recovered policies expose program-size, neighbor-atom, and dual-price-atom tradeoffs. | VERIFIED | CLI exposes total, neighbor, dual, placebo budgets and penalties; `atom_indices_by_metadata()` deduplicates category indices via sets; all 15 solved JSON runs and all CSV rows include `program_complexity`, category counts, max category budgets, and `penalty_breakdown`. |
| 4 | Atom library covers local pressure, downstream capacity/slack, raw neighbor queues, pressure/backpressure, dual sensitivity, and random/permuted dual placebo families. | VERIFIED | `ATOM_REGISTRY` covers families `local`, `capacity`, `raw_neighbor`, `pressure`, `dual`, and `placebo`; `dual_sensitivity` is `uses_dual: true, is_placebo: false`, while `random_price` is `family: placebo, uses_dual: true, is_placebo: true`. `full_symbolic` includes the registry atoms. |
| 5 | Each recovery run emits auditable rule text plus selected atoms, solve time, oracle regret, action agreement, program length, neighbor count, and dual atom count. | VERIFIED | JSON has 15 solved runs with all required run fields; CSV has 15 run rows with selected atoms, counts, penalties, regret metrics, agreement, solve time, and `rule_text_path`; rule text contains `choose movement m maximizing score(m)` and per-run selected atom sections. |

**Score:** 5/5 truths verified

## Requirement Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| RECV-01: K-atom sparse symbolic recovery beyond one-atom pilots. | SATISFIED | K>1 solve path exists in code and artifacts: `gate_k_gt_one_solved: true`, 7 solved K>1 runs. Diagnostic `gate_multi_atom_program_observed: false` is correctly recorded and is not a blocker because the requirement demands K>1 solve capacity, not that this fixture select more than one atom. |
| RECV-02: Objective optimizes oracle regret or value gap, not imitation accuracy alone. | SATISFIED | `objective_mode: oracle_regret`; action agreement is diagnostic only. Public objective/value gap fields are realized rule regret plus penalties, with solver optimistic tie-selected regret preserved separately as diagnostics. |
| RECV-03: Explicit penalties or constraints for program size, neighbor atom count, and dual-price atom count. | SATISFIED | Total size, neighbor, genuine dual, and placebo budgets/penalties are present in code and output. Category indices are deduped before count/penalty application; recomputation from selected metadata matched all artifact counts. |
| RECV-04: Required atom families including placebo. | SATISFIED | Registry includes local, capacity, raw_neighbor, pressure, dual, and placebo families. Placebo `random_price` is reported separately from genuine `dual_sensitivity`. |
| RECV-05: Auditable outputs include program/rules and required metrics. | SATISFIED | JSON, CSV, and rule text artifacts exist and contain required metrics: selected atoms, solve time, realized regret, action agreement, program length, neighbor count, dual count, placebo count, and rule text path/content. |

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `/home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py` | Sparse recovery implementation with atom metadata, K-atom MILP, regret-first objective, budgets/penalties, and JSON/CSV/TXT writers. | VERIFIED | Substantive implementation: `ATOM_REGISTRY`, `LIBRARIES`, `solve_library()`, `render_rule_text()`, CSV writer, schema/output gates, and CLI. Wired by quick validation command and artifact generation. |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block2_sparse_recovery.json` | Main schema-gated Phase 2 recovery artifact. | VERIFIED | `status: PASSED`; gates for schema, regret-first objective, required families, outputs, Phase 3 deferral, and K>1 solve are true. |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block2_sparse_recovery.csv` | Run-level comparison table. | VERIFIED | 15 data rows, required columns present, one row per solved run, includes `rule_text_path`. |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block2_sparse_recovery_rules.txt` | Human-readable symbolic rule text. | VERIFIED | Contains per-run counts, regret/action diagnostics, selected atoms, and `score(m)` rule text. |

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `run_sparse_recovery.py` | JSON artifact | `out_path.write_text(json.dumps(payload, ...))` plus schema gates | WIRED | Independent quick validation produced `/tmp/phase2_verify_sparse_recovery.json` with `status: PASSED`. |
| `run_sparse_recovery.py` | CSV artifact | `csv.DictWriter` rows from solved runs | WIRED | CSV columns match RECV-05 metrics and row count matches solved run count. |
| `run_sparse_recovery.py` | Rule text artifact | `render_rule_text()` and `render_rules_file()` | WIRED | Rule text cross-references solved runs and states audit-only Phase 2 scope. |
| `run_sparse_recovery.py` | Phase 3 claim boundary | `note` and `phase3_candidate_diagnostics` | WIRED | Top-level Phase 3 comparison gates are absent; diagnostics are non-gating and note defers dual-vs-pressure empirical claim routing to Phase 3. |

## Data-Flow Trace

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `scripts/run_sparse_recovery.py` | `examples` / atom features | `load_examples()` reads targeted states, `scenario_from_sample()`, `summarize_scenario()`, `build_example()` | Yes | FLOWING — quick validation loaded 16 examples and generated solved runs. |
| `block2_sparse_recovery.json` | `runs`, `summary`, `best_by_library` | MILP solve results from `solve_library()` | Yes | FLOWING — 15 solved runs with per-example results. |
| `block2_sparse_recovery.csv` | CSV rows | `csv_rows_for_runs()` over `runs` | Yes | FLOWING — 15 rows match generated run metrics. |
| `block2_sparse_recovery_rules.txt` | Rule text | `render_rule_text()` over selected atoms/weights/counts | Yes | FLOWING — selected atoms and weights appear in rule sections. |

## Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Python syntax is valid. | `python3 -m py_compile /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py` | Exit code 0 | PASS |
| Quick Phase 2 validation command produces complete artifacts. | `python3 scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json --budgets 1 2 3 --out /tmp/phase2_verify_sparse_recovery.json --csv-out /tmp/phase2_verify_sparse_recovery.csv --rules-out /tmp/phase2_verify_sparse_recovery_rules.txt` | Exit code 0; stdout reported `status: PASSED`, `num_examples: 16`; post-checks confirmed schema/output/Phase 3/K>1 gates. | PASS |
| Public objective fields equal realized regret plus penalties. | JSON inspection over all solved runs | 0 mismatches | PASS |
| Category counts are metadata-derived and deduped. | Recomputed neighbor/dual/placebo counts from `selected_atom_metadata` | 0 mismatches | PASS |

## Probe Execution

No `scripts/*/tests/probe-*.sh` probe was declared for this phase. Probe execution skipped; script-based quick validation was run instead.

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `/home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py` | N/A | No `TBD`, `FIXME`, `XXX`, placeholder, or console-only implementation patterns found. | Info | None |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block2_sparse_recovery.json` | N/A | No blocking anti-patterns found. | Info | None |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block2_sparse_recovery.csv` | N/A | No blocking anti-patterns found. | Info | None |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block2_sparse_recovery_rules.txt` | N/A | No blocking anti-patterns found. | Info | None |

## Human Verification Required

None. Phase 2 deliverables are script/artifact based and were verified programmatically. No visual, real-time, or external-service behavior is claimed by this phase.

## Residual Warnings / Diagnostics

- `gate_multi_atom_program_observed` is currently `false`: K>1 budgets solve, but the current targeted fixture selects only one atom in the solved programs. This is a useful diagnostic for Phase 3/expanded fixtures, not a Phase 2 blocker, because RECV-01 requires K>1 sparse recovery capability and solved K>1 runs, not selected multi-atom programs on this specific fixture.
- Phase 3 empirical claim remains deferred by design. `phase3_candidate_diagnostics` is non-gating, and the artifact note states that dual-vs-pressure empirical claim routing belongs to Phase 3.

## Gaps Summary

No blocking gaps found. Phase 2 satisfies ROADMAP Phase 2 success criteria and RECV-01 through RECV-05.

---

_Verified: 2026-05-22T18:15:36Z_
_Verifier: Claude (gsd-verifier)_
