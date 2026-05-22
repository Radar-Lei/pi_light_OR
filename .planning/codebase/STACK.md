# Technology Stack

**Analysis Date:** 2026/05/22

## Languages

**Primary:**
- Python 3 - experiment scripts and PI-Light code in `scripts/*.py`, `networks/*/create_network.py`, and `pi_light_code/**/*.py`.
  - Evidence: `python3 --version` reports `Python 3.14.4` on this machine.
  - Compatibility note: `pi_light_code/readme.md` declares the original PI-Light stack as `python=3.8.10`.

**Secondary:**
- XML - SUMO networks, routes, additional TLS programs, and SUMO configs in `networks/*/*.xml` and `networks/*/*.sumocfg`.
- JSON - configuration, CityFlow datasets, sampled states, and experiment outputs in `pi_light_code/config.json`, `pi_light_code/data/*/*.json`, and `experiments/dual_sensitivity/*.json`.
- LaTeX/BibTeX - reference paper/template sources in `Programmatically_Interpretable_Reinforcement_Learning_original_paper/*.tex` and `INFORMS-TRSC-Template-5-6-2025/*.tex`.
- C++ extension build scaffold - `pi_light_code/utilities/setup.py` builds any local `*.cpp` files as Python extensions with `distutils.core.Extension`.

## Runtime

**Environment:**
- Python 3.14.4 currently available on the host.
- Original PI-Light runtime targets Python 3.8.10 per `pi_light_code/readme.md`.
- SUMO 1.26.0 installed and usable; `sumo --version` reports `Eclipse SUMO sumo 1.26.0`.
- CPU-oriented experiments are the expected path: `refine-logs/EXPERIMENT_PLAN.md` lists SUMO/TraCI simulation, AMPL/HiGHS solves, and sparse MIP recovery as CPU-only work.

**Package Manager:**
- Not detected: no `requirements.txt`, `pyproject.toml`, `environment.yml`, `Pipfile`, or lockfile under `/home/samuel/projects/pi_light_OR`.
- Local virtual environment directory `.venv/` is ignored by `.gitignore`; do not commit it.
- Lockfile: missing.

## Frameworks

**Core:**
- SUMO 1.26.0 - microscopic traffic simulation for `networks/single_intersection`, `networks/arterial`, `networks/grid_4x4`, and `networks/chengdu`.
- TraCI / sumolib - Python control and network parsing in `scripts/sample_sumo_states.py` and `scripts/generate_targeted_bottleneck_states.py`.
- CityFlow 0.1.0 - original PI-Light simulator dependency declared in `pi_light_code/readme.md`; used directly by `pi_light_code/env/TSC_env.py` via `cityflow.Engine(...)`.
- PyTorch 1.7.1+cu110 - original PI-Light neural baseline dependency declared in `pi_light_code/readme.md`; imported by `pi_light_code/agent/drl_based/*.py`, `pi_light_code/agent/tiny_light/*.py`, and `pi_light_code/replay_buffer/replay_buffer.py`.

**Testing:**
- Not detected: no pytest/unittest config or dedicated test framework found.
- Validation is script-driven through experiment runners such as `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`, and `scripts/run_sparse_recovery.py`.

**Build/Dev:**
- SUMO `netconvert` - network compiler invoked from `networks/single_intersection/create_network.py`, `networks/arterial/create_network.py`, and `networks/grid_4x4/create_network.py`.
- SciPy HiGHS LP/MILP backends - `scripts/run_dual_sanity.py` uses `scipy.optimize.linprog(method="highs")`; `scripts/run_sparse_recovery.py` uses `scipy.optimize.milp` plus sparse matrices.
- scikit-optimize - PI-Light MCTS parameter optimization in `pi_light_code/agent/pi_light/MCTS.py` via `gp_minimize`, `Real`, and `Integer`.
- scikit-learn + Graphviz - VIPER/decision-tree imitation in `pi_light_code/agent/imitation_based/dt.py`.

## Key Dependencies

**Critical:**
- `traci` / `sumolib` - required for SUMO state sampling and movement metadata in `scripts/sample_sumo_states.py`.
- `scipy` - required for LP/MILP optimization in `scripts/run_dual_sanity.py` and `scripts/run_sparse_recovery.py`.
- `numpy` - numerical arrays and scoring throughout `scripts/*.py` and `pi_light_code/**/*.py`.
- `cityflow` - required by original PI-Light environment `pi_light_code/env/TSC_env.py`.
- `torch` - required by DRL, TinyLight, replay buffer, and observation/reward tensor conversion in `pi_light_code/**/*.py`.

**Infrastructure:**
- SUMO CLI tools: `sumo` for simulation and `netconvert` for compiling network XML.
- `gym` - action spaces and optional rendering in `pi_light_code/env/TSC_env.py`.
- `scikit-learn` - decision tree policy distillation in `pi_light_code/agent/imitation_based/dt.py`.
- `graphviz` - decision tree visualization in `pi_light_code/agent/imitation_based/dt.py`.
- `scikit-optimize` - Bayesian parameter search for PI-Light synthesized programs in `pi_light_code/agent/pi_light/MCTS.py`.

## Configuration

**Environment:**
- No `.env` file is present in the project root; `.env` and `.env.*` are ignored by `.gitignore`.
- Original PI-Light settings are centralized in `pi_light_code/config.json` with keys such as `interval`, `num_step`, `action_interval`, `device`, `engine_thread`, and agent-specific observation/reward/metric lists.
- SUMO network experiments use `.sumocfg` files under `networks/*/*.sumocfg` and generated XML route/network/additional files under `networks/*/`.
- Script outputs default to local JSON artifacts under `experiments/dual_sensitivity/`.

**Build:**
- `pi_light_code/utilities/setup.py` dynamically builds local C++ extension modules from `*.cpp` files when present.
- `networks/*/create_network.py` scripts generate `.nod.xml`, `.edg.xml`, `.net.xml`, `.rou.xml`, `.add.xml`, and `.sumocfg` artifacts using SUMO tools.
- No Python packaging/build config is detected at the repository root.

## Platform Requirements

**Development:**
- Install Python packages used by scripts and original PI-Light code: `numpy`, `scipy`, `traci`, `sumolib`, `torch`, `gym`, `scikit-learn`, `graphviz`, `scikit-optimize`, and `cityflow` where original PI-Light runs are needed.
- Install SUMO 1.26.0+ with `sumo` and `netconvert` available on `PATH`.
- Use local JSON/XML artifacts in `networks/`, `experiments/dual_sensitivity/`, and `pi_light_code/data/`; no database service is required.

**Production:**
- Not applicable: this is a research/experiment codebase, not a deployed service.
- Deployment target for experiments is local CPU execution with SUMO/TraCI and offline SciPy/HiGHS optimization.

---

*Stack analysis: 2026/05/22*
