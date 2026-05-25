# Phase 07: Theory and Separation Package - Research

**Researched:** 2026-05-24  
**Domain:** finite-storage primal-dual traffic-signal theory package / deterministic separation artifacts  
**Confidence:** HIGH for codebase/artifact interfaces; MEDIUM for theorem-strength recommendations pending formal proof implementation

<user_constraints>
## User Constraints (from CONTEXT.md)

### Phase Boundary

This phase produces a formal finite-storage primal-dual separation package for v1.1. It must justify exactly when the method reduces to classical max-pressure/backpressure and when finite-storage, spillback, switching-loss, service-urgency, or incident/capacity-drop constraints can change decisions and improve a predeclared local criterion.

This phase is theory and artifact scaffolding only. It must not implement the live controller, run closed-loop SUMO experiments, add new baselines, write final manuscript sections, or claim deployment/universal dominance.

### Required Outcomes

- **THRY-01:** A special-case theorem showing reduction to classical max-pressure/backpressure under infinite storage, no switching loss, fixed turning ratios, and slack operational constraints.
- **THRY-02:** A theorem or counterexample where explicit finite storage, spillback, incident capacity drop, or switching loss causes the primal-dual controller and classical pressure to choose different phases.
- **THRY-03:** The separation example must show strict improvement on a predeclared one-step constrained objective, spillback penalty, Lyapunov drift, or equivalent auditable criterion.
- **THRY-04:** Include one additional guarantee candidate suitable for later use: throughput/bounded-drift, regret to a constrained LP oracle, or symbolic-compression error bound.

### Locked Claim Discipline

- The permitted strong claim remains bounded: slack regimes recover or tie max-pressure; improvement claims are only allowed for explicit binding finite-storage/spillback/switching/service/incident regimes.
- v1.0 pressure-equivalent static or closed-loop evidence is historical and insufficient for superiority claims.
- Theory language must distinguish structural separation from simulator/network/horizon/seed-relative empirical dominance.
- Phase 7 outputs should pass the central claim policy introduced in Phase 6 and must not use unsupported superiority wording.

### Theory Design Decisions

#### D-07-01 Special-Case Recovery

Use the existing movement-value sign convention and prove that when receiving-capacity/storage constraints are nonbinding, switching/service/incident terms are absent or slack, and turning ratios are fixed, all shadow-price correction terms vanish or are common ranking constants. The resulting movement/phase score reduces to queue-pressure/backpressure.

#### D-07-02 Binding Separation

Construct a minimal deterministic network state with at least two competing phases where classical pressure selects one phase but finite-storage primal-dual scoring selects another because a downstream receiving-capacity, spillback, incident, or switching-loss constraint is binding. The example must use explicit Phase 6 state fields, not proxy-only regime labels.

#### D-07-03 Strict Improvement Criterion

Predeclare the comparison criterion before evaluating the separation example. Prefer a one-step constrained objective using the Phase 6 objective components because it maps directly to later controller and kill-gate artifacts. Acceptable alternatives are spillback penalty or Lyapunov drift if the planner determines they are cleaner, but the criterion must be auditable and deterministic.

#### D-07-04 Additional Guarantee Candidate

Select exactly one additional guarantee candidate for v1.1 follow-up. The default recommendation is regret to a constrained LP oracle because the repository already uses oracle-regret recovery language and it links cleanly to symbolic compression. Throughput/bounded-drift may be noted as a future stronger theorem, but Phase 7 should avoid overcommitting if the finite-storage model assumptions are not fully ready.

### Out of Scope

- Live finite-storage controller wiring (`CTRL-*`) — Phase 8.
- Slack/binding kill gates (`GATE-*`) — Phase 9.
- Strong baselines and stress scenarios (`EXP-01`, `EXP-02`, `EXP-04`) — Phase 10.
- Long-horizon paired-seed experiments and statistics (`GATE-03`, `EXP-03`, `EXP-05`) — Phase 11.
- Future manuscript-input templates and final reproducibility packaging (`CLAIM-03`, `REPRO-*`) — Phase 12.
- Full paper drafting, related work, final manuscript integration, or submission preparation — explicitly deferred to v2.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| THRY-01 | Prove special-case reduction to max-pressure/backpressure under infinite storage, no switching loss, fixed turning ratios, and slack operational constraints. [VERIFIED: .planning/REQUIREMENTS.md] | Use the existing LP sign convention `movement_values = equality_duals[up] - equality_duals[down]` and the Phase 1 pressure special-case memo as the proof base. [VERIFIED: scripts/run_dual_sanity.py; refine-logs/THEORY_AND_CLAIMS.md; refine-logs/THEORY_AND_ATOMS.md] |
| THRY-02 | Construct/prove separation where finite storage, spillback, incident capacity drop, or switching loss changes the selected phase. [VERIFIED: .planning/REQUIREMENTS.md] | Build a deterministic two-phase JSON example using Phase 6 `finite_storage_state` fields, especially `residual_receiving_capacity` and `spillback_blocking`. [VERIFIED: scripts/finite_storage_schema.py; experiments/dual_sensitivity/phase6_explicit_state_schema.json] |
| THRY-03 | Show strict improvement on a predeclared one-step constrained objective, spillback penalty, Lyapunov drift, or equivalent criterion. [VERIFIED: .planning/REQUIREMENTS.md] | Predeclare an objective composed from Phase 6 components: `delay`, `unfinished_vehicle_penalty`, `spillback_blocking_time`, and `switching_lost_time`. [VERIFIED: scripts/finite_storage_schema.py; experiments/dual_sensitivity/phase6_explicit_state_schema.json] |
| THRY-04 | Include one additional guarantee candidate: throughput/bounded-drift, constrained LP oracle regret, or symbolic-compression error bound. [VERIFIED: .planning/REQUIREMENTS.md] | Recommend constrained LP oracle regret because existing project theory and sparse recovery already use realized oracle-regret/value-gap language. [VERIFIED: refine-logs/THEORY_AND_ATOMS.md; refine-logs/THEORY_AND_CLAIMS.md] |
</phase_requirements>

## Summary

Phase 7 should produce a lightweight theory-and-separation package, not controller code. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] The safest implementation-ready layout is: one technical memo under `refine-logs/`, one deterministic separation JSON under `experiments/dual_sensitivity/`, one stdlib-oriented checker under `scripts/`, and one test module under `tests/`. [RECOMMENDED] This layout follows existing repository conventions that OR scripts live in `scripts/`, JSON artifacts live in `experiments/dual_sensitivity/`, and theory logs live in uppercase Markdown under `refine-logs/`. [VERIFIED: CLAUDE.md]

The central theorem package should restate Phase 1’s movement-value convention and sharpen it for finite-storage v1.1: when storage/receiving constraints are slack, switching/service/incident corrections are absent or ranking-neutral, and turning ratios are fixed, the full finite-storage primal-dual phase score reduces to the usual sum of upstream-minus-downstream pressures. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md; refine-logs/THEORY_AND_ATOMS.md; .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] The separation example should be deliberately smaller than the arterial Phase 6 fixtures: two competing phases, one movement into a full downstream link, one movement into a nonfull downstream link, pressure choosing the risky movement, and finite-storage scoring choosing the safe movement. [RECOMMENDED]

**Primary recommendation:** implement Phase 7 as a memo + deterministic checker package that verifies slack recovery/ties and a storage-binding action/objective separation using only Phase 6 explicit state/objective fields; defer all live controller wiring and closed-loop claims to Phase 8+. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md]

## Project Constraints (from CLAUDE.md)

- Frame the project as OR / methodological traffic-network control, not an AI-controller benchmark. [VERIFIED: CLAUDE.md]
- Preserve the bounded claim: generalized pressure with scarcity-aware corrections, not broad cross-regime dominance over max-pressure. [VERIFIED: CLAUDE.md; scripts/claim_policy.py]
- Keep experiments and checkers CPU/SUMO/optimization oriented; no required GPU pipeline. [VERIFIED: CLAUDE.md]
- Emit auditable JSON/CSV artifacts and keep tables/figures traceable to raw outputs. [VERIFIED: CLAUDE.md]
- Treat max-pressure/backpressure and capacity/spillback-aware variants as first-class baselines, not strawmen. [VERIFIED: CLAUDE.md]
- Use lowercase snake_case for new Python scripts/modules and `main() -> None` with `if __name__ == "__main__"`. [VERIFIED: CLAUDE.md]
- Keep OR/SUMO scripts in `scripts/` and outputs in `experiments/dual_sensitivity/`. [VERIFIED: CLAUDE.md]
- Use `Path`, JSON-serializable dictionaries, fail-fast errors, and compact JSON CLI status output. [VERIFIED: CLAUDE.md]
- Do not place new OR experiments inside `pi_light_code/`. [VERIFIED: CLAUDE.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| THRY-01 slack recovery theorem | Theory artifact / `refine-logs` | Deterministic checker | The theorem is a mathematical statement; the checker only validates notation and fixture consistency. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| THRY-02 binding separation example | Static artifact / JSON | Checker script | Phase 7 must construct auditable state/objective examples but must not implement a live controller. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| THRY-03 one-step objective improvement | Checker script | JSON artifact | Strict improvement should be computed deterministically from predeclared objective components. [VERIFIED: scripts/finite_storage_schema.py; .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| THRY-04 guarantee candidate | Theory memo | Optional checker metadata | The additional guarantee is a future theorem candidate, not a runtime controller feature. [VERIFIED: .planning/REQUIREMENTS.md] |
| Claim discipline | Claim audit CLI | Tests | Phase 6 already centralizes claim policy and fail-closed audit behavior. [VERIFIED: scripts/claim_policy.py; scripts/audit_claim_discipline.py; tests/test_claim_discipline.py] |

## Standard Stack

### Core

| Component | Version / Status | Purpose | Why Standard |
|-----------|------------------|---------|--------------|
| Python stdlib `json`, `argparse`, `pathlib` | Host Python 3.14.4 observed; `environment.yml` declares Python >=3.10,<3.13. [VERIFIED: environment probe; environment.yml] | Build deterministic checker and emit JSON artifacts. | Existing OR scripts use CLI + `Path(...).write_text(json.dumps(...))`. [VERIFIED: scripts/run_dual_sanity.py; CLAUDE.md] |
| Existing `scripts/finite_storage_schema.py` | `SCHEMA_VERSION = "phase6_explicit_state_v1"`. [VERIFIED: scripts/finite_storage_schema.py] | Validate finite-storage state and objective components. | It is the canonical source for Phase 6 explicit fields. [VERIFIED: scripts/finite_storage_schema.py; experiments/dual_sensitivity/phase6_explicit_state_schema.json] |
| Existing `scripts/claim_policy.py` + `scripts/audit_claim_discipline.py` | Phase 6 artifacts currently `PASSED`. [VERIFIED: experiments/dual_sensitivity/phase6_claim_policy.json; experiments/dual_sensitivity/phase6_claim_audit.json] | Enforce bounded claim language. | Phase 7 context requires outputs to pass the central claim policy. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| pytest | 9.0.2 observed. [VERIFIED: environment probe] | Add deterministic tests for memo markers, JSON schema, and checker outputs. | Existing repository tests are pytest-style Python files. [VERIFIED: tests/test_finite_storage_schema.py; tests/test_claim_discipline.py] |

### Supporting

| Component | Version / Status | Purpose | When to Use |
|-----------|------------------|---------|-------------|
| NumPy/SciPy HiGHS | Declared in environment and used by existing LP code. [VERIFIED: environment.yml; scripts/run_dual_sanity.py] | Optional if the checker reuses the LP relaxation; not required for a minimal algebraic checker. [RECOMMENDED] | Use only if planner wants to validate dual values from an LP rather than fixed analytic scores. [RECOMMENDED] |
| SUMO | 1.26.0 observed. [VERIFIED: environment probe] | Not needed for Phase 7. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] | Keep for later phases; do not require SUMO for Phase 7 checker. [RECOMMENDED] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Deterministic algebraic checker | SciPy LP checker | LP checker is closer to dual-sensitivity mechanics, but algebraic checker is simpler, stdlib-only, and sufficient for a hand-constructed separation artifact. [RECOMMENDED] |
| New controller module | Static checker + JSON | Controller module belongs to Phase 8 and would violate Phase 7 boundary. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| Reusing Phase 6 arterial fixtures directly | Minimal two-phase fixture | Phase 6 fixtures are valuable schema evidence, but the minimal construction is easier to prove and audit for THRY-02/THRY-03. [VERIFIED: experiments/dual_sensitivity/phase6_state_objective_fixtures.json] |

**Installation:** no new packages recommended. [RECOMMENDED]

## Package Legitimacy Audit

No external package installation is recommended for Phase 7. [RECOMMENDED] Therefore the package legitimacy gate is not applicable. [RECOMMENDED]

## Recommended Phase 7 Artifact Layout

| File | Create / Modify | Role | Reason |
|------|-----------------|------|--------|
| `refine-logs/THEORY_AND_SEPARATION.md` | Create | Technical memo covering THRY-01~THRY-04. | Existing theory artifacts live in `refine-logs/` with uppercase names. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md; refine-logs/THEORY_AND_ATOMS.md; CLAUDE.md] |
| `experiments/dual_sensitivity/phase7_theory_separation.json` | Create | Deterministic machine-readable theorem/checker artifact. | Existing experiment artifacts use this directory and JSON status fields. [VERIFIED: CLAUDE.md; scripts/run_dual_sanity.py] |
| `scripts/check_theory_separation.py` | Create | Deterministic checker/generator for slack recovery and binding separation. | Existing OR scripts expose CLI `main()` and print compact JSON status. [VERIFIED: CLAUDE.md; scripts/run_dual_sanity.py] |
| `tests/test_theory_separation.py` | Create | Unit tests for schema validation, action separation, strict objective improvement, and claim-safe surfaces. | Existing tests directly import scripts via `sys.path.insert(0, scripts)`. [VERIFIED: tests/test_finite_storage_schema.py; tests/test_claim_discipline.py] |
| `scripts/claim_policy.py` | Do not modify unless necessary | Existing claim rules. | The current policy already covers slack recovery and binding-regime improvement prerequisites. [VERIFIED: scripts/claim_policy.py] |
| `scripts/finite_storage_schema.py` | Do not modify unless a missing validator blocks Phase 7 | Existing schema source. | Current required fields and objective components already match Phase 7 needs. [VERIFIED: scripts/finite_storage_schema.py] |

**Why this does not enter Phase 8 controller scope:** the proposed checker compares static candidate phase scores and one-step objective components from a fixed JSON state; it does not add a SUMO controller, a closed-loop runner, action decomposition output from a live controller, or a `full_dual_symbolic` successor. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] This preserves Phase 8 for live finite-storage controller wiring and runtime score decomposition. [VERIFIED: .planning/ROADMAP.md]

## Architecture Patterns

### System Architecture Diagram

```text
Phase 7 inputs
  |
  |-- CONTEXT / REQUIREMENTS / Phase 1 theory memos
  |-- Phase 6 schema + fixtures + claim policy
  v
Theory memo: refine-logs/THEORY_AND_SEPARATION.md
  |        \
  |         \ theorem assumptions + proof sketches
  |          \
  v           v
Deterministic separation JSON  --->  checker script
phase7_theory_separation.json        scripts/check_theory_separation.py
  |                                   |
  | explicit finite_storage_state      | validates schema
  | objective_components               | compares pressure vs finite-storage score
  | predeclared objective              | checks strict one-step improvement
  v                                   v
pytest tests --------------------> claim audit command
  |
  v
Planning-ready THRY-01~THRY-04 evidence, no live controller side effects
```

### Recommended Project Structure

```text
refine-logs/
└── THEORY_AND_SEPARATION.md          # Phase 7 theorem statements, assumptions, proof sketches
experiments/dual_sensitivity/
└── phase7_theory_separation.json     # deterministic slack + binding examples and checker result
scripts/
└── check_theory_separation.py        # stdlib checker/generator; imports Phase 6 schema validators
tests/
└── test_theory_separation.py         # pytest coverage for THRY-01~THRY-04 artifact contracts
```

### Pattern 1: Fixed artifact + deterministic checker

**What:** store the separation example in JSON and make the checker recompute all decisive fields: pressure action, finite-storage action, one-step objective costs, and strict-improvement margin. [RECOMMENDED]

**When to use:** use this for THRY-02/THRY-03 because the requirement is structural separation in an auditable state, not closed-loop performance. [VERIFIED: .planning/REQUIREMENTS.md]

**Example JSON skeleton:**

```json
{
  "experiment": "phase7_theory_separation",
  "status": "PASSED",
  "requirements_covered": ["THRY-01", "THRY-02", "THRY-03", "THRY-04"],
  "schema_version": "phase6_explicit_state_v1",
  "one_step_objective_definition": {
    "predeclared_before_action_comparison": true,
    "components": ["delay", "unfinished_vehicle_penalty", "spillback_blocking_time", "switching_lost_time"],
    "aggregation": "sum_components_or_declared_nonnegative_weights"
  },
  "examples": [
    {
      "name": "storage_binding_two_phase_separation",
      "finite_storage_state": {},
      "objective_components": {},
      "pressure_action": "phase_a",
      "finite_storage_action": "phase_b",
      "strict_objective_improvement": true
    }
  ]
}
```

The top-level `finite_storage_state` and `objective_components` fields should validate with `validate_state_objective_sample`. [VERIFIED: scripts/finite_storage_schema.py; tests/test_finite_storage_schema.py]

### Pattern 2: Memo markers traceable to requirements

**What:** include explicit headings `THRY-01`, `THRY-02`, `THRY-03`, and `THRY-04` in the memo and in the JSON `requirements_covered`. [RECOMMENDED]

**When to use:** use this so the planner and verifier can map requirements without semantic guessing. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md]

### Anti-Patterns to Avoid

- **Proxy-only separation:** do not use `supply_binding_proxy`, `corridor_bottleneck_proxy`, or `demand_shift_proxy` as final separation evidence because Phase 6 marks those regimes as proxy-only. [VERIFIED: experiments/dual_sensitivity/phase6_state_objective_fixtures.json]
- **Controller leakage:** do not create a live SUMO controller or wire `full_dual_symbolic` in Phase 7. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md]
- **Action-separation without objective improvement:** THRY-02 alone is insufficient for THRY-03; the example must compute a strict predeclared objective margin. [VERIFIED: .planning/REQUIREMENTS.md]
- **Unbacked correction terms:** do not claim corridor/service corrections unless the primal model writes the corresponding constraint. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md; refine-logs/THEORY_AND_ATOMS.md]

## THRY-01 Slack Recovery Theorem Recommendation

### Recommended theorem statement

**Theorem (slack finite-storage recovery of max-pressure).** For a fixed signal decision interval, consider candidate phases whose movement sets are fixed and whose turning ratios are fixed. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md] If downstream storage/receiving constraints are nonbinding or infinite, spillback/blocking indicators are false, switching-loss and incident-capacity-drop corrections are absent or common across candidates, service-urgency/resource multipliers are slack or ranking-neutral, and movement services are compared away from non-neutral lower/upper service bounds, then the finite-storage primal-dual phase ranking is identical to classical max-pressure/backpressure up to ties. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md; refine-logs/THEORY_AND_CLAIMS.md]

### Recommended notation

| Symbol | Meaning | Repository alignment |
|--------|---------|----------------------|
| `L` | directed links/lane groups | Existing LP `Scenario.links`. [VERIFIED: scripts/run_dual_sanity.py] |
| `M` | movements `m=(i,j)` | Existing LP `Scenario.movements`. [VERIFIED: scripts/run_dual_sanity.py] |
| `P` | candidate signal phases / compatible movement groups | Phase-level pressure aggregation in theory memo. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md] |
| `x_l` | queue/occupancy | Existing `queue` arrays and Phase 6 fixture `queues`. [VERIFIED: scripts/run_dual_sanity.py; experiments/dual_sensitivity/phase6_state_objective_fixtures.json] |
| `S_l` | storage/receiving capacity | Existing `downstream_capacity` and Phase 6 `downstream_storage`. [VERIFIED: scripts/run_dual_sanity.py; scripts/finite_storage_schema.py] |
| `r_{ij}` | fixed turning ratio from `i` to `j` | Required by THRY-01; current movement-explicit examples can set each active movement ratio to 1. [VERIFIED: .planning/REQUIREMENTS.md; scripts/run_dual_sanity.py] |
| `lambda_l` | conservation equality dual / link value | Existing code extracts `res.eqlin.marginals`. [VERIFIED: scripts/run_dual_sanity.py] |
| `D_m` | finite-storage primal-dual movement score | Recommended as `pressure + explicit corrections`. [RECOMMENDED] |
| `P_m` | classical pressure movement score | Existing code computes `queue_weight[up] - queue_weight[down]`. [VERIFIED: scripts/run_dual_sanity.py] |

### Proof skeleton

1. Start from the existing one-step store-and-forward LP with conservation, service, storage, and overflow variables. [VERIFIED: refine-logs/THEORY_AND_ATOMS.md; scripts/run_dual_sanity.py]
2. Use the current sign convention: movement value equals `lambda_up - lambda_down`. [VERIFIED: refine-logs/THEORY_AND_ATOMS.md; scripts/run_dual_sanity.py]
3. Under nonbinding storage/receiving constraints, the storage dual terms vanish or become ranking-neutral. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md]
4. Under no switching loss, no incident capacity drop, and slack/ranking-neutral operational constraints, no non-neutral correction remains. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md]
5. With queue weights specialized to queues and fixed movement topology/turning ratios, `lambda_i - lambda_j` reduces to `x_i - x_j`, and phase scores reduce to sums over compatible movements. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md; refine-logs/THEORY_AND_ATOMS.md]
6. Ties should be reported as expected recovery/tie behavior, not as failures. [VERIFIED: scripts/claim_policy.py; .planning/ROADMAP.md]

### Verification recommendation

The checker should include a `slack_recovery` case where all `residual_receiving_capacity` values exceed the tested one-step service, all `spillback_blocking` flags are false, `incident_capacity_drop.active` is false, and `switching_lost_time` is zero. [VERIFIED: scripts/finite_storage_schema.py; experiments/dual_sensitivity/phase6_state_objective_fixtures.json] It should assert that finite-storage and pressure actions match or belong to the same tie set. [RECOMMENDED]

## THRY-02 / THRY-03 Binding Separation Example Recommendation

### Minimal construction

Use a four-link, two-phase deterministic state. [RECOMMENDED]

| Item | Phase A | Phase B | Purpose |
|------|---------|---------|---------|
| Movement | `up_a -> down_a` | `up_b -> down_b` | Two competing candidate phases. [RECOMMENDED] |
| Classical pressure | high enough that pressure chooses A | lower than A | Creates THRY-02 action separation when corrections bind. [RECOMMENDED] |
| Downstream storage | `down_a` full or near full | `down_b` slack | Activates finite-storage correction only for A. [RECOMMENDED] |
| Phase 6 fields | `residual_receiving_capacity.down_a = 0`, `spillback_blocking.down_a.spillback = true`, `blocking = true` | positive residual and false flags | Uses explicit Phase 6 fields. [VERIFIED: scripts/finite_storage_schema.py] |
| Incident/switching | inactive by default | inactive by default | Keeps the first separation proof storage-only and minimal. [RECOMMENDED] |

Concrete values suitable for the checker: `queue(up_a)=30`, `queue(down_a)=10`, `storage(down_a)=10`, `queue(up_b)=15`, `queue(down_b)=2`, `storage(down_b)=10`. [RECOMMENDED] Classical pressure scores are then `20` for A and `13` for B, so classical pressure selects A. [RECOMMENDED] A finite-storage score such as `score = pressure - 10 * blocked_downstream_indicator` gives A score `10` and B score `13`, so the finite-storage score selects B. [RECOMMENDED] The correction must be documented as a checker-side surrogate for a shadow-price/scarcity correction in the technical memo, not as a live controller implementation. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md]

### Predeclared one-step constrained objective

Predeclare before comparing actions:

```text
J(action) = delay(action)
          + unfinished_vehicle_penalty(action)
          + spillback_blocking_time(action)
          + switching_lost_time(action)
```

The component names exactly match Phase 6 objective keys. [VERIFIED: scripts/finite_storage_schema.py; experiments/dual_sensitivity/phase6_explicit_state_schema.json]

Recommended action components:

| Action | delay | unfinished_vehicle_penalty | spillback_blocking_time | switching_lost_time | Total `J` |
|--------|-------|-----------------------------|--------------------------|---------------------|-----------|
| Phase A | same base delay | 1 | 1 | 0 | base + 2 |
| Phase B | same base delay | 0 | 0 | 0 | base |

This gives strict one-step improvement for the finite-storage action B over pressure action A by margin `2` under unit component weights. [RECOMMENDED] If the planner prefers nonunit weights, the JSON should declare the weights before computed action totals. [RECOMMENDED]

### Required JSON fields

- `finite_storage_state.downstream_storage` with all four links. [VERIFIED: scripts/finite_storage_schema.py]
- `finite_storage_state.residual_receiving_capacity` with `down_a` at zero and `down_b` positive. [VERIFIED: scripts/finite_storage_schema.py]
- `finite_storage_state.spillback_blocking` with explicit booleans and occupancy ratios. [VERIFIED: scripts/finite_storage_schema.py]
- `finite_storage_state.switching_loss_state` with `current_phase` and `time_since_switch`. [VERIFIED: scripts/finite_storage_schema.py]
- `finite_storage_state.service_urgency` with numeric values. [VERIFIED: scripts/finite_storage_schema.py]
- `finite_storage_state.incident_capacity_drop` with `active`, `edge`, and `factor`. [VERIFIED: scripts/finite_storage_schema.py]
- top-level `objective_components` and per-action `action_objective_components`. [VERIFIED: scripts/finite_storage_schema.py; RECOMMENDED]
- `pressure_action`, `finite_storage_action`, `objective_margin`, and `strict_objective_improvement`. [RECOMMENDED]

## THRY-04 Guarantee Candidate Recommendation

Use **constrained LP oracle regret** as the single Phase 7 guarantee candidate. [RECOMMENDED] Existing Phase 1 theory already defines empirical oracle regret/value gap as the primary recovery target, and `run_sparse_recovery.py` reports realized oracle regret. [VERIFIED: refine-logs/THEORY_AND_ATOMS.md; refine-logs/THEORY_AND_CLAIMS.md]

Recommended statement:

```text
For a finite audited dataset D_N of explicit finite-storage states, let a*_n be the action minimizing the predeclared one-step constrained LP/objective J_n(a). For any policy pi in a finite symbolic/controller class Pi, define empirical constrained-oracle regret R_hat_N(pi) = (1/N) sum_n [J_n(pi(s_n)) - J_n(a*_n)]. If the recovery/checker solver returns pi_hat within optimization gap epsilon_opt of the best policy in Pi under the declared penalties, then R_hat_N(pi_hat) + penalty(pi_hat) <= min_{pi in Pi} [R_hat_N(pi) + penalty(pi)] + epsilon_opt.
```

This guarantee is finite-sample, oracle-relative, and objective-relative; it does not establish closed-loop network performance. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md; scripts/claim_policy.py] Throughput/bounded-drift is a stronger future candidate but should remain deferred until the live controller, finite-storage dynamics, and closed-loop stress assumptions are available. [VERIFIED: .planning/ROADMAP.md; .planning/phases/07-theory-and-separation-package/07-CONTEXT.md]

## Claim-Discipline Guardrails

| Guardrail | Required Phase 7 behavior | Source |
|-----------|---------------------------|--------|
| Slack language | Say the method recovers or ties max-pressure in slack regimes. | [VERIFIED: scripts/claim_policy.py] |
| Binding language | Say improvement claims require explicit binding finite-storage/spillback/switching/service/incident evidence plus objective components. | [VERIFIED: scripts/claim_policy.py] |
| Historical evidence quarantine | Treat v1.0 pressure-equivalent artifacts as equivalence/compression evidence, not as evidence for broad performance claims. | [VERIFIED: scripts/claim_policy.py; experiments/dual_sensitivity/phase6_claim_audit.json] |
| Structural vs empirical | Separate theorem/counterexample action separation from simulator/network/horizon/seed-relative empirical evidence. | [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| Proxy warning | Mark proxy-only regimes as insufficient for final binding evidence unless explicit fields and objective components validate. | [VERIFIED: experiments/dual_sensitivity/phase6_state_objective_fixtures.json] |

**Avoid wording that implies:** broad cross-regime performance advantage, deployment-ready performance advantage, static evidence standing in for closed-loop evidence, or v1.0 pressure-equivalent evidence supporting stronger Phase 7+ claims. [VERIFIED: scripts/claim_policy.py; tests/test_claim_discipline.py]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Phase 6 schema validation | Custom ad hoc field checks | `validate_state_objective_sample`, `validate_finite_storage_state`, `validate_objective_components` | Existing validators already enforce required fields, finite numbers, booleans, and nonnegative objective components. [VERIFIED: scripts/finite_storage_schema.py; tests/test_finite_storage_schema.py] |
| Claim scan | Manual grep-only review | `scripts/audit_claim_discipline.py` | Existing audit handles text/JSON prose, missing paths, forbidden hits, and historical evidence quarantine. [VERIFIED: scripts/audit_claim_discipline.py; tests/test_claim_discipline.py] |
| Live controller behavior | Static checker pretending to be runtime control | Defer to Phase 8 | Phase 7 explicitly excludes live controller wiring. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| Closed-loop performance validation | One-step example labeled as closed-loop evidence | Defer to Phase 9/11 gates | Roadmap assigns kill gates and long-horizon paired-seed evidence to later phases. [VERIFIED: .planning/ROADMAP.md] |

**Key insight:** Phase 7 should prove and audit structural conditions; runtime control and closed-loop evidence are separate responsibilities in later phases. [VERIFIED: .planning/ROADMAP.md; .planning/phases/07-theory-and-separation-package/07-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: treating proxy regimes as explicit binding evidence

**What goes wrong:** a separation example uses `supply_binding_proxy`, `corridor_bottleneck_proxy`, or `demand_shift_proxy` without explicit constraint fields. [VERIFIED: experiments/dual_sensitivity/phase6_state_objective_fixtures.json]

**Why it happens:** Phase 6 retained proxy labels for historical/static coverage but marked several as proxy-only. [VERIFIED: experiments/dual_sensitivity/phase6_state_objective_fixtures.json]

**How to avoid:** use storage-binding or incident-capacity-drop examples with validated `finite_storage_state` and `objective_components`. [VERIFIED: experiments/dual_sensitivity/phase6_state_objective_fixtures.json]

### Pitfall 2: proving action separation without strict objective improvement

**What goes wrong:** pressure and finite-storage actions differ, but the one-step objective is not predeclared or not strictly better. [VERIFIED: .planning/REQUIREMENTS.md]

**How to avoid:** put `one_step_objective_definition` in JSON before action totals and test `objective_margin > 0`. [RECOMMENDED]

### Pitfall 3: using unmodeled correction terms

**What goes wrong:** the memo claims service/corridor corrections without a primal constraint. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md; refine-logs/THEORY_AND_ATOMS.md]

**How to avoid:** for Phase 7 minimal proof, use downstream storage/spillback correction only; mention service/corridor terms only as conditional on written constraints. [RECOMMENDED]

### Pitfall 4: controller scope creep

**What goes wrong:** Phase 7 creates live action-selection code under the controller path. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md]

**How to avoid:** keep checker output static and label it `theory_separation`, not a deployable controller. [RECOMMENDED]

## Code Examples

### Checker CLI pattern

Use the existing repository pattern: parse arguments, write JSON artifact, print compact status, and exit nonzero only on failed checks. [VERIFIED: scripts/run_dual_sanity.py; CLAUDE.md]

```python
# Source: scripts/run_dual_sanity.py and scripts/finite_storage_schema.py patterns
# Recommended shape only; planner should implement in scripts/check_theory_separation.py.
from pathlib import Path
import argparse
import json

from finite_storage_schema import validate_state_objective_sample


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/dual_sensitivity/phase7_theory_separation.json")
    args = parser.parse_args()
    payload = build_and_check_phase7_payload()
    for idx, sample in enumerate(payload["examples"]):
        validate_state_objective_sample(sample, path=Path(args.out), sample_idx=idx)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "out": args.out}, indent=2))
    if payload["status"] != "PASSED":
        raise SystemExit(1)
```

## State of the Art

| Old Approach | Current Phase 7 Approach | When Changed | Impact |
|--------------|--------------------------|--------------|--------|
| v1.0 pressure-equivalent generalized-pressure recovery | v1.1 explicit finite-storage primal-dual separation | v1.1 roadmap after Phase 6 | Phase 7 must prove slack recovery and construct explicit binding separation rather than reinterpret v1.0 evidence. [VERIFIED: .planning/PROJECT.md; .planning/ROADMAP.md] |
| Proxy binding regimes | Explicit `finite_storage_state` and `objective_components` | Phase 6 | Binding claims require canonical explicit fields. [VERIFIED: scripts/finite_storage_schema.py; experiments/dual_sensitivity/phase6_explicit_state_schema.json] |
| Action agreement as primary recovery metric | Realized oracle regret/value gap and constrained one-step objective | Phase 1/Phase 6 theory route | THRY-03 should optimize/audit objective improvement, not label agreement only. [VERIFIED: refine-logs/THEORY_AND_ATOMS.md; .planning/REQUIREMENTS.md] |

**Deprecated/outdated for Phase 7:** proxy-only final evidence, broad advantage wording, and live controller implementation inside theory phase. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md; scripts/claim_policy.py]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The minimal two-phase storage example values are recommended rather than already present as a Phase 7 artifact. [ASSUMED] | THRY-02 / THRY-03 Binding Separation Example Recommendation | Planner must implement and test exact numbers; if margins are adjusted, theorem/checker text must update. |
| A2 | A stdlib algebraic checker is sufficient for Phase 7, with SciPy LP validation optional. [ASSUMED] | Standard Stack / Alternatives Considered | If reviewers/planner require LP dual extraction, Phase 7 may need a SciPy-backed checker. |
| A3 | Unit weights over Phase 6 objective components are acceptable for the first deterministic separation artifact. [ASSUMED] | Predeclared one-step constrained objective | If nonunit weights are desired, JSON must predeclare them and tests must recompute totals. |

## Open Questions (RESOLVED)

1. **RESOLVED — checker uses fixed analytic scarcity scores, not LP dual extraction.**
   - What we know: existing LP code computes equality duals and pressure scores. [VERIFIED: scripts/run_dual_sanity.py]
   - Resolution: Phase 7 will start with a stdlib analytic checker because the phase needs deterministic structural separation, not solver provenance. SciPy LP validation is deferred unless a later review specifically requires tighter dual extraction evidence. [RECOMMENDED]

2. **RESOLVED — storage/spillback is the primary separation mechanism.**
   - What we know: Phase 6 schema supports `incident_capacity_drop` and `switching_loss_state`. [VERIFIED: scripts/finite_storage_schema.py]
   - Resolution: Phase 7 will use one minimal storage/spillback separation example only. Incident and switching examples are deferred unless they remain lightweight and do not expand the phase beyond THRY-02/THRY-03. [RECOMMENDED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | checker/tests | yes | 3.14.4 observed; environment file declares >=3.10,<3.13 | Use project environment if Python 3.14 causes dependency mismatch. [VERIFIED: environment probe; environment.yml] |
| pytest | tests | yes | 9.0.2 observed | Manual `python tests/test_theory_separation.py` pattern can mirror existing tests if needed. [VERIFIED: environment probe; tests/test_claim_discipline.py] |
| SUMO | later phases, not Phase 7 | yes | 1.26.0 observed | Not required for Phase 7. [VERIFIED: environment probe; .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| SciPy/NumPy | optional LP checker | declared/used | not probed here | Keep checker stdlib if environment mismatch occurs. [VERIFIED: environment.yml; scripts/run_dual_sanity.py] |

**Missing dependencies with no fallback:** none identified for the recommended stdlib Phase 7 checker. [RECOMMENDED]

**Missing dependencies with fallback:** SciPy/NumPy version not probed; fallback is the algebraic checker. [RECOMMENDED]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 observed. [VERIFIED: environment probe] |
| Config file | none detected in required reads; tests are standalone pytest-style modules. [VERIFIED: tests/test_finite_storage_schema.py; tests/test_claim_discipline.py] |
| Quick run command | `python3 -m pytest tests/test_theory_separation.py -q` [RECOMMENDED] |
| Full relevant command | `python3 -m pytest tests/test_finite_storage_schema.py tests/test_claim_discipline.py tests/test_theory_separation.py -q` [RECOMMENDED] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| THRY-01 | Slack example pressure and finite-storage actions match or tie. | unit | `python3 -m pytest tests/test_theory_separation.py::test_slack_recovery_matches_pressure_or_tie -q` | no — Wave 0 create. [RECOMMENDED] |
| THRY-02 | Binding example pressure action differs from finite-storage action using explicit fields. | unit | `python3 -m pytest tests/test_theory_separation.py::test_binding_example_separates_actions_with_explicit_state -q` | no — Wave 0 create. [RECOMMENDED] |
| THRY-03 | Binding example finite-storage action has strictly lower predeclared one-step objective. | unit | `python3 -m pytest tests/test_theory_separation.py::test_binding_example_strictly_improves_predeclared_objective -q` | no — Wave 0 create. [RECOMMENDED] |
| THRY-04 | Memo/artifact includes constrained LP oracle regret candidate and avoids stronger unsupported theorem language. | unit/static | `python3 -m pytest tests/test_theory_separation.py::test_guarantee_candidate_is_constrained_lp_oracle_regret -q` | no — Wave 0 create. [RECOMMENDED] |

### Sampling Rate

- **Per task commit:** `python3 -m pytest tests/test_theory_separation.py -q` [RECOMMENDED]
- **Per wave merge:** `python3 -m pytest tests/test_finite_storage_schema.py tests/test_claim_discipline.py tests/test_theory_separation.py -q` plus claim audit command below. [RECOMMENDED]
- **Phase gate:** full relevant tests and claim audit pass before verification. [RECOMMENDED]

### Wave 0 Gaps

- [ ] `scripts/check_theory_separation.py` — deterministic checker/generator for Phase 7 JSON. [RECOMMENDED]
- [ ] `tests/test_theory_separation.py` — tests THRY-01~THRY-04 contracts. [RECOMMENDED]
- [ ] `refine-logs/THEORY_AND_SEPARATION.md` — memo with theorem statements/proof sketches. [RECOMMENDED]
- [ ] `experiments/dual_sensitivity/phase7_theory_separation.json` — generated checker artifact. [RECOMMENDED]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No authentication surface in Phase 7 static artifacts. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| V3 Session Management | no | No sessions. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md] |
| V4 Access Control | no | Local file artifacts only. [VERIFIED: CLAUDE.md] |
| V5 Input Validation | yes | Use Phase 6 schema validators for JSON examples. [VERIFIED: scripts/finite_storage_schema.py] |
| V6 Cryptography | no | No cryptography or secrets. [VERIFIED: environment.yml; CLAUDE.md] |

### Known Threat Patterns for Phase 7 Static Artifacts

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed JSON artifact accepted as evidence | Tampering | Validate with `validate_state_objective_sample` and tests. [VERIFIED: scripts/finite_storage_schema.py; tests/test_finite_storage_schema.py] |
| Unsupported claim language enters reports | Repudiation / integrity | Run `scripts/audit_claim_discipline.py` over new memo and artifact paths. [VERIFIED: scripts/audit_claim_discipline.py; tests/test_claim_discipline.py] |
| Accidental secret/environment coupling | Information disclosure | Do not add `.env`, license IDs, or machine-specific secrets; Phase 7 needs no secrets. [VERIFIED: environment.yml; CLAUDE.md] |

## Concrete File and Command Plan for Planner

### Create / modify files

1. Create `refine-logs/THEORY_AND_SEPARATION.md` with sections `THRY-01` through `THRY-04`, explicit assumptions, proof sketches, and claim-boundary notes. [RECOMMENDED]
2. Create `scripts/check_theory_separation.py` that builds/loads Phase 7 examples, validates Phase 6 schema fields, recomputes pressure/finite-storage scores, and writes JSON. [RECOMMENDED]
3. Create `experiments/dual_sensitivity/phase7_theory_separation.json` via the checker, not manual transcription. [RECOMMENDED]
4. Create `tests/test_theory_separation.py` covering slack recovery, binding separation, strict objective margin, memo markers, schema validation, and claim-safe wording. [RECOMMENDED]
5. Avoid modifying `pi_light_code/` and avoid adding controller classes in Phase 7. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md; CLAUDE.md]

### Verification commands

```bash
python3 scripts/check_theory_separation.py --out experiments/dual_sensitivity/phase7_theory_separation.json
python3 -m pytest tests/test_theory_separation.py -q
python3 -m pytest tests/test_finite_storage_schema.py tests/test_claim_discipline.py tests/test_theory_separation.py -q
python3 scripts/audit_claim_discipline.py --paths refine-logs/THEORY_AND_SEPARATION.md experiments/dual_sensitivity/phase7_theory_separation.json --policy-out /tmp/phase7_claim_policy.json --audit-out /tmp/phase7_claim_audit.json
```

These commands are CPU/local-artifact oriented and do not require GPU or closed-loop SUMO. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md; environment.yml]

## Sources

### Primary (HIGH confidence)

- `/home/samuel/projects/pi_light_OR/.planning/phases/07-theory-and-separation-package/07-CONTEXT.md` — Phase boundary, THRY outcomes, claim discipline, artifact expectations.
- `/home/samuel/projects/pi_light_OR/.planning/PROJECT.md` — v1.1 finite-storage separation milestone and bounded claim constraints.
- `/home/samuel/projects/pi_light_OR/.planning/ROADMAP.md` — Phase 7/8/9/10/11/12 responsibility split.
- `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md` — THRY-01~THRY-04 requirement text.
- `/home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md` — existing LP notation, dual sign convention, pressure special case, binding-rank-change condition.
- `/home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_ATOMS.md` — minimal relaxation, movement marginal value, pressure/backpressure special case, oracle-regret objective.
- `/home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py` — canonical Phase 6 state/objective fields and validators.
- `/home/samuel/projects/pi_light_OR/scripts/claim_policy.py` — bounded claim vocabulary and forbidden-pattern policy.
- `/home/samuel/projects/pi_light_OR/scripts/audit_claim_discipline.py` — fail-closed claim audit CLI behavior.
- `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase6_explicit_state_schema.json` — generated schema artifact.
- `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase6_state_objective_fixtures.json` — explicit/proxy regime status and Phase 6 fixture fields.
- `/home/samuel/projects/pi_light_OR/tests/test_finite_storage_schema.py` — schema and fixture validation expectations.
- `/home/samuel/projects/pi_light_OR/tests/test_claim_discipline.py` — claim policy/audit behavior expectations.
- `/home/samuel/projects/pi_light_OR/CLAUDE.md` — project conventions, architecture, stack, workflow constraints.

### Secondary (MEDIUM confidence)

- Environment probes on 2026-05-24 for Python, pytest, and SUMO versions.

### Tertiary (LOW confidence)

- None. No web research was used, per user instruction.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — based on repository scripts, tests, local environment probes, and `environment.yml`. [VERIFIED: CLAUDE.md; environment.yml; environment probe]
- Architecture: HIGH — Phase boundaries and artifact locations are explicit in Phase 7 context and project conventions. [VERIFIED: .planning/phases/07-theory-and-separation-package/07-CONTEXT.md; CLAUDE.md]
- Theorem recommendation: MEDIUM — sign convention and slack special case are verified, but the exact Phase 7 theorem text still needs formal implementation. [VERIFIED: refine-logs/THEORY_AND_CLAIMS.md; scripts/run_dual_sanity.py]
- Separation example numbers: MEDIUM — construction is implementation-ready but recommended, not yet generated as a repository artifact. [ASSUMED]
- Pitfalls/guardrails: HIGH — backed by Phase 6 policy, audit, and fixtures. [VERIFIED: scripts/claim_policy.py; scripts/audit_claim_discipline.py; experiments/dual_sensitivity/phase6_state_objective_fixtures.json]

**Research date:** 2026-05-24  
**Valid until:** 2026-06-23 for repository-internal architecture; revisit if Phase 8 changes controller/state interfaces.
