---
phase: 09-slack-and-binding-kill-gates
status: draft
requirements:
  - GATE-01
  - GATE-02
  - GATE-04
---

# Phase 9 Validation Strategy

## Goal

Verify that Phase 9 adds fail-closed slack and binding gates that consume explicit finite-storage state and action decomposition evidence, while avoiding Gate C and closed-loop dominance claims.

## Required Truths

1. `scripts/run_slack_binding_gates.py` writes `experiments/dual_sensitivity/phase9_slack_binding_gates.json` with `status: PASSED` on canonical Phase 7/8 inputs.
2. Gate A verifies slack recovery/tie behavior and reports ties as expected behavior, not superiority.
3. Gate B verifies binding action separation and strict one-step constrained-objective improvement.
4. Gate B diagnostics identify storage/spillback/switching/incident changing terms from recomputed Phase 8 action audit.
5. Gate outputs fail closed when `finite_storage_state`, `objective_components`, action audit fields, pressure comparator fields, or required examples are missing.
6. Payload scope/caveats explicitly exclude Gate C, paired-seed closed-loop dominance, baseline suites, stress scenarios, and manuscript claims.

## Expected Modified Files

- `scripts/run_slack_binding_gates.py`
- `tests/test_slack_binding_gates.py`
- `experiments/dual_sensitivity/phase9_slack_binding_gates.json`

## Verification Commands

```bash
cd /home/samuel/projects/pi_light_OR && python3 -m py_compile scripts/run_slack_binding_gates.py tests/test_slack_binding_gates.py
cd /home/samuel/projects/pi_light_OR && python3 -m pytest tests/test_slack_binding_gates.py -q
cd /home/samuel/projects/pi_light_OR && python3 scripts/run_slack_binding_gates.py --phase7-json experiments/dual_sensitivity/phase7_theory_separation.json --out experiments/dual_sensitivity/phase9_slack_binding_gates.json
```

Relevant regression:

```bash
cd /home/samuel/projects/pi_light_OR && python3 -m pytest tests/test_slack_binding_gates.py tests/test_closed_loop_sumo.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q
```

## Scope Guards

- Do not add Gate C.
- Do not run paired-seed or long-horizon SUMO evidence.
- Do not add new baselines or stress scenarios.
- Do not write manuscript text or dominance claims.
- Do not weaken Phase 8 `full_dual_symbolic` not-feasible guard.
