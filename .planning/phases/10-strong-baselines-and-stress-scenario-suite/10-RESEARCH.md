---
phase: 10-strong-baselines-and-stress-scenario-suite
status: complete
requirements:
  - EXP-01
  - EXP-02
  - EXP-04
---

# Phase 10 Research Notes

## Recommended Approach

Extend the existing closed-loop suite rather than creating a separate experiment framework. The main work should be deterministic scenario/baseline registration and smoke-level validation, not long-horizon evidence.

## Existing Patterns

- `scripts/run_closed_loop_sumo.py` centralizes controller choice, failure/demand-shift mechanics, and row schema validation.
- `scripts/run_closed_loop_suite.py` centralizes scenario specs, controller coverage, aggregation, baseline coverage, and completion gates.
- `tests/test_closed_loop_sumo.py` already tests suite spec, baseline coverage, real mechanism flags, and renderers.

## Implementation Guidance

Likely files:

- `scripts/run_closed_loop_sumo.py`
- `scripts/run_closed_loop_suite.py`
- `tests/test_closed_loop_sumo.py`
- `experiments/dual_sensitivity/phase10_baselines_stress_suite.json`

Add controller names only if they are lightweight and honest:

- `cycle_pressure`: cycle/phase-hold pressure variant using existing phase scoring but with longer hold or cycle bias.
- `finite_storage_double_pressure`: finite-storage-aware pressure variant that can reuse finite-storage decomposition or capacity-aware terms without changing Phase 8 audited proposed path.

Add scenario tags with explicit mechanics/metadata:

- downstream blockage and spillback can reuse speed reduction/failure-mode mechanics plus row metadata.
- incident capacity drop can reuse failure mode and set incident metadata.
- oversaturation and turning shock can reuse demand insertion mechanics with explicit scenario tags and metadata.
- switching-loss-sensitive can use shorter action interval or metadata showing switching-lost-time emphasis without running long horizons.

## Validation Priorities

- Suite spec includes required strong baseline/controller set.
- Stress scenario coverage reports all six stress categories.
- Rows for stress scenarios include explicit finite-storage state and objective components.
- `finite_storage_primal_dual` rows include action decomposition where run.
- Grid fixed-time counterexample is represented as a documented check/metadata, not a broad claim.
- Scope caveats exclude Gate C, paired-seed dominance, long-horizon statistics, and manuscript claims.

## Open Questions (RESOLVED)

- **Should Phase 10 run long horizons?** No. It should create suite/scenario capability and short smoke validation only.
- **Should Phase 10 add new neural baselines?** No. Keep CPU/SUMO feasible baselines.
- **Should Phase 10 make performance claims?** No. Performance/dominance claims require Phase 11 evidence.
