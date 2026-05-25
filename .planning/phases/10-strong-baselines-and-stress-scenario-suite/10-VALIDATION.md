---
phase: 10-strong-baselines-and-stress-scenario-suite
status: draft
requirements:
  - EXP-01
  - EXP-02
  - EXP-04
---

# Phase 10 Validation Strategy

## Goal

Verify that Phase 10 adds strong feasible baselines and explicit finite-storage stress scenario suite coverage while preserving claim discipline and avoiding Phase 11 paired-seed dominance evidence.

## Required Truths

1. Suite/controller registry includes feasible strong baselines: fixed-time, actuated/local actuation, max-pressure, capacity-aware pressure, finite-storage primal-dual, and any added cycle/finite-storage pressure variants.
2. Old unsafe `full_dual_symbolic` and `local_pilight` remain honestly not feasible unless safely implemented.
3. Stress scenario coverage includes downstream blockage, spillback, incident/capacity drop, oversaturation, turning shock, and switching-loss-sensitive categories.
4. Grid fixed-time counterexample is represented as an explicit check/metadata before broad performance language.
5. Phase 10 artifact is schema-valid, machine-readable, and uses caveats that forbid treating smoke runs as dominance evidence.
6. No Gate C, paired-seed CI, long-horizon statistics, or manuscript claims are introduced.

## Expected Modified Files

- `scripts/run_closed_loop_sumo.py`
- `scripts/run_closed_loop_suite.py`
- `tests/test_closed_loop_sumo.py`
- `experiments/dual_sensitivity/phase10_baselines_stress_suite.json`

## Verification Commands

```bash
cd /home/samuel/projects/pi_light_OR && python3 -m py_compile scripts/run_closed_loop_sumo.py scripts/run_closed_loop_suite.py tests/test_closed_loop_sumo.py
cd /home/samuel/projects/pi_light_OR && python3 -m pytest tests/test_closed_loop_sumo.py -q
cd /home/samuel/projects/pi_light_OR && python3 scripts/run_closed_loop_suite.py --profile smoke --controllers fixed_time actuated_local_pressure max_pressure capacity_aware_pressure finite_storage_primal_dual --steps 80 --warmup 20 --action-interval 10 --out experiments/dual_sensitivity/phase10_baselines_stress_suite.json
```

Relevant regression:

```bash
cd /home/samuel/projects/pi_light_OR && python3 -m pytest tests/test_closed_loop_sumo.py tests/test_slack_binding_gates.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q
```

## Scope Guards

- Do not run long-horizon main evidence.
- Do not add paired confidence intervals or Gate C logic.
- Do not write manuscript claims.
- Do not remove not-feasible guards for unsafe controllers.
