# Phase 13: Complete Predeclared Gate C Evidence - Context

**Gathered:** 2026-05-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Complete the predeclared Phase 11/Gate C closed-loop evidence closure by resuming or executing the original 2160-row main profile, auditing all row-level coverage and failure modes, rerunning strict Gate C from refreshed raw artifacts, and regenerating the Phase 12 reproducibility/provenance/claim-status package. This phase is evidence closure only: it must not add controllers, change thresholds, change metrics, narrow evidence families, reinterpret partial rows, or start manuscript drafting.

</domain>

<decisions>
## Implementation Decisions

### Evidence Execution Scope
- Execute or resume the original Phase 11 `main` profile: 6 binding regimes x 6 controllers x 20 paired seeds x 3 demand multipliers = 2160 expected rows.
- Treat the existing 57/2160 partial rows as debugging/provenance only until the full predeclared row family is complete or explicitly fail-closed.
- Preserve spec fingerprints, expected row keys, progress/resume artifacts, and compatibility checks so stale or incompatible partial output cannot be silently reused.
- Any execution shortfall must be reported with explicit row keys and reasons rather than summarized away.

### Protocol Preservation
- Keep the predeclared Gate C controller set, binding regimes, paired seeds, demand multipliers, primary metrics, thresholds, and fail-closed rules unchanged.
- Do not introduce new controllers, scenarios, metrics, thresholds, evidence families, manuscript claims, or paper figures in this milestone.
- Preserve required finite-storage state fields, objective components, action decomposition, comparator metadata, pairing metadata, and demand multiplier metadata for every claim-eligible row.
- Keep `local_pilight` and old `full_dual_symbolic` guarded as not feasible unless an already committed prior decision is explicitly superseded in a later milestone.

### Gate C Interpretation
- Rerun strict Gate C from raw refreshed Phase 11 evidence and report exactly one status: `PASSED`, `FAILED`, or `INCONCLUSIVE`.
- Gate C must fail closed on missing rows, failed rows, duplicate/conflicting rows, unpaired seeds, schema-invalid metadata, missing comparators, missing finite-storage state, or missing action decomposition.
- If full execution finishes but strict Gate C fails statistically or structurally, record the failure honestly; do not tune thresholds, alter the comparator set, or narrow the evidence family after seeing results.
- Closed-loop superiority remains disallowed unless all predeclared Gate C completeness and dominance checks pass.

### Reproducibility and Claim Status Refresh
- Regenerate Phase 12 reproducibility, provenance, claim inputs, summaries, and claim audit from raw refreshed artifacts after Gate C reruns.
- Propagate Phase 11/Gate C status conservatively into Phase 12 package outputs without manual status edits.
- Preserve bounded claim language: simulator-, network-, horizon-, seed-, demand-multiplier-, and binding-regime-relative only.
- Keep manuscript drafting, related-work writing, final paper integration, submission preparation, and polished paper figures out of scope.

### the agent's Discretion
- The agent may choose safe execution mechanics such as batching, resume commands, logging, timeout management, and intermediate audits.
- The agent may add or strengthen validation helpers if they preserve the predeclared protocol and make coverage/failure reporting more explicit.
- The agent may choose exact verification commands and artifact-refresh ordering, provided refreshed outputs trace back to raw evidence and fail closed.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Existing Phase 11 artifact family: `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` and `experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json`.
- Existing Phase 12 artifact family and claim audit machinery consume Phase 11/Gate C status and must be refreshed after evidence execution.
- SUMO/TraCI execution is local and CPU-oriented; progress/resume support from Phase 12.1 wraps the existing experiment spec and `run_experiment` path.
- Codebase maps identify `scripts/` as the right home for OR/SUMO experiment CLIs and `experiments/dual_sensitivity/` as the authoritative generated artifact directory.

### Established Patterns
- Research gates write compact JSON payloads with explicit `status` fields and fail nonzero or fail closed when strict prerequisites are missing.
- Validation favors deterministic script-based gates and generated artifacts rather than a conventional pytest suite.
- Generated reports must distinguish `PASSED`, `FAILED`, `INCONCLUSIVE`, and partial/provenance-only rows instead of inferring evidence from incomplete artifacts.
- Existing planning decisions prioritize conservative TR-B / Transportation Science claim discipline over optimistic benchmark interpretation.

### Integration Points
- Phase 13 should connect to existing Phase 11 execution/resume commands, strict Gate C checker, progress/resume JSON, and Phase 12 reproduction/claim package scripts.
- The final status must update `.planning/STATE.md`, `.planning/ROADMAP.md`, phase summaries, verification artifacts, and regenerated experiment artifacts consistently.
- Any long-running SUMO execution should be resumable and auditable from row-level progress files.

</code_context>

<specifics>
## Specific Ideas

The user requested autonomous execution from Phase 13 and asked not to be interrupted unless necessary. Prior Phase 12.1 context explicitly chose complete execution over downgrade or partial evidence, with fail-closed handling for missing or failed rows and preservation of the original Phase 11 main profile.

</specifics>

<deferred>
## Deferred Ideas

Manuscript drafting, related-work writing, final paper integration, submission preparation, polished paper figures, new benchmarks, new controllers, new thresholds, and new metrics remain deferred to future milestones after Gate C status is known.

</deferred>
