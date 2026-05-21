# Phase 4 External Critical Review — Dual-Price DSL Synthesis

**Date**: 2026-05-20  
**Reviewer backend**: Codex CLI (`gpt-5.5`, xhigh reasoning, read-only)  
**Trace**: `.aris/traces/research-review/20260520_run01/`  
**Candidate**: Dual-Price DSL Synthesis for Coordinated π-Light

## Bottom-Line Review

The reviewer was cold on the current broad version:

- **Current score**: **5.5/10**
- **If narrowed hard**: **~7/10 for EJOR**, while **Transportation Science remains difficult**
- **Recommendation**: **Proceed, but narrow hard**

The present version looks like a combination of known ingredients:

- π-Light DSL / symbolic TSC,
- neighbor-aware coordination,
- OR dual features,
- MIP replacing MCTS,
- store-and-forward/MPC traffic control.

The idea becomes defensible only if reframed as:

> **Continuous network-relaxation dual sensitivity guiding π-Light-style symbolic policy recovery.**

## Strongest Rejection Argument

> The paper just combines known symbolic TSC, neighbor-aware coordination, max-pressure intuition, MPC/store-and-forward, and policy distillation. The claimed dual prices are merely queue-difference/downstream-slack features in disguise, not a new OR control principle.

Secondary rejection risks:

1. If duals come from a MILP with discrete phase decisions, the shadow-price interpretation is invalid or at least highly fragile.
2. If duals come from a continuous relaxation, the paper must justify why they remain meaningful for discrete SUMO phase control.
3. Without a clear relation to C-MP, cyclic/max-pressure, and MPC oracle baselines, the method may look weaker than established OR traffic control.
4. Without theory or regret, DSL recovery becomes classification/distillation rather than OR.

## Required Narrowing

Remove the method menu. Do **not** offer MILP/CP-SAT/column generation/bilevel as parallel unresolved options.

Fix the technical core to:

1. **Continuous store-and-forward / CTM-lite LP or QP relaxation**.
2. **Well-defined dual sensitivity** for links/corridors/storage/downstream supply.
3. **Dual-to-movement marginal-benefit lemma**: price imbalance gives a first-order signal for serving a movement.
4. **Pressure special case**: under simplified assumptions, the rule reduces to max-pressure/backpressure-like control.
5. **Sparse MIP DSL recovery** with objective:
   - oracle regret or value approximation,
   - program complexity penalty,
   - neighbor-count penalty.

## OR Component Requirements

The OR contribution is substantive only if:

- duals are extracted from a **continuous convex relaxation**, not from a phase-integer MILP;
- each DSL atom maps to a specific OR constraint or sensitivity;
- recovery optimizes regret/value, not merely action-label accuracy;
- the paper proves or empirically validates the dual sensitivity semantics;
- experiments show dual-guided DSL beats raw-neighbor, all-neighbor, random/permuted-price, and local-only DSL at the same program complexity.

## Mandatory Experiments

Must-have experiments:

1. **Single-intersection sanity**  
   Neighbor/dual features vanish; method should reduce to local PI-Light-style behavior and not degrade.

2. **5-intersection arterial**  
   Main coordination/platoon scenario; should show the strongest gain.

3. **4×4 grid**  
   Demonstrates the method is not just a corridor heuristic.

4. **Demand shift / generalization**  
   Train or synthesize prices under one regime; test on changed regimes, including peak reversal, oversaturation, and turning-ratio error.

5. **Strong baselines**  
   Webster/fixed-time, actuated, max-pressure, C-MP or approximate C-MP, MPC/OR oracle on small scale, local π-Light, neighbor π-Light without duals, raw-neighbor DSL, all-neighbor DSL, random/permuted-price DSL.

6. **Oracle gap and closed-loop performance**  
   Report regret, not only action agreement. Also report SUMO delay/travel time, queue spillback, throughput.

7. **Runtime and statistics**  
   AMPL/HiGHS solve time, synthesis time, online latency, multi-seed confidence intervals, paired tests.

Optional experiments:

- 100+ intersection large scale,
- GPU-heavy MARL,
- emissions/fuel,
- LLM/evolutionary synthesis comparison.

## Revised Positioning

Avoid:

- “new coordinated PI-Light framework”,
- “dual-price features for traffic control” without formal sensitivity,
- “MIP/CP-SAT/column-generation/bilevel synthesis” as a menu,
- “better than max-pressure” unless directly demonstrated.

Use:

> **OR dual sensitivity guided symbolic recovery for deployable network signal control.**

Suggested title directions:

1. **Dual-Sensitivity-Guided Symbolic Recovery for Neighbor-Aware Traffic Signal Control**
2. **Recovering π-Light-Style Network Signal Policies from Store-and-Forward Dual Sensitivities**
3. **OR-Guided Symbolic Signal Control under Network Spillback**

## Concrete Revision Plan

1. Delete unresolved method alternatives; keep continuous LP/QP relaxation + dual extraction + sparse MIP DSL recovery.
2. Map every DSL atom to an OR model constraint; delete atoms that cannot be mapped.
3. Write a pressure special-case result: when the method equals ordinary max-pressure and when finite storage/spillback creates extra terms.
4. Center experiments on arterial coordination, grid spillback, and demand shift.
5. Prioritize C-MP/MP/MPC/π-Light baselines over MARL baselines.
6. Reframe the contribution from “stronger controller” to “interpretable OR sensitivity surrogate for deployable symbolic control.”

## Phase 4 Decision

**Proceed, but narrow further before Phase 4.5 method refinement.**

Do not feed the broad Phase 2 method into refinement. Feed the narrowed technical core:

> Continuous store-and-forward/CTM-lite dual sensitivities → mapped DSL atoms → sparse MIP recovery minimizing oracle regret and complexity → SUMO validation against MP/C-MP/MPC/π-Light and dual ablations.
