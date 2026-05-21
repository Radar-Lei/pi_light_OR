# Experiment Plan — Dual-Sensitivity-Guided Programmatic Signal Control

**Date**: 2026-05-20  
**Target**: CPU/SUMO/AMPL validation for EJOR-first paper  
**Method under test**: continuous dual sensitivities → OR-mapped DSL atoms → sparse MIP regret recovery → closed-loop SUMO deployment

## Claims-to-Evidence Matrix

| Claim | Evidence required | Failure interpretation |
|---|---|---|
| C1: OR dual sensitivities provide principled neighbor coordination signals | dual-to-movement lemma; pressure special case; dual atoms beat raw/all/random/local atoms | If random/raw atoms match dual atoms, method is feature engineering |
| C2: Sparse MIP can recover compact symbolic policies with low oracle regret | oracle regret/value gap; program size; synthesis runtime | If action accuracy is high but regret is high, recovery is not useful |
| C3: Dual-guided symbolic policies improve coupled traffic settings | arterial, grid, demand-shift closed-loop SUMO metrics | If gains appear only in one corridor case, method is too narrow |
| C4: Method is deployable and interpretable | online latency, program size, atom mapping table | If runtime/size is high, deployability claim weakens |

## Metrics

Primary closed-loop metrics:
- average travel time,
- total delay,
- throughput / completed vehicles,
- queue length and max queue,
- spillback events or blocked downstream links,
- number of phase switches.

Oracle/recovery metrics:
- oracle regret/value gap,
- action agreement as secondary metric,
- selected atom count,
- neighbor atom count,
- rule depth / term count,
- MIP solve time.

Runtime metrics:
- AMPL/HiGHS relaxation solve time,
- sparse MIP recovery time,
- online controller latency per decision,
- total CPU time per experiment.

Statistical reporting:
- at least 10 seeds for final comparisons,
- 95% confidence intervals,
- paired tests where scenarios/seeds align,
- report negative and non-significant results.

## Experimental Blocks

### Block 0 — Oracle and Dual Sanity

Purpose: verify the continuous relaxation produces meaningful dual sensitivities before SUMO deployment.

Networks:
- single intersection,
- 2-intersection toy corridor,
- 5-intersection arterial sample states.

Tests:
1. perturb one link queue or storage capacity and compare finite-difference objective change with dual sensitivity;
2. verify movement value has upstream-minus-downstream structure;
3. verify pressure special case when storage constraints are nonbinding.

Pass criteria:
- dual finite-difference correlation is high in simple cases,
- pressure special-case behavior matches expected movement ranking,
- storage-binding cases produce non-pressure downstream scarcity terms.

Decision gate:
- If duals do not match finite-difference sensitivities, stop and fix the relaxation before recovery.

### Block 1 — Sparse MIP Recovery Offline

Purpose: test whether compact symbolic programs can recover oracle value, not merely labels.

Datasets:
- sampled states from single, arterial, grid,
- multiple demand regimes,
- held-out states by demand pattern.

Variants:
1. local-only DSL,
2. raw-neighbor DSL,
3. all-neighbor DSL,
4. random/permuted-price DSL,
5. dual-sensitivity DSL,
6. unconstrained oracle upper bound.

Report:
- oracle regret/value gap,
- action agreement,
- selected atoms,
- program complexity,
- recovery solve time.

Pass criteria:
- dual-sensitivity DSL has lower regret than raw/all/random/local at equal or lower complexity;
- selected atoms have clear OR constraint/sensitivity mapping.

Decision gate:
- If dual DSL does not improve offline regret, do not proceed to expensive closed-loop runs; revise atom mapping or relaxation.

### Block 2 — Single-Intersection Sanity

Purpose: ensure the method does not break local behavior when network coupling is absent.

Controllers:
- fixed-time/Webster,
- actuated,
- max-pressure,
- programmatic local baseline,
- dual-guided recovered policy with neighbor/dual terms absent or zero.

Scenarios:
- low, medium, high demand,
- balanced and imbalanced turning ratios.

Pass criteria:
- dual-guided policy should not materially underperform the local programmatic baseline;
- if it does, the recovery objective or DSL constraints are too restrictive.

### Block 3 — 5-Intersection Arterial Main Result

Purpose: main coordination/platoon setting where dual neighbor signals should matter.

Scenarios:
- directional platoon demand,
- peak reversal,
- oversaturation,
- downstream bottleneck / finite storage,
- turning-ratio error.

Controllers:
- fixed-time/Webster,
- actuated,
- max-pressure,
- C-MP or closest implementable coordinated MP,
- MPC/OR oracle on small horizon if feasible,
- local programmatic baseline,
- raw-neighbor programmatic DSL,
- all-neighbor programmatic DSL,
- random/permuted-price DSL,
- dual-sensitivity DSL.

Primary expectation:
- dual-sensitivity DSL should improve travel time/delay/spillback relative to raw/all/random/local symbolic baselines and be competitive with MP/C-MP.

Claim if successful:
- dual sensitivity supplies useful programmatic coordination signals under corridor coupling.

### Block 4 — 4×4 Grid Generality

Purpose: show the method is not only a corridor heuristic.

Scenarios:
- uniform demand,
- directional OD imbalance,
- localized bottleneck,
- grid oversaturation.

Controllers:
- same as Block 3, except MPC oracle may be limited to small sampled states due to runtime.

Pass criteria:
- dual DSL remains competitive and beats raw/random/local symbolic baselines;
- if C-MP wins, report honestly and focus claim on interpretability/compactness/regret rather than absolute dominance.

### Block 5 — Demand Shift and Robustness

Purpose: test whether dual-guided symbolic programs generalize across regimes.

Train/recover on:
- nominal demand,
- nominal turning ratios.

Test on:
- peak reversal,
- demand scale changes,
- oversaturation,
- turning-ratio perturbation,
- storage bottleneck change.

Key comparisons:
- nominal dual prices vs recomputed periodic dual prices,
- dual DSL vs raw/all/random/local symbolic DSL,
- MP/C-MP baselines.

Allowed claims:
- If nominal prices generalize: compact symbolic recovery captures robust network structure.
- If periodic recomputation is needed: dual sensitivities remain useful but require regime updates.
- If both fail: weaken claim to offline diagnosis/oracle recovery only.

### Block 6 — Runtime and Deployability

Purpose: support practical OR/control contribution.

Report:
- relaxation solve time by network size,
- recovery time by atom budget,
- online decision latency,
- memory footprint if relevant,
- program size and readability.

Pass criteria:
- online policy latency is negligible relative to signal decision intervals;
- offline/periodic optimization remains CPU-feasible for target networks.

## Run Order

1. **Block 0**: dual finite-difference and pressure-special-case sanity.
2. **Block 1 small**: offline recovery on single + arterial states.
3. **Block 2**: single-intersection closed-loop sanity.
4. **Block 3 pilot**: 5-intersection arterial with 3 seeds and key variants.
5. **Block 1 full**: expand recovery datasets after pilot confirms signal.
6. **Block 3 full**: 10-seed arterial results.
7. **Block 4 pilot/full**: 4×4 grid.
8. **Block 5**: demand shift.
9. **Block 6**: runtime, final stats, tables.

## Minimum Viable Paper Package

If time is constrained, minimum package:

- Block 0 dual sanity,
- Block 1 offline recovery,
- Block 3 arterial full,
- Block 4 grid pilot/full,
- Block 5 demand shift on arterial,
- runtime table.

Single-intersection sanity can be brief if already covered by existing code, but should not be omitted entirely.

## Decision Gates

### Gate A — Dual validity

Proceed only if finite-difference checks support dual sensitivity interpretation.

### Gate B — Offline recovery

Proceed only if dual DSL improves oracle regret over raw/random/local at equal complexity.

### Gate C — Arterial closed-loop

If no gain in arterial, do not claim coordination improvement. Reframe as diagnostic/interpretable oracle compression or pivot.

### Gate D — Grid generality

If grid fails but arterial succeeds, target an arterial/corridor coordination paper, not general network control.

### Gate E — Baseline honesty

If C-MP/MPC dominates, claim interpretability/compactness and OR sensitivity recovery, not performance superiority.

## Expected Tables and Figures

1. OR model and dual-to-DSL atom mapping table.
2. Dual finite-difference validation plot.
3. Pressure special-case schematic.
4. Offline recovery regret vs program complexity curve.
5. Arterial closed-loop performance table.
6. Grid closed-loop performance table.
7. Demand-shift robustness table.
8. Runtime/deployability table.
9. Example recovered symbolic program with atom semantics.

## Compute Budget

Expected to be CPU-only:
- SUMO/TraCI simulation,
- AMPL/HiGHS LP/QP solves,
- sparse MIP recovery on bounded atom libraries.

Avoid mandatory neural MARL training. If included, use literature numbers or simplified CPU-feasible baselines only as secondary comparison.
