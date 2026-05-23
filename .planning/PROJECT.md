# PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

## Current State

**Shipped version:** v1.0 Paper Artifact — shipped 2026-05-23

v1.0 produced a pressure-equivalent generalized-pressure symbolic recovery artifact for capacitated traffic-signal control. The completed scope covers Phases 1–5: theory and claim lock, sparse symbolic recovery, static pressure-failure kill-gate routing, closed-loop SUMO evaluation, and reproducible repository/paper artifact generation.

The next milestone should start from manuscript integration: turn the verified artifacts into a TR-B / Transportation Science paper draft, decide which follow-up experiments are necessary, and keep the claim disciplined around generalized-pressure symbolic recovery rather than universal dual superiority.

## What This Is

This project develops an OR-methodology paper on capacitated network traffic signal control, not a PI-Light enhancement paper. The working direction is **dual-sensitivity-guided symbolic control**: derive movement-level shadow-price / dual-sensitivity signals from a continuous store-and-forward or CTM-lite traffic-network relaxation, then recover compact interpretable signal-control policies under explicit complexity and neighbor-use constraints.

The current empirical route is **pressure-equivalent generalized-pressure symbolic recovery**: static and closed-loop artifacts support theory-backed equivalence/compression and reproducibility, not a claim that dual sensitivity universally outperforms max-pressure.

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
- ✓ Rigorous capacitated traffic-network relaxation, dual pressure decomposition, pressure special case, scarcity correction, and finite-dictionary recovery quality statements — v1.0
- ✓ Full sparse symbolic recovery with oracle-regret objective, explicit complexity/neighbor/dual atom controls, and auditable JSON/CSV/rule outputs — v1.0
- ✓ Static kill-gate evidence across slack/binding/failure regimes with route decision locked to pressure-equivalent generalized-pressure symbolic recovery — v1.0
- ✓ Closed-loop SUMO evaluation covering single, arterial, grid, demand-shift, and bottleneck/failure-mode scenarios with strong pressure-style baselines and CI-ready artifacts — v1.0
- ✓ Reproducible repository surface with README, CPU/SUMO environment, block reproduction harness, artifact manifest, and script-generated paper table/figure data — v1.0

### Active

- [ ] Write the paper as an OR/control methodology contribution for TR-B / Transportation Science, with PI-Light as predecessor/baseline rather than conceptual identity.
- [ ] Convert verified theory artifacts into manuscript-ready definitions, propositions, proof sketches, and notation.
- [ ] Convert static kill-gate and closed-loop artifacts into manuscript tables, figures, and claim-disciplined interpretation.
- [ ] Decide whether longer closed-loop horizons, larger real-world networks, or additional baseline runs are necessary before submission.
- [ ] Complete related work and limitations sections around max-pressure/backpressure, interpretable/programmatic policies, OR dual sensitivity, simulator realism, oracle approximation, and recovery scalability.

### Out of Scope

- Extending the project into ADMM, robust optimization, column generation, bilevel optimization, or corridor network-flow side lines — these dilute the main kill-gate claim.
- Claiming that symbolic traffic-signal control itself is novel — PI-Light, SymLight, EvolveSignal, SignalClaw, and related work already occupy that space.
- Claiming neighbor-aware coordination itself is novel — the novelty must be the OR-derived dual-sensitivity bridge and symbolic recovery.
- Claiming dual sensitivity beats pressure everywhere — the current route is generalized pressure / pressure-equivalent symbolic recovery.
- Targeting Transportation Research Part E without a freight/logistics pivot — current traffic-signal-control framing is more natural for TR-B / Transportation Science.
- Depending on GPU-heavy MARL training as a core requirement — the project should remain CPU/SUMO/optimization oriented unless neural baselines are strictly secondary.
- Treating static ranking pilots as final evidence — v1.0 now includes closed-loop SUMO evidence, and future claims should cite those artifacts rather than static pilots alone.

## Context

The project began as an attempt to adapt π-Light (AAAI 2024) into an OR-oriented traffic-signal-control paper. Multiple review rounds pushed the direction away from "PI-Light plus OR features" and toward a narrower methodological thesis: continuous network relaxations yield interpretable dual sensitivities that can guide symbolic policy recovery.

v1.0 changed the project from idea/prototype to a verified research artifact. The decisive Phase 3 kill gate did not support a broad dual-superiority claim; it locked the route to pressure-equivalent generalized-pressure symbolic recovery. Phase 4 then validated that route in SUMO closed-loop experiments, and Phase 5 hardened the repository so key artifacts, reports, and paper table/figure data are generated from raw JSON/CSV outputs.

Known scientific and process debt remains: Phase 3 imports Phase 2 recovery code directly rather than consuming generated recovery artifacts; `local_pilight` and `full_dual_symbolic` are honestly marked not feasible in the current SUMO runner; some closed-loop horizons are short; and final plotting/manuscript integration remains for the next milestone.

## Constraints

- **Venue fit**: Primary targets are Transportation Research Part B and Transportation Science — the paper must be framed as OR / methodological traffic-network control, not AI-controller benchmarking.
- **Theory requirement**: TR-B requires formal model structure and propositions/theorems; Transportation Science can tolerate slightly less theory but still needs rigorous OR formulation and computational evidence.
- **Empirical requirement**: Closed-loop SUMO multi-seed experiments against strong pressure-style baselines are mandatory and should remain first-class evidence.
- **Claim discipline**: The current claim is generalized-pressure symbolic recovery / pressure equivalence, not universal dominance over max-pressure.
- **Compute**: Experiments should remain CPU-oriented using SUMO/TraCI, SciPy/HiGHS, AMPL/HiGHS where useful, and sparse MIP recovery; no required GPU pipeline.
- **Reproducibility**: Scripts must emit auditable JSON/CSV artifacts and tables/figures must trace back to raw experiment outputs.
- **Baseline honesty**: Max-pressure/backpressure and capacity/spillback-aware variants are first-class baselines, not strawmen.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Target TR-B / Transportation Science, not TR-E | Current problem is methodological traffic-network control, not logistics/freight operations | ✓ Good |
| Frame method as dual-sensitivity symbolic control rather than PI-Light extension | TS/TR-B reviewers need OR/control novelty; PI-Light identity invites AI-paper criticism | ✓ Good |
| Treat pressure equivalence as a feature, not a failure | Static kill-gate routed to pressure-equivalent evidence; theory proves pressure as a special case | ✓ Good |
| Make storage/supply/corridor binding scenarios the central kill gate | The paper needed an explicit route decision before closed-loop interpretation | ✓ Good |
| Implement full sparse symbolic recovery before final empirical claims | One-atom pilots were insufficient; v1.0 now emits K-atom auditable artifacts | ✓ Good |
| Keep ADMM/robust/column-generation/bilevel ideas out of the mainline | Extra machinery would dilute the continuous relaxation → dual → symbolic recovery story | ✓ Good |
| Mark infeasible baselines honestly instead of relabeling heuristics | `local_pilight` and `full_dual_symbolic` were not safely adaptable in the current SUMO runner | ✓ Good |
| Generate paper-facing tables and figure data from raw artifacts | Manual transcription would weaken reproducibility and auditability | ✓ Good |

## Next Milestone Goals

- Define Phase 6 manuscript-integration requirements and acceptance checks.
- Draft the introduction, related work, method, experiments, and limitations around the v1.0 pressure-equivalent route.
- Decide whether external-review feedback requires additional experiments before manuscript finalization.
- Convert generated table/figure data into final manuscript figures and captions.

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
*Last updated: 2026-05-23 after v1.0 milestone*
