# Phase 3: Static Pressure-Failure Kill Gate - Context

**Gathered:** 2026-05-23
**Status:** Ready for research

<domain>
## Phase Boundary

This phase consumes the Phase 1 theory and Phase 2 sparse-recovery artifacts to decide the paper route using static dual-vs-pressure evidence across slack and binding regimes. It must test whether dual sensitivity improves over pressure-style atoms in the regimes where theory permits scarcity-aware rank changes, merely recovers pressure/equal-complexity behavior, or underperforms pressure. It produces static benchmark artifacts and claim-routing documentation, but it does not run closed-loop SUMO experiments; those belong to Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Kill-Gate Purpose
- Treat Phase 3 as the decisive empirical routing gate for the paper's dual-vs-pressure claim strength.
- The output must explicitly classify the route as one of: dual-improves-pressure, dual-recovers/ties-pressure, or dual-underperforms/diagnostic.
- Do not allow Phase 2 candidate diagnostics alone to decide the claim; Phase 3 must run its own static benchmark analysis.

### Static Regimes
- Cover slack, downstream storage-binding, supply-binding, corridor-bottleneck, incident/capacity-drop, and demand-shift regimes as far as current generators/scaffolds support.
- If corridor-bottleneck or supply-binding regimes cannot be created from existing explicit primal constraints, record the limitation instead of inventing unsupported corridor/service claims.
- Prefer script-generated or existing sampled state JSON fixtures under `experiments/dual_sensitivity/`.

### Metrics and Outputs
- Each static regime must report dual-vs-pressure disagreement rate, dual win rate, mean oracle regret, worst-case regret, and recovered symbolic rules.
- Outputs must be structured JSON/CSV plus a human-readable route report under `experiments/dual_sensitivity/`.
- Include enough sampled states for stable conclusions, targeting at least 1k states for the main pressure-failure analysis when feasible.
- Record sample counts by regime and flag regimes below target as preliminary rather than overstating evidence.

### Claim Discipline
- Strong dual advantage supports TR-B/Transportation Science mainline only if binding-regime evidence is clear and pressure/capacity-aware baselines are treated fairly.
- Pressure tie routes to generalized-pressure / symbolic recovery framing.
- Dual underperformance routes to diagnostic framing.
- Do not claim closed-loop superiority or deployable traffic-control performance in this phase.

### Integration with Existing Code
- Reuse Phase 2 artifacts and `scripts/run_sparse_recovery.py` outputs where useful.
- Reuse existing sampled-state generation/conversion scripts rather than creating a new simulator stack.
- Keep validation script-based and CPU/SciPy/HiGHS/SUMO oriented.

</decisions>

<code_context>
## Existing Inputs

- `experiments/dual_sensitivity/block2_sparse_recovery.json`, `.csv`, and `_rules.txt` provide Phase 2 auditable recovery outputs.
- `scripts/run_sparse_recovery.py` can run equal-complexity sparse-recovery comparisons over sampled state JSON.
- `scripts/generate_targeted_bottleneck_states.py` and `experiments/dual_sensitivity/targeted_bottleneck_states.json` provide targeted bottleneck examples.
- `scripts/run_sumo_sampled_recovery.py` provides sampled-state conversion patterns.
- Phase 1 theory artifacts define when pressure equivalence or scarcity correction is claim-bounded.

## Established Patterns

- Write structured JSON/CSV artifacts and compact JSON status to stdout.
- Keep Phase 3 route decisions sample-relative and static-benchmark scoped.
- Avoid broad method pivots, neural MARL, or closed-loop deployment in this phase.

</code_context>

<specifics>
## Specific Ideas

Implement a static kill-gate runner/report layer that groups states by regime, runs or consumes equal-complexity recovery/scoring comparisons for dual, pressure, raw-neighbor, and placebo families, computes disagreement/win/regret metrics, and writes a route decision report with evidence thresholds and caveats.

</specifics>

<deferred>
## Deferred Ideas

- Closed-loop SUMO controller experiments and travel-time/throughput performance claims belong to Phase 4.
- Repository-wide reproduction hardening belongs to Phase 5.
- Manuscript final positioning belongs after Phase 3 routing and Phase 4 evidence.

</deferred>
