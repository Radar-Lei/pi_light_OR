---
phase: 03-static-pressure-failure-kill-gate
verified: 2026-05-22T19:39:46Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 3: Static Pressure-Failure Kill Gate Verification Report

**Phase Goal:** Static benchmark evidence determines whether the paper can claim dual sensitivity improves pressure in binding regimes, should present pressure-equivalent symbolic recovery, or must pivot to diagnostic framing.
**Verified:** 2026-05-22T19:39:46Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | Static regimes include slack, downstream storage-binding, supply-binding, corridor-bottleneck, incident/capacity-drop, and demand-shift cases. | VERIFIED | `block3_regime_states.json` has 1,200 samples: 200 each for `slack`, `storage_binding`, `supply_binding_proxy`, `corridor_bottleneck_proxy`, `incident_capacity_drop`, and `demand_shift_proxy`. Generator records proxy rationale for supply/corridor/demand where the current schema lacks explicit primal fields. |
| 2 | Each regime reports disagreement rate, dual win rate, mean oracle regret, worst-case regret, and recovered symbolic rules for dual-vs-pressure comparison. | VERIFIED | `block3_static_kill_gate.json` contains 6 `regime_metrics`, each with disagreement, dual/pressure/tie rates, dual/pressure mean and worst-case oracle regret, selected atoms, and `recovered_symbolic_rules` for `dual_sensitivity` and `pressure_backpressure`. CSV has 6 rows with the same metric columns; rules text groups both libraries by regime. |
| 3 | Main analysis uses enough sampled states, targeting at least 1k states. | VERIFIED | Gate JSON reports `num_examples_total: 1200`, `target_total_states: 1000`, `sample_target_met: true`, and `preliminary_regimes: []`; valid examples by regime are 200 each. |
| 4 | Artifact explicitly classifies result as dual-improves-pressure, dual-recovers-pressure/pressure-equivalent, or diagnostic. | VERIFIED | Gate JSON and report classify route as `pressure-equivalent` with rationale: “Dual and pressure have tie-equivalent static oracle regret across solved regimes.” Report alias maps this to dual-recovers/ties pressure. |
| 5 | Selected claim route is documented before closed-loop experiments are interpreted. | VERIFIED | `block3_static_kill_gate_report.md` documents `pressure-equivalent`, includes all three route meanings, states Phase 3 is static/sample-relative and pre-closed-loop, and lists Phase 4 implications/priorities derived from the route. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `/home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py` | Deterministic labeled regime fixture generator | VERIFIED | Exists, substantive, exposes `main()`, imports `build_network_metadata`, validates regimes, writes schema-compatible samples and `regime_status`. |
| `/home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py` | Static dual-vs-pressure kill-gate runner | VERIFIED | Exists, substantive, imports Phase 2 recovery core (`solve_library`, `scenario_from_sample`, `build_example`), writes JSON/CSV/rules/report outputs, computes route and metrics. |
| `/home/samuel/projects/pi_light_OR/scripts/render_static_kill_gate_report.py` | Deterministic Markdown renderer | VERIFIED | Exists, substantive, validates route fields, renders from JSON, guards forbidden superiority phrasing. |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_regime_states.json` | Labeled static regime states | VERIFIED | 1,200 samples, all required sample fields present, six requested regimes represented with counts. |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.json` | Machine-readable route decision and metrics | VERIFIED | Status `PASSED`, route `pressure-equivalent`, 1,200 valid examples, six regime metrics, route caveats and artifact paths. |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.csv` | Per-regime metric table | VERIFIED | Six rows; columns include all KILL-02 metrics plus regime, examples, claim scope, selected atoms, and rule text path. |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_rules.txt` | Recovered symbolic rules | VERIFIED | Contains grouped `dual_sensitivity` and `pressure_backpressure` rules for each regime and sample-relative caveat. |
| `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_report.md` | Human-readable claim routing report | VERIFIED | Contains selected route, alias mapping, sample sufficiency, metrics table, proxy limitations, artifact links, and Phase 4 implications. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `generate_static_regime_states.py` | SUMO metadata/sample schema | `from sample_sumo_states import build_network_metadata`; generated sample fields | WIRED | Generator preserves `time`, `queues`, `vehicle_counts`, `capacities`, `tls_movements` and adds regime metadata. |
| `block3_regime_states.json` | `run_static_kill_gate.py` | state file consumed by `load_and_group_samples()` and `examples_for_samples()` | WIRED | Gate JSON raw/valid counts exactly match six regimes from state artifact. |
| `run_static_kill_gate.py` | Phase 2 sparse recovery core | imports/calls `solve_library`, `atoms_for_library`, `scenario_from_sample`, `summarize_scenario`, `build_example` | WIRED | Runner uses existing conversion/MILP pathway rather than standalone pressure/dual scorer. |
| `run_static_kill_gate.py` | JSON/CSV/rules/report artifacts | `Path.write_text`, `write_csv`, `render_report` | WIRED | Independent assertions confirmed all four artifacts exist and are internally consistent. |
| `render_static_kill_gate_report.py` | `block3_static_kill_gate.json` | reads route fields and renders report from payload | WIRED | Spot-check generated `/tmp/phase3_verifier_report.md` with route, sample sufficiency, all route aliases, and Phase 4 text. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `block3_regime_states.json` | `samples`, `counts_by_regime`, `regime_status` | `generate_payload()` from network metadata and deterministic perturbation generators | Yes | FLOWING |
| `block3_static_kill_gate.json` | `regime_metrics`, `valid_examples_by_regime`, `route_decision` | `examples_for_samples()` + `solve_regime()` + `compare_dual_pressure()` + `decide_route()` | Yes | FLOWING |
| `block3_static_kill_gate.csv` | per-regime metric rows | `write_csv(csv_rows)` from `regime_metrics` | Yes | FLOWING |
| `block3_static_kill_gate_rules.txt` | grouped rule text | `render_phase3_rules(runs_by_regime, note)` from solved sparse-recovery runs | Yes | FLOWING |
| `block3_static_kill_gate_report.md` | route/report sections | `render_report(payload, out_path, report_path)` from gate JSON payload | Yes | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Phase 3 scripts compile | `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 -m py_compile ...` | Succeeded | PASS |
| Generated artifacts satisfy route/sample/metric assertions | Custom Python assertions over JSON/CSV/report/rules | `independent artifact assertions passed` | PASS |
| Phase 3 script tests | `python3 tests/test_generate_static_regime_states.py && python3 tests/test_run_static_kill_gate.py` | `static kill-gate tests ok` | PASS |
| Standalone renderer regenerates report from JSON | `python3 scripts/render_static_kill_gate_report.py --gate-json ... --out /tmp/phase3_verifier_report.md --fail-on-missing-route` | `renderer behavior spot-check passed` | PASS |

### Probe Execution

No phase-declared `probe-*.sh` files or probe requirements found; probe execution not applicable.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| KILL-01 | 03-01 | Static regimes include slack, storage-binding, supply-binding, corridor-bottleneck, incident/capacity-drop, demand-shift. | SATISFIED | State and gate artifacts include all six as supported/proxy regimes with 200 samples each. |
| KILL-02 | 03-02 | Each regime reports disagreement, win rates, regrets, and recovered symbolic rules. | SATISFIED | JSON/CSV/rules artifacts contain required metrics and rules for all six regimes. |
| KILL-03 | 03-01, 03-02 | Main analysis targets at least 1k valid states. | SATISFIED | 1,200 valid converted examples; `sample_target_met: true`. |
| KILL-04 | 03-02, 03-03 | Analysis identifies dual-improves/recovers/fails pressure route. | SATISFIED | `route_decision: pressure-equivalent`; report aliases it to dual-recovers/ties pressure. |
| KILL-05 | 03-03 | Claim route documented before closed-loop interpretation. | SATISFIED | Report states selected route, all route meanings, no closed-loop claims, and Phase 4 priorities. |

No Phase 3 orphaned requirements found in `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md` beyond KILL-01 through KILL-05.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| Phase 3 scripts | n/a | Empty-list/dict initializations from grep scan | Info | Normal local accumulators and argparse defaults; not stubs because they are populated by generation/conversion flows. |

No unreferenced `TBD`, `FIXME`, or `XXX` markers found in modified Phase 3 scripts. No placeholder/coming-soon/not-implemented implementation found.

### Human Verification Required

None. The phase output is script/artifact/report based and was verified programmatically. Visual/user-flow UAT is not required for this static artifact gate.

### Gaps Summary

No blocking gaps found. Phase 3 achieved the static kill-gate goal and locked the claim route to `pressure-equivalent` / generalized-pressure symbolic recovery framing, with explicit proxy limitations and no closed-loop overclaim.

---

_Verified: 2026-05-22T19:39:46Z_
_Verifier: Claude (gsd-verifier)_
