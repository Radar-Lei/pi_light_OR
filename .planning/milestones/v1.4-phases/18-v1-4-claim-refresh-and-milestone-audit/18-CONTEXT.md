# Phase 18: v1.4 Claim Refresh and Milestone Audit - Context

**Gathered:** 2026-05-26
**Status:** Ready for planning
**Mode:** Autonomous smart discuss, user approved automatic defaults

<domain>
## Phase Boundary

Regenerate v1.4-specific reproducibility, provenance, table, claim-input, claim-audit, reproduction-manifest, summary, and milestone-audit artifacts from the v1.4 raw outputs. Closed-loop superiority may be allowed only if `experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json` is `PASSED`; the current locked Gate C is `INCONCLUSIVE`, so claim refresh must preserve `claim_allowed=false`.

</domain>

<decisions>
## Implementation Decisions

### Claim Refresh
- Write v1.4-specific outputs with `v1_4_` names rather than overwriting Phase 12 artifacts.
- Treat diagnostics, workstream pilots, and convergence outputs as exploratory or selection evidence, not final claim evidence.
- Treat locked execution and strict Gate C as the only closed-loop confirmation sources.

### Claim Allowance
- `claim_allowed=true` is permitted only when strict v1.4 Gate C status is `PASSED`.
- Non-PASSED Gate C statuses keep closed-loop superiority disallowed and preserve fail-closed reasons.
- Generated summaries must distinguish exploratory pilot evidence from locked Gate C evidence.

### Milestone Audit
- Verify v1.4 requirements coverage from planning state and generated artifacts.
- Flag protocol drift if execution/gate artifacts disagree with the locked protocol fingerprint, selected controller, or required comparators.
- Flag overclaim if any generated surface allows closed-loop superiority while Gate C is not `PASSED`.

### the agent's Discretion
Use deterministic JSON/CSV/Markdown generation and lightweight tests. Do not launch expensive SUMO rows.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/run_phase12_reproducibility_inputs.py` shows the package/provenance/claim-audit pattern.
- `scripts/claim_policy.py` provides forbidden claim scanning.
- Phase 14-17 artifacts already expose diagnostics, workstream boundaries, locked protocol, locked execution, and strict Gate C status.

### Established Patterns
- Generated claim surfaces are machine-readable and fail closed.
- Strict modes exit nonzero when upstream evidence is non-PASSED, while non-strict modes still write audit artifacts.

### Integration Points
- `experiments/dual_sensitivity/v1_4_claim_inputs.json`
- `experiments/dual_sensitivity/v1_4_claim_audit.json`
- `experiments/dual_sensitivity/v1_4_reproducibility_package.json`
- `experiments/dual_sensitivity/v1_4_milestone_audit.json`

</code_context>

<specifics>
## Specific Ideas

Current strict v1.4 Gate C is `INCONCLUSIVE` because no locked main SUMO rows have been executed. The v1.4 claim package must state this as a claim boundary, not as a method win.

</specifics>

<deferred>
## Deferred Ideas

Full manuscript drafting and broader benchmark integration remain deferred until a future milestone has PASSED locked Gate C evidence.

</deferred>
