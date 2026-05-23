# Phase 2: Full Sparse Symbolic Recovery - Research

**Researched:** 2026-05-23  
**Domain:** Sparse symbolic recovery for dual-sensitivity traffic-control rules  
**Confidence:** HIGH

## User Constraints (from CONTEXT.md)

### Locked Decisions
## Implementation Decisions

### Recovery Objective
- Use empirical oracle regret or value gap as the primary optimization target, not imitation/action agreement alone.
- Preserve action agreement as a secondary diagnostic output.
- The solver objective must expose or record any complexity, neighbor-use, and dual-price penalties or budgets.
- Claims must stay finite-dictionary and sample-relative; do not imply global traffic-control optimality.

### Atom Library and Tradeoffs
- Atom families must cover local queue/pressure, downstream capacity/slack, raw neighbor queues, pressure/backpressure, dual sensitivity/price imbalance, and random/permuted dual placebo families.
- Dual-price atoms must be distinguishable from raw neighbor and pressure/backpressure atoms in both metadata and output summaries.
- Placebo/random dual atoms must be available and reported separately from genuine dual-sensitivity atoms.
- Corridor/service atoms remain excluded unless backed by explicit primal constraints from Phase 1.

### Auditable Outputs
- Each recovery run must emit machine-readable JSON/CSV outputs and human-readable symbolic rule text.
- Required output metrics include selected atoms, solve time, oracle regret/value gap, action agreement, program length or selected atom count, neighbor atom count, and dual atom count.
- Equal-complexity comparisons must be reproducible without manual transcription.
- Output naming should remain under `experiments/dual_sensitivity/` and follow existing block-style artifact patterns.

### Integration with Existing Code
- Extend or refactor existing `scripts/run_sparse_recovery.py` rather than creating an unrelated recovery pipeline unless research proves a hard blocker.
- Reuse existing state inputs such as `experiments/dual_sensitivity/targeted_bottleneck_states.json` and existing scenario conversion from `scripts/run_sumo_sampled_recovery.py` where appropriate.
- Keep validation script-based and CPU/SciPy/HiGHS oriented.
- Avoid GPU-heavy MARL, AMPL dependency requirements, or broad method pivots in this phase.

### Claude's Discretion
Claude may choose exact CLI flags and internal data structures, provided the final command produces auditable rules and metrics satisfying RECV-01 through RECV-05. Claude may add small helper functions or output files if they directly support sparse recovery validation and reproducibility.

### Deferred Ideas (OUT OF SCOPE)
## Deferred Ideas

- Static pressure-failure claim routing belongs to Phase 3.
- Closed-loop SUMO controller deployment and performance evidence belong to Phase 4.
- Repository-wide reproduction hardening belongs to Phase 5.
- New corridor/service atoms are deferred until an explicit primal corridor/service constraint is implemented and validated.

## Project Constraints (from CLAUDE.md)

- Frame this work as OR/control methodology for capacitated signalized networks, not as a PI-Light enhancement paper. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Keep claims disciplined: generalized pressure with scarcity-aware corrections is allowed; universal dominance over max-pressure is not allowed. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Keep experiments CPU-oriented with SUMO/TraCI, SciPy/HiGHS, AMPL/HiGHS only where useful, and sparse MIP recovery; do not require GPU. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Emit auditable JSON/CSV artifacts so paper tables/figures can trace back to raw experiment outputs. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Use lowercase snake_case for new Python scripts/modules, `main() -> None`, `argparse`, `Path`, JSON-serializable dictionaries, fail-fast solver checks, and compact JSON status printing. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Run OR scripts from the repository root or with `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts` when importing between `scripts/` files. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Do not place new OR experiments inside `pi_light_code/`; keep them in `scripts/` and write outputs under `experiments/dual_sensitivity/`. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Do not make code changes outside the GSD workflow; this research phase itself must not modify executable code. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RECV-01 | The code implements K-atom sparse symbolic recovery beyond one-atom pilots. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | Extend `solve_library()` in `scripts/run_sparse_recovery.py` with explicit `--max-atoms/--budgets` semantics and library-level/full-library solves. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
| RECV-02 | The recovery objective optimizes oracle regret or value gap, not imitation accuracy alone. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | Preserve the current MILP objective coefficients that charge `best oracle value - chosen oracle value`; keep action agreement diagnostic-only. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
| RECV-03 | The recovery formulation includes explicit penalties or constraints for program size, neighbor atom count, and dual-price atom count. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | Add atom metadata plus hard budgets/soft penalties for size, neighbor, and dual categories. [DERIVED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md] |
| RECV-04 | The atom library includes local queue/pressure, downstream capacity/slack, raw neighbor queue, pressure/backpressure, dual sensitivity/price imbalance, and random/permuted dual placebo families. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | Reuse current feature extraction and expand atom registry metadata so dual, pressure, raw-neighbor, and placebo families are separable. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
| RECV-05 | Recovery outputs include auditable program text/rules, selected atoms, solve time, oracle regret, action agreement, program length, neighbor count, and dual atom count. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | Add rule text rendering, run-level CSV rows, and summary fields that are currently missing from the JSON payload. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
</phase_requirements>

## Summary

Phase 2 should extend `scripts/run_sparse_recovery.py`, not create a separate recovery pipeline, because the current script already loads sampled/targeted SUMO states, converts them through `scenario_from_sample()`, builds oracle/value examples with `summarize_scenario()`, solves a SciPy/HiGHS MILP via `scipy.optimize.milp`, and reports realized oracle regret/action agreement. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] The missing work is schema/semantics hardening: explicit atom metadata, K/budget controls, neighbor/dual penalties or budgets, placebo separation, CSV output, and auditable rule rendering. [DERIVED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md]

The primary implementation path is a targeted refactor of the existing atom library from `dict[str, list[str]]` into an atom registry with `name`, `family`, `requires_neighbor`, `uses_dual`, `is_placebo`, `expression`, and `description` fields. [DERIVED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] The MILP should continue to minimize empirical oracle regret/value gap plus declared penalties, while output summaries must expose the realized regret separately from penalties so equal-complexity comparisons are reproducible. [VERIFIED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md]

**Primary recommendation:** Implement Phase 2 as an in-place enhancement of `scripts/run_sparse_recovery.py`: keep the existing loader/LP/MILP path, add atom metadata and budget constraints, emit JSON+CSV+TXT artifacts, and gate on schema plus regret-first objective semantics rather than on a Phase 3 dual-vs-pressure empirical claim. [DERIVED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| SUMO sampled-state ingestion | Experiment script layer | Data artifacts | `run_sparse_recovery.py` already reads `experiments/dual_sensitivity/*.json`; it should not resample SUMO or rebuild topology. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
| Scenario conversion | OR recovery utility layer | SUMO sampled recovery script | Existing conversion lives in `run_sumo_sampled_recovery.py::scenario_from_sample()` and is imported by `run_sparse_recovery.py`. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sumo_sampled_recovery.py] |
| Oracle/value construction | LP sanity layer | OR recovery utility layer | `summarize_scenario()` produces finite-difference values, dual movement values, pressure scores, queue duals, and storage duals used by recovery. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py] |
| Sparse recovery solve | OR recovery script layer | SciPy/HiGHS solver | The existing MILP with binary action variables and atom-selection variables is the natural owner for K-atom recovery. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
| Rule rendering and CSV/JSON artifact emission | OR recovery script layer | Experiments artifact directory | Outputs should stay under `experiments/dual_sensitivity/` and follow block-style artifact naming. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md] |
| Phase 3 dual-vs-pressure claim interpretation | Out of scope for Phase 2 | Static kill-gate phase | Phase 3 owns pressure-failure claim routing; Phase 2 only produces auditable recovery artifacts. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md] |

## Standard Stack

### Core
| Library/Tool | Version | Purpose | Why Standard |
|--------------|---------|---------|--------------|
| Python via `python3` | 3.14.4 available | Run script-based recovery gates. | Current host has `python3` and imports project recovery dependencies successfully. [VERIFIED: environment probe] |
| NumPy | 2.4.3 | Feature arrays, normalization, oracle/value vectors. | Existing scripts use NumPy arrays for queues, capacities, duals, and MILP matrices. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
| SciPy optimize/HiGHS | 1.17.1 | `linprog` for LP dual summaries and `milp` for sparse recovery. | Existing Block 0 and sparse recovery scripts use SciPy/HiGHS directly. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py; /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
| Python stdlib `json`, `csv`, `pathlib`, `argparse` | Python stdlib | CLI and artifact writing. | Existing project scripts use `argparse`, `Path`, and JSON payloads. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |

### Supporting
| Library/Tool | Version | Purpose | When to Use |
|--------------|---------|---------|-------------|
| SUMO CLI `sumo` | 1.26.0 | State sampling upstream of recovery. | Only needed if regenerating sampled states; Phase 2 validation can consume existing JSON fixtures. [VERIFIED: environment probe; /home/samuel/projects/pi_light_OR/.planning/codebase/TESTING.md] |
| SUMO `netconvert` | 1.26.0 | Network generation upstream of state sampling. | Only needed if rebuilding SUMO network assets. [VERIFIED: environment probe; /home/samuel/projects/pi_light_OR/CLAUDE.md] |
| TraCI / sumolib | 1.26.0 | SUMO sampling and network parsing. | Only needed for `sample_sumo_states.py`, not for the sparse recovery command itself when states already exist. [VERIFIED: environment probe; /home/samuel/projects/pi_light_OR/scripts/run_sumo_sampled_recovery.py] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Extend `run_sparse_recovery.py` | New standalone recovery pipeline | Rejected because CONTEXT locks extension/refactor of the existing script unless a hard blocker is proven, and no hard blocker was found. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md] |
| SciPy/HiGHS MILP | AMPL/HiGHS | Rejected for Phase 2 because CONTEXT says avoid AMPL dependency requirements, while the existing SciPy MILP already solves the scaffold. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md] |
| Action-agreement objective | Oracle regret/value-gap objective | Rejected because Phase 1 and Phase 2 constraints explicitly make value gap primary and action agreement secondary. [VERIFIED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md] |

**Installation:** No new package installation is recommended for Phase 2. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md]

## Package Legitimacy Audit

Not applicable: Phase 2 should not install external packages; it should reuse Python, NumPy, SciPy, SUMO, TraCI, and sumolib already present in the project environment. [VERIFIED: environment probe]

## Architecture Patterns

### System Architecture Diagram

```text
Existing sampled/targeted states JSON
  -> run_sparse_recovery.py load_examples()
  -> scenario_from_sample() from run_sumo_sampled_recovery.py
  -> summarize_scenario() from run_dual_sanity.py
  -> build_example(): oracle values + atom feature vectors + movement metadata
  -> atom registry filter: selected library/families + K/neighbor/dual/placebo budgets
  -> SciPy/HiGHS MILP: choose atom weights + chosen action per example
  -> realized evaluator: recompute choices, regret/value gap, agreement, counts
  -> artifacts: JSON summary + CSV run table + TXT rule text
  -> Phase 3 consumes artifacts for static pressure-failure routing
```
[VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py; DERIVED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md]

### Recommended Project Structure

```text
scripts/
├── run_sparse_recovery.py        # extend in place: atom registry, budgets, renderer, CSV/TXT outputs
└── run_sumo_sampled_recovery.py  # reuse scenario_from_sample(); do not duplicate conversion
experiments/dual_sensitivity/
├── block2_sparse_recovery.json   # main machine-readable Phase 2 output
├── block2_sparse_recovery.csv    # run-level reproducibility table
└── block2_sparse_recovery_rules.txt  # human-readable selected rules
```
[DERIVED: /home/samuel/projects/pi_light_OR/CLAUDE.md]

### Pattern 1: Atom Registry with Metadata
**What:** Replace or wrap `LIBRARIES: dict[str, list[str]]` with a registry such as `ATOM_REGISTRY[name] = {family, requires_neighbor, uses_dual, is_placebo, expression, description}` while retaining named libraries as lists of atom names. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]  
**When to use:** Required for RECV-03, RECV-04, and RECV-05 because selected atom counts must separate neighbor, dual, pressure, raw-neighbor, and placebo families. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]  
**Implementation guidance:** Keep feature computation in `build_example()` and add metadata next to atom definitions; do not embed family inference in string matching. [DERIVED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]

### Pattern 2: Regret-First MILP with Secondary Diagnostics
**What:** Keep the current objective structure where binary action variables are charged by `max(oracle) - oracle[action]`, then add separate penalty coefficients for selected atom count, neighbor atoms, and dual atoms. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]  
**When to use:** Always for Phase 2 recovery; action agreement must remain an output metric, not an objective. [VERIFIED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md]  
**Implementation guidance:** Output both `objective_value_with_penalties` and `realized_total_regret` so penalty tuning cannot obscure value-gap performance. [DERIVED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md]

### Pattern 3: Hard Budgets and Soft Penalties Together
**What:** Support hard flags (`--max-atoms`, `--max-neighbor-atoms`, `--max-dual-atoms`, `--max-placebo-atoms`) and soft flags (`--complexity-penalty`, `--neighbor-penalty`, `--dual-penalty`, `--placebo-penalty`). [DERIVED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md]  
**When to use:** Hard budgets create equal-complexity comparisons; soft penalties support tradeoff sweeps without changing feasibility. [VERIFIED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md]  
**Implementation guidance:** Keep `--budgets` as a compatibility alias for atom-count sweeps, but add explicit names so planners/users can read commands without ambiguity. [DERIVED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]

### Pattern 4: Rule Renderer as Pure Formatting Layer
**What:** Render the selected weighted atom score as human-readable text, e.g. `score(m) = 0.42 * dual_sensitivity(m) + 0.08 * downstream_slack(m); choose argmax_m score(m)`. [DERIVED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]  
**When to use:** After solving each run; renderer must not change selected atoms, weights, or choices. [DERIVED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md]  
**Implementation guidance:** Use atom metadata `expression` and normalized-weight notes; include library, budgets, selected atoms, counts, and regret metrics above each rule. [DERIVED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]

### CLI Flags to Add or Clarify

| Flag | Purpose | Default/Behavior |
|------|---------|------------------|
| `--libraries` | Restrict named libraries to run. | Default all current libraries plus new full library. [DERIVED: codebase] |
| `--atom-families` | Filter families such as `local`, `capacity`, `raw_neighbor`, `pressure`, `dual`, `placebo`. | Default all families in chosen library. [DERIVED: requirements] |
| `--max-atoms` | Hard K atom budget for RECV-01. | Alias or replacement for each value in `--budgets`. [DERIVED: codebase] |
| `--max-neighbor-atoms` | Hard neighbor-use budget for RECV-03. | Default no tighter limit than K. [DERIVED: theory memo] |
| `--max-dual-atoms` | Hard dual-price budget for RECV-03. | Default no tighter limit than K. [DERIVED: theory memo] |
| `--max-placebo-atoms` | Keep placebo separate from genuine dual atoms. | Default no tighter limit unless running non-placebo libraries. [DERIVED: context] |
| `--neighbor-penalty` | Soft penalty per neighbor atom. | Default `0.0` to preserve old behavior. [DERIVED: codebase] |
| `--dual-penalty` | Soft penalty per genuine dual atom. | Default `0.0` to preserve old behavior. [DERIVED: codebase] |
| `--placebo-penalty` | Soft penalty per placebo atom. | Default `0.0`; report separately. [DERIVED: context] |
| `--csv-out` | Run-level CSV table path. | Default derived from `--out` suffix `.csv`. [DERIVED: requirements] |
| `--rules-out` | Human-readable rule text path. | Default derived from `--out` suffix `_rules.txt`. [DERIVED: requirements] |
| `--time-limit-sec` | Solver time limit. | Default current `60.0` seconds. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
| `--objective` | Explicit objective mode. | Default `oracle_regret`; may accept `value_gap` as synonym. [DERIVED: theory memo] |

### Required JSON Output Fields

At top level: `experiment`, `status`, `input_states`, `tls`, `num_examples`, `objective_mode`, `budgets`, `penalties`, `gate_schema_complete`, `gate_regret_first_objective`, `gate_required_families_present`, `summary`, `runs`, `csv_out`, `rules_out`, and `note`. [DERIVED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]

Each run should include: `library`, `budget` or `max_atoms`, `status`, `solver_status`, `objective_value_with_penalties`, `realized_total_regret`, `realized_mean_regret`, `max_regret`, `action_agreement`, `solve_time_sec`, `selected_atoms`, `selected_atom_metadata`, `weights`, `program_complexity`, `neighbor_atom_count`, `dual_atom_count`, `placebo_atom_count`, `pressure_atom_count`, `raw_neighbor_atom_count`, `capacity_atom_count`, `penalty_breakdown`, `rule_text`, and `results`. [DERIVED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]

Each per-example result should include: `scenario`, `source`, `chosen_movement`, `oracle_best_movement`, `oracle_value_chosen`, `oracle_value_best`, `oracle_regret`, `action_agreement`, `score_chosen`, `score_oracle_best`, and optionally `movement_scores`. [DERIVED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]

### CSV Output Fields

Use one row per `(library, K/budget, penalty setting)` with fields: `experiment`, `input_states`, `tls`, `library`, `max_atoms`, `max_neighbor_atoms`, `max_dual_atoms`, `max_placebo_atoms`, `complexity_penalty`, `neighbor_penalty`, `dual_penalty`, `placebo_penalty`, `status`, `solve_time_sec`, `selected_atoms`, `program_complexity`, `neighbor_atom_count`, `dual_atom_count`, `placebo_atom_count`, `realized_total_regret`, `realized_mean_regret`, `max_regret`, `action_agreement`, `rule_text_path`. [DERIVED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]

### Anti-Patterns to Avoid
- **Building a new recovery runner from scratch:** This would duplicate state loading, scenario conversion, oracle construction, and MILP logic already present in `run_sparse_recovery.py`. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]
- **Using action agreement as the pass gate:** Near-ties can make agreement misleading; Phase 1 locks empirical regret/value gap as the primary target. [VERIFIED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md]
- **Inferring atom family from atom names:** Dual, pressure, raw-neighbor, and placebo atoms must remain separate in metadata and summaries. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md]
- **Claiming dual beats pressure from Phase 2 outputs:** Phase 3 owns static pressure-failure claim routing. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SUMO state sampling inside recovery | New TraCI sampling loop in `run_sparse_recovery.py` | Existing state JSON and `scenario_from_sample()` | Current recovery already consumes sampled/targeted states; resampling would couple recovery to SUMO runtime unnecessarily. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py] |
| LP dual/oracle extraction | A second LP implementation | `summarize_scenario()` from `run_dual_sanity.py` | Existing function emits finite-difference values, dual movement values, pressure scores, and dual metadata. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py] |
| CSV writer | Manual comma string concatenation | Python stdlib `csv.DictWriter` | CSV artifacts need quoting-safe selected atom/rule fields. [ASSUMED] |
| Rule text generation | Executable code injection or PI-Light DSL integration | Pure text renderer over selected atoms and weights | Phase 2 needs auditable text, not closed-loop controller deployment. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md] |
| Dual/placebo bookkeeping | Name-prefix heuristics | Atom metadata registry | Metadata separation is a locked requirement. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md] |

**Key insight:** The existing recovery script already has the hard optimization core; Phase 2 value comes from making the finite dictionary, objective, tradeoffs, and outputs auditably explicit. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]

## Common Pitfalls

### Pitfall 1: Action Agreement Becomes the Hidden Objective
**What goes wrong:** The solver or gate selects policies because they match oracle argmax actions, not because they minimize value gap. [VERIFIED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md]  
**Why it happens:** Existing outputs include `action_agreement`, and it is tempting to gate on a percentage. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]  
**How to avoid:** Keep objective coefficients and pass gates tied to `realized_total_regret`, `realized_mean_regret`, and `max_regret`; report agreement as diagnostic only. [DERIVED: theory memo]  
**Warning signs:** A run with high agreement but nonzero/worse regret is marked better than a lower-regret run. [DERIVED: theory memo]

### Pitfall 2: Dual, Pressure, Raw Neighbor, and Placebo Metadata Collapse
**What goes wrong:** `dual_sensitivity`, `pressure_backpressure`, `random_price`, and downstream queue/slack atoms are summarized together, making RECV-03/04 unverifiable. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]  
**Why it happens:** Current `LIBRARIES` is a list of strings without structured metadata. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]  
**How to avoid:** Introduce explicit per-atom metadata and derive counts from metadata only. [DERIVED: codebase]  
**Warning signs:** Output has `selected_atoms` but lacks `dual_atom_count`, `placebo_atom_count`, or `selected_atom_metadata`. [VERIFIED: current output artifact]

### Pitfall 3: Phase 2 Accidentally Interprets the Empirical Claim
**What goes wrong:** A Phase 2 artifact says dual beats pressure, pressure fails, or pressure ties based on current sampled states. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md]  
**Why it happens:** Current sample outputs show dual/pressure comparisons, but Phase 3 is the designed kill gate. [VERIFIED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block1_sparse_recovery_combined.json]  
**How to avoid:** Phrase Phase 2 status as schema/recovery-completeness, not scientific conclusion; leave dual-vs-pressure routing to Phase 3. [DERIVED: roadmap]

### Pitfall 4: Budget Constraints Are Not Actually Enforced
**What goes wrong:** Output records `max_neighbor_atoms` or `max_dual_atoms`, but MILP constraints only cap total selected atoms. [DERIVED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]  
**Why it happens:** The current script only has a total atom budget constraint. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]  
**How to avoid:** Add separate linear constraints over `z_j` for each metadata category and include those limits in `penalty_breakdown`. [DERIVED: codebase]

### Pitfall 5: Rule Text Does Not Match Solver Weights
**What goes wrong:** Human-readable rules omit normalization, zero-weight atoms, or signs, making audit impossible. [DERIVED: requirements]  
**Why it happens:** The current script stores raw weights but no rule text. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]  
**How to avoid:** Render only selected positive-weight atoms; include normalized-feature note and the exact weight dictionary in JSON. [DERIVED: codebase]

## Code Examples

### Recommended Solver Extension Shape
```python
# Source: scripts/run_sparse_recovery.py existing solve_library shape [VERIFIED: codebase]
# Add metadata-driven constraints over z variables; keep regret objective over y variables.
# Pseudocode only; planner should implement inside solve_library or a small helper.
add({z_offset + j: 1.0 for j, atom in enumerate(atoms) if metadata[atom]["requires_neighbor"]}, 0.0, max_neighbor_atoms)
add({z_offset + j: 1.0 for j, atom in enumerate(atoms) if metadata[atom]["uses_dual"]}, 0.0, max_dual_atoms)
add({z_offset + j: 1.0 for j, atom in enumerate(atoms) if metadata[atom]["is_placebo"]}, 0.0, max_placebo_atoms)
```
[DERIVED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]

### Recommended Rule Text Format
```text
Run: library=full_symbolic, max_atoms=3, max_neighbor_atoms=2, max_dual_atoms=1
Counts: program=2, neighbor=1, dual=1, placebo=0
Regret: total=..., mean=..., max=...; action_agreement=...
Rule: choose movement m maximizing score(m)
score(m) = 0.731 * dual_sensitivity(m) + 0.269 * downstream_slack(m)
Note: atom values are normalized by training-sample max absolute value before scoring.
```
[DERIVED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]

## State of the Art

| Old Approach | Current Phase 2 Approach | When Changed | Impact |
|--------------|--------------------------|--------------|--------|
| One-atom/equal-complexity pilots | K-atom finite-dictionary sparse recovery with explicit budgets | Phase 2 requirement RECV-01 [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | Planner should schedule refactor tasks around budgeted atom selection, not one-atom comparison only. [DERIVED] |
| Action-agreement imitation | Oracle regret/value-gap objective with agreement diagnostic | Phase 1 THRY-05 and Phase 2 context [VERIFIED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md] | Gates must inspect regret/value-gap fields first. [DERIVED] |
| String-only atom lists | Atom metadata registry | Phase 2 RECV-03/04 [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | Output can audit neighbor, dual, pressure, and placebo dependence. [DERIVED] |
| JSON-only sparse recovery artifact | JSON + CSV + rule text | Phase 2 RECV-05 [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | Equal-complexity comparisons become reproducible without manual transcription. [DERIVED] |

**Deprecated/outdated:**
- Treating `block1_sparse_recovery_*` as complete Phase 2 evidence is outdated; those artifacts lack CSV output, rule text, explicit neighbor/dual/placebo counts, and full metadata separation. [VERIFIED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block1_sparse_recovery_targeted.json]

## Minimal New Files

| File | Needed? | Reason |
|------|---------|--------|
| `scripts/run_sparse_recovery.py` | Modify existing only | Primary implementation target; do not create unrelated pipeline. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md] |
| `experiments/dual_sensitivity/block2_sparse_recovery.json` | Yes, generated output | Main auditable JSON artifact for Phase 2. [DERIVED: requirements] |
| `experiments/dual_sensitivity/block2_sparse_recovery.csv` | Yes, generated output | Run-level table for equal-complexity comparison. [DERIVED: requirements] |
| `experiments/dual_sensitivity/block2_sparse_recovery_rules.txt` | Yes, generated output | Human-readable symbolic rule text. [DERIVED: requirements] |
| New helper module under `scripts/` | Avoid unless script becomes unwieldy | A small helper is allowed by context, but in-place helpers inside `run_sparse_recovery.py` are sufficient for Phase 2. [DERIVED: context] |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Python stdlib `csv.DictWriter` is preferred over manual CSV string concatenation for quoting-safe CSV artifacts. [ASSUMED] | Don't Hand-Roll | Low; manual CSV could still work but would be more error-prone for rule text fields. |

## Open Questions (RESOLVED)

1. **RESOLVED: Retain `--budgets` and add `--max-atoms`.**
   - What we know: Current script uses `--budgets` for total atom budget sweeps. [VERIFIED: /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py]
   - Final decision: Preserve `--budgets` for compatibility and add `--max-atoms` only as a clearer single-run alias. This matches Plan 02, where `--budgets` remains the sweep interface and `--max-atoms` supports one explicit K run. [DERIVED]
2. **RESOLVED: Keep family-specific libraries and add `full_symbolic`.**
   - What we know: Requirements demand all families be available and separately reported. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
   - Final decision: Preserve existing named libraries, add a `full_symbolic` library containing all allowed Phase 2 atom families, and support explicit `--libraries` / `--atom-families` filtering so Phase 3 can reproduce both family-specific and full-library comparisons. [DERIVED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `python3` | Recovery scripts | ✓ | 3.14.4 | `python` exists but is 3.12.3; prefer `python3`. [VERIFIED: environment probe] |
| NumPy | Feature tensors | ✓ | 2.4.3 | None needed. [VERIFIED: environment probe] |
| SciPy | LP/MILP solver | ✓ | 1.17.1 | None needed for Phase 2. [VERIFIED: environment probe] |
| SUMO `sumo` | Regenerating sampled states | ✓ | 1.26.0 | Use existing sampled JSON if not regenerating. [VERIFIED: environment probe] |
| SUMO `netconvert` | Rebuilding network assets | ✓ | 1.26.0 | Use existing network/state artifacts if not rebuilding. [VERIFIED: environment probe] |
| TraCI | SUMO sampling | ✓ | 1.26.0 | Use existing sampled JSON for recovery-only validation. [VERIFIED: environment probe] |
| sumolib | SUMO metadata parsing | ✓ | 1.26.0 | Use existing sampled JSON for recovery-only validation. [VERIFIED: environment probe] |

**Missing dependencies with no fallback:** None found for Phase 2 recovery validation. [VERIFIED: environment probe]

**Missing dependencies with fallback:** None found; SUMO/TraCI are only needed if regenerating inputs. [VERIFIED: environment probe]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Script-based JSON gates; no pytest/unittest config detected. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/codebase/TESTING.md] |
| Config file | None; gate parameters live in script CLI defaults. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/codebase/TESTING.md] |
| Quick run command | `python3 scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json --budgets 1 2 3 --out experiments/dual_sensitivity/block2_sparse_recovery.json --csv-out experiments/dual_sensitivity/block2_sparse_recovery.csv --rules-out experiments/dual_sensitivity/block2_sparse_recovery_rules.txt` [DERIVED] |
| Full suite command | `python3 scripts/run_dual_sanity.py && python3 scripts/run_sumo_sampled_recovery.py && python3 scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/arterial_sampled_states.json --states experiments/dual_sensitivity/targeted_bottleneck_states.json --budgets 1 2 3 --out experiments/dual_sensitivity/block2_sparse_recovery_combined.json --csv-out experiments/dual_sensitivity/block2_sparse_recovery_combined.csv --rules-out experiments/dual_sensitivity/block2_sparse_recovery_combined_rules.txt` [DERIVED] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| RECV-01 | K-atom recovery beyond one-atom pilots | integration | Quick run with `--budgets 1 2 3`, then assert at least one run has `max_atoms`/`budget` > 1 and no schema failure. [DERIVED] | ✅ existing script; output fields need Phase 2 implementation |
| RECV-02 | Regret/value-gap objective primary | integration/schema | Inspect JSON for `objective_mode: oracle_regret`, `realized_total_regret`, `realized_mean_regret`, and diagnostic-only `action_agreement`. [DERIVED] | ✅ partial existing fields; objective metadata needs Phase 2 implementation |
| RECV-03 | Program/neighbor/dual penalties or budgets | integration/schema | Inspect each run for `penalty_breakdown`, `neighbor_atom_count`, `dual_atom_count`, `max_neighbor_atoms`, and `max_dual_atoms`. [DERIVED] | ❌ Wave 0 gap |
| RECV-04 | Required atom families including placebo/random dual | integration/schema | Inspect top-level `atom_registry` or run metadata for families `local`, `capacity`, `raw_neighbor`, `pressure`, `dual`, `placebo`. [DERIVED] | ❌ Wave 0 gap |
| RECV-05 | JSON/CSV/rule text outputs | integration/filesystem | Confirm JSON, CSV, and rules TXT exist and JSON contains `csv_out` and `rules_out`. [DERIVED] | ❌ Wave 0 gap |

### Gate Criteria
- `status` is `PASSED` only when schema completeness gates pass and at least one run solves successfully under K > 1; do not require dual to beat pressure in Phase 2. [DERIVED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md]
- `gate_regret_first_objective == true` when objective metadata and penalty breakdown show regret/value-gap terms are primary and action agreement is not used as an objective coefficient. [DERIVED: /home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md]
- `gate_required_families_present == true` when atom metadata includes local queue/pressure, downstream capacity/slack, raw neighbor queue, pressure/backpressure, dual sensitivity/price imbalance, and random/permuted dual placebo families. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
- `gate_outputs_complete == true` when JSON, CSV, and rule text files exist and contain the required summary fields. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
- `gate_phase3_claim_deferred == true` when output note explicitly says dual-vs-pressure empirical claim routing is deferred to Phase 3. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md]

### Sampling Rate
- **Per task commit:** Run the quick command against `targeted_bottleneck_states.json`. [DERIVED]
- **Per wave merge:** Run full suite command against arterial sampled plus targeted states. [DERIVED]
- **Phase gate:** JSON schema complete, CSV exists, rule text exists, K > 1 run solved, and no Phase 3 empirical claim is asserted. [DERIVED]

### Wave 0 Gaps
- [ ] Add atom metadata registry in `scripts/run_sparse_recovery.py` for RECV-03/04. [VERIFIED: current script lacks metadata]
- [ ] Add CSV output writer for RECV-05. [VERIFIED: current script writes JSON only]
- [ ] Add rule text renderer for RECV-05. [VERIFIED: current script has no rule text output]
- [ ] Add schema gates and explicit Phase 3 deferral note. [DERIVED: roadmap]

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No authentication surface; local experiment scripts only. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md] |
| V3 Session Management | no | No sessions. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md] |
| V4 Access Control | no | No deployed service boundary in Phase 2. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md] |
| V5 Input Validation | yes | Validate CLI paths, nonnegative budgets, nonnegative penalties, and known atom/library names before solving. [DERIVED: codebase] |
| V6 Cryptography | no | No cryptography required. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md] |

### Known Threat Patterns for Script-Based Recovery
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Accidental overwrite of important outputs | Tampering | Keep outputs under `experiments/dual_sensitivity/` and require explicit paths for JSON/CSV/TXT. [DERIVED: project conventions] |
| Malformed input JSON causing misleading artifacts | Tampering | Validate presence of `samples`, `queues`, `capacities`, and `tls_movements` before solving; fail fast with clear error. [DERIVED: /home/samuel/projects/pi_light_OR/scripts/run_sumo_sampled_recovery.py] |
| Executable rule injection | Elevation of privilege | Render plain text only; do not `exec` generated rules in Phase 2. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md] |

## Sources

### Primary (HIGH confidence)
- `/home/samuel/projects/pi_light_OR/.planning/phases/02-full-sparse-symbolic-recovery/02-CONTEXT.md` — locked Phase 2 decisions, scope, outputs, and deferred ideas. [VERIFIED: codebase]
- `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md` — RECV-01 through RECV-05 definitions. [VERIFIED: codebase]
- `/home/samuel/projects/pi_light_OR/.planning/ROADMAP.md` — Phase 2 boundary and Phase 3 kill-gate ownership. [VERIFIED: codebase]
- `/home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_CLAIMS.md` — THRY-05 finite-dictionary regret/value-gap statement and claim boundaries. [VERIFIED: codebase]
- `/home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py` — existing sparse MILP scaffold. [VERIFIED: codebase]
- `/home/samuel/projects/pi_light_OR/scripts/run_sumo_sampled_recovery.py` — existing sampled-state scenario conversion. [VERIFIED: codebase]
- `/home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py` — LP dual/oracle summary source. [VERIFIED: codebase]
- `/home/samuel/projects/pi_light_OR/.planning/codebase/TESTING.md` — script-based validation pattern. [VERIFIED: codebase]
- `/home/samuel/projects/pi_light_OR/CLAUDE.md` — project constraints and conventions. [VERIFIED: codebase]

### Secondary (MEDIUM confidence)
- Environment probe executed in this session for `python3`, `python`, SUMO, netconvert, NumPy, SciPy, TraCI, and sumolib versions. [VERIFIED: environment probe]
- Existing artifacts `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block1_sparse_recovery_targeted.json` and `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block1_sparse_recovery_combined.json` for current output gaps. [VERIFIED: codebase]

### Tertiary (LOW confidence)
- No web-only sources used. [VERIFIED: research process]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — based on existing scripts plus live environment probe. [VERIFIED: codebase; VERIFIED: environment probe]
- Architecture: HIGH — based on direct code paths and locked context decisions. [VERIFIED: codebase]
- Pitfalls: HIGH — based on Phase 1 claim memo, Phase 2 context, requirements, and current output gaps. [VERIFIED: codebase]

**Research date:** 2026-05-23  
**Valid until:** 2026-06-22 for Phase 2 planning, assuming no major rewrite of `scripts/run_sparse_recovery.py` before implementation. [ASSUMED]
