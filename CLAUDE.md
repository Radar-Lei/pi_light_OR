<!-- GSD:project-start source:PROJECT.md -->
## Project

**PI-Light OR / Dual-Sensitivity Symbolic Traffic Control**

This project develops an OR-methodology paper on capacitated network traffic signal control, not a PI-Light enhancement paper. The working direction is **dual-sensitivity-guided symbolic control**: derive movement-level shadow-price / dual-sensitivity signals from a continuous store-and-forward or CTM-lite traffic-network relaxation, then recover compact interpretable signal-control policies under explicit complexity and neighbor-use constraints.

The target audience is Transportation Research Part B / Transportation Science reviewers who expect mathematical modeling, structural insight, rigorous optimization formulation, and closed-loop computational evidence against strong max-pressure-style baselines.

**Core Value:** Show that network-optimization dual sensitivities provide a generalized max-pressure principle that reduces to pressure when constraints are slack and adds scarcity-aware corrections when storage, supply, or corridor bottleneck constraints bind, and that this principle can be compressed into compact symbolic traffic-signal policies.

### Constraints

- **Venue fit**: Primary targets are Transportation Research Part B and Transportation Science — the paper must be framed as OR / methodological traffic-network control, not AI-controller benchmarking.
- **Theory requirement**: TR-B requires formal model structure and propositions/theorems; Transportation Science can tolerate slightly less theory but still needs rigorous OR formulation and computational evidence.
- **Empirical requirement**: Static one-step LP/ranking evidence is insufficient; closed-loop SUMO multi-seed experiments against strong pressure-style baselines are mandatory.
- **Claim discipline**: The core claim is generalized pressure with scarcity-aware corrections, not universal dominance over max-pressure.
- **Compute**: Experiments should remain CPU-oriented using SUMO/TraCI, SciPy/HiGHS, AMPL/HiGHS where useful, and sparse MIP recovery; no required GPU pipeline.
- **Reproducibility**: Scripts must emit auditable JSON/CSV artifacts and tables/figures must trace back to raw experiment outputs.
- **Baseline honesty**: Max-pressure/backpressure and capacity/spillback-aware variants are first-class baselines, not strawmen.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3 - experiment scripts and PI-Light code in `scripts/*.py`, `networks/*/create_network.py`, and `pi_light_code/**/*.py`.
- XML - SUMO networks, routes, additional TLS programs, and SUMO configs in `networks/*/*.xml` and `networks/*/*.sumocfg`.
- JSON - configuration, CityFlow datasets, sampled states, and experiment outputs in `pi_light_code/config.json`, `pi_light_code/data/*/*.json`, and `experiments/dual_sensitivity/*.json`.
- LaTeX/BibTeX - reference paper/template sources in `Programmatically_Interpretable_Reinforcement_Learning_original_paper/*.tex` and `INFORMS-TRSC-Template-5-6-2025/*.tex`.
- C++ extension build scaffold - `pi_light_code/utilities/setup.py` builds any local `*.cpp` files as Python extensions with `distutils.core.Extension`.
## Runtime
- Python 3.14.4 currently available on the host.
- Original PI-Light runtime targets Python 3.8.10 per `pi_light_code/readme.md`.
- SUMO 1.26.0 installed and usable; `sumo --version` reports `Eclipse SUMO sumo 1.26.0`.
- CPU-oriented experiments are the expected path: `refine-logs/EXPERIMENT_PLAN.md` lists SUMO/TraCI simulation, AMPL/HiGHS solves, and sparse MIP recovery as CPU-only work.
- Not detected: no `requirements.txt`, `pyproject.toml`, `environment.yml`, `Pipfile`, or lockfile under `/home/samuel/projects/pi_light_OR`.
- Local virtual environment directory `.venv/` is ignored by `.gitignore`; do not commit it.
- Lockfile: missing.
## Frameworks
- SUMO 1.26.0 - microscopic traffic simulation for `networks/single_intersection`, `networks/arterial`, `networks/grid_4x4`, and `networks/chengdu`.
- TraCI / sumolib - Python control and network parsing in `scripts/sample_sumo_states.py` and `scripts/generate_targeted_bottleneck_states.py`.
- CityFlow 0.1.0 - original PI-Light simulator dependency declared in `pi_light_code/readme.md`; used directly by `pi_light_code/env/TSC_env.py` via `cityflow.Engine(...)`.
- PyTorch 1.7.1+cu110 - original PI-Light neural baseline dependency declared in `pi_light_code/readme.md`; imported by `pi_light_code/agent/drl_based/*.py`, `pi_light_code/agent/tiny_light/*.py`, and `pi_light_code/replay_buffer/replay_buffer.py`.
- Not detected: no pytest/unittest config or dedicated test framework found.
- Validation is script-driven through experiment runners such as `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`, and `scripts/run_sparse_recovery.py`.
- SUMO `netconvert` - network compiler invoked from `networks/single_intersection/create_network.py`, `networks/arterial/create_network.py`, and `networks/grid_4x4/create_network.py`.
- SciPy HiGHS LP/MILP backends - `scripts/run_dual_sanity.py` uses `scipy.optimize.linprog(method="highs")`; `scripts/run_sparse_recovery.py` uses `scipy.optimize.milp` plus sparse matrices.
- scikit-optimize - PI-Light MCTS parameter optimization in `pi_light_code/agent/pi_light/MCTS.py` via `gp_minimize`, `Real`, and `Integer`.
- scikit-learn + Graphviz - VIPER/decision-tree imitation in `pi_light_code/agent/imitation_based/dt.py`.
## Key Dependencies
- `traci` / `sumolib` - required for SUMO state sampling and movement metadata in `scripts/sample_sumo_states.py`.
- `scipy` - required for LP/MILP optimization in `scripts/run_dual_sanity.py` and `scripts/run_sparse_recovery.py`.
- `numpy` - numerical arrays and scoring throughout `scripts/*.py` and `pi_light_code/**/*.py`.
- `cityflow` - required by original PI-Light environment `pi_light_code/env/TSC_env.py`.
- `torch` - required by DRL, TinyLight, replay buffer, and observation/reward tensor conversion in `pi_light_code/**/*.py`.
- SUMO CLI tools: `sumo` for simulation and `netconvert` for compiling network XML.
- `gym` - action spaces and optional rendering in `pi_light_code/env/TSC_env.py`.
- `scikit-learn` - decision tree policy distillation in `pi_light_code/agent/imitation_based/dt.py`.
- `graphviz` - decision tree visualization in `pi_light_code/agent/imitation_based/dt.py`.
- `scikit-optimize` - Bayesian parameter search for PI-Light synthesized programs in `pi_light_code/agent/pi_light/MCTS.py`.
## Configuration
- No `.env` file is present in the project root; `.env` and `.env.*` are ignored by `.gitignore`.
- Original PI-Light settings are centralized in `pi_light_code/config.json` with keys such as `interval`, `num_step`, `action_interval`, `device`, `engine_thread`, and agent-specific observation/reward/metric lists.
- SUMO network experiments use `.sumocfg` files under `networks/*/*.sumocfg` and generated XML route/network/additional files under `networks/*/`.
- Script outputs default to local JSON artifacts under `experiments/dual_sensitivity/`.
- `pi_light_code/utilities/setup.py` dynamically builds local C++ extension modules from `*.cpp` files when present.
- `networks/*/create_network.py` scripts generate `.nod.xml`, `.edg.xml`, `.net.xml`, `.rou.xml`, `.add.xml`, and `.sumocfg` artifacts using SUMO tools.
- No Python packaging/build config is detected at the repository root.
## Platform Requirements
- Install Python packages used by scripts and original PI-Light code: `numpy`, `scipy`, `traci`, `sumolib`, `torch`, `gym`, `scikit-learn`, `graphviz`, `scikit-optimize`, and `cityflow` where original PI-Light runs are needed.
- Install SUMO 1.26.0+ with `sumo` and `netconvert` available on `PATH`.
- Use local JSON/XML artifacts in `networks/`, `experiments/dual_sensitivity/`, and `pi_light_code/data/`; no database service is required.
- Not applicable: this is a research/experiment codebase, not a deployed service.
- Deployment target for experiments is local CPU execution with SUMO/TraCI and offline SciPy/HiGHS optimization.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Use lowercase snake_case for new Python scripts and modules, matching `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, `scripts/sample_sumo_states.py`, and `networks/single_intersection/create_network.py`.
- Preserve upstream PI-Light numbered runner names in `pi_light_code/00_run_tiny_light.py`, `pi_light_code/01_run_baseline.py`, `pi_light_code/02_run_MCTS.py`, `pi_light_code/03_run_viper.py`, and `pi_light_code/015_baseline_transfer.py`; do not create new numbered runners unless extending that upstream experiment family.
- Use uppercase Markdown names for planning/research logs in `refine-logs/EXPERIMENT_RESULTS.md`, `refine-logs/EXPERIMENT_TRACKER.md`, and `refine-logs/THEORY_AND_ATOMS.md`.
- Use snake_case for Python functions, as in `scripts/run_dual_sanity.py:35` (`build_scenario`), `scripts/run_dual_sanity.py:99` (`solve_relaxation`), `scripts/run_sparse_recovery.py:110` (`solve_library`), and `pi_light_code/utilities/utils.py:65` (`set_seed`).
- Put script orchestration in a `main() -> None` function and call it under `if __name__ == "__main__":`, matching `scripts/run_dual_sanity.py:328`, `scripts/run_sparse_recovery.py:236`, and `scripts/sample_sumo_states.py:99`.
- Upstream PI-Light runners use top-level `argparse` objects in `pi_light_code/01_run_baseline.py:9` and `pi_light_code/02_run_MCTS.py:10`; keep new OR pipeline scripts on the `main()` pattern used in `scripts/`.
- Use snake_case for local variables and dictionaries, matching `scripts/run_sumo_sampled_recovery.py:21` (`scenario_from_sample`), `scripts/run_sparse_recovery.py:272` (`by_key`), and `pi_light_code/01_run_baseline.py:82` (`metrics`).
- Use short mathematical variable names only inside optimization formulations where they mirror the model, as in `scripts/run_dual_sanity.py:107` (`c`), `scripts/run_dual_sanity.py:113` (`a_eq`), and `scripts/run_sparse_recovery.py:131` (`c`).
- Use module-level constants in uppercase for experiment libraries or generated-network constants, matching `scripts/run_sparse_recovery.py:18` (`LIBRARIES`) and `networks/single_intersection/create_network.py:25` (`NETWORK_DIR`).
- Use dataclasses for structured optimization state, as in `scripts/run_dual_sanity.py:21` (`@dataclass(frozen=True) class Scenario`).
- Use PEP 585 type hints in new scripts, matching `scripts/run_dual_sanity.py:25` (`list[str]`), `scripts/run_sparse_recovery.py:29` (`list[Path]`), and `scripts/sample_sumo_states.py:26` (`dict[str, Any]`).
- Preserve untyped upstream PI-Light classes in `pi_light_code/agent/base_agent.py` and `pi_light_code/env/TSC_env.py` unless refactoring a whole module.
## Code Style
- No formatter configuration is detected: `find /home/samuel/projects/pi_light_OR -maxdepth 3` found no `pyproject.toml`, `.prettierrc`, `ruff.toml`, `setup.cfg`, or equivalent formatter files.
- Use 4-space indentation and PEP 8 spacing in new Python, matching `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, and `scripts/sample_sumo_states.py`.
- Keep generated XML string templates local to generator functions, matching `networks/single_intersection/create_network.py:28` (`write_nodes`) and `networks/single_intersection/create_network.py:63` (`write_routes`).
- No linting configuration is detected: `find /home/samuel/projects/pi_light_OR -maxdepth 3` found no `.eslintrc*`, `eslint.config.*`, `biome.json`, `ruff.toml`, or `mypy.ini`.
- Prefer explicit exceptions in new code, matching `scripts/run_dual_sanity.py:155` (`raise RuntimeError(...)`) and avoid bare `except` patterns such as `pi_light_code/utilities/utils.py:94` unless preserving upstream behavior.
- Use assertions only for internal invariants, matching `pi_light_code/agent/pi_light/pi_light.py:32`; for CLI validation failures, raise `SystemExit(1)` or `ValueError`, matching `scripts/run_dual_sanity.py:96` and `scripts/run_dual_sanity.py:363`.
## Import Organization
- No package-level path alias is configured; scripts use direct imports from the working directory, such as `scripts/run_sparse_recovery.py:14` (`from run_dual_sanity import summarize_scenario`).
- Run OR scripts from the repository root or with `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts` when importing between files in `scripts/`.
- Run upstream PI-Light scripts from `pi_light_code/`, because `pi_light_code/utilities/utils.py:11` loads `config.json` relative to the current working directory.
## Error Handling
- Use fail-fast solver checks with informative messages, matching `scripts/run_dual_sanity.py:155-156` for LP failures and `scripts/run_sparse_recovery.py:188-195` for MILP failure payloads.
- For experiment gates, write a JSON artifact and exit nonzero only when the gate is truly failed, matching `scripts/run_dual_sanity.py:359-364`.
- For optional/invalid sampled scenarios, return `None` and skip, matching `scripts/run_sumo_sampled_recovery.py:21-34` and `scripts/run_sumo_sampled_recovery.py:161-164`.
## Logging
- New OR scripts print compact JSON status objects, matching `scripts/run_dual_sanity.py:362`, `scripts/run_sparse_recovery.py:343`, and `scripts/sample_sumo_states.py:133`.
- Upstream PI-Light experiments configure `logging` with stream/file handlers in `pi_light_code/utilities/utils.py:35-56` and release handlers in `pi_light_code/utilities/utils.py:59-63`; use this when extending `pi_light_code/` runners.
- Network generators use direct `print()` progress output, matching `networks/single_intersection/create_network.py:195-198` and `networks/arterial/create_network.py:465-496`.
## Comments
- Use docstrings at the top of standalone scripts to state scope and caveats, matching `scripts/run_dual_sanity.py:1-7`, `scripts/run_offline_recovery_pilot.py:1-7`, and `scripts/sample_sumo_states.py:1-6`.
- Use inline comments for model interpretation or paper caveats, matching `scripts/run_sumo_sampled_recovery.py:41` and `refine-logs/EXPERIMENT_RESULTS.md:40-43`.
- Avoid relying on comments to document known bugs in executable paths; `pi_light_code/env/TSC_env.py:363` contains a Chinese bug note and should be converted into an issue/test before changing behavior.
- Not applicable; no JavaScript/TypeScript code is detected under `/home/samuel/projects/pi_light_OR`.
## Function Design
- Prefer small, single-purpose functions in new scripts, matching `scripts/run_dual_sanity.py:35` (`build_scenario`), `scripts/run_dual_sanity.py:99` (`solve_relaxation`), and `scripts/run_dual_sanity.py:282` (`summarize_scenario`).
- Large generator scripts in `networks/grid_4x4/create_network.py` and `networks/arterial/create_network.py` are acceptable for deterministic artifact generation; keep additions as separate helper functions rather than extending `__main__` blocks.
- Pass configuration through explicit CLI arguments using `argparse`, matching `scripts/run_sparse_recovery.py:237-247`, `scripts/sample_sumo_states.py:100-106`, and `pi_light_code/01_run_baseline.py:9-12`.
- Use `Path` for new file path parameters, matching `scripts/run_sparse_recovery.py:29` and `scripts/sample_sumo_states.py:26`; upstream `pi_light_code/` uses `os.path` and can stay consistent within that subtree.
- Return dictionaries that are JSON-serializable for experiment summaries, matching `scripts/run_dual_sanity.py:173-185`, `scripts/run_sumo_sampled_recovery.py:130-146`, and `scripts/run_sparse_recovery.py:220-233`.
- Return numeric metric tuples only in upstream runner helpers, matching `pi_light_code/01_run_baseline.py:65-69` and `pi_light_code/02_run_MCTS.py:84-86`.
## Module Design
- `scripts/` modules expose reusable pure functions plus a CLI `main()`, as in `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`, and `scripts/run_sparse_recovery.py`.
- `pi_light_code/agent/` exposes agent classes through `pi_light_code/agent/__init__.py`; use `pi_light_code/utilities/utils.py:19-32` (`get_agent`) instead of dynamic imports when selecting upstream agents.
- `pi_light_code/agent/__init__.py`, `pi_light_code/env/__init__.py`, and `pi_light_code/replay_buffer/__init__.py` are the only detected barrel-style package files; do not add barrel files in `scripts/`.
## Project Skills
- Not detected: `.claude/skills/` and `.agents/skills/` are absent or empty under `/home/samuel/projects/pi_light_OR` according to the project skill directory check.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## System Overview
```text
```
## Component Responsibilities
| Component | Responsibility | File |
|-----------|----------------|------|
| Dual-sensitivity LP core | Defines proxy traffic scenarios, solves one-step store-and-forward LP relaxations, compares dual movement values to finite differences, writes Block 0 JSON artifacts. | `scripts/run_dual_sanity.py` |
| SUMO state sampler | Runs `sumo` through TraCI, records edge queues, vehicle counts, estimated capacities, and TLS movement topology. | `scripts/sample_sumo_states.py` |
| Targeted bottleneck generator | Builds synthetic arterial bottleneck/spillback states using SUMO network metadata. | `scripts/generate_targeted_bottleneck_states.py` |
| SUMO sampled recovery pilot | Converts sampled SUMO states into `Scenario` objects, evaluates oracle/dual/pressure/raw-neighbor variants, writes Block 1 recovery JSON. | `scripts/run_sumo_sampled_recovery.py` |
| Sparse symbolic recovery | Builds feature libraries, normalizes examples, solves a SciPy/HiGHS MILP over atom weights and chosen actions. | `scripts/run_sparse_recovery.py` |
| CityFlow simulation environment | Parses CityFlow roadnets, constructs intersections, computes observations/rewards/metrics, and advances simulation. | `pi_light_code/env/TSC_env.py` |
| Intersection state machine | Owns phase timing, yellow transitions, road/lane/roadlink indexing, and phase-to-lanelink mappings. | `pi_light_code/env/intersection.py` |
| PI-Light executable rule agent | Executes synthesized inlane/outlane Python snippets over movements and aggregates movement values to phase scores. | `pi_light_code/agent/pi_light/pi_light.py` |
| PI-Light DSL/program search | Defines DSL instructions, conditions, blocks, program expansion, complexity, and bale code output. | `pi_light_code/agent/pi_light/program.py` |
| Baseline agents | Implements rule-based and DRL baselines using the common agent interface. | `pi_light_code/agent/rule_based/max_pressure.py`, `pi_light_code/agent/drl_based/*.py` |
| Network generators | Generate SUMO nodes, edges, routes, TLS additional files, and `.sumocfg` files. | `networks/arterial/create_network.py`, `networks/grid_4x4/create_network.py`, `networks/single_intersection/create_network.py` |
## Pattern Overview
- Keep OR/SUMO experiments in `scripts/` and outputs in `experiments/dual_sensitivity/`; scripts use CLI arguments and write JSON via `Path(...).write_text(...)`.
- Keep original PI-Light/CityFlow code under `pi_light_code/`; driver scripts instantiate `TSCEnv`, populate `env.n_agent`, then call `utilities/snippets.py::run_an_episode`.
- Use data objects at layer boundaries: `Scenario` in `scripts/run_dual_sanity.py`, SUMO sample dictionaries from `scripts/sample_sumo_states.py`, CityFlow config dictionaries from `pi_light_code/config.json`.
## Layers
- Purpose: Launch reproducible experiment blocks and choose input/output artifacts.
- Location: `scripts/*.py`, `pi_light_code/00_run_tiny_light.py`, `pi_light_code/01_run_baseline.py`, `pi_light_code/02_run_MCTS.py`, `pi_light_code/03_run_viper.py`
- Contains: `argparse` CLIs, seed lists, loop structure, multiprocessing, file output paths.
- Depends on: OR utilities in `scripts/run_dual_sanity.py`, SUMO via `traci`, CityFlow via `TSCEnv`.
- Used by: Manual experiment runs and paper/refinement workflow.
- Purpose: Turn traffic states into LP/MILP ranking/recovery problems.
- Location: `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, `scripts/run_sumo_sampled_recovery.py`
- Contains: `Scenario`, LP construction with `scipy.optimize.linprog`, finite-difference oracle construction, MILP atom selection with `scipy.optimize.milp`.
- Depends on: NumPy, SciPy, sampled state JSON, scenario dictionaries.
- Used by: Block 0 sanity checks and Block 1 sparse recovery experiments.
- Purpose: Provide realistic traffic networks and sampled queue states for OR recovery experiments.
- Location: `networks/`, `experiments/dual_sensitivity/*.json`
- Contains: `.net.xml`, `.rou.xml`, `.sumocfg`, generated queue-state JSON files.
- Depends on: SUMO `netconvert`, `sumo`, `traci`, `sumolib`.
- Used by: `scripts/sample_sumo_states.py`, `scripts/generate_targeted_bottleneck_states.py`, recovery scripts.
- Purpose: Emulate PI-Light benchmark simulation, observations, rewards, and metrics.
- Location: `pi_light_code/env/`
- Contains: `TSCEnv`, `Intersection`, `Road`, `RoadLink`, `Phase`.
- Depends on: CityFlow, Gym spaces, PyTorch tensor conversion for DRL agents.
- Used by: PI-Light and baseline run scripts under `pi_light_code/`.
- Purpose: Convert observations into phase actions.
- Location: `pi_light_code/agent/`
- Contains: `BaseAgent`, rule-based controllers, DRL controllers, TinyLight, PI-Light DSL agent, MCTS synthesizer, imitation/VIPER policies.
- Depends on: `TSCEnv`, intersection topology, config-specified feature lists.
- Used by: `pi_light_code/00_run_tiny_light.py`, `pi_light_code/01_run_baseline.py`, `pi_light_code/02_run_MCTS.py`, `pi_light_code/03_run_viper.py`.
## Data Flow
### OR Dual-Sensitivity Recovery Path
### SUMO State Sampling Path
### PI-Light / CityFlow Control Path
- OR scripts keep state local to dataclasses and dictionaries, then serialize results to JSON.
- SUMO state lives in the external TraCI simulation during sampling.
- CityFlow state lives in `TSCEnv.eng`, while current phase/time live in each `Intersection` (`pi_light_code/env/intersection.py:14`).
- Agent state includes current phase, learned network weights, and replay buffers depending on agent type.
## Key Abstractions
- Purpose: Minimal continuous traffic-control problem for LP dual sensitivity.
- Examples: `scripts/run_dual_sanity.py:21`, `scripts/run_sumo_sampled_recovery.py:46`
- Pattern: Frozen dataclass with links, movements, queues, capacities, demands, service capacities, and objective weights.
- Purpose: Persist simulation snapshots independent of TraCI runtime.
- Examples: `scripts/sample_sumo_states.py:85`, `scripts/generate_targeted_bottleneck_states.py:18`
- Pattern: Dictionary with `time`, `queues`, `vehicle_counts`, `capacities`, and `tls_movements`.
- Purpose: Multi-intersection CityFlow environment and feature/metric adapter.
- Examples: `pi_light_code/env/TSC_env.py:13`
- Pattern: Central environment class with `_info_functions` dispatch table mapping config feature names to computation methods (`pi_light_code/env/TSC_env.py:27`).
- Purpose: Common controller interface for one intersection.
- Examples: `pi_light_code/agent/base_agent.py:5`
- Pattern: `reset`, `pick_action`, `learn`, and `store_experience` methods; subclasses override action logic.
- Purpose: Searchable DSL for interpretable inlane/outlane scoring programs.
- Examples: `pi_light_code/agent/pi_light/program.py:189`, `pi_light_code/agent/pi_light/program.py:349`
- Pattern: Tree of `Instruction`, `If`, `IfElse`, and `Block` objects that emits executable Python code snippets.
## Entry Points
- Location: `scripts/run_dual_sanity.py`
- Triggers: `python scripts/run_dual_sanity.py --out experiments/dual_sensitivity/block0_dual_sanity.json`
- Responsibilities: Validate dual rankings against finite-difference and pressure special cases.
- Location: `scripts/sample_sumo_states.py`
- Triggers: `python scripts/sample_sumo_states.py --network arterial --out experiments/dual_sensitivity/arterial_sampled_states.json`
- Responsibilities: Generate SUMO queue-state samples for recovery scripts.
- Location: `scripts/run_sparse_recovery.py`
- Triggers: `python scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json`
- Responsibilities: Solve atom-selection MILP and report realized regret/action agreement.
- Location: `pi_light_code/02_run_MCTS.py`
- Triggers: `python 02_run_MCTS.py --dataset Hangzhou2` from `pi_light_code/`
- Responsibilities: Build `TSCEnv`, synthesize PI-Light code with `MCTS_synthesizer`, inject rules, and evaluate.
- Location: `pi_light_code/01_run_baseline.py`
- Triggers: `python 01_run_baseline.py --model MaxPressure --dataset Hangzhou2` from `pi_light_code/`
- Responsibilities: Instantiate baseline agents, train DRL agents when needed, evaluate metrics over 10 flows.
- Location: `networks/arterial/create_network.py`, `networks/grid_4x4/create_network.py`, `networks/single_intersection/create_network.py`
- Triggers: Direct Python execution in the network directory.
- Responsibilities: Generate node/edge/route/TLS/config XML and compile `.net.xml` with `netconvert`.
## Architectural Constraints
- **Threading:** OR scripts are single-process by default; PI-Light drivers use `multiprocessing.Pool` for flow-level parallelism (`pi_light_code/01_run_baseline.py:90`) and force PyTorch to one thread via `utilities/utils.py:79`.
- **Global state:** `pi_light_code/agent/pi_light/program.py` uses module-level DSL limits (`max_block_breadth`, `max_depth`, `max_num_if`, `max_weight_param`) that constrain search globally.
- **Working directory:** PI-Light utilities expect `config.json` in the current working directory (`pi_light_code/utilities/utils.py:10`); run PI-Light scripts from `pi_light_code/` or adjust paths.
- **Backend split:** `scripts/` uses SUMO/TraCI/SciPy artifacts; `pi_light_code/` uses CityFlow roadnet/flow JSON and agent classes. Do not mix SUMO `.net.xml` files directly into `TSCEnv` without an adapter.
- **Dynamic code execution:** `PiLight` evaluates synthesized inlane/outlane code with `exec` in per-movement loops (`pi_light_code/agent/pi_light/pi_light.py:50`, `pi_light_code/agent/pi_light/pi_light.py:64`). Keep generated code small and controlled.
- **Circular imports:** `pi_light_code/env/TSC_env.py` imports `Intersection`, and `pi_light_code/env/intersection.py` imports `TSCEnv` for type/context use; this works in the current package layout but should not be deepened.
## Anti-Patterns
### Placing new OR experiments inside `pi_light_code/`
### Recomputing SUMO topology inside every recovery script
### Bypassing `TSCEnv` feature dispatch for CityFlow agents
## Error Handling
- Raise `RuntimeError` when SciPy LP fails (`scripts/run_dual_sanity.py:155`).
- Use status fields such as `PASSED`, `FAILED`, and `INCONCLUSIVE` in JSON payloads (`scripts/run_dual_sanity.py:348`, `scripts/run_sumo_sampled_recovery.py:194`, `scripts/run_sparse_recovery.py:299`).
- Use `try/finally` to close TraCI after SUMO sampling (`scripts/sample_sumo_states.py:78`, `scripts/sample_sumo_states.py:94`).
- Let `subprocess.run(..., check=True)` stop network generation when `netconvert` fails (`networks/arterial/create_network.py:361`).
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
