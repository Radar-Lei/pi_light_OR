# Phase 11: Long-Horizon Paired-Seed Evidence - Research

**Researched:** 2026-05-24  
**Domain:** SUMO closed-loop experiment orchestration, paired-seed statistical reporting, fail-closed evidence gates  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)
- Tuned/optimized fixed-time baseline remains a documented limitation unless a later phase implements it; Phase 11 must not pretend the current `fixed_time` is optimized.
- Neural/RL benchmark expansion remains deferred to v2 unless the v1.1 core result survives.
- Manuscript tables, claim templates, and final reproducibility packaging remain Phase 12/v2 work.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GATE-03 | Gate C verifies closed-loop dominance only in predeclared binding stress regimes using paired-seed confidence intervals against the strongest feasible baselines. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use a dedicated fail-closed Gate C checker that consumes Phase 11 raw rows, requires Phase 10 binding scenario tags, verifies paired seeds/comparators, evaluates every D-11-04 primary metric through the reusable Gate C family rule, and emits `binding_regime_dominance`, `slack_regime_recovery_or_context`, `inconclusive`, and `not_evidence` sections. [VERIFIED: `11-CONTEXT.md`; VERIFIED: codebase Read; RESOLVED: checker feedback] |
| EXP-03 | Long-horizon closed-loop experiments use 3600–7200s horizons, appropriate warmup, demand multiplier sweeps, and paired seeds where computationally feasible. [VERIFIED: `.planning/REQUIREMENTS.md`] | Extend the existing SUMO runner pattern with a Phase 11 `pilot`/`main` profile, defaulting to executed 3600+ rows and 900 warmup for journal-grade evidence, while recording actual horizon, warmup, seeds, route-demand scaling or insertion-intensity multiplier behavior, and profile in the JSON artifact. Pilot-only artifacts cannot complete the phase. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_closed_loop_sumo.py`; RESOLVED: checker feedback] |
| EXP-05 | Statistical reports include paired bootstrap or paired t/Wilcoxon confidence intervals, effect sizes, and multiple-comparison handling where relevant. [VERIFIED: `.planning/REQUIREMENTS.md`] | Use paired per-seed differences grouped by scenario/comparator/metric, paired bootstrap CIs as primary, optional paired t-test/Wilcoxon diagnostics, and one predeclared `gate_c_primary_metrics_v1` family over all applicable D-11-04 primary scenario/comparator/metric tests. [CITED: SciPy bootstrap docs; CITED: SciPy ttest_rel docs; CITED: SciPy wilcoxon docs; RESOLVED: checker feedback] |
</phase_requirements>

## Summary

Phase 11 should be planned as a new evidence layer on top of the existing SUMO closed-loop runner, not as an edit that reinterprets Phase 10 smoke evidence. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_closed_loop_suite.py`] The current code already has selectable controllers, stress scenario tags, explicit finite-storage state/objective fields, and finite-storage action decomposition rows, so planning should focus on a dedicated long-horizon runner/artifact, true demand multiplier behavior, paired-seed grouping, statistical summaries over all D-11-04 primary metrics, and a fail-closed Gate C checker. [VERIFIED: `scripts/run_closed_loop_sumo.py`; VERIFIED: `scripts/run_closed_loop_suite.py`; RESOLVED: checker feedback]

The primary technical risk is not package/API availability; it is evidence leakage: slack scenarios, short Phase 10 smoke rows, pilot-only Phase 11 artifacts, metadata-only demand sweeps, unpaired seeds, missing strong baselines, omitted D-11-04 primary metrics, or missing explicit finite-storage audit fields could accidentally become dominance evidence. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `.planning/STATE.md`; RESOLVED: checker feedback] Gate C should therefore validate the artifact structure before interpreting any metric, and should emit `FAILED` or `INCONCLUSIVE` whenever required rows or metadata are absent. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_slack_binding_gates.py`]

**Primary recommendation:** Implement `scripts/run_phase11_paired_evidence.py` as the orchestrator plus pure paired-statistics/Gate C helpers, writing `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json`; keep `scripts/run_closed_loop_sumo.py::run_experiment` as the simulation primitive and add the smallest route-demand scaling or insertion-intensity adapter needed for actual demand multiplier sweeps. [VERIFIED: codebase Read; RESOLVED: checker feedback]

## Project Constraints (from CLAUDE.md)

- Frame the work as OR / methodological traffic-network control for TR-B / Transportation Science, not AI-controller benchmarking. [VERIFIED: `CLAUDE.md`]
- Closed-loop SUMO multi-seed experiments against strong pressure-style baselines are mandatory; static one-step evidence is insufficient. [VERIFIED: `CLAUDE.md`]
- The claim is generalized pressure with scarcity-aware corrections, not universal dominance over max-pressure. [VERIFIED: `CLAUDE.md`]
- Experiments should remain CPU-oriented using SUMO/TraCI and SciPy/HiGHS where useful; no GPU pipeline should be required. [VERIFIED: `CLAUDE.md`]
- Scripts must emit auditable JSON/CSV artifacts and downstream tables/figures must trace back to raw outputs. [VERIFIED: `CLAUDE.md`]
- Max-pressure/backpressure and capacity/spillback-aware variants are first-class baselines, not strawmen. [VERIFIED: `CLAUDE.md`]
- New Python code should use lowercase snake_case, a `main() -> None` entry point, 4-space indentation, explicit exceptions for CLI validation, JSON-serializable dictionaries, and `Path` for file paths. [VERIFIED: `CLAUDE.md`]
- Keep OR/SUMO experiments under `scripts/` and outputs under `experiments/dual_sensitivity/`; do not put new OR experiments into `pi_light_code/`. [VERIFIED: `CLAUDE.md`]
- Project skill directories `.claude/skills/` and `.agents/skills/` were not available during this research session. [VERIFIED: environment probe]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Long-horizon experiment orchestration | Research orchestration layer (`scripts/`) | SUMO network/data layer | The script layer owns seed/scenario/controller/demand-multiplier loops and artifact writing, while SUMO executes simulation state transitions. [VERIFIED: `.planning/codebase/ARCHITECTURE.md`; VERIFIED: `scripts/run_closed_loop_suite.py`; RESOLVED: checker feedback] |
| Actual demand multiplier behavior | Research orchestration layer (`scripts/`) | SUMO route/config layer | Phase 11 must alter route demand or insertion intensity before simulation and record the generated/scaled route source for each row; metadata-only sweeps do not satisfy EXP-03. [VERIFIED: `.planning/REQUIREMENTS.md`; RESOLVED: checker feedback] |
| Controller execution | Control layer (`scripts/run_closed_loop_sumo.py`) | SUMO/TraCI runtime | Existing `run_experiment` selects controller actions through registered controller helpers during TraCI simulation steps. [VERIFIED: `scripts/run_closed_loop_sumo.py`] |
| Paired-seed statistics | Research orchestration layer (`scripts/`) | Local JSON artifact storage | Pairing and statistical summaries should consume completed rows grouped by scenario, seed, controller, comparator, demand multiplier, and metric after simulation. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_closed_loop_suite.py`; RESOLVED: checker feedback] |
| Gate C evidence validation | Research orchestration layer (`scripts/`) | Local JSON artifact storage | Gate A/B already use machine-readable fail-closed script artifacts; Gate C should mirror this pattern for closed-loop paired evidence and reuse one exact primary-metric rule. [VERIFIED: `scripts/run_slack_binding_gates.py`; RESOLVED: checker feedback] |
| Claim discipline | Artifact validation / reporting layer | Phase 12 future inputs | Phase 11 may report bounded paired-seed evidence but must not create final manuscript inputs or universal claims. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `.planning/STATE.md`] |

## Standard Stack

### Core
| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python | 3.12.3 available in this session | Phase 11 orchestration, JSON artifacts, pure statistics helpers | Existing project scripts are Python and new OR scripts follow `scripts/*.py` patterns. [VERIFIED: environment probe; VERIFIED: codebase Read] |
| SUMO | 1.26.0 available in this session | Long-horizon microscopic traffic simulation | Existing closed-loop runner starts SUMO through TraCI and uses `sumo -c ... --seed ...`. [VERIFIED: environment probe; VERIFIED: `scripts/run_closed_loop_sumo.py`; CITED: SUMO docs] |
| TraCI / sumolib | 1.26.0 available in this session | Python API for SUMO control and network metadata | Existing `run_experiment` and metadata helpers use TraCI and sumolib-derived network metadata. [VERIFIED: environment probe; VERIFIED: `scripts/run_closed_loop_sumo.py`; VERIFIED: `sample_sumo_states.py` via imports] |
| SciPy stats | 1.17.1 available in this session | Bootstrap/t-test/Wilcoxon paired statistical diagnostics | Official SciPy APIs provide `bootstrap(..., paired=True)`, `ttest_rel`, and `wilcoxon` for paired uncertainty/testing. [VERIFIED: environment probe; CITED: SciPy bootstrap docs; CITED: SciPy ttest_rel docs; CITED: SciPy wilcoxon docs] |
| Python stdlib `statistics`, `json`, `pathlib`, `argparse`, `xml.etree.ElementTree` | bundled with Python | Lightweight summaries, artifact IO, CLI, route XML scaling | Existing project scripts use stdlib-first gate/orchestration patterns; route demand scaling can be implemented without a new package. [VERIFIED: `scripts/run_closed_loop_suite.py`; VERIFIED: `scripts/run_slack_binding_gates.py`; RESOLVED: checker feedback] |

### Supporting
| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| pytest | 9.0.2 available in this session | Fast synthetic/unit validation | Use for Phase 11 helper tests because `tests/test_closed_loop_sumo.py` already contains direct Python test functions and pytest is available. [VERIFIED: environment probe; VERIFIED: `tests/test_closed_loop_sumo.py`] |
| NumPy | 1.26.4 available in this session | Numeric arrays if needed for bootstrap/vectorized metrics | Optional; Phase 11 can remain mostly stdlib + SciPy but NumPy is available. [VERIFIED: environment probe] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SciPy paired bootstrap | Hand-rolled bootstrap with `random` | Do not hand-roll unless SciPy import fails; official SciPy supports paired resampling and returns CI/standard error fields. [CITED: SciPy bootstrap docs] |
| Paired bootstrap primary CI | Paired t-test CI only | Paired t-test is lightweight and has a confidence interval method, but bootstrap is more robust for non-normal seed-level differences. [CITED: SciPy bootstrap docs; CITED: SciPy ttest_rel docs; ASSUMED] |
| Wilcoxon primary gate | Wilcoxon diagnostic only | Wilcoxon is nonparametric for paired differences, but its zero-handling/roundoff caveats make it better as a secondary diagnostic than the primary CI gate. [CITED: SciPy wilcoxon docs; ASSUMED] |
| Metadata-only demand multipliers | True route scaling or insertion-intensity scaling | Metadata-only sweeps are invalid for EXP-03; the implemented path must alter generated route demand or simulation insertion intensity before `run_experiment`. [VERIFIED: `.planning/REQUIREMENTS.md`; RESOLVED: checker feedback] |

**Installation:**

No new package installation should be planned for Phase 11 unless the implementation environment differs from this research environment. [VERIFIED: environment probe] If a clean environment lacks SciPy/TraCI/SUMO, the planner should add environment setup or mark the main profile blocked. [VERIFIED: environment probe]

**Version verification performed:**

```bash
python --version
python - <<'PY'
import scipy, numpy, traci, sumolib
print(scipy.__version__, numpy.__version__, traci.__version__, sumolib.__version__)
PY
sumo --version
netconvert --version
python -m pytest --version
```
[VERIFIED: environment probe]

## Package Legitimacy Audit

No external package installation is recommended for Phase 11, so the Package Legitimacy Gate is not applicable. [VERIFIED: environment probe] The phase should reuse installed `scipy`, `numpy`, `traci`, `sumolib`, and `pytest`; if a future plan adds new packages, it must run the package legitimacy protocol before installation. [VERIFIED: environment probe]

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| N/A | N/A | N/A | N/A | N/A | N/A | No new packages recommended. [VERIFIED: environment probe] |

**Packages removed due to slopcheck [SLOP] verdict:** none — no packages evaluated because no new installation is recommended. [VERIFIED: environment probe]  
**Packages flagged as suspicious [SUS]:** none — no packages evaluated because no packages were evaluated. [VERIFIED: environment probe]

## Architecture Patterns

### System Architecture Diagram

```text
Phase 11 CLI
  |
  | builds predeclared profile: binding scenarios x controllers x paired seeds x demand multipliers
  v
Demand multiplier adapter
  |
  | writes scaled route/config inputs or passes insertion-intensity settings that change actual SUMO demand
  v
Existing SUMO primitive: run_closed_loop_sumo.run_experiment(...)
  |
  | emits raw completed/not_feasible rows with metrics, stress metadata,
  | finite_storage_state, objective_components, action_decomposition, and demand multiplier provenance
  v
Raw Phase 11 rows in JSON artifact
  |
  | group by scenario_tag + seed + demand_multiplier + proposed/comparator + metric
  v
Paired statistics engine
  |-- if rows/metadata/seeds/actual multiplier behavior missing --> FAILED or INCONCLUSIVE
  |-- if slack/control scenario --> slack_regime_recovery_or_context only
  |-- if binding scenario + required comparator + paired seeds + all applicable D-11-04 metrics --> paired CI/effect size
  v
Reusable Gate C primary-metric family rule
  |
  | binding_regime_dominance / slack_regime_recovery_or_context /
  | inconclusive / not_evidence + caveats
  v
experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json
```
[VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_closed_loop_sumo.py`; VERIFIED: `scripts/run_slack_binding_gates.py`; RESOLVED: checker feedback]

### Recommended Project Structure

```text
scripts/
├── run_phase11_paired_evidence.py      # Phase 11 runner, demand scaling, paired statistics, Gate C helpers
├── run_gate_c_paired_evidence.py       # Standalone strict Gate C checker
└── run_closed_loop_sumo.py             # Existing simulation primitive; reuse, do not duplicate
experiments/dual_sensitivity/
├── phase11_long_horizon_paired_seed_evidence.json
├── phase11_gate_c_paired_evidence.json
└── phase11_scaled_routes/              # Optional generated route/config inputs for demand multipliers

tests/
├── test_phase11_paired_evidence.py     # synthetic paired stats, demand scaling, and fail-closed Gate C tests
└── test_closed_loop_sumo.py            # existing closed-loop and Phase 10 tests
```
[VERIFIED: codebase Read; RESOLVED: checker feedback]

### Pattern 1: Dedicated Phase Runner over Existing `run_experiment`

**What:** Build a Phase 11 spec of `(scenario_tag, network, controller, seed, steps, warmup, action_interval, demand_multiplier, profile)` tuples, then call `run_experiment(...)` for each tuple. [VERIFIED: `scripts/run_closed_loop_suite.py`; VERIFIED: `scripts/run_closed_loop_sumo.py`; RESOLVED: checker feedback]  
**When to use:** Always use this for Phase 11; do not mutate Phase 10 smoke semantics into dominance evidence. [VERIFIED: `11-CONTEXT.md`]

**Planning implications:**
- The planner should create Wave 1 pure helper/tests before any long SUMO run. [VERIFIED: `11-CONTEXT.md`]
- The runner should have `--profile pilot|main`, `--steps`, `--warmup`, `--seeds`, `--demand-multipliers`, `--out`, and `--route-json` arguments. [VERIFIED: project conventions; VERIFIED: `scripts/run_closed_loop_suite.py`; RESOLVED: checker feedback]
- `pilot` can use fewer seeds/shorter horizons to validate plumbing, but phase completion requires a main-profile artifact with executed 3600s+ rows or an explicit `FAILED`/`INCONCLUSIVE` main artifact; pilot-only cannot complete Phase 11. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]

### Pattern 2: Paired Difference as the Atomic Statistical Unit

**What:** For each `(scenario_tag, comparator, metric, seed, demand_multiplier)`, compute one difference between comparator and `finite_storage_primal_dual`, using direction-aware sign rules. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]  
**When to use:** Use for every Gate C primary metric and comparator; aggregate independent controller means are insufficient for EXP-05. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `.planning/REQUIREMENTS.md`]

**Metric direction:**
- Lower-is-better metrics such as `penalized_avg_travel_time`, `total_delay`, `spillback_count`, `blocking_count`, `unfinished_vehicle_count`, and `switching_count` should use `comparator - proposed`, so positive means proposed is better. [VERIFIED: `11-CONTEXT.md`]
- Higher-is-better metrics such as `throughput` should use `proposed - comparator`, so positive means proposed is better. [VERIFIED: `11-CONTEXT.md`]

### Pattern 3: Fail-Closed Gate C Before Interpretation

**What:** Validate required scenarios, comparators, seeds, actual demand multiplier behavior, metrics, stress metadata, finite-storage state/objective components, and action decomposition before reporting dominance. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]  
**When to use:** Always run before treating any paired CI as evidence. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_slack_binding_gates.py`]

**Required checks:**
- Required binding scenario tags are present. [VERIFIED: `11-CONTEXT.md`]
- Required comparator rows exist for `max_pressure`, `capacity_aware_pressure`, and `finite_storage_double_pressure`. [VERIFIED: `11-CONTEXT.md`]
- Paired seeds align between proposed and comparator rows for each scenario and demand multiplier. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]
- Demand multiplier values alter actual SUMO demand by route scaling or insertion-intensity changes and row/artifact metadata records the generated demand source; metadata-only values are invalid. [VERIFIED: `.planning/REQUIREMENTS.md`; RESOLVED: checker feedback]
- Required D-11-04 primary metrics exist and are numeric: the base primary family is `penalized_avg_travel_time`, `total_delay`, `spillback_count`, `blocking_count`, and `unfinished_vehicle_count`; `switching_count` is additionally required for `arterial_switching_loss_sensitive` and any scenario row with switching-loss metadata. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]
- `finite_storage_primal_dual` completed rows include nonempty `action_decomposition`. [VERIFIED: `scripts/run_closed_loop_sumo.py`; VERIFIED: `tests/test_closed_loop_sumo.py`]
- Rows include `finite_storage_state`, `objective_components`, and stress metadata for binding scenarios. [VERIFIED: `scripts/run_closed_loop_sumo.py`; VERIFIED: `scripts/run_closed_loop_suite.py`]

### Pattern 4: Reusable Gate C Primary-Metric Family Rule

**What:** Use one exported rule in `scripts/run_phase11_paired_evidence.py` that both the runner payload and standalone checker consume. [RESOLVED: checker feedback]

**Predeclared constants:**
- `GATE_C_PRIMARY_METRICS = ("penalized_avg_travel_time", "total_delay", "spillback_count", "blocking_count", "unfinished_vehicle_count")`.
- `GATE_C_CONDITIONAL_PRIMARY_METRICS = {"arterial_switching_loss_sensitive": ("switching_count",)}` plus any row marked with switching-loss metadata.
- `GATE_C_STATISTICAL_FAMILY = "gate_c_primary_metrics_v1"` over all applicable scenario/comparator/demand_multiplier/metric tests.

**Status rule:**
- `FAILED` before statistics if any required scenario/comparator/seed/actual-demand-multiplier/metric/audit-field precondition is missing.
- Per metric, compute direction-aware paired differences and paired bootstrap 95% CI. `ci_low >= 0` is a non-worsening pass for that metric; `ci_high < 0` is a statistically bounded harm fail; otherwise the metric is `INCONCLUSIVE`.
- Apply Holm-Bonferroni metadata to one-sided improvement p-values or paired-test diagnostics over `gate_c_primary_metrics_v1`. The family metadata is required even when the CI rule is the primary decision rule.
- Overall `PASSED` only if every applicable primary metric for every required binding scenario/comparator/demand multiplier is non-worsening (`ci_low >= 0`) and each scenario/comparator/demand-multiplier family has at least one strict positive signal (`ci_low > 0` or Holm-adjusted improvement diagnostic passes). Overall `FAILED` if any required precondition is missing or any applicable primary metric has `ci_high < 0`. Otherwise output `INCONCLUSIVE` with metric-level reasons. [RESOLVED: checker feedback]

### Anti-Patterns to Avoid

- **Reusing Phase 10 smoke rows as dominance evidence:** Phase 10 artifact status is `SMOKE_ONLY`, has 99 rows in the current artifact, and is scoped as capability evidence, not paired-seed dominance evidence. [VERIFIED: environment probe; VERIFIED: `experiments/dual_sensitivity/phase10_baselines_stress_suite.json`]
- **Letting pilot artifacts complete Phase 11:** `pilot` or `dry_run` artifacts validate plumbing only. Phase 11 completion requires a main-profile artifact with executed 3600s+ rows or a machine-readable main `FAILED`/`INCONCLUSIVE` result. [RESOLVED: checker feedback]
- **Metadata-only demand sweeps:** `demand_multiplier` values must change route demand or insertion intensity; recording a number without changing SUMO demand does not satisfy EXP-03. [RESOLVED: checker feedback]
- **Aggregating unpaired controller means:** Independent means discard seed-level pairing and do not satisfy the Phase 11 paired-seed requirement. [VERIFIED: `11-CONTEXT.md`; ASSUMED]
- **Treating slack/control scenarios as wins:** `single_sanity`, `arterial_main`, and `grid_scalability` are context/recovery rows only. [VERIFIED: `11-CONTEXT.md`]
- **Judging dominance against weak strawmen:** Gate C must judge against pressure/storage-aware comparators, not current unoptimized `fixed_time`. [VERIFIED: `11-CONTEXT.md`]
- **Reducing D-11-04 to one metric:** `penalized_avg_travel_time` alone is insufficient; all applicable D-11-04 primary metrics must be included in Gate C statistics and pass rules. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]
- **Silently skipping missing data:** Missing rows, unpaired seeds, or missing metadata must produce `FAILED` or `INCONCLUSIVE`. [VERIFIED: `11-CONTEXT.md`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SUMO execution loop | A second TraCI loop for Phase 11 | `run_closed_loop_sumo.run_experiment` | Existing primitive already emits metric fields, explicit state, objective components, stress metadata, and action decomposition. [VERIFIED: `scripts/run_closed_loop_sumo.py`] |
| Stress scenario list | New ad hoc scenario names | Phase 10 scenario tags from `SCENARIOS` / `STRESS_SCENARIO_CATEGORIES` | Gate C scope is locked to Phase 10 binding stress regimes. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_closed_loop_suite.py`] |
| Demand sweep metadata only | A field that never changes SUMO demand | Route demand scaling or insertion-intensity scaling before `run_experiment` | EXP-03 requires real demand multiplier sweeps, not metadata-only artifacts. [VERIFIED: `.planning/REQUIREMENTS.md`; RESOLVED: checker feedback] |
| Paired bootstrap algorithm | Custom index resampler as default | `scipy.stats.bootstrap(..., paired=True)` | Official SciPy paired bootstrap preserves observation pairing via shared resampled indices and returns CI/SE fields. [CITED: SciPy bootstrap docs] |
| Paired t-test | Manual t statistic and CI | `scipy.stats.ttest_rel(...).confidence_interval(...)` | Official SciPy paired t-test requires matching shapes and provides result CI fields. [CITED: SciPy ttest_rel docs] |
| Wilcoxon diagnostic | Custom signed-rank implementation | `scipy.stats.wilcoxon` | Official SciPy implements paired signed-rank testing and documents zero-handling choices. [CITED: SciPy wilcoxon docs] |
| Gate semantics | Prose-only checklist or per-consumer duplicated rules | JSON artifact with `PASSED` / `FAILED` / `INCONCLUSIVE` generated from one shared helper | Existing gate scripts write machine-readable artifacts and exit nonzero for failed gates; one helper prevents Plan 03 from drifting from Plan 01. [VERIFIED: `scripts/run_slack_binding_gates.py`; VERIFIED: `.planning/codebase/TESTING.md`; RESOLVED: checker feedback] |

**Key insight:** Phase 11’s difficulty is evidence governance rather than algorithmic novelty; reuse existing simulation and official statistics primitives, and spend implementation effort on real demand multiplier behavior, pairing, metadata validation, primary-metric family handling, and claim boundaries. [VERIFIED: codebase Read; RESOLVED: checker feedback]

## Common Pitfalls

### Pitfall 1: Phase 10 Smoke Evidence Becomes Phase 11 Dominance Evidence
**What goes wrong:** The planner reuses `phase10_baselines_stress_suite.json` rows as Gate C evidence. [VERIFIED: `11-CONTEXT.md`]  
**Why it happens:** Phase 10 already contains stress scenarios and baseline coverage, which can look like enough evidence. [VERIFIED: `scripts/run_closed_loop_suite.py`]  
**How to avoid:** Create a separate Phase 11 artifact and mark Phase 10 input as capability/scope metadata only. [VERIFIED: `11-CONTEXT.md`]  
**Warning signs:** Artifact profile says `smoke` or status says `SMOKE_ONLY`; horizon/warmup are short; seed count is one; no paired statistics exist. [VERIFIED: `experiments/dual_sensitivity/phase10_baselines_stress_suite.json`; VERIFIED: environment probe]

### Pitfall 2: Unpaired Seeds Inflate Evidence
**What goes wrong:** Proposed and comparator rows use different seed sets or missing seeds and still get summarized. [VERIFIED: `11-CONTEXT.md`]  
**Why it happens:** Existing `aggregate_results` groups by controller and scenario, not proposed/comparator seed pairs. [VERIFIED: `scripts/run_closed_loop_suite.py`]  
**How to avoid:** Gate C should form pair keys before computing statistics and fail/inconclusive any comparator with incomplete pairs. [VERIFIED: `11-CONTEXT.md`]  
**Warning signs:** `n_seeds` differs between proposed and comparator, or per-seed row counts differ after grouping. [ASSUMED]

### Pitfall 3: Metric Direction Is Inconsistent
**What goes wrong:** Lower-is-better and higher-is-better metrics are mixed with the same difference sign. [VERIFIED: `11-CONTEXT.md`]  
**Why it happens:** Existing metrics include both cost metrics and throughput. [VERIFIED: `scripts/run_closed_loop_sumo.py`]  
**How to avoid:** Store `direction`, `difference_definition`, and `positive_means` for every metric summary. [VERIFIED: `11-CONTEXT.md`]  
**Warning signs:** A reported improvement has a negative CI on lower-is-better metrics or no direction metadata. [ASSUMED]

### Pitfall 4: Gate C Passes Without Explicit Binding Metadata
**What goes wrong:** A row is counted as binding dominance based only on scenario name or performance metric. [VERIFIED: `11-CONTEXT.md`]  
**Why it happens:** Scenario tags are necessary but not sufficient; Phase 11 requires explicit finite-storage/stress metadata and objective components. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_closed_loop_sumo.py`]  
**How to avoid:** Require `stress_category`, `stress_mechanism` or mechanism-specific fields, `finite_storage_state`, and `objective_components` before any Gate C evidence classification. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_closed_loop_suite.py`]  
**Warning signs:** Binding summary contains rows without `failure_mode_mechanism`, `demand_shift_mechanism`, `stress_mechanism`, or explicit finite-storage fields. [VERIFIED: `scripts/run_closed_loop_sumo.py`; ASSUMED]

### Pitfall 5: Multiple Comparisons Are Omitted or Scoped Incorrectly
**What goes wrong:** Many scenario/comparator/metric CIs are reported as if each were a standalone primary test, or D-11-04 metrics are silently demoted to diagnostics. [VERIFIED: `.planning/REQUIREMENTS.md`; RESOLVED: checker feedback]  
**Why it happens:** Phase 11 has multiple binding scenarios, comparators, demand multipliers, and metrics. [VERIFIED: `11-CONTEXT.md`]  
**How to avoid:** Predeclare `gate_c_primary_metrics_v1`, apply Holm-Bonferroni metadata to improvement diagnostics across all applicable D-11-04 scenario/comparator/demand-multiplier/metric tests, and make every applicable D-11-04 primary metric part of the Gate C status rule. [RESOLVED: checker feedback]

### Pitfall 6: Demand Multipliers Are Metadata Only
**What goes wrong:** The artifact includes `demand_multiplier` fields but the route demand or insertion intensity is unchanged. [RESOLVED: checker feedback]  
**Why it happens:** Existing `run_experiment` supports scenario stress tags but not an explicit `demand_multiplier` argument. [VERIFIED: `scripts/run_closed_loop_sumo.py`]  
**How to avoid:** Add a helper that creates scaled SUMO route/config inputs or modifies insertion intensity before execution; verify multiplier 0.8, 1.0, and 1.2 create distinct route demand totals or insertion settings. [RESOLVED: checker feedback]

## Code Examples

Verified patterns from official and codebase sources:

### Paired Bootstrap Summary Shape
```python
# Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
from scipy import stats

result = stats.bootstrap(
    (paired_differences,),
    lambda x, axis: x.mean(axis=axis),
    paired=True,
    confidence_level=0.95,
    n_resamples=9999,
    method="BCa",
)
ci_low = float(result.confidence_interval.low)
ci_high = float(result.confidence_interval.high)
standard_error = float(result.standard_error)
```
SciPy documents `paired=True`, `confidence_level`, `n_resamples`, `method`, `confidence_interval`, `bootstrap_distribution`, and `standard_error`. [CITED: SciPy docs]

### Paired t-test Diagnostic Shape
```python
# Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html
from scipy import stats

res = stats.ttest_rel(proposed_values, comparator_values, alternative="less")
ci = res.confidence_interval(confidence_level=0.95)
```
`ttest_rel` is for two related samples with matching shapes and returns `statistic`, `pvalue`, `df`, plus a confidence interval method. [CITED: SciPy docs]

### Gate C Pairing Helper Pattern
```python
# Source: project pattern from scripts/run_slack_binding_gates.py and scripts/run_closed_loop_suite.py
pair_key = (scenario_tag, seed, demand_multiplier)
proposed = rows_by_controller["finite_storage_primal_dual"].get(pair_key)
comparator = rows_by_controller[comparator_name].get(pair_key)
if proposed is None or comparator is None:
    return {"status": "INCONCLUSIVE", "reason": "unpaired_seed"}
```
Existing gate code validates first and returns/raises fail-closed instead of silently skipping invalid evidence. [VERIFIED: `scripts/run_slack_binding_gates.py`; RESOLVED: checker feedback]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Independent controller aggregates with simple normal CI | Paired seed-level differences with paired bootstrap CI | Phase 11 requirement scope | The planner must add new paired-statistics helpers rather than reusing `aggregate_results` as the primary evidence summary. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_closed_loop_suite.py`] |
| Phase 10 smoke/stress capability artifact | Phase 11 dedicated long-horizon paired-seed artifact | Phase 11 boundary | Smoke rows remain suite capability evidence only. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `experiments/dual_sensitivity/phase10_baselines_stress_suite.json`] |
| Gate A/B static explicit-state gates | Gate C closed-loop paired evidence gate | Phase 11 after Phase 10 | Gate C must evaluate closed-loop dominance only in binding stress regimes. [VERIFIED: `.planning/ROADMAP.md`; VERIFIED: `11-CONTEXT.md`] |
| Broad performance language | Simulator/network/horizon/seed-relative evidence language | v1.1 claim discipline | Phase 11 outputs must not say universal dominance or deployment readiness. [VERIFIED: `.planning/STATE.md`; VERIFIED: `11-CONTEXT.md`] |
| Metadata-only demand sweep placeholder | Actual SUMO demand scaling or insertion-intensity behavior | Phase 11 revision | EXP-03 demand multiplier sweeps require behavior change, not artifact labels. [RESOLVED: checker feedback] |
| Single-metric Gate C objective | D-11-04 primary-metric family rule | Phase 11 revision | Gate C must evaluate penalized travel time, delay, spillback, blocking, unfinished vehicles, and switching where applicable. [RESOLVED: checker feedback] |

**Deprecated/outdated:**
- Treating `full_dual_symbolic` as a feasible live controller is outdated; Phase 8 kept it guarded as `not_feasible`, while `finite_storage_primal_dual` is the safe live successor. [VERIFIED: `.planning/STATE.md`; VERIFIED: `scripts/run_closed_loop_sumo.py`]
- Treating `fixed_time` as optimized is invalid for Phase 11 unless a tuned fixed-time implementation is added later. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `scripts/run_closed_loop_suite.py`]
- Treating `penalized_avg_travel_time` as the only Gate C primary metric is invalid after the Phase 11 checker revision; it remains one member of the D-11-04 primary family. [RESOLVED: checker feedback]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Bootstrap is more robust than paired t-test for non-normal seed-level traffic metric differences. | Standard Stack / Alternatives | If wrong, the primary CI method may be overly conservative or unnecessarily complex, but SciPy t-test remains available as a diagnostic. |
| A2 | Independent controller means discard useful seed-level pairing and are weaker than paired differences for this design. | Common Pitfalls | If wrong, the paired design still satisfies the locked requirement, but the statistical efficiency rationale is overstated. |
| A3 | Holm-Bonferroni is an acceptable lightweight multiple-comparison diagnostic for Phase 11 improvement diagnostics. | Pattern 4 / Common Pitfalls | If wrong, another family-level handling method can be substituted, but the plan must still predeclare one shared family and not omit D-11-04 primary metrics. |
| A4 | Phase 11’s main difficulty is evidence governance rather than algorithmic novelty. | Don’t Hand-Roll | If wrong, Wave 1 tests should expose gaps in runner/scenario mechanics. |
| A5 | Route XML scaling can be implemented with stdlib XML helpers for the networks used in Phase 11, with insertion-intensity scaling as a fallback if a scenario does not use scalable route flows. | Standard Stack / Demand multiplier resolution | If wrong, Plan 02 must mark the main artifact `FAILED`/`INCONCLUSIVE` with explicit demand multiplier reasons rather than treating metadata-only sweeps as evidence. |

## Open Questions (RESOLVED)

1. **What exact Gate C statistical pass rule should be binding?**
   - Resolution: Gate C uses all applicable D-11-04 primary metrics, not only `penalized_avg_travel_time`. The base required primary metrics are `penalized_avg_travel_time`, `total_delay`, `spillback_count`, `blocking_count`, and `unfinished_vehicle_count`; `switching_count` is additionally required for `arterial_switching_loss_sensitive` and any row/scenario carrying switching-loss metadata. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]
   - Resolution: The shared helper exports `GATE_C_STATISTICAL_FAMILY = "gate_c_primary_metrics_v1"` and one reusable Gate C rule consumed by both `run_phase11_paired_evidence.py` and `run_gate_c_paired_evidence.py`. [RESOLVED: checker feedback]
   - Resolution: Direction-aware paired bootstrap CI is the primary metric decision rule. For each applicable scenario/comparator/demand-multiplier/metric, `ci_low >= 0` is non-worsening, `ci_high < 0` is bounded harm, and CI crossing zero is inconclusive. Overall Gate C `PASSED` requires every applicable metric to be non-worsening and each scenario/comparator/demand-multiplier family to have at least one strict positive signal (`ci_low > 0` or Holm-adjusted improvement diagnostic passes). Overall `FAILED` occurs for missing preconditions or any bounded harm. Otherwise status is `INCONCLUSIVE` with metric-level reasons. [RESOLVED: checker feedback]
   - Resolution: Holm-Bonferroni metadata is recorded over the full `gate_c_primary_metrics_v1` family for improvement diagnostics; family metadata is required even when the CI rule is the primary pass rule. [RESOLVED: checker feedback]

2. **How many seeds are computationally feasible for `main`?**
   - Resolution: The main profile remains the journal-grade profile and must generate/run 3600s+ rows with 900s warmup for the configured paired seed set, or emit a machine-readable `FAILED`/`INCONCLUSIVE` main artifact explaining missing rows/runtime limitations. Pilot-only and dry-run artifacts validate plumbing only and cannot complete Phase 11. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]
   - Resolution: The artifact must state actual seed count, requested/predeclared seed count, profile, steps, warmup, action interval, demand multipliers, and whether rows are executed or dry-run/spec-only. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]
   - Resolution: Use 20 seeds for main where feasible per D-11-02; if runtime forces fewer seeds, the main artifact must still be `main`, executed, and explicit about actual seed count and evidence limitations. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]

3. **Demand multiplier sweeps are required but not yet represented in `run_experiment` arguments.**
   - Resolution: Phase 11 must implement true demand multiplier behavior. Each `demand_multiplier` must alter actual SUMO demand through generated/scaled route demand or scenario insertion intensity before `run_experiment`; metadata-only multiplier fields are invalid. [VERIFIED: `.planning/REQUIREMENTS.md`; RESOLVED: checker feedback]
   - Resolution: The runner must write or reference the generated/scaled demand input for each multiplier and include provenance such as `demand_multiplier`, `demand_scaling_method`, `base_demand_total`, `scaled_demand_total`, and route/config path or insertion-intensity fields in row/artifact metadata. [RESOLVED: checker feedback]
   - Resolution: Synthetic tests must verify distinct multiplier configurations produce distinct route demand totals or insertion-intensity settings, and Gate C must reject rows whose multiplier metadata lacks evidence of actual SUMO demand changes. [RESOLVED: checker feedback]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | Phase 11 runner/tests | ✓ | 3.12.3 | Use project `.venv` if available and preferred by executor. [VERIFIED: environment probe] |
| SUMO `sumo` | Long-horizon simulation | ✓ | 1.26.0 | Blocking if unavailable; no non-SUMO fallback satisfies Phase 11. [VERIFIED: environment probe] |
| SUMO `netconvert` | Network regeneration if needed | ✓ | 1.26.0 | Existing networks may avoid regeneration, but missing `netconvert` blocks network rebuilds. [VERIFIED: environment probe] |
| TraCI | Closed-loop control | ✓ | 1.26.0 | Blocking for SUMO closed-loop runner. [VERIFIED: environment probe] |
| sumolib | Network metadata | ✓ | 1.26.0 | Blocking for existing metadata helpers. [VERIFIED: environment probe; VERIFIED: codebase Read] |
| SciPy | Paired statistics | ✓ | 1.17.1 | Fallback to stdlib bootstrap only if SciPy unavailable, but not recommended. [VERIFIED: environment probe; CITED: SciPy docs] |
| NumPy | Optional numeric helper | ✓ | 1.26.4 | Use lists/stdlib if unnecessary. [VERIFIED: environment probe] |
| pytest | Fast validation | ✓ | 9.0.2 | Existing tests can run as `python tests/test_closed_loop_sumo.py` if pytest is unavailable. [VERIFIED: environment probe; VERIFIED: `tests/test_closed_loop_sumo.py`] |

**Missing dependencies with no fallback:** none detected in this session. [VERIFIED: environment probe]

**Missing dependencies with fallback:** none detected in this session. [VERIFIED: environment probe]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 available; existing tests are also executable as plain Python scripts. [VERIFIED: environment probe; VERIFIED: `tests/test_closed_loop_sumo.py`] |
| Config file | none detected in prior codebase scan; tests live under `tests/`. [VERIFIED: `.planning/codebase/TESTING.md`] |
| Quick run command | `python tests/test_phase11_paired_evidence.py` after adding Phase 11 tests. [ASSUMED] |
| Full suite command | `python tests/test_closed_loop_sumo.py && python tests/test_slack_binding_gates.py && python tests/test_phase11_paired_evidence.py` after adding Phase 11 tests. [VERIFIED: codebase Read; ASSUMED] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| GATE-03 | Gate C fails closed on missing required binding scenarios, strong comparators, paired seeds, actual demand multiplier behavior, stress metadata, finite-storage fields, and action decomposition. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback] | unit/synthetic gate | `python tests/test_phase11_paired_evidence.py` | ❌ Wave 0 |
| GATE-03 | Gate C evaluates all applicable D-11-04 primary metrics through `gate_c_primary_metrics_v1` and does not reduce the primary gate to one metric. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback] | unit/synthetic gate/statistics | `python tests/test_phase11_paired_evidence.py` | ❌ Wave 0 |
| GATE-03 | Gate C separates `binding_regime_dominance`, `slack_regime_recovery_or_context`, `inconclusive`, and `not_evidence`, and rejects pilot-only artifacts as completed evidence. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback] | unit/synthetic artifact | `python tests/test_phase11_paired_evidence.py` | ❌ Wave 0 |
| EXP-03 | Phase 11 runner builds paired seed profile with 3600/900 default main settings and records actual seed count/profile. [VERIFIED: `11-CONTEXT.md`] | unit/spec builder | `python tests/test_phase11_paired_evidence.py` | ❌ Wave 0 |
| EXP-03 | Runner implements demand multiplier behavior by route demand scaling or insertion-intensity changes and verifies distinct multiplier configurations. [VERIFIED: `.planning/REQUIREMENTS.md`; RESOLVED: checker feedback] | unit/spec builder / route scaling | `python tests/test_phase11_paired_evidence.py` | ❌ Wave 0 |
| EXP-03 | Main profile generates executed 3600s+ rows or writes an explicit main `FAILED`/`INCONCLUSIVE` artifact; pilot-only cannot complete the phase. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback] | CLI/artifact validation | `python scripts/run_phase11_paired_evidence.py --profile main --steps 3600 --warmup 900 --out experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` | ❌ Wave 2 |
| EXP-05 | Paired statistics report mean difference, CI, effect size, sample size, metric direction, and multiple-comparison family metadata. [VERIFIED: `.planning/REQUIREMENTS.md`; CITED: SciPy docs] | unit/statistics | `python tests/test_phase11_paired_evidence.py` | ❌ Wave 0 |
| EXP-05 | Paired statistics fail/inconclusive when proposed/comparator seed sets do not align. [VERIFIED: `11-CONTEXT.md`] | unit/statistics | `python tests/test_phase11_paired_evidence.py` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python tests/test_phase11_paired_evidence.py` after Wave 0 creates it. [ASSUMED]
- **Per wave merge:** `python tests/test_closed_loop_sumo.py && python tests/test_slack_binding_gates.py && python tests/test_phase11_paired_evidence.py`. [VERIFIED: codebase Read; ASSUMED]
- **Phase gate:** Run the Phase 11 main artifact plus Gate C checker. Pilot commands may be used during implementation but cannot be the final phase-completion artifact. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]

### Wave 0 Gaps
- [ ] `tests/test_phase11_paired_evidence.py` — covers GATE-03, EXP-03, EXP-05, all D-11-04 primary metrics, demand multiplier behavior, and pilot-only rejection. [ASSUMED; RESOLVED: checker feedback]
- [ ] `scripts/run_phase11_paired_evidence.py` — pure helper functions plus CLI for profile/spec/demand scaling/statistics/Gate C. [ASSUMED; RESOLVED: checker feedback]
- [ ] Synthetic fixture rows for pass, missing comparator, unpaired seed, missing stress metadata, missing action decomposition, missing actual demand scaling, slack-not-evidence, pilot-only artifact, and forbidden claim text. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]

## Security Domain

This is a local research/experiment pipeline with no authentication, web service, database, external secrets, or deployment surface detected. [VERIFIED: `.planning/codebase/INTEGRATIONS.md`] Security enforcement is enabled by default because `.planning/config.json` does not explicitly disable it. [VERIFIED: `.planning/config.json`]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface detected; do not add credentials or tokens. [VERIFIED: `.planning/codebase/INTEGRATIONS.md`] |
| V3 Session Management | no | No session layer detected. [VERIFIED: `.planning/codebase/INTEGRATIONS.md`] |
| V4 Access Control | no | Local filesystem scripts only; avoid introducing network services. [VERIFIED: `.planning/codebase/INTEGRATIONS.md`] |
| V5 Input Validation | yes | Validate CLI args, JSON rows, numeric metrics, scenario tags, comparator names, demand multiplier provenance, and paired seed sets before computation. [VERIFIED: project conventions; VERIFIED: `scripts/run_closed_loop_sumo.py`; RESOLVED: checker feedback] |
| V6 Cryptography | no | No cryptographic operation needed; do not hand-roll crypto. [VERIFIED: `.planning/codebase/INTEGRATIONS.md`] |

### Known Threat Patterns for Local Research Pipeline

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Artifact poisoning / malformed JSON rows | Tampering | Validate required fields and statuses fail-closed before Gate C interpretation. [VERIFIED: `scripts/run_slack_binding_gates.py`] |
| Metadata-only demand multiplier rows | Tampering | Require row/artifact provenance proving actual route demand scaling or insertion-intensity changes. [RESOLVED: checker feedback] |
| Path confusion or accidental overwrite | Tampering | Use explicit `--out` default under `experiments/dual_sensitivity/` and `Path`-based writes. [VERIFIED: project conventions] |
| Overclaiming in generated artifacts | Repudiation / Information integrity | Run claim-language checks and caveats; forbid universal dominance/deployment/manuscript claim wording. [VERIFIED: `11-CONTEXT.md`; VERIFIED: `claim_policy` import in `run_closed_loop_sumo.py`] |
| Pilot-only evidence misread as phase completion | Repudiation / Information integrity | Gate C checker rejects `pilot`, `dry_run`, and sub-3600 artifacts as completed evidence and returns `INCONCLUSIVE` or `FAILED`. [RESOLVED: checker feedback] |
| Unbounded expensive run | Denial of Service | Provide `pilot` profile and explicit seed/horizon counts before `main`; final completion still requires main artifact or explicit failed/inconclusive main result. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback] |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/11-long-horizon-paired-seed-evidence/11-CONTEXT.md` — locked Phase 11 decisions, allowed/disallowed scope, Gate C fail-closed rules. [VERIFIED: Read]
- `.planning/REQUIREMENTS.md` — GATE-03, EXP-03, EXP-05 definitions. [VERIFIED: Read]
- `.planning/STATE.md` — milestone decisions and Phase 11 blockers/concerns. [VERIFIED: Read]
- `.planning/ROADMAP.md` — Phase 11 roadmap scope and success criteria. [VERIFIED: Read]
- `CLAUDE.md` — project constraints, code conventions, architecture and validation patterns. [VERIFIED: Read]
- `scripts/run_closed_loop_sumo.py` — controller registry, metric fields, SUMO run primitive, finite-storage state/objective/action-decomposition row contract. [VERIFIED: Read]
- `scripts/run_closed_loop_suite.py` — Phase 10 baseline/stress scenario coverage, aggregation pattern, smoke/main profile precedent. [VERIFIED: Read]
- `scripts/run_slack_binding_gates.py` — fail-closed gate artifact pattern. [VERIFIED: Read]
- `tests/test_closed_loop_sumo.py` — existing synthetic tests and direct-script test pattern. [VERIFIED: Read]
- `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` — current Phase 10 smoke artifact shape and caveats. [VERIFIED: Read]

### Primary official docs (HIGH confidence)
- [SciPy `scipy.stats.bootstrap`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html) — paired bootstrap API, CI fields, resampling options. [CITED: SciPy docs]
- [SciPy `scipy.stats.ttest_rel`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html) — paired t-test API and confidence interval method. [CITED: SciPy docs]
- [SciPy `scipy.stats.wilcoxon`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html) — Wilcoxon signed-rank API and zero-handling options. [CITED: SciPy docs]
- [SUMO command-line options](https://sumo.dlr.de/docs/sumo.html) — `-c`, `--seed`, `--no-step-log`, and `--duration-log.disable`. [CITED: SUMO docs]

### Secondary (MEDIUM confidence)
- Environment probes run on 2026-05-24 for Python, SciPy, NumPy, TraCI, sumolib, SUMO, netconvert, pytest, and Phase 10 artifact summary. [VERIFIED: environment probe]

### Tertiary (LOW confidence)
- Statistical design preferences not directly mandated by official docs, including bootstrap robustness rationale and Holm-Bonferroni as the likely lightweight adjustment. [ASSUMED]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — current environment and codebase interfaces were probed/read; no new packages recommended. [VERIFIED: environment probe; VERIFIED: codebase Read]
- Architecture: HIGH — Phase 11 can reuse explicit existing runner/gate/artifact patterns, with a small demand-scaling adapter. [VERIFIED: codebase Read; RESOLVED: checker feedback]
- Pitfalls: HIGH for scope/fail-closed pitfalls from CONTEXT; HIGH for resolved checker concerns on all-primary-metric Gate C, pilot-only rejection, and demand multiplier behavior because they are now explicit plan constraints. [VERIFIED: `11-CONTEXT.md`; RESOLVED: checker feedback]

**Research date:** 2026-05-24  
**Valid until:** 2026-06-23 for codebase-local architecture; re-verify environment versions before long main runs. [ASSUMED]
