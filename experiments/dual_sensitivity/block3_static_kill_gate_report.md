# Phase 3 Static Kill-Gate Route Report

## Route Decision

- **Route decision:** `pressure-equivalent`
- **Route confidence:** `MEDIUM`
- **Status:** `PASSED`
- **Experiment:** `block3_static_pressure_failure_kill_gate`

This is a static sample-relative, pre-closed-loop route decision. It does not claim closed-loop results, travel-time gains, throughput gains, deployable traffic-control performance, or universal dominance over max-pressure/backpressure.

## Route Alias Mapping

| JSON route | Human-readable meaning | Downstream framing |
|---|---|---|
| `dual-improves-pressure` | Static binding-regime evidence favors dual over pressure. | Strong mainline candidate: test scarcity-aware generalized pressure in Phase 4. |
| `pressure-equivalent` | dual-recovers/ties pressure on static oracle-regret evidence. | Generalized-pressure symbolic recovery framing; no dominance claim. |
| `diagnostic` | dual-underperforms, unsupported regimes dominate, or evidence is too weak for a positive route. | Diagnostic/limitations framing. |

## Route Rationale

Dual and pressure have tie-equivalent static oracle regret across solved regimes.

## Static-Only Scope and Claim Caveats

- Phase 3 uses static/sample-relative one-step recovery metrics only.
- Phase 3 is pre-closed-loop; closed-loop SUMO experiments are Phase 4 work.
- The report documents claim routing before Phase 4 interpretation and does not treat static oracle regret as deployable control evidence.
- Route is based on static/sample-relative one-step recovery metrics only; closed-loop claims are deferred.

## Sample Sufficiency

- **Valid converted examples:** 1200
- **Target valid examples:** 1000
- **Sample target met:** yes
- **Preliminary regimes:** None
- **Raw samples by regime:** {"corridor_bottleneck_proxy": 200, "demand_shift_proxy": 200, "incident_capacity_drop": 200, "slack": 200, "storage_binding": 200, "supply_binding_proxy": 200}
- **Valid examples by regime:** {"corridor_bottleneck_proxy": 200, "demand_shift_proxy": 200, "incident_capacity_drop": 200, "slack": 200, "storage_binding": 200, "supply_binding_proxy": 200}

## Per-Regime Metrics

| Regime | Examples | Aligned | Disagreement | Dual win | Pressure win | Tie | Dual mean regret | Pressure mean regret | Δ regret pressure-dual | Dual worst | Pressure worst | Selected dual atoms | Selected pressure atoms | Scope |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| corridor_bottleneck_proxy | 200 | 200 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | dual_sensitivity | pressure_backpressure | static_sample_relative |
| demand_shift_proxy | 200 | 200 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | dual_sensitivity | pressure_backpressure | static_sample_relative |
| incident_capacity_drop | 200 | 200 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | dual_sensitivity | pressure_backpressure | static_sample_relative |
| slack | 200 | 200 | 0 | 0 | 0 | 1 | 7.10543e-13 | 7.10543e-13 | 0 | 2.84217e-11 | 2.84217e-11 | dual_sensitivity | pressure_backpressure | static_sample_relative |
| storage_binding | 200 | 200 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | dual_sensitivity | pressure_backpressure | static_sample_relative |
| supply_binding_proxy | 200 | 200 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | dual_sensitivity | pressure_backpressure | static_sample_relative |

## Unsupported / Proxy Regime Limitations

- supply_binding_proxy: proxy - Proxy only: current sample-to-scenario conversion has no explicit per-movement supply constraint field; encoded as high downstream occupancy.
- corridor_bottleneck_proxy: proxy - Proxy only: current static schema has no corridor-level capacity constraint; encoded as approach/corridor queue concentration.
- incident_capacity_drop: supported_synthetic - Capacity of downstream edge C32S3 reduced by factor 0.35 as an incident proxy.
- demand_shift_proxy: proxy - Queue-pattern proxy for demand shift with factor 0.75; no explicit demand field is consumed downstream.
- Route is based on static/sample-relative one-step recovery metrics only; closed-loop claims are deferred.

## Artifact Links

- Gate JSON: `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.json`
- CSV metrics: `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.csv`
- Recovered rules: `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_rules.txt`
- Rendered report: `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_report.md`

## Phase 4 Implications / Priorities

- Route Phase 4 toward generalized-pressure symbolic recovery: compactness, traceability, and equivalence to pressure are the main static lessons.
- Prioritize honest pressure and capacity-aware pressure baselines, because the static evidence does not separate dual from pressure on oracle regret.
- Design at least one closed-loop failure-mode scenario to check whether dynamic effects create separation absent from this static sample.
