# PI-Light OR: Dual-Sensitivity Symbolic Traffic Control

## Research question

Can movement-level dual sensitivities from a capacitated traffic-network relaxation be used as an interpretable generalized-pressure principle for signal control, and can that principle be compressed into auditable symbolic policies?

## Contribution claim

The current proven evidence route remains **pressure-equivalent generalized-pressure symbolic recovery**. Phase 3 found that dual-sensitivity and pressure/backpressure tie under the static sample-relative kill gate, and the completed v1.3/v1.4 closed-loop Gate C artifacts do not permit superiority claims over max-pressure-style baselines.

The active method-design direction is v1.5 **dynamic finite-storage primal-dual pressure**: use vehicle-count occupancy rather than halting queues for storage scarcity, maintain stateful storage/release/cascade/service shadow prices, and test the method against max-pressure, capacity-aware pressure, finite-storage double pressure, static v1.4, and occupancy-aware ablations under a future locked protocol.

Max-pressure/backpressure and capacity-aware pressure are first-class baselines, not strawmen. All reported results are simulator-, network-, horizon-, and seed-relative.

## Current status

- Phase 1 locked the continuous capacitated relaxation, dual movement sensitivity framing, and pressure special-case claim.
- Phase 2 implemented sparse symbolic recovery with auditable JSON/CSV/rule outputs.
- Phase 3 selected `route_decision=pressure-equivalent` through the static pressure-failure kill gate.
- Phase 4 generated closed-loop SUMO evidence for single, arterial, grid, demand-shift, and bottleneck/failure-mode scenarios.
- Phase 5 hardens the repository so a fresh reader can audit commands, artifacts, tables, and figure data.
- v1.4 locked Gate C executed 1440/1440 rows and remained non-PASSED; closed-loop superiority remains disallowed.
- v1.5 implementation work added occupancy-based finite-storage state, an occupancy-aware capacity baseline, `finite_storage_dynamic_primal_dual_v1_5`, deterministic method gates, closed-loop diagnostics, and locked holdout tooling.
- The original v1.5 holdout protocol was superseded after activation audit showed no storage-binding decisions in early rows. The revised binding protocol activates storage/cascade/release mechanisms, but early locked rows trigger safety-guard failures against strong baselines; closed-loop superiority remains disallowed.

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
| `experiments/dual_sensitivity/v1_5_dynamic_primal_dual_gates.json` | Deterministic v1.5 method gates for occupancy storage state, dynamic shadow-price activation, and action separation mechanisms. |
| `experiments/dual_sensitivity/v1_5_closed_loop_diagnostics.json` | Short SUMO diagnostic for storage activation, action-difference rate, and dynamic term activation. |
| `experiments/dual_sensitivity/v1_5_locked_protocol.json` | Original locked v1.5 protocol; superseded after storage-binding activation audit failed on early execution rows. |
| `experiments/dual_sensitivity/v1_5_protocol_activation_audit.json` | Audit proving the original protocol was non-binding in early rows and should not be used for final v1.5 claims. |
| `experiments/dual_sensitivity/v1_5_binding_locked_protocol.json` | Superseding binding-focused locked protocol with composite finite-storage operating cost and strong baselines/ablations. |
| `experiments/dual_sensitivity/v1_5_binding_holdout_execution.json` | Partial binding holdout execution artifact; mechanism activation is present but full execution is intentionally stopped after early safety-risk evidence. |
| `experiments/dual_sensitivity/v1_5_binding_protocol_activation_audit.json` | Audit confirming the revised binding protocol activates storage/cascade/release mechanisms in executed v1.5 rows. |
| `experiments/dual_sensitivity/v1_5_binding_paired_evidence.json` | Strict paired-evidence checker output for the partial binding holdout; `INCONCLUSIVE`, `claim_ready=false`. |
| `experiments/dual_sensitivity/v1_5_binding_early_holdout_risk.json` | Early locked-holdout risk audit; `FAILED` because safety guards show repeated harm against strong baselines after mechanism activation. |
| `experiments/dual_sensitivity/v1_5_r2_training_protocol.json` | Training-only protocol for `finite_storage_dynamic_primal_dual_v1_5_r2_guarded`, using fresh seeds disjoint from the failed binding holdout seeds. |
| `experiments/dual_sensitivity/v1_5_r2_training_execution.json` | Partial r2 training execution; 6/324 rows complete, `claim_ready=false`. |
| `experiments/dual_sensitivity/v1_5_r2_training_selection.json` | Training-only selection artifact; `REJECTED` because r2 is too pressure-equivalent and violates an unfinished-vehicle safety guard against finite-storage double pressure. |
| `experiments/dual_sensitivity/v1_5_r3_training_selection.json` | Training-only selection artifact; `REJECTED` despite positive composite signal because unfinished-vehicle safety guards fail. |
| `experiments/dual_sensitivity/v1_5_r4_training_selection.json` | Training-only selection artifact; `REJECTED` despite stronger action separation because unfinished-vehicle safety guards fail. |
| `experiments/dual_sensitivity/v1_5_r5_training_selection.json` | Training-only selection artifact; `REJECTED` despite finite-storage-double fallback because unfinished-vehicle safety guards fail. |
| `experiments/dual_sensitivity/v1_5_r6_training_selection.json` | Training-only selection artifact; `REJECTED` despite terminal finite-storage-double flush because unfinished-vehicle safety guards fail on the second seed. |
| `experiments/dual_sensitivity/v1_5_r7_training_selection.json` | Training-only selection artifact; `REJECTED` because double-score filtering is too pressure-equivalent and still harms capacity-aware unfinished-vehicle safety. |
| `experiments/dual_sensitivity/v1_5_r8_training_selection.json` | Training-only selection artifact; `REJECTED` because multi-baseline filtering is too pressure-equivalent and still harms unfinished-vehicle safety. |
| `experiments/dual_sensitivity/v1_5_r9_training_selection.json` | Training-only selection artifact; `REJECTED` because hold-only overrides still harm unfinished-vehicle safety. |
| `experiments/dual_sensitivity/v1_5_r10_training_selection.json` | Training-only selection artifact; `REJECTED` because bounded holds keep positive composite signals but fail unfinished-vehicle safety on the second seed. |
| `experiments/dual_sensitivity/v1_5_r11_training_selection.json` | Training-only selection artifact; `REJECTED` because local completion-risk service preservation still fails unfinished-vehicle safety on the second seed. |
| `experiments/dual_sensitivity/v1_5_r12_training_selection.json` | Training-only selection artifact; `REJECTED` because receiver-constrained route-completion proxy still fails unfinished-vehicle safety and action-separation guards. |
| `experiments/dual_sensitivity/v1_5_r13_training_selection.json` | Training-only selection artifact; `REJECTED` because movement-level route demand improves separation but still fails unfinished-vehicle safety. |
| `experiments/dual_sensitivity/v1_5_r14_training_selection.json` | Training-only selection artifact; `REJECTED` because finite-storage-double veto removes completion harm but collapses action separation and triggers delay safety harm. |
| `experiments/dual_sensitivity/v1_5_r15_training_selection.json` | Training-only selection artifact; `REJECTED` because horizon-modeled completion has positive composite signals but still fails unfinished-vehicle safety. |
| `experiments/dual_sensitivity/v1_5_r16_training_selection.json` | Training-only selection artifact; `REJECTED` because terminal finite-storage-double lock still fails capacity-aware unfinished-vehicle safety on the second seed. |
| `experiments/dual_sensitivity/v1_5_r17_training_selection.json` | Training-only selection artifact; `REJECTED` because terminal capacity-aware lock fails finite-storage-double unfinished-vehicle safety. |
| `experiments/dual_sensitivity/v1_5_r18_training_selection.json` | Training-only selection artifact; `REJECTED` because balanced terminal capacity/double lock still fails finite-storage-double unfinished-vehicle safety and loses composite cost to finite-storage double pressure. |
| `experiments/dual_sensitivity/v1_5_r19_training_selection.json` | Training-only selection artifact; `REJECTED` because stronger finite-storage-double anchoring still fails max-pressure unfinished-vehicle safety by one vehicle on the second training seed. |
| `experiments/dual_sensitivity/v1_5_r20_training_selection.json` | Training-only selection artifact; `REJECTED` because balanced max-pressure/double terminal lock still fails unfinished-vehicle safety against max-pressure and finite-storage double pressure. |
| `experiments/dual_sensitivity/v1_5_r21_training_selection.json` | Training-only selection artifact; `REJECTED` because terminal completion-service selection still fails unfinished-vehicle safety against max-pressure and finite-storage double pressure. |
| `experiments/dual_sensitivity/v1_5_r22_training_selection.json` | Training-only selection artifact; `REJECTED` because all-interval completion-safety veto still fails unfinished safety while action separation and composite means degrade. |
| `experiments/dual_sensitivity/v1_5_r23_training_selection.json` | Training-only selection artifact; `REJECTED` because baseline-dominance filtering drops action separation below 5% while unfinished safety still fails. |
| `experiments/dual_sensitivity/v1_5_r24_training_selection.json` | Training-only selection artifact; `REJECTED` because staged horizon completion still fails max-pressure unfinished safety by one vehicle despite positive composite means. |
| `experiments/dual_sensitivity/v1_5_r25_training_selection.json` | Training-only selection artifact; `REJECTED` because late max-pressure terminal lock still fails unfinished safety against max-pressure and finite-storage double pressure. |
| `experiments/dual_sensitivity/v1_5_r26_training_selection.json` | Training-only selection artifact; `REJECTED` because relative exit urgency still fails unfinished safety against max-pressure, capacity-aware pressure, and finite-storage double pressure. |
| `experiments/dual_sensitivity/v1_5_r27_training_selection.json` | Training-only selection artifact; `REJECTED` because terminal exit protection still fails max-pressure unfinished safety despite positive composite means. |
| `experiments/dual_sensitivity/v1_5_r28_training_selection.json` | Training-only selection artifact; `REJECTED` because max-pressure completion envelope still fails unfinished safety against all core strong baselines on the second training seed. |
| `experiments/dual_sensitivity/v1_5_r29_training_selection.json` | Training-only selection artifact; `REJECTED` because the all-core-baseline completion envelope still fails finite-storage-double unfinished safety and loses composite cost to max-pressure and finite-storage double. |
| `experiments/dual_sensitivity/v1_5_r30_training_selection.json` | Training-only selection artifact; `REJECTED` because the finite-storage-double completion envelope still fails capacity-aware unfinished safety and loses composite cost to all core strong baselines. |
| `experiments/dual_sensitivity/v1_5_r31_training_selection.json` | Training-only selection artifact; `REJECTED` because delaying the finite-storage-double terminal lock to 0.88 still fails finite-storage-double unfinished safety by one vehicle despite positive core composite means. |
| `experiments/dual_sensitivity/v1_5_r32_training_selection.json` | Training-only selection artifact; `REJECTED` because the narrow preterminal finite-storage-double guard clears the first seed but fails finite-storage-double unfinished safety on the second. |
| `experiments/dual_sensitivity/v1_5_r33_training_selection.json` | Training-only selection artifact; `REJECTED` because the midcourse finite-storage-double guard fails max-pressure and capacity-aware unfinished safety despite positive core composite means. |
| `experiments/dual_sensitivity/v1_5_r34_training_selection.json` | Training-only selection artifact; `REJECTED` because the core-minimax guard fails max-pressure and finite-storage-double unfinished safety and loses composite cost to max-pressure. |
| `experiments/dual_sensitivity/v1_5_r35_training_selection.json` | Training-only selection artifact; `REJECTED` because deadline-oriented urgency over-rotates actions, causing 1209 unfinished vehicles and negative composite means against all core baselines. |
| `experiments/dual_sensitivity/v1_5_r36_training_selection.json` | Training-only selection artifact; `REJECTED` because late-gated deadline urgency clears one seed but fails unfinished safety against all core baselines on the second. |
| `experiments/dual_sensitivity/v1_5_r37_training_selection.json` | Training-only selection artifact; `REJECTED` because the late-gated service anchor stabilizes actions but loses composite cost to max-pressure/capacity-aware pressure and still fails capacity-aware unfinished safety. |
| `experiments/dual_sensitivity/v1_5_r38_training_selection.json` | Training-only selection artifact; `REJECTED` because the capacity-aware rescue guard triggers too sparsely, leaving capacity-aware unfinished safety harm and negative composite signal against capacity-aware pressure. |
| `experiments/dual_sensitivity/v1_5_r39_training_selection.json` | Training-only selection artifact; `REJECTED` because the capacity-aware score envelope restores positive core composite means but collapses action separation and still fails unfinished safety. |
| `experiments/dual_sensitivity/v1_5_r40_training_selection.json` | Training-only selection artifact; `REJECTED` because pressure-safe horizon overrides keep positive core composite means and 5% action separation but still fail unfinished safety against all core baselines. |
| `experiments/dual_sensitivity/v1_5_r41_training_selection.json` | Training-only selection artifact; `REJECTED` because the terminal core-completion lock keeps positive core composite means but drops action separation below 5% and still fails unfinished safety. |
| `experiments/dual_sensitivity/v1_5_r42_training_selection.json` | Training-only selection artifact; `REJECTED` because tail-completion rescue restores action separation but still fails unfinished safety against capacity-aware and finite-storage double pressure. |
| `experiments/dual_sensitivity/v1_5_r43_training_selection.json` | Training-only selection artifact; `REJECTED` because strict staged pressure-safe filtering passes unfinished safety but collapses action separation and loses composite cost to all core baselines. |
| `experiments/dual_sensitivity/v1_5_r44_training_selection.json` | Training-only selection artifact; `REJECTED` because looser staged pressure-safe filtering restores positive composite means but still has low action separation and unfinished safety harm. |
| `experiments/dual_sensitivity/v1_5_r45_training_selection.json` | Training-only selection artifact; `REJECTED` after the full 324-row run because 176 safety harms accumulate, dominated by unfinished-vehicle regressions against strong baselines, and core composite means turn negative against max-pressure and capacity-aware pressure. |
| `experiments/dual_sensitivity/v1_5_r46_training_selection.json` | Training-only selection artifact; `REJECTED` after the first 12-row batch because unfinished-vehicle safety still fails on `arterial_v1_5_storage_activation` at seed `20261218`, even though early core composite means stay positive against all three core baselines. |
| `experiments/dual_sensitivity/v1_5_revision_candidate_summary.json` | r2-r46 convergence summary; `NO_CANDIDATE_SELECTED`; completion and safety risk remain unresolved. |
| `experiments/dual_sensitivity/v1_5_completion_safety_contract_audit.json` | Safety-contract audit through r46; `REVISION_REQUIRED`; no candidate passes unfinished safety with positive core composite/action separation, and current evidence does not support weakening the guard. |
| `experiments/dual_sensitivity/v1_5_completion_tradeoff_analysis.json` | Diagnostic execution-level tradeoff analysis across r2-r46 execution artifacts; 107 analyzed training cases, 75 unsafe cases, 52 composite-win cases, 24 safe-and-composite-win cases, and 33 core-baseline oracle conflicts. |

## Known limitations

- The current route is pressure-equivalent; it does not show that dual sensitivity universally beats pressure.
- v1.4 has complete locked execution but non-PASSED strict evidence; it should not be described as closed-loop superior to max-pressure, capacity-aware pressure, or finite-storage double pressure.
- Closed-loop SUMO evidence uses local networks, finite horizons, and fixed seed sets; results are not deployable real-world superiority claims.
- `local_pilight` and `full_dual_symbolic` are marked `not_feasible` in the closed-loop runner where no safe live SUMO adaptation exists.
- Paper figures are represented as generated CSV data in Phase 5; final manuscript plotting/styling can be added after the artifact audit path is stable.

## Next experiments

1. Treat current v1.5 binding rows as a method-risk finding, not a superiority result.
2. Rebuild completion modeling or add a stronger completion-safety controller guard on fresh training seeds before any confirmatory claim.
3. Lock a new training protocol before any future confirmatory paired-evidence claim.

## Claim discipline guardrails

Do not describe the current result as universal dual-over-pressure dominance or closed-loop superiority. Superiority language requires a future locked v1.5 artifact with passing paired-seed evidence against the required strong baselines and ablations.
