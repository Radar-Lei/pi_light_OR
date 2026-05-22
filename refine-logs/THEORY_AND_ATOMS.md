# Theory and OR-Mapped Atom Freeze

**Date**: 2026-05-22  
**Scope**: minimal primal-dual model, movement marginal-value lemma, pressure special case, and retained DSL atom taxonomy for the dual-sensitivity recovery paper.

## Purpose

This document freezes the theoretical core used by the current implementation and experiments. The goal is not to claim a new traffic-control optimality principle; it is to justify why dual sensitivities from a continuous relaxation are legitimate, interpretable inputs to sparse symbolic recovery.

## Minimal Continuous Relaxation

For a short horizon, let:

- `x_l(t)` be queue / occupancy on link `l`,
- `d_l(t)` be exogenous arrivals,
- `S_l` be receiving/storage capacity,
- `u_m(t)` be continuous service assigned to movement `m`,
- `A_{lm}` be the signed movement-link incidence matrix, with `A_{lm}=1` when movement `m` removes flow from link `l` and `A_{lm}=-1` when it sends flow into link `l`,
- `z_l(t) >= 0` be overflow/slack for storage violation,
- `w_l >= 0` be queue weight,
- `rho_l >= 0` be storage/spillback penalty.

The one-step relaxation used in the current implementation is:

```text
minimize    sum_l w_l x^+_l + sum_l rho_l z_l
subject to  x^+_l = x_l + d_l - sum_m A_{lm} u_m              for all l
            x^+_l <= S_l + z_l                                for all l
            sum_m u_m <= G
            0 <= u_m <= U_m                                    for all m
            x^+_l >= 0, z_l >= 0                               for all l
```

A multi-step store-and-forward / CTM-lite extension repeats the same conservation and storage constraints over time and may add green smoothness or switching proxies. The theory below only needs the local marginal structure, so the one-step form is sufficient for the Block 0/1 sanity gates.

## Dual Objects

Let `lambda_l` denote the equality dual for the queue conservation constraint of link `l`, under the solver sign convention used by `scipy.optimize.linprog(method="highs")`. Let `mu_l <= 0` denote the inequality dual for the storage/supply constraint `x^+_l - z_l <= S_l`.

In the current minimization convention:

- `lambda_l` is the marginal objective sensitivity of one additional vehicle in the conservation balance of link `l`,
- binding downstream storage changes `lambda_l` through the storage dual and overflow penalty,
- the movement value reported by the implementation is `lambda_up - lambda_down`.

The finite-difference validation compares this value at the same zero-service marginal point by forcing a small `epsilon` service on each movement and measuring objective decrease.

## Lemma 1 — Movement Marginal Service Value

For a feasible zero-service base point of the continuous relaxation, consider a small forced service perturbation `epsilon` on movement `m = i -> j`, with all other movement services fixed at zero and no active upper-service limit on `m` for sufficiently small `epsilon`.

Then the first-order objective improvement from serving movement `i -> j` is:

```text
Delta V_m / epsilon = lambda_i - lambda_j + o(1)
```

under the solver sign convention used in the implementation. When downstream storage or spillback constraints bind, their dual effects enter through `lambda_j`; equivalently, the downstream link value contains both queue-cost and receiving-capacity scarcity. In expanded notation this can be described as:

```text
MovementValue(i,j) = LinkValue(i) - LinkValue(j)
                   = upstream queue value - downstream queue/storage scarcity value
```

For richer CTM-lite models with turning ratios or corridor/service balance constraints, additional terms appear for the affected downstream/corridor constraints. Those terms should only be used as DSL atoms when the corresponding primal constraint exists in the relaxation.

### Implementation Evidence

- `scripts/run_dual_sanity.py` computes `movement_values` as `equality_duals[up] - equality_duals[down]`.
- `finite_difference_service_values()` compares against forced-service perturbations from the same zero-service marginal point.
- `experiments/dual_sensitivity/block0_dual_sanity.json` passes rank and finite-difference sanity on toy, single-intersection, and arterial proxy cases.
- Passive and targeted SUMO-derived states now pass top-choice, exact full-rank, and tie-aware full-rank checks after using the common zero-service marginal point.

## Lemma 2 — Pressure / Backpressure Special Case

Assume:

1. linear queue objective with `w_l = x_l` or another monotone queue weight,
2. no binding downstream storage/supply constraints,
3. no corridor/service balance constraints,
4. fixed local movement topology,
5. infinitesimal service perturbations around the zero-service base point.

Then `lambda_l = w_l` up to the common solver sign convention, and therefore:

```text
MovementValue(i,j) = lambda_i - lambda_j = w_i - w_j.
```

If `w_l = x_l`, this is the ordinary pressure/backpressure movement ranking. Thus max-pressure is a special case of the dual movement-value score, not the novel component itself. The paper's novelty must therefore come from using the same OR dual machinery to select compact symbolic atoms under finite storage, spillback, turning, and network-coupling regimes.

## Retained OR-Mapped Atom Taxonomy

Only atoms with a direct model variable, constraint, or dual interpretation should be retained.

| Atom | Current implementation name | OR source | Status |
|---|---|---|---|
| Local upstream queue | `upstream_queue` | queue state `x_i` | Retain as local baseline atom |
| Downstream queue penalty | `neg_downstream_queue` | queue state `x_j` | Retain as raw-neighbor baseline atom |
| Downstream storage slack | `downstream_slack` | storage capacity residual `S_j - x_j` | Retain when capacities are present |
| Downstream fullness | `neg_downstream_fullness` | normalized storage occupancy `x_j / S_j` | Retain as interpretable storage feature |
| Link value | `LinkValue(l)` | conservation dual `lambda_l` | Retain for theory/paper taxonomy |
| Downstream scarcity | `DownstreamScarcity(l)` | storage/supply dual effect in `lambda_l` or explicit `mu_l` | Retain when storage constraints bind |
| Movement value | `dual_sensitivity` / `MovementValue(i,j)` | `lambda_i - lambda_j` | Retain as primary dual atom |
| Value imbalance | `ValueImbalance(up,down)` | upstream-downstream dual difference | Retain as movement scoring atom |
| Pressure diagnostic | `pressure_backpressure` | special case `w_i - w_j` | Retain as diagnostic/strong baseline, not as a novelty claim |
| Random price | `random_price` | permuted dual ablation | Retain only as ablation |
| Corridor value | `CorridorValue(c)` | corridor/service balance dual | Deferred until the relaxation includes an explicit corridor constraint |

## Excluded or Deferred Atoms

The following should not be used as paper claims unless the relaxation is extended with matching variables or constraints:

- generic neighbor queue aggregates not tied to a movement or constraint,
- learned neural embeddings,
- arbitrary distance-to-intersection or route features,
- corridor criticality without a corridor constraint or OD/service-balance proxy,
- phase-history features unless switching/smoothness constraints are explicitly added.

## Recovery Objective Freeze

The offline recovery objective should be reported as:

```text
minimize realized_oracle_regret(policy)
       + lambda_complexity * selected_atom_count
       + lambda_neighbor * neighbor_atom_count
```

The primary metric is realized oracle regret under deterministic policy evaluation. Action agreement is secondary. This avoids the failure mode where a policy matches labels in low-value states but makes high-regret errors in bottleneck/spillback states.

## Claim Boundary

Allowed claims after Block 0/1:

- dual movement values match finite-difference marginal service values in the continuous relaxation;
- pressure/backpressure is recovered as a nonbinding-storage special case;
- sparse offline recovery selects dual-sensitivity atoms and achieves lower realized oracle regret than raw/local/random atoms on passive+targeted state datasets.

Not yet allowed before closed-loop experiments:

- dual symbolic control improves real traffic performance;
- dual dominates max-pressure or C-MP;
- the method is robust on grids or demand shifts;
- the recovered program is deployable at scale beyond measured runtime.
