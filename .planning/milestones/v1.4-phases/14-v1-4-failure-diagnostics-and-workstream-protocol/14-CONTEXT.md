# Phase 14: v1.4 Failure Diagnostics and Workstream Protocol - Context

**Gathered:** 2026-05-26
**Status:** Ready for planning
**Mode:** Autonomous smart discuss, user approved automatic defaults

<domain>
## Phase Boundary

Explain why v1.3 failed Gate C and define four v1.4 exploratory workstreams. This phase may produce diagnostics, workstream scopes, selection criteria, and validation commands. It must not create final claim-ready evidence.

</domain>

<decisions>
## Implementation Decisions

### Evidence Boundary
- Treat v1.3 `FAILED` and strict Gate C `INCONCLUSIVE` as authoritative inputs.
- Preserve all v1.4 workstream outputs as `claim_ready=false`.
- Distinguish claim-informative Gate C metric rows from context-only and non-evidence rows.

### Diagnostics
- Summarize bounded harm, inconclusive, non-worsening, and strict-positive-signal results by scenario, demand, comparator, and metric.
- Include driver assessments for controller action weakness, objective mismatch, insufficient binding activation, scenario design, and baseline parity.

### the agent's Discretion
Implementation details may use deterministic Python summaries over the existing JSON artifacts.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/run_gate_c_paired_evidence.py` owns strict Gate C payload structure.
- `scripts/run_phase11_paired_evidence.py` defines scenarios, comparators, metrics, and controller IDs.

### Established Patterns
- Evidence scripts write JSON under `experiments/dual_sensitivity/` and expose CLI defaults.
- Tests import scripts through `tests/` with `sys.path.insert(0, "scripts")`.

### Integration Points
- Phase 15 consumes `experiments/dual_sensitivity/v1_4_failure_diagnostics.json`.

</code_context>

<specifics>
## Specific Ideas

Use v1.3 failure as an input to method search, not as a claim rescue.

</specifics>

<deferred>
## Deferred Ideas

Locked main Gate C execution is deferred to Phase 17.

</deferred>
