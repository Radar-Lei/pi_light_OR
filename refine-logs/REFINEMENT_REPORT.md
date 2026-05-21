# Refinement Report — Phase 4.5

**Date**: 2026-05-20

## Gate Check

**Final method thesis**: continuous OR network-control dual sensitivities can guide the recovery of compact programmatic traffic-signal policies with interpretable neighbor coordination.

**Dominant contribution**: OR-to-symbolic-program bridge via dual sensitivity mapping and sparse regret-based recovery.

**Rejected complexity**: broad PI-Light extension framing, integer-MILP shadow prices, method menu, GPU-heavy MARL, raw imitation-only recovery.

**Remaining reviewer concerns**:
- duals may be proxy queue features,
- method may collapse to max-pressure,
- sparse recovery may be mere distillation,
- C-MP/MPC may outperform,
- TS may require stronger theory.

**Frontier primitive status**: absent. No LLM/VLM/diffusion/RL frontier primitive is central. This is intentional; the paper should be OR/control-first and CPU/SUMO/AMPL-feasible.

## Refinement Decisions

### Decision 1: General PIRL framing

Use “programmatically interpretable RL/control” as the umbrella framing. PI-Light is a predecessor and baseline, not the method identity.

### Decision 2: Continuous relaxation only

Dual sensitivities must come from continuous convex LP/QP relaxations. Integer phase decisions may appear later in deployment or comparison, but not as the source of shadow prices.

### Decision 3: DSL atom discipline

Every atom must map to an OR variable, constraint, reduced cost, or sensitivity. Atoms without OR semantics are excluded from the main method.

### Decision 4: Regret-based recovery

The recovery objective must minimize oracle regret/value gap, with complexity and neighbor penalties. Action agreement is secondary.

### Decision 5: Max-pressure relationship

The theory section should prove pressure as a special case. This turns a novelty risk into a positioning asset.

## Final Contribution Snapshot

- **Theory**: dual-to-movement marginal-benefit lemma; pressure special case.
- **Method**: dual-sensitivity DSL atom construction; sparse MIP program recovery.
- **Empirical**: closed-loop SUMO validation under coordination, spillback, and demand shift.
- **Practical**: CPU-feasible symbolic online controller with interpretable OR semantics.

## Ready for Experiment Planning

Yes. The method is now stable enough for claim-driven experiment planning.
