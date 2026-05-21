# Review Summary — Phase 3/4 to Phase 4.5

**Date**: 2026-05-20

## Phase 3 Novelty Result

The idea survived novelty checking only under a narrowed claim:

> dual/shadow-price-conditioned symbolic DSL recovery for neighbor-aware coordination.

What is not novel enough alone:
- symbolic/interpretable traffic signal control,
- neighbor-aware multi-intersection coordination,
- Lagrangian multipliers in RL,
- max-pressure-like marginal-congestion logic,
- generic store-and-forward/MPC signal optimization.

Most dangerous prior-work clusters:
- PI-Light / π-eLight / SymLight / GP symbolic TSC / EvolveSignal / SignalClaw,
- CoordLight / neighbor-aware MARL,
- C-MP / coordinated max-pressure / capacity-aware backpressure,
- safe/constrained RL with Lagrange multipliers,
- OracleTSC and policy distillation.

## Phase 4 External Review Result

External review score:
- broad version: 5.5/10,
- hard-narrowed version: around 7/10 for EJOR,
- TS remains difficult.

The strongest rejection argument:

> The paper just combines known symbolic TSC, neighbor-aware coordination, max-pressure intuition, MPC/store-and-forward, and policy distillation. The claimed dual prices are merely queue-difference/downstream-slack features in disguise, not a new OR control principle.

## User Framing Correction

The user clarified that the paper should not be framed primarily as an extension of PI-Light. The correct framing is broader:

> an extension of programmatically interpretable RL/control or symbolic programmatic control into network traffic signal control using OR dual-sensitivity guidance.

PI-Light remains:
- prior work,
- a baseline,
- a code/DSL reference,
- an example of the broader programmatic-control family.

## Method Refinement Decision

Adopt a single fixed technical route:

1. continuous store-and-forward / CTM-lite LP/QP relaxation,
2. rigorous dual sensitivity extraction,
3. DSL atoms mapped to OR constraints/sensitivities,
4. sparse MIP symbolic recovery,
5. oracle-regret objective plus complexity and neighbor penalties,
6. closed-loop SUMO validation against MP/C-MP/MPC/programmatic baselines.

Reject unresolved menus of MILP/CP-SAT/column generation/bilevel alternatives.

## Validation Priorities

Must validate:
- dual sensitivities are meaningful,
- dual-guided atoms beat raw/all/random/local atoms at equal complexity,
- recovered policies have low oracle regret and good closed-loop performance,
- finite storage/spillback cases expose value beyond ordinary pressure,
- runtime remains CPU-feasible.
