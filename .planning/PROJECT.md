# PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

## What This Is

This project develops an OR-methodology paper on capacitated network traffic signal control, not a PI-Light enhancement paper. The working direction is **dual-sensitivity-guided symbolic control**: derive movement-level shadow-price / dual-sensitivity signals from a continuous store-and-forward or CTM-lite traffic-network relaxation, then recover compact interpretable signal-control policies under explicit complexity and neighbor-use constraints.

The target audience is Transportation Research Part B / Transportation Science reviewers who expect mathematical modeling, structural insight, rigorous optimization formulation, and closed-loop computational evidence against strong max-pressure-style baselines.

## Core Value

Show that network-optimization dual sensitivities provide a generalized max-pressure principle that reduces to pressure when constraints are slack and adds scarcity-aware corrections when storage, supply, or corridor bottleneck constraints bind, and that this principle can be compressed into compact symbolic traffic-signal policies.

## Requirements

### Validated

- ✓ Existing PI-Light / CityFlow reference code is available as a baseline and DSL reference family — existing
- ✓ SUMO network assets and samplers exist for single-intersection, arterial, grid, and Chengdu-style experiments — existing
- ✓ Block 0 dual sanity scaffold exists and supports the claim that dual movement rankings match finite-difference sensitivity in simple regimes — existing
- ✓ Early static recovery scaffolds compare dual-sensitivity, pressure/backpressure, local-only, raw-neighbor, all-neighbor, and random/permuted-price variants — existing
- ✓ Project framing has moved beyond "PI-Light + OR features" toward continuous relaxation → dual sensitivity → symbolic recovery — existing

### Active

- [ ] Define a rigorous capacitated traffic-network relaxation with queue conservation, movement service, phase compatibility, and storage/supply/capacity constraints.
- [ ] Derive the movement-level dual pressure decomposition and explain each term as an upstream value, downstream value, storage/supply scarcity, or corridor/service correction.
- [ ] Prove max-pressure/backpressure is a special case when storage/supply/corridor constraints are nonbinding or ranking-neutral.
- [ ] Prove or formalize the spillback/scarcity correction showing when dual sensitivity can differ from ordinary pressure.
- [ ] Implement full sparse symbolic recovery beyond one-atom pilots, with oracle-regret objective and penalties for program size, neighbor use, and dual-price atoms.
- [ ] Build pressure-failure static benchmarks with slack, storage-binding, supply-binding, corridor-bottleneck, incident, and demand-shift regimes.
- [ ] Run closed-loop SUMO experiments on single-intersection sanity, 5-intersection arterial main case, grid scalability, and robustness/demand-shift scenarios.
- [ ] Compare against strong baselines: fixed-time, actuated/local pressure, max-pressure/backpressure, capacity-aware or spillback-aware pressure, local PI-Light, raw-neighbor symbolic, all-neighbor symbolic, random/permuted dual, and full dual-symbolic policy.
- [ ] Produce reproducible paper artifacts: root README, environment specification, scripts organized by experiment block, JSON/CSV result outputs, tables, figures, and manuscript skeleton.
- [ ] Write the paper as an OR/control methodology contribution for TR-B / Transportation Science, with PI-Light as predecessor/baseline rather than conceptual identity.

### Out of Scope

- Extending the project into ADMM, robust optimization, column generation, bilevel optimization, or corridor network-flow side lines — these dilute the main kill-gate claim.
- Claiming that symbolic traffic-signal control itself is novel — PI-Light, SymLight, EvolveSignal, SignalClaw, and related work already occupy that space.
- Claiming neighbor-aware coordination itself is novel — the novelty must be the OR-derived dual-sensitivity bridge and symbolic recovery.
- Claiming dual sensitivity beats pressure everywhere — the intended claim is generalized pressure: equivalence in slack regimes, added scarcity corrections in binding regimes.
- Targeting Transportation Research Part E without a freight/logistics pivot — current traffic-signal-control framing is more natural for TR-B / Transportation Science.
- Depending on GPU-heavy MARL training as a core requirement — the project should remain CPU/SUMO/optimization oriented unless neural baselines are strictly secondary.
- Treating static ranking pilots as final evidence — closed-loop SUMO with strong baselines is required for paper claims.

## Context

The project began as an attempt to adapt π-Light (AAAI 2024) into an OR-oriented traffic-signal-control paper. Multiple review rounds pushed the direction away from "PI-Light plus OR features" and toward a narrower methodological thesis: continuous network relaxations yield interpretable dual sensitivities that can guide symbolic policy recovery.

Current public/static-review assessment places the work around research maturity 5.5–6.5/10: beyond idea brainstorming and into early verifiable method prototype, but not yet paper-ready. Existing Block 0 and Block 1 scaffolds support dual sanity and early ablations, but the decisive gap remains unresolved: current pilots show dual-sensitivity can beat naive raw/all/random neighbor atoms, while pressure/backpressure often ties dual-sensitivity. The paper will only be strong for TR-B / Transportation Science if it demonstrates when and why dual sensitivity extends pressure under storage, supply, spillback, or corridor bottlenecks.

The current repository is script-oriented and still resembles a personal research scratchpad. It contains original PI-Light / CityFlow code under `pi_light_code/`, SUMO networks under `networks/`, OR/SUMO experiment scripts under `scripts/`, early JSON artifacts under `experiments/`, and idea/refinement reports under `idea-stage/` and `refine-logs/`. A paper-ready repository should add a clear root README, environment file, organized experiment blocks, result-generation scripts, and a manuscript skeleton.

## Constraints

- **Venue fit**: Primary targets are Transportation Research Part B and Transportation Science — the paper must be framed as OR / methodological traffic-network control, not AI-controller benchmarking.
- **Theory requirement**: TR-B requires formal model structure and propositions/theorems; Transportation Science can tolerate slightly less theory but still needs rigorous OR formulation and computational evidence.
- **Empirical requirement**: Static one-step LP/ranking evidence is insufficient; closed-loop SUMO multi-seed experiments against strong pressure-style baselines are mandatory.
- **Claim discipline**: The core claim is generalized pressure with scarcity-aware corrections, not universal dominance over max-pressure.
- **Compute**: Experiments should remain CPU-oriented using SUMO/TraCI, SciPy/HiGHS, AMPL/HiGHS where useful, and sparse MIP recovery; no required GPU pipeline.
- **Reproducibility**: Scripts must emit auditable JSON/CSV artifacts and tables/figures must trace back to raw experiment outputs.
- **Baseline honesty**: Max-pressure/backpressure and capacity/spillback-aware variants are first-class baselines, not strawmen.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Target TR-B / Transportation Science, not TR-E | Current problem is methodological traffic-network control, not logistics/freight operations | — Pending |
| Frame method as dual-sensitivity symbolic control rather than PI-Light extension | TS/TR-B reviewers need OR/control novelty; PI-Light identity invites AI-paper criticism | — Pending |
| Treat pressure equivalence as a feature, not a failure | Existing pilots show dual and pressure often tie; theory should prove pressure as a special case | — Pending |
| Make storage/supply/corridor binding scenarios the central kill gate | The paper needs evidence that dual adds value where ordinary pressure misses scarcity | — Pending |
| Implement full sparse symbolic recovery before final empirical claims | One-atom equal-complexity pilots are sanity checks, not publishable recovery evidence | — Pending |
| Keep ADMM/robust/column-generation/bilevel ideas out of the mainline | Extra machinery would dilute the clean continuous relaxation → dual → symbolic recovery story | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-22 after initialization*
