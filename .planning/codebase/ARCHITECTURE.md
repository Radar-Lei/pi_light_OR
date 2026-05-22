<!-- refreshed: 2026/05/22 -->
# Architecture

**Analysis Date:** 2026/05/22

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                  Research Experiment Drivers                 │
├──────────────────────┬──────────────────────┬───────────────┤
│ OR dual/MILP scripts │ SUMO state samplers  │ PI-Light runs │
│ `scripts/*.py`       │ `scripts/sample_...` │ `pi_light_code/0*.py` │
└──────────┬───────────┴──────────┬───────────┴───────┬───────┘
           │                      │                   │
           ▼                      ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 Control / Optimization Layer                 │
│ `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py` │
│ `pi_light_code/agent/`, `pi_light_code/env/`                │
└──────────┬──────────────────────┬────────────────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────────┐  ┌────────────────────────────────────┐
│ SUMO network assets  │  │ CityFlow benchmark assets           │
│ `networks/`          │  │ `pi_light_code/data/*`              │
└──────────┬───────────┘  └──────────────┬─────────────────────┘
           │                             │
           ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│                 JSON outputs / paper artifacts               │
│ `experiments/dual_sensitivity/*.json`, `refine-logs/*.md`   │
└─────────────────────────────────────────────────────────────┘
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

**Overall:** Script-oriented research pipeline with two simulation backends.

**Key Characteristics:**
- Keep OR/SUMO experiments in `scripts/` and outputs in `experiments/dual_sensitivity/`; scripts use CLI arguments and write JSON via `Path(...).write_text(...)`.
- Keep original PI-Light/CityFlow code under `pi_light_code/`; driver scripts instantiate `TSCEnv`, populate `env.n_agent`, then call `utilities/snippets.py::run_an_episode`.
- Use data objects at layer boundaries: `Scenario` in `scripts/run_dual_sanity.py`, SUMO sample dictionaries from `scripts/sample_sumo_states.py`, CityFlow config dictionaries from `pi_light_code/config.json`.

## Layers

**Research orchestration layer:**
- Purpose: Launch reproducible experiment blocks and choose input/output artifacts.
- Location: `scripts/*.py`, `pi_light_code/00_run_tiny_light.py`, `pi_light_code/01_run_baseline.py`, `pi_light_code/02_run_MCTS.py`, `pi_light_code/03_run_viper.py`
- Contains: `argparse` CLIs, seed lists, loop structure, multiprocessing, file output paths.
- Depends on: OR utilities in `scripts/run_dual_sanity.py`, SUMO via `traci`, CityFlow via `TSCEnv`.
- Used by: Manual experiment runs and paper/refinement workflow.

**OR optimization layer:**
- Purpose: Turn traffic states into LP/MILP ranking/recovery problems.
- Location: `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, `scripts/run_sumo_sampled_recovery.py`
- Contains: `Scenario`, LP construction with `scipy.optimize.linprog`, finite-difference oracle construction, MILP atom selection with `scipy.optimize.milp`.
- Depends on: NumPy, SciPy, sampled state JSON, scenario dictionaries.
- Used by: Block 0 sanity checks and Block 1 sparse recovery experiments.

**SUMO network/data layer:**
- Purpose: Provide realistic traffic networks and sampled queue states for OR recovery experiments.
- Location: `networks/`, `experiments/dual_sensitivity/*.json`
- Contains: `.net.xml`, `.rou.xml`, `.sumocfg`, generated queue-state JSON files.
- Depends on: SUMO `netconvert`, `sumo`, `traci`, `sumolib`.
- Used by: `scripts/sample_sumo_states.py`, `scripts/generate_targeted_bottleneck_states.py`, recovery scripts.

**CityFlow environment layer:**
- Purpose: Emulate PI-Light benchmark simulation, observations, rewards, and metrics.
- Location: `pi_light_code/env/`
- Contains: `TSCEnv`, `Intersection`, `Road`, `RoadLink`, `Phase`.
- Depends on: CityFlow, Gym spaces, PyTorch tensor conversion for DRL agents.
- Used by: PI-Light and baseline run scripts under `pi_light_code/`.

**Agent/control layer:**
- Purpose: Convert observations into phase actions.
- Location: `pi_light_code/agent/`
- Contains: `BaseAgent`, rule-based controllers, DRL controllers, TinyLight, PI-Light DSL agent, MCTS synthesizer, imitation/VIPER policies.
- Depends on: `TSCEnv`, intersection topology, config-specified feature lists.
- Used by: `pi_light_code/00_run_tiny_light.py`, `pi_light_code/01_run_baseline.py`, `pi_light_code/02_run_MCTS.py`, `pi_light_code/03_run_viper.py`.

## Data Flow

### OR Dual-Sensitivity Recovery Path

1. Build proxy or sampled traffic states as `Scenario` values (`scripts/run_dual_sanity.py:21`, `scripts/run_sumo_sampled_recovery.py:21`).
2. Solve the no-service or service-constrained LP with `scipy.optimize.linprog` (`scripts/run_dual_sanity.py:99`, `scripts/run_dual_sanity.py:146`).
3. Extract equality/storage/green-budget marginals and movement values from solver output (`scripts/run_dual_sanity.py:161`, `scripts/run_dual_sanity.py:166`).
4. Compare dual rankings against finite-difference oracle and pressure rankings (`scripts/run_dual_sanity.py:282`).
5. Write structured JSON results into `experiments/dual_sensitivity/` (`scripts/run_dual_sanity.py:359`, `scripts/run_sumo_sampled_recovery.py:212`, `scripts/run_sparse_recovery.py:340`).

### SUMO State Sampling Path

1. Read a SUMO network with `sumolib.net.readNet` and infer TLS movements from `<connection tl=...>` metadata (`scripts/sample_sumo_states.py:26`, `scripts/sample_sumo_states.py:36`).
2. Start SUMO with TraCI using the selected `.sumocfg` (`scripts/sample_sumo_states.py:65`, `scripts/sample_sumo_states.py:76`).
3. Record queues and vehicle counts every sampling interval (`scripts/sample_sumo_states.py:79`, `scripts/sample_sumo_states.py:83`).
4. Persist samples, capacities, and TLS movements as JSON under `experiments/dual_sensitivity/` (`scripts/sample_sumo_states.py:119`, `scripts/sample_sumo_states.py:130`).

### PI-Light / CityFlow Control Path

1. Driver script loads `pi_light_code/config.json` through `utilities/utils.py::get_config` (`pi_light_code/utilities/utils.py:10`).
2. `TSCEnv` creates a CityFlow engine from the dumpable config and parses roads/intersections (`pi_light_code/env/TSC_env.py:21`, `pi_light_code/env/TSC_env.py:88`).
3. Run script creates one agent per intersection and stores it in `env.n_agent` (`pi_light_code/01_run_baseline.py:37`, `pi_light_code/01_run_baseline.py:39`).
4. `run_an_episode` repeatedly asks each agent for an action, calls `env.step`, optionally stores experience and learns (`pi_light_code/utilities/snippets.py:24`, `pi_light_code/utilities/snippets.py:35`).
5. `TSCEnv.step` applies intersection actions for `action_interval` simulation ticks, computes observations/rewards/done/info, and updates aggregate metrics (`pi_light_code/env/TSC_env.py:177`, `pi_light_code/env/TSC_env.py:188`).

**State Management:**
- OR scripts keep state local to dataclasses and dictionaries, then serialize results to JSON.
- SUMO state lives in the external TraCI simulation during sampling.
- CityFlow state lives in `TSCEnv.eng`, while current phase/time live in each `Intersection` (`pi_light_code/env/intersection.py:14`).
- Agent state includes current phase, learned network weights, and replay buffers depending on agent type.

## Key Abstractions

**Scenario:**
- Purpose: Minimal continuous traffic-control problem for LP dual sensitivity.
- Examples: `scripts/run_dual_sanity.py:21`, `scripts/run_sumo_sampled_recovery.py:46`
- Pattern: Frozen dataclass with links, movements, queues, capacities, demands, service capacities, and objective weights.

**SUMO sample dictionary:**
- Purpose: Persist simulation snapshots independent of TraCI runtime.
- Examples: `scripts/sample_sumo_states.py:85`, `scripts/generate_targeted_bottleneck_states.py:18`
- Pattern: Dictionary with `time`, `queues`, `vehicle_counts`, `capacities`, and `tls_movements`.

**TSCEnv:**
- Purpose: Multi-intersection CityFlow environment and feature/metric adapter.
- Examples: `pi_light_code/env/TSC_env.py:13`
- Pattern: Central environment class with `_info_functions` dispatch table mapping config feature names to computation methods (`pi_light_code/env/TSC_env.py:27`).

**BaseAgent:**
- Purpose: Common controller interface for one intersection.
- Examples: `pi_light_code/agent/base_agent.py:5`
- Pattern: `reset`, `pick_action`, `learn`, and `store_experience` methods; subclasses override action logic.

**PI-Light Program/Bale:**
- Purpose: Searchable DSL for interpretable inlane/outlane scoring programs.
- Examples: `pi_light_code/agent/pi_light/program.py:189`, `pi_light_code/agent/pi_light/program.py:349`
- Pattern: Tree of `Instruction`, `If`, `IfElse`, and `Block` objects that emits executable Python code snippets.

## Entry Points

**Block 0 dual sanity:**
- Location: `scripts/run_dual_sanity.py`
- Triggers: `python scripts/run_dual_sanity.py --out experiments/dual_sensitivity/block0_dual_sanity.json`
- Responsibilities: Validate dual rankings against finite-difference and pressure special cases.

**SUMO sampler:**
- Location: `scripts/sample_sumo_states.py`
- Triggers: `python scripts/sample_sumo_states.py --network arterial --out experiments/dual_sensitivity/arterial_sampled_states.json`
- Responsibilities: Generate SUMO queue-state samples for recovery scripts.

**Sparse recovery:**
- Location: `scripts/run_sparse_recovery.py`
- Triggers: `python scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json`
- Responsibilities: Solve atom-selection MILP and report realized regret/action agreement.

**PI-Light MCTS synthesis:**
- Location: `pi_light_code/02_run_MCTS.py`
- Triggers: `python 02_run_MCTS.py --dataset Hangzhou2` from `pi_light_code/`
- Responsibilities: Build `TSCEnv`, synthesize PI-Light code with `MCTS_synthesizer`, inject rules, and evaluate.

**Baseline evaluation/training:**
- Location: `pi_light_code/01_run_baseline.py`
- Triggers: `python 01_run_baseline.py --model MaxPressure --dataset Hangzhou2` from `pi_light_code/`
- Responsibilities: Instantiate baseline agents, train DRL agents when needed, evaluate metrics over 10 flows.

**SUMO network generation:**
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

**What happens:** New SUMO/LP/MILP experiments are placed beside CityFlow PI-Light run scripts.
**Why it's wrong:** `pi_light_code/` assumes CityFlow config/data layout and cwd-relative `config.json`; OR/SUMO experiments use different backends and artifacts.
**Do this instead:** Add OR/SUMO experiment drivers under `scripts/` and write results to `experiments/dual_sensitivity/`, following `scripts/run_sparse_recovery.py`.

### Recomputing SUMO topology inside every recovery script

**What happens:** Recovery code parses `.net.xml` or calls TraCI directly instead of consuming sampled state JSON.
**Why it's wrong:** It couples deterministic recovery to simulator runtime and duplicates topology extraction.
**Do this instead:** Use `scripts/sample_sumo_states.py::build_network_metadata` and sample JSON records, as `scripts/run_sumo_sampled_recovery.py` does.

### Bypassing `TSCEnv` feature dispatch for CityFlow agents

**What happens:** Agent code calls CityFlow engine methods directly for observations.
**Why it's wrong:** It bypasses config-controlled feature lists and breaks shared metrics/reward handling.
**Do this instead:** Add feature methods to `pi_light_code/env/TSC_env.py` and reference them in `pi_light_code/config.json`.

## Error Handling

**Strategy:** Fail fast in scripts, serialize status when experiment gates are inconclusive or failed.

**Patterns:**
- Raise `RuntimeError` when SciPy LP fails (`scripts/run_dual_sanity.py:155`).
- Use status fields such as `PASSED`, `FAILED`, and `INCONCLUSIVE` in JSON payloads (`scripts/run_dual_sanity.py:348`, `scripts/run_sumo_sampled_recovery.py:194`, `scripts/run_sparse_recovery.py:299`).
- Use `try/finally` to close TraCI after SUMO sampling (`scripts/sample_sumo_states.py:78`, `scripts/sample_sumo_states.py:94`).
- Let `subprocess.run(..., check=True)` stop network generation when `netconvert` fails (`networks/arterial/create_network.py:361`).

## Cross-Cutting Concerns

**Logging:** PI-Light drivers configure Python logging through `pi_light_code/utilities/utils.py::set_logger`; OR scripts print compact JSON summaries to stdout and write full artifacts.
**Validation:** OR validation uses ranking gates and realized-regret gates in `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`, and `scripts/run_sparse_recovery.py`; PI-Light mostly uses assertions and simulator/runtime failures.
**Authentication:** Not applicable; no auth layer detected.
**Reproducibility:** Use explicit seeds in scripts (`scripts/sample_sumo_states.py:105`, `pi_light_code/01_run_baseline.py:88`) and keep generated experiment outputs under `experiments/dual_sensitivity/`.
**Project skills:** No `.claude/skills/` or `.agents/skills/` directory detected in `/home/samuel/projects/pi_light_OR`.

---

*Architecture analysis: 2026/05/22*
