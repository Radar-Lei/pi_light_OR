# Phase 16: Candidate Convergence and Protocol Lock - Context

**Gathered:** 2026-05-26
**Status:** Ready for planning
**Mode:** Autonomous smart discuss, user approved automatic defaults

<domain>
## Phase Boundary

Rank Phase 15 exploratory candidates, select at most one route, reject or archive the rest, and write a locked v1.4 Gate C protocol before Phase 17 creates any confirmation rows.

</domain>

<decisions>
## Implementation Decisions

### Selection Discipline
- At most one candidate may be promoted.
- Selection depends on non-worsening behavior, strict-positive signals, binding activation, auditability, and reproducibility.
- Selected candidate is still not claim-ready until locked Phase 17 Gate C passes.

### Protocol Lock
- Required comparators remain max-pressure, capacity-aware pressure, and finite-storage double-pressure.
- The protocol records a spec fingerprint before main confirmation.

### the agent's Discretion
Use deterministic ranking over Phase 15 pilot artifacts.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/run_phase11_paired_evidence.py` defines the locked scenario/comparator/metric families.
- Phase 15 pilot index provides candidate statuses and criteria.

### Established Patterns
- Fail-closed JSON protocol artifacts are preferred over prose-only decisions.

### Integration Points
- Phase 17 should consume `experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json`.

</code_context>

<specifics>
## Specific Ideas

Promote the best candidate only if it satisfies the required lock criteria.

</specifics>

<deferred>
## Deferred Ideas

Gate C execution and claim refresh remain in Phases 17 and 18.

</deferred>
