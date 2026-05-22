# Theory and Claim-Lock Memo

**Date**: 2026-05-22  
**Phase**: 01 — Theoretical Core and Claim Lock  
**Requirements covered in this plan**: THRY-01, THRY-02  
**Primary references**: `.planning/phases/01-theoretical-core-and-claim-lock/01-CONTEXT.md`, `.planning/phases/01-theoretical-core-and-claim-lock/01-RESEARCH.md`, `refine-logs/THEORY_AND_ATOMS.md`, `scripts/run_dual_sanity.py`

## Purpose

This memo locks the model-facing theory for a dual-sensitivity-guided symbolic traffic-control paper. The artifact is a technical memo, not an empirical-results report. Its purpose is to define a continuous capacitated traffic-network relaxation and a movement-level dual-sensitivity decomposition that later sections can use to prove pressure/backpressure special cases, binding-regime scarcity corrections, and finite-dictionary recovery statements.

## Claim-Discipline Guardrails

Allowed within this Phase 1 theory artifact:

- define a store-and-forward / CTM-lite continuous relaxation with queue conservation, movement service, phase compatibility, and storage/supply/capacity constraints;
- interpret LP/KKT shadow prices as movement-level marginal service values;
- state that dual sensitivity is a generalized pressure object that can reduce to pressure under slack or ranking-neutral conditions;
- state that storage, supply, phase/service, or corridor terms enter only when those primal constraints are explicitly modeled.

Not allowed in this memo:

- treating Phase 1 as closed-loop empirical evidence;
- claiming universal improvement over max-pressure or capacity-aware pressure baselines;
- adding ADMM, robust optimization, column generation, bilevel optimization, freight/TR-E pivots, or GPU-heavy MARL to the Phase 1 scope;
- introducing corridor or service-balance dual terms without writing the corresponding primal constraint.

## Notation

| Symbol | Meaning | Implementation alignment |
|---|---|---|
| `L` | Set of directed links or lane groups | `Scenario.links` |
| `M` | Set of permitted movements `m=(i,j)` from upstream link `i` to downstream link `j` | `Scenario.movements` |
| `P` | Set of signal phases or phase-compatible movement groups | implicit green/service feasibility |
| `x_l` | Current queue or occupancy on link `l` | `Scenario.queue` |
| `x_l^+` | Next-step queue or occupancy after service and arrivals | LP `x_slice` variables |
| `d_l` | Exogenous arrival/demand entering link `l` during the decision interval | `Scenario.demand` |
| `u_m` | Continuous service assigned to movement `m` during the interval | LP `u_slice` variables |
| `a_{lm}` | Signed movement-link incidence: `+1` if movement removes flow from `l`, `-1` if it sends flow into `l`, `0` otherwise | queue-balance rows |
| `S_l` | Receiving/storage/supply bound for link `l` | `Scenario.downstream_capacity` |
| `U_m` | Saturation or service upper bound for movement `m` | `Scenario.service_capacity` |
| `g_p` | Green or service resource assigned to phase `p` | represented by green budget / phase feasibility |
| `G` | Total green/service budget over the local decision interval | `Scenario.green_budget` |
| `z_l` | Nonnegative overflow/slack for storage or supply violation | LP `z_slice` variables |
| `w_l` | Queue or occupancy objective weight | `Scenario.queue_weight` |
| `rho_l` | Penalty for storage/supply overflow slack | `Scenario.storage_penalty` |
| `lambda_l` | Equality dual for link `l` queue conservation | `res.eqlin.marginals[l]` |
| `mu_l` | Inequality dual for link `l` storage/supply bound | `res.ineqlin.marginals[1+l]` |

## Modeling Assumptions

1. The local controller observes a short-horizon traffic state containing link queues or occupancies, movement feasibility, storage/supply capacities, and approximate saturation-service bounds.
2. The relaxation is continuous: phase and service choices are relaxed to split-like service variables rather than integer signal programs.
3. Turning and routing are represented at the movement level; a movement consumes upstream queue and contributes to downstream occupancy.
4. Storage and supply constraints are finite when capacity information is present. Soft overflow variables are included where infeasibility would otherwise obscure the marginal-value interpretation.
5. The one-step model is sufficient for local marginal service values. A multi-step CTM-lite extension repeats the same conservation, service, and capacity structure over time.

## THRY-01 — Continuous Capacitated Relaxation

### Definition 1 — Capacitated movement-service relaxation

Let `L` be the set of directed links or lane groups at one controlled neighborhood and `M` the set of feasible turning movements. Each movement `m=(i,j)` removes flow from an upstream link `i` and sends it to a downstream link `j`. For a short decision interval, define the continuous relaxation:

```text
minimize      sum_{l in L} w_l x_l^+ + sum_{l in L} rho_l z_l

subject to    x_l^+ = x_l + d_l - sum_{m in M} a_{lm} u_m
                                                    for all l in L      (queue conservation)

              sum_{m in M_p} u_m <= g_p             for all p in P      (phase compatibility)
              sum_{p in P} g_p <= G                                      (green/service budget)

              0 <= u_m <= U_m                       for all m in M      (movement service bounds)

              x_l^+ <= S_l + z_l                    for all l in L      (storage/supply/capacity)
              x_l^+ >= 0,  z_l >= 0                 for all l in L
              g_p >= 0                              for all p in P
```

The incidence coefficient `a_{lm}` is `+1` when service on movement `m` removes vehicles from link `l`, `-1` when it adds vehicles to link `l`, and `0` otherwise. Equivalently, for movement `m=(i,j)`, the conservation equations include `-u_m` in the upstream next-queue equation and `+u_m` in the downstream next-queue equation after moving all terms to the standard equality form used above.

### Relationship to the implemented sanity LP

The Block 0 validation script `scripts/run_dual_sanity.py` uses the one-step version of this model:

```text
minimize      sum_l w_l x_l^+ + sum_l rho_l z_l
subject to    x_l^+ = x_l + d_l - movement service out of l + movement service into l
              sum_m u_m <= G
              x_l^+ <= S_l + z_l
              0 <= u_m <= U_m
              x_l^+ >= 0, z_l >= 0
```

The script collapses phase compatibility into a single green/service budget for deterministic sanity scenarios. The more general memo form writes phase-compatible movement sets `M_p` and phase resources `g_p` explicitly so that reviewer-facing notation covers signal feasibility. If a later implementation uses phase-specific split variables, the dual terms for those phase/service constraints should be interpreted exactly as the KKT multipliers on the written constraints.

### Optional CTM-lite extension

For a multi-period horizon `t=0,...,T-1`, the same relaxation repeats conservation and storage/supply constraints over time:

```text
x_l(t+1) = x_l(t) + d_l(t) - sum_m a_{lm} u_m(t)
x_l(t+1) <= S_l(t) + z_l(t)
0 <= u_m(t) <= U_m(t)
phase-compatible service constraints for each controlled junction and time t.
```

The present plan only needs the local one-step marginal structure. Later manuscript sections may introduce switching penalties, minimum-green approximations, or corridor/service constraints, but such terms should be written as explicit primal constraints before any corresponding dual-price atom is claimed.

### Proof-ready properties

- The feasible set is a polyhedron whenever `S_l`, `U_m`, `G`, and the phase-service sets are fixed for the decision interval.
- With linear queue and slack penalties, the relaxation is a linear program and admits LP dual/shadow-price sensitivity analysis under the usual feasibility and boundedness conditions.
- Nonnegative overflow variables make finite-capacity stress explicit while preserving feasibility for diagnostic states, provided `rho_l` is chosen as a sufficiently large penalty for storage/supply violation.
- The phase compatibility constraints distinguish physically feasible service from arbitrary movement scoring; only movements compatible with available phases can receive simultaneous service.

### Reviewer-facing interpretation

THRY-01 establishes the mathematical object whose duals are later used as interpretable control signals. Queue conservation gives upstream/downstream movement effects; movement service variables encode controllable signal allocation; phase compatibility and green-service feasibility encode signal constraints; storage/supply/capacity constraints encode finite receiving space and spillback risk. This is a capacitated traffic-network relaxation, not a claim that the relaxation alone proves closed-loop traffic performance.
