# Focused Phase 1 Literature Landscape — PI-Light + OR + Neighbor-Aware Multi-Intersection Coordination

**Date**: 2026-05-19
**User-refined direction**: Keep the project centered on PI-Light + OR, but extend from single-intersection control to multi-intersection coordination. Each intersection may know neighboring intersections' traffic states. The goal is not to become a max-pressure paper, but to find a genuine PI-Light/OR hybrid mechanism for coordinated control.

## Position Shift from Previous Phase

Previous direction emphasized OR-certified priority rules and max-pressure-like guarantees. The refined direction is different:

- PI-Light should remain the method identity.
- OR should enhance PI-Light, not merely explain or certify max-pressure.
- Multi-intersection coordination is central; single-intersection remains a special case / ablation.
- Neighboring-intersection states are allowed, so the policy can go beyond the original PI-Light local DSL.
- Max-pressure should be a baseline/theoretical reference, not the name of the proposed method.

## Key Literature Clusters

### 1. Symbolic / programmatic TSC policies

Representative works:
- PI-Light (AAAI 2024): searches compact lane-link priority programs via DSL + MCTS. It is inspired by max-pressure structure but not a max-pressure controller. It uses local intersection features and a shared program.
- PI-eLight (IEEE TMC 2026), SymLight (arXiv/OpenReview 2025/2026), GPLight+, TPET, EvolveSignal, SignalClaw: recent symbolic/evolutionary/LLM-generated interpretable TSC policies.

Implication:
A new paper cannot simply say “we search symbolic rules.” The new contribution must be **network-aware symbolic programs** or **OR-guided symbolic coordination**.

### 2. Neighbor-aware / network-wide RL coordination

Representative works found:
- CoordLight (2026): decentralized network-wide TSC with neighbor-aware policy optimization; uses attention over adjacent agents' states/actions. Strong neighbor-aware MARL baseline, but not symbolic/interpretable and not OR-based.
- Multi-agent regional TSC with traffic-flow prediction and graph attention (2026): neighborhood-augmented state, adjacent-intersection reward, graph attention, MADDPG, SUMO/TraCI.
- Coordinated multi-intersection policy-regulated DQN (2026): multi-intersection coordination with spillback/neighbor influence in SUMO.
- HGAT/MARL multi-intersection TSC and related graph-attention MARL papers.

Implication:
Neighbor information is already common in neural MARL. The novelty cannot be “uses neighbor states.” The novelty must be: neighbor states are used inside **interpretable PI-Light-style programs** with **OR-derived coordination structure**.

### 3. OR/model-based signal coordination

Representative works:
- Hierarchical signal coordination and control using hybrid model-based + RL approach (2025): high-level coordinator selects Max-Flow Coordination or Green-Wave Coordination; lower-level PPO agents choose feasible phases in SUMO-RLlib.
- Offset/split coordination and arterial progression works, including adaptive offsets, green-wave coordination, and recent hybrid offset-split interdependency approaches.
- Classical traffic signal timing manuals and OR models for coordinated timing plans.
- Optimization-based coordinated signal control under variational/stochastic formulations.

Implication:
OR has a natural role in choosing **coordination structure**: offsets, progression bands, corridor priority, decomposition constraints, or shadow prices. This can guide the symbolic PI-Light policy rather than replacing it.

### 4. Decentralized coordination with local neighbor information

Representative works:
- C-MP (TRB 2025): decentralized adaptive-coordinated max-pressure using platoon priority; proves maximum stability; clear and strong competitor.
- Adaptive network partition / road partition methods (2024–2026): dynamically group intersections or encode multi-channel states.
- Coordination graph approaches and higher-order conflict graph approaches.
- Self-organizing traffic signals with secondary extension and dynamic coordination.

Implication:
There is an opportunity to define a **coordination graph for symbolic rules**: each local program sees selected neighbor states, but OR decides which neighbor terms matter and how they enter.

## Structural Gap

Existing work tends to occupy one of three corners:

1. **Symbolic/interpretable but mostly local**: PI-Light/SymLight-style policies.
2. **Neighbor-aware but neural**: CoordLight, GAT/MARL, DQN coordination.
3. **OR/model-based coordination but not compact symbolic PI-Light programs**: offset/green-wave/MPC/hierarchical coordination.

The open gap is the triangle center:

> **OR-guided, neighbor-aware, interpretable PI-Light-style programs for multi-intersection signal coordination.**

## What “OR + PI-Light” Could Mean Here

Not recommended:
- OR simply replaces MCTS.
- OR only certifies a max-pressure baseline.
- PI-Light is reduced to compression of an OR controller without performance upside.

Recommended meanings:

1. **OR designs the coordination skeleton**
   - Which neighbors are relevant?
   - Which routes/corridors receive priority?
   - Which offset/progression constraints should local rules respect?
   - Which phase restrictions should apply under congestion regimes?

2. **PI-Light learns/exposes the local symbolic execution rule**
   - A DSL program maps local + neighbor features to movement/phase priorities.
   - The program stays compact and deployable.
   - Neighbor terms are interpretable, e.g., upstream arrival pressure, downstream storage slack, corridor platoon urgency.

3. **AMPL/SUMO provide oracle and validation**
   - AMPL can solve small/medium coordination subproblems or generate labels/weights.
   - SUMO tests whether the local symbolic rules coordinate better than local-only PI-Light, max-pressure, and neural MARL baselines.

## Most Promising Problem Anchor

**Neighbor-aware PI-Light programs with OR-derived coordination terms for multi-intersection signal control.**

One-sentence thesis:

> We extend PI-Light from local interpretable priority programs to neighbor-aware coordinated programs by using OR models to select/weight the neighbor information that should enter each intersection's DSL rule, yielding deployable symbolic policies that coordinate across networks while remaining interpretable.

## Candidate Mechanisms to Explore in Phase 2

1. **OR-Guided Neighbor Feature Selection**
   - Use an OR model/dual sensitivity/coordination graph to decide which upstream/downstream neighbor states enter each DSL rule.
   - PI-Light searches over a smaller, structured neighbor-augmented DSL.

2. **Coordination-Graph PI-Light**
   - Build a graph of intersection couplings via OR or traffic-flow sensitivity.
   - Local DSL rules include terms from graph-neighbor queues, phase states, platoon arrivals, and downstream storage.

3. **Green-Wave / Offset-Aware Symbolic Programs**
   - OR computes corridor offsets or progression windows.
   - PI-Light DSL learns when to follow or break coordination based on local/neighbor states.

4. **OR Oracle Distillation to Neighbor-Aware DSL**
   - AMPL solves a rolling-horizon multi-intersection coordination problem on sampled states.
   - A DSL rule is recovered that approximates the oracle using local + neighbor features.

5. **Two-Level Hybrid: OR Coordinator + PI-Light Local Agents**
   - High-level OR coordinator sets mode/constraints/weights for corridors.
   - Low-level PI-Light symbolic agents choose phases.

6. **Network-Aware Reward/Objective for PI-Light Search**
   - Instead of changing online policy only, change the search objective to include corridor delay, platoon progression, spillback avoidance, or network balance.
   - Still returns a compact program.

## Key Risks

- If the method uses a neural attention mechanism, it competes directly with CoordLight/GAT-MARL and loses interpretability.
- If the method is only an OR/MPC controller, it loses PI-Light identity.
- If the method only adds neighbor features without OR structure, it is too close to standard MARL state augmentation.
- If it only matches max-pressure, it is not strong enough; it should show performance upside versus max-pressure and local-only PI-Light.

## Recommended Phase 2 Search Space

Generate ideas under this template:

- Policy form: compact symbolic DSL program.
- Inputs: local lane/link features + selected neighbor state features.
- OR role: feature selection, weights, oracle labels, coordination constraints, corridor modes, or objective shaping.
- Output: phase/movement priority at each intersection.
- Experiments: single intersection, 5-intersection arterial, 4×4 grid, and larger real network if available.
- Baselines: fixed-time, actuated, max-pressure, C-MP, local PI-Light, neighbor-state neural MARL such as CoordLight/GAT-MARL where feasible, OR/MPC oracle on small networks.

## Sources to cite/check further

- PI-Light: https://ojs.aaai.org/index.php/AAAI/article/view/30103
- SymLight: https://arxiv.org/abs/2511.05790
- CoordLight: https://arxiv.org/abs/2603.24366
- Real-Time Network-Level TSC explicit multiagent coordination: https://arxiv.org/abs/2306.08843
- Hierarchical hybrid model-based/RL signal coordination: https://arxiv.org/abs/2508.20102
- C-MP: https://arxiv.org/abs/2407.01421
- Coordinated multi-intersection policy-regulated DQN: https://www.mdpi.com/2071-1050/18/3/1510
- Adaptive offsets for arterial intersections: https://arxiv.org/abs/2008.02691
- Large-scale traffic signal offset optimization: https://arxiv.org/abs/1911.08368
