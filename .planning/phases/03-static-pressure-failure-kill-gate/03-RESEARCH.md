# Phase 3: Static Pressure-Failure Kill Gate - Research

**Researched:** 2026-05-23  
**Domain:** static dual-vs-pressure benchmark routing for traffic signal control  
**Confidence:** HIGH for current code/artifacts, MEDIUM for proposed thresholds and regime labels

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Kill-Gate Purpose
- Treat Phase 3 as the decisive empirical routing gate for the paper's dual-vs-pressure claim strength.
- The output must explicitly classify the route as one of: dual-improves-pressure, dual-recovers/ties-pressure, or dual-underperforms/diagnostic.
- Do not allow Phase 2 candidate diagnostics alone to decide the claim; Phase 3 must run its own static benchmark analysis.

### Static Regimes
- Cover slack, downstream storage-binding, supply-binding, corridor-bottleneck, incident/capacity-drop, and demand-shift regimes as far as current generators/scaffolds support.
- If corridor-bottleneck or supply-binding regimes cannot be created from existing explicit primal constraints, record the limitation instead of inventing unsupported corridor/service claims.
- Prefer script-generated or existing sampled state JSON fixtures under `experiments/dual_sensitivity/`.

### Metrics and Outputs
- Each static regime must report dual-vs-pressure disagreement rate, dual win rate, mean oracle regret, worst-case regret, and recovered symbolic rules.
- Outputs must be structured JSON/CSV plus a human-readable route report under `experiments/dual_sensitivity/`.
- Include enough sampled states for stable conclusions, targeting at least 1k states for the main pressure-failure analysis when feasible.
- Record sample counts by regime and flag regimes below target as preliminary rather than overstating evidence.

### Claim Discipline
- Strong dual advantage supports TR-B/Transportation Science mainline only if binding-regime evidence is clear and pressure/capacity-aware baselines are treated fairly.
- Pressure tie routes to generalized-pressure / symbolic recovery framing.
- Dual underperformance routes to diagnostic framing.
- Do not claim closed-loop superiority or deployable traffic-control performance in this phase.

### Integration with Existing Code
- Reuse Phase 2 artifacts and `scripts/run_sparse_recovery.py` outputs where useful.
- Reuse existing sampled-state generation/conversion scripts rather than creating a new simulator stack.
- Keep validation script-based and CPU/SciPy/HiGHS/SUMO oriented.

### Claude's Discretion

Implement a static kill-gate runner/report layer that groups states by regime, runs or consumes equal-complexity recovery/scoring comparisons for dual, pressure, raw-neighbor, and placebo families, computes disagreement/win/regret metrics, and writes a route decision report with evidence thresholds and caveats.

### Deferred Ideas (OUT OF SCOPE)

- Closed-loop SUMO controller experiments and travel-time/throughput performance claims belong to Phase 4.
- Repository-wide reproduction hardening belongs to Phase 5.
- Manuscript final positioning belongs after Phase 3 routing and Phase 4 evidence.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| KILL-01 | Static benchmarks include slack, downstream storage-binding, supply-binding, corridor-bottleneck, incident/capacity-drop, and demand-shift regimes. | Use the current SUMO sampler for slack and new/expanded synthetic state generation for binding, incident/capacity-drop, corridor-bottleneck, and demand-shift labels; record unsupported explicit constraints as limitations. [VERIFIED: `.planning/REQUIREMENTS.md`, `scripts/sample_sumo_states.py`, `scripts/generate_targeted_bottleneck_states.py`] |
| KILL-02 | Each static regime reports dual-vs-pressure disagreement rate, dual win rate, mean oracle regret, worst-case regret, and recovered symbolic rules. | Extend/compose `run_sparse_recovery.py` outputs and add per-regime aggregation over dual and pressure libraries. [VERIFIED: `scripts/run_sparse_recovery.py`, `experiments/dual_sensitivity/block2_sparse_recovery.json`] |
| KILL-03 | Static benchmark contains enough sampled states per regime to support stable conclusions, with target of at least 1k states for main pressure-failure analysis. | Existing artifacts have 10 SUMO sampled states and 16 targeted bottleneck states, so Phase 3 needs a regime sampler target and an explicit `sample_target_met` gate. [VERIFIED: `experiments/dual_sensitivity/arterial_sampled_states.json`, `experiments/dual_sensitivity/targeted_bottleneck_states.json`] |
| KILL-04 | Analysis identifies whether dual recovers pressure, improves pressure in binding regimes, or fails to match pressure. | Route decision should be computed from per-regime dual-vs-pressure disagreement/win/regret metrics, not from Phase 2 diagnostics alone. [VERIFIED: `.planning/ROADMAP.md`, `.planning/phases/03-static-pressure-failure-kill-gate/03-CONTEXT.md`] |
| KILL-05 | Claim routing is documented: strong dual advantage supports mainline; pressure tie routes to generalized pressure; dual underperformance routes to diagnostic framing. | Add a human-readable route report plus machine-readable `route_decision` and `route_rationale` fields. [VERIFIED: `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`] |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- New Python scripts should use lowercase snake_case names, `main() -> None`, and `if __name__ == "__main__":` entry points. [VERIFIED: `/home/samuel/projects/pi_light_OR/CLAUDE.md`]
- New OR scripts should stay under `scripts/` and write auditable outputs under `experiments/dual_sensitivity/`. [VERIFIED: `/home/samuel/projects/pi_light_OR/CLAUDE.md`]
- Script outputs should be structured JSON/CSV artifacts plus compact JSON status printed to stdout. [VERIFIED: `/home/samuel/projects/pi_light_OR/CLAUDE.md`]
- Use Python/SciPy/HiGHS/SUMO CPU-oriented workflows; do not require GPU. [VERIFIED: `/home/samuel/projects/pi_light_OR/CLAUDE.md`]
- Run OR scripts from repository root or set `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts` for imports between scripts. [VERIFIED: `/home/samuel/projects/pi_light_OR/CLAUDE.md`]
- Avoid placing new OR experiments inside `pi_light_code/`; that subtree is the upstream PI-Light/CityFlow code path. [VERIFIED: `/home/samuel/projects/pi_light_OR/CLAUDE.md`]
- No dedicated pytest/unittest configuration is detected; validation is currently script-driven. [VERIFIED: `/home/samuel/projects/pi_light_OR/CLAUDE.md`, codebase probe]

## Summary

Phase 3 should be implemented as a thin static benchmark/report layer over the existing LP summary, SUMO sample conversion, and sparse recovery machinery rather than as a new simulator stack. [VERIFIED: `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`, `scripts/run_sparse_recovery.py`] The current pipeline already computes oracle finite-difference values, dual movement values, pressure scores, per-library recovered rules, realized mean regret, max regret, action agreement, and selected atom metadata. [VERIFIED: `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, `experiments/dual_sensitivity/block2_sparse_recovery.json`]

The main gap is not scoring/recovery capability; it is regime coverage and sample volume. [VERIFIED: `experiments/dual_sensitivity/arterial_sampled_states.json`, `experiments/dual_sensitivity/targeted_bottleneck_states.json`] Existing artifacts contain 10 naturally sampled arterial states and 16 targeted bottleneck states, while KILL-03 targets at least 1k states for the main pressure-failure analysis. [VERIFIED: `experiments/dual_sensitivity/arterial_sampled_states.json`, `experiments/dual_sensitivity/targeted_bottleneck_states.json`, `.planning/REQUIREMENTS.md`] Therefore the planner should add a regime sampler that can expand current fixtures into labeled state regimes and a kill-gate runner that records `sample_target_met=false` when 1k valid examples cannot be reached. [VERIFIED: `.planning/phases/03-static-pressure-failure-kill-gate/03-CONTEXT.md`] [ASSUMED]

**Primary recommendation:** Implement `scripts/run_static_kill_gate.py` to call/reuse `run_sparse_recovery.py` functions over labeled state files, backed by `scripts/generate_static_regime_states.py` for state expansion and `scripts/render_static_kill_gate_report.py` for human-readable routing. [ASSUMED]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Regime state generation | Experiment scripts | SUMO/static artifacts | Synthetic and sampled JSON fixtures are produced by scripts and stored under `experiments/dual_sensitivity/`. [VERIFIED: `scripts/sample_sumo_states.py`, `scripts/generate_targeted_bottleneck_states.py`] |
| Scenario conversion and LP oracle scoring | Optimization core scripts | Experiment runner | `scenario_from_sample()` converts JSON samples to `Scenario`, and `summarize_scenario()` computes finite-difference oracle, dual, and pressure arrays. [VERIFIED: `scripts/run_sumo_sampled_recovery.py`, `scripts/run_dual_sanity.py`] |
| Sparse symbolic recovery | Optimization core scripts | Report layer | `run_sparse_recovery.py` owns atom libraries, normalized tensors, MILP recovery, selected atoms, and rule text. [VERIFIED: `scripts/run_sparse_recovery.py`] |
| Kill-gate metric aggregation | Experiment runner | Report layer | Phase 3 metrics are regime-level aggregations across dual and pressure library results, so a runner should own JSON/CSV metric materialization. [VERIFIED: `.planning/REQUIREMENTS.md`, `experiments/dual_sensitivity/block2_sparse_recovery.json`] [ASSUMED] |
| Route decision | Report layer | Experiment runner | The route is an interpretation of static metrics and caveats, not a solver primitive. [VERIFIED: `.planning/ROADMAP.md`, `.planning/phases/03-static-pressure-failure-kill-gate/03-CONTEXT.md`] |

## Current State Artifacts and Generator Support

| Regime | Existing Support | Evidence | Phase 3 Action |
|--------|------------------|----------|----------------|
| Slack | Natural SUMO sampled arterial states are mostly low occupancy: 10 samples, mean maximum occupancy ≈ 0.075, max ≈ 0.174. [VERIFIED: `experiments/dual_sensitivity/arterial_sampled_states.json`, codebase probe] | `sample_sumo_states.py` supports `--network`, `--steps`, `--sample-every`, `--warmup`, `--seed`, and emits queues/capacities/tls movements. [VERIFIED: `scripts/sample_sumo_states.py`] | Use as `slack` baseline; generate more seeds/longer runs if needed for count, but do not claim binding-regime evidence from this fixture. [ASSUMED] |
| Downstream storage-binding | Targeted bottleneck fixture has 16 synthetic states with max occupancy 0.98–1.0 and note says it stresses downstream scarcity vs pressure. [VERIFIED: `experiments/dual_sensitivity/targeted_bottleneck_states.json`, `scripts/generate_targeted_bottleneck_states.py`] | Generator sets selected downstream links near 0.82, 0.98, or high capacity fractions and constructs conflict cases. [VERIFIED: `scripts/generate_targeted_bottleneck_states.py`] | Reuse and expand this generator with labels per sample and multiple intensity/approach combinations. [ASSUMED] |
| Supply-binding | Current `Scenario` has `service_capacity` and `green_budget`, but sample JSON does not explicitly encode per-movement supply constraints beyond fixed service capacities from conversion. [VERIFIED: `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`] | No current state fixture has explicit `movement_service_capacity` or `supply_binding` labels. [VERIFIED: codebase artifact list and required reads] | Add optional sample fields for per-movement service/supply reductions or mark supply-binding unsupported if not encoded in conversion. [ASSUMED] |
| Corridor-bottleneck | `run_dual_sanity.py` has `arterial_bottleneck_proxy`, and targeted states use arterial topology around C3. [VERIFIED: `scripts/run_dual_sanity.py`, `scripts/generate_targeted_bottleneck_states.py`] | The current LP does not encode a separate corridor capacity constraint; storage/queue pressure is the active mechanism. [VERIFIED: `scripts/run_dual_sanity.py`] | Label only as `corridor_bottleneck_proxy` unless a corridor-level constraint or explicit capacity-drop field is added; avoid unsupported corridor/service claims. [VERIFIED: `.planning/phases/03-static-pressure-failure-kill-gate/03-CONTEXT.md`] |
| Incident/capacity-drop | Existing capacities are stored per edge in every sample, and a generator can lower downstream capacities in JSON. [VERIFIED: `scripts/sample_sumo_states.py`, `experiments/dual_sensitivity/targeted_bottleneck_states.json`] | No required current generator has `incident` or `capacity_drop_factor` CLI flags. [VERIFIED: `scripts/generate_targeted_bottleneck_states.py`, `scripts/sample_sumo_states.py`] | Extend regime generator to copy base topology and reduce selected edge capacities with labels such as `capacity_drop_factor`. [ASSUMED] |
| Demand-shift | Natural SUMO sampler can vary seed and sampling horizon, but current sample schema does not store demand multipliers or route perturbations. [VERIFIED: `scripts/sample_sumo_states.py`, `experiments/dual_sensitivity/arterial_sampled_states.json`] | `Scenario` includes `demand`, but `scenario_from_sample()` sets demand to zeros. [VERIFIED: `scripts/run_sumo_sampled_recovery.py`] | Treat queue-pattern shifts as `demand_shift_proxy` unless adding explicit demand fields and conversion support. [ASSUMED] |

**Key current artifact facts:** `block2_sparse_recovery.json` is PASSED, contains 16 examples, libraries `local_only`, `raw_neighbor`, `all_neighbor`, `random_price`, `dual_sensitivity`, `dual_plus_raw`, `pressure_backpressure`, and `full_symbolic`, and has `gate_multi_atom_program_observed=false`. [VERIFIED: `experiments/dual_sensitivity/block2_sparse_recovery.json`] In the 16-state targeted fixture, both `dual_sensitivity` and `pressure_backpressure` have zero realized regret, so Phase 2 artifacts alone show pressure equivalence on that fixture, not a dual-over-pressure win. [VERIFIED: `experiments/dual_sensitivity/block2_sparse_recovery.json`, `experiments/dual_sensitivity/block2_sparse_recovery.csv`]

## Standard Stack

### Core

| Library/Tool | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| Python | 3.14.4 | Script runtime for generators, runners, and reports. | Existing scripts are Python and host Python is available. [VERIFIED: environment probe, `CLAUDE.md`] |
| NumPy | 2.4.3 | Numeric arrays and feature tensors. | Existing scripts import and use NumPy arrays for scenarios and features. [VERIFIED: environment probe, `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`] |
| SciPy | 1.17.1 | LP/MILP via HiGHS (`linprog`, `milp`). | Current dual sanity and sparse recovery already depend on SciPy optimization. [VERIFIED: environment probe, `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`] |
| SUMO CLI | 1.26.0 | Optional state sampling and network metadata support. | Existing sampler/generator use SUMO/TraCI/sumolib assets. [VERIFIED: environment probe, `scripts/sample_sumo_states.py`, `scripts/generate_targeted_bottleneck_states.py`] |
| TraCI / sumolib | available | SUMO state sampling and network topology parsing. | Existing sampler/generator import these modules. [VERIFIED: environment probe, `scripts/sample_sumo_states.py`, `scripts/generate_targeted_bottleneck_states.py`] |

### Supporting

| Library/Tool | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| Python stdlib `json`, `csv`, `argparse`, `pathlib` | Python 3.14.4 stdlib | Structured artifact IO and CLI flags. | Use for all new Phase 3 scripts to match existing patterns. [VERIFIED: `scripts/run_sparse_recovery.py`, `scripts/sample_sumo_states.py`] |
| Existing `run_sparse_recovery.py` functions | project-local | Load examples, build atom features, solve MILP, render rules. | Import and reuse rather than shelling out when kill-gate aggregation needs per-example details. [VERIFIED: `scripts/run_sparse_recovery.py`] [ASSUMED] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Reusing `run_sparse_recovery.py` | Build a separate static scorer from scratch | Hand-rolling duplicates atom library, normalization, MILP, and rule rendering; reuse is lower risk. [VERIFIED: `scripts/run_sparse_recovery.py`] [ASSUMED] |
| Script-generated JSON fixtures | Closed-loop SUMO experiments | Closed-loop evidence is explicitly deferred to Phase 4. [VERIFIED: `.planning/phases/03-static-pressure-failure-kill-gate/03-CONTEXT.md`] |
| New packages | pandas / pytest / click | No new package is required for JSON/CSV/report generation, and the repository currently has no lockfile or package spec. [VERIFIED: `CLAUDE.md`, codebase probe] |

**Installation:** No new external packages should be installed for Phase 3. [VERIFIED: existing imports and environment probes]  
**Package Legitimacy Audit:** Skipped because this research recommends no new external packages. [VERIFIED: no proposed installs]

## Architecture Patterns

### System Architecture Diagram

```text
Existing/Generated state JSON files
  ├─ arterial_sampled_states.json (slack proxy)
  ├─ targeted_bottleneck_states.json (storage-binding proxy)
  └─ new regime_state_*.json (supply/corridor/incident/demand proxies)
        |
        v
[Regime sampler / labeler]
  - validates sample schema
  - attaches regime labels and sample provenance
  - enforces target counts or marks preliminary
        |
        v
[Static kill-gate runner]
  - converts samples with scenario_from_sample()
  - computes oracle/dual/pressure via summarize_scenario()
  - reuses sparse recovery libraries/budgets
  - aggregates dual vs pressure metrics by regime
        |
        +--> JSON artifact: block3_static_kill_gate.json
        +--> CSV artifact: block3_static_kill_gate.csv
        +--> Rules artifact: block3_static_kill_gate_rules.txt
        |
        v
[Route report generator]
  - applies route thresholds and caveats
  - writes dual-improves-pressure / pressure-equivalent / diagnostic decision
        |
        v
Human-readable report: block3_static_kill_gate_report.md
```

### Recommended Project Structure

```text
scripts/
├── generate_static_regime_states.py      # New: expand/label slack, binding, incident, demand-shift proxy state fixtures. [ASSUMED]
├── run_static_kill_gate.py               # New: main Phase 3 runner; reuses run_sparse_recovery.py and computes KILL-02 metrics. [ASSUMED]
├── render_static_kill_gate_report.py     # New or function module: route report from block3 JSON. [ASSUMED]
├── run_sparse_recovery.py                # Existing: atom library, MILP, JSON/CSV/rule writer. [VERIFIED: codebase]
├── run_sumo_sampled_recovery.py          # Existing: sample-to-Scenario conversion. [VERIFIED: codebase]
└── run_dual_sanity.py                    # Existing: LP oracle, dual, pressure summaries. [VERIFIED: codebase]

experiments/dual_sensitivity/
├── block3_regime_states.json             # New combined labeled state fixture. [ASSUMED]
├── block3_static_kill_gate.json          # New machine-readable gate artifact. [ASSUMED]
├── block3_static_kill_gate.csv           # New per-regime/per-library metrics. [ASSUMED]
├── block3_static_kill_gate_rules.txt     # New recovered symbolic rules. [ASSUMED]
└── block3_static_kill_gate_report.md     # New route decision report. [ASSUMED]
```

### Pattern 1: Reuse `run_sparse_recovery.py` as a library

**What:** Import `load_examples()`, `solve_library()`, `select_library_names()`, `validate_atom_registry()`, `derived_artifact_paths()`, and rule rendering helpers rather than duplicating atom and MILP logic. [VERIFIED: `scripts/run_sparse_recovery.py`]  
**When to use:** Use when computing per-regime recovered rules and regret metrics for the same libraries and budgets required by Phase 2/3. [VERIFIED: `experiments/dual_sensitivity/block2_sparse_recovery.json`]  
**Example:**

```python
# Source: scripts/run_sparse_recovery.py [VERIFIED: codebase]
validate_atom_registry()
examples = load_examples(state_paths, tls=args.tls, max_samples=args.max_samples,
                         max_movements=args.max_movements, epsilon=args.epsilon)
run = solve_library(examples, "pressure_backpressure", ["pressure_backpressure"],
                    budget=1, complexity_penalty=1e-4, neighbor_penalty=0.0,
                    dual_penalty=0.0, placebo_penalty=0.0,
                    max_neighbor_atoms=None, max_dual_atoms=None,
                    max_placebo_atoms=None, objective_mode="oracle_regret",
                    time_limit_sec=args.time_limit_sec, min_weight=0.1,
                    tie_margin=1e-6)
```

### Pattern 2: Regime-first aggregation

**What:** Split samples by `regime` before computing route metrics; do not aggregate slack and binding states into one conclusion. [VERIFIED: `.planning/REQUIREMENTS.md`]  
**When to use:** Always for KILL-01/KILL-02 because Simpson-style aggregation can hide pressure equivalence in slack states and dual differences in binding states. [ASSUMED]  
**Example:**

```python
# Source: Phase 3 design recommendation [ASSUMED]
for regime_name, regime_state_path in regime_state_paths.items():
    runs = run_recovery_for_regime(regime_state_path)
    metrics[regime_name] = compare_dual_and_pressure(runs)
```

### Pattern 3: Route decision from thresholded evidence plus caveats

**What:** Store `route_decision`, `route_confidence`, `route_rationale`, and `route_caveats` in JSON, and mirror them in the report. [VERIFIED: `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`] [ASSUMED]  
**When to use:** After all regimes are processed and sample sufficiency flags are known. [ASSUMED]

### Anti-Patterns to Avoid

- **Using Phase 2 candidate diagnostics as the Phase 3 decision:** CONTEXT explicitly forbids this; Phase 3 must run its own static benchmark. [VERIFIED: `.planning/phases/03-static-pressure-failure-kill-gate/03-CONTEXT.md`]
- **Claiming closed-loop superiority:** Closed-loop SUMO performance belongs to Phase 4. [VERIFIED: `.planning/phases/03-static-pressure-failure-kill-gate/03-CONTEXT.md`]
- **Calling storage-binding evidence `supply-binding` without explicit supply fields:** Current sample conversion fixes service capacities and does not preserve supply regime labels. [VERIFIED: `scripts/run_sumo_sampled_recovery.py`] [ASSUMED]
- **Aggregating all regimes before routing:** Slack states are expected to tie/recover pressure, while binding states are the meaningful pressure-failure test. [VERIFIED: `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`] [ASSUMED]
- **Overstating 16 targeted states as stable evidence:** KILL-03 targets 1k states for the main analysis; existing targeted fixture has only 16. [VERIFIED: `.planning/REQUIREMENTS.md`, `experiments/dual_sensitivity/targeted_bottleneck_states.json`]

## Proposed CLI Flags

### `scripts/generate_static_regime_states.py` [ASSUMED]

| Flag | Type | Default | Purpose |
|------|------|---------|---------|
| `--base-states` | repeatable path | existing arterial and targeted fixtures | Input JSON states to copy/perturb. [ASSUMED] |
| `--net-file` | path | `networks/arterial/arterial.net.xml` | SUMO network metadata source for movements/capacities. [VERIFIED: `scripts/generate_targeted_bottleneck_states.py`] |
| `--tls` | string | `C3` | Target signal used by conversion/recovery. [VERIFIED: existing scripts] |
| `--regimes` | list | all KILL-01 regimes | Regimes to generate/label. [VERIFIED: `.planning/REQUIREMENTS.md`] |
| `--target-per-regime` | int | 200 or configured value | Per-regime sample goal; 5 regimes × 200 gives 1k main target. [ASSUMED] |
| `--seed` | int | deterministic | Reproducible perturbations. [ASSUMED] |
| `--capacity-drop-factors` | floats | e.g. `0.3 0.5 0.7` | Incident/capacity-drop capacity perturbations. [ASSUMED] |
| `--demand-shift-factors` | floats | e.g. `0.5 1.0 1.5` | Queue-pattern/demand proxy perturbations. [ASSUMED] |
| `--out` | path | `experiments/dual_sensitivity/block3_regime_states.json` | Combined labeled state artifact. [ASSUMED] |

### `scripts/run_static_kill_gate.py` [ASSUMED]

| Flag | Type | Default | Purpose |
|------|------|---------|---------|
| `--states` | repeatable path | `block3_regime_states.json` | Labeled state inputs. [ASSUMED] |
| `--tls` | string | `C3` | TLS ID for scenario conversion. [VERIFIED: existing scripts] |
| `--max-samples` | int | `0` | Limit for quick validation; `0` means all, matching `run_sparse_recovery.py`. [VERIFIED: `scripts/run_sparse_recovery.py`] |
| `--max-movements` | int | `12` | Movement cap passed to `scenario_from_sample()`. [VERIFIED: existing scripts] |
| `--epsilon` | float | `1e-3` | Finite-difference epsilon. [VERIFIED: existing scripts] |
| `--budgets` | list[int] | `1 2 3` | Recovery atom budgets. [VERIFIED: `experiments/dual_sensitivity/block2_sparse_recovery.json`] |
| `--libraries` | list[str] | `dual_sensitivity pressure_backpressure all_neighbor random_price full_symbolic` | Required comparison families. [VERIFIED: `scripts/run_sparse_recovery.py`] [ASSUMED] |
| `--min-regime-count` | int | `30` | Below this, mark a regime preliminary. [ASSUMED] |
| `--target-total-states` | int | `1000` | KILL-03 target for main analysis. [VERIFIED: `.planning/REQUIREMENTS.md`] |
| `--dual-win-threshold` | float | `0.55` | Minimum binding-regime dual win rate for strong route. [ASSUMED] |
| `--regret-improvement-threshold` | float | `0.05` | Minimum mean regret reduction vs pressure for strong route. [ASSUMED] |
| `--equivalence-tolerance` | float | `1e-9` | Numeric tolerance for regret ties. [VERIFIED: existing scripts use `1e-9` style comparisons] |
| `--time-limit-sec` | float | `60.0` | MILP solve limit passed to `solve_library()`. [VERIFIED: `scripts/run_sparse_recovery.py`] |
| `--out` | path | `experiments/dual_sensitivity/block3_static_kill_gate.json` | Machine-readable gate artifact. [ASSUMED] |
| `--csv-out` | path | derived `.csv` | Per-regime metrics. [ASSUMED] |
| `--rules-out` | path | derived `_rules.txt` | Human-readable recovered rules. [ASSUMED] |
| `--report-out` | path | derived `_report.md` | Route decision report. [ASSUMED] |

### `scripts/render_static_kill_gate_report.py` [ASSUMED]

| Flag | Type | Default | Purpose |
|------|------|---------|---------|
| `--gate-json` | path | `block3_static_kill_gate.json` | Input machine-readable result. [ASSUMED] |
| `--out` | path | `block3_static_kill_gate_report.md` | Human-readable route report. [ASSUMED] |
| `--fail-on-missing-route` | bool | false | Optional CI-style guard for missing route decision. [ASSUMED] |

## Required JSON/CSV Fields

### Labeled state JSON input

| Field | Required | Meaning |
|-------|----------|---------|
| `network` | yes | Network/source label. Existing artifacts use this field. [VERIFIED: current JSON artifacts] |
| `num_samples` | yes | Sample count. Existing artifacts use this field. [VERIFIED: current JSON artifacts] |
| `samples[]` | yes | State list. Existing scripts read this key. [VERIFIED: `scripts/run_sparse_recovery.py`] |
| `samples[].time` | yes | Sample timestamp or synthetic index. [VERIFIED: current JSON artifacts] |
| `samples[].queues` | yes | Edge queue map. [VERIFIED: current JSON artifacts] |
| `samples[].vehicle_counts` | yes | Edge vehicle counts. [VERIFIED: current JSON artifacts] |
| `samples[].capacities` | yes | Edge storage/capacity estimates. [VERIFIED: current JSON artifacts] |
| `samples[].tls_movements` | yes | TLS to movement list mapping. [VERIFIED: current JSON artifacts] |
| `samples[].regime` | new required | One of `slack`, `storage_binding`, `supply_binding`, `corridor_bottleneck`, `incident_capacity_drop`, `demand_shift`, or explicit proxy labels. [ASSUMED] |
| `samples[].regime_detail` | new required | Human-readable details such as bottleneck edge, capacity drop factor, demand shift factor, or limitation. [ASSUMED] |
| `samples[].generated_by` | new recommended | Script and parameter provenance. [ASSUMED] |
| `samples[].sample_weight` | optional | If generated grids overrepresent a regime, weights can prevent misleading aggregate counts. [ASSUMED] |

### Kill-gate JSON output

| Field | Required | Meaning |
|-------|----------|---------|
| `experiment` | yes | Use `block3_static_pressure_failure_kill_gate`. [ASSUMED] |
| `status` | yes | `PASSED`, `INCONCLUSIVE`, or `FAILED`; `FAILED` only for schema/metric/gate failure, not for diagnostic route. [VERIFIED: current scripts use status fields] [ASSUMED] |
| `input_states` | yes | List of state files consumed. [VERIFIED: `run_sparse_recovery.py` output schema] |
| `tls` | yes | TLS ID. [VERIFIED: current scripts] |
| `target_total_states` | yes | KILL-03 target, default 1000. [VERIFIED: `.planning/REQUIREMENTS.md`] |
| `num_examples_total` | yes | Valid converted examples. [VERIFIED: `run_sparse_recovery.py` has `num_examples`] |
| `sample_target_met` | yes | Whether valid examples reach target. [ASSUMED] |
| `preliminary_regimes` | yes | Regimes below target/min count. [ASSUMED] |
| `regime_metrics[]` | yes | Per-regime KILL-02 metrics. [VERIFIED: KILL-02 requirement] |
| `route_decision` | yes | `dual-improves-pressure`, `pressure-equivalent`, or `diagnostic`. [VERIFIED: CONTEXT route labels] |
| `route_confidence` | yes | `HIGH`, `MEDIUM`, `LOW` based on counts and metric separation. [ASSUMED] |
| `route_rationale` | yes | Short explanation of decision. [VERIFIED: KILL-05 requirement] |
| `route_caveats` | yes | Claim-discipline limitations. [VERIFIED: CONTEXT claim discipline] |
| `runs` | yes | Underlying per-library recovery results or references. [VERIFIED: `run_sparse_recovery.py` output schema] |
| `rules_out`, `csv_out`, `report_out` | yes | Artifact paths. [VERIFIED: Phase 2 pattern] |

### Per-regime metric object / CSV columns

| Field | Required | Formula / Meaning |
|-------|----------|-------------------|
| `regime` | yes | Regime label. [ASSUMED] |
| `num_examples` | yes | Count of valid examples for this regime. [ASSUMED] |
| `sample_target_met` | yes | Whether this regime meets configured count target. [ASSUMED] |
| `dual_library` | yes | Usually `dual_sensitivity`. [VERIFIED: `scripts/run_sparse_recovery.py`] |
| `pressure_library` | yes | Usually `pressure_backpressure`. [VERIFIED: `scripts/run_sparse_recovery.py`] |
| `dual_vs_pressure_disagreement_rate` | yes | Mean of `dual_chosen_movement != pressure_chosen_movement`, with tie-aware handling recommended. [VERIFIED: KILL-02 requirement] [ASSUMED] |
| `dual_win_rate` | yes | Share of examples where `dual_regret < pressure_regret - tol`. [VERIFIED: KILL-02 requirement] [ASSUMED] |
| `pressure_win_rate` | yes | Share where `pressure_regret < dual_regret - tol`. [ASSUMED] |
| `tie_rate` | yes | Share where regrets are equal within tolerance. [ASSUMED] |
| `dual_mean_oracle_regret` | yes | Mean dual regret over examples. [VERIFIED: KILL-02 requirement, `run_sparse_recovery.py`] |
| `pressure_mean_oracle_regret` | yes | Mean pressure regret over examples. [VERIFIED: KILL-02 requirement, `run_sparse_recovery.py`] |
| `mean_oracle_regret_delta_pressure_minus_dual` | yes | Positive means dual improves pressure. [ASSUMED] |
| `dual_worst_case_regret` | yes | Max dual regret. [VERIFIED: KILL-02 requirement, `run_sparse_recovery.py`] |
| `pressure_worst_case_regret` | yes | Max pressure regret. [VERIFIED: KILL-02 requirement, `run_sparse_recovery.py`] |
| `recovered_symbolic_rules` | yes | Rule text or path for dual/pressure/baseline libraries. [VERIFIED: KILL-02 requirement, Phase 2 rules artifact] |
| `selected_atoms_dual`, `selected_atoms_pressure` | yes | Auditable selected atom lists. [VERIFIED: `run_sparse_recovery.py`] |
| `claim_scope` | yes | `static_only`, `preliminary`, or `unsupported_regime`. [VERIFIED: CONTEXT claim discipline] [ASSUMED] |

## KILL-02 Metric Computation

Use per-example results from solved runs for `dual_sensitivity` and `pressure_backpressure`, aligned by `(scenario, source)` or stable sample ID. [VERIFIED: `run_sparse_recovery.py` result fields include `scenario` and `source`] The current result rows include `chosen_movement`, `oracle_best_movement`, `oracle_regret`, and oracle values, which are sufficient for disagreement, win/tie/loss, and regret metrics. [VERIFIED: `scripts/run_sparse_recovery.py`]

Recommended formulas with tolerance `tol = --equivalence-tolerance`: [ASSUMED]

```text
disagreement_i = dual.chosen_movement != pressure.chosen_movement

dual_win_i = dual.oracle_regret < pressure.oracle_regret - tol
pressure_win_i = pressure.oracle_regret < dual.oracle_regret - tol
tie_i = abs(dual.oracle_regret - pressure.oracle_regret) <= tol

dual_vs_pressure_disagreement_rate = mean(disagreement_i)
dual_win_rate = mean(dual_win_i)
mean_oracle_regret_delta_pressure_minus_dual = mean(pressure.oracle_regret - dual.oracle_regret)
worst_case_regret_delta_pressure_minus_dual = max(pressure.oracle_regret) - max(dual.oracle_regret)
```

Tie-aware caveat: if dual and pressure choose different movements but both have zero/equal oracle regret, count that as action disagreement but not a dual win or pressure win. [ASSUMED] This prevents overstating policy-rank differences when oracle values are tied. [ASSUMED]

Recovered symbolic rules should be reported from `rule_text`, `selected_atoms`, `selected_atom_metadata`, `program_complexity`, `neighbor_atom_count`, `dual_atom_count`, `pressure_atom_count`, `realized_mean_regret`, `max_regret`, and `action_agreement`. [VERIFIED: `scripts/run_sparse_recovery.py`, `experiments/dual_sensitivity/block2_sparse_recovery.json`]

## KILL-03 Sample Target Strategy

The main pressure-failure analysis should aim for `target_total_states >= 1000` valid converted examples. [VERIFIED: `.planning/REQUIREMENTS.md`] Existing artifacts are far below that target: `arterial_sampled_states.json` has 10 samples and `targeted_bottleneck_states.json` has 16 samples. [VERIFIED: current artifacts]

Recommended implementation: [ASSUMED]

1. Generate or collect labeled states until total valid examples reach `--target-total-states`. [ASSUMED]
2. Track both raw samples and valid examples after `scenario_from_sample()` filtering. [VERIFIED: `scenario_from_sample()` can return `None`]
3. Emit `sample_target_met`, `valid_examples_by_regime`, `raw_samples_by_regime`, and `preliminary_regimes`. [ASSUMED]
4. If a regime cannot be generated from explicit constraints, emit `regime_status="unsupported_by_current_model"` rather than fabricating evidence. [VERIFIED: CONTEXT static-regime limitation rule]
5. If the 1k target is not feasible within Phase 3 runtime, route confidence must be `LOW` or `MEDIUM` and the report must say evidence is preliminary. [VERIFIED: CONTEXT sample-count caveat] [ASSUMED]

## Route Decision Rules

Use static, sample-relative evidence only. [VERIFIED: CONTEXT claim discipline] Recommended route logic: [ASSUMED]

| Route | Conditions | Report Language |
|-------|------------|-----------------|
| `dual-improves-pressure` | In supported binding regimes, `dual_win_rate` exceeds threshold, `mean_oracle_regret_delta_pressure_minus_dual` is positive beyond tolerance, pressure win rate is near zero, and pressure/capacity-aware baselines are not ignored. [ASSUMED] | “Static binding-regime evidence supports testing a scarcity-aware generalized-pressure claim in Phase 4; no closed-loop superiority is claimed yet.” [VERIFIED: CONTEXT claim discipline] |
| `pressure-equivalent` | Dual and pressure have near-equal mean/worst regret across regimes, or disagreements are mostly tie-equivalent. [ASSUMED] | “Static evidence indicates dual recovers/ties pressure; route to generalized-pressure symbolic recovery framing.” [VERIFIED: ROADMAP gate routing] |
| `diagnostic` | Pressure beats dual, dual is unstable, sample coverage is too weak for a positive route, or required binding regimes are unsupported. [ASSUMED] | “Static evidence is diagnostic/preliminary; Phase 4 should test failure modes and limitations rather than claim dual advantage.” [VERIFIED: ROADMAP gate routing] |

For current Phase 2 artifacts alone, the appropriate preliminary interpretation is pressure-equivalent on the targeted 16-state fixture because `dual_sensitivity` and `pressure_backpressure` both have zero regret and perfect action agreement in the summary, while local/raw/placebo families are worse. [VERIFIED: `experiments/dual_sensitivity/block2_sparse_recovery.json`] This must not be treated as the Phase 3 final route because CONTEXT requires Phase 3 to run its own static benchmark. [VERIFIED: `.planning/phases/03-static-pressure-failure-kill-gate/03-CONTEXT.md`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| LP oracle / dual / pressure calculation | A new LP model in Phase 3 | `summarize_scenario()` from `run_dual_sanity.py` | Existing code already emits finite-difference oracle, dual values, pressure scores, storage duals, and pressure special-case checks. [VERIFIED: `scripts/run_dual_sanity.py`] |
| SUMO sample conversion | A second state-to-scenario adapter | `scenario_from_sample()` from `run_sumo_sampled_recovery.py` | Existing adapter handles movements, queues, capacities, service capacity, green budget, and invalid samples. [VERIFIED: `scripts/run_sumo_sampled_recovery.py`] |
| Atom metadata and sparse rules | A custom rule renderer | `ATOM_REGISTRY`, `LIBRARIES`, `render_rule_text()` from `run_sparse_recovery.py` | Phase 2 already verified atom families, selected atoms, rule text, and schema gates. [VERIFIED: `02-VERIFICATION.md`, `scripts/run_sparse_recovery.py`] |
| CSV/JSON schema patterns | Ad hoc console output | Existing `write_csv()`/payload patterns | Current project convention requires auditable JSON/CSV and compact JSON stdout. [VERIFIED: `CLAUDE.md`, `scripts/run_sparse_recovery.py`] |
| Route report from manual transcription | Manual spreadsheet/report writing | Deterministic report generator from block3 JSON | KILL-05 requires documented routing traceable to raw artifacts. [VERIFIED: `.planning/REQUIREMENTS.md`] [ASSUMED] |

**Key insight:** The difficult part of Phase 3 is fair regime construction and disciplined interpretation, not implementing a new optimizer. [VERIFIED: current scripts and artifacts] [ASSUMED]

## Common Pitfalls

### Pitfall 1: Mistaking pressure equivalence for dual advantage

**What goes wrong:** Dual and pressure both get zero regret, but the report claims dual improves pressure. [VERIFIED: current `block2_sparse_recovery.json` shows this tie]  
**Why it happens:** The current LP often makes dual movement values reduce to pressure scores when constraints are nonbinding or ranking-neutral. [VERIFIED: `run_dual_sanity.py`, `.planning/REQUIREMENTS.md`]  
**How to avoid:** Compare dual directly against `pressure_backpressure` by regime, and use regret deltas rather than local/raw baselines as the main route signal. [ASSUMED]  
**Warning signs:** `dual_mean_oracle_regret == pressure_mean_oracle_regret == 0` or disagreements are tie-equivalent. [VERIFIED: current artifacts]

### Pitfall 2: Regime labels outrun model constraints

**What goes wrong:** A state is labeled supply-binding/corridor-bottleneck even though the current LP only encodes queues, storage capacities, service capacities, and green budget. [VERIFIED: `scripts/run_dual_sanity.py`]  
**Why it happens:** Synthetic queue/capacity perturbations can look like corridor incidents without explicit corridor/service constraints. [ASSUMED]  
**How to avoid:** Use proxy labels (`corridor_bottleneck_proxy`, `demand_shift_proxy`) or add explicit fields/conversion logic; otherwise mark unsupported. [VERIFIED: CONTEXT limitation rule] [ASSUMED]  
**Warning signs:** No JSON fields such as `regime`, `capacity_drop_factor`, `movement_service_capacity`, or `demand_multiplier`. [VERIFIED: current artifacts]

### Pitfall 3: 1k target counted before conversion

**What goes wrong:** The sampler emits 1k raw samples but fewer valid `Scenario` examples after movement filtering. [VERIFIED: `scenario_from_sample()` can return `None`]  
**Why it happens:** Samples can lack candidate movements for the selected TLS or have missing queue/capacity edges. [VERIFIED: `scripts/run_sumo_sampled_recovery.py`]  
**How to avoid:** Gate on valid examples, not raw sample count. [ASSUMED]  
**Warning signs:** `num_samples` differs from `num_examples_total` or some regimes have zero valid examples. [ASSUMED]

### Pitfall 4: Letting `dual_plus_raw` obscure the pure dual-vs-pressure comparison

**What goes wrong:** `dual_plus_raw` selects a non-dual atom and is interpreted as dual performance. [VERIFIED: current `block2_sparse_recovery.json` has `dual_plus_raw` selecting `upstream_queue` for budgets >1 in some summaries]  
**Why it happens:** The library includes multiple atoms and MILP selection can choose any atom that optimizes sample regret under penalties. [VERIFIED: `scripts/run_sparse_recovery.py`]  
**How to avoid:** Treat `dual_sensitivity` vs `pressure_backpressure` as the primary route comparison; use `dual_plus_raw` and `full_symbolic` as secondary recovery diagnostics. [ASSUMED]

### Pitfall 5: Overclaiming static evidence as deployable control performance

**What goes wrong:** The report states travel-time, throughput, or closed-loop control superiority. [VERIFIED: CONTEXT forbids this in Phase 3]  
**Why it happens:** Zero one-step oracle regret can be rhetorically inflated into policy performance. [ASSUMED]  
**How to avoid:** Keep all route language “static”, “sample-relative”, and “pre-closed-loop”. [VERIFIED: CONTEXT claim discipline]

## Code Examples

### Load and split labeled states by regime

```python
# Source: Phase 3 design recommendation [ASSUMED]
def samples_by_regime(payload: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for sample in payload.get("samples", []):
        regime = str(sample.get("regime", "unlabeled"))
        grouped.setdefault(regime, []).append(sample)
    return grouped
```

### Compute dual-vs-pressure metrics from aligned results

```python
# Source: Phase 3 design recommendation [ASSUMED]
def compare_dual_pressure(dual_results: list[dict], pressure_results: list[dict], tol: float) -> dict:
    dual_by_key = {(r["source"], r["scenario"]): r for r in dual_results}
    pressure_by_key = {(r["source"], r["scenario"]): r for r in pressure_results}
    keys = sorted(set(dual_by_key) & set(pressure_by_key))
    dual_wins = pressure_wins = ties = disagreements = 0
    dual_regrets = []
    pressure_regrets = []
    for key in keys:
        d = dual_by_key[key]
        p = pressure_by_key[key]
        d_regret = float(d["oracle_regret"])
        p_regret = float(p["oracle_regret"])
        dual_regrets.append(d_regret)
        pressure_regrets.append(p_regret)
        disagreements += int(d["chosen_movement"] != p["chosen_movement"])
        dual_wins += int(d_regret < p_regret - tol)
        pressure_wins += int(p_regret < d_regret - tol)
        ties += int(abs(d_regret - p_regret) <= tol)
    n = max(len(keys), 1)
    return {
        "num_examples": len(keys),
        "dual_vs_pressure_disagreement_rate": disagreements / n,
        "dual_win_rate": dual_wins / n,
        "pressure_win_rate": pressure_wins / n,
        "tie_rate": ties / n,
        "dual_mean_oracle_regret": sum(dual_regrets) / n,
        "pressure_mean_oracle_regret": sum(pressure_regrets) / n,
        "dual_worst_case_regret": max(dual_regrets, default=0.0),
        "pressure_worst_case_regret": max(pressure_regrets, default=0.0),
    }
```

### Compact JSON status pattern

```python
# Source: scripts/run_sparse_recovery.py and scripts/sample_sumo_states.py [VERIFIED: codebase]
print(json.dumps({"status": payload["status"], "out": str(out_path), "num_examples": len(examples)}, indent=2))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| One-atom/equal-complexity pilots only | K-atom sparse recovery with atom families, budgets, penalties, JSON/CSV/rules outputs | Phase 2 completion on 2026-05-22 | Phase 3 should reuse Phase 2 recovery instead of reimplementing symbolic selection. [VERIFIED: `02-VERIFICATION.md`] |
| Phase 2 candidate diagnostics deciding route | Phase 3 independent static kill-gate benchmark | Phase 3 CONTEXT | Route decision must be generated by new Phase 3 analysis. [VERIFIED: `03-CONTEXT.md`] |
| Natural SUMO sampled states only | Mixture of natural slack samples and targeted synthetic bottleneck states | Existing Block 1/2 artifacts | Phase 3 needs labeled, larger, multi-regime state sets. [VERIFIED: current artifacts] |

**Deprecated/outdated:**
- Treating `gate_dual_budget1_beats_raw` as claim routing is deprecated for Phase 3 because the locked context says Phase 2 diagnostics are non-gating. [VERIFIED: `03-CONTEXT.md`, `block2_sparse_recovery.json`]
- Treating local/raw/placebo baselines as substitutes for `pressure_backpressure` is insufficient because KILL-02 requires dual-vs-pressure comparison. [VERIFIED: `.planning/REQUIREMENTS.md`, `scripts/run_sparse_recovery.py`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Add `generate_static_regime_states.py`, `run_static_kill_gate.py`, and `render_static_kill_gate_report.py` as the implementation split. | Summary / Architecture Patterns | Planner may prefer a smaller two-script design; functionality remains similar. |
| A2 | Use proxy labels for demand-shift/corridor-bottleneck unless explicit fields are added. | Current State Artifacts | If explicit theory artifacts already define these constraints elsewhere, planner may need stronger implementation. |
| A3 | Use threshold defaults such as `dual_win_threshold=0.55`, regret improvement threshold `0.05`, and min-regime count `30`. | CLI / Route Decision | Thresholds are policy choices and should be human-confirmed before locking. |
| A4 | Tie-aware different actions with equal oracle regret should not count as dual/pressure win. | KILL-02 Metric Computation | Different tie semantics could change disagreement interpretation. |
| A5 | New regime sampler can synthesize enough states by perturbing queues/capacities. | KILL-03 Sample Target Strategy | If synthetic perturbations are not accepted, sample target may require longer SUMO sampling or be marked preliminary. |

## Open Questions

1. **Should supply-binding be implemented as explicit per-movement service capacity or marked unsupported?**
   - What we know: `Scenario` has `service_capacity`, but current sample JSON does not carry per-movement supply fields and `scenario_from_sample()` sets service capacity uniformly to 3.0. [VERIFIED: `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`]
   - What's unclear: Whether Phase 1 theory artifacts demand a separate supply constraint beyond current service capacity. [ASSUMED]
   - RESOLVED recommendation: Implement optional `samples[].movement_service_capacity` support only if planner finds a Phase 1 definition; otherwise label supply-binding as `unsupported_by_current_model` or `supply_binding_proxy` with caveat. [ASSUMED]

2. **Can corridor-bottleneck be claimed from queue/capacity perturbations alone?**
   - What we know: Current arterial proxy and targeted generator use topology and storage pressure, not a corridor-level primal constraint. [VERIFIED: `scripts/run_dual_sanity.py`, `scripts/generate_targeted_bottleneck_states.py`]
   - What's unclear: Whether a corridor/service correction term is implemented outside required files. [ASSUMED]
   - RESOLVED recommendation: Use `corridor_bottleneck_proxy` unless adding an explicit corridor capacity field and LP conversion support; do not claim full corridor-binding evidence from existing artifacts. [VERIFIED: CONTEXT limitation rule] [ASSUMED]

3. **What exact route thresholds should be locked?**
   - What we know: Route categories are locked, but numeric thresholds are not specified in CONTEXT or REQUIREMENTS. [VERIFIED: `03-CONTEXT.md`, `.planning/REQUIREMENTS.md`]
   - What's unclear: Reviewer-facing tolerance for “clear” binding-regime evidence. [ASSUMED]
   - RESOLVED recommendation: Use conservative defaults as CLI flags and include them in JSON; treat thresholds as transparent analysis parameters rather than hidden constants. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | All Phase 3 scripts | yes | 3.14.4 | None needed. [VERIFIED: environment probe] |
| NumPy | Scenario arrays/features | yes | 2.4.3 | None needed. [VERIFIED: environment probe] |
| SciPy | LP/MILP HiGHS | yes | 1.17.1 | None needed. [VERIFIED: environment probe] |
| SUMO `sumo` | Optional natural state sampling | yes | 1.26.0 | Use existing JSON fixtures if sampling is not run. [VERIFIED: environment probe] |
| SUMO `netconvert` | Network generation, if needed | yes | 1.26.0 | Use existing `.net.xml` assets. [VERIFIED: environment probe] |
| TraCI | `sample_sumo_states.py` | yes | import available | Skip new SUMO sampling and use static fixtures. [VERIFIED: environment probe] |
| sumolib | topology/capacity metadata | yes | import available | Use existing `tls_movements` in state JSON. [VERIFIED: environment probe] |

**Missing dependencies with no fallback:** None detected. [VERIFIED: environment probe]  
**Missing dependencies with fallback:** None detected. [VERIFIED: environment probe]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Script-based validation; no pytest/unittest config detected. [VERIFIED: codebase probe, `CLAUDE.md`] |
| Config file | none — Wave 0 should not add a framework unless planner wants unit tests. [VERIFIED: codebase probe] [ASSUMED] |
| Quick run command | `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py --states /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/targeted_bottleneck_states.json --tls C3 --max-samples 16 --target-total-states 1000 --out /tmp/block3_static_kill_gate.json --csv-out /tmp/block3_static_kill_gate.csv --rules-out /tmp/block3_static_kill_gate_rules.txt --report-out /tmp/block3_static_kill_gate_report.md` [ASSUMED] |
| Full suite command | `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py --target-per-regime 200 --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_regime_states.json && PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py --states /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_regime_states.json --target-total-states 1000 --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.json --csv-out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.csv --rules-out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_rules.txt --report-out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_report.md` [ASSUMED] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| KILL-01 | Regime artifact contains all requested regime labels or explicit unsupported/proxy statuses. | smoke/schema | Inspect `block3_regime_states.json` and `block3_static_kill_gate.json`. [ASSUMED] | ❌ Wave 0 |
| KILL-02 | Per regime reports disagreement, dual win, mean regret, worst-case regret, and rules. | smoke/schema | Run quick kill-gate command and assert required JSON/CSV fields. [ASSUMED] | ❌ Wave 0 |
| KILL-03 | Target 1k valid states or marks insufficiency/preliminary. | gate/schema | Assert `target_total_states`, `num_examples_total`, and `sample_target_met` exist. [ASSUMED] | ❌ Wave 0 |
| KILL-04 | JSON route decision is one of locked categories and matches metric conditions. | gate/schema | Validate `route_decision in {...}` and route rationale present. [ASSUMED] | ❌ Wave 0 |
| KILL-05 | Human-readable route report documents route and caveats. | artifact check | Assert report file exists and contains route decision plus “static” caveat. [ASSUMED] | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python3 -m py_compile /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py /home/samuel/projects/pi_light_OR/scripts/render_static_kill_gate_report.py` plus quick run on 16 targeted samples. [ASSUMED]
- **Per wave merge:** Full suite command over generated `block3_regime_states.json`. [ASSUMED]
- **Phase gate:** `block3_static_kill_gate.json`, `.csv`, `_rules.txt`, and `_report.md` exist; JSON status is not schema-failed; route decision is present; sample insufficiency is explicitly recorded if target not met. [ASSUMED]

### Wave 0 Gaps

- [ ] `scripts/generate_static_regime_states.py` — creates/labels multi-regime states for KILL-01/KILL-03. [ASSUMED]
- [ ] `scripts/run_static_kill_gate.py` — computes KILL-02 metrics and KILL-04 route. [ASSUMED]
- [ ] `scripts/render_static_kill_gate_report.py` or equivalent function — emits KILL-05 report. [ASSUMED]
- [ ] Schema validation code for required JSON/CSV fields. [ASSUMED]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No authentication surface; local offline scripts only. [VERIFIED: project architecture] |
| V3 Session Management | no | No session state. [VERIFIED: project architecture] |
| V4 Access Control | no | Local file writes only; avoid writing outside configured output paths. [ASSUMED] |
| V5 Input Validation | yes | Validate CLI numeric thresholds, known regime names, library names, and JSON schema before solving. [VERIFIED: `run_sparse_recovery.py` validates CLI/library inputs] |
| V6 Cryptography | no | No cryptographic operations. [VERIFIED: required scripts] |

### Known Threat Patterns for local experiment scripts

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path overwrite outside artifact directory | Tampering | Use explicit output paths, create parent dirs only for user-supplied paths, and do not delete files. [ASSUMED] |
| Malformed JSON causing misleading route | Tampering | Validate required sample fields and fail/inconclusive with schema error. [ASSUMED] |
| Dynamic code execution | Elevation of privilege | Do not execute rendered rule text; keep it audit-only as Phase 2 does. [VERIFIED: `run_sparse_recovery.py` rule text note] |

## Validation Commands and Gate Criteria

### Existing commands useful before Phase 3 implementation

```bash
PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py --out /tmp/block0_dual_sanity.json
PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py --states /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/targeted_bottleneck_states.json --budgets 1 2 3 --out /tmp/block2_sparse_recovery.json --csv-out /tmp/block2_sparse_recovery.csv --rules-out /tmp/block2_sparse_recovery_rules.txt
```

These commands validate that the LP/oracle and sparse recovery substrate still run before adding Phase 3. [VERIFIED: `02-VERIFICATION.md`, `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`]

### Phase 3 gate criteria

| Gate | Criteria |
|------|----------|
| Schema gate | JSON has `regime_metrics`, `route_decision`, `sample_target_met`, `preliminary_regimes`, `csv_out`, `rules_out`, and `report_out`; CSV has required KILL-02 columns. [ASSUMED] |
| Metric gate | Every supported regime reports disagreement rate, dual win rate, mean oracle regret, worst-case regret, and recovered rules. [VERIFIED: KILL-02] |
| Sample gate | `num_examples_total >= 1000` or `sample_target_met=false` plus explicit preliminary caveat. [VERIFIED: KILL-03 and CONTEXT] |
| Route gate | `route_decision` is one of `dual-improves-pressure`, `pressure-equivalent`, or `diagnostic`; report explains why. [VERIFIED: CONTEXT and ROADMAP] |
| Claim discipline gate | Report contains no closed-loop performance claim and states static/sample-relative scope. [VERIFIED: CONTEXT] |

## Avoid Over-Claiming Notes

- Do not describe Phase 3 as proving deployable control superiority; it is a static one-step benchmark gate. [VERIFIED: CONTEXT]
- Do not claim dual improves pressure when pressure has the same oracle regret or tie-equivalent choices. [VERIFIED: current Phase 2 artifact]
- Do not call a generated state `supply-binding` or `corridor-bottleneck` without explicit fields/conversion support; use proxy/unsupported labels. [VERIFIED: CONTEXT limitation rule] [ASSUMED]
- Do not hide sample insufficiency; if total valid examples are below 1k, mark the route preliminary or lower confidence. [VERIFIED: KILL-03 and CONTEXT]
- Do not treat random/permuted dual or raw-neighbor failures as proof of dual advantage over pressure. [VERIFIED: `scripts/run_sparse_recovery.py`, `experiments/dual_sensitivity/block2_sparse_recovery.json`]

## Sources

### Primary (HIGH confidence)

- `/home/samuel/projects/pi_light_OR/.planning/phases/03-static-pressure-failure-kill-gate/03-CONTEXT.md` — locked Phase 3 purpose, regimes, metrics, routing, and claim discipline.
- `/home/samuel/projects/pi_light_OR/.planning/ROADMAP.md` — Phase 3 gate routing and success criteria.
- `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md` — KILL-01 through KILL-05 requirements.
- `/home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-VERIFICATION.md` — verified Phase 2 recovery substrate and artifacts.
- `/home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py` — atom libraries, MILP recovery, outputs, CLI flags.
- `/home/samuel/projects/pi_light_OR/scripts/generate_targeted_bottleneck_states.py` — current targeted bottleneck generator.
- `/home/samuel/projects/pi_light_OR/scripts/run_sumo_sampled_recovery.py` — state-to-scenario conversion and pilot comparison metrics.
- `/home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py` — LP oracle, dual values, pressure scores, finite differences.
- `/home/samuel/projects/pi_light_OR/scripts/sample_sumo_states.py` — natural SUMO state sampling and metadata schema.
- `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block2_sparse_recovery.json` — Phase 2 main artifact.
- `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block2_sparse_recovery.csv` — Phase 2 per-run table.
- `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block2_sparse_recovery_rules.txt` — Phase 2 recovered rules.
- `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/targeted_bottleneck_states.json` — current targeted state fixture.
- `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/arterial_sampled_states.json` — current natural sampled state fixture.
- `/home/samuel/projects/pi_light_OR/CLAUDE.md` — project conventions and constraints.

### Secondary (MEDIUM confidence)

- Environment probes for Python, NumPy, SciPy, SUMO, netconvert, TraCI, and sumolib availability.
- Codebase probes for file lists, CLI flags, and artifact summaries.

### Tertiary (LOW confidence)

- Proposed numeric route thresholds and exact new script split are design recommendations requiring planner/user confirmation.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — current scripts and environment probes confirm Python/NumPy/SciPy/SUMO availability.
- Architecture: HIGH for reuse targets, MEDIUM for new script split — existing scripts are verified, proposed Phase 3 file boundaries are recommendations.
- Pitfalls: HIGH for overclaim/sample insufficiency, MEDIUM for threshold semantics — pitfalls follow locked context and current artifacts, but threshold policy is not yet locked.

**Research date:** 2026-05-23  
**Valid until:** 2026-06-22 for codebase-local findings; revisit earlier if Phase 1/2 artifacts or state schemas change.
