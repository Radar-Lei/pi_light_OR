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

## Sign Convention for Dual Movement Values

This memo follows the minimization convention used in `scripts/run_dual_sanity.py` and SciPy/HiGHS LP marginals.

```text
LinkValue(l)        := lambda_l
MovementValue(i,j)  := lambda_i - lambda_j
```

A positive `MovementValue(i,j)` is interpreted as first-order objective improvement, or marginal service benefit, from increasing service on movement `i -> j` at the zero-service marginal point. In the implementation this is exactly the convention

```text
movement_values[m] = equality_duals[up] - equality_duals[down]
```

where `up` and `down` are the upstream and downstream link indices of movement `m`. Because the LP is written as a cost minimization problem, the same statement can also be read as: serving an upstream queue is valuable when it removes vehicles from a high marginal congestion-cost link and sends them toward a lower marginal congestion-cost or less scarce downstream link.

The phrase `dual-sensitivity decomposition` below refers to the decomposition of this movement value into upstream link value, downstream link value, and any modeled scarcity or service feasibility shadow prices that are present in the written primal relaxation.

## THRY-02 — Movement-Level Dual-Sensitivity Decomposition

### Lemma 1 — Movement marginal service value

Consider the capacitated movement-service relaxation in THRY-01 and a feasible base point at which movement `m=(i,j)` can receive an infinitesimal additional service perturbation `epsilon > 0` without immediately hitting its own upper-service bound. Let `V(epsilon)` denote the optimal objective value after forcing `u_m = epsilon` from the same base state and holding the other zero-service marginal comparison conventions fixed. Then, under the sign convention above,

```text
[V(0) - V(epsilon)] / epsilon = lambda_i - lambda_j + o(1).
```

Thus the first-order movement value is

```text
MovementValue(i,j) = upstream link value - downstream link value
                   = lambda_i - lambda_j.
```

The upstream term is positive when service removes flow from a link with high marginal congestion cost. The downstream term is subtracted because the same movement contributes flow to the receiving link, whose marginal value may include downstream queue cost and modeled receiving-capacity scarcity.

### Expanded generalized-pressure form

When the written primal model includes finite storage, supply, phase/service, or corridor constraints, the link and movement values can be expanded conceptually as

```text
MovementValue(i,j)
  = [local upstream queue value on i]
    - [local downstream queue value on j]
    + [modeled upstream/downstream storage or supply correction]
    + [modeled phase/service feasibility correction]
    + [modeled corridor or network-coupling correction, if and only if such a primal constraint exists].
```

More concretely:

- **Upstream value**: the conservation dual `lambda_i` captures the marginal objective effect of one additional vehicle in the upstream queue balance.
- **Downstream value**: the conservation dual `lambda_j` captures the marginal objective effect of one additional vehicle in the downstream queue balance.
- **Storage/supply correction**: when `x_j^+ <= S_j + z_j` binds, the storage/supply dual and overflow penalty alter `lambda_j`; the downstream term therefore contains receiving-capacity scarcity rather than only downstream queue length.
- **Phase/service correction**: if a phase green budget, split constraint, or service feasibility constraint is written explicitly and binds, its KKT multiplier changes the reduced marginal benefit of assigning service to movements that consume that phase resource.
- **Corridor correction**: a corridor, platoon, or service-balance term exists only if the relaxation explicitly includes a primal corridor/service constraint. Without that constraint, no corridor dual should be claimed and no `CorridorValue` atom should be treated as theory-backed.

This is why the memo describes dual movement value as generalized pressure: ordinary upstream-minus-downstream pressure is the visible skeleton, while binding capacity and service constraints can add scarcity-aware corrections through the LP dual system.

### Proof sketch

Write the Lagrangian for the THRY-01 LP using equality multipliers `lambda_l` for queue conservation and inequality multipliers for storage/supply, phase/service, and service-bound constraints. A perturbation that increases service on `m=(i,j)` changes only the conservation rows for links `i` and `j` at first order, plus any explicit resource constraints that the service variable consumes. The conservation contribution to the directional derivative is `lambda_i - lambda_j` under the implementation convention. If storage/supply or phase/service constraints bind, their multipliers enter through stationarity and reduced-cost terms, either embedded in the affected link values `lambda_l` or appearing as explicit resource-consumption corrections.

Standard LP sensitivity then identifies the derivative of the optimal value with the relevant shadow-price expression for sufficiently small perturbations that preserve the active-set structure. Therefore ranking movements by `lambda_up - lambda_down` is equivalent to ranking first-order service benefits in the relaxation, and any additional scarcity or service terms must be traceable to a corresponding primal constraint.

### Alignment with validation code

`solve_relaxation()` in `scripts/run_dual_sanity.py` extracts `res.eqlin.marginals` as equality duals and computes movement values as `equality_duals[up] - equality_duals[down]`. The validation routine `finite_difference_service_values()` forces a small service amount on each movement and compares the resulting objective decrease with those dual movement values. The script gate `rank_match_finite_difference` is therefore a direct check that this THRY-02 sign convention and dual-sensitivity decomposition are consistent with the project’s current Block 0 LP sanity scaffold.

### Claim boundary for THRY-02

THRY-02 proves an interpretation of marginal service values inside the continuous relaxation. It does not prove that a controller using those values universally dominates max-pressure, capacity-aware pressure, or learned controllers in closed-loop SUMO. Those empirical and regime-specific claims are intentionally deferred to later phase gates.
