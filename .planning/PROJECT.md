# PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

## Current State

**Shipped version:** v1.4 Strong Baseline-Dominance Method Search — shipped 2026-05-26
**Current milestone:** v1.5 Dynamic Finite-Storage Primal-Dual Method Redesign — implementation started 2026-05-27

v1.0 produced a pressure-equivalent generalized-pressure symbolic recovery artifact for capacitated traffic-signal control. The completed scope covers Phases 1–5: theory and claim lock, sparse symbolic recovery, static pressure-failure kill-gate routing, closed-loop SUMO evaluation, and reproducible repository/paper artifact generation.

v1.1 changed the project from a pressure-equivalent recovery artifact into a finite-storage generalized-pressure research program: claim discipline, explicit finite-storage state/objective fields, slack/binding theory, a live auditable controller, deterministic Gate A/B checks, strong baseline/stress infrastructure, and fail-closed reproducibility inputs are in place.

v1.3 closed the predeclared Gate C evidence gap. The original 2160-row Phase 11 main profile completed with generated status `FAILED`; strict Gate C regenerated as `INCONCLUSIVE`; Phase 12 reproducibility and claim-status artifacts regenerated conservatively with claim audit `PASSED`. Closed-loop superiority claims remain disallowed.

v1.4 reopened method design under stricter discipline: it diagnosed the v1.3 failure, ran parallel exploratory workstreams, selected `finite_storage_primal_dual_v1_4_score` as a single locked candidate, and executed the locked 1440-row Gate C confirmation. The row audit is clean, but the locked execution status is `FAILED` and strict paired evidence remains `INCONCLUSIVE`; closed-loop superiority over max-pressure-style baselines remains disallowed.

v1.5 starts from the v1.4 failure diagnosis rather than tuning static weights again. The method-design target is dynamic finite-storage primal-dual pressure: storage scarcity must use vehicle-count occupancy, not halting queue; the controller must maintain stateful storage, release, cascade, and service shadow prices; and any future claim must come from a new locked v1.5 protocol with strong baselines and occupancy/static ablations. The first v1.5 implementation reached mechanism activation, but early binding-holdout rows show repeated safety-guard harm against strong baselines, so this candidate is not claim-ready.

## What This Is

This project develops an OR-methodology paper on capacitated network traffic signal control, not a PI-Light enhancement paper. The working direction is **dual-sensitivity-guided symbolic control**: derive movement-level shadow-price / dual-sensitivity signals from a continuous store-and-forward or CTM-lite traffic-network relaxation, then recover compact interpretable signal-control policies under explicit complexity and neighbor-use constraints.

The v1.0 empirical route is **pressure-equivalent generalized-pressure symbolic recovery**: static and closed-loop artifacts support theory-backed equivalence/compression and reproducibility, not a claim that dual sensitivity universally outperforms max-pressure. The v1.1 route is **finite-storage generalized-pressure separation**: prove and test that the controller reduces to max-pressure when constraints are slack but changes decisions and improves constrained objectives when downstream storage, spillback, switching, service, or incident constraints bind. v1.3 determined that the predeclared SUMO Gate C route does not currently support closed-loop superiority: the full 2160-row main artifact is complete but `FAILED`, and strict Gate C is `INCONCLUSIVE`. v1.4 confirmed that the static weighted candidate is not enough: 1440/1440 locked rows executed, but strict Gate C remains non-PASSED. v1.5 is a method redesign around dynamic occupancy-based shadow prices, not a reinterpretation of v1.4 evidence.

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
- ✓ Full predeclared Phase 11 main-profile execution over 2160 paired-seed rows with refreshed progress/source artifacts — v1.3
- ✓ Strict Gate C and Phase 12 reproducibility/claim-status regeneration from refreshed raw artifacts — v1.3
- ✓ Closed-loop superiority claim remains disallowed after complete Gate C evidence closure — v1.3
- ✓ v1.4 failure diagnostics, workstream pilots, candidate convergence, locked protocol, fail-closed Gate C status, and claim refresh are generated without overclaiming — v1.4
- ✓ `finite_storage_primal_dual_v1_4_score` is the only locked v1.4 candidate, with max-pressure, capacity-aware pressure, and finite-storage double-pressure preserved as required comparators — v1.4
- ✓ v1.4 locked Gate C executed 1440/1440 rows with clean row audit but non-PASSED strict evidence; closed-loop superiority remains disallowed — v1.4

### Active

- [x] Replace proxy binding regimes with explicit finite-storage, receiving-capacity, spillback, switching-loss, service-urgency, and incident/capacity-drop state fields — Phases 6, 8, 9, 11.
- [x] Implement a live finite-storage primal-dual pressure controller / `full_dual_symbolic` path that is safely deployable in closed-loop SUMO — Phase 8.
- [x] Prove special-case recovery of max-pressure under slack constraints and a separation theorem under binding finite-storage or spillback constraints — Phase 7.
- [x] Redesign the kill gate around slack-regime recovery and binding-regime separation with fail-closed explicit-state/action-decomposition checks — Phase 9. Gate C paired-seed dominance remains Phase 11.
- [x] Add strong operational baselines including optimized fixed-time, actuated/semi-actuated, cycle-based pressure, and finite-storage/double-pressure variants where feasible — Phase 10 smoke/spec coverage complete; optimized fixed-time remains documented as a current limit.
- [x] Run journal-grade long-horizon paired-seed experiments with demand and incident sweeps and predeclared delay/spillback/unfinished-vehicle metrics — v1.3 completed the predeclared run, generated status `FAILED`.
- [x] Preserve claim discipline: no statement that the method is better than max-pressure until the new binding-regime theory and experiments support that bounded claim — v1.3 keeps closed-loop superiority disallowed.
- [x] Execute the locked 1440-row v1.4 Gate C main confirmation run and rerun strict paired evidence — completed with non-PASSED strict evidence.
- [x] Treat non-PASSED v1.4 as a claim boundary, not a tuning invitation.
- [x] Complete v1.5 occupancy-based finite-storage state migration across schema and closed-loop runner.
- [x] Complete `finite_storage_dynamic_primal_dual_v1_5` with stateful storage, release, cascade, and service-age shadow prices plus action-decomposition audit fields.
- [x] Add v1.5 deterministic separation fixtures/gates for slack pressure recovery, occupancy-based storage separation, multi-hop cascade separation, and release-value behavior.
- [x] Add v1.5 closed-loop diagnostics for storage activation rates, action-difference rates, and mechanism term activation in binding SUMO regimes.
- [x] Define a locked v1.5 training/holdout protocol with composite finite-storage operating cost as primary endpoint and practical-harm safety guards.
- [x] Add fail-closed, resumable v1.5 locked holdout execution tooling and dry-run artifact.
- [x] Add strict v1.5 paired-evidence checker over composite finite-storage operating cost and safety guards.
- [x] Audit the original locked v1.5 protocol for actual storage-binding activation and supersede it with a binding-focused protocol when early rows fail to bind.
- [x] Run early binding-holdout rows against `max_pressure`, `capacity_aware_pressure`, `occupancy_capacity_aware_pressure`, `finite_storage_double_pressure`, and static v1.4 ablation.
- [x] Record early binding-holdout risk: mechanisms activate, but safety guards fail repeatedly against strong baselines, so full execution should stop before method revision.
- [x] Add `finite_storage_dynamic_primal_dual_v1_5_r2_guarded`, a post-holdout method-revision candidate that caps non-pressure dynamic corrections to reduce safety-guard risk while preserving auditable mechanism terms.
- [x] Lock `v1_5_r2_training_protocol.json` with fresh training seeds disjoint from the current binding holdout seeds.
- [x] Execute the first r2 training batch and reject the guarded candidate: action separation fell to about 1.1%, composite tied max-pressure, and unfinished vehicles harmed `finite_storage_double_pressure`.
- [x] Test r3-r5 training candidates on fresh seeds; all reduce composite cost in the first training cell but are rejected because unfinished-vehicle safety guards fail.
- [x] Test r6 terminal finite-storage-double flush on fresh seeds; it preserves positive composite signal but is rejected because unfinished-vehicle safety fails on the second seed.
- [x] Test r7 finite-storage-double score filtering; it ties finite-storage double but remains too pressure-equivalent and harms capacity-aware unfinished-vehicle safety.
- [x] Test r8-r10 safety-filter variants; all remain non-selected because unfinished-vehicle safety fails despite positive composite signals in r9/r10.
- [x] Test r11 local completion-risk service preservation; reject after the second fresh training seed because unfinished-vehicle safety still fails against strong baselines.
- [x] Test r12 receiver-constrained route-completion proxy; reject in the first fresh training seed because unfinished-vehicle safety still fails and action separation falls below 5%.
- [x] Test r13 movement-level TraCI route-demand completion prediction; reject in the first fresh training seed because unfinished-vehicle safety still fails despite restored action separation.
- [x] Test r14 route-demand completion with finite-storage-double score veto; reject because it collapses action separation and triggers delay safety harm.
- [x] Test r15 horizon-aware modeled completion; reject because unfinished-vehicle safety still fails despite positive composite signals against all core strong baselines.
- [x] Test r16 horizon-aware modeled completion with terminal finite-storage-double lock; reject on the second fresh training seed due capacity-aware unfinished-vehicle safety harm.
- [x] Test r17 horizon-aware modeled completion with terminal capacity-aware lock; reject in the first fresh training seed due finite-storage-double unfinished-vehicle safety harm.
- [x] Test r18 horizon-aware modeled completion with balanced terminal capacity/double lock; reject in the first fresh training seed because finite-storage-double unfinished-vehicle safety still fails and composite is worse than finite-storage double pressure.
- [x] Test r19 horizon-aware modeled completion with stronger finite-storage-double anchoring; reject on the second fresh training seed because max-pressure unfinished-vehicle safety fails by one vehicle, despite positive composite means against all core strong baselines.
- [x] Test r20 horizon-aware modeled completion with balanced max-pressure/double terminal lock; reject in the first fresh training seed because unfinished-vehicle safety fails against both max-pressure and finite-storage double pressure despite positive composite means.
- [x] Test r21 horizon-aware modeled completion with terminal max/double completion-service guard; reject in the first fresh training seed because unfinished-vehicle safety still fails against both max-pressure and finite-storage double pressure despite positive composite means.
- [x] Test r22 horizon-aware modeled completion with all-interval completion-safety veto; reject in the first fresh training seed because the veto lowers action separation below 5%, makes composite means negative against core baselines, and still fails unfinished-vehicle safety.
- [x] Test r23 horizon-aware modeled completion with baseline-dominance filtering for marginal horizon overrides; reject in the first fresh training seed because the filter lowers action separation below 5% and unfinished-vehicle safety still fails.
- [x] Test r24 staged horizon completion; reject in the first fresh training seed because max-pressure unfinished-vehicle safety still fails by one vehicle despite positive composite means and 14.7% action separation.
- [x] Test r25 staged horizon completion with late max-pressure terminal lock; reject in the first fresh training seed because unfinished-vehicle safety worsens against max-pressure and finite-storage double despite positive composite means.
- [x] Test r26 staged horizon completion with remaining-horizon relative exit urgency; reject in the first fresh training seed because unfinished-vehicle safety worsens against max-pressure, capacity-aware pressure, and finite-storage double pressure despite positive composite means and 14.6% action separation.
- [x] Test r27 staged horizon completion with a terminal exit-protection guard; reject in the first fresh training seed because max-pressure unfinished-vehicle safety still fails despite positive composite means and 17.6% action separation.
- [x] Test r28 staged horizon completion with a max-pressure completion envelope; continue after a clean first seed, then reject on the second fresh training seed because unfinished-vehicle safety fails against max-pressure, capacity-aware pressure, and finite-storage double pressure.
- [x] Test r29 staged horizon completion with an all-core-baseline completion envelope; reject in the first fresh training seed because finite-storage-double unfinished safety still fails and composite means turn negative against max-pressure and finite-storage double.
- [x] Test r30 staged horizon completion with a finite-storage-double completion envelope; reject in the first fresh training seed because capacity-aware unfinished safety still fails and composite means turn negative against all core strong baselines.
- [x] Test r31 staged horizon completion with the r24 finite-storage-double terminal lock delayed from 0.78 to 0.88; reject in the first fresh training seed because finite-storage-double unfinished safety still fails by one vehicle despite positive core composite means.
- [x] Test r32 staged horizon completion with a narrow preterminal finite-storage-double guard after 0.82; clear the first fresh training seed, then reject on the second because finite-storage-double unfinished safety fails.
- [x] Test r33 staged horizon completion with a midcourse finite-storage-double guard after 0.70; reject in the first fresh training seed because max-pressure and capacity-aware unfinished safety fail despite positive core composite means.
- [x] Test r34 staged horizon completion with a core-minimax guard across max-pressure, capacity-aware pressure, and finite-storage double; reject in the first fresh training seed because max-pressure and finite-storage-double unfinished safety both fail and composite mean is negative against max-pressure.
- [x] Test r35 staged horizon completion with deadline-oriented route urgency for low-slack finishable vehicles; reject in the first fresh training seed because it over-rotates actions, causing unfinished count 1209 and negative composite means against all core baselines.
- [x] Test r36 staged horizon completion with late-gated deadline urgency after 0.78 and a higher base weight; clear the first fresh training seed, then reject on the second because unfinished safety fails against all core baselines despite positive core composite means.
- [x] Test r37 staged horizon completion with a late-gated deadline service anchor; reject in the first fresh training seed because service anchoring overcorrects action stability, loses composite cost to max-pressure and capacity-aware pressure, and still fails capacity-aware unfinished safety.
- [x] Test r38 staged horizon completion with a narrow capacity-aware rescue guard; reject in the first fresh training seed because the guard triggers only once, leaving capacity-aware unfinished safety harm while composite still loses to capacity-aware pressure.
- [x] Test r39 staged horizon completion with a capacity-aware score envelope; reject in the first fresh training seed because the envelope collapses action separation below 5% and unfinished safety still fails against max-pressure and capacity-aware pressure despite positive core composite means.
- [x] Test r40 staged horizon completion with a pressure-safe horizon override guard; reject in the first fresh training seed because unfinished safety still fails against all core baselines despite positive core composite means and 5.26% action separation.
- [x] Test r41 staged horizon completion with a locked terminal core-completion choice; reject in the first fresh training seed because action separation drops below 5% and unfinished safety still fails against all core baselines despite positive core composite means.
- [x] Test r42 staged horizon completion with a late tail-completion rescue; reject in the first fresh training seed because unfinished safety still fails against capacity-aware and finite-storage double pressure while composite means turn negative against both.
- [x] Test r43 staged horizon completion with a strict pressure-safe guard and no deadline urgency; reject in the first fresh training seed because unfinished safety passes but action separation drops to 2.07% and composite means turn negative against all core baselines.
- [x] Test r44 staged horizon completion with a looser pressure-safe guard; reject in the first fresh training seed because composite means recover positive but action separation remains below 5% and unfinished safety fails against capacity-aware and finite-storage double pressure.
- [x] Test r45 staged horizon completion with a preterminal pressure-safe guard plus route-horizon tail-completion rescue; reject after the full 324-row training execution because 176 safety harms accumulate, unfinished-vehicle regressions spread across strong baselines, and core composite means turn negative against max-pressure and capacity-aware pressure.
- [x] Test r46 staged horizon completion with an occupancy-gated completion-safety veto on top of r45; reject after the first 12-row batch because early core composite means stay positive against all core baselines, but `arterial_v1_5_storage_activation` still produces unfinished-vehicle safety harm on seed `20261218`.
- [x] Generate `v1_5_revision_candidate_summary.json` showing no selected r2-r46 candidate and identifying completion/safety risk as unresolved.
- [x] Generate `v1_5_completion_safety_contract_audit.json`: 45 candidates are rejected, 43 have unfinished safety blockers, 27 keep positive core composite means, 23 also clear the action-separation floor, and zero pass unfinished safety; current evidence does not support weakening the safety contract.
- [x] Generate `v1_5_completion_tradeoff_analysis.json`: 107 analyzed training cases, 75 unsafe cases, 52 composite-win cases, 24 safe-and-composite-win cases, and 33 core-baseline oracle conflicts.
- [ ] Add an explicit completion-safety controller guard that passes fresh training seeds before any confirmatory holdout; do not weaken the unfinished-vehicle safety contract based on current evidence.
- [ ] Lock a fresh/superseding protocol before any new confirmatory claim attempt.

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

v1.1/Phase 6-12.1 established a strong theory, audit, controller, baseline, and experiment protocol foundation, but did not complete closed-loop Gate C evidence. v1.3 completed that empirical closure: the full predeclared Phase 11 main artifact has 2160/2160 rows and generated status `FAILED`; strict Gate C is `INCONCLUSIVE`; Phase 12 package is `INCONCLUSIVE`; claim audit is `PASSED`. This is a negative/fail-closed empirical result for the predeclared closed-loop superiority route, not dominance evidence.

v1.4 started from the user's requirement that the eventual method must be stronger than max-pressure and related strong baselines. That requirement was treated as a predeclared success criterion, not an assumed conclusion. The locked 1440-row run completed with clean row audit, but the method did not produce passing strict evidence; closed-loop superiority remains disallowed.

v1.5 now follows the round-1 GPT Pro suggestion: replace queue-based storage proxies with occupancy-based storage state, add stateful dynamic dual variables, separate occupancy-aware baseline effects from dynamic primal-dual effects, and define any future superiority claim through a new locked protocol.

Known scientific and process debt remains: Phase 3 imports Phase 2 recovery code directly rather than consuming generated recovery artifacts; `local_pilight` and `full_dual_symbolic` are honestly marked not feasible in the current SUMO runner; and some closed-loop horizons are short. Final manuscript writing and polished paper integration remain deferred until the finite-storage separation gates establish which claims survive.

## Constraints

- **Venue fit**: Primary targets are Transportation Research Part B and Transportation Science — the paper must be framed as OR / methodological traffic-network control, not AI-controller benchmarking.
- **Theory requirement**: TR-B requires formal model structure and propositions/theorems; Transportation Science can tolerate slightly less theory but still needs rigorous OR formulation and computational evidence.
- **Separation requirement**: v1.1 must show slack-regime max-pressure recovery and binding-regime action/objective separation before any strong performance claim is allowed.
- **Empirical requirement**: Closed-loop SUMO multi-seed experiments against strong pressure-style baselines are mandatory and should remain first-class evidence.
- **Claim discipline**: The allowed claim is bounded: tie when finite-storage and operational constraints are slack; improve only when those constraints bind and paired-seed evidence supports it.
- **v1.5 strong-claim gate**: Baseline dominance is a hard target, not an assumption. Closed-loop superiority remains disallowed unless a new locked v1.5 protocol is `PASSED`.
- **v1.5 holdout hygiene**: Current binding holdout seeds have exposed safety-guard harm and cannot be used for tuning followed by reuse as confirmatory evidence.
- **Exploration vs confirmation**: Workstream smoke/pilot results may select a candidate method but cannot be used as final claim evidence unless the protocol explicitly marks them as exploratory.
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
| Move strong-claim work into a new finite-storage separation milestone before manuscript claims | v1.0 evidence is pressure-equivalent; superiority requires new explicit binding constraints and evidence | ✓ Good |
| Treat complete non-PASSED Gate C as a claim boundary, not a tuning invitation | v1.3 completed 2160/2160 rows and still generated `FAILED`/`INCONCLUSIVE` statuses | ✓ Good |
| Start v1.4 as parallel method search with a hard Gate C target | The user requires a strong baseline-dominance claim, but v1.3 makes it unsafe to assume that result before evidence | ✓ Good |
| Keep v1.4 exploratory pilots separate from final claim evidence | Prevents post-selection overclaim and preserves a clean confirmation boundary | ✓ Good |
| Select only `finite_storage_primal_dual_v1_4_score` for locked confirmation | It ranked best under pilot criteria while preserving auditability and strong comparators | ✓ Good |
| Keep closed-loop superiority disallowed after complete non-PASSED v1.4 Gate C | The locked 1440-row run completed but strict paired evidence remained non-PASSED | ✓ Good |
| Start v1.5 as dynamic occupancy-based primal-dual redesign | v1.4 showed static weighted pressure did not separate enough from strong baselines | In progress |

## Next Milestone Direction

v1.5 Dynamic Finite-Storage Primal-Dual Method Redesign is active.

Likely next steps:
- Finish v1.5 controller diagnostics for storage activation, action difference relative to pressure, cascade price activation, and release-value behavior.
- Create v1.5 theory/gate artifacts and a locked pilot/training/holdout protocol.
- Defer manuscript superiority language until a strict locked v1.5 artifact permits the claim.

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
*Last updated: 2026-05-26 after completing v1.4 Strong Baseline-Dominance Method Search*
