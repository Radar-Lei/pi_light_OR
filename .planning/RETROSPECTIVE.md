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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | N/A | 5 | Shifted from idea/prototype to archived pressure-equivalent paper artifact with reproducible evidence. |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | Python compile checks, stdlib tests, artifact assertions, milestone audit | 25/25 scoped requirements satisfied | No required GPU/model-serving dependency added |

### Top Lessons (Verified Across Milestones)

1. Keep claim discipline encoded in generated artifacts and validation gates.
2. Archive requirements only after stale checkboxes have been reconciled with verification evidence.
