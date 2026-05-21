# OR-Informed Phase 2 Idea Report — PI-Light + Neighbor-Aware Coordination

**Date**: 2026-05-19
**Purpose**: Re-run Phase 2 using Obsidian OR material, not only TSC literature.
**Current user preference**: PI-Light should stay central; OR should genuinely enhance multi-intersection coordination using neighboring intersection states.

## Obsidian OR Material Used

Fully usable/read material:
- `Research/OR_RL_TSC_Literature_Survey_2024_2026.md`: OR+RL for TSC survey. Key mechanisms: Lagrangian methods, ADMM, max-pressure as OR reward/state signal, store-and-forward, bilevel optimization, CTM, reward shaping, MIP/decomposition, hierarchical RL/decomposition.
- `OR/Linear Programming/...Part16.md`: references/index-level material on network flows, LP, Dantzig-Wolfe decomposition, network simplex, minimum-cost circulation, dynamic programming, distributed optimization.

Caveat:
- Some broad OR textbook/ILP notes were too large to read fully through the MCP response and are not used as direct evidence here.

## Key OR Mechanisms Extracted

The previous Phase 2 used “OR-derived coordination graph” somewhat generically. The OR material suggests more concrete mechanisms:

1. **Shadow prices / dual variables**
   - Solve a store-and-forward or CTM-lite relaxation.
   - Extract link/intersection/corridor dual values.
   - Use those values as interpretable weights in PI-Light DSL terms.

2. **Lagrangian / dual decomposition**
   - Relax coupling constraints between intersections.
   - Each intersection gets a local subproblem plus neighbor/coupling prices.
   - PI-Light learns a symbolic approximation to the local price-augmented policy.

3. **ADMM / consensus coordination**
   - Adjacent intersections maintain local decisions but coordinate shared boundary flows or queues.
   - ADMM messages can become symbolic program inputs: neighbor imbalance, consensus residual, downstream capacity pressure.

4. **Store-and-forward / CTM-lite oracle**
   - Use a traffic-flow conservation model as an OR oracle.
   - Generate labels/weights/features for PI-Light rather than replacing PI-Light online.

5. **Network flow / min-cost flow abstraction**
   - Treat intersection coordination as sending capacity along corridors/routes.
   - OR identifies critical corridors, bottleneck links, and relevant neighbors.

6. **MIP/LP certificates**
   - Use MIP/LP to certify which neighbor terms are necessary, or to upper-bound the gap between symbolic rule and oracle.

## Revised Ranked Ideas

### Idea 1: Dual-Price π-Light — RECOMMENDED

**One-sentence summary**: Use OR dual variables from a store-and-forward/CTM-lite network relaxation as neighbor-aware weights inside PI-Light’s symbolic priority programs.

**Core method**:
1. Build a network-level LP/QP/MILP-lite model over short horizon:
   - state: queue/storage on links,
   - decision: approximate service/phase allocation,
   - constraints: flow conservation, storage, turning ratios, green split feasibility.
2. Solve offline or periodically with AMPL/HiGHS.
3. Extract dual variables/shadow prices for:
   - downstream storage constraints,
   - link conservation constraints,
   - corridor capacity constraints,
   - intersection coupling constraints.
4. Convert prices into PI-Light DSL features:
   - `neighbor_downstream_price`,
   - `upstream_arrival_price`,
   - `corridor_shadow_price`,
   - `storage_slack_price`.
5. Search a compact symbolic program using local + price-weighted neighbor features.

**Why this is more OR than generic coordination graph**:
The neighbor weights are not hand-designed; they are marginal values from an optimization relaxation. This gives a clear OR interpretation: a vehicle/queue is prioritized when the network optimization says its marginal congestion cost is high.

**Hypothesis**:
A small number of dual-price neighbor terms can make PI-Light coordinate across intersections and outperform local PI-Light/max-pressure under directional demand, bottlenecks, and spillback.

**Minimum pilot**:
- 5-intersection arterial.
- LP relaxation computes link/corridor prices every 300s or offline by demand regime.
- Compare:
  1. local PI-Light-style rule,
  2. all-neighbor PI-Light,
  3. OR-selected-neighbor PI-Light without prices,
  4. Dual-Price π-Light,
  5. max-pressure / C-MP.

**Contribution type**: Method + OR interpretation + empirical.

**Novelty estimate**: HIGH-MEDIUM.
Closest ideas exist in reward shaping and max-pressure theory, but direct “optimization dual prices as symbolic PI-Light program features for neighbor-aware TSC” appears distinctive.

**Risk**: MEDIUM.
Dual values may be noisy or regime-dependent; mitigate by using price bins/signs/thresholds in DSL rather than raw continuous prices.

**Why it should be top**:
It is a genuine PI-Light+OR combination: PI-Light is still the controller; OR supplies marginal-value semantics and neighbor coordination.

---

### Idea 2: Lagrangian-Decomposed π-Light — RECOMMENDED

**One-sentence summary**: Formulate multi-intersection coordination as a decomposed optimization problem, where coupling constraints between neighboring intersections produce Lagrange multipliers that enter each local PI-Light program.

**Core method**:
- Network problem has local intersection objectives plus coupling constraints:
  - downstream storage consistency,
  - upstream/downstream flow balance,
  - corridor progression constraints,
  - shared bottleneck capacity constraints.
- Relax coupling constraints with Lagrange multipliers.
- Each intersection receives local observations plus neighbor multiplier signals.
- PI-Light searches a symbolic local policy of the form:
  - local priority term + multiplier-weighted neighbor term.

**OR role**:
Lagrangian decomposition provides the architecture: local subproblems connected by prices. This is stronger than generic “neighbor state augmentation.”

**Hypothesis**:
Price-mediated symbolic policies coordinate better than purely local rules while remaining decentralized and interpretable.

**Minimum pilot**:
- 2×2 grid or 5-intersection arterial.
- Use simple multiplier updates from simulated flow imbalance.
- Compare no multipliers vs fixed multipliers vs learned/updated multipliers.

**Contribution type**: Method + decomposition framework.

**Novelty estimate**: HIGH-MEDIUM.
The Obsidian survey explicitly notes dual decomposition + RL for TSC as a gap. Here it is dual decomposition + programmatic interpretable RL.

**Risk**: MEDIUM-HIGH.
May be mathematically/implementation heavy. Multipliers need stable update logic.

**Best positioning**:
Use it as the theoretical framing behind Idea 1: Dual-Price π-Light can be presented as the deployable policy class arising from a Lagrangian decomposition.

---

### Idea 3: Store-and-Forward Oracle → Neighbor-Aware DSL Recovery — RECOMMENDED AS VALIDATION COMPONENT

**One-sentence summary**: Use a store-and-forward OR model to generate coordinated decisions or marginal labels, then recover a compact neighbor-aware PI-Light DSL rule.

**Core method**:
- Use store-and-forward model as oracle on sampled SUMO states.
- Solve finite-horizon LP/MILP/QP in AMPL.
- Generate either:
  1. action labels,
  2. phase priority labels,
  3. dual-price labels,
  4. critical-neighbor labels.
- Search/recover compact DSL rule.

**OR role**:
Oracle generation + recoverability certificate.

**Hypothesis**:
Coordinated OR decisions are compressible into a small number of neighbor-aware symbolic conditions.

**Minimum pilot**:
- 2×2 grid, 4 intersections, short horizon.
- Sample 1k–10k states.
- Recover K=1/K=2 rules.
- Report oracle agreement and SUMO deployment gap.

**Novelty estimate**: HIGH-MEDIUM.
Distillation is known, but OR traffic-signal oracle to PI-Light neighbor-aware DSL is a specific and likely novel bridge.

**Risk**: MEDIUM.
If oracle recovery fails, contribution shifts to diagnostic: “why simple symbolic coordination fails.”

**Role in paper**:
This should not necessarily be the main online method, but it can justify Dual-Price/Decomposed π-Light and provide an OR upper bound.

---

### Idea 4: ADMM-Message π-Light

**One-sentence summary**: Use ADMM-style neighbor messages/residuals as compact interpretable inputs to PI-Light local programs.

**Core method**:
- Neighboring intersections share local planned flow/service variables.
- ADMM updates consensus residuals for boundary links or corridor flow.
- PI-Light program uses residual signs/magnitudes to adjust priorities:
  - if downstream residual high, hold or reroute green;
  - if upstream residual high, release platoon.

**OR role**:
Distributed optimization messages become interpretable policy features.

**Hypothesis**:
ADMM residuals summarize coordination pressure better than raw all-neighbor states.

**Minimum pilot**:
- 2×2 grid with boundary flow consistency constraints.
- Compare raw-neighbor DSL vs ADMM-message DSL.

**Novelty estimate**: MEDIUM-HIGH.
ADMM traffic coordination exists, but ADMM messages as symbolic PI-Light inputs seems unusual.

**Risk**: HIGH.
More difficult to explain and implement cleanly; may feel artificial unless the ADMM subproblem is well motivated.

**Verdict**:
Interesting but not first choice; keep as theoretical extension if Dual-Price π-Light works.

---

### Idea 5: Network-Flow Critical Corridor π-Light

**One-sentence summary**: Use min-cost flow / shortest-path / bottleneck analysis to identify critical corridors and neighbors, then let PI-Light learn symbolic rules that prioritize corridor progression under congestion.

**Core method**:
- Build a graph abstraction from origin-destination demand and travel times.
- Solve min-cost flow or identify critical paths/cuts.
- Mark corridor memberships and bottleneck links as features.
- PI-Light DSL learns corridor-aware local priority rules.

**OR role**:
Network flow identifies global structure; PI-Light handles local online decisions.

**Hypothesis**:
Corridor/cut features are a low-dimensional, interpretable substitute for neural attention.

**Minimum pilot**:
- 5-intersection arterial + 4×4 grid with OD flows.
- Compare corridor-aware DSL to local/all-neighbor DSL.

**Novelty estimate**: MEDIUM.
Network flow and corridor coordination are classic; novelty depends on PI-Light DSL integration and performance.

**Risk**: MEDIUM.
Could be perceived as feature engineering.

**Verdict**:
Strong practical baseline/ablation; less theoretically elegant than dual prices.

---

### Idea 6: Robust Dual-Price π-Light under Demand Uncertainty

**One-sentence summary**: Use robust/stochastic optimization to compute price ranges or uncertainty-aware neighbor weights, then search PI-Light rules that remain effective under changing demand patterns.

**Core method**:
- Demand uncertainty sets/scenarios.
- Robust or stochastic LP computes worst-case/expected marginal values.
- DSL uses robust price categories rather than point estimates.

**OR role**:
Robust/stochastic optimization determines stable coordination signals.

**Hypothesis**:
Robust price features improve generalization across cities/demand shifts, aligning with PI-Light’s original generalization motivation.

**Minimum pilot**:
- Train/search on one demand distribution, test on shifted OD/demand ratios.

**Novelty estimate**: MEDIUM.
Robust TSC exists; robust dual-price symbolic PI-Light is more specific.

**Risk**: MEDIUM-HIGH.
Can become too broad for first paper.

**Verdict**:
Use as a later ablation or extension, not main method.

## Revised Recommendation

The strongest OR-informed paper should combine Ideas 1–3:

# **Dual-Price Coordination π-Light**

Working thesis:

> We extend PI-Light to multi-intersection coordination by augmenting its symbolic priority programs with OR-derived dual-price neighbor features. A store-and-forward/CTM-lite relaxation computes marginal congestion prices for links/corridors; these prices select and weight neighboring states in the DSL. The resulting controller remains a compact PI-Light program but coordinates across intersections through interpretable OR price signals.

## Why this is better than the previous “Coordination-Graph PI-Light”

Previous version:
- OR chooses a neighbor graph.
- Risk: looks like heuristic feature selection.

OR-informed version:
- OR computes dual prices/multipliers from an explicit network optimization model.
- Neighbor graph/weights are marginal congestion values.
- DSL terms have economic/OR meaning.
- Easier to defend in Transportation Science.

## Proposed Method Skeleton

1. **Network relaxation**
   - Use store-and-forward or CTM-lite model.
   - Solve with AMPL/HiGHS offline or periodically.
   - Include queues, storage, turning ratios, approximate green allocation.

2. **Dual feature extraction**
   - Extract link/corridor shadow prices or Lagrange multipliers.
   - Discretize into interpretable bins: low/medium/high price; upstream/downstream price imbalance.

3. **Neighbor-aware DSL extension**
   - Add DSL atoms:
     - `NeighborQueue(direction, k)`
     - `DownstreamStorageSlack(link)`
     - `DualPrice(link)`
     - `PriceImbalance(upstream, downstream)`
     - `CorridorCriticality(route)`
   - Keep program small.

4. **Program search/recovery**
   - Option A: MCTS search in SUMO with price features.
   - Option B: recover from OR oracle labels.
   - Option C: hybrid: use oracle to seed/limit MCTS search.

5. **Deployment**
   - Online policy is symbolic and lightweight.
   - Prices can be precomputed by scenario or updated periodically.

## Key Baselines

- Fixed-time / Webster.
- Actuated.
- Max-pressure.
- C-MP if implementable or approximate competitor.
- Local PI-Light.
- Neighbor-state PI-Light without OR prices.
- All-neighbor PI-Light.
- Neural neighbor-aware baseline if feasible: CoordLight/GAT-MARL or simplified MARL.
- OR oracle on small networks.

## Minimal Experiment Package

### Experiment 1: Single-intersection sanity
- Dual/neighbor features absent or zero.
- Method reduces to local PI-Light.

### Experiment 2: 5-intersection arterial
- Directional platoon demand.
- Test corridor progression and queue balance.
- Expect strongest gains.

### Experiment 3: 4×4 grid
- Test whether price features prevent local overfitting and improve network throughput.

### Experiment 4: Demand shift / generalization
- Precompute prices under nominal demand; test under shifted demand.
- Compare robust vs non-robust price variants if time permits.

### Experiment 5: Ablation
- No price.
- Raw neighbor states.
- Random prices.
- OR dual prices.
- Oracle labels vs SUMO-search.

## Main Risks and Mitigations

1. **Dual prices are hard to compute online**
   - Mitigation: offline by demand regime, periodic update, or small LP only.

2. **Prices do not improve performance**
   - Mitigation: use oracle recovery to diagnose whether price features are predictive.

3. **Reviewer says this is reward shaping/feature engineering**
   - Mitigation: emphasize dual decomposition interpretation and ablations against raw/all/random neighbor features.

4. **Too much OR complexity**
   - Mitigation: keep LP model simple and use it only to generate interpretable signals, not as the online controller.

## Final Ranking

| Rank | Idea | Keep? | Role |
|---:|---|---|---|
| 1 | Dual-Price π-Light | Yes | Main method |
| 2 | Lagrangian-Decomposed π-Light | Yes | Theoretical framing |
| 3 | Store-and-Forward Oracle → DSL | Yes | Validation / certificate |
| 4 | Network-Flow Critical Corridor π-Light | Maybe | Simple baseline/ablation |
| 5 | ADMM-Message π-Light | Later | Advanced extension |
| 6 | Robust Dual-Price π-Light | Later | Generalization extension |

## Recommended Phase 3 Novelty Checks

1. **Dual-price / shadow-price features for interpretable traffic signal DSL policies**.
2. **Lagrangian-decomposed programmatic RL for multi-intersection TSC**.
3. **Store-and-forward OR oracle distillation into neighbor-aware symbolic traffic signal rules**.

## Updated Working Titles

1. **Dual-Price π-Light: OR-Guided Interpretable Programs for Coordinated Traffic Signal Control**
2. **Shadow-Price Guided Programmatic Signal Control for Multi-Intersection Networks**
3. **From OR Prices to Interpretable Traffic Signal Programs**
4. **Neighbor-Aware π-Light via Lagrangian Coordination Signals**

## Bottom Line

After incorporating Obsidian OR material, the best PI-Light+OR combination is no longer a generic coordination graph. It is:

> **Use OR dual prices / Lagrangian coordination signals as interpretable neighbor features inside PI-Light’s DSL.**

This gives a clear Transportation Science identity: not black-box MARL, not pure max-pressure, not pure OR/MPC, but a deployable symbolic controller whose coordination terms come from optimization theory.
