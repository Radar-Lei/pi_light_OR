---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Explicit Finite-Storage Primal-Dual Separation
status: ready_to_plan
stopped_at: Phase 06 complete (3/3) — ready to discuss Phase 7
last_updated: 2026-05-24T02:50:10.684Z
last_activity: 2026-05-23
progress:
  total_phases: 7
  completed_phases: 1
  total_plans: 3
  completed_plans: 19
  percent: 14
---

# Project State

## Project Reference

See: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md (updated 2026-05-23)

**Core value:** Show that finite-storage primal-dual pressure control strictly generalizes max-pressure: it reduces to pressure when constraints are slack, adds scarcity-aware shadow-price corrections when storage, spillback, switching, service, or incident constraints bind, and can be deployed or compressed into auditable symbolic traffic-signal policies.
**Current focus:** Phase 7 — theory and separation package

## Current Position

Phase: 7
Plan: Not started
Status: Ready to plan
Last activity: 2026-05-24

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 18 from v1.0
- v1.1 plans completed: 0
- Average duration: N/A
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. Theoretical Core and Claim Lock | 3/3 | Complete |
| 2. Full Sparse Symbolic Recovery | 3/3 | Complete |
| 3. Static Pressure-Failure Kill Gate | 3/3 | Complete |
| 4. Closed-Loop SUMO Evaluation | 3/3 | Complete |
| 5. Reproducibility and Repository Hardening | 3/3 | Complete |
| 6. Claim Discipline and Explicit State Foundation | 0/TBD | Ready to plan |
| 7. Theory and Separation Package | 0/TBD | Not started |
| 8. Live Finite-Storage Primal-Dual Controller | 0/TBD | Not started |
| 9. Slack and Binding Kill Gates | 0/TBD | Not started |
| 10. Strong Baselines and Stress Scenario Suite | 0/TBD | Not started |
| 11. Long-Horizon Paired-Seed Evidence | 0/TBD | Not started |
| 12. Reproducibility and Future Claim Inputs | 0/TBD | Not started |
| Phase 06 P01 | 9min 11s | 3 tasks | 5 files |
| Phase 06 P02 | 14min 31s | 3 tasks | 6 files |
| Phase 06 P03 | 10min 37s | 3 tasks | 10 files |

## Accumulated Context

### Decisions

- [Phase 03]: Keep the locked static route as pressure-equivalent: dual-recovers/ties pressure under sample-relative oracle-regret evidence, not dual superiority.
- [Phase 04]: Mark `local_pilight` and `full_dual_symbolic` as explicit `not_feasible` rather than substituting unsafe queue heuristics.
- [Phase 05]: Paper-facing artifacts must fail closed unless upstream source artifacts report `PASSED`, route decisions agree, closed-loop completion gates pass, expected artifacts parse, and closed-loop metric schema is complete.
- [v1.1 Roadmap]: Do not start paper drafting in this milestone; build only theory, controller, experiments, gates, reproducibility, and future manuscript inputs.
- [v1.1 Roadmap]: Strong claim remains bounded: recover/tie max-pressure when constraints are slack; claim wins only when finite-storage/spillback/switching/service/incident constraints bind.
- [Phase 06]: Plan 01 claim scans treat negated/bounded caveats as safe while failing affirmative superiority wording.
- [Phase 06]: Plan 01 historical v1.0 pressure-equivalent artifacts are quarantined as insufficient_historical_v1_0 rather than treated as binding-regime superiority evidence.
- [Phase 06]: Plan 02 explicit fixtures preserve legacy sample keys while adding validated finite_storage_state and objective_components nested objects.
- [Phase 06]: Plan 02 build_objective_components_from_metrics is the canonical shared helper for static fixtures and later closed-loop metric rows.
- [Phase 06]: Plan 02 proxy regime labels remain historical/insufficient unless paired with validated explicit state and objective fields.
- [Phase 06]: Plan 03 closed-loop objective_components remain row-level audit fields and are not CI-aggregated through METRIC_FIELDS.
- [Phase 06]: Plan 03 infeasible/not_feasible closed-loop rows carry schema-valid unavailable finite_storage_state objects instead of omitting explicit state.
- [Phase 06]: Plan 03 paper-facing artifact validation treats Phase 6 claim/state guard artifacts as mandatory before output generation.
- [Phase 06]: Plan 03 claim scanning uses central claim_policy prose checks while policy/audit metadata fields are validated separately.

### Pending Todos

Verify Phase 6 completion, then plan Phase 7 with `/gsd:plan-phase 7`.

### Blockers/Concerns

- v1.1 must not reinterpret v1.0 pressure-equivalent evidence as superiority evidence.
- v1.1 must not include manuscript drafting, related-work writing, final paper integration, or submission preparation.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Manuscript | Full paper drafting, related work, final integration, and submission preparation | Deferred to v2 after v1.1 gates determine surviving claims | v1.1 roadmap |
| Benchmarks | RESCO/CityFlow/LibSignal, larger real-world benchmarks, and neural MARL baselines | Deferred to v2 unless v1.1 core result survives | v1.0 close |
| Integration | Phase 3 consumes Phase 2 recovery implementation directly rather than Phase 2 generated JSON/CSV/rule artifacts | Acknowledged as non-blocking tech debt | v1.0 close |
| Baselines | `local_pilight` and old `full_dual_symbolic` are marked `not_feasible` in closed-loop artifacts | v1.1 must safely wire a finite-storage successor or keep unsafe paths excluded | v1.0 close |

## Session Continuity

Last session: 2026-05-23T13:01:36.612Z
Stopped at: Completed 06-03-PLAN.md
Resume file: None
