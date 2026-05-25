# PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

## Current State

**Shipped version:** v1.0 Paper Artifact — shipped 2026-05-23
**Current milestone:** v1.3 Complete Predeclared Gate C Evidence — started 2026-05-25

v1.0 produced a pressure-equivalent generalized-pressure symbolic recovery artifact for capacitated traffic-signal control. The completed scope covers Phases 1–5: theory and claim lock, sparse symbolic recovery, static pressure-failure kill-gate routing, closed-loop SUMO evaluation, and reproducible repository/paper artifact generation.

v1.1 changed the project from a pressure-equivalent recovery artifact into a finite-storage generalized-pressure research program: claim discipline, explicit finite-storage state/objective fields, slack/binding theory, a live auditable controller, deterministic Gate A/B checks, strong baseline/stress infrastructure, and fail-closed reproducibility inputs are in place. Gate C remains incomplete: Phase 12.1 closed conservatively with 57/2160 long-horizon paired-seed rows complete, 2103 rows missing, Gate C `INCONCLUSIVE`, and closed-loop superiority claims still disallowed.

v1.3 is a narrow evidence-closure milestone. It does not add controllers, change thresholds, revise the predeclared metric family, or start manuscript writing. Its job is to complete the original 2160-row Phase 11 main profile, rerun strict Gate C, and regenerate the Phase 12 reproducibility/claim package from raw artifacts.

## What This Is

This project develops an OR-methodology paper on capacitated network traffic signal control, not a PI-Light enhancement paper. The working direction is **dual-sensitivity-guided symbolic control**: derive movement-level shadow-price / dual-sensitivity signals from a continuous store-and-forward or CTM-lite traffic-network relaxation, then recover compact interpretable signal-control policies under explicit complexity and neighbor-use constraints.

The v1.0 empirical route is **pressure-equivalent generalized-pressure symbolic recovery**: static and closed-loop artifacts support theory-backed equivalence/compression and reproducibility, not a claim that dual sensitivity universally outperforms max-pressure. The v1.1 route is **finite-storage generalized-pressure separation**: prove and test that the controller reduces to max-pressure when constraints are slack but changes decisions and improves constrained objectives when downstream storage, spillback, switching, service, or incident constraints bind. v1.3 carries only the predeclared closed-loop evidence closure needed to determine whether that binding-regime improvement claim survives in SUMO.

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
- [x] Implement a live finite-storage primal-dual pressure controller / `full_dual_symbolic` path that is safely deployable in closed-loop SUMO — Phase 8.
- [x] Prove special-case recovery of max-pressure under slack constraints and a separation theorem under binding finite-storage or spillback constraints — Phase 7.
- [x] Redesign the kill gate around slack-regime recovery and binding-regime separation with fail-closed explicit-state/action-decomposition checks — Phase 9. Gate C paired-seed dominance remains Phase 11.
- [x] Add strong operational baselines including optimized fixed-time, actuated/semi-actuated, cycle-based pressure, and finite-storage/double-pressure variants where feasible — Phase 10 smoke/spec coverage complete; optimized fixed-time remains documented as a current limit.
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

v1.1/Phase 6-12.1 established a strong theory, audit, controller, baseline, and experiment protocol foundation, but did not complete closed-loop Gate C evidence. The current empirical status is fail-closed `INCONCLUSIVE`, not a negative result and not dominance evidence.

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

## Current Milestone: v1.3 Complete Predeclared Gate C Evidence

**Goal:** Complete the predeclared Phase 11/Gate C closed-loop evidence closure by executing the full 2160-row main profile, rerunning strict Gate C, and refreshing Phase 12 reproducibility/claim-status artifacts without changing thresholds, adding features, or starting manuscript writing.

**Target features:**
- Resume/execute the Phase 11 main profile to cover 6 binding regimes × 6 controllers × 20 paired seeds × 3 demand multipliers = 2160 expected rows.
- Preserve the predeclared Gate C protocol exactly: controller set, scenario regimes, paired seeds, demand multipliers, primary metrics, thresholds, and fail-closed rules are not retuned.
- Regenerate strict Gate C from raw Phase 11 evidence and report `PASSED`, `FAILED`, or `INCONCLUSIVE` without narrowing the evidence family.
- Regenerate the Phase 12 reproducibility package, claim inputs, provenance, and summaries from raw artifacts after Gate C refresh.
- Keep partial rows as debugging/provenance only; do not interpret 57/2160 rows as performance evidence.
- Defer manuscript drafting, related work, paper integration, submission preparation, and polished paper figures until after Gate C status is known.

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
*Last updated: 2026-05-25 after starting v1.3 Gate C evidence closure milestone*
