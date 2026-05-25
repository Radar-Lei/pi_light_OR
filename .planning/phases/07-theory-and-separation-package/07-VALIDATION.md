---
phase: 07-theory-and-separation-package
status: draft
requirements:
  - THRY-01
  - THRY-02
  - THRY-03
  - THRY-04
---

# Phase 7 Validation Strategy

## Goal

Verify that Phase 7 produces a bounded, auditable finite-storage theory/separation package without entering live-controller or closed-loop experiment scope.

## Required Truths

1. The theory artifact states THRY-01 slack recovery: finite-storage primal-dual scoring reduces to classical max-pressure/backpressure under infinite storage, no switching loss, fixed turning ratios, and slack operational constraints.
2. A deterministic binding example shows pressure and finite-storage primal-dual scoring select different phases because explicit finite-storage/spillback/switching/service/incident fields bind.
3. The binding example predeclares a one-step constrained objective using Phase 6 objective components and shows strict improvement for the finite-storage action relative to the pressure action.
4. The package identifies exactly one additional guarantee candidate suitable for later use; default expected candidate is constrained LP oracle regret.
5. All Phase 7 outputs remain bounded-claim-safe and do not reinterpret v1.0 pressure-equivalent evidence as superiority evidence.

## Expected Artifacts

- `refine-logs/THEORY_AND_SEPARATION.md`
- `scripts/check_theory_separation.py`
- `experiments/dual_sensitivity/phase7_theory_separation.json`
- `tests/test_theory_separation.py`

## Verification Commands

Targeted checks:

```bash
cd /home/samuel/projects/pi_light_OR && python3 scripts/check_theory_separation.py --out experiments/dual_sensitivity/phase7_theory_separation.json
cd /home/samuel/projects/pi_light_OR && python3 -m pytest tests/test_theory_separation.py -q
```

Relevant regression checks:

```bash
cd /home/samuel/projects/pi_light_OR && python3 -m pytest tests/test_finite_storage_schema.py tests/test_claim_discipline.py tests/test_theory_separation.py -q
```

Claim audit over new Phase 7 surfaces:

```bash
cd /home/samuel/projects/pi_light_OR && python3 scripts/audit_claim_discipline.py --paths refine-logs/THEORY_AND_SEPARATION.md experiments/dual_sensitivity/phase7_theory_separation.json --policy-out /tmp/phase7_claim_policy.json --audit-out /tmp/phase7_claim_audit.json
```

## Scope Guards

- Do not add a live SUMO controller or wire `full_dual_symbolic`; that is Phase 8.
- Do not run closed-loop SUMO experiments; those belong to later gates.
- Do not add new baselines or stress scenarios; those belong to Phase 10.
- Do not draft final manuscript sections or related work.
- Do not use proxy-only v1.0 labels as final binding-regime superiority evidence.
