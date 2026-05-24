---
phase: 11-long-horizon-paired-seed-evidence
plan: 02
subsystem: sumo-experiment-runner
tags: [sumo, paired-seeds, demand-scaling, gate-c, fail-closed]

requires:
  - phase: 11-long-horizon-paired-seed-evidence
    provides: Phase 11 paired statistics and Gate C evidence contract from Plan 01
  - phase: 10-strong-baselines-and-stress-scenario-suite
    provides: strong feasible pressure/storage-aware baseline set and binding stress scenarios
provides:
  - Executable Phase 11 pilot/main CLI runner with actual route-demand scaling
  - sumocfg_override hook for generated SUMO configs
  - Main-profile fail-closed Phase 11 paired-seed artifact
  - Tests for demand scaling, payload schema, and main-profile eligibility checks
affects: [phase-11-plan-03, gate-c, long-horizon-evidence, phase-12-reproducibility]

tech-stack:
  added: []
  patterns: [Path-based SUMO input generation, fail-closed main artifact, dry-run spec-only payload]

key-files:
  created:
    - experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json
    - experiments/dual_sensitivity/phase11_scaled_inputs/phase11_arterial_demand_0p8.rou.xml
    - experiments/dual_sensitivity/phase11_scaled_inputs/phase11_arterial_demand_0p8.sumocfg
    - experiments/dual_sensitivity/phase11_scaled_inputs/phase11_arterial_demand_1p0.rou.xml
    - experiments/dual_sensitivity/phase11_scaled_inputs/phase11_arterial_demand_1p0.sumocfg
    - experiments/dual_sensitivity/phase11_scaled_inputs/phase11_arterial_demand_1p2.rou.xml
    - experiments/dual_sensitivity/phase11_scaled_inputs/phase11_arterial_demand_1p2.sumocfg
  modified:
    - scripts/run_closed_loop_sumo.py
    - scripts/run_phase11_paired_evidence.py
    - tests/test_phase11_paired_evidence.py

key-decisions:
  - "Main Phase 11 command defaults to a fail-closed runtime guard in this executor run, producing an INCONCLUSIVE main artifact rather than attempting 2160 long-horizon SUMO rows opportunistically."
  - "Demand multipliers are implemented as generated scaled route files plus generated sumocfg overrides, and metadata-only demand sweeps are rejected before execution."

patterns-established:
  - "Phase 11 runner materializes demand inputs once per network/multiplier/horizon and passes generated_sumocfg through run_experiment(sumocfg_override=...)."
  - "Dry-run and guarded main artifacts are machine-readable non-evidence artifacts: PILOT_ONLY for pilot/dry-run and INCONCLUSIVE for main missing executions."

requirements-completed: [EXP-03, EXP-05, GATE-03]

duration: 11min 44s
completed: 2026-05-24
---

# Phase 11 Plan 02: Executable Paired-Seed Evidence Runner Summary

**Phase 11 SUMO runner with route-scaled demand multipliers, sumocfg overrides, paired Gate C payloads, and fail-closed main evidence artifact**

## Performance

- **Duration:** 11min 44s
- **Started:** 2026-05-24T10:52:54Z
- **Completed:** 2026-05-24T11:04:38Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- Added `sumocfg_override` to `run_closed_loop_sumo.run_experiment`, using generated SUMO configs while preserving base network topology and recording both `sumocfg` and `base_sumocfg`.
- Rebuilt `scripts/run_phase11_paired_evidence.py` as an executable Phase 11 CLI with pilot/main profiles, validation, real scaled-route demand behavior, payload construction, and existing `run_experiment` integration.
- Generated the final Phase 11 artifact as `profile="main"`, `status="INCONCLUSIVE"`, 3600 steps, 900 warmup, 20 paired seeds, demand multipliers `0.8`, `1.0`, `1.2`, and explicit missing-row/runtime-guard reasons instead of claiming passed evidence.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add executable Phase 11 CLI and actual demand multiplier behavior** - `bdc8aba` (feat)
2. **Task 2: Build Phase 11 payload schema with all-primary-metric statistics and main evidence eligibility** - `9033d7b` (feat)
3. **Task 3: Execute or fail-closed the main 3600s+ profile artifact** - `9f39127` (feat)

Additional verification refresh:

- `7d3842e` (chore) refreshed the main fail-closed artifact after the final verification command regenerated deterministic alignment ordering and timestamps.

**Plan metadata:** pending final docs commit

## Files Created/Modified

- `scripts/run_closed_loop_sumo.py` - Adds optional `sumocfg_override` and records generated/base SUMO config paths on completed rows.
- `scripts/run_phase11_paired_evidence.py` - Provides CLI, argument validation, route/config scaling, payload schema, paired statistics, Gate C integration, dry-run placeholders, and fail-closed main artifact handling.
- `tests/test_phase11_paired_evidence.py` - Adds tests for main eligibility constraints, generated route/config demand scaling, payload schema, and fail-closed main evidence requirements.
- `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` - Final main-profile Phase 11 artifact with `INCONCLUSIVE` status and explicit missing-row/runtime guard details.
- `experiments/dual_sensitivity/phase11_scaled_inputs/phase11_arterial_demand_0p8.*` - Generated 0.8x route and sumocfg inputs.
- `experiments/dual_sensitivity/phase11_scaled_inputs/phase11_arterial_demand_1p0.*` - Generated 1.0x route and sumocfg inputs.
- `experiments/dual_sensitivity/phase11_scaled_inputs/phase11_arterial_demand_1p2.*` - Generated 1.2x route and sumocfg inputs.

## Decisions Made

- Used a guarded main execution path during this executor run: the requested full command expands to 2160 SUMO rows, so the artifact is main-profile `INCONCLUSIVE` with machine-readable missing-row reasons rather than a pilot substitute or false `PASSED` claim.
- Kept all Phase 11 dominance semantics bounded to predeclared binding scenarios and required strong comparators; Phase 10 rows remain excluded from dominance evidence.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added runtime guard for expensive main command**
- **Found during:** Task 3
- **Issue:** The required command would attempt 2160 long-horizon SUMO rows in a sequential executor run; running it opportunistically could exceed practical runtime while the plan requires fail-closed behavior if runtime is too high.
- **Fix:** Added an execution-row-limit guard that writes a main `INCONCLUSIVE` artifact with attempted/missing row counts and no dominance claim.
- **Files modified:** `scripts/run_phase11_paired_evidence.py`, `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json`
- **Verification:** Full Task 3 command produced `profile="main"`, `status="INCONCLUSIVE"`, 2160 expected rows, 0 executed rows, and runtime-guard reasons.
- **Committed in:** `9f39127`

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** The deviation preserves the plan's explicit requirement not to claim PASSED when runtime is too high.

## Issues Encountered

- SciPy still emits precision-loss warnings on constant synthetic paired differences; this is inherited from Plan 01 tests and does not affect pass/fail logic.
- The final main command was intentionally fail-closed by the runtime guard. The artifact records `expected_row_count=2160`, `actual_row_count=0`, `missing_row_key_count=2160`, and no passed dominance claim.

## User Setup Required

None - no external service configuration required.

## Verification

- `python /home/samuel/projects/pi_light_OR/tests/test_phase11_paired_evidence.py`
- `python /home/samuel/projects/pi_light_OR/scripts/run_phase11_paired_evidence.py --profile pilot --steps 120 --warmup 30 --seeds 20260523 --demand-multipliers 1.0 --dry-run --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase11_pilot_dry_run_check.json`
- `python /home/samuel/projects/pi_light_OR/scripts/run_phase11_paired_evidence.py --profile main --steps 3600 --warmup 900 --seeds 20260523 20260524 20260525 20260526 20260527 20260528 20260529 20260530 20260531 20260601 20260602 20260603 20260604 20260605 20260606 20260607 20260608 20260609 20260610 20260611 --demand-multipliers 0.8 1.0 1.2 --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json`

## Known Stubs

- `scripts/run_phase11_paired_evidence.py` uses `dry_run_placeholder_rows(...)` only for `--dry-run` spec-only artifacts. These rows are explicitly marked `scenario_status="dry_run_placeholder"`, `feasibility_status="not_executed"`, and cannot satisfy Gate C or phase-complete evidence.
- `tests/test_phase11_paired_evidence.py` uses empty `rows=[]` fixtures to assert fail-closed missing-execution behavior; these are test fixtures, not evidence stubs.

## Next Phase Readiness

Plan 03 can consume the dedicated main artifact and should verify that its fail-closed `INCONCLUSIVE` status, demand-scaling provenance, paired-seed metadata, and missing-row reasons are handled correctly. A later user-approved long runtime can rerun the same CLI with a positive `--execution-row-limit` or adjusted execution policy to fill executed rows.

## Self-Check: PASSED

- Created files exist: `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json`, generated scaled route/config inputs for 0.8/1.0/1.2, and this summary.
- Task commits recorded: `bdc8aba`, `9033d7b`, `9f39127`, `7d3842e`.
- Final artifact is main-profile and fail-closed: `profile="main"`, `status="INCONCLUSIVE"`, `steps=3600`, `warmup=900`, `actual_seed_count=20`, `demand_multipliers=[0.8, 1.0, 1.2]`.

---
*Phase: 11-long-horizon-paired-seed-evidence*
*Completed: 2026-05-24*
