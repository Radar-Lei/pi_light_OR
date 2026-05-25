# Requirements: PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

**Defined:** 2026-05-25
**Milestone:** v1.3 Complete Predeclared Gate C Evidence
**Core Value:** Show that finite-storage primal-dual pressure control strictly generalizes max-pressure: it reduces to pressure when constraints are slack, adds scarcity-aware shadow-price corrections when storage, spillback, switching, service, or incident constraints bind, and can be deployed or compressed into auditable symbolic traffic-signal policies.

## v1.3 Requirements

Requirements for the Gate C evidence-closure milestone. Each maps to roadmap Phase 13.

### Evidence Execution

- [ ] **EXEC-01**: Researcher can resume or execute the original Phase 11 main profile for 6 binding regimes x 6 controllers x 20 paired seeds x 3 demand multipliers = 2160 expected rows.
- [ ] **EXEC-02**: Researcher can inspect progress/resume artifacts and see completed row keys, missing row keys, duplicate conflicts, failed rows, and spec-fingerprint compatibility.
- [ ] **EXEC-03**: Researcher can identify whether every required regime/controller/seed/demand-multiplier combination executed or failed closed with an explicit reason.

### Protocol Preservation

- [ ] **PROTO-01**: The milestone preserves the predeclared Gate C controller set, binding regimes, paired seeds, demand multipliers, primary metrics, and thresholds without post-hoc retuning.
- [ ] **PROTO-02**: The milestone preserves required explicit finite-storage state fields, objective components, action decomposition, baseline comparators, and pairing metadata for every claim-eligible row.
- [ ] **PROTO-03**: Partial rows remain debugging/provenance only and are not summarized as early performance evidence.

### Gate C Closure

- [ ] **GATEC-01**: Researcher can rerun strict Gate C from refreshed raw Phase 11 evidence and obtain exactly one fail-closed status: `PASSED`, `FAILED`, or `INCONCLUSIVE`.
- [ ] **GATEC-02**: Gate C fails closed on missing rows, unpaired seeds, missing comparators, runtime failures, missing explicit state, missing action decomposition, or schema-invalid metadata.
- [ ] **GATEC-03**: Gate C output distinguishes slack recovery evidence, static binding separation evidence, and closed-loop binding-regime dominance evidence.

### Reproducibility and Claim Status

- [ ] **REPRO-01**: Researcher can regenerate the Phase 12 reproducibility package, provenance, claim inputs, summaries, and claim audit from raw refreshed artifacts.
- [ ] **REPRO-02**: Phase 12 package status propagates the refreshed Phase 11/Gate C status conservatively without manual edits.
- [ ] **CLAIM-01**: Closed-loop superiority remains `claim_allowed=false` unless all predeclared Gate C completeness and dominance checks pass.
- [ ] **CLAIM-02**: Manuscript drafting, related-work writing, final paper integration, submission preparation, and polished paper figures remain out of scope for v1.3.

## Future Requirements

Deferred to future milestones after v1.3 determines the Gate C outcome.

### Manuscript and Presentation

- **MS-01**: Draft the TR-B / Transportation Science manuscript using only claims allowed by the completed Gate C and reproducibility package.
- **MS-02**: Convert Phase 7 static separation and any completed Gate C evidence into polished paper figures, tables, captions, and theorem statements.
- **MS-03**: Run external review or kill-argument on the full manuscript before submission.

### Benchmark Expansion

- **BENCH-01**: Add RESCO, CityFlow, LibSignal, or larger real-world benchmarks if the v1.3 Gate C outcome supports continuing the empirical performance route.
- **BENCH-02**: Add neural or PI-Light-family baselines only as secondary evidence if they can be run honestly without shifting the paper into benchmark chasing.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| New controllers or new score terms | v1.3 must close the predeclared Gate C evidence, not change the tested method. |
| New scenarios, metrics, thresholds, or seed plans | Post-hoc changes would invalidate the Phase 11/Gate C protocol. |
| Interpreting 57/2160 partial rows as results | Partial rows are debugging/provenance only until the full predeclared row set is complete or fail-closed. |
| Manuscript drafting or final paper integration | User explicitly requested not to start writing; v1.3 is evidence closure only. |
| Universal superiority claims over max-pressure | The allowed empirical claim is bounded to predeclared binding regimes and only if Gate C passes. |
| Reclassifying `full_dual_symbolic` as feasible | Phase 8 preserved that path as not feasible; v1.3 should not alter controller feasibility labels. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| EXEC-01 | Phase 13 | Pending |
| EXEC-02 | Phase 13 | Pending |
| EXEC-03 | Phase 13 | Pending |
| PROTO-01 | Phase 13 | Pending |
| PROTO-02 | Phase 13 | Pending |
| PROTO-03 | Phase 13 | Pending |
| GATEC-01 | Phase 13 | Pending |
| GATEC-02 | Phase 13 | Pending |
| GATEC-03 | Phase 13 | Pending |
| REPRO-01 | Phase 13 | Pending |
| REPRO-02 | Phase 13 | Pending |
| CLAIM-01 | Phase 13 | Pending |
| CLAIM-02 | Phase 13 | Pending |

**Coverage:**
- v1.3 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0
- Duplicate phase assignments: 0

---
*Requirements defined: 2026-05-25*
*Last updated: 2026-05-25 after v1.3 milestone initialization*
