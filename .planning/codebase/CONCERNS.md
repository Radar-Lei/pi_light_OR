# Codebase Concerns

**Analysis Date:** 2026/05/22

## Tech Debt

**Offline OR pipeline remains separated from closed-loop controllers:**
- Issue: The dual-sensitivity scripts validate one-step LP/MILP recovery offline, while the executable PI-Light/CityFlow controller path remains the original `pi_light_code/` implementation. `scripts/run_sumo_sampled_recovery.py:4-7` states the sampled recovery is lightweight and does not implement full sparse MIP recovery; `refine-logs/EXPERIMENT_RESULTS.md:127-131` states the next step is closed-loop SUMO validation.
- Files: `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, `scripts/run_sumo_sampled_recovery.py`, `pi_light_code/agent/pi_light/pi_light.py`, `refine-logs/EXPERIMENT_RESULTS.md`
- Impact: Offline PASS results can be overstated as deployable controller evidence; new closed-loop experiments must bridge SUMO state sampling, recovered atoms, and online signal decisions explicitly.
- Fix approach: Add a single controller adapter that converts recovered atom weights from `scripts/run_sparse_recovery.py` into an online policy and evaluates it in SUMO networks under `networks/single_intersection/`, `networks/arterial/`, and `networks/grid_4x4/`.

**Research plan tracks several pending validation gates:**
- Issue: Gates C/D/E are pending: single-controller sanity, arterial closed-loop, grid/demand generality, robustness, and runtime remain TODO in `refine-logs/EXPERIMENT_TRACKER.md:16-26`; gate status confirms C/D/E pending in `refine-logs/EXPERIMENT_TRACKER.md:30-34`.
- Files: `refine-logs/EXPERIMENT_TRACKER.md`, `refine-logs/EXPERIMENT_RESULTS.md`
- Impact: Claims beyond dual validity and offline sparse recovery are not fully supported by current artifacts.
- Fix approach: Treat `refine-logs/EXPERIMENT_TRACKER.md` as the authoritative claim boundary; do not add paper claims for max-pressure dominance, robustness, or runtime until corresponding JSON outputs exist under `experiments/`.

**Original PI-Light code contains abstract no-op hooks and legacy scaffolding:**
- Issue: Base methods `learn()` and `store_experience()` are no-ops in `pi_light_code/agent/base_agent.py:26-30`; `PiLight.reset()` is a no-op in `pi_light_code/agent/pi_light/pi_light.py:27-28`; rule-based agents also expose pass-only resets according to `grep -RIn "pass$"` evidence.
- Files: `pi_light_code/agent/base_agent.py`, `pi_light_code/agent/pi_light/pi_light.py`, `pi_light_code/agent/rule_based/max_pressure.py`, `pi_light_code/agent/rule_based/sotl.py`
- Impact: New experiments can silently skip training/reset behavior and produce misleading comparisons if assumptions are not checked.
- Fix approach: For every new controller, implement explicit reset/learning semantics or document it as stateless; add smoke tests that assert state is reset between seeds.

## Known Bugs

**Single-intersection TLS phase states appear duplicated/mislabeled:**
- Symptoms: `networks/single_intersection/create_network.py:127-141` labels NS through, NS left, EW through, and EW left phases, but the green-state strings repeat (`GGgrrrGGgrrr` and `rrrGGgrrrGGg`) across different directions.
- Files: `networks/single_intersection/create_network.py`, `networks/single_intersection/single_intersection.add.xml`
- Trigger: Running fixed-time or TraCI controllers that rely on the generated additional TLS program for direction-specific phase semantics.
- Workaround: Inspect generated `networks/single_intersection/single_intersection.net.xml` connection ordering with SUMO tools before using this network for phase-specific claims; regenerate the TLS program from connection metadata rather than hand-coded strings.

**Unseeded stochastic components remain in legacy imitation/MCTS code:**
- Symptoms: `pi_light_code/agent/imitation_based/dt.py:13-20` shuffles train/test indices with global `np.random`; `pi_light_code/agent/pi_light/MCTS.py` uses random expansion/evaluation paths according to `grep -RIn "np.random\|random\."` evidence. These paths are only reproducible if callers invoke `utilities.utils.set_seed()` before every run.
- Files: `pi_light_code/agent/imitation_based/dt.py`, `pi_light_code/agent/pi_light/MCTS.py`, `pi_light_code/utilities/utils.py`
- Trigger: Running VIPer/MCTS/decision-tree baselines from `pi_light_code/02_run_MCTS.py` or `pi_light_code/03_run_viper.py` without strict seed setup.
- Workaround: Always call `pi_light_code/utilities/utils.py:66-77` seed setup before experiments and record seed lists in output JSON/logs.

## Security Considerations

**Dynamic `exec()` is used for generated PI-Light policies:**
- Risk: Generated code strings injected through `PiLight.inject_code()` execute directly in `pi_light_code/agent/pi_light/pi_light.py:51`, `pi_light_code/agent/pi_light/pi_light.py:55`, `pi_light_code/agent/pi_light/pi_light.py:65`, and `pi_light_code/agent/pi_light/pi_light.py:67`.
- Files: `pi_light_code/agent/pi_light/pi_light.py`, `pi_light_code/agent/pi_light/program.py`
- Current mitigation: Program strings are normally produced internally by `pi_light_code/agent/pi_light/program.py`, not from an external API.
- Recommendations: Do not execute untrusted recovered policies; replace `exec()` with a constrained AST/interpreter before exposing policy files as experiment inputs.

**Pickle model loading is unsafe for untrusted artifacts:**
- Risk: `pi_light_code/agent/imitation_based/dt.py:43-47` loads decision-tree policies with `pickle.load()`, which can execute arbitrary code when reading attacker-controlled files.
- Files: `pi_light_code/agent/imitation_based/dt.py`
- Current mitigation: Artifacts are local research outputs.
- Recommendations: Only load pickle files generated inside this repository; prefer JSON/joblib with validation for shareable experiment artifacts.

**Environment files are ignored but must not be committed:**
- Risk: `.gitignore:4-5` ignores `.env` and `.env.*`, while `refine-logs/EXPERIMENT_RESULTS.md:152-156` notes AMPL setup/license details stay outside the public repository.
- Files: `.gitignore`, `refine-logs/EXPERIMENT_RESULTS.md`
- Current mitigation: `.env` patterns are ignored.
- Recommendations: Keep AMPL license IDs, solver activation commands, and API credentials outside `refine-logs/`, `scripts/`, and `.planning/codebase/`.

## Performance Bottlenecks

**MILP recovery uses a fixed per-library time limit and dense pairwise ranking constraints:**
- Problem: `scripts/run_sparse_recovery.py:165-187` builds Big-M pairwise movement constraints and calls SciPy/HiGHS `milp()` with `options={"time_limit": 60.0}` for every library/budget run.
- Files: `scripts/run_sparse_recovery.py`
- Cause: Constraint count grows with examples × movements² × atoms; `--max-movements` defaults to 12 in `scripts/run_sparse_recovery.py:242`, and larger networks increase candidate movements.
- Improvement path: Cache normalized tensors, prune dominated/tied movement pairs, expose solver gap/status in summaries, and benchmark runtime for Gate E before scaling to Chengdu-sized networks.

**Large SUMO XML artifacts dominate repository size and manual inspection cost:**
- Problem: `wc -l` evidence shows `networks/chengdu/chengdu.rou.xml` has 29,697 lines and `networks/chengdu/chengdu.net.xml` has 20,229 lines.
- Files: `networks/chengdu/chengdu.rou.xml`, `networks/chengdu/chengdu.net.xml`
- Cause: Full generated route/network XML is committed as text.
- Improvement path: Keep generator scripts and compressed/metadata summaries for large scenarios; inspect Chengdu files with targeted XML parsing instead of full-file reads.

**CityFlow environment recomputes all-pairs neighbor relations at initialization:**
- Problem: `pi_light_code/env/TSC_env.py:106-113` loops over every pair of intersections to populate neighbor indices.
- Files: `pi_light_code/env/TSC_env.py`
- Cause: O(n²) neighbor discovery is acceptable for small benchmark maps but grows poorly for larger networks.
- Improvement path: Build adjacency from parsed road links once and cache it in the roadnet metadata.

## Fragile Areas

**SUMO sampled states are converted through simplified capacity/service assumptions:**
- Files: `scripts/sample_sumo_states.py`, `scripts/run_sumo_sampled_recovery.py`
- Why fragile: `scripts/sample_sumo_states.py:21-24` estimates capacity from length × lanes / jam spacing; `scripts/run_sumo_sampled_recovery.py:40-46` sets queue weights, storage penalties, service capacity, and green budget by simple formulas rather than calibrated phase constraints.
- Safe modification: Keep these formulas centralized and record them in every experiment payload; validate sensitivity to `jam_spacing_m`, service capacity, storage threshold, and green budget before making robustness claims.
- Test coverage: No detected automated tests; validation is by generated JSON under `experiments/dual_sensitivity/`.

**Network generator scripts overwrite generated XML in-place:**
- Files: `networks/single_intersection/create_network.py`, `networks/arterial/create_network.py`, `networks/grid_4x4/create_network.py`
- Why fragile: Generators write directly to committed files such as `*.nod.xml`, `*.edg.xml`, `*.net.xml`, `*.rou.xml`, `*.add.xml`, and `*.sumocfg`; accidental reruns can change experiment baselines.
- Safe modification: Run generators only from a clean working tree and diff generated XML before accepting changes; pin SUMO/netconvert versions in experiment logs.
- Test coverage: No detected regression tests compare generated topology/phase semantics across SUMO versions.

**Logger and output directory helpers mutate existing directories:**
- Files: `pi_light_code/utilities/utils.py`
- Why fragile: `pi_light_code/utilities/utils.py:119-125` renames an existing directory before recreating it; repeated runs can move logs unexpectedly.
- Safe modification: Write new experiments to timestamped output directories or explicit `--out` paths instead of relying on mutable `log/{inter_name}/{cur_agent}` paths.
- Test coverage: No detected automated tests for output-path behavior.

## Scaling Limits

**Current SUMO evidence is narrow relative to project scope:**
- Current capacity: `experiments/dual_sensitivity/arterial_sampled_states.json` records 10 passive arterial samples; `experiments/dual_sensitivity/targeted_bottleneck_states.json` records 16 synthetic targeted states; sparse combined recovery uses 26 examples in `experiments/dual_sensitivity/block1_sparse_recovery_combined.json`.
- Limit: Evidence supports dual validity and offline recovery, not network-wide closed-loop dominance.
- Scaling path: Add closed-loop outputs for single, arterial, grid, and Chengdu under `experiments/` with multi-seed confidence intervals before extending claims.

**Sampling script only supports single and arterial networks:**
- Current capacity: `scripts/sample_sumo_states.py:101-117` exposes `--network` choices `single` and `arterial`.
- Limit: Grid and Chengdu states cannot be sampled through the current CLI despite existing `networks/grid_4x4/` and `networks/chengdu/` assets.
- Scaling path: Generalize `scripts/sample_sumo_states.py` to accept explicit `--sumocfg` and `--net-file` paths and add presets for `networks/grid_4x4/` and `networks/chengdu/`.

## Dependencies at Risk

**`amplpy` is not available in the current environment:**
- Risk: `refine-logs/EXPERIMENT_RESULTS.md:152-156` notes SUMO tools are usable but `amplpy` is not installed; OR experiments currently rely on SciPy/HiGHS in `scripts/run_sparse_recovery.py`.
- Impact: AMPL-specific validation or paper replication cannot run from this repository without external setup.
- Migration plan: Keep SciPy/HiGHS as the reproducible default and make any AMPL backend optional with dependency checks and no committed license data.

**Original PI-Light environment depends on CityFlow while OR scripts use SUMO/TraCI:**
- Risk: `pi_light_code/env/TSC_env.py:1-23` imports and initializes `cityflow.Engine`, while `scripts/sample_sumo_states.py:17-18` imports `sumolib` and `traci`.
- Impact: Controller code and OR recovery scripts operate on different simulator APIs, increasing integration risk.
- Migration plan: Add a simulator-neutral observation/action interface or implement SUMO-native controller loops for recovered policies.

## Missing Critical Features

**No automated test suite or CI configuration detected:**
- Problem: `find` evidence detected no `pytest.ini`, `pyproject.toml`, `requirements*.txt`, or `*test*.py` files outside setup scaffolding.
- Blocks: Regression checks for LP dual signs, sparse-recovery gates, SUMO network generation, and phase semantics.
- Files: `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, `scripts/sample_sumo_states.py`, `networks/*/create_network.py`

**No online recovered-policy controller for SUMO closed-loop validation:**
- Problem: Current scripts produce offline JSON (`experiments/dual_sensitivity/*.json`) but do not run recovered symbolic policies as TraCI signal controllers.
- Blocks: Gate C/D/E claims for arterial/grid performance, robustness, runtime, and comparison against max-pressure/C-MP.
- Files: `scripts/run_sparse_recovery.py`, `scripts/run_sumo_sampled_recovery.py`, `refine-logs/EXPERIMENT_TRACKER.md`

**No requirements lockfile detected:**
- Problem: Dependency discovery found only `pi_light_code/utilities/setup.py`; no root `requirements.txt`, `pyproject.toml`, or environment lockfile was detected.
- Blocks: Reproducible setup for SUMO, SciPy, scikit-optimize, CityFlow, PyTorch, graphviz, and optional AMPL components.
- Files: `pi_light_code/utilities/setup.py`, `scripts/run_dual_sanity.py`, `scripts/sample_sumo_states.py`, `pi_light_code/env/TSC_env.py`

## Test Coverage Gaps

**LP dual and finite-difference sign conventions are only checked by script outputs:**
- What's not tested: Unit-level conservation rows, storage-dual sign, green-budget dual, finite-difference forcing, and pressure special case.
- Files: `scripts/run_dual_sanity.py`, `experiments/dual_sensitivity/block0_dual_sanity.json`
- Risk: Refactors can invert signs or change tie handling while still producing plausible JSON.
- Priority: High

**Sparse recovery tie-handling and Big-M constraints lack regression tests:**
- What's not tested: Atom scaling, selected-atom budget enforcement, pairwise ranking constraints, failed solver handling, and deterministic realized regret.
- Files: `scripts/run_sparse_recovery.py`, `experiments/dual_sensitivity/block1_sparse_recovery_combined.json`
- Risk: Solver/library changes can alter selected atoms or silently weaken the recovery claim.
- Priority: High

**SUMO network phase semantics lack automated validation:**
- What's not tested: Generated `tlLogic` state lengths, green/yellow ordering, protected-left semantics, and connection-to-phase mapping.
- Files: `networks/single_intersection/create_network.py`, `networks/arterial/create_network.py`, `networks/grid_4x4/create_network.py`
- Risk: Controllers may optimize against mislabeled or invalid phases.
- Priority: High

**Legacy PI-Light baselines have no reproducibility harness:**
- What's not tested: Seed isolation, log directory behavior, random MCTS expansion, decision-tree split reproducibility, and environment reset behavior.
- Files: `pi_light_code/00_run_tiny_light.py`, `pi_light_code/02_run_MCTS.py`, `pi_light_code/03_run_viper.py`, `pi_light_code/utilities/utils.py`
- Risk: Baseline comparisons may vary across runs or overwrite/move logs.
- Priority: Medium

---

*Concerns audit: 2026/05/22*
