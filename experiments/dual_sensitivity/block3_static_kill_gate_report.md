# Phase 3 Static Kill-Gate Report

Route decision: `pressure-equivalent`
Route confidence: `MEDIUM`

This report is static/sample-relative only; closed-loop SUMO performance and travel-time claims are deferred.

## Rationale

Dual and pressure have tie-equivalent static oracle regret across solved regimes.

## Sample Sufficiency

- Valid converted examples: 1200
- Target valid examples: 1000
- Sample target met: True
- Preliminary regimes: None

## Per-Regime Metrics

| Regime | Examples | Disagreement | Dual win | Pressure win | Tie | Δ regret pressure-dual | Scope |
|---|---:|---:|---:|---:|---:|---:|---|
| corridor_bottleneck_proxy | 200 | 0 | 0 | 0 | 1 | 0 | static_sample_relative |
| demand_shift_proxy | 200 | 0 | 0 | 0 | 1 | 0 | static_sample_relative |
| incident_capacity_drop | 200 | 0 | 0 | 0 | 1 | 0 | static_sample_relative |
| slack | 200 | 0 | 0 | 0 | 1 | 0 | static_sample_relative |
| storage_binding | 200 | 0 | 0 | 0 | 1 | 0 | static_sample_relative |
| supply_binding_proxy | 200 | 0 | 0 | 0 | 1 | 0 | static_sample_relative |

## Caveats

- Route is based on static/sample-relative one-step recovery metrics only; closed-loop claims are deferred.

## Artifacts

- JSON: `experiments/dual_sensitivity/block3_static_kill_gate.json`
- CSV: `experiments/dual_sensitivity/block3_static_kill_gate.csv`
- Rules: `experiments/dual_sensitivity/block3_static_kill_gate_rules.txt`
