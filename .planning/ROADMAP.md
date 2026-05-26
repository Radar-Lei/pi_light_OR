---
phase: 14
slug: v1-4-failure-diagnostics-and-workstream-protocol
status: planned
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-26
---

# Roadmap: PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

## Milestones

- Complete **v1.0 Paper Artifact** — Phases 1-5 shipped 2026-05-23; pressure-equivalent generalized-pressure symbolic recovery artifact archived in [`milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md).
- Complete **v1.1 Explicit Finite-Storage Primal-Dual Separation** — Phases 6-12.1 established claim discipline, finite-storage state/objective fields, slack/binding theory, a live auditable controller, deterministic Gate A/B, strong baseline/stress infrastructure, predeclared Gate C tooling, and fail-closed reproducibility surfaces.
- Complete **v1.3 Complete Predeclared Gate C Evidence** — Phase 13 shipped 2026-05-25; full 2160-row Phase 11 main artifact generated `FAILED`, strict Gate C generated `INCONCLUSIVE`, and Phase 12 regenerated conservative claim surfaces.
- Active **v1.4 Strong Baseline-Dominance Method Search** — Diagnose the v1.3 failure, run parallel method workstreams, select one candidate, lock a new Gate C, and refresh claim surfaces without assuming the strong claim before evidence.

## Overview

v1.4 exists because the desired paper needs a strong closed-loop claim against max-pressure-style baselines, but v1.3 did not support that claim. The milestone therefore treats baseline dominance as a hard predeclared evidence gate. Exploratory workstreams may search for better methods, but final claim eligibility can only come from a locked v1.4 Gate C artifact with status `PASSED`.

The milestone deliberately separates exploration from confirmation:

- Workstream pilot/smoke results can select or reject candidate methods.
- Workstream outputs must remain `claim_ready=false`.
- The selected method must be locked into a protocol before main confirmation rows are generated.
- Strong baselines remain first-class comparators.
- Non-PASSED v1.4 Gate C results preserve closed-loop superiority as disallowed.

## Phases

**Phase Numbering:** continuing from v1.3 Phase 13.

- [x] **Phase 14: v1.4 Failure Diagnostics and Workstream Protocol** - Diagnose v1.3 Gate C failure and define workstream evidence boundaries. (completed 2026-05-26)
- [x] **Phase 15: Parallel Exploratory Method Workstreams** - Execute candidate pilots in the four v1.4 workstreams and mark all pilot evidence as exploratory. (completed 2026-05-26)
- [x] **Phase 16: Candidate Convergence and Protocol Lock** - Select at most one candidate and freeze the v1.4 Gate C protocol before confirmation. (completed 2026-05-26)
- [x] **Phase 17: Locked v1.4 Gate C Execution** - Execute or resume the locked main Gate C against required strong baselines. (completed 2026-05-26)
- [x] **Phase 18: v1.4 Claim Refresh and Milestone Audit** - Regenerate claim/reproducibility surfaces and preserve or allow the strong claim strictly from Gate C status. (completed 2026-05-26)

## Phase Details

### Phase 14: v1.4 Failure Diagnostics and Workstream Protocol

- [x] Phase 14: Complete (completed 2026-05-26)

**Goal:** Researchers can explain why v1.3 failed and can start method workstreams with clear exploratory/claim boundaries.
**Depends on:** Phase 13
**Requirements:** DIAG-01, DIAG-02, DIAG-03, WS-01
**Success Criteria** (what must be TRUE):

1. User can inspect a v1.3 failure diagnostic JSON/Markdown report summarizing bounded harm, inconclusive, non-worsening, and strict-positive-signal results by scenario, demand, comparator, and metric.
2. User can see whether the failure appears driven by controller action weakness, objective mismatch, insufficient binding activation, scenario design, or baseline parity.
3. User can distinguish claim-informative rows from context-only and non-evidence rows.
4. User can inspect all four v1.4 workstreams and their scope, status, artifact paths, and claim-readiness boundary.

**Plans:** 3/3 plans complete

Plans:

**Wave 1**

- [x] 14-01-PLAN.md — Build v1.3 Gate C failure diagnostic artifact and report.
- [x] 14-02-PLAN.md — Audit workstream scopes, artifact naming, and `claim_ready=false` pilot contract.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 14-03-PLAN.md — Define pilot selection criteria and validation commands for each workstream.

### Phase 15: Parallel Exploratory Method Workstreams

- [x] Phase 15: Complete (completed 2026-05-26)

**Goal:** Researchers can evaluate multiple candidate method families without confusing pilot evidence for final claim evidence.
**Depends on:** Phase 14
**Requirements:** WS-02, WS-03
**Success Criteria** (what must be TRUE):

1. Each active workstream produces pilot/smoke artifacts with candidate ID, spec, provenance, action decomposition, and `claim_ready=false`.
2. Candidate pilots are evaluated against the predeclared selection criteria from Phase 14.
3. Each workstream ends with status `rejected`, `candidate`, or `archived`, with explicit reasons.
4. No pilot artifact is imported as final Gate C evidence.

**Plans:** 4/4 plans complete

Plans:

**Wave 1**

- [x] 15-01-PLAN.md — Run `v1-4-score-controller` pilot and record candidate status.
- [x] 15-02-PLAN.md — Run `v1-4-objective-weights` pilot and record candidate status.
- [x] 15-03-PLAN.md — Run `v1-4-scenario-diagnostics` pilot and record candidate status.
- [x] 15-04-PLAN.md — Run `v1-4-symbolic-policy` pilot and record candidate status.

### Phase 16: Candidate Convergence and Protocol Lock

- [x] Phase 16: Complete (completed 2026-05-26)

**Goal:** Researchers can choose at most one candidate and freeze a confirmation protocol before the main v1.4 Gate C.
**Depends on:** Phase 15
**Requirements:** SELECT-01, SELECT-02, SELECT-03, LOCK-01
**Success Criteria** (what must be TRUE):

1. User can inspect a convergence artifact that ranks candidates by non-worsening behavior, strict-positive signals, binding activation, auditability, and implementation reproducibility.
2. At most one candidate is promoted to locked confirmation.
3. Rejected routes record explicit rejection reasons.
4. The selected candidate has controller ID, mechanism description, changed score/objective terms, action-decomposition schema, and reproducible implementation pointer.
5. The v1.4 Gate C protocol is locked before main confirmation rows are generated.

**Plans:** 3/3 plans complete

Plans:

**Wave 1**

- [x] 16-01-PLAN.md — Build workstream convergence and candidate ranking artifact.
- [x] 16-02-PLAN.md — Select or reject candidate routes with explicit decision record.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 16-03-PLAN.md — Generate locked v1.4 Gate C protocol and spec fingerprint.

### Phase 17: Locked v1.4 Gate C Execution

- [x] Phase 17: Complete (completed 2026-05-26)

**Goal:** Researchers can run the selected candidate against strong baselines under the locked confirmation protocol and obtain an honest Gate C status.
**Depends on:** Phase 16
**Requirements:** LOCK-02, LOCK-03, LOCK-04
**Success Criteria** (what must be TRUE):

1. The locked Gate C keeps max-pressure, capacity-aware pressure, and finite-storage double-pressure as required comparators.
2. User can execute or resume all locked main rows and inspect completed, missing, failed, duplicate, unpaired, bad-provenance, and schema-invalid rows.
3. Strict v1.4 Gate C emits exactly `PASSED`, `FAILED`, or `INCONCLUSIVE`.
4. Gate C fails closed on non-PASSED source, missing primary metric, bounded harm, missing comparator, or missing action-decomposition evidence.

**Plans:** 4/4 plans complete

Plans:

**Wave 1**

- [x] 17-01-PLAN.md — Preflight locked v1.4 Gate C spec, environment, row keys, and resume paths.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 17-02-PLAN.md — Execute or resume locked v1.4 main Gate C rows.

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 17-03-PLAN.md — Audit row completeness, pairing, demand provenance, and action decomposition.
- [x] 17-04-PLAN.md — Run strict v1.4 Gate C and preserve generated status.

### Phase 18: v1.4 Claim Refresh and Milestone Audit

- [x] Phase 18: Complete (completed 2026-05-26)

**Goal:** Researchers can regenerate claim/reproducibility surfaces and determine whether the strong closed-loop claim is allowed.
**Depends on:** Phase 17
**Requirements:** CLAIM-01, CLAIM-02, CLAIM-03
**Success Criteria** (what must be TRUE):

1. User can regenerate Phase 12-style reproducibility, provenance, table input, claim input, claim audit, reproduction manifest, and summary artifacts from v1.4 raw outputs.
2. `claim_allowed=true` for closed-loop superiority only if locked v1.4 Gate C is `PASSED`.
3. Non-PASSED Gate C keeps closed-loop superiority `claim_allowed=false`.
4. Generated reports distinguish exploratory pilot evidence, static theory evidence, and locked claim-ready evidence.
5. Milestone audit verifies requirements coverage and flags any overclaim or protocol drift.

**Plans:** 3/3 plans complete

Plans:

**Wave 1**

- [x] 18-01-PLAN.md — Refresh v1.4 reproducibility and claim-status artifacts.
- [x] 18-02-PLAN.md — Run claim audit and update planning surfaces from generated statuses.

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 18-03-PLAN.md — Complete v1.4 milestone audit and next-route recommendation.

## Progress

**Execution Order:** Phase 14 follows Phase 13.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-5 | v1.0 | 15/15 | Complete | 2026-05-23 |
| 6-12.1 | v1.1 | 26/26 | Complete | 2026-05-25 |
| 13. Complete Predeclared Gate C Evidence | v1.3 | 4/4 | Complete | 2026-05-25 |
| 14. v1.4 Failure Diagnostics and Workstream Protocol | v1.4 | 3/3 | Complete    | 2026-05-26 |
| 15. Parallel Exploratory Method Workstreams | v1.4 | 4/4 | Complete    | 2026-05-26 |
| 16. Candidate Convergence and Protocol Lock | v1.4 | 3/3 | Complete    | 2026-05-26 |
| 17. Locked v1.4 Gate C Execution | v1.4 | 4/4 | Complete    | 2026-05-26 |
| 18. v1.4 Claim Refresh and Milestone Audit | v1.4 | 3/3 | Complete    | 2026-05-26 |

## Coverage

| Requirement | Phase |
|-------------|-------|
| DIAG-01 | Phase 14 |
| DIAG-02 | Phase 14 |
| DIAG-03 | Phase 14 |
| WS-01 | Phase 14 |
| WS-02 | Phase 15 |
| WS-03 | Phase 15 |
| SELECT-01 | Phase 16 |
| SELECT-02 | Phase 16 |
| SELECT-03 | Phase 16 |
| LOCK-01 | Phase 16 |
| LOCK-02 | Phase 17 |
| LOCK-03 | Phase 17 |
| LOCK-04 | Phase 17 |
| CLAIM-01 | Phase 18 |
| CLAIM-02 | Phase 18 |
| CLAIM-03 | Phase 18 |

**Coverage:**
- v1.4 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0
- Duplicate phase assignments: 0

---
*Roadmap created: 2026-05-26 for v1.4 Strong Baseline-Dominance Method Search*
