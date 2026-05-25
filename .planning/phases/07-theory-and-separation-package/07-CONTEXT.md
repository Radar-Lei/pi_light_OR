---
phase: 07-theory-and-separation-package
status: ready_for_research_and_planning
generated: 2026-05-24
requirements:
  - THRY-01
  - THRY-02
  - THRY-03
  - THRY-04
depends_on:
  - phase: 06-claim-discipline-and-explicit-state-foundation
    provides: bounded claim policy, explicit finite_storage_state schema, objective_components, and fail-closed guard artifacts
---

# Phase 7: Theory and Separation Package — Context

## Phase Boundary

This phase produces a formal finite-storage primal-dual separation package for v1.1. It must justify exactly when the method reduces to classical max-pressure/backpressure and when finite-storage, spillback, switching-loss, service-urgency, or incident/capacity-drop constraints can change decisions and improve a predeclared local criterion.

This phase is theory and artifact scaffolding only. It must not implement the live controller, run closed-loop SUMO experiments, add new baselines, write final manuscript sections, or claim deployment/universal dominance.

## Required Outcomes

- **THRY-01:** A special-case theorem showing reduction to classical max-pressure/backpressure under infinite storage, no switching loss, fixed turning ratios, and slack operational constraints.
- **THRY-02:** A theorem or counterexample where explicit finite storage, spillback, incident capacity drop, or switching loss causes the primal-dual controller and classical pressure to choose different phases.
- **THRY-03:** The separation example must show strict improvement on a predeclared one-step constrained objective, spillback penalty, Lyapunov drift, or equivalent auditable criterion.
- **THRY-04:** Include one additional guarantee candidate suitable for later use: throughput/bounded-drift, regret to a constrained LP oracle, or symbolic-compression error bound.

## Locked Claim Discipline

- The permitted strong claim remains bounded: slack regimes recover or tie max-pressure; improvement claims are only allowed for explicit binding finite-storage/spillback/switching/service/incident regimes.
- v1.0 pressure-equivalent static or closed-loop evidence is historical and insufficient for superiority claims.
- Theory language must distinguish structural separation from simulator/network/horizon/seed-relative empirical dominance.
- Phase 7 outputs should pass the central claim policy introduced in Phase 6 and must not use unsupported superiority wording.

## Upstream Evidence and Interfaces

### Phase 1 Theory Baseline

Existing theory already established:

- A store-and-forward / CTM-lite continuous relaxation with queue conservation, movement service, phase compatibility, and capacity/storage/supply constraints.
- Movement value convention: `lambda_up - lambda_down`.
- Classical pressure/backpressure is a slack or ranking-neutral special case of dual movement ranking.
- Binding-regime scarcity corrections were previously stated as sufficient rank-change conditions, but v1.1 must now make the finite-storage separation explicit and auditable.

Relevant files:

- `refine-logs/THEORY_AND_CLAIMS.md`
- `refine-logs/THEORY_AND_ATOMS.md`
- `.planning/phases/01-theoretical-core-and-claim-lock/01-01-SUMMARY.md`
- `.planning/phases/01-theoretical-core-and-claim-lock/01-02-SUMMARY.md`

### Phase 3 Pressure-Equivalent Route

Phase 3 locked v1.0 static evidence to `pressure-equivalent`: dual and pressure tied under the old sample-relative oracle-regret evidence. Phase 7 must not reinterpret this as superiority. Instead, Phase 7 should define new finite-storage examples where explicit binding state/objective terms mathematically create action separation.

Relevant artifacts:

- `experiments/dual_sensitivity/block3_static_kill_gate.json`
- `experiments/dual_sensitivity/block3_static_kill_gate_report.md`
- `.planning/phases/03-static-pressure-failure-kill-gate/03-VERIFICATION.md`

### Phase 6 Claim and State Foundation

Phase 6 provides the hard boundary for Phase 7 theory artifacts:

- `scripts/claim_policy.py` and `scripts/audit_claim_discipline.py` define the bounded claim vocabulary and fail-closed claim scan.
- `scripts/finite_storage_schema.py` defines canonical finite-storage state keys and objective component keys.
- `experiments/dual_sensitivity/phase6_explicit_state_schema.json` and `phase6_state_objective_fixtures.json` provide deterministic explicit state/objective examples.
- Closed-loop and static surfaces now expect full `finite_storage_state` and `objective_components` rather than proxy labels.

Canonical finite-storage state keys:

- `downstream_storage`
- `residual_receiving_capacity`
- `spillback_blocking`
- `switching_loss_state`
- `service_urgency`
- `incident_capacity_drop`

Canonical objective components:

- `delay`
- `unfinished_vehicle_penalty`
- `spillback_blocking_time`
- `switching_lost_time`

## Theory Design Decisions

### D-07-01 Special-Case Recovery

Use the existing movement-value sign convention and prove that when receiving-capacity/storage constraints are nonbinding, switching/service/incident terms are absent or slack, and turning ratios are fixed, all shadow-price correction terms vanish or are common ranking constants. The resulting movement/phase score reduces to queue-pressure/backpressure.

### D-07-02 Binding Separation

Construct a minimal deterministic network state with at least two competing phases where classical pressure selects one phase but finite-storage primal-dual scoring selects another because a downstream receiving-capacity, spillback, incident, or switching-loss constraint is binding. The example must use explicit Phase 6 state fields, not proxy-only regime labels.

### D-07-03 Strict Improvement Criterion

Predeclare the comparison criterion before evaluating the separation example. Prefer a one-step constrained objective using the Phase 6 objective components because it maps directly to later controller and kill-gate artifacts. Acceptable alternatives are spillback penalty or Lyapunov drift if the planner determines they are cleaner, but the criterion must be auditable and deterministic.

### D-07-04 Additional Guarantee Candidate

Select exactly one additional guarantee candidate for v1.1 follow-up. The default recommendation is regret to a constrained LP oracle because the repository already uses oracle-regret recovery language and it links cleanly to symbolic compression. Throughput/bounded-drift may be noted as a future stronger theorem, but Phase 7 should avoid overcommitting if the finite-storage model assumptions are not fully ready.

## Implementation/Artifact Expectations

Expected Phase 7 outputs should be source-controlled artifacts, not just conversation reasoning. Suitable outputs include:

- A technical memo or theory package under `refine-logs/` or `experiments/dual_sensitivity/` with theorem statements, assumptions, proof sketches, and counterexample data.
- A small deterministic Python checker/generator, if useful, that validates the separation example numerically from explicit state/objective fields.
- Tests or script-gate checks ensuring the example is parseable, bounded-claim-safe, and internally consistent.

The planner should choose the exact artifact layout after codebase research, but must keep outputs lightweight, reproducible, and CPU/stdlib-oriented where possible.

## Out of Scope

- Live finite-storage controller wiring (`CTRL-*`) — Phase 8.
- Slack/binding kill gates (`GATE-*`) — Phase 9.
- Strong baselines and stress scenarios (`EXP-01`, `EXP-02`, `EXP-04`) — Phase 10.
- Long-horizon paired-seed experiments and statistics (`GATE-03`, `EXP-03`, `EXP-05`) — Phase 11.
- Future manuscript-input templates and final reproducibility packaging (`CLAIM-03`, `REPRO-*`) — Phase 12.
- Full paper drafting, related work, final manuscript integration, or submission preparation — explicitly deferred to v2.

## Verification Expectations

Phase 7 plans should include checks such as:

- Theory artifact contains THRY-01 through THRY-04 sections or equivalent requirement markers.
- Separation example has explicit finite-storage state/objective fields and deterministic action/objective comparison.
- Claim audit passes over the new theory/report surfaces.
- Any checker script or tests pass without GPUs or full SUMO execution.

## Resolved Decisions by Autonomous Defaults

- **Artifact form:** Use a technical memo plus deterministic checker/test artifacts if they reduce ambiguity.
- **Separation criterion:** Prefer one-step constrained objective over closed-loop performance because Phase 7 precedes controller and experiments.
- **Additional guarantee candidate:** Prefer constrained LP oracle regret as the v1.1 guarantee candidate unless research finds a stronger low-risk bounded-drift statement.
- **User checkpoint:** Do not ask for interactive selection; proceed with the safest bounded-theory path.
