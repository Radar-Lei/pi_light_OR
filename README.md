# PI-Light OR: Dual-Sensitivity Symbolic Traffic Control

## Research question

Can movement-level dual sensitivities from a capacitated traffic-network relaxation be used as an interpretable generalized-pressure principle for signal control, and can that principle be compressed into auditable symbolic policies?

## Contribution claim

The current evidence route is **pressure-equivalent generalized-pressure symbolic recovery**. Phase 3 found that dual-sensitivity and pressure/backpressure tie under the static sample-relative kill gate, so Phase 4 interprets closed-loop SUMO evidence as generalized-pressure symbolic recovery rather than dual superiority.

Max-pressure/backpressure and capacity-aware pressure are first-class baselines, not strawmen. All reported results are simulator-, network-, horizon-, and seed-relative.

## Current status

- Phase 1 locked the continuous capacitated relaxation, dual movement sensitivity framing, and pressure special-case claim.
- Phase 2 implemented sparse symbolic recovery with auditable JSON/CSV/rule outputs.
- Phase 3 selected `route_decision=pressure-equivalent` through the static pressure-failure kill gate.
- Phase 4 generated closed-loop SUMO evidence for single, arterial, grid, demand-shift, and bottleneck/failure-mode scenarios.
- Phase 5 hardens the repository so a fresh reader can audit commands, artifacts, tables, and figure data.

## Repository layout

| Path | Purpose |
|---|---|
| `scripts/` | Experiment, renderer, audit, and table-generation scripts. |
| `networks/` | SUMO network assets for single-intersection, arterial, and grid experiments. |
| `experiments/dual_sensitivity/` | Raw JSON/CSV outputs, reports, rules, manifests, and paper-facing generated artifacts. |
| `.planning/` | GSD roadmap, phase plans, reviews, summaries, and verification reports. |
| `pi_light_code/` | Reference PI-Light/CityFlow code used as predecessor context. |
| `environment.yml` | CPU/SUMO/optimization environment contract. |

## Environment setup

This project is intended to run locally on CPU with SUMO/TraCI and Python optimization tooling.

```bash
conda env create -f environment.yml
conda activate pi-light-or
```

No GPU, CUDA stack, vllm server, neural MARL training service, cloud service, or committed secret is required for the Phase 5 reproduction path. AMPL support through `amplpy` is optional and must be configured outside the repository if needed.

## Reproduction commands

The Phase 5 block runner is the preferred entrypoint once generated:

```bash
python scripts/reproduce_blocks.py --list
python scripts/reproduce_blocks.py --audit --manifest-out experiments/dual_sensitivity/reproducibility_manifest.json
```

| Block | Command | Primary artifacts |
|---|---|---|
| Block 0 dual sanity | `python scripts/run_dual_sanity.py --out experiments/dual_sensitivity/block0_dual_sanity.json` | `block0_dual_sanity.json` |
| Static recovery | `python scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json --out experiments/dual_sensitivity/block2_sparse_recovery.json` | `block2_sparse_recovery.json`, `block2_sparse_recovery.csv`, `block2_sparse_recovery_rules.txt` |
| Static kill-gate | `python scripts/run_static_kill_gate.py --states experiments/dual_sensitivity/block3_regime_states.json --out experiments/dual_sensitivity/block3_static_kill_gate.json --csv-out experiments/dual_sensitivity/block3_static_kill_gate.csv --rules-out experiments/dual_sensitivity/block3_static_kill_gate_rules.txt --report-out experiments/dual_sensitivity/block3_static_kill_gate_report.md` | `block3_static_kill_gate.json`, `.csv`, `_rules.txt`, `_report.md` |
| Closed-loop SUMO smoke | `python scripts/run_closed_loop_suite.py --profile smoke --out experiments/dual_sensitivity/block4_closed_loop_suite_smoke.json` | `block4_closed_loop_suite_smoke.json` |
| Closed-loop SUMO main | `python scripts/run_closed_loop_suite.py --profile main --steps 300 --warmup 60 --action-interval 10 --out experiments/dual_sensitivity/block4_closed_loop_suite.json` | `block4_closed_loop_suite.json` |
| Closed-loop report/CSV | `python scripts/render_closed_loop_report.py --input experiments/dual_sensitivity/block4_closed_loop_suite.json --out experiments/dual_sensitivity/block4_closed_loop_suite_report.md --csv-out experiments/dual_sensitivity/block4_closed_loop_suite.csv` | `block4_closed_loop_suite_report.md`, `.csv` |
| Artifact audit | `python scripts/reproduce_blocks.py --audit --manifest-out experiments/dual_sensitivity/reproducibility_manifest.json` | `reproducibility_manifest.json` |
| Paper table/figure generation | `python scripts/render_paper_artifacts.py --out-dir experiments/dual_sensitivity` | `paper_tables.csv`, `paper_figure_data.csv`, `paper_artifacts_manifest.json` |

## Key artifact paths

| Artifact | Meaning |
|---|---|
| `experiments/dual_sensitivity/block0_dual_sanity.json` | Dual finite-difference sanity checks. |
| `experiments/dual_sensitivity/block2_sparse_recovery.json` | Sparse symbolic recovery outputs. |
| `experiments/dual_sensitivity/block3_static_kill_gate.json` | Static route decision source of truth. |
| `experiments/dual_sensitivity/block3_static_kill_gate_report.md` | Human-readable static kill-gate report. |
| `experiments/dual_sensitivity/block4_closed_loop_suite.json` | Raw closed-loop SUMO suite output. |
| `experiments/dual_sensitivity/block4_closed_loop_suite_report.md` | Claim-disciplined closed-loop report. |
| `experiments/dual_sensitivity/block4_closed_loop_suite.csv` | Flat seed and aggregate audit table. |
| `experiments/dual_sensitivity/reproducibility_manifest.json` | Block-to-command-to-artifact audit manifest. |
| `experiments/dual_sensitivity/paper_tables.csv` | Paper-facing tables generated from raw artifacts. |
| `experiments/dual_sensitivity/paper_figure_data.csv` | Plot-ready figure data generated from raw artifacts. |

## Known limitations

- The current route is pressure-equivalent; it does not show that dual sensitivity universally beats pressure.
- Static supply-binding, corridor-bottleneck, and demand-shift labels include proxy/static limitations where explicit model fields are not yet available.
- Closed-loop SUMO evidence uses local networks, finite horizons, and fixed seed sets; results are not deployable real-world superiority claims.
- `local_pilight` and `full_dual_symbolic` are marked `not_feasible` in the closed-loop runner where no safe live SUMO adaptation exists.
- Paper figures are represented as generated CSV data in Phase 5; final manuscript plotting/styling can be added after the artifact audit path is stable.

## Next experiments

1. Extend explicit storage/supply/corridor constraint fields so binding-regime claims rely less on proxies.
2. Add longer closed-loop horizons and larger real-world networks after the current reproducibility path is stable.
3. Convert generated table and figure-data CSVs into manuscript-ready figures once the paper outline is fixed.
4. Retry external review with the pressure-equivalent framing and Phase 4 closed-loop evidence.

## Claim discipline guardrails

Do not describe the current result as universal dual-over-pressure dominance. The repository should continue to use pressure-equivalent generalized-pressure symbolic recovery language unless a future kill gate changes the route decision.
