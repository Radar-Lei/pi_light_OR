# External Integrations

**Analysis Date:** 2026/05/22

## APIs & External Services

**Traffic Simulation:**
- SUMO CLI - used to run microscopic traffic simulation from `.sumocfg` files.
  - SDK/Client: `traci`, `sumolib`, command-line `sumo`
  - Auth: Not applicable
  - Evidence: `scripts/sample_sumo_states.py` starts `sumo -c <sumocfg>` through `traci.start(cmd)` and samples edge queues with `traci.edge.*` APIs.
- SUMO netconvert - used to compile network definitions.
  - SDK/Client: command-line `netconvert`
  - Auth: Not applicable
  - Evidence: `networks/arterial/create_network.py`, `networks/grid_4x4/create_network.py`, and `networks/single_intersection/create_network.py` invoke `netconvert` through `subprocess.run(...)`.
- CityFlow - original PI-Light traffic simulator.
  - SDK/Client: `cityflow` Python package
  - Auth: Not applicable
  - Evidence: `pi_light_code/env/TSC_env.py` creates `cityflow.Engine(json_str, thread_num=...)`; original dependency is documented in `pi_light_code/readme.md`.

**Optimization:**
- SciPy/HiGHS - current LP/MILP backend for dual sanity checks and sparse recovery.
  - SDK/Client: `scipy.optimize.linprog(method="highs")`, `scipy.optimize.milp`, `scipy.sparse.coo_matrix`
  - Auth: Not applicable
  - Evidence: `scripts/run_dual_sanity.py` and `scripts/run_sparse_recovery.py`.
- AMPL/HiGHS - planned/optional OR backend referenced in project notes.
  - SDK/Client: AMPL / `amplpy` when installed
  - Auth: AMPL license is intentionally kept outside this repository
  - Evidence: `refine-logs/EXPERIMENT_RESULTS.md` states `amplpy` is not installed in the current environment and AMPL setup notes must not be committed.

**Machine Learning / Program Synthesis:**
- PyTorch - neural TSC baselines and tensor-based observation/reward handling.
  - SDK/Client: `torch`
  - Auth: Not applicable
  - Evidence: `pi_light_code/agent/drl_based/*.py`, `pi_light_code/agent/tiny_light/*.py`, `pi_light_code/replay_buffer/replay_buffer.py`, and `pi_light_code/env/TSC_env.py`.
- scikit-optimize - Bayesian optimization inside PI-Light MCTS program synthesis.
  - SDK/Client: `skopt.gp_minimize`, `skopt.space.Real`, `skopt.space.Integer`
  - Auth: Not applicable
  - Evidence: `pi_light_code/agent/pi_light/MCTS.py`.
- scikit-learn / Graphviz - VIPER decision tree policy distillation and visualization.
  - SDK/Client: `sklearn.tree.DecisionTreeClassifier`, `export_graphviz`, `graphviz.Source`
  - Auth: Not applicable
  - Evidence: `pi_light_code/agent/imitation_based/dt.py`.

## Data Storage

**Databases:**
- Not detected.
  - Connection: Not applicable
  - Client: Not applicable

**File Storage:**
- Local filesystem only.
  - SUMO networks: `networks/single_intersection/`, `networks/arterial/`, `networks/grid_4x4/`, `networks/chengdu/`.
  - Original CityFlow datasets: `pi_light_code/data/*/roadnet.json` and `pi_light_code/data/*/flow*.json`.
  - Experiment outputs: `experiments/dual_sensitivity/*.json`.
  - Research planning and results: `idea-stage/*.md` and `refine-logs/*.md`.

**Caching:**
- In-memory only.
  - `pi_light_code/env/TSC_env.py` maintains metric caches such as `_cache_queue_length`, `_cache_average_delay`, and `_cache_throughput` during episodes.
  - No Redis/Memcached/external cache detected.

## Authentication & Identity

**Auth Provider:**
- Not applicable.
  - Implementation: no web service, user identity, login flow, or external auth provider detected.

## Monitoring & Observability

**Error Tracking:**
- None detected.

**Logs:**
- Console output and local files.
  - PI-Light runners log experiment summaries under `pi_light_code/log/...` via helper functions in `pi_light_code/utilities/utils.py` and runner scripts such as `pi_light_code/02_run_MCTS.py`.
  - SUMO/network creation scripts print generated file paths and warnings, for example `networks/arterial/create_network.py` prints `netconvert` warnings and output locations.
  - Experiment scripts write structured JSON status payloads under `experiments/dual_sensitivity/`.

## CI/CD & Deployment

**Hosting:**
- None detected; local research repository only.

**CI Pipeline:**
- None detected; no `.github/`, workflow files, or CI config found.

## Environment Configuration

**Required env vars:**
- Not detected in source code.
- SUMO executables (`sumo`, `netconvert`) must be on `PATH` for scripts under `scripts/` and `networks/`.
- Python import path/working directory matters for scripts that import sibling modules, such as `scripts/run_sumo_sampled_recovery.py` importing `run_dual_sanity`.

**Secrets location:**
- No committed secrets detected.
- `.env` and `.env.*` are ignored by `.gitignore`; do not read or commit their contents if created.
- AMPL license/setup notes are explicitly outside the repository per `refine-logs/EXPERIMENT_RESULTS.md`; do not commit license IDs or activation commands.

## Webhooks & Callbacks

**Incoming:**
- None detected.

**Outgoing:**
- None detected.

---

*Integration audit: 2026/05/22*
