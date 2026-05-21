# Experiment Tracker — Dual-Sensitivity-Guided Programmatic Signal Control

**Date**: 2026-05-20

| ID | Block | Task | Status | Gate | Notes |
|---|---|---|---|---|---|
| B0.1 | Dual sanity | Implement continuous store-and-forward/CTM-lite relaxation | TODO | A | LP/QP only; no integer phase-dual story |
| B0.2 | Dual sanity | Extract duals for queue conservation, storage/supply, movement value | TODO | A | Every sensitivity must map to model object |
| B0.3 | Dual sanity | Run finite-difference validation | TODO | A | Compare perturbation objective changes to duals |
| B0.4 | Theory | Derive dual-to-movement marginal-benefit lemma | TODO | A | Needed before strong OR claim |
| B0.5 | Theory | Derive pressure/backpressure special case | TODO | A | Turns MP overlap into positioning asset |
| B1.1 | Recovery | Define OR-mapped DSL atom library | TODO | B | Delete unmapped atoms |
| B1.2 | Recovery | Implement sparse MIP recovery objective | TODO | B | Regret/value + complexity + neighbor penalties |
| B1.3 | Recovery | Build sampled-state datasets | TODO | B | single, arterial, grid, demand regimes |
| B1.4 | Recovery | Compare local/raw/all/random/dual DSL offline | TODO | B | Equal complexity budget |
| B2.1 | Single | Run local sanity controllers | TODO | C | fixed/Webster, actuated, MP, local programmatic, dual-zero |
| B3.1 | Arterial | Configure directional platoon + bottleneck scenarios | TODO | C | main result scenario |
| B3.2 | Arterial | Implement C-MP or closest coordinated MP baseline | TODO | C/E | high-priority baseline |
| B3.3 | Arterial | Run 3-seed pilot for key variants | TODO | C | stop if no signal |
| B3.4 | Arterial | Run 10-seed full comparison | TODO | C/E | with CI and paired tests |
| B4.1 | Grid | Configure 4×4 demand and bottleneck scenarios | TODO | D | not corridor-only |
| B4.2 | Grid | Run grid pilot/full comparison | TODO | D/E | compare symbolic ablations + MP/C-MP |
| B5.1 | Robustness | Build peak reversal and demand-scale shifts | TODO | D/E | nominal vs recomputed duals |
| B5.2 | Robustness | Build turning-ratio error and storage-bottleneck shifts | TODO | D/E | finite storage value test |
| B6.1 | Runtime | Measure LP/QP, MIP recovery, online latency | TODO | E | CPU-only table |
| B6.2 | Reporting | Generate claims-to-results matrix | TODO | E | what can be claimed under outcomes |

## Gate Status

- Gate A — Dual validity: PENDING
- Gate B — Offline recovery: PENDING
- Gate C — Arterial closed-loop: PENDING
- Gate D — Grid/demand generality: PENDING
- Gate E — Baseline honesty/runtime: PENDING

## First Three Runs

1. Implement and validate finite-difference dual sanity on toy/single/arterial states.
2. Run offline sparse MIP recovery on single + arterial sampled states.
3. Run 3-seed arterial pilot comparing local/raw/random/dual symbolic policies plus MP.
