# Theory and Claim-Lock Memo

**Date**: 2026-05-22  
**Phase**: 01 — Theoretical Core and Claim Lock  
**Requirements covered in this phase artifact**: THRY-01, THRY-02, THRY-03, THRY-04, THRY-05  
**Primary references**: `.planning/phases/01-theoretical-core-and-claim-lock/01-CONTEXT.md`, `.planning/phases/01-theoretical-core-and-claim-lock/01-RESEARCH.md`, `refine-logs/THEORY_AND_ATOMS.md`, `scripts/run_dual_sanity.py`, `pi_light_code/agent/rule_based/max_pressure.py`

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
LinkValue(l)              := lambda_l
LinkDualPressure(i,j)     := lambda_i - lambda_j
FullServiceValue(i,j)     := LinkDualPressure(i,j)
                             + ExplicitResourceCorrection(i,j)
```

A positive `LinkDualPressure(i,j)` is interpreted as the conservation-dual component of first-order objective improvement from increasing service on movement `i -> j` at the zero-service marginal point. In the current Block 0 implementation this is exactly the convention

```text
movement_values[m] = equality_duals[up] - equality_duals[down]
```

where `up` and `down` are the upstream and downstream link indices of movement `m`. Because the LP is written as a cost minimization problem, the same statement can also be read as: serving an upstream queue is valuable when it removes vehicles from a high marginal congestion-cost link and sends them toward a lower marginal congestion-cost or less scarce downstream link.

`FullServiceValue(i,j)` denotes the full reduced marginal service value after adding any reduced-cost terms from explicitly written phase, green-budget, service-bound, corridor, or other resource constraints. The equality `FullServiceValue(i,j) = LinkDualPressure(i,j)` holds only when those explicit resource multipliers are absent, slack, or ranking-neutral for the movements being compared.

The phrase `dual-sensitivity decomposition` below refers to the decomposition of the full service value into upstream link value, downstream link value, and any modeled scarcity or service feasibility shadow prices that are present in the written primal relaxation.

## THRY-02 — Movement-Level Dual-Sensitivity Decomposition

### Lemma 1 — Movement marginal service value

Consider the capacitated movement-service relaxation in THRY-01 and a feasible base point at which movement `m=(i,j)` can receive an infinitesimal additional service perturbation `epsilon > 0` without immediately hitting its own upper-service bound. Let `V(epsilon)` denote the optimal objective value after forcing `u_m = epsilon` from the same base state and holding the other zero-service marginal comparison conventions fixed. Then, under the sign convention above,

```text
[V(0) - V(epsilon)] / epsilon = lambda_i - lambda_j + o(1).
```

Thus the conservation-dual component of the first-order movement value is

```text
LinkDualPressure(i,j) = upstream link value - downstream link value
                      = lambda_i - lambda_j.
```

When explicit resource constraints are absent, slack, or ranking-neutral for the compared movements, this component is also the full reduced service value. Otherwise, the full reduced service value adds the corresponding explicit reduced-cost corrections from those written constraints.

The upstream term is positive when service removes flow from a link with high marginal congestion cost. The downstream term is subtracted because the same movement contributes flow to the receiving link, whose marginal value may include downstream queue cost and modeled receiving-capacity scarcity.

### Expanded generalized-pressure form

When the written primal model includes finite storage, supply, phase/service, or corridor constraints, the link and movement values can be expanded conceptually as

```text
FullServiceValue(i,j)
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

Standard LP sensitivity then identifies the derivative of the optimal value with the relevant shadow-price expression for sufficiently small perturbations that preserve the active-set structure. Therefore ranking movements by `lambda_up - lambda_down` is equivalent to ranking first-order service benefits only in the Block 0 comparison class where explicit resource corrections are absent, slack, or ranking-neutral. In the general written relaxation, ranking by `FullServiceValue` must include any non-neutral reduced-cost corrections, and every such scarcity or service term must be traceable to a corresponding primal constraint.

### Alignment with validation code

`solve_relaxation()` in `scripts/run_dual_sanity.py` extracts `res.eqlin.marginals` as equality duals and computes movement values as `equality_duals[up] - equality_duals[down]`. The validation routine `finite_difference_service_values()` forces a small service amount on each movement and compares the resulting objective decrease with those dual movement values. The script gate `rank_match_finite_difference` is therefore a direct check that this THRY-02 sign convention and dual-sensitivity decomposition are consistent with the project’s current Block 0 LP sanity scaffold.

### Claim boundary for THRY-02

THRY-02 proves an interpretation of marginal service values inside the continuous relaxation. It does not prove that a controller using those values is superior to max-pressure, capacity-aware pressure, or learned controllers in closed-loop SUMO. Those empirical and regime-specific claims are intentionally deferred to later phase gates.

## THRY-03 — Pressure/Backpressure Special Case

### Theorem 1 — Pressure/backpressure is the slack-regime dual ranking

Consider the THRY-01 relaxation at a fixed local traffic state with a fixed set of feasible movements and phase-compatible movement groups. Suppose the following conditions hold for the movements being compared:

1. **Queue-value specialization**: the link value used by the relaxation is a monotone queue weight `w_l`, and in the ordinary pressure case `w_l = x_l`.
2. **Interior service perturbations**: upstream queues permit the compared infinitesimal services, next-queue lower bounds remain slack, and movement lower/upper service bounds do not bind non-neutrally.
3. **Slack or ranking-neutral scarcity and resources**: storage, supply, downstream receiving-capacity, phase/green resources, service-feasibility constraints, and optional corridor/service constraints are either nonbinding for the compared infinitesimal services or contribute the same additive or positive affine adjustment to all compared movement scores, so they do not change the ranking.
4. **Fixed local movement topology**: each candidate phase score is computed by summing the movement values of its feasible lane-link or movement set; the compared movements share the same topology convention.
5. **No unmodeled correction terms**: any phase/service or corridor correction used in the score is backed by a written primal constraint; if no such constraint is present, its dual term is zero by definition rather than assumed.

Then ranking movements by the THRY-02 full service value is identical to ranking ordinary pressure/backpressure, because the full value reduces to its link-dual pressure component under these interior/slack or ranking-neutral assumptions:

```text
FullServiceValue(i,j) = LinkDualPressure(i,j)
                      = lambda_i - lambda_j
                      = w_i - w_j,
```

and, when `w_l = x_l`,

```text
FullServiceValue(i,j) = x_i - x_j.
```

For a phase `p` with feasible movement set `M_p`, the corresponding phase score reduces to the usual pressure aggregation:

```text
PhaseScore(p) = sum_{(i,j) in M_p} MovementValue(i,j)
              = sum_{(i,j) in M_p} (x_i - x_j).
```

Thus ordinary max-pressure/backpressure is a structural special case of the generalized dual-sensitivity score, not a failed novelty claim.

### Proof sketch

Under THRY-02, a movement `m=(i,j)` has conservation-dual pressure component `lambda_i - lambda_j`, while the full reduced service value may include explicit resource corrections. In the interior/slack regime, upstream service feasibility, next-queue lower bounds, movement service bounds, storage/supply inequalities, and phase/green resources have no non-neutral active contribution. In a ranking-neutral regime, any remaining modeled scarcity or service contribution is common across the movements being compared, or is transformed by the same positive affine map, so it cannot change their order.

With link value specialized to the queue weight, the conservation-dual pressure component becomes `w_i - w_j`. Setting `w_l = x_l` gives the standard upstream-minus-downstream pressure score. Summing these movement scores over the movements enabled by a phase yields the phase-level backpressure score. Therefore the full dual ranking and ordinary pressure/backpressure ranking coincide only under the stated interior, slack, or ranking-neutral assumptions.

### Alignment with the existing max-pressure implementation

`pi_light_code/agent/rule_based/max_pressure.py` scores each candidate phase by iterating over the phase's available lane links, adding the upstream lane observation and subtracting the downstream lane observation. This is the implementation analogue of

```text
sum_{(i,j) in M_p} (x_i - x_j).
```

The implementation is not used as a proof. It is cited only to show that the project baseline's phase-score convention matches the theorem's upstream-minus-downstream queue aggregation when the generalized dual score is in its pressure/backpressure special case.

### Validation-code alignment

`run_dual_sanity.py` computes both `movement_values[m] = equality_duals[up] - equality_duals[down]` and `pressure_scores[m] = queue_weight[up] - queue_weight[down]`. Its gate `pressure_special_case_pass` checks that the dual rank matches the pressure rank when storage duals are nonbinding. This script gate supports notation consistency for THRY-03; it is not closed-loop traffic-control evidence.

### Claim boundary for THRY-03

THRY-03 is a positive equivalence result: the dual-sensitivity construction recovers ordinary pressure/backpressure in slack or ranking-neutral regimes. It should be presented as an expected structural property and as a reason pressure remains a strong baseline. Any claim that scarcity-aware corrections are empirically useful is routed to later phase gates.

## THRY-04 — Binding-Regime Scarcity Correction

### Proposition 1 — Sufficient binding-regime rank-change condition

Consider two candidate movements `a=(i,j)` and `b=(p,q)` that are feasible under the same local signal-decision comparison. Let their ordinary pressure scores be

```text
P_a = w_i - w_j,
P_b = w_p - w_q,
```

and let their modeled dual-sensitivity scores be written as

```text
D_a = P_a + C_a,
D_b = P_b + C_b,
```

where `C_a` and `C_b` collect only correction terms generated by explicit primal constraints in the THRY-01 relaxation or in a stated extension of it. In the present memo these are storage/supply scarcity effects embedded in downstream or upstream link values and any written phase/service feasibility multipliers. Corridor or service-balance corrections may be included only after the primal model writes the corresponding corridor/service constraint; without that constraint, the corridor/service correction is not theory-backed and is set aside.

If ordinary pressure ranks movement `a` above movement `b`, so that

```text
P_a - P_b > 0,
```

but the modeled scarcity correction satisfies

```text
C_b - C_a > P_a - P_b,
```

then the dual-sensitivity ranking places `b` above `a`:

```text
D_b > D_a.
```

Equivalently, the pressure ranking can change in a binding-regime state whenever the differential storage/supply or service-feasibility scarcity correction exceeds the ordinary pressure gap.

### Interpretation of storage and supply scarcity

The main binding-regime case is downstream receiving scarcity. If movement `a=(i,j)` sends vehicles into a nearly full downstream link `j`, while movement `b=(p,q)` sends vehicles into a downstream link `q` with more available storage or lower supply shadow price, then the link value `lambda_j` can contain a larger receiving-capacity penalty than `lambda_q`. Because downstream value is subtracted in `lambda_up - lambda_down`, this can reduce `D_a` relative to `D_b` even when `P_a > P_b`.

This proposition is intentionally stated as a sufficient rank-change condition. It does not say that every binding storage constraint changes the action, nor that every correction improves traffic outcomes. A binding constraint can be too small, common across alternatives, or ranking-neutral. In those cases THRY-03-style pressure ranking may persist.

### Proof sketch

Subtract the two dual scores:

```text
D_b - D_a = (P_b - P_a) + (C_b - C_a).
```

Ordinary pressure ranks `a` above `b` when `P_a - P_b > 0`, or equivalently `P_b - P_a < 0`. If the correction advantage for `b` satisfies `C_b - C_a > P_a - P_b`, then the positive correction difference is larger than the pressure gap favoring `a`. Therefore `D_b - D_a > 0`, so the dual score ranks `b` above `a`. The same algebra covers ties or partial rank changes by replacing the strict inequality with non-strict or thresholded versions.

The proposition is model-dependent because `C_a` and `C_b` are not free narrative terms. They must arise from the KKT multipliers or reduced-cost terms of the written storage/supply, phase/service, or explicitly added corridor/service constraints.

### Phase 3 claim routing

THRY-04 legitimizes why dual sensitivity may differ from ordinary pressure in a binding-regime state. It does not establish that those differences are beneficial in closed-loop traffic control. The empirical route is deliberately assigned to the Phase 3 static pressure-failure kill gate:

1. If static binding-regime evidence shows that scarcity corrections reduce oracle regret against pressure, later phases may pursue the stronger generalized-pressure claim.
2. If evidence shows ties, the paper should emphasize pressure-equivalent symbolic recovery and compactness.
3. If evidence shows worse rankings, the paper should pivot to diagnostic framing rather than claiming pressure improvement.

This Phase 3 routing is part of the claim boundary: scarcity correction is a formal possibility under explicit model assumptions, while empirical usefulness remains a downstream gate.

## THRY-05 — Finite-Dictionary Symbolic Recovery Quality

### Definition 2 — Finite symbolic policy dictionary

Let `D_N = {(s_n, Q_n(a))}_{n=1}^N` be a finite set of sampled traffic states and oracle movement or phase values, where `Q_n(a)` is the relaxation-derived finite-difference value, dual-guided oracle value, or other explicitly declared oracle value for action `a` in state `s_n`. A symbolic policy `pi` maps each sampled state to one feasible action through a finite atom dictionary.

For Phase 1 claim-lock purposes, define a **finite-dictionary** class

```text
Pi(K, B, H, D) = { symbolic policies using
                  at most K selected atoms,
                  program size at most B or a program-size penalty,
                  at most H neighbor-dependent atoms or a neighbor-use penalty,
                  at most D dual-price-dependent atoms or a dual-price penalty }.
```

The atom library may include local queue atoms, raw upstream/downstream neighbor atoms, downstream slack/fullness atoms, pressure/backpressure atoms, dual-sensitivity atoms, and placebo/random-price atoms. The current scaffold in `scripts/run_sparse_recovery.py` implements finite libraries such as `local_only`, `raw_neighbor`, `all_neighbor`, `random_price`, `dual_sensitivity`, `dual_plus_raw`, and `pressure_backpressure`; Phase 2 may expand the library, but the recovery-quality statement remains finite-class and budgeted.

The budgets or penalties have the following claim-lock meaning:

- **Atom budget `K`** limits the number of selected scoring atoms.
- **Program-size budget or penalty `B`** limits rule length or charges a complexity penalty such as `lambda_complexity * selected_atom_count`.
- **Neighbor-use budget or penalty `H`** limits or charges atoms requiring nonlocal upstream/downstream state beyond the controlled approach.
- **Dual-price dependence budget or penalty `D`** limits or charges atoms that use LP/KKT shadow prices or dual-sensitivity values rather than raw traffic state alone.

### Empirical recovery target

The primary recovery target is empirical oracle regret or value gap, not action agreement alone. For a deterministic policy `pi`, define

```text
R_hat_N(pi) = (1/N) sum_{n=1}^N [ max_{a in A(s_n)} Q_n(a) - Q_n(pi(s_n)) ].
```

Equivalently, when the oracle is expressed as a cost-to-minimize rather than value-to-maximize, use the empirical value gap between the policy action and the sample-best oracle action. In both conventions, lower `R_hat_N` means the recovered symbolic policy is closer to the finite-sample oracle. Action agreement with the oracle argmax may be reported as a secondary diagnostic, but it is not the main recovery objective because ties and near-ties can make agreement misleading relative to value gap.

### Proposition 2 — Deterministic finite-dictionary empirical recovery quality

Fix the sampled states `D_N`, the feasible action sets, the finite atom dictionary, and budgets or penalties `(K, B, H, D)`. Suppose the recovery solver returns a symbolic policy `pi_hat` whose mixed-integer or enumerative objective is within additive optimization gap `epsilon_opt >= 0` of the best feasible policy in `Pi(K, B, H, D)` for the empirical oracle-regret objective plus declared penalties. Then

```text
R_hat_N(pi_hat)
  + penalty(pi_hat)
  <= min_{pi in Pi(K,B,H,D)} [ R_hat_N(pi) + penalty(pi) ] + epsilon_opt.
```

If the implementation uses hard budgets only, `penalty(pi)=0` for feasible policies and the statement reduces to

```text
R_hat_N(pi_hat) <= min_{pi in Pi(K,B,H,D)} R_hat_N(pi) + epsilon_opt.
```

If the implementation uses soft penalties, an example compatible with `scripts/run_sparse_recovery.py` is

```text
penalty(pi) = lambda_size * selected_atom_count(pi)
            + lambda_neighbor * neighbor_atom_count(pi)
            + lambda_dual * dual_price_atom_count(pi).
```

This is an optimization-quality statement over the declared finite dictionary and the declared sample. It does not claim that the recovered policy is globally optimal for traffic control, globally optimal over all possible symbolic rules, or closed-loop superior to max-pressure. Those empirical and deployment claims require Phase 3 and Phase 4 evidence.

### Alignment with the sparse recovery scaffold

`run_sparse_recovery.py` builds a finite atom matrix for each library, chooses atom weights and one selected action per example, charges a complexity penalty on selected atoms, and evaluates realized oracle regret using

```text
best oracle value - oracle value of chosen action.
```

Its outputs include selected atoms, weights, program complexity, realized total regret, realized mean regret, action agreement, and per-example oracle regret. These outputs are sufficient to validate that a Phase 2 implementation is optimizing an empirical oracle-regret or value-gap target under finite-dictionary constraints. The script is supporting scaffold evidence, not a claim that full Phase 2 recovery is complete.

### Optional finite-sample corollary — assumption-bound only

If the sampled states are IID from a declared population distribution, oracle regrets are uniformly bounded in `[0, R_max]`, and the dictionary `Pi(K,B,H,D)` is finite with cardinality `|Pi|`, then standard finite-class uniform convergence can be invoked to state a population-regret corollary of the form

```text
R(pi_hat) <= min_{pi in Pi(K,B,H,D)} R(pi)
             + epsilon_opt
             + O(R_max * sqrt((log |Pi| + log(1/delta)) / N))
```

with probability at least `1-delta`, up to constants and any penalty accounting. This optional corollary must be labeled statistical, sample-assumption-dependent, and dictionary-relative. It must not be used as evidence of global traffic-control optimality or universal dominance over pressure-style controllers.

### Claim boundary for THRY-05

Allowed: the finite-dictionary recovery procedure can be judged by empirical oracle regret/value gap relative to the best policy in the same constrained dictionary plus solver gap, with program size, neighbor use, and dual-price dependence explicitly budgeted or penalized.

Not allowed: claiming that sparse recovery alone proves closed-loop traffic performance, that action agreement is sufficient evidence of recovery quality, or that a recovered dual-symbolic rule is globally optimal for traffic control before the Phase 3 kill gate and Phase 4 closed-loop validation.
