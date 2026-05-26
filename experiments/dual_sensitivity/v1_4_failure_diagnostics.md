# v1.4 Failure Diagnostics

Status: `PASSED`
Source Gate C status: `INCONCLUSIVE`
Source Phase 11 status: `FAILED`

## Classification Summary

| Classification | Count |
|---|---:|
| bounded_harm | 48 |
| inconclusive | 221 |
| non_worsening | 10 |

Strict-positive signals: 4

## Failure Drivers

| Driver | Level | Evidence |
|---|---|---|
| controller_action_weakness | high | 48 bounded-harm metric comparisons versus 10 non-worsening comparisons. |
| objective_mismatch | medium | Bounded harm appears in travel-time/delay metrics, so objective tuning remains a plausible route. |
| insufficient_binding_activation | medium | Finite-storage decisions differed from pressure in 9.833% of audited TLS decisions; nonzero components: {'pressure': 3338, 'switching': 745}. |
| scenario_design | medium | 221 metric comparisons were inconclusive, so scenario or metric sensitivity remains unresolved. |
| baseline_parity | medium | Only 4 strict-positive signals were present against strong max-pressure-style comparators. |

## Workstreams

| Workstream | Status | Claim Ready | Artifact |
|---|---|---|---|
| v1-4-score-controller | ready_for_pilot | False | `experiments/dual_sensitivity/v1_4_workstreams/v1-4-score-controller-pilot.json` |
| v1-4-objective-weights | ready_for_pilot | False | `experiments/dual_sensitivity/v1_4_workstreams/v1-4-objective-weights-pilot.json` |
| v1-4-scenario-diagnostics | ready_for_pilot | False | `experiments/dual_sensitivity/v1_4_workstreams/v1-4-scenario-diagnostics-pilot.json` |
| v1-4-symbolic-policy | ready_for_pilot | False | `experiments/dual_sensitivity/v1_4_workstreams/v1-4-symbolic-policy-pilot.json` |

## Claim Boundary

v1.3 failed Gate C; diagnostics and v1.4 pilots cannot be imported as final superiority evidence.
