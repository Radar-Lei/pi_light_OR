# Phase 4 Re-Review — General Programmatic RL / OR Dual-Sensitivity Framing

**Date**: 2026-05-20  
**Reviewer backend**: Codex CLI (`gpt-5.5`, xhigh reasoning, read-only)  
**Trace**: `.aris/traces/research-review/20260520_run02/`  
**Candidate**: Dual-Sensitivity-Guided Symbolic Recovery for Neighbor-Aware Traffic Signal Control

## Review Context

This re-review used the corrected framing requested by the user:

> The paper should be framed as extending **programmatically interpretable RL/control** or symbolic programmatic control into OR-guided network signal control, not primarily as a PI-Light extension.

PI-Light remains prior work, a baseline, and a reference DSL/code family, but not the conceptual identity of the method.

The reviewed narrowed method was:

> continuous store-and-forward/CTM-lite dual sensitivities → OR-mapped DSL atoms → sparse MIP symbolic recovery minimizing oracle regret and complexity → SUMO validation.

## Bottom-Line Review

The re-review is materially stronger than the previous Phase 4 review.

Scores:

- **EJOR**: **6.8/10**
- **Transportation Science**: **6.0/10**
- **Overall maturity**: **6.5/10**

Potential if early gates are strong:

- If Block 0 dual sanity and Block 1 equal-complexity recovery are strong: **EJOR 7.3–7.6**.
- If spillback/bottleneck cases clearly beat max-pressure/C-MP: **TS may approach 7**, but it is not currently a strong TS paper.

Venue recommendation:

- Best fit: **EJOR**, **Transportation Research Part C**, or computational optimization/control-oriented OR journals.
- Transportation Science remains a high-risk stretch unless theory and traffic-control insight become stronger.
- Avoid ML/RL conference framing.

## Main Improvement Over Previous Version

The reviewer agreed that the new framing improves the strongest rejection risk:

> It no longer looks like “PI-Light plus neighbor features plus a new searcher.” It now has a clearer OR/traffic-control center: continuous network relaxation → dual sensitivities → symbolic program recovery.

The method is now more defensible as:

> an optimization-derived sensitivity representation for recovering compact deployable control programs.

## Remaining Central Risk

The central risk is no longer derivative PI-Light framing. It is now:

> Are the dual atoms genuinely meaningful control signals, or are they just queue, downstream capacity, and neighbor-state features repackaged as shadow-price-flavored features?

If raw-neighbor, all-neighbor, random-price, or local-only DSLs match the dual-guided DSL under equal complexity, the main claim collapses.

## Minimum Necessary Theory

The reviewer says full closed-loop stability is not necessary at this stage, but a clean sensitivity lemma is mandatory.

Required lemma:

> For a given network state and continuous signal-service relaxation, the marginal value of serving a movement is a combination of queue-conservation duals, downstream storage/supply duals, and corridor/service constraint duals.

The theorem/lemma must show:

1. how increasing movement capacity or green service changes the optimal objective marginally;
2. how this change is represented by dual variables or reduced costs;
3. how the expression maps to `MovementValue`, `LinkValue`, `DownstreamScarcity`, and `ValueImbalance` atoms;
4. how the expression reduces to weighted pressure/backpressure when downstream storage and corridor constraints are nonbinding;
5. how binding storage/supply constraints introduce additional scarcity terms beyond ordinary pressure.

## Most Important Early Kill Gates

### Kill Gate 1 — Block 0: Dual sanity

If finite-difference checks do not agree with dual sensitivities, or if the pressure special case is not clean, the OR semantics are not credible.

### Kill Gate 2 — Block 1: Equal-complexity offline recovery

If any of these happen, the main C1/C2 claims collapse:

- raw-neighbor DSL ≈ dual-sensitivity DSL,
- all-neighbor DSL is better,
- random/permuted-price DSL is similar,
- local-only DSL is already sufficient.

### Kill Gate 3 — Block 3/4: Bottleneck and spillback

If dual-guided policies do not help under oversaturation, downstream bottleneck, or spillback scenarios relative to MP/C-MP, the “finite storage adds useful scarcity terms” claim is weak.

## What Would Still Cause Rejection

The reviewer would reject if:

- dual variables are noisy LP artifacts without stable physical meaning;
- dual-guided DSL improves only because it has more information, not better structure;
- raw/all-neighbor baselines match dual DSL at equal complexity;
- sparse MIP recovery is tiny, tuned, or hard to reproduce;
- oracle regret looks good but closed-loop SUMO performance fails;
- max-pressure/C-MP baselines are weak;
- recovered programs are not actually interpretable;
- dual recomputation is too expensive for deployability;
- theory stays intuitive rather than a rigorous sensitivity statement.

## Revision Checklist

1. Complete Block 0 first: finite-difference dual sanity and pressure special case.
2. Write the core sensitivity lemma with clear primal variables, dual variables, reduced costs, and marginal service value.
3. Freeze DSL atom taxonomy; each atom must come from relaxation variables/constraints/duals.
4. Run Block 1 equal-complexity recovery: local, raw-neighbor, all-neighbor, random-price, dual-price.
5. Make oracle regret the primary recovery metric; action agreement is diagnostic only.
6. Test arterial bottleneck and grid spillback specifically for dual-term advantage.
7. Implement strong max-pressure/C-MP baselines.
8. Show recovered programs and explain every atom’s traffic meaning.
9. Report dual recomputation frequency, AMPL/HiGHS solve time, MIP recovery time, and online latency.
10. Keep PI-Light as prior/baseline, not the main frame.

## Updated Phase 4 Decision

**Proceed to Block 0 / Block 1 implementation, not another broad ideation loop.**

The idea is now viable enough for early technical validation, but only if the first two gates demonstrate that dual sensitivities are not just relabeled neighbor features.
