# Codebase Structure

**Analysis Date:** 2026/05/22

## Directory Layout

```
/home/samuel/projects/pi_light_OR/
├── scripts/                 # OR/SUMO experiment drivers and recovery pipeline
├── experiments/             # Generated experiment artifacts, primarily JSON outputs
│   └── dual_sensitivity/    # Block 0/1 dual-sensitivity state and result files
├── networks/                # SUMO networks, routes, TLS configs, and network generators
│   ├── single_intersection/ # Single-junction SUMO case
│   ├── arterial/            # 5-intersection arterial SUMO case
│   ├── grid_4x4/            # 16-intersection grid SUMO case
│   └── chengdu/             # Chengdu SUMO case assets
├── pi_light_code/           # Original PI-Light/CityFlow implementation and baselines
│   ├── agent/               # Rule-based, DRL, TinyLight, PI-Light, imitation agents
│   ├── env/                 # CityFlow environment, intersections, roads, phases
│   ├── utilities/           # Config, logging, seeding, episode runners
│   ├── replay_buffer/       # DRL replay buffer
│   └── data/                # CityFlow benchmark roadnet/flow JSON datasets
├── refine-logs/             # Research plans, results, proposal, tracker documents
├── idea-stage/              # Idea discovery, novelty checks, external reviews
├── pi_light_original_paper/ # PI-Light paper text/images
├── Programmatically_Interpretable_Reinforcement_Learning_original_paper/ # PIRL LaTeX source
├── INFORMS-TRSC-Template-5-6-2025/ # Journal template files
└── .planning/codebase/      # Generated codebase maps
```

## Directory Purposes

**`scripts/`:**
- Purpose: Current OR research experiment implementation for dual-sensitivity and symbolic recovery.
- Contains: Standalone Python CLIs with `argparse`, SciPy LP/MILP code, SUMO state sampling, targeted state generation.
- Key files: `scripts/run_dual_sanity.py`, `scripts/sample_sumo_states.py`, `scripts/generate_targeted_bottleneck_states.py`, `scripts/run_sumo_sampled_recovery.py`, `scripts/run_sparse_recovery.py`, `scripts/run_offline_recovery_pilot.py`

**`experiments/dual_sensitivity/`:**
- Purpose: Persist inputs and outputs for Block 0/1 dual-sensitivity experiments.
- Contains: Sampled state JSON, targeted synthetic state JSON, sanity/recovery result JSON.
- Key files: `experiments/dual_sensitivity/block0_dual_sanity.json`, `experiments/dual_sensitivity/arterial_sampled_states.json`, `experiments/dual_sensitivity/targeted_bottleneck_states.json`, `experiments/dual_sensitivity/block1_sparse_recovery_combined.json`

**`networks/`:**
- Purpose: SUMO network scenarios used by OR experiments.
- Contains: `create_network.py` generators, `.nod.xml`, `.edg.xml`, `.net.xml`, `.rou.xml`, `.add.xml`, `.sumocfg` files.
- Key files: `networks/arterial/create_network.py`, `networks/grid_4x4/create_network.py`, `networks/single_intersection/create_network.py`, `networks/chengdu/chengdu.sumocfg`

**`pi_light_code/`:**
- Purpose: PI-Light source code and CityFlow benchmark runner copied/adapted from the original project.
- Contains: Agent implementations, CityFlow environment, benchmark data, run scripts, configuration.
- Key files: `pi_light_code/config.json`, `pi_light_code/00_run_tiny_light.py`, `pi_light_code/01_run_baseline.py`, `pi_light_code/02_run_MCTS.py`, `pi_light_code/03_run_viper.py`

**`pi_light_code/agent/`:**
- Purpose: Traffic signal controller implementations.
- Contains: Common `BaseAgent`, DRL agents, rule-based baselines, TinyLight, PI-Light DSL/MCTS, imitation/VIPER.
- Key files: `pi_light_code/agent/base_agent.py`, `pi_light_code/agent/__init__.py`, `pi_light_code/agent/rule_based/max_pressure.py`, `pi_light_code/agent/pi_light/pi_light.py`, `pi_light_code/agent/pi_light/program.py`, `pi_light_code/agent/pi_light/MCTS.py`

**`pi_light_code/env/`:**
- Purpose: CityFlow simulation adapter and network object model.
- Contains: Environment class, intersection phase state machine, roads, road links, phases.
- Key files: `pi_light_code/env/TSC_env.py`, `pi_light_code/env/intersection.py`, `pi_light_code/env/road.py`, `pi_light_code/env/road_link.py`, `pi_light_code/env/phase.py`

**`pi_light_code/utilities/`:**
- Purpose: Common runtime utilities for PI-Light runs.
- Contains: Config loading, logging setup, seeding, thread control, episode loops.
- Key files: `pi_light_code/utilities/utils.py`, `pi_light_code/utilities/snippets.py`, `pi_light_code/utilities/setup.py`

**`pi_light_code/data/`:**
- Purpose: CityFlow roadnet and flow datasets for original PI-Light benchmarks.
- Contains: Dataset directories such as `Atlanta`, `Hangzhou1`, `Hangzhou2`, `Jinan`, `LosAngeles`, `Manhattan`, each with `roadnet.json` and `flow_*.json`.
- Key files: `pi_light_code/data/Hangzhou2/roadnet.json`, `pi_light_code/data/Hangzhou2/flow_0.json`

**`refine-logs/` and `idea-stage/`:**
- Purpose: Research planning, external reviews, experiment trackers, and proposal documents.
- Contains: Markdown research artifacts; not execution code.
- Key files: `refine-logs/EXPERIMENT_PLAN.md`, `refine-logs/EXPERIMENT_RESULTS.md`, `refine-logs/FINAL_PROPOSAL.md`, `idea-stage/IDEA_REPORT.md`

## Key File Locations

**Entry Points:**
- `scripts/run_dual_sanity.py`: Block 0 LP/dual sanity checks.
- `scripts/sample_sumo_states.py`: SUMO/TraCI queue-state sampler.
- `scripts/generate_targeted_bottleneck_states.py`: Synthetic arterial bottleneck-state generator.
- `scripts/run_sumo_sampled_recovery.py`: Block 1 sampled-state equal-complexity recovery pilot.
- `scripts/run_sparse_recovery.py`: SciPy/HiGHS sparse atom-selection MILP.
- `pi_light_code/00_run_tiny_light.py`: TinyLight training/evaluation entry point.
- `pi_light_code/01_run_baseline.py`: Baseline controller training/evaluation entry point.
- `pi_light_code/02_run_MCTS.py`: PI-Light MCTS synthesis/evaluation entry point.
- `pi_light_code/03_run_viper.py`: VIPER imitation baseline entry point.

**Configuration:**
- `pi_light_code/config.json`: CityFlow/PI-Light base config, feature lists, reward lists, metric lists, hyperparameters.
- `networks/*/*.sumocfg`: SUMO simulation configs for each network.
- `.gitignore`: Ignore rules for generated/local artifacts.

**Core Logic:**
- `scripts/run_dual_sanity.py`: `Scenario` dataclass, LP construction, dual extraction, finite differences.
- `scripts/run_sparse_recovery.py`: Atom libraries, example loading, normalized tensors, MILP formulation.
- `pi_light_code/env/TSC_env.py`: CityFlow environment, feature dispatch, observations, rewards, metrics.
- `pi_light_code/env/intersection.py`: Per-intersection phase/yellow timing and topology indexing.
- `pi_light_code/agent/pi_light/program.py`: PI-Light DSL and complexity model.
- `pi_light_code/agent/pi_light/pi_light.py`: Runtime execution of synthesized DSL snippets.
- `pi_light_code/agent/rule_based/max_pressure.py`: Max-pressure baseline control logic.

**Testing:**
- Dedicated test directory not detected.
- Current validation is experiment-gate based in `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`, and `scripts/run_sparse_recovery.py`.
- Result evidence lives in `experiments/dual_sensitivity/*.json`.

**Research/Paper Materials:**
- `refine-logs/EXPERIMENT_TRACKER.md`: Experiment status tracking.
- `refine-logs/PIPELINE_SUMMARY.md`: Pipeline summary.
- `refine-logs/THEORY_AND_ATOMS.md`: Theory/DSL atom notes.
- `INFORMS-TRSC-Template-5-6-2025/INFORMS-TRSC-Template.tex`: Transportation Science template source.

## Naming Conventions

**Files:**
- Experiment scripts use verb phrases with snake_case: `scripts/run_dual_sanity.py`, `scripts/sample_sumo_states.py`, `scripts/generate_targeted_bottleneck_states.py`.
- Generated experiment results use block/scenario identifiers: `experiments/dual_sensitivity/block1_sparse_recovery_combined.json`.
- SUMO assets share a scenario prefix: `networks/arterial/arterial.net.xml`, `networks/arterial/arterial.rou.xml`, `networks/arterial/arterial.sumocfg`.
- PI-Light driver scripts use numeric prefixes: `pi_light_code/01_run_baseline.py`, `pi_light_code/02_run_MCTS.py`.
- Agent implementation modules are snake_case except copied/acronym modules such as `pi_light_code/agent/pi_light/MCTS.py`.

**Directories:**
- Research experiment outputs are grouped by topic: `experiments/dual_sensitivity/`.
- SUMO network directories are scenario names: `networks/arterial/`, `networks/grid_4x4/`, `networks/single_intersection/`, `networks/chengdu/`.
- PI-Light agents are grouped by method family: `pi_light_code/agent/rule_based/`, `pi_light_code/agent/drl_based/`, `pi_light_code/agent/pi_light/`, `pi_light_code/agent/imitation_based/`, `pi_light_code/agent/tiny_light/`.

## Where to Add New Code

**New OR/SUMO experiment block:**
- Primary code: `scripts/run_<experiment_name>.py`
- Inputs/outputs: `experiments/dual_sensitivity/<block_or_experiment_name>.json`
- Reuse: Import `Scenario`/`summarize_scenario` from `scripts/run_dual_sanity.py`; import `scenario_from_sample` from `scripts/run_sumo_sampled_recovery.py` when consuming sampled states.

**New SUMO state sampler or topology utility:**
- Primary code: `scripts/<sampler_or_generator>.py`
- Network inputs: `networks/<scenario>/<scenario>.sumocfg` and `networks/<scenario>/<scenario>.net.xml`
- Outputs: `experiments/dual_sensitivity/<scenario>_<description>_states.json`

**New SUMO network scenario:**
- Generator: `networks/<scenario>/create_network.py`
- Assets: `networks/<scenario>/<scenario>.nod.xml`, `networks/<scenario>/<scenario>.edg.xml`, `networks/<scenario>/<scenario>.net.xml`, `networks/<scenario>/<scenario>.rou.xml`, `networks/<scenario>/<scenario>.sumocfg`
- Follow the two-pass `netconvert` + TLS adjustment pattern in `networks/arterial/create_network.py` or `networks/grid_4x4/create_network.py`.

**New CityFlow/PI-Light controller:**
- Agent implementation: `pi_light_code/agent/<family>/<agent_name>.py`
- Registry exports: `pi_light_code/agent/__init__.py`
- Factory mapping: `pi_light_code/utilities/utils.py::get_agent`
- Config section: `pi_light_code/config.json`
- Driver: use `pi_light_code/01_run_baseline.py` pattern unless the method needs a dedicated entry point.

**New CityFlow observation/reward/metric feature:**
- Implementation: add a method to `pi_light_code/env/TSC_env.py`.
- Dispatch registration: add the feature name to `TSCEnv._info_functions` in `pi_light_code/env/TSC_env.py`.
- Configuration: reference the feature in the relevant agent section of `pi_light_code/config.json`.

**New PI-Light DSL atom or constraint:**
- DSL definition: `pi_light_code/agent/pi_light/program.py`.
- Runtime semantics: `pi_light_code/agent/pi_light/pi_light.py` if emitted code needs new observation variables.
- Config feature list: `pi_light_code/config.json` under `PiLight.observation_feature_list`.

**New paper/refinement note:**
- Current planning documents: `refine-logs/`.
- Idea-stage or review documents: `idea-stage/`.
- Do not place executable code in `refine-logs/` or `idea-stage/`.

**Utilities:**
- OR/SUMO reusable helpers: keep small helper functions in the consuming `scripts/*.py` module unless used by multiple scripts; shared state/topology helpers currently live in `scripts/sample_sumo_states.py`.
- PI-Light runtime utilities: `pi_light_code/utilities/utils.py` for config/logging/seeding; `pi_light_code/utilities/snippets.py` for episode loop helpers.

## Special Directories

**`experiments/dual_sensitivity/`:**
- Purpose: Generated experiment states and results.
- Generated: Yes
- Committed: Present in working tree as JSON artifacts.

**`networks/*/`:**
- Purpose: SUMO network definitions and generated simulation assets.
- Generated: Partially; `create_network.py` regenerates XML for synthetic scenarios.
- Committed: Present in working tree.

**`pi_light_code/data/`:**
- Purpose: CityFlow benchmark datasets used by original PI-Light scripts.
- Generated: No for normal runs; benchmark inputs are source data.
- Committed: Present in working tree.

**`pi_light_code/log/`:**
- Purpose: PI-Light runtime logs/models when `save_result` is enabled.
- Generated: Yes
- Committed: Not present in current file listing; should be treated as generated output.

**`pi_light_code/__pycache__/` and `scripts/__pycache__/`:**
- Purpose: Python bytecode cache.
- Generated: Yes
- Committed: Should not be committed or used as source evidence.

**`INFORMS-TRSC-Template-5-6-2025/`:**
- Purpose: Transportation Science LaTeX class/template and sample files.
- Generated: No
- Committed: Present in working tree.

**`.planning/codebase/`:**
- Purpose: Generated codebase maps used by GSD planning/execution workflows.
- Generated: Yes
- Committed: Intended to be tracked when codebase mapping is desired.

---

*Structure analysis: 2026/05/22*
