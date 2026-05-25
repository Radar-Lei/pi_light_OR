# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Paper Artifact

**Shipped:** 2026-05-23
**Phases:** 5 | **Plans:** 15 | **Sessions:** N/A

### What Was Built

- Continuous capacitated traffic-network relaxation, dual-sensitivity decomposition, pressure/backpressure special case, binding-regime scarcity correction, and finite-dictionary recovery quality artifacts.
- K-atom sparse symbolic recovery with oracle-regret objective, atom-family metadata, budget/penalty controls, and auditable JSON/CSV/rule outputs.
- Static pressure-failure kill-gate that routed the paper to pressure-equivalent generalized-pressure symbolic recovery.
- Real SUMO/TraCI closed-loop suite covering single, arterial, grid, demand-shift, and bottleneck/failure-mode scenarios with CI-ready raw and aggregate artifacts.
- Reproducibility surface: root README, CPU/SUMO environment, block reproduction harness, artifact audit manifest, and raw-artifact-generated paper table/figure data.

### What Worked

- The Phase 3 kill gate prevented overcommitting to dual-superiority claims and kept downstream evaluation claim-disciplined.
- Treating max-pressure and capacity-aware pressure as first-class baselines made the closed-loop evidence more credible for OR/control reviewers.
- Fail-closed renderers and artifact manifests reduced manual transcription risk for paper-facing outputs.

### What Was Inefficient

- `CLOP-*` and `REPR-*` completion status was not synchronized back into `.planning/REQUIREMENTS.md` before close, requiring manual archive correction.
- Some summary-extraction paths missed Phase 4/5 one-liners because the summary frontmatter shape varied.
- Phase 3 consumes Phase 2 recovery code directly instead of generated Phase 2 artifacts, leaving weaker artifact-level handoff semantics.

### Patterns Established

- Use pressure-equivalent route metadata as a project-wide guardrail in reports, manifests, and paper artifacts.
- Mark infeasible baselines explicitly rather than relabeling unrelated heuristics.
- Generate human-facing reports and paper CSVs deterministically from raw JSON/CSV artifacts.

### Key Lessons

1. Kill gates are most useful when they route claims, not just pass/fail implementation.
2. Requirements status must be updated at phase completion, not only inferred during audit.
3. Reviewer-facing credibility improves when limitations and infeasible baselines are encoded in artifacts rather than prose afterthoughts.

### Cost Observations

- Model mix: N/A
- Sessions: N/A
- Notable: Local CPU/SUMO execution was sufficient for v1.0, but short closed-loop horizons remain a manuscript-review risk.

---

## Milestone: v1.3 — Complete Predeclared Gate C Evidence

**Shipped:** 2026-05-25
**Phases:** 1 | **Plans:** 4 | **Sessions:** 1

### What Was Built

- Completed the original Phase 11 main profile to 2160/2160 predeclared rows with progress/resume provenance.
- Refreshed strict Gate C from raw Phase 11 evidence and preserved generated status `INCONCLUSIVE`.
- Regenerated Phase 12 reproducibility, provenance, table input, claim input, claim audit, reproduction manifest, and summary artifacts.
- Updated planning, verification, and milestone archives to reflect the fail-closed empirical result.

### What Worked

- Row-level resume made a long SUMO run practical without modifying the evidence family.
- The predeclared protocol prevented threshold tuning or controller/scenario changes after seeing the result.
- Phase 12 claim inputs correctly propagated non-PASSED upstream statuses into `claim_allowed=false`.

### What Was Inefficient

- The long-horizon run dominated wall-clock time and produced many SUMO warnings, even though the process remained healthy.
- Planning metadata needed manual reconciliation after artifact generation because summaries did not include enough structured requirement-completion frontmatter for fully automatic audit extraction.
- The milestone completion CLI created archives but left live project framing stale enough to require manual PROJECT/ROADMAP cleanup.

### Patterns Established

- Complete empirical closure can be valuable even when the result is non-PASSED; the artifact now distinguishes completeness from dominance.
- Strict mode nonzero exits are acceptable evidence when they generate explicit fail-closed artifacts.
- Claim surfaces should quote generated statuses directly and avoid narrative upgrades.

### Key Lessons

1. Do not treat incomplete evidence as merely "pending" once the full predeclared run is feasible; execute it or explicitly fail closed.
2. A complete negative/fail-closed Gate C result should route the next research decision, not trigger post-hoc retuning inside the same evidence family.
3. GSD summaries should include structured requirements-completed metadata if milestone audit automation is expected to be fully reliable.

### Cost Observations

- Model mix: N/A
- Sessions: 1
- Notable: SUMO execution, not agent reasoning, was the bottleneck.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | N/A | 5 | Shifted from idea/prototype to archived pressure-equivalent paper artifact with reproducible evidence. |
| v1.3 | 1 | 1 | Converted partial Gate C evidence into a complete fail-closed empirical result. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | Python compile checks, stdlib tests, artifact assertions, milestone audit | 25/25 scoped requirements satisfied | No required GPU/model-serving dependency added |
| v1.3 | Phase 11/12 fast assertion suites, row audit, strict Gate C, strict Phase 12 fail-closed validation | 13/13 requirements satisfied | No new dependency; reused SUMO/Python pipeline |

### Top Lessons (Verified Across Milestones)

1. Keep claim discipline encoded in generated artifacts and validation gates.
2. Archive requirements only after stale checkboxes have been reconciled with verification evidence.
3. Preserve non-PASSED empirical outcomes as first-class scientific routing signals instead of treating them as implementation failures.
