---
phase: 11-long-horizon-paired-seed-evidence
reviewed: 2026-05-24T11:18:24Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - scripts/run_closed_loop_sumo.py
  - scripts/run_phase11_paired_evidence.py
  - scripts/run_gate_c_paired_evidence.py
  - tests/test_phase11_paired_evidence.py
findings:
  critical: 5
  warning: 4
  info: 1
  total: 10
status: issues_found
---

# Phase 11: Code Review Report

**Reviewed:** 2026-05-24T11:18:24Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Reviewed the Phase 11 SUMO runner, paired-evidence artifact builder, standalone Gate C checker, and Phase 11 tests. The implementation has several artifact-integrity and gate-discipline defects that can allow insufficient, stale, or upstream-failed evidence to be emitted as passing Gate C evidence. The highest-risk issues are strict mode returning success for `INCONCLUSIVE`, single-seed evidence being able to pass the statistical rule, stale incident state being recorded as final finite-storage evidence, and long-horizon demand scaling not extending route demand beyond the base 3600-second route file.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: BLOCKER — Strict Gate C mode exits successfully for inconclusive artifacts

**File:** `scripts/run_gate_c_paired_evidence.py:188-189`

**Issue:** `--strict` exits nonzero only when `payload["status"] == "FAILED"`. Missing-execution, pilot, dry-run, and otherwise insufficient artifacts are intentionally classified as `INCONCLUSIVE`, but strict mode still returns process success for those non-evidence artifacts. Any automation that treats `--strict` exit code as the gate result can proceed with no completed Gate C evidence.

**Fix:** Fail strict mode unless the recomputed status is `PASSED`.

```python
if args.strict and payload["status"] != "PASSED":
    raise SystemExit(1)
```

### CR-02: BLOCKER — Gate C can pass with only one paired seed

**File:** `scripts/run_phase11_paired_evidence.py:468-471`, `scripts/run_phase11_paired_evidence.py:727-781`

**Issue:** `_bootstrap_ci()` returns a degenerate positive interval for a single positive difference, and `evaluate_gate_c()` never enforces a minimum paired-seed count. A handcrafted or partial artifact with exactly one proposed/comparator pair per scenario can therefore satisfy `strict_positive_signal` and return `PASSED`, despite no confidence interval being constructible and despite the main profile requiring paired-seed statistical evidence.

**Fix:** Enforce the predeclared minimum seed count before evaluating the primary-metric rule, and classify insufficient seed counts as `FAILED` or `INCONCLUSIVE`.

```python
MIN_GATE_C_PAIRED_SEEDS = 2
# inside evaluate_gate_c, before evaluate_gate_c_primary_metric_rule(...)
for scenario in BINDING_EVIDENCE_SCENARIOS:
    for multiplier in demand_multipliers:
        grouped = _rows_by_controller_seed(completed, scenario, multiplier)
        required_seed_sets = [set(grouped.get(ctrl, {})) for ctrl in (PROPOSED_CONTROLLER, *REQUIRED_GATE_C_COMPARATORS)]
        if any(len(seed_set) < MIN_GATE_C_PAIRED_SEEDS for seed_set in required_seed_sets):
            reasons.append(f"{scenario}/{multiplier} has fewer than {MIN_GATE_C_PAIRED_SEEDS} paired seeds")
```

### CR-03: BLOCKER — Upstream failed Phase 11 artifacts can be re-issued as passed Gate C artifacts

**File:** `scripts/run_gate_c_paired_evidence.py:129-134`

**Issue:** `build_gate_payload()` bases the output status on recomputed rows, profile eligibility, and demand-provenance shape, but it ignores `input_payload["status"]`. If the source Phase 11 artifact is marked `FAILED` or `INCONCLUSIVE` for an upstream integrity reason while still containing rows that recompute as passing, the standalone checker can emit `"status": "PASSED"`. This breaks artifact provenance: a failed source artifact must not be upgraded by a downstream gate checker.

**Fix:** Treat any non-`PASSED` input status as fail-closed unless the checker is explicitly producing an inconclusive diagnostic artifact.

```python
input_status = str(input_payload.get("status", "")).upper()
if input_status != "PASSED":
    combined_reasons.append(f"input artifact status is {input_status or 'missing'}, not PASSED")
    status = "INCONCLUSIVE"
elif gate_c["status"] == "PASSED" and not profile_eligibility["eligible"]:
    status = "INCONCLUSIVE"
elif demand_reasons and profile_eligibility["eligible"]:
    status = "FAILED"
else:
    status = gate_c["status"]
```

### CR-04: BLOCKER — Final finite-storage state records stale incident/failure mode after the incident has ended

**File:** `scripts/run_closed_loop_sumo.py:667-670`, `scripts/run_closed_loop_sumo.py:765-773`, `scripts/run_closed_loop_sumo.py:785-790`

**Issue:** `failure_mode_mechanism` is set when `apply_failure_mode()` returns a mechanism, but it is never cleared after `apply_failure_mode()` restores the edge speed at `warmup + 120`. The final row then builds `finite_storage_state` with `incident_edge=target_edge` and `capacity_drop_factor=0.35` whenever the incident was active at any earlier time, even if it ended thousands of steps before the final snapshot. Gate C validators only check that `finite_storage_state` exists, so stale incident state can be used as binding-regime evidence.

**Fix:** Track active incident state separately from historical mechanism metadata, clear it when the speed is restored, and use the active flag when building the final finite-storage state.

```python
failure_mode_active = False
...
mechanism = apply_failure_mode(step, warmup, target_edge, original_speed)
if mechanism:
    failure_mode_mechanism = mechanism
    failure_mode_active = True
elif step >= warmup + 120:
    failure_mode_active = False
...
"finite_storage_state": build_completed_finite_storage_state(
    latest_queues,
    capacities,
    current_phase=latest_current_phase,
    time_since_switch=latest_time_since_switch,
    incident_edge=target_edge if failure_mode_active else None,
    capacity_drop_factor=0.35 if failure_mode_active else None,
)
```

### CR-05: BLOCKER — Long-horizon demand artifacts stop generating base route demand at the original route-file end time

**File:** `scripts/run_phase11_paired_evidence.py:309-325`

**Issue:** `generate_scaled_route_and_sumocfg()` sets the generated SUMO config `time/end` to the requested `steps`, but it does not extend `<flow begin/end>` or `<flow until>` attributes in the route file. For any long-horizon run with `steps > 3600`, the generated config runs longer while the arterial base flows still end at 3600 seconds. The artifact can report a long-horizon demand multiplier even though later simulation time has no route-file demand, weakening the intended stress regime and corrupting demand provenance.

**Fix:** Either fail closed when route flows do not cover the requested horizon, or extend eligible flow end times during generation and recompute provenance from the modified route.

```python
for flow in route_root.findall("flow"):
    end_value = float(flow.get("end", flow.get("until", "0")))
    if end_value and end_value < float(steps):
        flow.set("end", str(int(steps)))
    _scale_flow(flow, float(demand_multiplier))
```

## Warnings

### WR-01: WARNING — Demand provenance accepts fabricated paths and inconsistent scaled totals

**File:** `scripts/run_gate_c_paired_evidence.py:82-108`, `scripts/run_phase11_paired_evidence.py:663-679`

**Issue:** Gate C provenance checks require field presence but do not verify that generated route/config files exist or that `scaled_demand_total` matches `base_demand_total * demand_multiplier`. The tests currently pass synthetic non-existent files as valid provenance, so a fabricated artifact can satisfy `valid_actual_behavior` without proving that SUMO used the scaled demand inputs.

**Fix:** In the standalone checker, validate per-row provenance numerically and, when paths are local to the artifact environment, verify file existence. At minimum, reject mismatched totals.

### WR-02: WARNING — `actual_seed_count` is computed from the spec, not from executed rows

**File:** `scripts/run_phase11_paired_evidence.py:879-881`

**Issue:** `build_payload()` sets both `actual_seed_count` and `requested_seed_count` from `spec`. A runtime-guarded or partially failed main artifact can report all requested seeds as “actual” even when `actual_row_count` is zero. This does not currently make the status pass, but it makes the artifact internally inconsistent and can mislead downstream summaries.

**Fix:** Compute actual seed count from completed rows and requested seed count from the spec.

```python
actual_seeds = sorted({int(row["seed"]) for row in executed_rows})
requested_seeds = sorted({int(row["seed"]) for row in spec})
"actual_seed_count": len(actual_seeds),
"requested_seed_count": len(requested_seeds),
```

### WR-03: WARNING — Holm-Bonferroni adjusted p-values are not monotone adjusted values

**File:** `scripts/run_phase11_paired_evidence.py:563-575`

**Issue:** `_holm_bonferroni()` stores `min((m - rank + 1) * pvalue, 1.0)` independently for each sorted p-value. Holm adjusted p-values require a cumulative maximum over the sorted sequence; otherwise a less significant comparison can receive a smaller adjusted p-value than a more significant one. The gate status does not currently use these values, but the artifact’s statistical-family metadata is incorrect.

**Fix:** Apply the cumulative maximum in sorted order, then map back to original indices.

### WR-04: WARNING — The seed-alignment test contains a tautological filter and can miss broken specs

**File:** `tests/test_phase11_paired_evidence.py:100-102`

**Issue:** The comprehension uses `row["controller"] == row["controller"]`, which is always true. The test therefore collects all controller seeds for each controller key instead of verifying that each required controller has the same seed set. A regression that breaks paired seed alignment can pass this test.

**Fix:** Compare against the controller being inspected, using distinct variable names to avoid shadowing.

```python
by_controller = {}
for controller in {row["controller"] for row in spec if row["scenario_tag"] == scenario and row["demand_multiplier"] == multiplier}:
    by_controller[controller] = {
        item["seed"]
        for item in spec
        if item["scenario_tag"] == scenario
        and item["demand_multiplier"] == multiplier
        and item["controller"] == controller
    }
```

## Info

### IN-01: INFO — Unused test module variable

**File:** `tests/test_phase11_paired_evidence.py:131`

**Issue:** `_defused_tmp_error` is assigned but never read. This is dead test code and can confuse future readers about an expected temporary-file failure path.

**Fix:** Remove the unused assignment.

---

_Reviewed: 2026-05-24T11:18:24Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
