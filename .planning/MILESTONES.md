# Milestones

## v1.3 Complete Predeclared Gate C Evidence (Shipped: 2026-05-25)

**Phases completed:** 1 phases, 4 plans, 0 tasks
**Audit:** Passed; 13/13 v1.3 requirements satisfied; no critical blockers.

**Key accomplishments:**

- Completed the locked Phase 11 main profile at 2160/2160 predeclared rows with generated status `FAILED`.
- Preserved protocol discipline: no controller, scenario, seed, demand multiplier, metric, threshold, or evidence-family changes.
- Reran strict Gate C from refreshed raw evidence and preserved generated status `INCONCLUSIVE`.
- Regenerated Phase 12 reproducibility, provenance, table input, claim input, claim audit, reproduction manifest, and summary artifacts.
- Propagated non-PASSED Phase 11/Gate C statuses conservatively: closed-loop superiority remains `claim_allowed=false`.

**Archived:**

- [`milestones/v1.3-ROADMAP.md`](milestones/v1.3-ROADMAP.md)
- [`milestones/v1.3-REQUIREMENTS.md`](milestones/v1.3-REQUIREMENTS.md)
- [`milestones/v1.3-MILESTONE-AUDIT.md`](milestones/v1.3-MILESTONE-AUDIT.md)

---

## v1.0 Paper Artifact (Shipped: 2026-05-23)

**Phases completed:** 5 phases, 15 plans, 20 tasks
**Audit:** Tech debt only; 25/25 scoped Phase 1–5 requirements satisfied; no critical blockers.
**Known deferred items at close:** 7 categories tracked in `.planning/STATE.md` Deferred Items.

**Key accomplishments:**

- Built continuous capacitated traffic-network relaxation and dual-sensitivity decomposition aligned to the Block 0 LP sanity scaffold.
- Proved pressure/backpressure recovery as a special case and formalized binding-regime scarcity rank-change routing.
- Added finite-dictionary oracle-regret recovery quality statement and reviewer-facing THRY traceability.
- Implemented K-atom sparse symbolic recovery with auditable atom metadata, oracle-regret objective, and size/neighbor/dual/placebo controls.
- Emitted schema-gated sparse recovery JSON, run-level CSV, and plain-text score rules.
- Generated deterministic static-regime fixtures and per-regime dual-vs-pressure kill-gate metrics.
- Locked the static/sample-relative route to pressure-equivalent generalized-pressure symbolic recovery framing.
- Built real SUMO/TraCI closed-loop smoke and multi-network suite artifacts for single, arterial, grid, demand-shift, and bottleneck/failure-mode scenarios.
- Rendered closed-loop Markdown/CSV reports with gate validation and overclaim guardrails.
- Created repository-level reproducibility assets: README, environment.yml, block reproduction harness, artifact audit manifest, and script-generated paper table/figure data.

**Archived:**

- [`milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md)
- [`milestones/v1.0-REQUIREMENTS.md`](milestones/v1.0-REQUIREMENTS.md)
- [`milestones/v1.0-MILESTONE-AUDIT.md`](milestones/v1.0-MILESTONE-AUDIT.md)

---
