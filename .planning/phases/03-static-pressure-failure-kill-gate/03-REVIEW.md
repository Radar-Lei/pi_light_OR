---
phase: 03-static-pressure-failure-kill-gate
reviewed: 2026-05-22T19:35:50Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py
  - /home/samuel/projects/pi_light_OR/scripts/render_static_kill_gate_report.py
  - /home/samuel/projects/pi_light_OR/tests/test_run_static_kill_gate.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 03: Code Review Re-Review Report

**Reviewed:** 2026-05-22T19:35:50Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** clean

## Summary

Re-reviewed the Phase 03 static pressure-failure kill-gate fixes in the runner, renderer, and targeted tests. The previously reported CR-01, WR-01, and WR-02 are fixed. The regenerated Block 3 gate artifact still reports `route_decision: pressure-equivalent`, `sample_target_met: true`, and no preliminary regimes for the full fixture.

Verification performed:

- `python3 /home/samuel/projects/pi_light_OR/tests/test_run_static_kill_gate.py` passed.
- Inspected `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.json`: `num_examples_total` is 1200, all six requested regimes have 200 raw and 200 valid examples, `preliminary_regimes` is empty, `sample_target_met` is true, and `route_decision` is `pressure-equivalent`.
- Exercised `render_metric_table()` with pipe and newline characters in regime labels, atom names, and claim scope; cells are escaped/normalized.

## Narrative Findings (AI reviewer)

All reviewed files meet the current Phase 03 quality requirements for the requested fixes. No remaining Critical, Warning, or Info findings were identified.

## Resolved Previous Findings

### CR-01: Sample sufficiency is checked only globally, allowing under-covered regimes to be promoted as non-preliminary

**Status:** Fixed.

`/home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py` now tracks raw requested regimes through `raw_samples_by_regime`, converted counts through `valid_examples_by_regime`, and solved primary-library evidence through `runs_by_regime`. `find_preliminary_regimes()` marks any requested regime preliminary if it has fewer than `min_regime_count` valid converted examples or lacks a solved dual/pressure run. The top-level `sample_target_met` is true only when the global target is met and `preliminary_regimes` is empty, and `decide_route()` forces `diagnostic` when preliminary regimes are present. The regression test `test_missing_requested_regime_routes_to_diagnostic()` covers the missing-regime route downgrade.

### WR-01: Malformed legacy or generated samples can crash during scenario conversion instead of producing a controlled validation error or skip

**Status:** Fixed.

`/home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py` now validates `time`, numeric queue/vehicle/capacity mappings, TLS movement list shape, two-string movement tuples, and referenced queue/capacity links before conversion. `examples_for_samples()` wraps conversion and summary construction errors and re-raises a controlled `ValueError` that includes the sample source label. This satisfies the requested controlled malformed-sample validation/conversion behavior.

### WR-02: Markdown table rendering is not escaped, so regime labels or atom names containing pipes/newlines can corrupt deterministic reports

**Status:** Fixed.

`/home/samuel/projects/pi_light_OR/scripts/render_static_kill_gate_report.py` now uses `md_cell()` for Markdown table values, escaping backslashes and pipes and normalizing carriage returns/newlines. The metric table uses this helper for regime labels, selected atom lists, claim scope, and numeric/string cells, preserving deterministic table structure for malformed or legacy payload text.

---

_Reviewed: 2026-05-22T19:35:50Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
