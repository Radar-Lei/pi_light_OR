---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Explicit Finite-Storage Primal-Dual Separation
status: executing
stopped_at: v1.1 roadmap created and Phase 6 ready to plan
last_updated: "2026-05-23T12:26:35.407Z"
last_activity: 2026-05-23 -- Phase 06 planning complete
progress:
  total_phases: 7
  completed_phases: 0
  total_plans: 3
  completed_plans: 0
  percent: 0
---

# Project State

## Project Reference

See: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md (updated 2026-05-23)

**Core value:** Show that finite-storage primal-dual pressure control strictly generalizes max-pressure: it reduces to pressure when constraints are slack, adds scarcity-aware shadow-price corrections when storage, spillback, switching, service, or incident constraints bind, and can be deployed or compressed into auditable symbolic traffic-signal policies.
**Current focus:** Phase 6 — Claim Discipline and Explicit State Foundation

## Current Position

Phase: 6 of 12 (first phase of v1.1: Claim Discipline and Explicit State Foundation)
Plan: Not planned yet
Status: Ready to execute
Last activity: 2026-05-23 -- Phase 06 planning complete

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**

- Total plans completed: 15 from v1.0
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

## Accumulated Context

### Decisions

- [Phase 03]: Keep the locked static route as pressure-equivalent: dual-recovers/ties pressure under sample-relative oracle-regret evidence, not dual superiority.
- [Phase 04]: Mark `local_pilight` and `full_dual_symbolic` as explicit `not_feasible` rather than substituting unsafe queue heuristics.
- [Phase 05]: Paper-facing artifacts must fail closed unless upstream source artifacts report `PASSED`, route decisions agree, closed-loop completion gates pass, expected artifacts parse, and closed-loop metric schema is complete.
- [v1.1 Roadmap]: Do not start paper drafting in this milestone; build only theory, controller, experiments, gates, reproducibility, and future manuscript inputs.
- [v1.1 Roadmap]: Strong claim remains bounded: recover/tie max-pressure when constraints are slack; claim wins only when finite-storage/spillback/switching/service/incident constraints bind.

### Pending Todos

Plan Phase 6 next with `/gsd:plan-phase 6`.

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

Last session: 2026-05-23
Stopped at: v1.1 roadmap created and Phase 6 ready to plan
Resume file: None
