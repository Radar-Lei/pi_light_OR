# Phase 4 Closed-Loop SUMO Evaluation Report

## Route and Claim Discipline

- **Phase 3 route decision:** `pressure-equivalent`
- **Claim framing:** generalized-pressure symbolic recovery under closed-loop SUMO evidence.
- Pressure/backpressure and capacity-aware pressure are first-class baselines, not strawmen.
- Results are simulator-, network-, horizon-, and seed-relative; they do not prove deployable real-world superiority.

## Scenario and Network Coverage

- **Networks:** arterial, grid_4x4, single
- **Scenarios:** arterial_bottleneck_failure_mode, arterial_demand_shift, arterial_main, grid_scalability, single_sanity
- **Raw rows:** 104
- **Aggregate rows:** 26

## Baseline Coverage

| Controller | Status | Reason |
|---|---|---|
| actuated_local_pressure | run |  |
| all_neighbor_symbolic | run |  |
| capacity_aware_pressure | run |  |
| fixed_time | run |  |
| full_dual_symbolic | not_feasible | Closed-loop per-TLS dual Scenario conversion is not yet safe for live SUMO actuation. |
| local_pilight | not_feasible | No safely adaptable PI-Light local DSL baseline is present in the SUMO runner interface. |
| max_pressure | run |  |
| random_permuted_dual | run |  |
| raw_neighbor_symbolic | run |  |

## Completion Gates

| Gate | Status |
|---|---|
| arterial_main/all_neighbor_symbolic | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| arterial_main/capacity_aware_pressure | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| arterial_main/fixed_time | 5 completed seeds; actuation={'passed': True, 'switching_rows': 'not_required'}; passed=True |
| arterial_main/max_pressure | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| arterial_main/random_permuted_dual | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| arterial_main/raw_neighbor_symbolic | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| grid_scalability/all_neighbor_symbolic | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| grid_scalability/capacity_aware_pressure | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| grid_scalability/fixed_time | 5 completed seeds; actuation={'passed': True, 'switching_rows': 'not_required'}; passed=True |
| grid_scalability/max_pressure | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| grid_scalability/random_permuted_dual | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| grid_scalability/raw_neighbor_symbolic | 5 completed seeds; actuation={'passed': True, 'switching_rows': 5, 'no_switch_rows': 0}; passed=True |
| demand_shift_real_mechanism | True |
| failure_mode_real_mechanism | True |
| failure_mode_pressure_rows | True |

## Main Arterial and Grid CI Summary

| Network | Scenario | Controller | Seeds | Avg travel time | Penalized travel time | Completion rate | Delay | Throughput | Mean queue | Max queue | Spillback | Blocking | Switching | Runtime sec |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| arterial | arterial_bottleneck_failure_mode | capacity_aware_pressure | 1 | 67.0857 | 101.857 | 0.798913 | 8208 | 3.0625 | 34.2 | 25 | 0 | 0 | 56 | 0.00521891 |
| arterial | arterial_bottleneck_failure_mode | max_pressure | 1 | 67.0857 | 101.857 | 0.798913 | 8208 | 3.0625 | 34.2 | 25 | 0 | 0 | 56 | 0.0078781 |
| arterial | arterial_demand_shift | capacity_aware_pressure | 1 | 63.3847 | 98.0226 | 0.803879 | 7491 | 3.10833 | 31.2125 | 16 | 0 | 0 | 55 | 0.0073652 |
| arterial | arterial_demand_shift | fixed_time | 1 | 64.0942 | 103.142 | 0.778017 | 9964 | 3.00833 | 41.5167 | 17 | 0 | 0 | 40 | 0.00510657 |
| arterial | arterial_demand_shift | max_pressure | 1 | 63.3847 | 98.0226 | 0.803879 | 7491 | 3.10833 | 31.2125 | 16 | 0 | 0 | 55 | 0.0081793 |
| arterial | arterial_main | actuated_local_pressure | 5 | 62.7401 | 96.8828 | 0.807391 | 7246.6 | 3.095 | 30.1942 | 15.4 | 0 | 0 | 55.6 | 0.00766895 |
| arterial | arterial_main | all_neighbor_symbolic | 5 | 62.8826 | 97.8063 | 0.802826 | 7378.2 | 3.0775 | 30.7425 | 15.6 | 0 | 0 | 55.4 | 0.00688121 |
| arterial | arterial_main | capacity_aware_pressure | 5 | 62.8826 | 97.8063 | 0.802826 | 7378.2 | 3.0775 | 30.7425 | 15.6 | 0 | 0 | 55.4 | 0.00864741 |
| arterial | arterial_main | fixed_time | 5 | 64.7458 | 102.575 | 0.78413 | 9811.4 | 3.00583 | 40.8808 | 16.8 | 0 | 0 | 40 | 0.00491158 |
| arterial | arterial_main | max_pressure | 5 | 62.8826 | 97.8063 | 0.802826 | 7378.2 | 3.0775 | 30.7425 | 15.6 | 0 | 0 | 55.4 | 0.00822349 |
| arterial | arterial_main | random_permuted_dual | 5 | 65.464 | 118.215 | 0.694565 | 18659 | 2.6625 | 77.7458 | 47.2 | 0 | 0 | 34.6 | 0.00912229 |
| arterial | arterial_main | raw_neighbor_symbolic | 5 | 62.8826 | 97.8063 | 0.802826 | 7378.2 | 3.0775 | 30.7425 | 15.6 | 0 | 0 | 55.4 | 0.00688193 |
| grid_4x4 | grid_scalability | actuated_local_pressure | 5 | 82.2427 | 131.978 | 0.684615 | 2348.6 | 0.593333 | 9.78583 | 3.4 | 0 | 0 | 177.4 | 0.0225386 |
| grid_4x4 | grid_scalability | all_neighbor_symbolic | 5 | 82.3101 | 132.195 | 0.683654 | 2349.4 | 0.5925 | 9.78917 | 3.2 | 0 | 0 | 174.4 | 0.0171158 |
| grid_4x4 | grid_scalability | capacity_aware_pressure | 5 | 82.3101 | 132.195 | 0.683654 | 2349.4 | 0.5925 | 9.78917 | 3.2 | 0 | 0 | 174.4 | 0.0195666 |
| grid_4x4 | grid_scalability | fixed_time | 5 | 77.1712 | 126.803 | 0.695192 | 2198.6 | 0.6025 | 9.16083 | 3 | 0 | 0 | 128 | 0.0149176 |
| grid_4x4 | grid_scalability | max_pressure | 5 | 82.2427 | 131.978 | 0.684615 | 2348.6 | 0.593333 | 9.78583 | 3.4 | 0 | 0 | 177.4 | 0.0208259 |
| grid_4x4 | grid_scalability | random_permuted_dual | 5 | 90.51 | 144.106 | 0.640385 | 4484.8 | 0.555 | 18.6867 | 3.8 | 0 | 0 | 123.8 | 0.0252553 |
| grid_4x4 | grid_scalability | raw_neighbor_symbolic | 5 | 82.2427 | 131.978 | 0.684615 | 2348.6 | 0.593333 | 9.78583 | 3.4 | 0 | 0 | 177.4 | 0.0197408 |
| single | single_sanity | actuated_local_pressure | 1 | 57.0479 | 87.235 | 0.835 | 944 | 0.695833 | 3.93333 | 5 | 0 | 0 | 12 | 0.00170805 |
| single | single_sanity | all_neighbor_symbolic | 1 | 57.0479 | 87.235 | 0.835 | 944 | 0.695833 | 3.93333 | 5 | 0 | 0 | 12 | 0.00154496 |
| single | single_sanity | capacity_aware_pressure | 1 | 57.0479 | 87.235 | 0.835 | 944 | 0.695833 | 3.93333 | 5 | 0 | 0 | 12 | 0.00177894 |
| single | single_sanity | fixed_time | 1 | 57.7425 | 87.815 | 0.835 | 1125 | 0.695833 | 4.6875 | 6 | 0 | 0 | 8 | 0.001244 |
| single | single_sanity | max_pressure | 1 | 57.0479 | 87.235 | 0.835 | 944 | 0.695833 | 3.93333 | 5 | 0 | 0 | 12 | 0.00146421 |
| single | single_sanity | random_permuted_dual | 1 | 68.296 | 132.685 | 0.625 | 6178 | 0.520833 | 25.7417 | 29 | 0 | 0 | 5 | 0.00196269 |
| single | single_sanity | raw_neighbor_symbolic | 1 | 57.0479 | 87.235 | 0.835 | 944 | 0.695833 | 3.93333 | 5 | 0 | 0 | 12 | 0.000968889 |

## Robustness / Demand-Shift Summary

- Demand-shift mechanism(s): traci_vehicle_insertion
- Demand-shift rows: 3

## Bottleneck / Failure-Mode Summary

- Failure-mode mechanism(s): edge_speed_reduction
- Failure-mode rows: 2

## Runtime and Switching Summary

Controller runtime and switching counts are included in the aggregate table and raw CSV rows.

## Limitations and Next Evidence Needed

- SUMO emitted emergency-braking warnings during some runs; interpret outputs as simulator diagnostics requiring follow-up tuning.
- The main suite used the recorded short horizon to complete required seed gates locally; longer horizons remain future robustness work.
- `local_pilight` and `full_dual_symbolic` are not claimed when not feasible; their unsupported reasons remain visible in baseline coverage.

## Artifact Links

- Raw suite JSON: `experiments/dual_sensitivity/block4_closed_loop_suite.json`
- Smoke JSON: `experiments/dual_sensitivity/block4_closed_loop_smoke.json`
- Phase 3 route report: `experiments/dual_sensitivity/block3_static_kill_gate_report.md`
