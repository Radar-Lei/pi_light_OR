# Phase 2: Full Sparse Symbolic Recovery - Context

**Gathered:** 2026-05-23
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase turns the Phase 1 finite-dictionary recovery-quality statement into executable sparse symbolic recovery code. It must recover K-atom auditable signal-control policies from dual-guided oracle targets while explicitly trading off empirical oracle regret/value gap, program size, neighbor atom use, and dual-price dependence. It extends existing one-atom and sparse recovery scaffolds, but does not decide the paper’s empirical dual-vs-pressure claim route; that remains Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Recovery Objective
- Use empirical oracle regret or value gap as the primary optimization target, not imitation/action agreement alone.
- Preserve action agreement as a secondary diagnostic output.
- The solver objective must expose or record any complexity, neighbor-use, and dual-price penalties or budgets.
- Claims must stay finite-dictionary and sample-relative; do not imply global traffic-control optimality.

### Atom Library and Tradeoffs
- Atom families must cover local queue/pressure, downstream capacity/slack, raw neighbor queues, pressure/backpressure, dual sensitivity/price imbalance, and random/permuted dual placebo families.
- Dual-price atoms must be distinguishable from raw neighbor and pressure/backpressure atoms in both metadata and output summaries.
- Placebo/random dual atoms must be available and reported separately from genuine dual-sensitivity atoms.
- Corridor/service atoms remain excluded unless backed by explicit primal constraints from Phase 1.

### Auditable Outputs
- Each recovery run must emit machine-readable JSON/CSV outputs and human-readable symbolic rule text.
- Required output metrics include selected atoms, solve time, oracle regret/value gap, action agreement, program length or selected atom count, neighbor atom count, and dual atom count.
- Equal-complexity comparisons must be reproducible without manual transcription.
- Output naming should remain under `experiments/dual_sensitivity/` and follow existing block-style artifact patterns.

### Integration with Existing Code
- Extend or refactor existing `scripts/run_sparse_recovery.py` rather than creating an unrelated recovery pipeline unless research proves a hard blocker.
- Reuse existing state inputs such as `experiments/dual_sensitivity/targeted_bottleneck_states.json` and existing scenario conversion from `scripts/run_sumo_sampled_recovery.py` where appropriate.
- Keep validation script-based and CPU/SciPy/HiGHS oriented.
- Avoid GPU-heavy MARL, AMPL dependency requirements, or broad method pivots in this phase.

### Claude's Discretion
Claude may choose exact CLI flags and internal data structures, provided the final command produces auditable rules and metrics satisfying RECV-01 through RECV-05. Claude may add small helper functions or output files if they directly support sparse recovery validation and reproducibility.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/run_sparse_recovery.py` already implements a SciPy/HiGHS sparse atom-selection MILP with realized oracle regret outputs.
- `scripts/run_sumo_sampled_recovery.py` and `scripts/generate_targeted_bottleneck_states.py` provide sampled/targeted states and conversion patterns.
- `experiments/dual_sensitivity/block1_sparse_recovery_targeted.json` and related artifacts provide current expected output structure.
- `refine-logs/THEORY_AND_CLAIMS.md` now defines THRY-05 as deterministic finite-dictionary empirical recovery quality plus solver gap.

### Established Patterns
- Project validation uses script gates that write structured JSON status payloads.
- New Python scripts use snake_case, `argparse`, `Path`, JSON-serializable dictionaries, fail-fast solver checks, and compact JSON status printing.
- Existing result notes distinguish scaffold/static recovery evidence from closed-loop performance claims.

### Integration Points
- Phase 3 will consume Phase 2 outputs for static pressure-failure claim routing.
- Phase 5 will later harden reproduction commands and table/figure generation.
- Phase 1 theory artifacts constrain this phase’s claims and atom semantics.

</code_context>

<specifics>
## Specific Ideas

Implement full sparse recovery as a natural extension of the current MILP scaffold: configurable K/budget, explicit atom metadata, regret-first objective, placebo families, and a rule-rendering layer that converts selected atoms/weights into auditable symbolic text.

</specifics>

<deferred>
## Deferred Ideas

- Static pressure-failure claim routing belongs to Phase 3.
- Closed-loop SUMO controller deployment and performance evidence belong to Phase 4.
- Repository-wide reproduction hardening belongs to Phase 5.
- New corridor/service atoms are deferred until an explicit primal corridor/service constraint is implemented and validated.

</deferred>
