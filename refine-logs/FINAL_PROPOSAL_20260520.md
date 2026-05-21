# Final Proposal — Dual-Sensitivity-Guided Programmatic Signal Control

**Date**: 2026-05-20  
**Status**: READY WITH NARROWED CLAIM  
**Target**: EJOR-first, Transportation Science only if theory/experiments become unusually strong  
**Working title**: Dual-Sensitivity-Guided Symbolic Recovery for Neighbor-Aware Traffic Signal Control

## Problem Anchor

Programmatically interpretable reinforcement learning and symbolic control have shown that compact traffic-signal programs can be deployable and understandable, but existing symbolic/programmatic TSC methods are mostly local or search-driven. Network traffic control, however, is governed by coupled queues, downstream storage, turning flows, and corridor spillback. The open problem is:

> How can a compact, deployable programmatic traffic-signal policy use network-coupling information in a way that is OR-principled rather than merely adding raw neighboring states?

## Final Method Thesis

A continuous store-and-forward / CTM-lite network-control relaxation provides dual sensitivities that quantify the marginal network value of service, storage, and downstream capacity. These dual sensitivities can be mapped into a small set of interpretable DSL atoms, then used to recover compact programmatic traffic-signal policies through sparse mixed-integer optimization that minimizes oracle regret and program complexity.

## Framing

This should be framed as an extension of **programmatically interpretable RL/control** into OR-guided network signal control, not primarily as a PI-Light extension.

PI-Light should appear as:
- a prior example of programmatic interpretable TSC,
- a baseline/reference DSL family,
- a code or implementation reference where useful.

The method identity should be broader:

> OR dual-sensitivity-guided symbolic recovery for deployable network signal control.

## Dominant Contribution

The dominant contribution is the OR-to-program bridge:

1. derive dual sensitivities from a continuous network traffic-control relaxation;
2. map each retained symbolic DSL atom to a specific OR constraint or sensitivity;
3. recover compact symbolic policies by minimizing oracle regret plus complexity and neighbor-use penalties;
4. validate that dual-sensitivity atoms outperform raw-neighbor, all-neighbor, random-price, and local-only symbolic policies under equal complexity.

## Explicitly Rejected Complexity

To avoid the Phase 4 rejection risk, the paper should reject the following:

- no menu of MILP/CP-SAT/column-generation/bilevel alternatives;
- no shadow-price story from integer phase-decision MILPs;
- no GPU-heavy MARL as a mandatory component;
- no claim that symbolic TSC itself is novel;
- no claim that neighbor-aware coordination itself is novel;
- no claim that max-pressure intuition itself is novel;
- no raw imitation-accuracy-only evaluation.

## Fixed Technical Core

### 1. Continuous Network Relaxation

Use a continuous LP/QP store-and-forward or CTM-lite model over a short horizon.

State:
- link queue / occupancy `x_l(t)`,
- storage capacity `S_l`,
- turning fractions `r_{lm}`,
- demand / arrival estimate `d_l(t)`,
- approximate service allocation `g_p(t)` or movement service `u_m(t)`.

Constraints:
- flow conservation,
- downstream storage / supply limits,
- nonnegative queues,
- green-split feasibility in continuous form,
- optional corridor/service smoothness penalties.

Objective:
- minimize total weighted queue, delay proxy, spillback penalty, and optionally switching/green smoothness proxy.

Important: the relaxation must be continuous and convex so dual sensitivities have a legitimate marginal-value interpretation.

### 2. Dual Sensitivity Extraction

Extract dual variables/sensitivities for interpretable network quantities:

| OR object | Dual meaning | Candidate DSL atom |
|---|---|---|
| queue conservation constraint | marginal cost of extra vehicles on a link | `LinkValue(l)` |
| downstream storage/supply constraint | marginal value of scarce receiving capacity | `DownstreamScarcity(l)` |
| corridor/service balance constraint | marginal corridor imbalance | `CorridorValue(c)` |
| movement service variable reduced cost / value difference | marginal benefit of serving a movement | `MovementValue(m)` |
| upstream-downstream value difference | pressure-like service priority | `ValueImbalance(up,down)` |

Do not introduce DSL atoms that cannot be traced to a model variable, constraint, or sensitivity.

### 3. Dual-to-Movement Marginal-Benefit Lemma

The paper needs a small formal result:

> In the continuous relaxation, the first-order change in objective from increasing service on movement `i -> j` is proportional to an upstream value minus a downstream scarcity/value term, adjusted by turning and storage constraints.

This makes `ValueImbalance(up,down)` an OR-derived generalization of pressure, not a hand-designed queue feature.

### 4. Pressure Special Case

Under simplified assumptions:
- no finite-storage binding,
- fixed turning ratios,
- linear queue objective,
- local movement service,
- no corridor coupling,

the dual-sensitivity movement score should reduce to a max-pressure/backpressure-like score.

This result positions max-pressure as a special case and explains why finite storage / spillback introduces additional dual terms.

### 5. Sparse MIP Symbolic Recovery

Given sampled states and oracle values from the continuous relaxation, recover a compact programmatic policy.

Candidate atom library:
- only OR-mapped atoms,
- local queue/value atoms,
- downstream scarcity atoms,
- neighbor value-imbalance atoms,
- optional corridor value atoms if the relaxation includes a corridor constraint.

Decision variables:
- atom selection,
- threshold/bin selection,
- movement/phase score coefficients,
- optional rule depth or term count.

Objective:

`min oracle_regret(policy) + λ_complexity * program_size + λ_neighbor * neighbor_terms`

Primary fit metric should be oracle regret/value gap, not just action agreement.

## Main Claims

### Claim 1 — OR-principled symbolic coordination

Dual sensitivities from a continuous network-control relaxation provide a principled way to select and weight neighbor information in programmatic traffic-signal policies.

Required evidence:
- dual-to-movement lemma,
- pressure special case,
- atom-to-constraint mapping,
- ablation vs raw/all/random neighbor atoms.

### Claim 2 — Compact recovery without losing network value

Sparse MIP recovery can produce compact symbolic policies with small oracle regret and practical closed-loop performance.

Required evidence:
- oracle regret / value gap,
- program size,
- SUMO delay/travel time/throughput/spillback,
- runtime.

### Claim 3 — Dual-guided atoms matter under network coupling

The advantage appears specifically in coupled settings: arterial coordination, grid spillback, and demand shift.

Required evidence:
- 5-intersection arterial,
- 4×4 grid,
- demand shift including peak reversal, oversaturation, and turning-ratio error.

## Paper Positioning

Do not lead with “we extend PI-Light.” Lead with:

> Programmatic interpretable control needs network-coupling structure. We show that continuous OR relaxations provide dual sensitivities that can be recovered as compact symbolic signal-control programs.

PI-Light is cited as a key predecessor and implementation reference, but not the conceptual boundary of the work.

## Remaining Risks

1. **Dual values may collapse to ordinary pressure.**  
   Mitigation: prove pressure special case and show finite storage / downstream scarcity adds useful terms.

2. **Sparse MIP recovery may only imitate oracle actions, not value.**  
   Mitigation: optimize regret/value gap, report action agreement only as secondary.

3. **C-MP may dominate.**  
   Mitigation: target interpretability/compactness plus demand-shift robustness; compare fairly and do not overclaim if C-MP wins in some regimes.

4. **TS may demand stronger theory.**  
   Mitigation: target EJOR unless theory/experimental evidence becomes substantially stronger.

## Verdict

Proceed to experiment planning under this narrowed thesis. Do not widen the method unless a validation failure forces a pivot.
