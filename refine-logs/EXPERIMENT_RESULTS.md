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

## SUMO Sampled-State and Targeted Bottleneck Extension

Additional artifacts:

- `scripts/sample_sumo_states.py`
- `scripts/generate_targeted_bottleneck_states.py`
- `scripts/run_sumo_sampled_recovery.py`
- `experiments/dual_sensitivity/arterial_sampled_states.json`
- `experiments/dual_sensitivity/targeted_bottleneck_states.json`
- `experiments/dual_sensitivity/block1_sumo_sampled_recovery.json`
- `experiments/dual_sensitivity/block1_targeted_bottleneck_recovery.json`

What was added:

1. Used TraCI on the existing 5-intersection arterial network.
2. Sampled 10 passive states from `networks/arterial/arterial.sumocfg`.
3. Parsed SUMO `net.xml` connections to infer TLS movement candidates.
4. Generated 16 targeted bottleneck/spillback states using the same arterial topology.
5. Converted sampled and targeted edge queues/capacities into one-step LP scenarios.
6. Re-ran equal-complexity one-atom recovery with true raw atoms: upstream queue, downstream queue, upstream+downstream, random price, and dual sensitivity. Pressure/backpressure is reported only as a strong diagnostic baseline.

Passive SUMO sampled-state result:

- **Status**: PASSED AS SANITY CHECK
- After aligning dual values and finite differences at the same zero-service marginal point, passive SUMO states pass all sanity layers:
  - top-choice sanity: 8/8
  - exact full-rank dual-vs-finite-difference check: 8/8
  - tie-aware pairwise full-rank check: 8/8, 0 violations
- Passive fixed-time samples are useful dual-validity sanity checks, but are not by themselves sufficient evidence for the bottleneck/spillback recovery advantage.

Targeted bottleneck-state result:

- **Status**: PASSED AS TARGETED BLOCK 1 EVIDENCE
- Dual-sensitivity achieved zero aggregate oracle regret across 16 targeted states.
- Targeted states also pass all sanity layers: top-choice 16/16, exact full-rank 16/16, tie-aware full-rank 16/16 with 0 violations.
- Equal-complexity raw atoms failed under the same one-atom budget:
  - local upstream queue: total regret 405.3824, mean 25.3364
  - raw downstream queue: total regret 1857.7696, mean 116.1106
  - upstream+downstream raw atom: total regret 1267.0656, mean 79.1916
  - random price: total regret 1057.3856, mean 66.0866
- Pressure/backpressure diagnostic also achieved zero regret, confirming that the constructed cases are traffic-control meaningful rather than arbitrary labels.

Sparse MILP recovery result:

- **Status**: PASSED
- Implemented `scripts/run_sparse_recovery.py` with a SciPy/HiGHS MILP backend.
- The recovery objective selects sparse atom subsets under a bounded program budget and reports external deterministic realized oracle regret.
- Targeted-only dataset: 16 examples.
  - dual-sensitivity, budget 1: selected `dual_sensitivity`, total regret 0.0, action agreement 1.0
  - dual+raw library, best recovered program: selected `dual_sensitivity`, total regret 0.0, action agreement 1.0
  - local/raw/all raw libraries: best recovered atom `upstream_queue`, total regret 405.3824, action agreement 0.75
  - random price: total regret 761.3792, action agreement 0.125
- Combined passive+targeted dataset: 26 examples.
  - dual-sensitivity, budget 1: selected `dual_sensitivity`, total regret 0.0, action agreement 1.0
  - dual+raw library, best recovered program: selected `dual_sensitivity`, total regret 0.0, action agreement 1.0
  - local/raw/all raw libraries: best recovered atom `upstream_queue`, total regret 469.3824, action agreement 0.538
  - random price: total regret 787.3792, action agreement 0.231
- Pressure/backpressure diagnostic also achieved zero regret, confirming consistency with the pressure special case rather than arbitrary labels.

Interpretation:

- The SUMO/topology state pipeline is working.
- Gate B now has positive sparse-recovery evidence: the MILP recovery procedure selects dual-sensitivity atoms and achieves lower realized oracle regret than raw/local/random atoms at equal or lower complexity.
- This remains an offline recovery gate; the next step is closed-loop SUMO validation on arterial bottleneck/platoon scenarios.

## Theory and Atom Taxonomy Freeze

Additional artifact:

- `refine-logs/THEORY_AND_ATOMS.md`

What was frozen:

1. Minimal continuous one-step store-and-forward relaxation with queue conservation, downstream storage, green budget, service bounds, and overflow slack.
2. Movement marginal-value lemma at the zero-service marginal point: movement value is `lambda_up - lambda_down`, with downstream storage scarcity entering through the downstream link value / storage dual effect.
3. Pressure/backpressure special case: when storage and coupling constraints are nonbinding, dual movement value reduces to `w_up - w_down`, and to ordinary pressure when `w_l = x_l`.
4. OR-mapped atom taxonomy: retained atoms must map to a model state, constraint residual, dual value, or reduced movement value.
5. Claim boundary: Block 0/1 supports dual validity and offline sparse recovery, but not yet closed-loop performance or dominance over max-pressure/C-MP.

Interpretation:

- The formal theory is now drafted sufficiently to support the next closed-loop pilot, though it still needs polishing into paper theorem/proof prose.
- Corridor atoms remain deferred until an explicit corridor/service-balance constraint is added to the relaxation.

## AMPL/SUMO Environment Notes

- SUMO, netconvert, TraCI, and sumolib are installed and usable.
- `amplpy` is not installed in the current Python environment.
- AMPL setup notes are kept outside this public repository. Do not commit license IDs or activation commands.

## Gate Status

- Gate A — Dual validity: **PASSED for proxy LP, passive SUMO, and targeted SUMO; top-choice, exact full-rank, and tie-aware full-rank checks all pass after using a common zero-service marginal point**.
- Gate B — Offline recovery: **PASSED for targeted/combined offline sparse recovery; full claim still needs closed-loop SUMO validation**.
- Gate C/D/E: not started.

## Next Step

Recommended next implementation step:

1. Start Block 3 arterial closed-loop pilot with bottleneck/platoon scenarios.
2. Compare local/raw/random/dual recovered symbolic controllers against max-pressure and fixed/actuated baselines.
3. Keep pressure/backpressure as a strong diagnostic baseline and claim dual value only where it improves sparse symbolic recovery or deployability.
4. Optionally add an AMPL backend later; current sparse recovery is already solved through SciPy/HiGHS and does not require committing AMPL license details.
