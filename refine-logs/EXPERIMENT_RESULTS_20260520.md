# Initial Experiment Results — Block 0/1 Pilot

**Date**: 2026-05-20  
**Plan**: `refine-logs/EXPERIMENT_PLAN.md`  
**Scope**: early validation only; no broad SUMO closed-loop experiments yet.

## Implemented Artifacts

- `scripts/run_dual_sanity.py`
- `scripts/run_offline_recovery_pilot.py`
- `experiments/dual_sensitivity/block0_dual_sanity.json`
- `experiments/dual_sensitivity/block1_offline_recovery_pilot.json`

## Block 0 — Dual Sanity

**Status**: PASSED

What was tested:

1. Continuous one-step store-and-forward LP proxy.
2. Queue-conservation duals and downstream storage duals.
3. Movement marginal values from upstream/downstream dual differences.
4. Finite-difference checks by forcing a small amount of service on each movement.
5. Pressure special-case ranking when storage constraints are nonbinding.

Scenarios:

| Scenario | Dual vs finite-difference | Pressure special case | Notes |
|---|---|---|---|
| toy_nonbinding | PASS | PASS | Dual values equal pressure-like marginal service values. |
| toy_storage_binding | PASS | PASS | Service into high downstream queue is penalized. |
| single_intersection_proxy | PASS | PASS | Movement ranking matches pressure ranking. |
| arterial_bottleneck_proxy | PASS | PASS | Binding downstream storage produces extra scarcity term; dual value differs from simple pressure magnitude. |

Key result:

- Dual movement values match finite-difference marginal service values in all proxy scenarios.
- In nonbinding-storage cases, dual ranking matches pressure/backpressure ranking.
- In the arterial bottleneck proxy, the downstream bottleneck movement gets a strong negative dual value due to downstream scarcity.

Important caveat:

- This is a proxy LP sanity check, not yet a full SUMO-derived state pipeline or AMPL formulation.
- The storage-binding example currently validates ranking and scarcity behavior; the next step should formalize the exact primal/dual derivation and, if desired, port to AMPL/HiGHS using Obsidian materials/license.

## Block 1 — Equal-Complexity Offline Recovery Pilot

**Status**: PASSED AS SCAFFOLD

What was tested:

- One-atom equal-complexity policy selection on Block 0 proxy states.
- Variants: local-only, raw-neighbor, all-neighbor, random-price, dual-sensitivity.
- Metric: oracle regret using finite-difference movement values as oracle.

Result:

- Dual-sensitivity tied the best oracle-regret result in all proxy scenarios.
- Random/permuted price failed in all scenarios.
- Local/raw/all also tied in these proxy states because the current scenarios are still pressure-aligned.

Important caveat:

- This does **not** prove the main Block 1 claim yet.
- It is only a scaffold confirming that equal-complexity comparison, oracle-regret calculation, and JSON output are wired.
- Full Block 1 still needs sampled states where raw/all/local features diverge from dual scarcity features, plus a real sparse MIP recovery objective.

## Gate Status

- Gate A — Dual validity: **PASSED for proxy LP sanity**.
- Gate B — Offline recovery: **SCAFFOLD PASSED, full gate still PENDING**.
- Gate C/D/E: not started.

## Next Step

Recommended next implementation step:

1. Replace proxy scenarios with sampled states from SUMO networks.
2. Port the continuous relaxation to AMPL/HiGHS if needed, using Obsidian SUMO/AMPL notes and license.
3. Implement real sparse MIP recovery over OR-mapped atoms.
4. Create states where raw-neighbor/all-neighbor/local baselines diverge from dual-scarcity features, especially downstream bottleneck and spillback cases.
