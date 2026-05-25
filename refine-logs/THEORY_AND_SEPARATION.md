# Finite-Storage Theory and Separation Memo

**Date:** 2026-05-24  
**Phase:** 07 — Theory and Separation Package  
**Requirements covered:** THRY-01, THRY-02, THRY-03, THRY-04  
**Primary references:** `refine-logs/THEORY_AND_CLAIMS.md`, `refine-logs/THEORY_AND_ATOMS.md`, `experiments/dual_sensitivity/phase7_theory_separation.json`, `scripts/check_theory_separation.py`, `scripts/finite_storage_schema.py`, `scripts/claim_policy.py`

## Purpose

This memo sharpens the v1.1 finite-storage primal-dual claim into a bounded theory package. It records when the finite-storage score recovers or ties classical max-pressure/backpressure, and it gives a deterministic static one-step example where explicit downstream storage and spillback fields change the selected phase and improve the predeclared local objective.

This is a theory/static artifact. It is not a live SUMO controller, not closed-loop evidence, not a baseline suite, and not a final manuscript section.

## Claim-Discipline Guardrails

Allowed within this Phase 7 artifact:

- state that slack finite-storage and operational constraints recover or tie max-pressure/backpressure;
- construct an explicit binding finite-storage/spillback example with validated `finite_storage_state` and `objective_components`;
- show static one-step action separation and strict local objective improvement in the generated Phase 7 artifact;
- identify one finite-sample, oracle-relative follow-up guarantee candidate.

Not allowed within this Phase 7 artifact:

- claiming live-controller or closed-loop performance from the static example;
- claiming deployment readiness or universal cross-regime advantage;
- treating v1.0 pressure-equivalent evidence as superiority evidence; it remains historical and insufficient for the v1.1 binding-regime improvement claim;
- adding controller wiring, closed-loop SUMO experiments, new baselines, related work, final manuscript drafting, or submission preparation.

## Notation and Existing Sign Convention

The project keeps the Phase 1 movement-value sign convention:

```text
MovementValue(i,j) = lambda_up - lambda_down.
```

When link values specialize to queue occupancies and all finite-storage or operational corrections are absent, slack, or ranking-neutral, this becomes the classical movement pressure:

```text
Pressure(i,j) = x_up - x_down.
```

For a phase `p`, the phase score is the sum of its compatible movement scores. The deterministic Phase 7 checker uses one movement per candidate phase so the phase score equals the movement score.

## THRY-01 — Slack finite-storage recovery of max-pressure/backpressure

### Theorem

Consider a fixed signal-decision interval with fixed candidate phases, fixed turning ratios, and movement services compared away from non-neutral service bounds. If downstream storage is infinite or nonbinding, residual receiving-capacity constraints are slack, spillback/blocking indicators are false, switching-loss terms are zero or common across candidate phases, incident-capacity-drop terms are inactive, and service/resource constraints are slack or ranking-neutral, then the finite-storage primal-dual phase ranking recovers or ties classical max-pressure/backpressure.

### Proof sketch

By the Phase 1 dual-sensitivity decomposition, the conservation-dual part of a movement score is `lambda_up - lambda_down`. Under slack finite-storage and operational constraints, storage, receiving-capacity, spillback, switching, incident, and service-resource multipliers either vanish or add no non-neutral rank change. With queue-specialized link values, `lambda_up - lambda_down = x_up - x_down`. Summing over a fixed phase movement set gives the classical phase pressure score. Ties are expected recovery/tie behavior, not a failure of the theorem.

### Checker alignment

`experiments/dual_sensitivity/phase7_theory_separation.json` contains the `slack_recovery` example. Its `finite_storage_state` has positive residual receiving capacity, no spillback/blocking flags, inactive incident metadata, and no switching loss. The checker verifies that the pressure action and finite-storage action match or tie.

## THRY-02 — Explicit binding finite-storage separation

### Counterexample structure

The generated artifact contains `storage_binding_two_phase_separation`, a two-phase static example with one movement per phase:

- `phase_a`: movement `up_a -> down_a`;
- `phase_b`: movement `up_b -> down_b`.

Classical pressure scores are computed as `queue_up - queue_down`. With the generated queues, pressure selects `phase_a`. However, `down_a` has zero residual receiving capacity and explicit spillback/blocking flags, while `down_b` has positive residual receiving capacity and no spillback/blocking flags. The finite-storage score applies a declared storage/scarcity correction to the blocked downstream movement, so it selects `phase_b`.

### Rank-change algebra

Let `P_a` and `P_b` be classical pressure scores, and let `C_a` and `C_b` be explicit finite-storage correction terms derived from written storage/spillback fields. The finite-storage scores are

```text
D_a = P_a + C_a,
D_b = P_b + C_b.
```

Pressure selects `a` when `P_a > P_b`. A binding finite-storage correction changes the action when

```text
C_b - C_a > P_a - P_b.
```

The generated example satisfies this condition because `phase_a` sends flow into a blocked downstream link while `phase_b` does not.

## THRY-03 — Strict one-step constrained objective improvement

The one-step objective is predeclared before action comparison:

```text
J(action) = delay
          + unfinished_vehicle_penalty
          + spillback_blocking_time
          + switching_lost_time.
```

These component names exactly match the Phase 6 `objective_components` schema. The generated JSON stores unit nonnegative weights for these four terms and records per-action objective components before computing action totals.

In the binding example, the pressure action `phase_a` incurs unfinished-vehicle and spillback/blocking penalties from sending service toward a blocked downstream link. The finite-storage action `phase_b` avoids those terms. The checker recomputes totals and records a positive `objective_margin`, so the finite-storage action has strictly lower predeclared one-step objective cost than the pressure-selected action in this static example.

This is a local structural separation criterion. It does not establish closed-loop network performance; later phases must build controller, kill-gate, baseline, and paired-seed evidence before any broader empirical claim.

## THRY-04 — Constrained LP oracle regret guarantee candidate

The single Phase 7 follow-up guarantee candidate is **constrained LP oracle regret**.

For a finite audited dataset `D_N` of explicit finite-storage states, let `a*_n` be the action minimizing a predeclared constrained one-step objective `J_n(a)`. For any policy `pi` in a finite symbolic or controller class `Pi`, define empirical constrained-oracle regret as

```text
R_hat_N(pi) = (1/N) sum_n [J_n(pi(s_n)) - J_n(a*_n)].
```

If a recovery procedure returns `pi_hat` within optimization gap `epsilon_opt` of the best policy in `Pi` under declared penalties, then the future candidate statement is

```text
R_hat_N(pi_hat) + penalty(pi_hat)
  <= min_{pi in Pi} [R_hat_N(pi) + penalty(pi)] + epsilon_opt.
```

This candidate is finite-sample and oracle-relative. It does not establish closed-loop network stability, deployment performance, or global optimality. Stronger bounded-drift or throughput statements are later-phase theory work after the live controller and finite-storage dynamics are fixed.

## Artifact Trace

- `scripts/check_theory_separation.py` builds and validates the deterministic examples.
- `experiments/dual_sensitivity/phase7_theory_separation.json` records `status: PASSED`, THRY-01 through THRY-04 coverage, Phase 6 schema version, objective definition, examples, and claim scope.
- `tests/test_theory_separation.py` verifies slack recovery, binding action separation, strict one-step objective margin, memo markers, claim-safe wording, and the constrained LP oracle regret candidate.
- `scripts/audit_claim_discipline.py` is the claim-language gate for this memo and the generated JSON.
