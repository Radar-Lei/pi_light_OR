# Phase 17: Locked v1.4 Gate C Execution - Context

**Gathered:** 2026-05-26
**Status:** Ready for planning
**Mode:** Autonomous smart discuss, user approved automatic defaults

<domain>
## Phase Boundary

Execute or resume the locked v1.4 Gate C confirmation protocol from `experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json`, preserving the Phase 16 candidate selection and required strong comparators. This phase may implement execution plumbing and fail-closed audit surfaces, but it must not alter the selected candidate, scenarios, seeds, demand multipliers, primary metrics, or required comparators after confirmation begins.

</domain>

<decisions>
## Implementation Decisions

### Locked Protocol Consumption
- Use the Phase 16 protocol as the authoritative source for selected controller, required comparators, scenarios, seeds, demand multipliers, horizon, warmup, and fingerprint.
- Preserve `max_pressure`, `capacity_aware_pressure`, and `finite_storage_double_pressure` as required comparators.
- Keep exploratory pilot artifacts non-claim-ready and never import them as final Gate C rows.

### Execution and Resume
- Add a v1.4-specific execution wrapper that can run, resume, dry-run, or fail closed using row-level progress.
- Preserve row keys by scenario, demand multiplier, controller, and seed.
- Surface completed, missing, failed, duplicate, unpaired, bad-provenance, and schema-invalid rows in a machine-readable row audit.

### Strict Gate C
- Emit exactly `PASSED`, `FAILED`, or `INCONCLUSIVE`.
- Fail closed on non-PASSED source, missing primary metric, bounded harm, missing comparator, missing selected-controller action decomposition, malformed demand provenance, or unlocked protocol.
- Keep `claim_ready=false`; Phase 18 owns claim refresh and claim allowance.

### the agent's Discretion
Use deterministic wrappers and tests around existing Phase 11 runner primitives rather than rewriting the SUMO orchestration loop.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/run_phase11_paired_evidence.py` already owns paired-seed specs, demand scaling, progress/resume, row execution, paired statistics, and Gate C metric rules.
- `scripts/run_gate_c_paired_evidence.py` already owns strict Gate C fail-closed source validation for the Phase 11 artifact.
- `scripts/run_closed_loop_sumo.py` already owns live finite-storage action decomposition and strong comparator controllers.

### Established Patterns
- JSON artifacts fail closed and carry `status`, `requirements_covered`, provenance, caveats, raw rows, and schema metadata.
- Existing tests prefer small synthetic inputs plus dry-run/spec-only execution for expensive SUMO flows.

### Integration Points
- Phase 17 writes `experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json`.
- Phase 17 writes `experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json` when progress is enabled.
- Phase 17 writes `experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json`.

</code_context>

<specifics>
## Specific Ideas

The selected candidate is `finite_storage_primal_dual_v1_4_score`. Implement it as an auditable finite-storage controller variant that changes the score decomposition while preserving action-decomposition fields.

</specifics>

<deferred>
## Deferred Ideas

Phase 18 regenerates claim/reproducibility surfaces from the v1.4 Gate C artifacts and decides whether closed-loop superiority is allowed.

</deferred>
