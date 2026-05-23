---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: completed
stopped_at: Completed Phase 5 verification
last_updated: "2026-05-23T03:02:43Z"
last_activity: 2026-05-23
progress:
  total_phases: 5
  completed_phases: 5
  total_plans: 15
  completed_plans: 16
  percent: 100
---

# Project State

## Project Reference

See: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md (updated 2026-05-22)

**Core value:** Show that network-optimization dual sensitivities provide a generalized max-pressure principle that reduces to pressure when constraints are slack and adds scarcity-aware corrections when storage, supply, or corridor bottleneck constraints bind, and that this principle can be compressed into compact symbolic traffic-signal policies.
**Current focus:** Milestone complete — pressure-equivalent generalized-pressure symbolic recovery artifact hardened for audit.

## Current Position

Phase: 5
Plan: 05-03
Status: Completed
Last activity: 2026-05-23

Progress: [██████████] 100%

Next command: external review / manuscript integration

## Performance Metrics

**Velocity:**

- Total plans completed: 16
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

## Accumulated Context

### Decisions

- [Phase 03]: Keep the locked static route as pressure-equivalent: dual-recovers/ties pressure under sample-relative oracle-regret evidence, not dual superiority.
- [Phase 04]: Treat closed-loop evidence as generalized-pressure symbolic recovery under SUMO, with max-pressure and capacity-aware pressure as first-class baselines.
- [Phase 04]: Mark `local_pilight` and `full_dual_symbolic` as explicit `not_feasible` rather than substituting unsafe queue heuristics.
- [Phase 04]: Require closed-loop evidence gates to include completed vehicles, actuation evidence for non-fixed controllers, real demand insertion, active failure target traffic, and renderer recomputation from raw rows.
- [Phase 05]: Treat `README.md`, `environment.yml`, `scripts/reproduce_blocks.py`, `reproducibility_manifest.json`, `scripts/render_paper_artifacts.py`, `paper_tables.csv`, `paper_figure_data.csv`, and `paper_artifacts_manifest.json` as the repository audit surface.
- [Phase 05]: Paper-facing artifacts must fail closed unless upstream source artifacts report `PASSED`, route decisions agree, closed-loop completion gates pass, expected artifacts parse, and closed-loop metric schema is complete.

### Pending Todos

None for this milestone.

### Blockers/Concerns

None.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Extensions | TR-E/freight pivot, larger real-world networks, neural MARL baselines, and extra optimization side frameworks | Deferred to v2 unless v1 evidence supports expansion | Initialization |
| Experiments | Longer closed-loop horizons and larger real-world networks | Deferred to manuscript/external-review follow-up | Phase 5 |
| Manuscript | Final plotting/styling from generated figure-data CSVs | Deferred until manuscript outline is fixed | Phase 5 |

## Session Continuity

Last session: 2026-05-23T03:02:43Z
Stopped at: Completed milestone verification
Resume file: None
