# Testing Patterns

**Analysis Date:** 2026/05/22

## Test Framework

**Runner:**
- No dedicated unit-test runner is configured. The quality scan found no `pytest.ini`, `tox.ini`, `pyproject.toml`, `jest.config.*`, `vitest.config.*`, `*.test.*`, `*.spec.*`, `test_*.py`, or `*_test.py` files under `/home/samuel/projects/pi_light_OR` outside ignored cache/venv paths.
- Current validation is script-based experiment gating through `scripts/run_dual_sanity.py`, `scripts/run_sumo_sampled_recovery.py`, `scripts/run_sparse_recovery.py`, and JSON artifacts in `experiments/dual_sensitivity/`.
- Config: Not detected for pytest/unittest. Gate parameters live in each script's `argparse` defaults, such as `scripts/run_dual_sanity.py:329-341` and `scripts/run_sparse_recovery.py:237-247`.

**Assertion Library:**
- Python built-in `assert` is used for internal invariants in upstream code, e.g. `pi_light_code/agent/imitation_based/imitate.py:90`, `pi_light_code/env/TSC_env.py:328`, and `pi_light_code/agent/pi_light/pi_light.py:32`.
- NumPy/SciPy outputs are checked through explicit boolean gates and status fields, not a test assertion library, as in `scripts/run_dual_sanity.py:345-350` and `scripts/run_sparse_recovery.py:286-299`.

**Run Commands:**
```bash
python scripts/run_dual_sanity.py                         # Block 0 LP dual sanity gate; writes experiments/dual_sensitivity/block0_dual_sanity.json
python scripts/sample_sumo_states.py --network arterial    # Sample SUMO/TraCI states for Block 1 inputs
python scripts/run_sumo_sampled_recovery.py                # SUMO sampled-state one-atom recovery gate
python scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json --out experiments/dual_sensitivity/block1_sparse_recovery_targeted.json  # Sparse MILP recovery gate
```

## Test File Organization

**Location:**
- Script-based validations live in `scripts/` and write artifacts to `experiments/dual_sensitivity/`.
- Human-readable gate interpretation lives in `refine-logs/EXPERIMENT_RESULTS.md` and progress tracking lives in `refine-logs/EXPERIMENT_TRACKER.md`.
- Upstream PI-Light evaluation runners live in `pi_light_code/00_run_tiny_light.py`, `pi_light_code/01_run_baseline.py`, `pi_light_code/02_run_MCTS.py`, `pi_light_code/03_run_viper.py`, and `pi_light_code/015_baseline_transfer.py`.

**Naming:**
- Gate scripts use verb-object snake_case names: `scripts/run_dual_sanity.py`, `scripts/run_offline_recovery_pilot.py`, `scripts/run_sumo_sampled_recovery.py`, `scripts/run_sparse_recovery.py`, and `scripts/generate_targeted_bottleneck_states.py`.
- Output artifacts use block and purpose names: `experiments/dual_sensitivity/block0_dual_sanity.json`, `experiments/dual_sensitivity/block1_sumo_sampled_recovery.json`, and `experiments/dual_sensitivity/block1_sparse_recovery_targeted.json`.

**Structure:**
```
scripts/
├── run_dual_sanity.py              # Block 0 deterministic LP sanity checks
├── sample_sumo_states.py           # SUMO/TraCI state sampler
├── run_sumo_sampled_recovery.py    # One-atom recovery gate on sampled states
└── run_sparse_recovery.py          # Sparse MILP recovery gate
experiments/dual_sensitivity/
├── block0_dual_sanity.json
├── block1_sumo_sampled_recovery.json
├── block1_sparse_recovery_targeted.json
└── block1_sparse_recovery_combined.json
```

## Test Structure

**Suite Organization:**
```python
# Pattern from scripts/run_dual_sanity.py
results = [summarize_scenario(build_scenario(name), args.epsilon) for name in args.scenarios]
gate_a_pass = all(
    r["rank_match_finite_difference"] and r["pressure_special_case_pass"] for r in results
)
payload = {"experiment": "block0_dual_sanity", "status": "PASSED" if gate_a_pass else "FAILED", "results": results}
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
if not gate_a_pass:
    raise SystemExit(1)
```

**Patterns:**
- Build deterministic scenarios in code, matching `scripts/run_dual_sanity.py:35-96` (`build_scenario`).
- Compute oracle/model summaries through pure functions, matching `scripts/run_dual_sanity.py:282-325` (`summarize_scenario`) and `scripts/run_sparse_recovery.py:49-98` (`build_example`).
- Aggregate boolean gates in `main()`, then persist a JSON payload, matching `scripts/run_dual_sanity.py:344-362`, `scripts/run_sumo_sampled_recovery.py:168-215`, and `scripts/run_sparse_recovery.py:286-343`.
- Print a compact JSON status object at the end, matching `scripts/run_sparse_recovery.py:343`.

## Mocking

**Framework:** Not detected.

**Patterns:**
```python
# Prefer deterministic proxy scenarios instead of mocks, as in scripts/run_dual_sanity.py
scenario = build_scenario("arterial_bottleneck_proxy")
summary = summarize_scenario(scenario, eps=1e-3)
```

**What to Mock:**
- Avoid mocks for optimization math; use deterministic proxy scenarios in `scripts/run_dual_sanity.py`.
- If a future unit-test suite is added, isolate SUMO/TraCI boundaries by passing sampled JSON from `experiments/dual_sensitivity/arterial_sampled_states.json` into functions such as `scripts/run_sumo_sampled_recovery.py:21` (`scenario_from_sample`).

**What NOT to Mock:**
- Do not mock `scipy.optimize.linprog` or `scipy.optimize.milp` in gate tests; these solvers are part of the validation target in `scripts/run_dual_sanity.py:146-154` and `scripts/run_sparse_recovery.py:180-186`.
- Do not mock JSON output creation in gate scripts; downstream research logs and planning consume `experiments/dual_sensitivity/*.json` artifacts.

## Fixtures and Factories

**Test Data:**
```python
# Pattern from scripts/run_dual_sanity.py
Scenario(
    name="toy_storage_binding",
    links=["up_a", "up_b", "down_a", "down_b"],
    movements=[(0, 2), (1, 3)],
    queue=np.array([18.0, 9.0, 80.0, 3.0]),
    downstream_capacity=np.array([80.0, 80.0, 80.0, 80.0]),
    storage_penalty=np.array([0.0, 0.0, 25.0, 0.0]),
)
```

**Location:**
- In-code fixtures: `scripts/run_dual_sanity.py:35-96` defines proxy scenarios.
- Generated state fixtures: `experiments/dual_sensitivity/arterial_sampled_states.json` and `experiments/dual_sensitivity/targeted_bottleneck_states.json`.
- Network-generation fixtures: `networks/single_intersection/create_network.py`, `networks/arterial/create_network.py`, and `networks/grid_4x4/create_network.py` generate SUMO network assets.

## Coverage

**Requirements:** None enforced.

**View Coverage:**
```bash
# Not available: no coverage tool/config detected in /home/samuel/projects/pi_light_OR
```

## Test Types

**Unit Tests:**
- Not implemented as `pytest`/`unittest` tests.
- Closest equivalent: deterministic pure-function checks in `scripts/run_dual_sanity.py`, especially `solve_relaxation`, `finite_difference_service_values`, `ranking`, and `summarize_scenario`.

**Integration Tests:**
- SUMO/TraCI integration is exercised by `scripts/sample_sumo_states.py`, which calls `sumolib.net.readNet` in `build_network_metadata` and `traci.start` in `sample_states`.
- Sparse recovery integration is exercised by `scripts/run_sparse_recovery.py`, which imports summaries from `scripts/run_dual_sanity.py` and sampled-state conversion from `scripts/run_sumo_sampled_recovery.py`.
- Upstream closed-loop PI-Light/CityFlow evaluation is script-driven through `pi_light_code/01_run_baseline.py` and `pi_light_code/02_run_MCTS.py`.

**E2E Tests:**
- No automated E2E test framework is detected.
- Manual/research E2E path: generate networks in `networks/`, sample SUMO states via `scripts/sample_sumo_states.py`, run recovery gates via `scripts/run_sumo_sampled_recovery.py` and `scripts/run_sparse_recovery.py`, then record status in `refine-logs/EXPERIMENT_RESULTS.md`.

## Common Patterns

**Async Testing:**
```python
# No async code detected. Parallel experiment runs use multiprocessing instead.
with multiprocessing.Pool(processes=num_concurrent_p) as pool:
    n_return_value = pool.starmap(run_an_experiment, [(data_name, f_idx, seed_list[f_idx]) for f_idx in range(total_run)])
```
- Multiprocessing pattern appears in `pi_light_code/01_run_baseline.py:90-97` and `pi_light_code/02_run_MCTS.py:108-115`.

**Error Testing:**
```python
# Pattern from scripts/run_dual_sanity.py
if not res.success:
    raise RuntimeError(f"LP failed for {s.name}: {res.message}")

if not gate_a_pass:
    raise SystemExit(1)
```
- Solver failure is converted to explicit exceptions in `scripts/run_dual_sanity.py:155-156`.
- Gate failure exits nonzero after writing the artifact in `scripts/run_dual_sanity.py:359-364`.
- MILP failure is captured as a structured result rather than an exception in `scripts/run_sparse_recovery.py:188-195`.

## Evidence Artifacts

- `experiments/dual_sensitivity/block0_dual_sanity.json:1-7` reports `status: PASSED` and criteria for dual rank and pressure special-case checks.
- `experiments/dual_sensitivity/block1_sparse_recovery_targeted.json:1-13` reports `status: PASSED`, `num_examples: 16`, and `gate_dual_budget1_beats_raw: true`.
- `refine-logs/EXPERIMENT_RESULTS.md:157-160` summarizes Gate A and Gate B as passed for current offline validation scope.

---

*Testing analysis: 2026/05/22*
