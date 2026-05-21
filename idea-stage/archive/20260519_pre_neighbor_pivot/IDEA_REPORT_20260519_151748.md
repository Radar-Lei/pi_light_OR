# Research Idea Report — PI-Light OR / Transportation Science

**Direction**: OR-certified interpretable priority rules for signalized networks, with throughput/stability guarantees under finite storage and realistic phase constraints.
**Generated**: 2026-05-19
**Pipeline stage**: idea-discovery Phase 2
**Ideas evaluated**: 10 generated → 5 survived filtering → 3 recommended for deep novelty/review → pilots not launched yet

## Executive Summary

The strongest Transportation Science path is to reposition PI-Light from “symbolic policy search” to “deployable priority-rule control with OR certification.” The paper should not claim novelty from another DSL/MCTS/MIP search method. Its center should be a constrained max-pressure-style rule class that can be interpreted as PI-Light-like DSL programs, certified under finite storage and realistic phase constraints, and validated in SUMO.

Recommended top idea:

> **Constrained Interpretable Max-Pressure Rules (CIMPR): a PI-Light-compatible priority-rule class with stability/capacity certificates under finite storage and realistic phase constraints.**

This is the best blend of OR contribution, PI-Light continuity, feasible SUMO implementation, and TS reviewer appeal.

## Landscape Summary

PI-Light already shows that compact lane-link priority programs can beat many DRL baselines and transfer across networks. However, the interpretable TSC space has become crowded: PI-eLight, SymLight, TPET, EvolveSignal, GPLight+, and SignalClaw all compete on symbolic/evolutionary/LLM-discovered policies. A new paper cannot rely on “we search better interpretable rules” as the primary claim.

The OR opening is max-pressure theory. Classic max-pressure has stability/throughput foundations, but practical deployment imposes finite downstream storage, spillback, minimum green, yellow loss, phase ordering, NEMA/ring-barrier constraints, and pedestrian conflicts. Existing constrained/cyclical/capacity-aware MP variants address pieces of this, but they do not connect to compact PI-Light-style rule recovery and certification.

SUMO and AMPL make this feasible. SUMO can test realistic constraints and spillback; AMPL/HiGHS can solve oracle/certification LP/MILP models. The paper should use optimization not as a replacement for MCTS, but as a way to derive, certify, and explain deployable priority rules.

## Recommended Ideas

### Idea 1: Constrained Interpretable Max-Pressure Rules (CIMPR)

- **One-sentence summary**: Define a PI-Light-compatible priority-rule class that extends max-pressure with finite-storage and realistic phase-constraint terms, then prove/certify stability over the constrained capacity region.
- **Core hypothesis**: A compact rule using incoming queues, downstream occupancy/storage slack, and phase-switching feasibility can preserve most of max-pressure’s throughput advantage while satisfying deployable signal constraints.
- **Minimum viable experiment**: Implement single-intersection and arterial SUMO scenarios with finite link capacities, min-green/yellow constraints, and spillback; compare classic MP, constrained/cyclical MP, PI-Light rule, and CIMPR across demand ratios.
- **Expected contribution type**: Theory + method + empirical validation.
- **Novelty quick-check**: 8/10. Closest work: Varaiya-style MP, capacity-aware MP, cyclical phase MP, MPC with stability guarantees. Differentiation: compact interpretable DSL-compatible rule plus OR certification under deployment constraints.
- **Feasibility**: HIGH. Can start from existing max-pressure and PI-Light rule code; SUMO implementation is CPU-only; AMPL used for certification/oracle, not full online control.
- **Risk**: MEDIUM. The full theorem may be hard; fallback is a certification procedure plus a weaker theorem for a constrained network class.
- **Pilot result**: SKIPPED — pilot should be CPU/SUMO, not GPU. Proposed pilot: 2×2 grid, 4 demand levels, 3 seeds, test queue growth slope and throughput.
- **Reviewer’s likely objection**: “This is just another max-pressure variant.”
- **Answer to objection**: The paper must emphasize the rule-class/certificate bridge: max-pressure theory → finite-storage/phase-constrained deployment → interpretable PI-Light-style programs.
- **Why we should do this**: It is the cleanest TS story and directly converts PI-Light’s empirical rule search into an OR-certified control framework.

### Idea 2: Optimization-Certified DSL Recovery from a Constrained MP/MPC Oracle

- **One-sentence summary**: Use AMPL to solve a constrained MP/MPC oracle offline, then recover the simplest PI-Light DSL rule that matches oracle decisions with a certificate of disagreement and cost loss.
- **Core hypothesis**: In realistic networks, most oracle decisions can be represented by very shallow priority rules; the remaining disagreement can be bounded or localized to high-congestion boundary states.
- **Minimum viable experiment**: Generate state-action pairs from AMPL oracle on small networks; fit/search DSL rules; report oracle agreement, travel time loss, throughput loss, and complexity frontier.
- **Expected contribution type**: Method + diagnostic + certification.
- **Novelty quick-check**: 7/10. Closest work: PI-Light/MCTS, VIPER/policy distillation, PIRL, MPC-based signal control. Differentiation: exact OR oracle plus formal mismatch/cost certificate rather than black-box imitation.
- **Feasibility**: MEDIUM-HIGH. Requires building oracle datasets and a DSL-fitting/certification layer; can reuse PI-Light DSL machinery.
- **Risk**: MEDIUM. If oracle decisions are too complex, shallow DSL may underfit. But that negative result is still publishable as a diagnostic about deployability limits.
- **Pilot result**: SKIPPED. Proposed pilot: one 4-way intersection with 4 phases, enumerate/random-sample queue states, solve oracle, test K=1/K=2 DSL recovery.
- **Reviewer’s likely objection**: “Distillation is not new.”
- **Answer to objection**: The novelty must be framed as OR-certified rule recovery with capacity/phase constraints, not generic imitation learning.
- **Why we should do this**: It creates a direct bridge from AMPL/OR to PI-Light DSL and provides strong evidence for why simple rules are enough.

### Idea 3: Finite-Storage Effective Pressure with Interpretable Spillback Penalties

- **One-sentence summary**: Derive an effective pressure formula that penalizes downstream occupancy/storage risk, then restrict it to a PI-Light-style interpretable rule and test whether it prevents spillback without sacrificing throughput.
- **Core hypothesis**: PI-Light’s use of outgoing-lane vehicle count is an empirical version of a finite-storage shadow price; a principled storage-slack penalty should outperform classic MP under spillback-heavy demand.
- **Minimum viable experiment**: Build SUMO networks with short downstream links and high turning demand; compare classic MP, capacity-aware MP, PI-Light learned rule, and effective-pressure rule.
- **Expected contribution type**: Method + empirical + partial theory.
- **Novelty quick-check**: 6.5/10. Closest work: capacity-aware back-pressure, enhanced queue-based MP, finite-storage MPC. Differentiation must rely on interpretable DSL deployment and SUMO realism.
- **Feasibility**: HIGH. Easy to implement once SUMO lane storage and downstream occupancy are exposed.
- **Risk**: MEDIUM-HIGH. Recent capacity-aware/enhanced MP papers may be close; needs sharp differentiation.
- **Pilot result**: SKIPPED. Proposed pilot: one arterial with a short downstream bottleneck; success if rule reduces blocked departures/spillback and queue growth.
- **Reviewer’s likely objection**: “Finite-storage MP already exists.”
- **Answer to objection**: Position this as a component within CIMPR or as an empirical/theoretical sub-claim, not the whole paper.
- **Why we should do this**: It is a strong experimental ingredient and likely necessary for the top idea.

### Idea 4: Realistic Phase-Constraint Capacity Region and Rule Certification

- **One-sentence summary**: Characterize the capacity region induced by min-green, yellow loss, phase order, and NEMA-like constraints, then certify whether an interpretable priority rule stabilizes demands inside that region.
- **Core hypothesis**: Much of the apparent gap between learned rules and max-pressure comes from ignoring the reduced feasible service region under realistic phases; explicitly modeling this region yields fairer comparisons and better rules.
- **Minimum viable experiment**: Compare ideal MP, min-green MP, cyclical MP, and certified constrained rules on identical demand points inside/outside the constrained region.
- **Expected contribution type**: Theory + diagnostic.
- **Novelty quick-check**: 7/10. Closest work: cyclical phase MP, cycle-based MP, MPC with NEMA constraints. Differentiation: capacity-region audit plus interpretable rule certification.
- **Feasibility**: MEDIUM. Needs careful mathematical modeling; implementation is manageable.
- **Risk**: HIGH if full characterization becomes too broad.
- **Pilot result**: SKIPPED. Proposed pilot: two-phase and four-phase toy networks where feasible service polytope can be computed exactly.
- **Reviewer’s likely objection**: “Too theoretical or too narrow.”
- **Answer to objection**: Use it as a theorem/certification layer supporting Idea 1 rather than a standalone paper unless the theorem is very clean.
- **Why we should do this**: It can provide the paper’s most OR-looking theoretical contribution.

### Idea 5: Network-Coupled Local Priority Rules via OR Shadow Prices

- **One-sentence summary**: Compute network-level shadow prices from an AMPL store-and-forward/CTM relaxation, then inject them into local interpretable priority rules to achieve coordination without online network optimization.
- **Core hypothesis**: A small number of link/phase shadow-price weights can coordinate local rules across arterials/grids and outperform purely local MP/PI-Light under directional waves and bottlenecks.
- **Minimum viable experiment**: Solve offline LP/dual weights for an arterial and 4×4 grid; deploy local rules with these weights in SUMO; compare against local MP, C-MP, and PI-Light shared rule.
- **Expected contribution type**: Method + empirical.
- **Novelty quick-check**: 7/10. Closest work: C-MP, multi-commodity signal/routing optimization, network-wide adaptive optimization. Differentiation: offline OR prices distilled into deployable local DSL rules.
- **Feasibility**: MEDIUM. More moving parts than Ideas 1–3.
- **Risk**: MEDIUM-HIGH. May be sensitive to demand and require periodic re-optimization.
- **Pilot result**: SKIPPED. Proposed pilot: 5-intersection arterial with directional peak demand; evaluate progression and queue imbalance.
- **Reviewer’s likely objection**: “This is just parameter tuning with LP weights.”
- **Answer to objection**: Need clear dual interpretation and robustness/generalization tests.
- **Why we should do this**: It is the strongest “signal coordination” story, but should probably be a secondary contribution unless early pilots are very strong.

## Eliminated or Deprioritized Ideas

| Idea | Reason eliminated/deprioritized |
|---|---|
| Pure “MIP replaces MCTS for PI-Light” | Too weak as a TS contribution; likely perceived as an implementation variant of PI-Light search. |
| Full ADMM + MARL for signal networks | Interesting but drifts away from PI-Light/DSL and would become a separate MARL paper. |
| Decision-focused flow prediction → signal optimization | Strong OR/ML topic but not tightly connected to PI-Light; requires prediction data and a different paper narrative. |
| Column generation for phase-plan discovery | Highly novel but problem mapping is underdeveloped and risky for current project timeline. |
| LLM/evolutionary symbolic rule search | Crowded by EvolveSignal, SignalClaw, GPLight+, TPET; weak TS fit unless paired with OR certificates. |

## Suggested Execution Order

1. **Start with Idea 1 (CIMPR)** as the main paper thesis.
2. Use **Idea 3** as the concrete finite-storage/spillback component inside Idea 1.
3. Use **Idea 4** as the theory/certification layer if the theorem can be made clean.
4. Keep **Idea 2** as the empirical bridge to PI-Light DSL recovery.
5. Consider **Idea 5** only if the paper needs a stronger “coordination” component after initial pilots.

## Immediate Pilot Plan

No GPU is required. The cheapest pilot should be CPU/SUMO:

### Pilot A — CIMPR sanity check
- Network: single intersection + 2×2 grid.
- Controllers: fixed-time, actuated, classic MP, min-green MP, PI-Light-style hand rule, CIMPR.
- Demand: 0.7×, 1.0×, 1.2×, 1.5× nominal demand.
- Seeds: 3.
- Metrics: throughput, average travel time, queue growth slope, blocked departures, phase switches.
- Positive signal: CIMPR matches MP under uncongested demand and beats MP/min-green MP under finite-storage spillback without unstable queue growth.

### Pilot B — DSL recovery from oracle
- Network: one intersection.
- Generate queue/storage states.
- Solve AMPL oracle with min-green/storage constraints.
- Fit K=1/K=2 DSL rule.
- Metrics: oracle action agreement, oracle regret proxy, rule complexity.
- Positive signal: shallow DSL reaches >90% oracle agreement or shows interpretable disagreement concentrated near capacity boundaries.

## Recommended Next Step

Proceed to Phase 3 deep novelty verification for the top 3 ideas:

1. CIMPR: constrained interpretable max-pressure rules.
2. OR-certified DSL recovery from constrained MP/MPC oracle.
3. Finite-storage effective pressure with spillback penalties.

If Phase 3 finds that Idea 3 is too close to existing capacity-aware/enhanced MP papers, fold it into Idea 1 as a component rather than treating it as the headline.
