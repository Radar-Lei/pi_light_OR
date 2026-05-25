---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: Explicit Finite-Storage Primal-Dual Separation
status: executing
stopped_at: Phase 12.1 context gathered
last_updated: "2026-05-25T03:45:23.870Z"
last_activity: 2026-05-25
progress:
  total_phases: 1
  completed_phases: 0
  total_plans: 5
  completed_plans: 1
  percent: 0
---

# Project State

## Project Reference

See: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md (updated 2026-05-24)

**Core value:** Show that finite-storage primal-dual pressure control strictly generalizes max-pressure: it reduces to pressure when constraints are slack, adds scarcity-aware shadow-price corrections when storage, spillback, switching, service, or incident constraints bind, and can be deployed or compressed into auditable symbolic traffic-signal policies.
**Current focus:** Phase 12.1 — close-v1-1-gap-execute-or-downgrade-gate-c-long-horizon-evid

## Current Position

Phase: 12.1 (close-v1-1-gap-execute-or-downgrade-gate-c-long-horizon-evid) — EXECUTING
Plan: 2 of 5
Status: Ready to execute
Last activity: 2026-05-25

Progress: [██░░░░░░░░] 20%

## Performance Metrics

**Velocity:**

- Total plans completed: 20 from v1.0
- v1.1 plans completed: 6
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
| 6. Claim Discipline and Explicit State Foundation | 3/3 | Complete |
| 7. Theory and Separation Package | 1/1 | Complete |
| 8. Live Finite-Storage Primal-Dual Controller | 1/1 | Complete |
| 9. Slack and Binding Kill Gates | 1/1 | Complete |
| 10. Strong Baselines and Stress Scenario Suite | 1/1 | Complete |
| 11. Long-Horizon Paired-Seed Evidence | 3/3 | Complete |
| 12. Reproducibility and Future Claim Inputs | 0/TBD | Not started |
| Phase 06 P01 | 9min 11s | 3 tasks | 5 files |
| Phase 06 P02 | 14min 31s | 3 tasks | 6 files |
| Phase 06 P03 | 10min 37s | 3 tasks | 10 files |
| Phase 07 P01 | completed | 3 tasks | 12 files |
| Phase 08 P01 | completed | 3 tasks | 5 files |
| Phase 09 P01 | completed | 3 tasks | 8 files |
| Phase 10 P01 | completed | 3 tasks | 8 files |
| Phase 12.1 P01 | 8min 5s | 3 tasks | 11 files |

## Accumulated Context

### Roadmap Evolution

- Phase 12.1 inserted after Phase 12: Close v1.1 gap: execute or downgrade Gate C long-horizon evidence (URGENT)

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
- [Phase 07]: Use deterministic stdlib analytic checker for theory separation; LP dual extraction remains optional future hardening.
- [Phase 07]: Minimal storage/spillback two-phase example is the canonical THRY-02/THRY-03 static separation artifact; incident/switching examples are deferred unless later phases need them.
- [Phase 07]: Constrained LP oracle regret is the only additional guarantee candidate and remains finite-sample/oracle-relative, not closed-loop evidence.
- [Phase 08]: Use `finite_storage_primal_dual` as the safe live successor and keep old `full_dual_symbolic` guarded as not feasible.
- [Phase 08]: Runtime action audit is compact last-decision-per-TLS `action_decomposition`; nested audit is not part of `METRIC_FIELDS` or aggregate scalar metrics.
- [Phase 08]: Controller decomposes scores into pressure, downstream_storage, spillback, switching, service, incident, and total; tests require isolated nonzero correction terms and slack/binding behavior.
- [Phase 09]: Gate A/B are deterministic explicit-state gates only; Gate C paired-seed closed-loop dominance remains deferred to Phase 11.
- [Phase 09]: Gate artifacts fail closed on missing or forged action decomposition components, finite-storage tie sets, pressure comparators, objective totals/components/margins, and out-of-scope claim language.
- [Phase 10]: Strong baseline/stress coverage is smoke/spec capability evidence only; required baselines and stress mechanisms fail closed, while optimized fixed-time remains a documented limitation.
- [Phase ?]: [Phase 12.1]: Phase 11 resume support wraps execute_spec and continues using run_experiment rather than creating a new TraCI loop.
- [Phase ?]: [Phase 12.1]: Progress files fail closed on invalid JSON, spec fingerprint mismatch, outside row keys, and conflicting duplicate completed rows.
- [Phase ?]: [Phase 12.1]: Phase 12 reproduction now advertises --execution-row-limit 2160 plus progress/resume paths instead of unsupported --allow-long-horizon.

### Pending Todos

Discuss and plan Phase 12 reproducibility and future claim inputs.

### Blockers/Concerns

- v1.1 must not reinterpret v1.0 pressure-equivalent evidence as superiority evidence.
- v1.1 must not include manuscript drafting, related-work writing, final paper integration, or submission preparation.
- Phase 11 Gate C tooling is complete and fail-closed; current main artifact remains INCONCLUSIVE until the long-horizon SUMO rows are actually executed.
- Phase 12 must package reproducibility/future claim inputs without drafting paper text or broadening beyond bounded binding-regime claims.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Manuscript | Full paper drafting, related work, final integration, and submission preparation | Deferred to v2 after v1.1 gates determine surviving claims | v1.1 roadmap |
| Benchmarks | RESCO/CityFlow/LibSignal, larger real-world benchmarks, and neural MARL baselines | Deferred to v2 unless v1.1 core result survives | v1.0 close |
| Integration | Phase 3 consumes Phase 2 recovery implementation directly rather than Phase 2 generated JSON/CSV/rule artifacts | Acknowledged as non-blocking tech debt | v1.0 close |
| Baselines | `local_pilight` and old `full_dual_symbolic` are marked `not_feasible` in closed-loop artifacts | Phase 8 added safe `finite_storage_primal_dual`; unsafe paths remain excluded | Phase 8 |

## Session Continuity

Last session: 2026-05-25T03:44:50.237Z
Stopped at: Phase 12.1 context gathered
Resume file: None
