# Phase 11: Long-Horizon Paired-Seed Evidence - Context

**Gathered:** 2026-05-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 11 delivers journal-grade closed-loop evidence for the finite-storage primal-dual controller only in predeclared binding stress regimes. It must run long-horizon paired-seed SUMO experiments, compute paired statistical uncertainty, and implement Gate C for closed-loop dominance against the strongest feasible baselines.

This phase must not draft manuscript text, create future claim templates, regenerate final paper-facing tables/figures, expand into neural/MARL benchmarks, or claim universal dominance. Phase 12 owns reproducibility/future claim inputs; v2 owns paper drafting.

</domain>

<decisions>
## Implementation Decisions

### D-11-01 Evidence Scope and Regime Split
- Run Gate C only on predeclared binding stress regimes from Phase 10: `arterial_downstream_blockage`, `arterial_spillback_stress`, `arterial_incident_capacity_drop`, `arterial_oversaturation`, `arterial_turning_shock`, and `arterial_switching_loss_sensitive`.
- Treat slack/control scenarios such as `single_sanity`, `arterial_main`, and `grid_scalability` as recovery/tie or sanity context only, not dominance evidence.
- Phase 10 smoke rows and short-horizon coverage artifacts are admissible as suite capability evidence only; they must not be reused as paired-seed dominance evidence.

### D-11-02 Experiment Profile
- Add a dedicated Phase 11 experiment profile or runner rather than overloading Phase 10 semantics. Recommended artifact: `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json`.
- Default journal-grade target should be 3600s horizon, 900s warmup, paired seeds, and CPU/SUMO-only execution. If runtime is too high, implement an explicit `pilot`/`main` profile split where `pilot` proves the pipeline and `main` is the predeclared journal-grade command.
- Use paired seed sets shared across all compared controllers for each scenario. Prefer 20 seeds for main evidence where computationally feasible; require the artifact to state the actual seed count and whether the profile is `pilot` or `main`.

### D-11-03 Comparator Set
- Gate C must compare `finite_storage_primal_dual` against the strongest feasible Phase 10 baselines: at minimum `max_pressure`, `capacity_aware_pressure`, and `finite_storage_double_pressure`.
- Include `cycle_pressure` and `actuated_local_pressure` in experiment rows when feasible, but Gate C dominance should be judged against the strongest feasible pressure/storage-aware comparators, not weak operational strawmen.
- Keep `fixed_time` as context/counterexample evidence only unless a tuned fixed-time implementation exists. Do not treat current unoptimized `fixed_time` as a strong comparator for dominance claims.
- Keep `local_pilight` and old `full_dual_symbolic` guarded as `not_feasible` unless prior safety decisions are deliberately changed in a later phase.

### D-11-04 Metrics and Statistical Tests
- Primary metrics for Gate C: `penalized_avg_travel_time`, `total_delay`, `spillback_count`, `blocking_count`, `unfinished_vehicle_count` or objective-derived unfinished penalty, and `switching_count` where switching-loss scenarios are evaluated.
- Use paired per-seed differences between `finite_storage_primal_dual` and each comparator within the same scenario. Lower-is-better metrics must report improvement as comparator minus proposed controller; higher-is-better metrics such as throughput must report proposed minus comparator.
- Statistical reports must include paired confidence intervals, effect sizes, sample size, mean paired difference, and a multiple-comparison adjustment or clearly scoped family-level handling.
- Use paired bootstrap confidence intervals as the default robust method; paired t/Wilcoxon may be included as secondary diagnostics if lightweight.

### D-11-05 Gate C Fail-Closed Rule
- Implement Gate C as a machine-readable fail-closed checker, not as prose. Recommended script: `scripts/run_gate_c_paired_evidence.py` or equivalent helper integrated into a Phase 11 runner.
- Gate C passes only if required binding scenarios are present, paired seeds align across proposed and required comparators, required metrics exist, finite-storage explicit state/stress metadata exists, and the predeclared primary objective shows nonnegative or positive bounded improvement according to the chosen statistical rule.
- Missing rows, unpaired seeds, missing stress metadata, missing finite-storage state/objective components, missing action decomposition for `finite_storage_primal_dual`, or missing strong comparator rows must produce `FAILED` or `INCONCLUSIVE`, never a silent skip.
- Gate C output must distinguish `binding_regime_dominance`, `slack_regime_recovery_or_context`, `inconclusive`, and `not_evidence` sections.

### D-11-06 Claim Discipline
- Allowed Phase 11 language: closed-loop paired-seed evidence in predeclared binding stress regimes, simulator/network/horizon/seed-relative.
- Forbidden Phase 11 language: universal dominance, deployment readiness, final manuscript claim, broad superiority over max-pressure outside binding regimes, or reuse of v1.0/Phase 10 evidence as superiority evidence.
- Outputs should include caveats that Phase 12 still must regenerate final manuscript inputs and claim templates from raw artifacts.

### Claude's Discretion
- Downstream agents may choose exact seed IDs, runner naming, and bootstrap implementation details, provided the artifact records them and the tests verify paired alignment and fail-closed behavior.
- Downstream agents may implement a fast synthetic/unit test layer for statistics and Gate C validation before running any expensive SUMO profile.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and requirements
- `.planning/ROADMAP.md` — Phase 11 scope, success criteria, and out-of-scope boundary.
- `.planning/REQUIREMENTS.md` — Requirements `GATE-03`, `EXP-03`, and `EXP-05` plus claim-discipline constraints.
- `.planning/STATE.md` — Current milestone decisions and blockers, especially no reinterpretation of v1.0/Phase 10 evidence.

### Prior phase contracts
- `.planning/phases/10-strong-baselines-and-stress-scenario-suite/10-CONTEXT.md` — Strong feasible baselines, stress scenario tags, and Phase 10 no-dominance caveat.
- `.planning/phases/09-slack-and-binding-kill-gates/09-CONTEXT.md` — Gate A/B fail-closed pattern and explicit distinction between recovery/separation and Gate C.
- `.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md` — `finite_storage_primal_dual` action-decomposition contract and safety guard for `full_dual_symbolic`.

### Code and artifacts
- `scripts/run_closed_loop_suite.py` — Existing suite builder, Phase 10 stress scenarios, aggregate pattern, and baseline coverage helpers.
- `scripts/run_closed_loop_sumo.py` — Closed-loop SUMO runner, metric fields, finite-storage state/objective components, stress metadata, and action decomposition.
- `scripts/run_slack_binding_gates.py` — Existing fail-closed gate style for Phase 9.
- `tests/test_closed_loop_sumo.py` — Existing synthetic row and suite/gate test patterns.
- `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` — Phase 10 capability artifact; must be treated as smoke/suite evidence, not dominance evidence.

### Codebase maps
- `.planning/codebase/ARCHITECTURE.md` — Script-oriented research pipeline and JSON artifact conventions.
- `.planning/codebase/TESTING.md` — Script-based gate/test pattern and artifact status convention.
- `.planning/codebase/INTEGRATIONS.md` — SUMO/TraCI and SciPy/HiGHS integration constraints.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/run_closed_loop_suite.py::build_suite_spec` can inform Phase 11 spec construction but Phase 11 should use new semantics and artifacts rather than modifying Phase 10 into dominance evidence.
- `scripts/run_closed_loop_suite.py::aggregate_results` and `ci` provide a simple aggregation pattern; Phase 11 needs paired rather than independent aggregate statistics.
- `scripts/run_closed_loop_sumo.py::run_experiment` already emits `finite_storage_state`, `objective_components`, stress metadata, and `action_decomposition` for `finite_storage_primal_dual` rows.
- `scripts/run_closed_loop_sumo.py::METRIC_FIELDS` defines the closed-loop metric schema consumed by existing reports and tests.
- `scripts/run_slack_binding_gates.py` provides the fail-closed gate style to mirror for Gate C.

### Established Patterns
- Research scripts live under `scripts/`, write JSON artifacts under `experiments/dual_sensitivity/`, print compact JSON summaries, and fail nonzero when gates fail.
- Tests are lightweight Python files with direct assertions and synthetic row fixtures rather than a heavy framework configuration.
- Existing artifacts use top-level `status`, explicit `scope`/`claim_framing`, `requirements_covered`, and caveats to prevent overclaiming.
- Nested `objective_components` and `finite_storage_state` remain row-level audit fields; aggregate summaries should not flatten them unless explicitly generating a separate statistics view.

### Integration Points
- Phase 11 can call `run_experiment(...)` directly for every scenario/controller/seed tuple, using `route_metadata = load_route_metadata(...)` from the existing runner.
- Phase 11 should add paired-statistics helpers that group rows by `(scenario_tag, seed, controller)` and fail closed when a proposed/comparator pair is missing.
- Gate C should consume raw Phase 11 rows and produce a separate gate summary inside the Phase 11 artifact or as a companion JSON.
- Tests should cover synthetic pass, missing comparator, unpaired seed, missing stress metadata, missing action decomposition, and forbidden universal-claim text cases.

</code_context>

<specifics>
## Specific Ideas

Auto-selected decisions prioritize a conservative Transportation Science/TR-B evidence standard: paired long-horizon CPU/SUMO evidence, binding-only dominance, strong pressure/storage-aware comparators, bootstrap uncertainty, and fail-closed artifacts.

</specifics>

<deferred>
## Deferred Ideas

- Tuned/optimized fixed-time baseline remains a documented limitation unless a later phase implements it; Phase 11 must not pretend the current `fixed_time` is optimized.
- Neural/RL benchmark expansion remains deferred to v2 unless the v1.1 core result survives.
- Manuscript tables, claim templates, and final reproducibility packaging remain Phase 12/v2 work.

</deferred>

---

*Phase: 11-Long-Horizon Paired-Seed Evidence*
*Context gathered: 2026-05-24*
