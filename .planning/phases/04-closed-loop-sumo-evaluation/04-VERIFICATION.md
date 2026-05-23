---
phase: 04-closed-loop-sumo-evaluation
verified: 2026-05-23T02:22:03Z
status: passed
score: 10/10 must-haves verified
overrides_applied: 0
---

# Phase 4: Closed-Loop SUMO Evaluation Verification Report

**Phase Goal:** Closed-loop SUMO experiments provide credible computational evidence for the Phase 3-selected claim route against strong max-pressure-style, symbolic, placebo, and practical baselines.
**Verified:** 2026-05-23T02:22:03Z
**Status:** passed
**Verdict:** PASS — Phase 4 goal achieved.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | Real TraCI closed-loop SUMO runner exists and controls SUMO end-to-end | VERIFIED | `scripts/run_closed_loop_sumo.py` starts SUMO via `traci.start`, reads live edge queues/vehicles, selects TLS phases, applies `traci.trafficlight.setPhase`, and closes TraCI. Independent spot-check ran `run_closed_loop_sumo.py --network single ... --steps 60` and produced 3 controller rows with `route_decision=pressure-equivalent`. |
| 2 | Single, arterial, and grid coverage exists | VERIFIED | `resolve_network` supports `single`, `arterial`, `grid_4x4`; required `.sumocfg`/`.net.xml` assets exist. Suite JSON contains networks `single`, `arterial`, `grid_4x4` and scenarios `single_sanity`, `arterial_main`, `grid_scalability`. |
| 3 | Core baselines include fixed_time, max_pressure, capacity_aware_pressure, raw/all neighbor symbolic, random_permuted_dual | VERIFIED | `CONTROLLER_REGISTRY` and suite rows include all required controller names: `fixed_time`, `actuated_local_pressure`, `max_pressure`, `capacity_aware_pressure`, `local_pilight`, `raw_neighbor_symbolic`, `all_neighbor_symbolic`, `random_permuted_dual`, `full_dual_symbolic`. |
| 4 | Unsafe PI-Light/full-dual policies are honestly marked not_feasible | VERIFIED | Suite `baseline_coverage` marks `local_pilight` as `not_feasible` with reason `No safely adaptable PI-Light local DSL baseline...`; `full_dual_symbolic` as `not_feasible` with reason `Closed-loop per-TLS dual Scenario conversion is not yet safe...`. No heuristic is mislabeled as PI-Light/full dual. |
| 5 | Arterial and grid core baselines have 5 completed seeds and CI-ready aggregates | VERIFIED | Suite JSON `completion_gates_passed=true`; each core baseline has 5 arterial seeds `[20260523..20260527]` and 5 grid seeds `[20260601..20260605]`. Aggregates include `n_seeds`, `mean`, `std_error`, `ci95_low`, `ci95_high` for CLOP-04 metrics. |
| 6 | Demand-shift scenario uses a real mechanism | VERIFIED | Completed `arterial_demand_shift` rows for `fixed_time`, `max_pressure`, `capacity_aware_pressure` record `demand_shift_mechanism=traci_vehicle_insertion` and `demand_shift_inserted_vehicles=8`. Runner calls `demand_shift_tick` during simulation and uses `traci.vehicle.add`. |
| 7 | Bottleneck/failure-mode scenario uses a real mechanism and completes pressure rows | VERIFIED | Completed `arterial_bottleneck_failure_mode` rows for `max_pressure` and `capacity_aware_pressure` record `failure_mode_mechanism=edge_speed_reduction`, target edge `C12C2`, active target traffic, and intervention window 60-180. Runner applies/restores speed through `traci.edge.setMaxSpeed`. |
| 8 | CLOP-04 metrics are present in raw JSON and CSV | VERIFIED | No suite row is missing required metrics: `avg_travel_time`, `total_delay`, `completed_vehicles`, `throughput`, `mean_queue`, `max_queue`, `spillback_count`, `blocking_count`, `switching_count`, `controller_runtime_sec`. CSV header contains these fields plus CI columns. |
| 9 | Report/CSV are auditable and regenerable from JSON | VERIFIED | `scripts/render_closed_loop_report.py` validates raw gates, renders Markdown, and writes CSV. Independent check confirmed `render_report(...)` and `write_csv(...)` exactly reproduce `block4_closed_loop_suite_report.md` and `block4_closed_loop_suite.csv` from `block4_closed_loop_suite.json`. |
| 10 | Claim discipline follows route_decision=pressure-equivalent | VERIFIED | Phase 3 JSON has `route_decision=pressure-equivalent`; smoke/suite/report carry it. Report contains `generalized-pressure symbolic recovery`, treats pressure/capacity-aware as first-class baselines, and forbidden phrases are absent from suite JSON/report. |

**Score:** 10/10 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `scripts/run_closed_loop_sumo.py` | Real TraCI closed-loop runner and controller registry | VERIFIED | 513 lines; substantive SUMO/TraCI loop, controller action scoring, route metadata, demand shift, failure mode, metrics. |
| `scripts/run_closed_loop_suite.py` | Multi-network/multi-seed suite orchestrator and CI aggregation | VERIFIED | 238 lines; suite spec, baseline coverage, completion gates, aggregate CIs. |
| `scripts/render_closed_loop_report.py` | Deterministic report/CSV renderer with claim gate | VERIFIED | 383 lines; validates completion gates, rejects overclaims, writes Markdown/CSV from JSON. |
| `tests/test_closed_loop_sumo.py` | Fast behavior and regression tests | VERIFIED | Tests controller registry, metric aggregation, infeasibility metadata, failure-mode restoration, suite gates, renderer rejection. Passed in verifier run. |
| `experiments/dual_sensitivity/block4_closed_loop_smoke.json` | Single-intersection smoke artifact | VERIFIED | Exists; route `pressure-equivalent`; includes required controller rows/metrics. |
| `experiments/dual_sensitivity/block4_closed_loop_suite.json` | Raw per-seed and aggregate suite artifact | VERIFIED | Exists; 104 raw rows, 26 aggregate rows, completion gates passed. |
| `experiments/dual_sensitivity/block4_closed_loop_suite_report.md` | Human-readable report | VERIFIED | Regenerates exactly from raw JSON; contains route/coverage/baseline/CI/failure-mode sections. |
| `experiments/dual_sensitivity/block4_closed_loop_suite.csv` | Flat audit table | VERIFIED | Regenerates exactly from raw JSON; includes seed and aggregate rows. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `run_closed_loop_sumo.py` | `sample_sumo_states.py` | `from sample_sumo_states import build_network_metadata` | WIRED | Runner reuses metadata for edge capacities. |
| `run_closed_loop_suite.py` | `run_closed_loop_sumo.py` | imports `CLAIM_FRAMING`, `METRIC_FIELDS`, `load_route_metadata`, `run_experiment` | WIRED | Suite invokes runner for every spec row. |
| Runner/suite | SUMO network assets | network resolver and suite spec | WIRED | Single, arterial, and grid `.sumocfg`/`.net.xml` files exist and are referenced. |
| Suite JSON | Renderer | `render_report` / `write_csv` read raw suite JSON | WIRED | Exact regeneration check passed. |
| Phase 3 route | Phase 4 outputs | route metadata loader | WIRED | Phase 3 route copied as `pressure-equivalent` into smoke/suite/report. |

### Data-Flow Trace

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `run_closed_loop_sumo.py` | queues, vehicles, arrivals, TLS phase | live TraCI calls (`traci.edge`, `traci.simulation`, `traci.trafficlight`) | Yes | FLOWING |
| `run_closed_loop_suite.py` | raw rows and aggregates | `run_experiment(...)` per spec, then `aggregate_results` | Yes | FLOWING |
| `render_closed_loop_report.py` | report tables/CSV rows | `block4_closed_loop_suite.json` raw rows and aggregates | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Compile and unit tests | `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 -m py_compile ... && python3 tests/test_closed_loop_sumo.py` | `closed-loop SUMO tests ok` | PASS |
| Real short SUMO closed-loop run | `run_closed_loop_sumo.py --network single --controllers fixed_time max_pressure capacity_aware_pressure --seeds 424242 --steps 60 ...` | Wrote `/tmp/phase4_verify_single_smoke.json`; assertions passed with 3 rows | PASS |
| Report/CSV audit regeneration | `render_report(...)` and `write_csv(...)` from suite JSON | Exact match to committed report and CSV | PASS |

### Requirements Coverage

| Requirement | Status | Evidence |
|---|---|---|
| CLOP-01 | SATISFIED | Suite covers single sanity, arterial main, grid scalability, demand shift, and bottleneck/failure-mode. |
| CLOP-02 | SATISFIED | All required baselines represented; infeasible PI-Light/full-dual rows are explicit and reasoned. |
| CLOP-03 | SATISFIED | Arterial/grid core baselines have 5 completed seeds and aggregate CIs. |
| CLOP-04 | SATISFIED | Raw rows and CSV include travel time, delay, throughput/completions, queues, spillback/blocking, switching, runtime. |
| CLOP-05 | SATISFIED | Bottleneck/failure-mode uses actual edge-speed reduction with completed max_pressure and capacity_aware_pressure rows. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `scripts/run_closed_loop_sumo.py` | 317, 320, 339, 345 | `return None` in optional mechanism helpers | Info | Legitimate no-action branches for demand shift/failure mode timing, not stubs. |

### Human Verification Required

None.

### Gaps Summary

No blocking gaps found. The implementation materially satisfies the closed-loop Phase 4 goal with real TraCI execution, required network and baseline coverage, honest infeasibility metadata, multi-seed CI-ready artifacts, real demand/failure mechanisms, auditable reporting, and pressure-equivalent claim discipline.

---

_Verified: 2026-05-23T02:22:03Z_
_Verifier: Claude (gsd-verifier)_
