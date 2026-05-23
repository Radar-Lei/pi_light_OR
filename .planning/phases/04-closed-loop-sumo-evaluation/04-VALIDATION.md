# Phase 4 Validation Gates

## Local smoke validation

Run from repository root with `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts`.

1. Compile new scripts and tests with `python3 -m py_compile`.
2. Run closed-loop unit tests directly with `python3 tests/test_closed_loop_sumo.py` once Plan 04-01 creates them.
3. Run a single-intersection smoke experiment with one seed, short horizon, and at least `fixed_time,max_pressure,capacity_aware_pressure`.

Expected smoke artifact fields:

- `experiment`: `block4_closed_loop_sumo`
- `route_decision`: `pressure-equivalent`
- `scenario_results`: non-empty
- every result has `avg_travel_time`, `total_delay`, `completed_vehicles`, `throughput`, `mean_queue`, `max_queue`, `spillback_count`, `blocking_count`, `switching_count`, and `controller_runtime_sec`.

## Main validation

Run arterial and grid with 5-10 seeds for CI once Plan 04-02 is complete.

Validation checks:

- single, arterial, grid, robustness/demand-shift, and at least one bottleneck/failure-mode scenario are present across generated artifacts.
- required baseline names appear in metadata; only `full_dual_symbolic` may be marked `not_feasible` when per-TLS dual features cannot be safely computed, and all other required baselines must have completed rows.
- arterial main and grid scalability each have at least 5 completed seeds for core baselines (`fixed_time`, `max_pressure`, `capacity_aware_pressure`, `raw_neighbor_symbolic`, `all_neighbor_symbolic`, `random_permuted_dual`); `local_pilight` must also complete 5 seeds if a real PI-Light/DSL baseline is safely adaptable, otherwise it must be explicitly marked `not_feasible` with an unsupported reason and is not counted as a core completion gate.
- demand-shift rows record an actual demand change mechanism (`route_file_scaled`, `traci_vehicle_insertion`, or equivalent), not seed-only metadata.
- bottleneck/failure-mode rows record an actual SUMO/TraCI manipulation (`edge_speed_reduction`, `lane_closure`, `capacity_proxy`, or equivalent) and include completed `max_pressure` and `capacity_aware_pressure` rows.
- aggregate JSON and CSV include mean, standard error, 95% confidence interval, and seed count per metric; Phase 4 cannot be marked complete with `not_completed_runtime_budget` for arterial/grid core-baseline seed coverage.

## Claim discipline validation

Plan 04-03 must generate a report that includes `pressure-equivalent`, `generalized-pressure symbolic recovery`, and first-class pressure/capacity-aware baseline caveats.

Forbidden report phrases:

- `dual universally beats pressure`
- `max-pressure strawman`
- `proves superiority`
- `deployable superiority`
- `static evidence proves closed-loop`

If any forbidden phrase appears in non-comment report text, fix the report before marking Phase 4 complete.
