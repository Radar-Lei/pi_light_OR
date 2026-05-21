# Phase 2 Idea Report — PI-Light + OR Neighbor-Aware Coordination

**Date**: 2026-05-19
**Direction**: PI-Light + OR hybrid for single- and multi-intersection signal control, where each intersection may observe neighboring intersections' traffic states.
**Landscape input**: `LITERATURE_LANDSCAPE_NEIGHBOR_OR.md`
**Ideas evaluated**: 10 generated → 5 retained → 2 primary recommendations → pilots not yet run

## Executive Summary

The strongest direction is not “max-pressure with certification” and not “neural neighbor-aware MARL.” It is:

> **OR-guided, neighbor-aware PI-Light programs**: compact symbolic priority rules that use local and selected neighboring-intersection states, where OR supplies the coordination graph, corridor modes, weights, constraints, or oracle labels.

Recommended top idea:

> **Coordination-Graph PI-Light (CG-πLight)** — build an OR-derived coordination graph over intersections, augment the PI-Light DSL with interpretable neighbor terms, and search/recover compact programs that coordinate arterial/grid signals better than local PI-Light and max-pressure while remaining deployable.

Backup/co-primary idea:

> **OR-Oracle Distillation to Neighbor-Aware DSL** — use AMPL to solve small rolling-horizon multi-intersection coordination problems, then recover a compact neighbor-aware PI-Light program with action-disagreement and performance-gap certificates.

## Ranked Ideas

### Idea 1: Coordination-Graph PI-Light (CG-πLight) — RECOMMENDED

**One-sentence summary**: Extend PI-Light from local DSL rules to neighbor-aware symbolic programs by using an OR-derived coordination graph to decide which neighboring states enter each intersection's priority rule.

**Core mechanism**:
- Build a directed coordination graph among intersections.
- Edge weights encode OR-derived coupling: platoon travel time, downstream storage dependency, shared corridor progression, or queue-spillback sensitivity.
- Each local PI-Light program can use features from selected graph neighbors:
  - upstream queue / approaching platoon count,
  - downstream occupancy / storage slack,
  - neighbor current phase,
  - estimated arrival time window,
  - corridor priority mode.
- Program still outputs movement/phase priority and remains compact.

**OR role**:
- Not replacing MCTS.
- OR selects the coordination skeleton: edges, weights, or admissible neighbor features.
- Possible OR formulations:
  1. shortest-path / travel-time coupling graph,
  2. min-cost flow sensitivity graph,
  3. store-and-forward LP dual/shadow-price graph,
  4. arterial progression graph.

**Hypothesis**:
A small OR-selected neighbor feature set gives most of the coordination benefit of neural MARL, while preserving PI-Light’s interpretability and deployability.

**Minimum viable experiment**:
- Single intersection: should reduce to local PI-Light.
- 5-intersection arterial: show progression/platoon benefit.
- 4×4 grid: show network-level benefit.
- Compare local-only PI-Light vs neighbor-augmented PI-Light with random neighbors vs OR-selected coordination graph.

**Expected contribution type**: New method + empirical + interpretability/diagnostic.

**Novelty**: 8/10 before deep check.
Closest works: PI-Light/SymLight for symbolic policies; CoordLight/GAT-MARL for neighbor-aware neural policies; C-MP/coordination graph/offset methods for OR coordination. The exact combination “OR-derived neighbor graph + compact PI-Light DSL” appears open.

**Feasibility**: HIGH-MEDIUM.
- Requires modifying PI-Light feature extraction and DSL.
- OR graph can start simple: edge if travel time < threshold or if downstream road receives flow.
- No GPU required for initial pilots.

**Risk**: MEDIUM.
- If OR graph is too simple, reviewer may call it heuristic feature engineering.
- Need ablation showing OR-selected neighbors beat all-neighbors/random-neighbors.

**Pilot signal target**:
- +5–10% travel time improvement over local PI-Light or max-pressure on arterial/grid.
- Better throughput/queue balance under directional demand.
- Smaller program than neural MARL with competitive performance.

**Why we should do this**:
This best matches the user’s preference: PI-Light remains central, OR genuinely adds multi-intersection coordination, and neighbor state information is used in an interpretable way.

---

### Idea 2: OR-Oracle Distillation to Neighbor-Aware DSL — RECOMMENDED / CO-PRIMARY

**One-sentence summary**: Solve rolling-horizon multi-intersection coordination subproblems with AMPL, then distill the resulting actions into compact PI-Light-style programs using local and neighbor features.

**Core mechanism**:
- Sample traffic states from SUMO.
- For small networks, solve an AMPL coordination oracle:
  - finite-horizon store-and-forward or CTM-lite model,
  - objective: total delay, queue balance, corridor progression, spillback avoidance,
  - constraints: min green, yellow loss, phase feasibility.
- Use the oracle action labels to search/recover a neighbor-aware DSL rule.
- Deploy the recovered rule online without solving AMPL.

**OR role**:
- OR provides labels and a performance upper bound.
- Also provides a certificate: disagreement rate, oracle regret proxy, or objective gap.

**Hypothesis**:
Multi-intersection OR decisions are often compressible into shallow neighbor-aware symbolic rules, especially on arterial/grid networks with repeated structure.

**Minimum viable experiment**:
- One intersection: prove pipeline works.
- 2×2 grid: solve oracle states, recover K=1/K=2 DSL rules.
- 5-intersection arterial: test transfer and deployment in SUMO.

**Expected contribution type**: Method + diagnostic + certification.

**Novelty**: 8/10 before deep check.
Closest works: PIRL/VIPER distillation, PI-Light direct search, MPC/RL hybrid signal control. Direct “OR oracle → neighbor-aware PI-Light DSL → certificate” seems less crowded.

**Feasibility**: MEDIUM.
- Requires AMPL model and state sampling.
- Easier to write a strong OR story than Idea 1, but implementation is heavier.

**Risk**: MEDIUM.
- Oracle may not scale; mitigate by using it offline for labels/weights only.
- DSL may fail to match oracle; this can still be a useful diagnostic but weakens method claim.

**Pilot signal target**:
- >85–90% oracle action agreement on sampled small-network states, or clear low-regret structure.
- Recovered DSL beats local PI-Light/max-pressure in SUMO.

**Why we should do this**:
This is the cleanest OR+PI-Light bridge: OR creates coordinated intelligence; PI-Light compresses it into deployable interpretable rules.

---

### Idea 3: Green-Wave-Aware PI-Light Programs

**One-sentence summary**: Use OR to compute corridor progression windows/offset modes, then let PI-Light learn symbolic rules for when to follow, extend, or break green-wave coordination based on local and neighbor states.

**Core mechanism**:
- OR computes desired offset/progression plan for a corridor.
- DSL includes features such as expected platoon arrival, neighbor phase, time-to-arrival, corridor mode, and queue imbalance.
- The symbolic program can override green-wave when side-street queues or spillback become critical.

**OR role**:
- Computes progression bands or offset targets.
- Defines corridor coordination modes.

**Hypothesis**:
Static/adaptive offsets are too rigid; PI-Light-style rules can make corridor coordination state-responsive while remaining explainable.

**Minimum viable experiment**:
- 5-intersection arterial with directional demand waves.
- Baselines: fixed offset, adaptive offset, max-pressure, C-MP, local PI-Light, green-wave-aware PI-Light.

**Expected contribution type**: Method + empirical.

**Novelty**: 7/10.
There is much offset/green-wave/RL work, including hybrid model-based/RL coordination. Novelty depends on symbolic deployable PI-Light rules and clear OR-derived modes.

**Feasibility**: HIGH.
Arterial progression is easier than full-grid coordination.

**Risk**: MEDIUM-HIGH.
May look like a corridor-specialized paper rather than general network control.

**Verdict**: Strong backup or experimental subcase for Idea 1.

---

### Idea 4: Two-Level OR Coordinator + PI-Light Local Agents

**One-sentence summary**: A high-level OR coordinator assigns corridor/network modes, constraints, or weights; low-level PI-Light programs choose phases locally using those signals plus neighbor states.

**Core mechanism**:
- High level every T seconds solves a lightweight OR problem:
  - choose active corridors,
  - assign intersection modes,
  - allocate green budgets or phase restrictions,
  - set weights for local DSL rules.
- Low-level PI-Light rules execute every signal decision interval.

**OR role**:
- Online or periodic network coordinator.

**Hypothesis**:
A slow OR coordinator plus fast symbolic local agents gives the performance of model-based control with better deployability and robustness than neural MARL.

**Minimum viable experiment**:
- 5-intersection arterial and 4×4 grid.
- Compare against OR-only MPC, local PI-Light, and MARL.

**Expected contribution type**: System/method.

**Novelty**: 6.5/10.
Closest work: hierarchical model-based/RL signal coordination. Difference is interpretable PI-Light local policy, but the high-level/low-level structure itself is known.

**Feasibility**: MEDIUM.
More engineering complexity than Ideas 1–3.

**Risk**: HIGH.
May become an OR/MPC paper with PI-Light as a component rather than the central method.

**Verdict**: Keep as architecture inspiration, not first choice.

---

### Idea 5: Network-Aware Objective for PI-Light Search

**One-sentence summary**: Keep the PI-Light DSL local or neighbor-augmented, but change its search objective from average travel time to an OR-shaped network objective that rewards coordination, progression, and spillback avoidance.

**Core mechanism**:
- Modify MCTS evaluation reward to include:
  - total travel time,
  - corridor progression penalty,
  - downstream spillback penalty,
  - queue imbalance penalty,
  - platoon delay penalty.
- OR provides the objective terms/weights.
- The final controller is still a compact program.

**OR role**:
- Objective design and weighting; possibly dual weights from a relaxation.

**Hypothesis**:
A better network-aware objective may produce coordinated symbolic rules without increasing online policy complexity.

**Minimum viable experiment**:
- Run PI-Light search under different objectives on arterial/grid.
- Compare learned programs and deployment metrics.

**Expected contribution type**: Empirical/method.

**Novelty**: 6/10.
Could be seen as reward shaping unless tied to an OR derivation.

**Feasibility**: HIGH.
Likely easiest to implement.

**Risk**: MEDIUM.
If performance gains are small, contribution is weak.

**Verdict**: Good pilot/ablation, not main thesis.

## Eliminated / Deprioritized Ideas

| Idea | Reason |
|---|---|
| Neural attention PI-Light | Loses interpretability and competes directly with CoordLight/GAT-MARL. |
| Pure OR/MPC online controller | Loses PI-Light identity and deployability story. |
| Add all neighbor states to PI-Light DSL | Too close to generic state augmentation; no OR contribution. |
| Max-pressure-only coordinated variant | Conflicts with user preference; C-MP and related work are strong. |
| LLM-generated neighbor rules | Crowded by SignalClaw/EvolveSignal and weak OR contribution unless paired with OR oracle/certification. |

## Recommended Path

### Primary paper direction

**Coordination-Graph PI-Light: OR-Guided Neighbor-Aware Symbolic Programs for Multi-Intersection Signal Control**

Core claims:
1. Original PI-Light is local; this extends it to network-aware symbolic programs.
2. OR chooses the coordination graph / neighbor terms, avoiding black-box neural attention.
3. The resulting program is compact, interpretable, and deployable.
4. It improves over local PI-Light, max-pressure/C-MP, and selected neural neighbor-aware baselines in SUMO.

### Co-primary / validation component

**OR-oracle distillation** should be used to justify that the selected neighbor terms are meaningful and to produce an upper-bound/diagnostic on small networks.

## Pilot Plan

### Pilot 1 — OR-selected neighbors vs all/random/no neighbors

- Network: 5-intersection arterial.
- Controllers:
  1. Local PI-Light-style rule.
  2. PI-Light with all neighbor features.
  3. PI-Light with random neighbor features.
  4. CG-πLight with OR-selected neighbor features.
  5. Max-pressure / C-MP baseline.
- Demand: balanced, directional peak, oversaturated downstream bottleneck.
- Metrics: travel time, throughput, queue spillback, number of stops, arterial progression speed.
- Success: OR-selected neighbor DSL beats local/all/random neighbor variants and max-pressure on at least directional/bottleneck scenarios.

### Pilot 2 — OR oracle recoverability

- Network: 2×2 grid.
- Generate sampled states from SUMO.
- Solve small AMPL oracle for coordinated phases.
- Search K=1/K=2 neighbor-aware DSL rules.
- Metrics: oracle agreement, rule complexity, deployed SUMO performance.
- Success: compact rule reaches high agreement or low regret against oracle.

### Pilot 3 — Single-intersection sanity

- Show CG-πLight reduces to PI-Light/local rule when no coordination edges exist.
- This prevents reviewers from claiming the method only works by adding network-specific hacks.

## Suggested Phase 3 Novelty Checks

Run deep novelty check on:
1. **Coordination-Graph PI-Light / OR-selected neighbor feature DSL**.
2. **OR oracle distillation to neighbor-aware PI-Light DSL**.
3. **Green-wave-aware symbolic PI-Light programs** if arterial coordination becomes the preferred paper angle.

## Working Title Options

1. **Coordination-Graph π-Light: OR-Guided Interpretable Programs for Network Traffic Signal Control**
2. **Neighbor-Aware Programmatic Signal Control via OR-Guided Coordination Graphs**
3. **From Local Rules to Network Coordination: OR-Guided π-Light for Multi-Intersection Signal Control**
4. **Interpretable Neighbor-Aware Priority Programs for Coordinated Traffic Signal Control**

## Current Recommendation

Proceed to Phase 3 with Idea 1 and Idea 2 together, because they are complementary:

- Idea 1 is the deployable method.
- Idea 2 is the OR justification/certification bridge.

If novelty check shows Idea 1 is too close to CoordLight/C-MP/coordination graph work, pivot to Idea 2 as the main contribution.
