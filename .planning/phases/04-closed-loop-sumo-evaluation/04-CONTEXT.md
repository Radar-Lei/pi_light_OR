# Phase 4 Context: Closed-Loop SUMO Evaluation

## Locked route from Phase 3

- Phase 3 verified route: `pressure-equivalent`.
- Downstream framing: generalized-pressure symbolic recovery, not dual superiority.
- Phase 4 reports must interpret closed-loop results as computational evidence for symbolic generalized-pressure recovery under closed-loop SUMO, not proof that dual policies dominate max-pressure.
- Pressure/backpressure and capacity/spillback-aware pressure are first-class baselines and must appear prominently in raw outputs and reports.

## Required network coverage

- Single-intersection sanity: `networks/single_intersection/single_intersection.sumocfg`
- Arterial main case: `networks/arterial/arterial.sumocfg`
- Grid scalability: `networks/grid_4x4/grid_4x4.sumocfg`
- Robustness/demand-shift and failure-mode scenarios: generated at runtime through SUMO/TraCI options and recorded in JSON metadata.

## Required baseline coverage

Baselines to expose in Phase 4 outputs:

1. `fixed_time`
2. `actuated_local_pressure`
3. `max_pressure`
4. `capacity_aware_pressure`
5. `local_pilight`
6. `raw_neighbor_symbolic`
7. `all_neighbor_symbolic`
8. `random_permuted_dual`
9. `full_dual_symbolic` where the Phase 3/LP-derived per-TLS features are feasible.

## Required metrics

Every per-controller/per-seed result must include:

- average travel time
- total delay/time loss
- throughput/completed vehicles
- mean queue
- max queue
- spillback/blocking counts
- switching counts
- controller runtime

## Claim-discipline guardrails

Report language must say:

- Phase 4 is closed-loop SUMO evidence.
- Phase 3 selected `pressure-equivalent` route.
- Symbolic controllers are evaluated as generalized-pressure recoveries/compressions.
- Any observed win/loss is simulator- and scenario-relative.

Report language must not say:

- dual universally beats pressure
- pressure is a strawman
- static kill-gate evidence proves closed-loop superiority
- closed-loop evidence proves deployable real-world superiority
