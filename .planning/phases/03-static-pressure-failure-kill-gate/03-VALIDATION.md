# Phase 3: Static Pressure-Failure Kill Gate - Validation

**Created:** 2026-05-23
**Purpose:** Define script-based acceptance gates for KILL-01 through KILL-05 before Phase 3 is marked complete.

## Validation Strategy

Phase 3 validation checks static benchmark routing only. It must verify that dual-vs-pressure metrics are computed per regime, sample sufficiency is explicit, and route language stays static/sample-relative. It must not require or claim closed-loop SUMO performance.

## Quick Gate Command

```bash
PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 scripts/run_static_kill_gate.py \
  --states experiments/dual_sensitivity/targeted_bottleneck_states.json \
  --tls C3 \
  --max-samples 16 \
  --default-regime storage_binding_proxy \
  --target-total-states 1000 \
  --out /tmp/block3_static_kill_gate.json \
  --csv-out /tmp/block3_static_kill_gate.csv \
  --rules-out /tmp/block3_static_kill_gate_rules.txt \
  --report-out /tmp/block3_static_kill_gate_report.md
```

## Full Gate Command

```bash
PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 scripts/generate_static_regime_states.py \
  --target-per-regime 200 \
  --out experiments/dual_sensitivity/block3_regime_states.json
PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 scripts/run_static_kill_gate.py \
  --states experiments/dual_sensitivity/block3_regime_states.json \
  --tls C3 \
  --target-total-states 1000 \
  --out experiments/dual_sensitivity/block3_static_kill_gate.json \
  --csv-out experiments/dual_sensitivity/block3_static_kill_gate.csv \
  --rules-out experiments/dual_sensitivity/block3_static_kill_gate_rules.txt \
  --report-out experiments/dual_sensitivity/block3_static_kill_gate_report.md
```

## Requirement Gates

| Requirement | Gate | Pass Condition |
|---|---|---|
| KILL-01 | Regime coverage | Static artifacts include all requested regimes as supported, proxy, or unsupported-by-current-model with explicit rationale. |
| KILL-02 | Per-regime metrics | Each supported/proxy regime reports dual-vs-pressure disagreement rate, dual win rate, pressure win rate, tie rate, mean oracle regret, worst-case regret, and recovered rules. |
| KILL-03 | Sample sufficiency | JSON records `target_total_states`, `num_examples_total`, `sample_target_met`, `preliminary_regimes`, and does not hide count shortfalls. |
| KILL-04 | Route classification | JSON includes `route_decision` as `dual-improves-pressure`, `pressure-equivalent`, or `diagnostic`, derived from static metrics and caveats. |
| KILL-05 | Route report | Markdown report exists, states the route decision/rationale/caveats, and explicitly limits claims to static sample-relative evidence. |

## Phase Completion Criteria

Phase 3 passes when `block3_static_kill_gate.json`, `.csv`, `_rules.txt`, and `_report.md` are generated; schema/metric/route gates pass; sample insufficiency is explicit if the 1k target is not met; and no closed-loop or universal dominance claim is made.
