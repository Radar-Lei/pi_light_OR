# Phase 1: Theoretical Core and Claim Lock - Context

**Gathered:** 2026-05-22
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers the theory and claim-lock artifacts for the TR-B / Transportation Science framing: a continuous capacitated traffic-network relaxation, interpretable movement-level dual-sensitivity decomposition, max-pressure/backpressure recovery as a special case, binding-regime scarcity corrections, and a finite-dictionary symbolic recovery quality statement. It should not claim universal dominance over max-pressure and should route empirical dominance questions to Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Theory Scope
- Use a store-and-forward / CTM-lite continuous network relaxation with queue conservation, movement service, phase compatibility, and capacity/storage/supply constraints.
- Express movement dual sensitivity as generalized pressure: upstream value minus downstream value plus correction terms from binding storage, supply, phase/service, or corridor constraints.
- Treat ordinary max-pressure/backpressure equivalence as a positive structural result, not as a failure of the method.
- State binding-regime deviations as sufficient conditions or formal propositions rather than universal dominance claims.

### Claim Discipline
- Position the paper as OR/control methodology for capacitated signalized networks, not as a PI-Light enhancement paper.
- Keep the main claim conservative: dual sensitivity recovers pressure in slack or ranking-neutral regimes and may add scarcity-aware corrections in binding regimes.
- Avoid ADMM, robust optimization, column generation, bilevel optimization, freight/TR-E pivots, and GPU-heavy MARL as Phase 1 scope.
- Make Phase 3 the decisive kill gate for whether the empirical framing becomes dual advantage, pressure-equivalent symbolic recovery, or diagnostic framing.

### Recovery Link
- Include THRY-05 as a finite-dictionary recovery-regret or optimization-quality statement that bridges theory to sparse symbolic recovery in Phase 2.
- The recovery target should be oracle regret/value gap rather than imitation accuracy alone.
- Program size, neighbor use, and dual-price dependence should appear as explicit finite-dictionary constraints or penalties.
- The theory artifact should make later reviewer-facing checklist mapping straightforward for THRY-01 through THRY-05.

### Claude's Discretion
Claude may choose whether the Phase 1 artifact is a standalone technical memo, manuscript method-section draft, or both, provided the success criteria and verification checklist are satisfied. Claude may choose proposition names and exact notation, but should keep notation readable for OR/transportation reviewers.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/run_dual_sanity.py` contains deterministic LP scenarios, dual extraction, finite-difference validation, and pressure special-case checks.
- `scripts/run_sparse_recovery.py` contains the current sparse atom-selection MILP and can inform the finite-dictionary recovery statement.
- Existing JSON evidence under `experiments/dual_sensitivity/` includes Block 0 dual sanity and Block 1 sparse recovery artifacts.
- `pi_light_code/agent/rule_based/max_pressure.py` provides the baseline max-pressure implementation used for conceptual alignment.

### Established Patterns
- Validation is script-gate based rather than pytest-based; scripts write structured JSON artifacts and compact status objects.
- New OR artifacts should be auditable and traceable to requirements rather than hidden in notebook-only reasoning.
- Existing codebase maps recommend deterministic proxy scenarios instead of mocking optimization math.

### Integration Points
- Theory notes should reference and be consistent with `refine-logs/THEORY_AND_ATOMS.md` if present, `refine-logs/FINAL_PROPOSAL.md`, and current scripts under `scripts/`.
- Phase 2 will consume the recovery-regret statement and translate it into full sparse symbolic recovery.
- Phase 3 will consume the pressure-equivalence and binding-regime conditions as claim routes for static evidence.

</code_context>

<specifics>
## Specific Ideas

Use the project’s current core value as the north star: dual sensitivities are a generalized max-pressure principle that reduce to pressure under slack constraints and add scarcity-aware corrections under binding storage, supply, or corridor bottlenecks.

</specifics>

<deferred>
## Deferred Ideas

- Empirical proof that dual beats pressure belongs to Phase 3 and Phase 4, not Phase 1.
- Full sparse recovery implementation belongs to Phase 2.
- Repository reproducibility hardening belongs to Phase 5.

</deferred>
