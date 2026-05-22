---
phase: 03-static-pressure-failure-kill-gate
plan: "01"
subsystem: experiment-fixtures
tags: [python, sumo, static-regimes, sampled-states, kill-gate]

requires:
  - phase: 02-full-sparse-symbolic-recovery
    provides: Sparse recovery and sampled-state conversion contracts consumed by Phase 3.
provides:
  - Deterministic Phase 3 static-regime state generator.
  - 1,200-sample labeled static regime fixture with counts and proxy rationale.
affects: [phase-03-static-kill-gate, KILL-01, KILL-03]

tech-stack:
  added: []
  patterns:
    - Reuse sample_sumo_states.build_network_metadata for capacities and TLS movements.
    - Preserve scenario_from_sample-compatible sampled-state schema while adding regime labels.

key-files:
  created:
    - scripts/generate_static_regime_states.py
    - experiments/dual_sensitivity/block3_regime_states.json
    - tests/test_generate_static_regime_states.py
  modified: []

key-decisions:
  - "Represent supply-binding and corridor-bottleneck as explicit proxy regimes because the current downstream conversion schema has no supply or corridor-level constraint fields."
  - "Keep KILL-03 sufficiency preliminary at fixture-generation time; final valid-example sufficiency is deferred to run_static_kill_gate.py conversion in Plan 03-02."

patterns-established:
  - "Static regime fixtures carry counts_by_regime, regime_status, generation_config, and sample_sufficiency_note at top level."
  - "Each generated sample preserves time, queues, vehicle_counts, capacities, and tls_movements, then adds regime, regime_detail, and generated_by."

requirements-completed: [KILL-01, KILL-03]

duration: 9min
completed: 2026-05-22
---

# Phase 3 Plan 01: Static Regime State Fixture Summary

**Deterministic SUMO-topology static-regime fixture generation with explicit proxy rationale for Phase 3 kill-gate sampling.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-05-22T18:47:40Z
- **Completed:** 2026-05-22T18:53:10Z
- **Tasks:** 2 completed
- **Files modified:** 3 created

## Accomplishments

- Created `scripts/generate_static_regime_states.py` with argparse CLI, deterministic seed handling, network metadata reuse, TLS validation, positive numeric validation, and compact JSON stdout.
- Generated `experiments/dual_sensitivity/block3_regime_states.json` with 1,200 samples: 200 each for `slack`, `storage_binding`, `supply_binding_proxy`, `corridor_bottleneck_proxy`, `incident_capacity_drop`, and `demand_shift_proxy`.
- Preserved downstream sample fields required by `scenario_from_sample()` and added `regime`, `regime_detail`, and `generated_by` to each sample.
- Added explicit top-level `counts_by_regime`, `regime_status`, `generation_config`, `target_per_regime`, and `sample_sufficiency_note` so KILL-03 is auditable without overstating valid converted examples.

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Create failing generator behavior test** - `c633247` (test)
2. **Task 1 GREEN: Create deterministic multi-regime state generator** - `e8a3d28` (feat)
3. **Task 2: Materialize the Phase 3 regime fixture artifact** - `5100070` (chore)

## Files Created/Modified

- `scripts/generate_static_regime_states.py` - Deterministic labeled-regime state generator for Phase 3.
- `experiments/dual_sensitivity/block3_regime_states.json` - Combined labeled state fixture for the static kill gate.
- `tests/test_generate_static_regime_states.py` - Script-based TDD behavior checks for generator schema and CLI validation.

## Verification Results

Plan verification commands passed:

- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 -m py_compile /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py`
- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py --target-per-regime 10 --out /tmp/block3_regime_states.json`
- Smoke schema assertion printed `generator schema ok`.
- `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py --target-per-regime 200 --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_regime_states.json`
- Artifact assertion printed `regime artifact ok`.

Materialized artifact summary:

| Regime | Count | Status |
|---|---:|---|
| slack | 200 | supported_synthetic |
| storage_binding | 200 | supported_synthetic |
| supply_binding_proxy | 200 | proxy |
| corridor_bottleneck_proxy | 200 | proxy |
| incident_capacity_drop | 200 | supported_synthetic |
| demand_shift_proxy | 200 | proxy |

## Decisions Made

- Used `supply_binding_proxy` rather than a stronger supply-binding label because current `scenario_from_sample()` does not consume an explicit per-movement supply field.
- Used `corridor_bottleneck_proxy` rather than a stronger corridor-binding label because current static samples do not encode a corridor-level capacity constraint.
- Added a TDD smoke test file even though the plan only listed generator and artifact files, because Task 1 was marked `tdd="true"` and required a RED/GREEN gate.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added executable TDD smoke tests**
- **Found during:** Task 1 (Create deterministic multi-regime state generator)
- **Issue:** The plan marked Task 1 as TDD but did not list a test file. Without a test artifact, RED/GREEN compliance would be unverifiable.
- **Fix:** Added `tests/test_generate_static_regime_states.py` covering schema-compatible output and invalid CLI inputs.
- **Files modified:** `tests/test_generate_static_regime_states.py`
- **Verification:** Initial corrected RED failed because `generate_static_regime_states.py` was missing; GREEN passed after implementation.
- **Committed in:** `c633247` and `e8a3d28`

**2. [Rule 1 - Bug] Fixed false-positive RED test execution**
- **Found during:** Task 1 RED phase
- **Issue:** The first test file version defined test functions but had no script entry point, so direct `python3 tests/test_generate_static_regime_states.py` exited successfully without executing assertions.
- **Fix:** Added a `main()` function with a temporary directory that invokes both behavior checks.
- **Files modified:** `tests/test_generate_static_regime_states.py`
- **Verification:** Corrected RED failed with missing-script error before implementation, then passed after generator implementation.
- **Committed in:** `c633247`

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 bug)
**Impact on plan:** Deviations were limited to TDD compliance and did not expand Phase 3 scope beyond fixture generation.

## Issues Encountered

- Existing working tree contained many unrelated modified/untracked files before execution. These were left untouched; only the 03-01 files above were staged and committed.
- The repository is currently on `main` and not a GSD worktree. The worktree-specific protected-branch assertion did not apply because `.git` is a directory, not a file.

## Known Stubs

None found in created code. The scan only matched `default=None` in argparse, which is normal CLI default handling and not a UI/data stub.

## Threat Flags

None. The new surface is a local CLI artifact generator already covered by the plan threat model; it validates positive numeric flags, rejects unknown regimes, and writes only the requested output path while creating parent directories.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 03-02 can consume `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_regime_states.json` to compute valid converted examples, per-regime dual-vs-pressure metrics, and the route decision. The fixture explicitly warns that raw sample counts are preliminary until `scenario_from_sample()` and `build_example()` conversion occurs.

## Self-Check: PASSED

- Found created files:
  - `/home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py`
  - `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_regime_states.json`
  - `/home/samuel/projects/pi_light_OR/tests/test_generate_static_regime_states.py`
- Found task commits: `c633247`, `e8a3d28`, `5100070`
- Verification commands completed successfully.

---
*Phase: 03-static-pressure-failure-kill-gate*
*Completed: 2026-05-22*
