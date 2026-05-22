# Roadmap: PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

## Overview

This roadmap turns the project into a TR-B / Transportation Science research artifact by moving from a rigorous continuous capacitated network relaxation to dual movement sensitivity, sparse symbolic recovery, pressure-failure kill-gate evidence, closed-loop SUMO validation, reproducible repository artifacts, and a manuscript skeleton. The central gate is Phase 3: if dual sensitivity beats pressure in binding regimes, the project continues as a strong generalized max-pressure contribution; if it ties pressure, the framing downgrades to generalized-pressure symbolic recovery; if it underperforms, the paper pivots to diagnostic framing.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Theoretical Core and Claim Lock** - Lock the capacitated relaxation, dual decomposition, pressure special case, scarcity correction, and recoverability claim. (completed 2026-05-22)
- [ ] **Phase 2: Full Sparse Symbolic Recovery** - Implement auditable K-atom recovery with oracle-regret objective, complexity penalties, and full atom families.
- [ ] **Phase 3: Static Pressure-Failure Kill Gate** - Decide the paper route by testing dual-vs-pressure behavior across slack and binding static regimes.
- [ ] **Phase 4: Closed-Loop SUMO Evaluation** - Validate the selected claim route in closed-loop SUMO against strong traffic-control baselines.
- [ ] **Phase 5: Reproducibility and Repository Hardening** - Make the repository rerunnable, auditable, and table/figure reproducible from raw artifacts.

## Gate Routing

Phase 3 is the project kill gate and controls the downstream claim strength:

1. **Dual beats pressure in binding regimes**: continue the strong mainline claim that dual sensitivity extends max-pressure with scarcity-aware corrections under storage, supply, spillback, or corridor bottleneck constraints.
2. **Dual ties pressure**: downgrade the contribution to generalized-pressure symbolic recovery, emphasizing theory-backed equivalence, compact symbolic compression, and reproducible closed-loop evidence without dominance claims.
3. **Dual performs worse than pressure**: pivot to diagnostic framing, explaining where continuous-relaxation dual signals fail as deployable pressure surrogates and preserving the artifact as a negative/diagnostic OR-control study.

## Phase Details

### Phase 1: Theoretical Core and Claim Lock

**Goal**: The project has a venue-credible OR/control theory core that explains dual movement sensitivity as generalized max-pressure and precisely states when pressure equivalence or scarcity correction should occur.
**Depends on**: Nothing (first phase)
**Dependencies**: Existing Block 0 dual sanity scaffold and current PROJECT.md claim discipline.
**Requirements**: THRY-01, THRY-02, THRY-03, THRY-04, THRY-05
**Requirements Covered**: THRY-01, THRY-02, THRY-03, THRY-04, THRY-05
**Success Criteria** (what must be TRUE):

  1. The manuscript notes or technical memo state a continuous capacitated network relaxation with queue conservation, movement service, phase compatibility, and capacity/storage/supply constraints.
  2. A reader can trace each movement-level dual-sensitivity term to upstream value, downstream value, storage/supply scarcity, or corridor/service correction.
  3. The theory section clearly proves or formalizes why ordinary max-pressure/backpressure is recovered when binding constraints are absent or ranking-neutral.
  4. The theory section identifies binding-regime conditions under which dual sensitivity may legitimately differ from ordinary pressure.
  5. The symbolic recovery target has an explicit recovery-regret or finite-dictionary optimization-quality statement.

**Verification/UAT (artifact acceptance checks)**:

  1. A theory artifact contains definitions, assumptions, propositions, and proof sketches for THRY-01 through THRY-05.
  2. The claim language avoids universal dominance over pressure and matches PROJECT.md constraints.
  3. A reviewer-facing checklist can map every theorem/proposition to the intended TR-B / Transportation Science contribution.

**Plans**: 3 plans
Plans:
**Wave 1**

- [x] 01-01-PLAN.md — Define the continuous capacitated relaxation and movement-level dual-sensitivity decomposition.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02-PLAN.md — Formalize pressure/backpressure as a special case and binding-regime scarcity corrections.

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 01-03-PLAN.md — Add finite-dictionary recovery quality and reviewer-facing claim checklist.

### Phase 2: Full Sparse Symbolic Recovery

**Goal**: The code can recover compact, auditable symbolic signal-control policies from dual-guided oracle targets while explicitly trading off regret, program size, neighbor use, and dual-price dependence.
**Depends on**: Phase 1
**Dependencies**: Locked theory definitions from Phase 1; existing static recovery scaffolds.
**Requirements**: RECV-01, RECV-02, RECV-03, RECV-04, RECV-05
**Requirements Covered**: RECV-01, RECV-02, RECV-03, RECV-04, RECV-05
**Success Criteria** (what must be TRUE):

  1. The recovery pipeline can solve K-atom symbolic policies beyond one-atom pilots.
  2. Recovery selection is driven by oracle regret or value gap rather than imitation accuracy alone.
  3. The recovered policies expose program-size, neighbor-atom, and dual-price-atom tradeoffs.
  4. The atom library covers local pressure, downstream capacity/slack, raw neighbor queues, pressure/backpressure, dual sensitivity, and random/permuted dual placebo families.
  5. Each recovery run emits auditable rule text plus selected atoms, solve time, oracle regret, action agreement, program length, neighbor count, and dual atom count.

**Verification/UAT (artifact acceptance checks)**:

  1. A sample recovery command produces structured JSON/CSV outputs and human-readable symbolic rules.
  2. Placebo/random dual atoms are available and reported separately from genuine dual-sensitivity atoms.
  3. Equal-complexity comparisons can be reproduced without manual result transcription.

**Plans**: TBD

### Phase 3: Static Pressure-Failure Kill Gate

**Goal**: Static benchmark evidence determines whether the paper can claim dual sensitivity improves pressure in binding regimes, should present pressure-equivalent symbolic recovery, or must pivot to diagnostic framing.
**Depends on**: Phase 2
**Dependencies**: Full recovery outputs from Phase 2; theory expectations from Phase 1.
**Requirements**: KILL-01, KILL-02, KILL-03, KILL-04, KILL-05
**Requirements Covered**: KILL-01, KILL-02, KILL-03, KILL-04, KILL-05
**Success Criteria** (what must be TRUE):

  1. Static regimes include slack, downstream storage-binding, supply-binding, corridor-bottleneck, incident/capacity-drop, and demand-shift cases.
  2. Each regime reports disagreement rate, dual win rate, mean oracle regret, worst-case regret, and recovered symbolic rules for dual-vs-pressure comparison.
  3. The main pressure-failure analysis uses enough sampled states to support stable conclusions, targeting at least 1k states.
  4. The artifact explicitly classifies the result as dual-improves-pressure, dual-recovers-pressure, or dual-underperforms-pressure.
  5. The selected claim route is documented before closed-loop experiments are interpreted.

**Verification/UAT (artifact acceptance checks)**:

  1. A static kill-gate report/table can be regenerated from raw sampled-state artifacts.
  2. The report includes the three routing outcomes: strong mainline, generalized-pressure symbolic recovery, or diagnostic framing.
  3. Downstream Phase 4 experiment priorities are updated to match the selected gate route.

**Plans**: TBD

### Phase 4: Closed-Loop SUMO Evaluation

**Goal**: Closed-loop SUMO experiments provide credible computational evidence for the Phase 3-selected claim route against strong max-pressure-style, symbolic, placebo, and practical baselines.
**Depends on**: Phase 3
**Dependencies**: Phase 3 gate routing decision; runnable SUMO network assets and controllers.
**Requirements**: CLOP-01, CLOP-02, CLOP-03, CLOP-04, CLOP-05
**Requirements Covered**: CLOP-01, CLOP-02, CLOP-03, CLOP-04, CLOP-05
**Success Criteria** (what must be TRUE):

  1. Closed-loop experiments cover single-intersection sanity, 5-intersection arterial main case, grid scalability, and robustness/demand-shift scenarios.
  2. Comparisons include fixed-time, actuated/local pressure, max-pressure/backpressure, capacity/spillback-aware pressure, local PI-Light, raw-neighbor symbolic, all-neighbor symbolic, random/permuted dual, and full dual-symbolic policies where feasible.
  3. Main arterial and grid comparisons run enough seeds to support confidence intervals, targeting 5–10 seeds.
  4. Outputs report travel time, delay, throughput/completed vehicles, mean/max queues, spillback/blocking counts, switching counts, and controller runtime.
  5. At least one closed-loop scenario is designed around storage, supply, spillback, or corridor bottleneck failure modes for ordinary pressure.

**Verification/UAT (artifact acceptance checks)**:

  1. Experiment outputs are structured and include raw per-seed metrics plus aggregate confidence intervals.
  2. Baseline comparisons are honest: max-pressure and capacity/spillback-aware variants are first-class baselines, not strawmen.
  3. Closed-loop interpretation follows the Phase 3 gate route and does not overclaim beyond the evidence.

**Plans**: TBD

### Phase 5: Reproducibility and Repository Hardening

**Goal**: The repository becomes a paper artifact whose key theory checks, static analyses, closed-loop experiments, and paper tables/figures can be rerun and audited.
**Depends on**: Phase 4
**Dependencies**: Stable experiment commands and output schemas from Phases 2–4.
**Requirements**: REPR-01, REPR-02, REPR-03, REPR-04, REPR-05
**Requirements Covered**: REPR-01, REPR-02, REPR-03, REPR-04, REPR-05
**Success Criteria** (what must be TRUE):

  1. The root README states the research question, contribution claim, current status, reproduction commands, known limitations, and next experiments.
  2. The environment specification can recreate the CPU/SUMO/optimization workflow without GPU dependence.
  3. Experiment scripts are organized or named by block for Block 0, static recovery, closed-loop evaluation, and table generation.
  4. Every reported experiment emits structured JSON/CSV artifacts sufficient to regenerate tables and figures.
  5. Paper tables and figures are generated by scripts from raw artifacts rather than manual transcription.

**Verification/UAT (artifact acceptance checks)**:

  1. A fresh-reader reproduction path can identify which commands regenerate key static and closed-loop results.
  2. Generated tables/figures are traceable to raw artifacts by file path and script.
  3. Known limitations are stated in the repository rather than hidden in ad hoc notes.

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Theoretical Core and Claim Lock | 3/3 | Complete   | 2026-05-22 |
| 2. Full Sparse Symbolic Recovery | 0/TBD | Not started | - |
| 3. Static Pressure-Failure Kill Gate | 0/TBD | Not started | - |
| 4. Closed-Loop SUMO Evaluation | 0/TBD | Not started | - |
| 5. Reproducibility and Repository Hardening | 0/TBD | Not started | - |

## Requirement Coverage

| Requirement | Phase |
|-------------|-------|
| THRY-01 | Phase 1 |
| THRY-02 | Phase 1 |
| THRY-03 | Phase 1 |
| THRY-04 | Phase 1 |
| THRY-05 | Phase 1 |
| RECV-01 | Phase 2 |
| RECV-02 | Phase 2 |
| RECV-03 | Phase 2 |
| RECV-04 | Phase 2 |
| RECV-05 | Phase 2 |
| KILL-01 | Phase 3 |
| KILL-02 | Phase 3 |
| KILL-03 | Phase 3 |
| KILL-04 | Phase 3 |
| KILL-05 | Phase 3 |
| CLOP-01 | Phase 4 |
| CLOP-02 | Phase 4 |
| CLOP-03 | Phase 4 |
| CLOP-04 | Phase 4 |
| CLOP-05 | Phase 4 |
| REPR-01 | Phase 5 |
| REPR-02 | Phase 5 |
| REPR-03 | Phase 5 |
| REPR-04 | Phase 5 |
| REPR-05 | Phase 5 |

**Coverage:** 25/25 v1 requirements mapped; no orphaned requirements; no duplicate mappings.
