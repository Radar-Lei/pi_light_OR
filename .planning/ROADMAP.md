---
phase: 12.1
slug: close-v1-1-gap-execute-or-downgrade-gate-c-long-horizon-evid
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-25
---

# Roadmap: PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

## Milestones

- ✅ **v1.0 Paper Artifact** — Phases 1–5 shipped 2026-05-23; pressure-equivalent generalized-pressure symbolic recovery artifact archived in [`milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md).
- 🚧 **v1.1 Explicit Finite-Storage Primal-Dual Separation** — Phases 6–12 in planning/execution; builds theory, controller, gates, experiments, reproducibility, and future evidence inputs without starting paper drafting.

## Overview

v1.1 converts the v1.0 pressure-equivalent artifact into a bounded strong-claim research design. The milestone must prove and test that finite-storage primal-dual pressure recovers or ties max-pressure when constraints are slack, and only separates/improves when downstream storage, spillback, switching, service urgency, or incident/capacity-drop constraints bind. This roadmap deliberately excludes paper drafting, related-work writing, final manuscript integration, and submission preparation.

## Phases

**Phase Numbering:** continuing from shipped v1.0 Phases 1–5.

- [x] **Phase 6: Claim Discipline and Explicit State Foundation** - Lock bounded claim rules and replace proxy regimes with explicit finite-storage state/objective artifacts. (completed 2026-05-23)
- [ ] **Phase 7: Theory and Separation Package** - Prove slack max-pressure recovery, binding-regime separation, strict one-step improvement, and one additional guarantee candidate.
- [x] **Phase 8: Live Finite-Storage Primal-Dual Controller** - Implement a safely deployable controller path with auditable score decompositions and slack-regime reduction tests. (completed 2026-05-24)
- [x] **Phase 9: Slack and Binding Kill Gates** - Build fail-closed gates for slack recovery and binding-state action/objective separation. (completed 2026-05-24)
- [x] **Phase 10: Strong Baselines and Stress Scenario Suite** - Add honest operational/pressure baselines and explicit finite-storage stress scenarios, including the grid fixed-time counterexample. (completed 2026-05-24)
- [x] **Phase 11: Long-Horizon Paired-Seed Evidence** - Run journal-grade closed-loop paired-seed experiments and statistical dominance checks only in binding stress regimes. (completed 2026-05-24)
- [x] **Phase 12: Reproducibility and Future Claim Inputs** - Regenerate all new evidence from raw artifacts and prepare bounded future claim inputs without drafting the paper. (completed 2026-05-24)
- [ ] **Phase 12.1: Close v1.1 gap: execute or downgrade Gate C long-horizon evidence** - Execute the predeclared Gate C main profile or preserve fail-closed status through downstream reproducibility/status artifacts.

## Phase Details

### Phase 6: Claim Discipline and Explicit State Foundation

**Goal**: Researchers can audit explicit finite-storage state/objective data and see that all project language prevents v1.0 evidence from being treated as dual-superiority evidence.
**Depends on**: Phase 5
**Requirements**: CLAIM-01, CLAIM-02, STATE-01, STATE-02, STATE-03
**Success Criteria** (what must be TRUE):

  1. User can inspect milestone claim guards and see the bounded claim: slack regimes recover/tie max-pressure, while improvement claims are restricted to binding storage/spillback/switching/service/incident regimes.
  2. User can run or inspect artifact generation and find explicit downstream storage, residual receiving capacity, spillback/blocking, switching-loss, service-urgency, and incident/capacity-drop fields instead of proxy-only labels.
  3. User can audit finite-storage objective outputs decomposed into delay, unfinished-vehicle penalty, spillback/blocking time, and switching lost-time terms.
  4. User can see repository/report checks that prevent v1.0 pressure-equivalent evidence from being described as dual superiority.

**Plans**: 3 plans
Plans:
**Wave 1**

- [x] 06-01-PLAN.md — Create central bounded claim policy and fail-closed claim audit CLI.
- [x] 06-02-PLAN.md — Create finite-storage state/objective schema helpers and deterministic Phase 6 fixtures.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 06-03-PLAN.md — Integrate claim/state safeguards into static, closed-loop, report, and reproducibility surfaces.

### Phase 7: Theory and Separation Package

**Goal**: Researchers have a formal finite-storage primal-dual separation package that justifies exactly when the method reduces to pressure and when it can differ.
**Depends on**: Phase 6
**Requirements**: THRY-01, THRY-02, THRY-03, THRY-04
**Success Criteria** (what must be TRUE):

  1. User can verify a special-case theorem showing reduction to classical max-pressure/backpressure under infinite storage, no switching loss, fixed turning ratios, and slack operational constraints.
  2. User can inspect a theorem or counterexample where finite storage, spillback, incident capacity drop, or switching loss makes the primal-dual controller choose a different phase than classical pressure.
  3. User can audit the separation example and see strict improvement on a predeclared one-step constrained objective, spillback penalty, Lyapunov drift, or equivalent criterion.
  4. User can identify one additional guarantee candidate suitable for later use: throughput/bounded-drift, regret to a constrained LP oracle, or symbolic-compression error bound.

**Plans**: 1 plan
Plans:
**Wave 1**

- [x] 07-01-PLAN.md — Create bounded finite-storage theory memo, deterministic separation checker, JSON artifact, and tests.

### Phase 8: Live Finite-Storage Primal-Dual Controller

**Goal**: Operators can run a safe finite-storage primal-dual controller in closed-loop SUMO and audit why binding constraints changed actions.
**Depends on**: Phase 7
**Requirements**: CTRL-01, CTRL-02, CTRL-03, CTRL-04
**Success Criteria** (what must be TRUE):

  1. User can select a finite-storage primal-dual controller or safe `full_dual_symbolic` successor in closed-loop SUMO without relabeling unsafe queue heuristics as the proposed method.
  2. User can inspect movement/phase score decompositions showing queue pressure plus downstream storage, spillback, switching, service, and incident shadow-price corrections.
  3. User can run deterministic slack fixtures and observe pressure-equivalent actions matching existing max-pressure behavior.
  4. User can run binding fixtures and see which shadow-price terms changed the selected action relative to classical pressure.

**Plans**: 1 plan
Plans:
**Wave 1**

- [x] 08-01-PLAN.md — Implement safe `finite_storage_primal_dual` controller, audited score decompositions, slack/binding tests, and completed-row action audit.

### Phase 9: Slack and Binding Kill Gates

**Goal**: Researchers can run fail-closed gates that separately validate slack-regime recovery and binding-regime separation before any closed-loop dominance claim is allowed.
**Depends on**: Phase 8
**Requirements**: GATE-01, GATE-02, GATE-04
**Success Criteria** (what must be TRUE):

  1. User can run Gate A and see high slack-regime action agreement with max-pressure/backpressure, with ties reported as expected behavior.
  2. User can run Gate B and see binding-state action separation plus constrained-oracle or one-step objective improvement on explicit storage/spillback/switching/incident states.
  3. User can observe gates fail closed when explicit state fields, action decompositions, paired seeds, or required baseline comparators are missing.
  4. User can inspect gate summaries that clearly distinguish recovery evidence from separation evidence.

**Plans**: 1 plan
Plans:
**Wave 1**

- [x] 09-01-PLAN.md — Implement deterministic fail-closed Gate A/B runner and artifact for slack recovery and binding separation.

### Phase 10: Strong Baselines and Stress Scenario Suite

**Goal**: Experimenters can compare the new controller against strong honest baselines across explicit finite-storage stress regimes.
**Depends on**: Phase 9
**Requirements**: EXP-01, EXP-02, EXP-04
**Success Criteria** (what must be TRUE):

  1. User can run or inspect optimized fixed-time, actuated/semi-actuated, classical max-pressure, capacity-aware pressure, and feasible cycle-based or finite-storage/double-pressure baselines.
  2. User can reproduce and understand the current grid fixed-time counterexample before any broad performance language is used.
  3. User can trigger downstream blockage, spillback, incident/lane capacity drop, oversaturation, turning shock, and switching-loss-sensitive stress scenarios.
  4. User can see infeasible baselines reported honestly rather than replaced by unsafe heuristics.

**Plans**: 1 plan
Plans:
**Wave 1**

- [x] 10-01-PLAN.md — Add strong feasible baselines, explicit stress scenario suite coverage, grid fixed-time metadata, and Phase 10 smoke/spec artifact.

### Phase 11: Long-Horizon Paired-Seed Evidence

**Goal**: Researchers can evaluate closed-loop dominance only in predeclared binding stress regimes using long horizons, paired seeds, and statistical uncertainty.
**Depends on**: Phase 10
**Requirements**: GATE-03, EXP-03, EXP-05
**Success Criteria** (what must be TRUE):

  1. User can run long-horizon closed-loop experiments with 3600–7200s horizons, appropriate warmup, demand multiplier sweeps, and paired seeds where computationally feasible.
  2. User can inspect paired statistical reports with confidence intervals, effect sizes, and multiple-comparison handling where relevant.
  3. User can run Gate C and see closed-loop dominance evaluated only in predeclared binding stress regimes against the strongest feasible baselines.
  4. User can distinguish slack-regime ties/recovery from binding-regime wins in the experiment summaries.

**Plans**: 3 plans
Plans:
**Wave 1**

- [x] 11-01-PLAN.md — Create Phase 11 evidence contracts, paired statistics, and reusable Gate C rule.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 11-02-PLAN.md — Add executable paired-evidence runner, demand scaling, and main-profile fail-closed artifact.

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 11-03-PLAN.md — Add strict Gate C checker and machine-readable paired-evidence gate artifact.

### Phase 12: Reproducibility and Future Claim Inputs

**Goal**: Future paper work receives auditable evidence packages and bounded claim templates generated from raw artifacts, without starting manuscript drafting.
**Depends on**: Phase 11
**Requirements**: CLAIM-03, REPRO-01, REPRO-02, REPRO-03
**Success Criteria** (what must be TRUE):

  1. User can regenerate all new result tables, figure-data files, and claim-audit summaries from raw JSON/CSV artifacts rather than manual transcription.
  2. User can rerun finite-storage separation gates and long-horizon experiment summaries on CPU/SUMO without GPU dependencies.
  3. User can inspect future claim templates and limitations that state strict generalization and binding-regime superiority only, not universal dominance.
  4. User can see simulator-, network-, horizon-, and seed-relative qualifiers preserved in future manuscript-input artifacts without any paper drafting or submission-prep phase.

**Plans**: 2 plans
Plans:
**Wave 1**

- [x] 12-01-PLAN.md — Create Phase 12 source registry, bounded claim/provenance/reproduction builders, CLI, and tests.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 12-02-PLAN.md — Generate and validate real Phase 12 reproducibility package, provenance, table, claim, audit, reproduction, and summary artifacts.

### Phase 12.1: Close v1.1 gap: execute or downgrade Gate C long-horizon evidence (INSERTED)

**Goal:** Researchers can see whether the predeclared Gate C long-horizon evidence passed, failed, or remains inconclusive after full main-profile execution and downstream status refresh.
**Requirements**: GATE-03, EXP-03, EXP-05, CLAIM-03, REPRO-01, REPRO-02, REPRO-03
**Depends on:** Phase 12
**Success Criteria** (what must be TRUE):

  1. User can start or resume the original Phase 11 main profile: 6 binding scenarios × 6 controllers × 20 seeds × 3 demand multipliers = 2160 expected rows.
  2. User can inspect the Phase 11 source artifact and see either all 2160 rows completed or explicit fail-closed reasons for missing/failed/unpaired rows, missing comparators, missing explicit state, or missing action decomposition.
  3. User can run strict Gate C and see the actual `PASSED`, `FAILED`, or `INCONCLUSIVE` outcome without threshold tuning or evidence-family narrowing.
  4. User can regenerate Phase 12 reproducibility and claim-status artifacts from raw sources and see bounded, conservative status propagation.

**Plans:** 2/5 plans executed
Plans:
**Wave 1**

- [x] 12.1-01-PLAN.md — Repair command contract and add progress/resume preflight for 2160-row execution.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 12.1-02-PLAN.md — Execute or resume the full Phase 11 main profile and inspect row completeness.

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 12.1-03-PLAN.md — Regenerate Gate C and enforce strict fail-closed status.

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 12.1-04-PLAN.md — Refresh Phase 12 reproducibility and claim-status artifacts.

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 12.1-05-PLAN.md — Run final verification and update planning/status surfaces.

## Progress

**Execution Order:** Phases execute in numeric order: 6 → 7 → 8 → 9 → 10 → 11 → 12 → 12.1.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Theoretical Core and Claim Lock | v1.0 | 3/3 | Complete | 2026-05-23 |
| 2. Full Sparse Symbolic Recovery | v1.0 | 3/3 | Complete | 2026-05-23 |
| 3. Static Pressure-Failure Kill Gate | v1.0 | 3/3 | Complete | 2026-05-23 |
| 4. Closed-Loop SUMO Evaluation | v1.0 | 3/3 | Complete | 2026-05-23 |
| 5. Reproducibility and Repository Hardening | v1.0 | 3/3 | Complete | 2026-05-23 |
| 6. Claim Discipline and Explicit State Foundation | v1.1 | 3/3 | Complete   | 2026-05-23 |
| 7. Theory and Separation Package | v1.1 | 1/1 | Complete | 2026-05-24 |
| 8. Live Finite-Storage Primal-Dual Controller | v1.1 | 1/1 | Complete | 2026-05-24 |
| 9. Slack and Binding Kill Gates | v1.1 | 1/1 | Complete | 2026-05-24 |
| 10. Strong Baselines and Stress Scenario Suite | v1.1 | 1/1 | Complete | 2026-05-24 |
| 11. Long-Horizon Paired-Seed Evidence | v1.1 | 3/3 | Complete   | 2026-05-24 |
| 12. Reproducibility and Future Claim Inputs | v1.1 | 2/2 | Complete    | 2026-05-24 |
| 12.1. Close v1.1 gap: execute or downgrade Gate C long-horizon evidence | v1.1 | 2/5 | In Progress|  |

## Coverage

| Requirement | Phase |
|-------------|-------|
| CLAIM-01 | Phase 6 |
| CLAIM-02 | Phase 6 |
| CLAIM-03 | Phase 12, Phase 12.1 |
| STATE-01 | Phase 6 |
| STATE-02 | Phase 6 |
| STATE-03 | Phase 6 |
| THRY-01 | Phase 7 |
| THRY-02 | Phase 7 |
| THRY-03 | Phase 7 |
| THRY-04 | Phase 7 |
| CTRL-01 | Phase 8 |
| CTRL-02 | Phase 8 |
| CTRL-03 | Phase 8 |
| CTRL-04 | Phase 8 |
| GATE-01 | Phase 9 |
| GATE-02 | Phase 9 |
| GATE-03 | Phase 11, Phase 12.1 |
| GATE-04 | Phase 9 |
| EXP-01 | Phase 10 |
| EXP-02 | Phase 10 |
| EXP-03 | Phase 11, Phase 12.1 |
| EXP-04 | Phase 10 |
| EXP-05 | Phase 11, Phase 12.1 |
| REPRO-01 | Phase 12, Phase 12.1 |
| REPRO-02 | Phase 12, Phase 12.1 |
| REPRO-03 | Phase 12, Phase 12.1 |

**Coverage:** 26/26 v1.1 requirements mapped; Phase 12.1 adds urgent closure coverage for pending Gate C execution/status propagation; no orphaned requirements.
