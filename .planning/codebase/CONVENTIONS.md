# Coding Conventions

**Analysis Date:** 2026/05/22

## Naming Patterns

**Files:**
- Use lowercase snake_case for new Python scripts and modules, matching `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, `scripts/sample_sumo_states.py`, and `networks/single_intersection/create_network.py`.
- Preserve upstream PI-Light numbered runner names in `pi_light_code/00_run_tiny_light.py`, `pi_light_code/01_run_baseline.py`, `pi_light_code/02_run_MCTS.py`, `pi_light_code/03_run_viper.py`, and `pi_light_code/015_baseline_transfer.py`; do not create new numbered runners unless extending that upstream experiment family.
- Use uppercase Markdown names for planning/research logs in `refine-logs/EXPERIMENT_RESULTS.md`, `refine-logs/EXPERIMENT_TRACKER.md`, and `refine-logs/THEORY_AND_ATOMS.md`.

**Functions:**
- Use snake_case for Python functions, as in `scripts/run_dual_sanity.py:35` (`build_scenario`), `scripts/run_dual_sanity.py:99` (`solve_relaxation`), `scripts/run_sparse_recovery.py:110` (`solve_library`), and `pi_light_code/utilities/utils.py:65` (`set_seed`).
- Put script orchestration in a `main() -> None` function and call it under `if __name__ == "__main__":`, matching `scripts/run_dual_sanity.py:328`, `scripts/run_sparse_recovery.py:236`, and `scripts/sample_sumo_states.py:99`.
- Upstream PI-Light runners use top-level `argparse` objects in `pi_light_code/01_run_baseline.py:9` and `pi_light_code/02_run_MCTS.py:10`; keep new OR pipeline scripts on the `main()` pattern used in `scripts/`.

**Variables:**
- Use snake_case for local variables and dictionaries, matching `scripts/run_sumo_sampled_recovery.py:21` (`scenario_from_sample`), `scripts/run_sparse_recovery.py:272` (`by_key`), and `pi_light_code/01_run_baseline.py:82` (`metrics`).
- Use short mathematical variable names only inside optimization formulations where they mirror the model, as in `scripts/run_dual_sanity.py:107` (`c`), `scripts/run_dual_sanity.py:113` (`a_eq`), and `scripts/run_sparse_recovery.py:131` (`c`).
- Use module-level constants in uppercase for experiment libraries or generated-network constants, matching `scripts/run_sparse_recovery.py:18` (`LIBRARIES`) and `networks/single_intersection/create_network.py:25` (`NETWORK_DIR`).

**Types:**
- Use dataclasses for structured optimization state, as in `scripts/run_dual_sanity.py:21` (`@dataclass(frozen=True) class Scenario`).
- Use PEP 585 type hints in new scripts, matching `scripts/run_dual_sanity.py:25` (`list[str]`), `scripts/run_sparse_recovery.py:29` (`list[Path]`), and `scripts/sample_sumo_states.py:26` (`dict[str, Any]`).
- Preserve untyped upstream PI-Light classes in `pi_light_code/agent/base_agent.py` and `pi_light_code/env/TSC_env.py` unless refactoring a whole module.

## Code Style

**Formatting:**
- No formatter configuration is detected: `find /home/samuel/projects/pi_light_OR -maxdepth 3` found no `pyproject.toml`, `.prettierrc`, `ruff.toml`, `setup.cfg`, or equivalent formatter files.
- Use 4-space indentation and PEP 8 spacing in new Python, matching `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, and `scripts/sample_sumo_states.py`.
- Keep generated XML string templates local to generator functions, matching `networks/single_intersection/create_network.py:28` (`write_nodes`) and `networks/single_intersection/create_network.py:63` (`write_routes`).

**Linting:**
- No linting configuration is detected: `find /home/samuel/projects/pi_light_OR -maxdepth 3` found no `.eslintrc*`, `eslint.config.*`, `biome.json`, `ruff.toml`, or `mypy.ini`.
- Prefer explicit exceptions in new code, matching `scripts/run_dual_sanity.py:155` (`raise RuntimeError(...)`) and avoid bare `except` patterns such as `pi_light_code/utilities/utils.py:94` unless preserving upstream behavior.
- Use assertions only for internal invariants, matching `pi_light_code/agent/pi_light/pi_light.py:32`; for CLI validation failures, raise `SystemExit(1)` or `ValueError`, matching `scripts/run_dual_sanity.py:96` and `scripts/run_dual_sanity.py:363`.

## Import Organization

**Order:**
1. Standard library imports first, matching `scripts/run_dual_sanity.py:10-15` (`argparse`, `json`, `math`, `dataclasses`, `pathlib`, `typing`).
2. Third-party imports next, matching `scripts/run_dual_sanity.py:17-18` (`numpy`, `scipy.optimize`) and `scripts/sample_sumo_states.py:16-17` (`sumolib`, `traci`).
3. Local imports last, matching `scripts/run_sparse_recovery.py:14-15` (`run_dual_sanity`, `run_sumo_sampled_recovery`) and `pi_light_code/01_run_baseline.py:1-2` (`env`, `utilities`).

**Path Aliases:**
- No package-level path alias is configured; scripts use direct imports from the working directory, such as `scripts/run_sparse_recovery.py:14` (`from run_dual_sanity import summarize_scenario`).
- Run OR scripts from the repository root or with `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts` when importing between files in `scripts/`.
- Run upstream PI-Light scripts from `pi_light_code/`, because `pi_light_code/utilities/utils.py:11` loads `config.json` relative to the current working directory.

## Error Handling

**Patterns:**
- Use fail-fast solver checks with informative messages, matching `scripts/run_dual_sanity.py:155-156` for LP failures and `scripts/run_sparse_recovery.py:188-195` for MILP failure payloads.
- For experiment gates, write a JSON artifact and exit nonzero only when the gate is truly failed, matching `scripts/run_dual_sanity.py:359-364`.
- For optional/invalid sampled scenarios, return `None` and skip, matching `scripts/run_sumo_sampled_recovery.py:21-34` and `scripts/run_sumo_sampled_recovery.py:161-164`.

## Logging

**Framework:** console plus optional Python logging.

**Patterns:**
- New OR scripts print compact JSON status objects, matching `scripts/run_dual_sanity.py:362`, `scripts/run_sparse_recovery.py:343`, and `scripts/sample_sumo_states.py:133`.
- Upstream PI-Light experiments configure `logging` with stream/file handlers in `pi_light_code/utilities/utils.py:35-56` and release handlers in `pi_light_code/utilities/utils.py:59-63`; use this when extending `pi_light_code/` runners.
- Network generators use direct `print()` progress output, matching `networks/single_intersection/create_network.py:195-198` and `networks/arterial/create_network.py:465-496`.

## Comments

**When to Comment:**
- Use docstrings at the top of standalone scripts to state scope and caveats, matching `scripts/run_dual_sanity.py:1-7`, `scripts/run_offline_recovery_pilot.py:1-7`, and `scripts/sample_sumo_states.py:1-6`.
- Use inline comments for model interpretation or paper caveats, matching `scripts/run_sumo_sampled_recovery.py:41` and `refine-logs/EXPERIMENT_RESULTS.md:40-43`.
- Avoid relying on comments to document known bugs in executable paths; `pi_light_code/env/TSC_env.py:363` contains a Chinese bug note and should be converted into an issue/test before changing behavior.

**JSDoc/TSDoc:**
- Not applicable; no JavaScript/TypeScript code is detected under `/home/samuel/projects/pi_light_OR`.

## Function Design

**Size:**
- Prefer small, single-purpose functions in new scripts, matching `scripts/run_dual_sanity.py:35` (`build_scenario`), `scripts/run_dual_sanity.py:99` (`solve_relaxation`), and `scripts/run_dual_sanity.py:282` (`summarize_scenario`).
- Large generator scripts in `networks/grid_4x4/create_network.py` and `networks/arterial/create_network.py` are acceptable for deterministic artifact generation; keep additions as separate helper functions rather than extending `__main__` blocks.

**Parameters:**
- Pass configuration through explicit CLI arguments using `argparse`, matching `scripts/run_sparse_recovery.py:237-247`, `scripts/sample_sumo_states.py:100-106`, and `pi_light_code/01_run_baseline.py:9-12`.
- Use `Path` for new file path parameters, matching `scripts/run_sparse_recovery.py:29` and `scripts/sample_sumo_states.py:26`; upstream `pi_light_code/` uses `os.path` and can stay consistent within that subtree.

**Return Values:**
- Return dictionaries that are JSON-serializable for experiment summaries, matching `scripts/run_dual_sanity.py:173-185`, `scripts/run_sumo_sampled_recovery.py:130-146`, and `scripts/run_sparse_recovery.py:220-233`.
- Return numeric metric tuples only in upstream runner helpers, matching `pi_light_code/01_run_baseline.py:65-69` and `pi_light_code/02_run_MCTS.py:84-86`.

## Module Design

**Exports:**
- `scripts/` modules expose reusable pure functions plus a CLI `main()`, as in `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`, and `scripts/run_sparse_recovery.py`.
- `pi_light_code/agent/` exposes agent classes through `pi_light_code/agent/__init__.py`; use `pi_light_code/utilities/utils.py:19-32` (`get_agent`) instead of dynamic imports when selecting upstream agents.

**Barrel Files:**
- `pi_light_code/agent/__init__.py`, `pi_light_code/env/__init__.py`, and `pi_light_code/replay_buffer/__init__.py` are the only detected barrel-style package files; do not add barrel files in `scripts/`.

## Project Skills

- Not detected: `.claude/skills/` and `.agents/skills/` are absent or empty under `/home/samuel/projects/pi_light_OR` according to the project skill directory check.

---

*Convention analysis: 2026/05/22*
