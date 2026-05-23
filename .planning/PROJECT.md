# PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

## Current State

**Shipped version:** v1.0 Paper Artifact — shipped 2026-05-23
**Current milestone:** v1.1 Explicit Finite-Storage Primal-Dual Separation — started 2026-05-23

v1.0 produced a pressure-equivalent generalized-pressure symbolic recovery artifact for capacitated traffic-signal control. The completed scope covers Phases 1–5: theory and claim lock, sparse symbolic recovery, static pressure-failure kill-gate routing, closed-loop SUMO evaluation, and reproducible repository/paper artifact generation.

v1.1 changes the next step from manuscript integration to a new research-design milestone: build explicit finite-storage / spillback / phase-constraint mechanisms so the strong claim becomes bounded and evidence-backed. The paper may claim strict generalization and binding-regime improvement only after the new theory, live controller, kill gates, baselines, and long-horizon paired-seed evidence support it.

## What This Is

This project develops an OR-methodology paper on capacitated network traffic signal control, not a PI-Light enhancement paper. The working direction is **dual-sensitivity-guided symbolic control**: derive movement-level shadow-price / dual-sensitivity signals from a continuous store-and-forward or CTM-lite traffic-network relaxation, then recover compact interpretable signal-control policies under explicit complexity and neighbor-use constraints.

The v1.0 empirical route is **pressure-equivalent generalized-pressure symbolic recovery**: static and closed-loop artifacts support theory-backed equivalence/compression and reproducibility, not a claim that dual sensitivity universally outperforms max-pressure. The v1.1 route is **finite-storage primal-dual pressure separation**: prove and test that the controller reduces to max-pressure when constraints are slack but changes decisions and improves constrained objectives when downstream storage, spillback, switching, service, or incident constraints bind.

The target audience is Transportation Research Part B / Transportation Science reviewers who expect mathematical modeling, structural insight, rigorous optimization formulation, and closed-loop computational evidence against strong max-pressure-style baselines.

## Core Value

Show that finite-storage primal-dual pressure control strictly generalizes max-pressure: it reduces to pressure when constraints are slack, adds scarcity-aware shadow-price corrections when storage, spillback, switching, service, or incident constraints bind, and can be deployed or compressed into auditable symbolic traffic-signal policies.

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

- [ ] Replace proxy binding regimes with explicit finite-storage, receiving-capacity, spillback, switching-loss, service-urgency, and incident/capacity-drop state fields.
- [ ] Implement a live finite-storage primal-dual pressure controller / `full_dual_symbolic` path that is safely deployable in closed-loop SUMO.
- [ ] Prove special-case recovery of max-pressure under slack constraints and a separation theorem under binding finite-storage or spillback constraints.
- [ ] Redesign the kill gate around slack-regime recovery, binding-regime separation, and closed-loop dominance under paired-seed tests.
- [ ] Add strong operational baselines including optimized fixed-time, actuated/semi-actuated, cycle-based pressure, and finite-storage/double-pressure variants where feasible.
- [ ] Run journal-grade long-horizon paired-seed experiments with demand and incident sweeps and predeclared delay/spillback/unfinished-vehicle metrics.
- [ ] Preserve claim discipline: no statement that the method is better than max-pressure until the new binding-regime theory and experiments support that bounded claim.

### Out of Scope

- Extending the project into ADMM, robust optimization, column generation, bilevel optimization, or corridor network-flow side lines — these dilute the main kill-gate claim.
- Claiming that symbolic traffic-signal control itself is novel — PI-Light, SymLight, EvolveSignal, SignalClaw, and related work already occupy that space.
- Claiming neighbor-aware coordination itself is novel — the novelty must be the OR-derived dual-sensitivity bridge and symbolic recovery.
- Claiming dual sensitivity beats pressure everywhere — the permitted strong claim is bounded to binding finite-storage / spillback / switching / service / incident regimes and must report slack-regime ties as expected behavior.
- Reinterpreting v1.0 pressure-equivalent evidence as superiority evidence — new superiority language requires v1.1 theory, live controller evidence, and paired-seed closed-loop support.
- Targeting Transportation Research Part E without a freight/logistics pivot — current traffic-signal-control framing is more natural for TR-B / Transportation Science.
- Depending on GPU-heavy MARL training as a core requirement — the project should remain CPU/SUMO/optimization oriented unless neural baselines are strictly secondary.
- Treating static ranking pilots as final evidence — v1.0 now includes closed-loop SUMO evidence, and future claims should cite those artifacts rather than static pilots alone.

## Context

The project began as an attempt to adapt π-Light (AAAI 2024) into an OR-oriented traffic-signal-control paper. Multiple review rounds pushed the direction away from "PI-Light plus OR features" and toward a narrower methodological thesis: continuous network relaxations yield interpretable dual sensitivities that can guide symbolic policy recovery.

v1.0 changed the project from idea/prototype to a verified research artifact. The decisive Phase 3 kill gate did not support a broad dual-superiority claim; it locked the route to pressure-equivalent generalized-pressure symbolic recovery. Phase 4 then validated that route in SUMO closed-loop experiments, and Phase 5 hardened the repository so key artifacts, reports, and paper table/figure data are generated from raw JSON/CSV outputs.

Known scientific and process debt remains: Phase 3 imports Phase 2 recovery code directly rather than consuming generated recovery artifacts; `local_pilight` and `full_dual_symbolic` are honestly marked not feasible in the current SUMO runner; and some closed-loop horizons are short. Final manuscript writing and polished paper integration remain deferred until the finite-storage separation gates establish which claims survive.

## Constraints

- **Venue fit**: Primary targets are Transportation Research Part B and Transportation Science — the paper must be framed as OR / methodological traffic-network control, not AI-controller benchmarking.
- **Theory requirement**: TR-B requires formal model structure and propositions/theorems; Transportation Science can tolerate slightly less theory but still needs rigorous OR formulation and computational evidence.
- **Separation requirement**: v1.1 must show slack-regime max-pressure recovery and binding-regime action/objective separation before any strong performance claim is allowed.
- **Empirical requirement**: Closed-loop SUMO multi-seed experiments against strong pressure-style baselines are mandatory and should remain first-class evidence.
- **Claim discipline**: The allowed claim is bounded: tie when finite-storage and operational constraints are slack; improve only when those constraints bind and paired-seed evidence supports it.
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
| Move strong-claim work into a new finite-storage separation milestone before manuscript claims | v1.0 evidence is pressure-equivalent; superiority requires new explicit binding constraints and evidence | — Pending |

## Current Milestone: v1.1 Explicit Finite-Storage Primal-Dual Separation

**Goal:** Convert the honest v1.0 pressure-equivalent artifact into a bounded strong-claim research design by proving and testing finite-storage primal-dual separation: slack constraints recover max-pressure, binding constraints activate shadow-price corrections and improve constrained closed-loop outcomes.

**Target features:**
- Explicit finite-storage / receiving-capacity / spillback / switching-loss / service-urgency / incident state schema.
- Live finite-storage primal-dual pressure controller and safely wired `full_dual_symbolic` closed-loop path.
- Three-layer kill gate: slack special-case recovery, binding-regime separation, paired-seed closed-loop dominance.
- Strong pressure and operational baselines: optimized fixed-time, actuated/semi-actuated, capacity-aware pressure, cycle-based pressure, and finite-storage/double-pressure variants where feasible.
- Journal-grade experiment suite: 3600–7200s horizons, 900–1800s warmup, 20–30 paired seeds where computationally feasible, demand multiplier sweeps, incident/capacity-drop scenarios, and paired statistical tests.
- Theory package: special-case theorem, separation theorem/counterexample, and one stability/regret/approximation-style guarantee.

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
*Last updated: 2026-05-23 after starting v1.1 finite-storage separation milestone*
