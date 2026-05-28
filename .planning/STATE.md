---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: Dynamic Finite-Storage Primal-Dual Method Redesign
status: in_progress
stopped_at: v1.5 r46 early batch rejected despite positive core composite means
last_updated: "2026-05-27T00:00:00+08:00"
last_activity: 2026-05-27 — v1.5 r46 occupancy-gated completion-safety veto was implemented, initial 12-row training batch stayed rejected on unfinished safety, and aggregate tradeoff/audit artifacts were refreshed.
progress:
  total_phases: 5
  completed_phases: 5
  total_plans: 45
  completed_plans: 45
  percent: 100
---

# Project State

## Project Reference

See: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md (updated 2026-05-27)

**Core value:** Show that finite-storage primal-dual pressure control strictly generalizes max-pressure: it reduces to pressure when constraints are slack, adds scarcity-aware shadow-price corrections when storage, spillback, switching, service, or incident constraints bind, and can be deployed or compressed into auditable symbolic traffic-signal policies.
**Current focus:** v1.5 dynamic finite-storage primal-dual redesign — occupancy state, stateful shadow prices, diagnostics, and locked protocol

## Current Position

Phase: Phase 19 candidate — v1.5 method redesign
Plan: —
Status: In progress
Last activity: 2026-05-27 — v1.5 r46 initial batch stayed rejected; the new completion-safety veto improved early composite signal but did not clear unfinished safety.

## Performance Metrics

**Velocity:**

- Total plans completed: 30 from v1.0
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
| 12. Reproducibility and Future Claim Inputs | 2/2 | Complete |
| 13. Complete Predeclared Gate C Evidence | 4/4 | Complete |
| 14. v1.4 Failure Diagnostics and Workstream Protocol | 3/3 | Complete |
| 15. Parallel Exploratory Method Workstreams | 4/4 | Complete |
| 16. Candidate Convergence and Protocol Lock | 3/3 | Complete |
| 17. Locked v1.4 Gate C Execution | 4/4 | Complete |
| 18. v1.4 Claim Refresh and Milestone Audit | 3/3 | Complete |
| Phase 06 P01 | 9min 11s | 3 tasks | 5 files |
| Phase 06 P02 | 14min 31s | 3 tasks | 6 files |
| Phase 06 P03 | 10min 37s | 3 tasks | 10 files |
| Phase 07 P01 | completed | 3 tasks | 12 files |
| Phase 08 P01 | completed | 3 tasks | 5 files |
| Phase 09 P01 | completed | 3 tasks | 8 files |
| Phase 10 P01 | completed | 3 tasks | 8 files |
| Phase 12.1 P01 | 8min 5s | 3 tasks | 11 files |
| Phase 12.1 P02 | 14min 56s | 2 tasks | 2 files |
| Phase 12.1 P03 | completed | 3 tasks | 2 files |
| Phase 12.1 P04 | completed | 2 tasks | 5 files |
| Phase 12.1 P05 | completed | 3 tasks | 3 files |

## Quick Tasks Completed

| Date | Quick Task | Status | Summary |
|------|------------|--------|---------|
| 2026-05-26 | `260526-olz` — Tighten `gpt_pro_suggestion_round1.md` baseline-superiority claims | Complete | Rewrote current/future claim boundaries and verified with `scripts/audit_claim_discipline.py` |

## Accumulated Context

### Roadmap Evolution

- Phase 12.1 inserted after Phase 12: Close v1.1 gap: execute or downgrade Gate C long-horizon evidence (URGENT)
- v1.3 started as a narrow evidence-closure milestone: complete the predeclared 2160-row Phase 11 main profile, rerun strict Gate C, and refresh Phase 12 reproducibility/claim-status artifacts without adding features or drafting the paper.

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
- [Phase 12.1]: Plan 02 started the 2160-row main profile with progress/resume, then preserved fail-closed INCONCLUSIVE status after interruption at 57/2160 rows.
- [Phase 12.1]: Partial Phase 11 rows are audit/provenance only; 2103 missing rows prevent Gate C dominance inference.
- [Phase 12.1]: Gate C and Phase 12 package both remain `INCONCLUSIVE`; Phase 12 claim audit is `PASSED`, but Phase 11/Gate C claim inputs remain `claim_allowed=false`.
- [v1.3 Roadmap]: Do not introduce new controllers, scenarios, thresholds, metrics, or manuscript-writing scope before the predeclared Gate C evidence closure is complete.
- [v1.4 Roadmap]: Treat baseline dominance as a hard predeclared Gate C target, not an assumed conclusion.
- [v1.4 Roadmap]: Use parallel method workstreams for exploratory screening, but keep claim-ready evidence separate from exploratory pilot selection.
- [Phase 14]: v1.3 strict Gate C remains `INCONCLUSIVE`; diagnostics are explanatory and not claim-ready evidence.
- [Phase 15]: All v1.4 workstream pilot artifacts are exploratory with `claim_ready=false` and `final_gate_c_import_allowed=false`.
- [Phase 16]: `finite_storage_primal_dual_v1_4_score` is the single locked candidate route for Phase 17; strong baselines remain required comparators.
- [Phase 17]: v1.4 locked execution completed 1440/1440 rows with clean row audit, but strict Gate C remained non-PASSED; closed-loop superiority remains disallowed.
- [v1.5]: The finite-storage state must use vehicle-count occupancy for storage scarcity and receiving capacity; queue remains appropriate for pressure/service urgency.
- [v1.5]: `finite_storage_dynamic_primal_dual_v1_5` is a new controller, not a relabeling of v1.4; keep static v1.4 as an ablation and preserve strong baselines.
- [v1.5]: `v1_5_closed_loop_diagnostics.json` is diagnostic evidence only; it validates storage activation/action separation readiness, not locked holdout performance.
- [v1.5]: `v1_5_locked_protocol.json` locks the composite finite-storage operating cost endpoint and required baselines before any holdout claim.
- [v1.5]: `v1_5_protocol_activation_audit.json` marks the original locked protocol as non-binding in early execution rows; it is superseded by `v1_5_binding_locked_protocol.json`.
- [v1.5]: `v1_5_binding_protocol_activation_audit.json` passes on the revised protocol, confirming storage/cascade/release mechanisms activate in executed v1.5 rows.
- [v1.5]: `v1_5_binding_paired_evidence.json` remains `INCONCLUSIVE` because execution is partial and not claim-ready.
- [v1.5]: `v1_5_binding_early_holdout_risk.json` is `FAILED`: after activation is verified, early locked rows show repeated safety-guard harm against max-pressure, capacity-aware pressure, and finite-storage double pressure.
- [v1.5]: Do not tune on the current binding holdout seeds and reuse the same protocol as confirmatory evidence.
- [v1.5]: `finite_storage_dynamic_primal_dual_v1_5_r2_guarded` is a post-holdout method-revision candidate with capped non-pressure dynamic corrections.
- [v1.5]: `v1_5_r2_training_protocol.json` is training-only, uses seeds disjoint from the current binding holdout seeds, and cannot support a superiority claim by itself.
- [v1.5]: `v1_5_r2_training_selection.json` rejects r2 on training evidence: action separation is about 1.1%, composite ties max-pressure, and unfinished vehicles harm finite-storage double pressure.
- [v1.5]: r3-r5 training candidates improve composite cost in their first fresh training cells, but each is rejected by unfinished-vehicle safety guards.
- [v1.5]: r6 terminal finite-storage-double flush preserves positive composite signal but is rejected after the second fresh training seed triggers unfinished-vehicle safety harm.
- [v1.5]: r7 finite-storage-double score filtering ties finite-storage double but is rejected because action separation falls to about 1.3% and capacity-aware unfinished-vehicle safety still fails.
- [v1.5]: r8-r10 safety-filter variants also fail training selection; r10 keeps positive composite signals on two seeds but still increases unfinished vehicles on the second seed.
- [v1.5]: r11 local completion-risk service preservation activates and keeps action separation above 5%, but is rejected after the second training seed because unfinished vehicles still harm max-pressure, capacity-aware pressure, and finite-storage double pressure.
- [v1.5]: r12 receiver-constrained route-completion proxy activates on every decision, but is rejected on the first training seed because unfinished vehicles still harm strong baselines and action separation falls below 5%.
- [v1.5]: r13 TraCI movement-level route-demand completion restores action separation and improves composite against max-pressure/capacity-aware pressure, but is rejected because unfinished vehicles still harm strong baselines.
- [v1.5]: r14 route-demand with finite-storage-double score veto removes unfinished harm in the first training seed, but is rejected because it becomes too pressure-equivalent and triggers total-delay safety harm.
- [v1.5]: r15 horizon-aware completion restores action separation and yields positive composite signal against max-pressure, capacity-aware pressure, and finite-storage double pressure, but is rejected by unfinished-vehicle safety harm.
- [v1.5]: r16 adds terminal finite-storage-double lock and passes the first training seed, but is rejected on the second seed by capacity-aware unfinished-vehicle safety harm.
- [v1.5]: r17 switches the terminal lock to capacity-aware and is rejected by finite-storage-double unfinished-vehicle safety harm.
- [v1.5]: r18 uses a balanced terminal capacity/double lock and restores action separation, but is rejected in the first training seed by finite-storage-double unfinished-vehicle safety harm and negative composite against finite-storage double pressure.
- [v1.5]: r19 strengthens finite-storage-double anchoring and keeps positive composite means against core baselines through two training seeds, but is rejected by a one-vehicle unfinished safety harm against max-pressure.
- [v1.5]: r20 balances max-pressure and finite-storage double in the terminal lock, but is rejected in the first training seed by unfinished safety harm against both max-pressure and finite-storage double pressure.
- [v1.5]: r21 uses terminal completion-service selection between max-pressure and finite-storage double, but is rejected in the first training seed by unfinished safety harm against both.
- [v1.5]: r22 adds an all-interval completion-safety veto; it activates but is rejected because action separation falls below 5%, composite means turn negative against core baselines, and unfinished safety still fails.
- [v1.5]: r23 filters marginal horizon overrides by baseline dominance; it preserves only a small positive composite signal, but action separation falls below 5% and unfinished safety still fails.
- [v1.5]: r24 delays horizon completion overrides until late-horizon risk; it preserves positive composite means and action separation, but is rejected by one-vehicle max-pressure unfinished safety harm.
- [v1.5]: r25 adds a late max-pressure terminal lock to r24, but is rejected by unfinished safety harm against max-pressure and finite-storage double pressure.
- [v1.5]: r26 changes staged horizon completion to weight exit urgency relative to remaining simulation time, but is rejected in the first training seed by unfinished safety harm against all core strong baselines.
- [v1.5]: r27 adds a late terminal exit-protection guard with direct finishable-route and service scoring, but is rejected in the first training seed by max-pressure unfinished safety harm.
- [v1.5]: r28 adds a max-pressure completion envelope; it clears the first training seed but is rejected on the second by unfinished safety harm against max-pressure, capacity-aware pressure, and finite-storage double pressure.
- [v1.5]: r29 adds an all-core-baseline completion envelope; it is rejected in the first training seed by finite-storage-double unfinished safety harm and negative composite means against max-pressure and finite-storage double pressure.
- [v1.5]: r30 adds a finite-storage-double completion envelope; it is rejected in the first training seed by capacity-aware unfinished safety harm and negative composite means against all core strong baselines.
- [v1.5]: r31 delays the r24 finite-storage-double terminal lock from 0.78 to 0.88; it is rejected in the first training seed by one-vehicle finite-storage-double unfinished safety harm despite positive core composite means.
- [v1.5]: r32 adds a narrow preterminal finite-storage-double guard after 0.82; it clears the first training seed, then is rejected on the second by finite-storage-double unfinished safety harm.
- [v1.5]: r33 moves the finite-storage-double guard earlier to 0.70; it is rejected in the first training seed by max-pressure and capacity-aware unfinished safety harm despite positive core composite means.
- [v1.5]: r34 adds a core-minimax guard across max-pressure, capacity-aware pressure, and finite-storage double scores; it is rejected in the first training seed by max-pressure and finite-storage-double unfinished safety harm, with negative composite mean against max-pressure.
- [v1.5]: r35 adds deadline-oriented route urgency for low-slack finishable vehicles; it is rejected in the first training seed with 91.8% action separation, 1209 unfinished vehicles, and negative composite means against all core baselines.
- [v1.5]: r36 delays deadline urgency to 0.78 and raises the base weight; it clears the first training seed with 17.7% action separation and positive core composite means, then is rejected on the second by unfinished safety harm against all core baselines.
- [v1.5]: r37 adds a late-gated completion-service anchor; it is rejected in the first training seed with 8.96% action separation, negative composite means against max-pressure and capacity-aware pressure, and capacity-aware unfinished safety harm.
- [v1.5]: r38 adds a narrow late capacity-aware rescue guard; it is rejected in the first training seed with 17.7% action separation, one guard activation, negative composite mean against capacity-aware pressure, and capacity-aware unfinished safety harm.
- [v1.5]: r39 adds a strict late capacity-aware score envelope; it is rejected in the first training seed with positive core composite means, 1.4% action separation, and unfinished safety harm against max-pressure and capacity-aware pressure.
- [v1.5]: r40 adds a pressure-safe horizon override guard; it is rejected in the first training seed with positive core composite means, 5.26% action separation, and unfinished safety harm against max-pressure, capacity-aware pressure, and finite-storage double pressure.
- [v1.5]: r41 adds a locked terminal core-completion choice among pressure, capacity-aware, and finite-storage double actions; it is rejected in the first training seed with positive core composite means, 3.48% action separation, and unfinished safety harm against all core baselines.
- [v1.5]: r42 adds a late tail-completion rescue after pressure-safe horizon reverts; it is rejected in the first training seed with 5.41% action separation, two unfinished safety harms, and negative composite means against capacity-aware and finite-storage double pressure.
- [v1.5]: r43 returns to r24 staged horizon with a strict pressure-safe guard and no deadline urgency; it is rejected in the first training seed because unfinished safety passes but action separation falls to 2.07% and composite means are negative against all core baselines.
- [v1.5]: r44 loosens the r43 pressure-safe guard; it is rejected in the first training seed because composite means recover positive, but action separation remains 3.26% and unfinished safety fails against capacity-aware and finite-storage double pressure.
- [v1.5]: r45 preterminal pressure-safe guard plus route-horizon tail-completion rescue was run through the full 324-row training split and remained `REJECTED`; it accumulated 176 safety harms and turned core composite means negative against max-pressure and capacity-aware pressure.
- [v1.5]: r46 adds an occupancy-gated completion-safety veto on top of r45; the first 12-row batch remains `REJECTED`, but early core composite means are positive against max-pressure, capacity-aware pressure, and finite-storage double pressure before one storage-activation seed reintroduces unfinished-vehicle safety harm.
- [v1.5]: `v1_5_completion_safety_contract_audit.json` reports `REVISION_REQUIRED`: 45 candidates are rejected, 43 have unfinished safety blockers, 27 keep positive core composite means, 23 also clear the action-separation floor, and zero pass unfinished-vehicle safety; the audit does not support weakening the safety contract.
- [v1.5]: `v1_5_completion_tradeoff_analysis.json` reports 107 analyzed training cases, 75 unsafe cases, 52 composite-win cases, 24 safe-and-composite-win cases, and 33 core-baseline conflicts between unfinished oracle and composite oracle.
- [v1.5]: `v1_5_revision_candidate_summary.json` reports `NO_CANDIDATE_SELECTED`; the next step is a structurally stronger completion model or completion-safety controller guard on fresh training seeds before any confirmatory holdout.
- [Phase 18]: v1.4 claim refresh preserves `closed_loop_superiority_claim_allowed=false`; milestone audit found no overclaim or protocol drift.

### Pending Todos

- None for v1.3. Phase 13 completed the original Phase 11 main profile, reran strict Gate C, and refreshed Phase 12 reproducibility/claim-status artifacts.

### Blockers/Concerns

- v1.3 must not reinterpret v1.0 pressure-equivalent evidence or partial Phase 11 rows as superiority evidence.
- v1.3 must not include manuscript drafting, related-work writing, final paper integration, or submission preparation.
- Phase 11 main artifact is now complete at 2160/2160 rows and generated status `FAILED`; completeness is resolved, dominance is not.
- Strict Gate C regenerated status is `INCONCLUSIVE` because the input artifact status is `FAILED`, not `PASSED`.
- Phase 12 packaging has been refreshed from raw artifacts and remains conservative: package `INCONCLUSIVE`, claim audit `PASSED`, Phase 11/Gate C claim inputs not claim-ready.
- v1.4 must not convert exploratory workstream wins into final superiority claims without a locked post-selection Gate C.
- v1.4 must preserve strong max-pressure-style baselines as first-class comparators, including capacity-aware pressure and finite-storage double-pressure.
- Phase 17 must consume `experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json` and must not change candidate selection after confirmation begins.
- Phase 18 must keep closed-loop superiority `claim_allowed=false` unless `experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json` is `PASSED`.
- v1.5 current candidate is not claim-ready: mechanism activation is no longer the blocker, but safety-guard harm against strong baselines is.
- v1.5 r2 must be selected or rejected on training-only evidence before any fresh confirmatory holdout is locked.
- v1.5 r2 has been rejected; the next method candidate must not reuse current binding holdout seeds for tuning.
- v1.5 r3-r46 have also been rejected on training-only evidence; no confirmatory protocol should be locked until a candidate passes training selection.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Manuscript | Full paper drafting, related work, final integration, and submission preparation | Deferred to v2 after v1.1 gates determine surviving claims | v1.1 roadmap |
| Benchmarks | RESCO/CityFlow/LibSignal, larger real-world benchmarks, and neural MARL baselines | Deferred to v2 unless v1.1 core result survives | v1.0 close |
| Integration | Phase 3 consumes Phase 2 recovery implementation directly rather than Phase 2 generated JSON/CSV/rule artifacts | Acknowledged as non-blocking tech debt | v1.0 close |
| Baselines | `local_pilight` and old `full_dual_symbolic` are marked `not_feasible` in closed-loop artifacts | Phase 8 added safe `finite_storage_primal_dual`; unsafe paths remain excluded | Phase 8 |

## Session Continuity

Last session: 2026-05-25T04:02:38.292Z
Stopped at: Phase 12.1 context gathered
Resume file: None

## Operator Next Steps

- Start the next milestone with /gsd-new-milestone
