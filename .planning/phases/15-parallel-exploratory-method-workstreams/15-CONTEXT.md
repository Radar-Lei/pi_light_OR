# Phase 15: Parallel Exploratory Method Workstreams - Context

**Gathered:** 2026-05-26
**Status:** Ready for planning
**Mode:** Autonomous smart discuss, user approved automatic defaults

<domain>
## Phase Boundary

Run deterministic pilot/smoke artifacts for each active v1.4 workstream. This phase evaluates candidates against Phase 14 criteria but keeps every pilot artifact exploratory and `claim_ready=false`.

</domain>

<decisions>
## Implementation Decisions

### Pilot Contract
- Each pilot must include candidate ID, spec, provenance, action decomposition, selection criteria results, explicit reasons, and `claim_ready=false`.
- Candidate statuses are limited to `rejected`, `candidate`, or `archived`.
- No pilot artifact may be imported as final Gate C evidence.

### the agent's Discretion
Use deterministic pilot scoring based on Phase 14 diagnostics instead of expensive SUMO execution.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 14 diagnostic payload provides workstream definitions and selection criteria.

### Established Patterns
- JSON outputs live under `experiments/dual_sensitivity/`.

### Integration Points
- Phase 16 consumes `experiments/dual_sensitivity/v1_4_workstreams/index.json`.

</code_context>

<specifics>
## Specific Ideas

Keep exploration and claim confirmation separate.

</specifics>

<deferred>
## Deferred Ideas

Main confirmation rows are deferred to Phase 17.

</deferred>
