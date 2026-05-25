# Phase 8: Live Finite-Storage Primal-Dual Controller - Research

**Researched:** 2026-05-24  
**Domain:** closed-loop SUMO finite-storage primal-dual controller integration  
**Confidence:** HIGH for existing architecture/schema; MEDIUM for initial score coefficient recommendations

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### D-08-01 Controller Naming

Default to adding `finite_storage_primal_dual` as the safe live successor. Keep `full_dual_symbolic` marked `not_feasible` unless a plan explicitly and safely aliases it to the new path with tests. This prevents relabeling unsafe queue heuristics as the proposed method.

### D-08-02 Score Decomposition

A movement score should decompose into auditable terms:

- `pressure`: upstream queue minus downstream queue.
- `downstream_storage`: penalty or correction when residual receiving capacity is low.
- `spillback`: penalty when downstream spillback/blocking flags bind.
- `switching`: penalty for switching away from current phase when switching loss applies.
- `service`: service urgency correction, preferably favoring high upstream urgency while preserving slack recovery when neutral.
- `incident`: penalty when downstream incident/capacity-drop metadata lowers effective capacity.
- `total`: sum of components.

Phase scores should aggregate movement decompositions for green movements in each candidate phase and expose enough detail to show which term changed action relative to `max_pressure` in binding fixtures.

### D-08-03 Slack Reduction

When residual receiving capacity is positive, spillback/blocking is false, incident inactive, switching penalty neutral/zero, and service correction is ranking-neutral, finite-storage action must match or tie `max_pressure` on deterministic fixtures.

### D-08-04 Binding Separation

When a pressure-preferred phase sends flow into a blocked or capacity-constrained downstream link, finite-storage scoring should select a different feasible phase if the correction exceeds the pressure gap. Tests should reuse the Phase 7 example values or a direct equivalent.

### D-08-05 Runtime Row Audit

Closed-loop rows for the new controller should include score decomposition audit data. Prefer a compact row-level field such as `score_decomposition` or `action_decomposition` that records at least the last action decision per TLS, including pressure action, finite-storage action, selected action, selected phase scores, and component totals.

### Claude's Discretion

- **Controller name:** use `finite_storage_primal_dual` as the safe successor; keep `full_dual_symbolic` not feasible for now.
- **Initial correction formula:** mirror Phase 7 analytic storage/spillback correction and extend with switching/service/incident terms as explicit additive components.
- **SUMO dependency in tests:** core controller behavior should be pure unit tests; only existing lightweight `run_experiment` not-feasible patterns should be used unless a smoke run is already cheap and reliable.
- **Claim language:** controller implementation supports auditability only; no dominance claim in Phase 8.

### Deferred Ideas (OUT OF SCOPE)

- Gate A/B/C implementation — Phase 9 and Phase 11.
- Strong baselines and stress scenario suite — Phase 10.
- Long-horizon paired-seed evidence — Phase 11.
- Future manuscript-input templates — Phase 12.
- Any broad closed-loop dominance claim.
- Removing `full_dual_symbolic` safety guard without a tested safe successor.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CTRL-01 | A live finite-storage primal-dual pressure controller computes movement/phase scores using queue pressure plus downstream storage, spillback, switching, service, and incident shadow-price corrections. | Use the pure helper design and score component formulas in this research. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md] |
| CTRL-02 | `full_dual_symbolic` or its finite-storage successor is safely wired into closed-loop SUMO without relabeling unsafe queue heuristics as the proposed method. | Add `finite_storage_primal_dual` to `CONTROLLER_REGISTRY`; keep `full_dual_symbolic` in `NOT_FEASIBLE_CONTROLLERS`. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| CTRL-03 | The controller reduces to the existing pressure-equivalent behavior in slack regimes according to deterministic unit or fixture tests. | Reuse the Phase 7 `slack_recovery` fixture pattern: finite-storage scores equal pressure scores when corrections are neutral. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json] |
| CTRL-04 | Controller outputs include auditable score decompositions showing which shadow-price terms changed the action in binding regimes. | Add row-level `action_decomposition`/`score_decomposition` for the new controller path without adding it to aggregate `METRIC_FIELDS`. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md] |
</phase_requirements>

## Summary

Phase 8 should implement a new closed-loop controller named `finite_storage_primal_dual`, not repurpose the old `full_dual_symbolic` label. The current runner already has a safe controller registry, a not-feasible guard for unsafe controllers, a phase scoring pipeline, and row-level finite-storage/objective schema validation. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

The safe implementation path is to keep current `choose_controller_action() -> phase_score() -> movement_score()` behavior intact for existing controllers, add pure decomposition helpers for the new controller, and have the SUMO loop store the latest per-TLS action audit for completed `finite_storage_primal_dual` rows. This avoids changing metric aggregation and preserves Phase 6 schema contracts. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

**Primary recommendation:** Add `finite_storage_primal_dual` as a selectable controller with pure additive score decompositions and compact row-level `action_decomposition`; keep `full_dual_symbolic` explicitly `not_feasible` until a later deliberate alias decision is tested. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

## Project Constraints (from CLAUDE.md)

- Reply and planning-facing prose should be in Simplified Chinese for this user. [CITED: /home/samuel/.claude_codex/CLAUDE.md]
- Do not modify source code during this research phase; the user requested read-only research plus writing this planning artifact. [CITED: user request]
- New Python additions should use lowercase snake_case names, small single-purpose functions, 4-space indentation, PEP 8 style, and explicit exceptions for validation failures. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- New OR/SUMO logic should stay under `scripts/` rather than inside `pi_light_code/`, because `scripts/` is the project’s OR experiment layer and `pi_light_code/` is upstream PI-Light/CityFlow code. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Script orchestration should use `main() -> None` with `if __name__ == "__main__":` for new standalone scripts, though Phase 8 likely only changes existing script helpers. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Shared data returned from helpers should be JSON-serializable dictionaries suitable for experiment artifacts. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Do not deepen dynamic code execution or mix SUMO `.net.xml` directly into PI-Light CityFlow agents. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Live action selection | `scripts/run_closed_loop_sumo.py` controller layer | SUMO TraCI runtime | Current action decisions are made during the warmup/action-interval loop and applied through `traci.trafficlight.setPhase`. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Movement/phase score decomposition | Pure helper layer in `scripts/run_closed_loop_sumo.py` | Phase 7 static checker concepts | Existing `movement_score()` and `phase_score()` are pure functions over queues/capacities; Phase 7 supplies the slack/binding decomposition pattern. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Explicit finite-storage state | `scripts/finite_storage_schema.py` | Closed-loop row builder | `build_finite_storage_state()` and validators define required state fields and are already used by completed/not-feasible closed-loop rows. [CITED: /home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py] |
| Objective components | `scripts/finite_storage_schema.py` | `aggregate_metrics()` | `build_objective_components_from_metrics()` is already used to populate row-level `objective_components`. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Controller feasibility guard | `NOT_FEASIBLE_CONTROLLERS` | `CONTROLLER_REGISTRY` | `run_experiment()` returns an explicit not-feasible row before SUMO execution when a controller is guarded. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Row-level action audit | Completed row payload | Renderer/aggregation should ignore unless explicitly surfaced | Existing validators allow extra row keys, while aggregators intentionally exclude `objective_components` and should similarly not aggregate audit blobs. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py] |

## Current Closed-Loop Action Selection Architecture and Safe Entry Points

### Existing data flow

```text
CLI args
  -> validate_args(controller in CONTROLLER_REGISTRY)
  -> run_experiment()
     -> if controller in NOT_FEASIBLE_CONTROLLERS: infeasible_row()
     -> parse SUMO net metadata, TLS phases, TLS movements, capacities
     -> TraCI simulation loop
        -> every action_interval after warmup:
           queues = edge halting numbers
           choose_controller_action(controller, tls_id, current_phase, ...)
             -> fixed_time fallback OR scored green phase list
             -> phase_score(controller, phase_idx, ...)
                -> movement_score(controller, movement, queues, capacities, seed)
           -> set target phase through TraCI transition logic
     -> aggregate_metrics()
     -> build_completed_finite_storage_state()
     -> validate_closed_loop_row()
``` 

This flow is verified in local code: `run_experiment()` checks `NOT_FEASIBLE_CONTROLLERS` before SUMO setup, gets queues from `traci.edge.getLastStepHaltingNumber`, calls `choose_controller_action()` inside the action-interval loop, and writes validated row fields after closing TraCI. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

### Safe entry points

1. **Registry entry:** add `finite_storage_primal_dual` to `CONTROLLER_REGISTRY` only. Do not remove `full_dual_symbolic` from `NOT_FEASIBLE_CONTROLLERS`. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]
2. **Pure score helpers:** add helpers adjacent to `movement_score()` / `phase_score()` so deterministic unit tests can call them without SUMO. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
3. **Selection wrapper:** keep `choose_controller_action()` returning `int` for compatibility, but add a pure `select_finite_storage_action_with_audit()` helper returning both selected phase and audit dictionary. [ASSUMED]
4. **Runtime audit capture:** inside `run_experiment()`, store `latest_action_decomposition_by_tls[tls_id]` only when `controller == "finite_storage_primal_dual"`, then add it to the completed row. [ASSUMED]
5. **Schema preservation:** do not add the audit field to `METRIC_FIELDS`, because metric aggregation currently treats `METRIC_FIELDS` as scalar closed-loop metrics. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| Python | 3.14.4 | Implements OR/SUMO scripts and tests | Host runtime is available and existing project scripts are Python. [VERIFIED: local command `python3 --version`] |
| SUMO | 1.26.0 | Closed-loop traffic simulation runtime | Existing networks and closed-loop runner use SUMO/TraCI. [VERIFIED: local command `sumo --version`] |
| TraCI / sumolib | import OK | SUMO control and network metadata access | `run_closed_loop_sumo.py` imports `traci`, and local import probe succeeded. [VERIFIED: local command `import traci, sumolib`] |
| pytest | 9.0.2 | Unit/contract tests | Existing tests are pytest-compatible and `python3 -m pytest --version` succeeded. [VERIFIED: local command `python3 -m pytest --version`] |
| `scripts/finite_storage_schema.py` | local | Finite-storage state/objective schema validation | It defines required fields, builders, and validators already consumed by closed-loop rows. [CITED: /home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py] |
| `scripts/run_closed_loop_sumo.py` | local | Live controller registry, action selection, SUMO runner, row schema | It is the current closed-loop action selection and output surface. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |

### Supporting

| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| `scripts/check_theory_separation.py` | local | Static slack/binding theory fixture generator | Use values/patterns from Phase 7 tests; do not import it into live runtime unless necessary. [CITED: /home/samuel/projects/pi_light_OR/scripts/check_theory_separation.py] |
| `experiments/dual_sensitivity/phase7_theory_separation.json` | generated 2026-05-24 | Canonical slack and binding examples | Use as fixture reference for CTRL-03/CTRL-04 deterministic tests. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json] |
| `tests/test_closed_loop_sumo.py` | local | Existing closed-loop contracts | Extend with controller registry, guard, decomposition, and schema tests. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| New `finite_storage_primal_dual` controller | Alias `full_dual_symbolic` immediately | Alias is unsafe because current `full_dual_symbolic` is explicitly not feasible due to unsafe per-TLS dual Scenario conversion. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Pure helper tests | Full SUMO smoke test for every behavior | Pure tests are faster and directly validate slack/binding logic without simulation noise; SUMO smoke can remain optional. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md] |
| Row-level audit blob | Adding decomposition terms to `METRIC_FIELDS` | `METRIC_FIELDS` is scalar metric schema; adding nested audit data there would risk breaking aggregation/rendering assumptions. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |

**Installation:** No new external packages should be installed for Phase 8. [CITED: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md]

## Package Legitimacy Audit

Not applicable: Phase 8 should use existing Python/SUMO/pytest dependencies and local modules only; no new package installation is recommended. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

## Architecture Patterns

### System Architecture Diagram

```text
SUMO simulation state
  -> edge queues/capacities/current TLS phase
  -> finite_storage_state builder for current decision state
  -> finite_storage_primal_dual decomposition helpers
       movement components:
         pressure + downstream_storage + spillback + service + incident
       phase components:
         sum(green movement components) + switching penalty
  -> select finite-storage action and pressure reference action
  -> TraCI phase transition logic
  -> row metrics + finite_storage_state + objective_components + action_decomposition
  -> JSON payload / downstream reports
```

This design keeps live actuation inside the existing SUMO runner and keeps decomposition helpers testable without SUMO. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

### Recommended Project Structure

```text
scripts/
├── run_closed_loop_sumo.py      # add registry entry, pure helpers, audit capture
└── finite_storage_schema.py     # reuse existing state/objective validators; do not duplicate

tests/
└── test_closed_loop_sumo.py     # add CTRL-01~CTRL-04 unit/contract tests
```

This structure follows current project conventions: OR/SUMO experiment code belongs in `scripts/`, and closed-loop tests already live in `tests/test_closed_loop_sumo.py`. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]

### Pattern 1: Additive Score Decomposition

**What:** Compute every movement score as a dictionary with fixed keys, then set `total = sum(non_total_components)`. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

**When to use:** Use for `finite_storage_primal_dual` only; keep existing controller formulas unchanged. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

**Recommended helper signatures:**

```python
def finite_storage_movement_score_decomposition(
    movement: tuple[str, str],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    *,
    weights: dict[str, float] | None = None,
) -> dict[str, float]:
    ...


def finite_storage_phase_score_decomposition(
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    *,
    current_phase: int | None,
    action_interval: int,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    ...


def select_finite_storage_action_with_audit(
    tls_id: str,
    current_phase: int,
    step: int,
    action_interval: int,
    phase_states: dict[str, list[str]],
    tls_movements: dict[str, list[tuple[str, str]]],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    *,
    seed: int = 0,
) -> dict[str, Any]:
    ...
```

These names follow project snake_case function conventions and keep data JSON-serializable. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]

### Pattern 2: Pressure Reference Plus Finite-Storage Action Audit

**What:** Select the new action while also computing the pressure-only reference action over the same green phases. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

**When to use:** Use inside `select_finite_storage_action_with_audit()` so binding tests can prove `action_changed_vs_pressure == True` and identify nonzero correction terms. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json]

**Audit fields should include:** `pressure_action`, `finite_storage_action`, `selected_action`, `pressure_phase_scores`, `finite_storage_phase_scores`, `selected_phase_components`, `action_changed_vs_pressure`, and `changing_terms`. [ASSUMED]

### Pattern 3: Existing Not-Feasible Honesty Guard

**What:** Keep `full_dual_symbolic` in `NOT_FEASIBLE_CONTROLLERS` and add a test asserting it remains guarded. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

**When to use:** Until a later phase explicitly aliases `full_dual_symbolic` to the safe finite-storage path. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

### Anti-Patterns to Avoid

- **Relabeling unsafe `full_dual_symbolic`:** The old label is guarded because live per-TLS dual Scenario conversion is not safe; do not present it as implemented by merely changing registry text. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
- **Nested audit data in `METRIC_FIELDS`:** `METRIC_FIELDS` is for scalar metrics such as travel time, queues, spillback counts, switching counts, and runtime. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
- **Duplicating schema validators:** Use `validate_finite_storage_state()` and `validate_state_objective_sample()` instead of custom validation. [CITED: /home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py]
- **Claiming closed-loop dominance:** Phase 8 is controller/audit implementation only; dominance, paired seeds, and gates belong to later phases. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

## Recommended Controller Naming / Registry / NOT_FEASIBLE Strategy

| Item | Recommendation | Rationale |
|------|----------------|-----------|
| New controller name | `finite_storage_primal_dual` | Context locks this as the safe default successor. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md] |
| Registry text | “Finite-storage primal-dual pressure with auditable storage/spillback/switching/service/incident decomposition.” | The text should distinguish it from pressure-only and old unsafe dual labels. [ASSUMED] |
| `NOT_FEASIBLE_CONTROLLERS` | Do not include `finite_storage_primal_dual`; keep `full_dual_symbolic` guarded | `run_experiment()` blocks guarded controllers before SUMO execution; keeping `full_dual_symbolic` guarded preserves honesty. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Default CLI controllers | Leave default as `list(CONTROLLER_REGISTRY)` only if planner accepts new controller appearing in default smoke runs | Current CLI defaults to all registry entries, so adding this controller can cause it to run in broad smoke commands. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Future alias | Defer `full_dual_symbolic -> finite_storage_primal_dual` alias | Context says alias only after tested safe scoring/decomposition exists. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md] |

## Recommended Pure Helper Function Design

### 1. Movement score decomposition

Return exactly these numeric keys for every movement: `pressure`, `downstream_storage`, `spillback`, `switching`, `service`, `incident`, `total`. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

Inputs should be only movement, queue/capacity maps, a validated `finite_storage_state`, and optional weights. This makes the helper deterministic and unit-testable without TraCI. [CITED: /home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py]

### 2. Phase score decomposition

For each candidate phase, iterate over its SUMO phase-state string and aggregate only movements whose signal is `G` or `g`, matching existing `phase_score()` behavior. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

The phase helper should return:

```python
{
    "phase_index": phase_index,
    "components": {"pressure": ..., "downstream_storage": ..., "spillback": ..., "switching": ..., "service": ..., "incident": ..., "total": ...},
    "movement_components": [
        {"movement": [upstream, downstream], "components": {...}},
    ],
}
```

The movement list uses JSON arrays rather than tuples once serialized in rows. [ASSUMED]

### 3. Action selection with audit

The selection helper should compute finite-storage phase scores and separate pressure-only phase scores, then select by `(score, -phase_idx, phase_idx)` to preserve the existing deterministic tie-break pattern. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

Return shape:

```python
{
    "schema_version": "phase8_score_decomposition_v1",
    "controller": "finite_storage_primal_dual",
    "tls_id": tls_id,
    "step": step,
    "current_phase": current_phase,
    "pressure_action": pressure_action,
    "finite_storage_action": finite_storage_action,
    "selected_action": finite_storage_action,
    "action_changed_vs_pressure": finite_storage_action != pressure_action,
    "pressure_phase_scores": {"0": 15.0, "1": 10.0},
    "finite_storage_phase_scores": {"0": 10.0, "1": 13.0},
    "phase_decompositions": {"0": {...}, "1": {...}},
    "changing_terms": ["downstream_storage", "spillback"],
}
```

The field names align with Phase 8 context requirements and Phase 7 artifact concepts. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

## Score Component Keys and Formula Recommendations

### Required keys

| Key | Recommended formula | Notes |
|-----|---------------------|-------|
| `pressure` | `q_up - q_down` | Existing max-pressure formula and Phase 7 sign convention. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| `downstream_storage` | `-w_storage * max(0, effective_service - residual_receiving_capacity[downstream])` | Activates only when downstream cannot receive the effective service amount; preserves slack equality when residual is adequate. [ASSUMED] |
| `spillback` | `-w_spillback * effective_service` when downstream `spillback` or `blocking` is true, else `0.0` | Mirrors Phase 7 blocked downstream penalty in a decomposed form. [CITED: /home/samuel/projects/pi_light_OR/scripts/check_theory_separation.py] |
| `switching` | phase-level `-w_switching * switching_lost_time` when candidate phase differs from current phase and switching penalty applies, else `0.0` | Switching depends on candidate phase, so compute it during phase decomposition while still exposing the same key. [CITED: /home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py] |
| `service` | `w_service * max(0, service_urgency[upstream] - service_neutral_threshold)` | Use neutral threshold so ordinary slack states remain pressure-equivalent. [ASSUMED] |
| `incident` | `-w_incident * (1 - factor) * effective_service` if incident active on downstream edge, else `0.0` | Extends the Phase 7 incident penalty pattern to live decomposition. [CITED: /home/samuel/projects/pi_light_OR/scripts/check_theory_separation.py] |
| `total` | sum of all previous components | Tests should assert exact sum within float tolerance. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md] |

### Recommended default parameters

| Parameter | Initial value | Why |
|-----------|---------------|-----|
| `effective_service` | `min(q_up, max(1.0, min(capacity_up, capacity_down, 10.0)))` if capacities exist; otherwise `min(q_up, 10.0)` | Gives Phase 7-like `10.0` correction on the canonical binding fixture while avoiding arbitrary unbounded penalties. [ASSUMED] |
| `w_storage` | `0.5` | Splits Phase 7 blocked-downstream correction across residual scarcity and spillback flags. [ASSUMED] |
| `w_spillback` | `0.5` | With `effective_service=10`, storage+spillback total `-10` under zero residual/blocking, matching Phase 7 separation magnitude. [ASSUMED] |
| `w_switching` | `1.0` | Matches objective component interpretation where switching lost time is a nonnegative penalty. [CITED: /home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py] |
| `w_service` | `1.0`, with neutral threshold `1.0` | Allows explicit high-urgency overrides while keeping ordinary occupancy-derived `<=1` urgency neutral. [ASSUMED] |
| `w_incident` | `1.0` | Scales penalty by lost receiving/service fraction. [ASSUMED] |

### Slack and binding behavior check

- Slack fixture: residual receiving capacity exceeds `effective_service`, spillback/blocking are false, incident inactive, switching neutral, and service urgency does not exceed threshold; all correction terms are zero and finite-storage scores equal pressure scores. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json]
- Binding fixture: pressure gap is `20 - 13 = 7`, blocked `phase_a` receives storage+spillback penalty around `-10`, and finite-storage selects `phase_b`. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json]

## Row-Level Audit Field Recommendation

### Field name

Use `action_decomposition` as the compact row-level field for completed `finite_storage_primal_dual` rows. [ASSUMED]

### Recommended row shape

```python
row["action_decomposition"] = {
    "schema_version": "phase8_score_decomposition_v1",
    "controller": "finite_storage_primal_dual",
    "decision_scope": "last_action_decision_per_tls",
    "last_decision_by_tls": {
        tls_id: audit_dict,
    },
}
```

This shape is compact and satisfies the context requirement to expose last action decision per TLS with pressure action, finite-storage action, selected action, phase scores, and component totals. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

### How not to break existing metrics/schema

- Do not add `action_decomposition` to `METRIC_FIELDS`; it is nested audit data, not a scalar metric. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
- Keep existing row fields `finite_storage_state` and `objective_components` exactly as required by Phase 6. [CITED: /home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py]
- Keep `validate_closed_loop_row(row)` unchanged unless adding an optional validator for `action_decomposition`; existing row validation only requires finite-storage state and objective components. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
- Renderers and aggregators should ignore the nested audit by default, just as current aggregation excludes `objective_components`. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py]
- Not-feasible rows for `full_dual_symbolic` should remain schema-valid with unavailable finite-storage state and zero objective components; they do not need fake action decompositions. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Finite-storage state validation | Ad-hoc required-key checks | `validate_finite_storage_state()` | Existing validator checks nested spillback, switching, incident, and numeric fields. [CITED: /home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py] |
| Objective component construction | New objective formula builder | `build_objective_components_from_metrics()` | Phase 6 made this the shared row-level helper. [CITED: /home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py] |
| Controller feasibility handling | Silent fallback to pressure | `NOT_FEASIBLE_CONTROLLERS` and explicit `infeasible_row()` | Current code emits honest not-feasible rows with schema-valid finite-storage state/objective fields. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Slack/binding examples | New unrelated toy numbers | Phase 7 `slack_recovery` and `storage_binding_two_phase_separation` values | Phase 7 artifacts already passed THRY-01~THRY-04 checks. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json] |
| SUMO topology parsing | Re-parse inside every helper | Existing `read_tls_phase_states()` and `read_tls_link_movements()` | Current runner already maps TLS states and movements from `.net.xml`. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |

**Key insight:** Phase 8 is mainly safe integration and auditability; hand-rolling schema, feasibility, or topology logic would increase risk without adding scientific value. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Accidentally rebranding `full_dual_symbolic`

**What goes wrong:** The planner removes `full_dual_symbolic` from `NOT_FEASIBLE_CONTROLLERS` and routes it through old pressure/queue heuristics. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]  
**Why it happens:** `full_dual_symbolic` is already in the registry, so it looks selectable. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]  
**How to avoid:** Add a new `finite_storage_primal_dual` controller and keep a guard test for `full_dual_symbolic`. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]  
**Warning signs:** `test_not_feasible_controller_metadata()` no longer sees `feasibility_status == "not_feasible"`. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py]

### Pitfall 2: Breaking slack reduction with always-on corrections

**What goes wrong:** Downstream storage or service terms are nonzero in ordinary slack states, so the finite-storage action diverges from max-pressure. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json]  
**Why it happens:** Formulas based on continuous occupancy ratios can perturb rankings even when constraints are not binding. [ASSUMED]  
**How to avoid:** Gate correction terms so they are zero when residual receiving capacity is adequate, spillback/blocking false, incident inactive, switching neutral, and service urgency neutral. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]  
**Warning signs:** Deterministic slack fixture finite-storage scores are not equal to pressure scores. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json]

### Pitfall 3: Double-counting storage and spillback

**What goes wrong:** A blocked downstream link receives both a full residual-capacity penalty and a full spillback penalty, making the controller overreact. [ASSUMED]  
**Why it happens:** `downstream_storage` and `spillback` represent related scarcity signals. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]  
**How to avoid:** Calibrate initial weights so the canonical Phase 7 binding correction total is about `-10`, not `-20`. [CITED: /home/samuel/projects/pi_light_OR/scripts/check_theory_separation.py]  
**Warning signs:** Binding fixture separates for the wrong reason, or `changing_terms` shows extreme totals inconsistent with Phase 7. [ASSUMED]

### Pitfall 4: Making audit data too large or non-serializable

**What goes wrong:** Row output contains tuple keys, raw objects, or per-step audit histories that bloat JSON artifacts. [ASSUMED]  
**Why it happens:** SUMO loops run repeatedly, and Python tuples/dicts can serialize awkwardly if used as object keys. [ASSUMED]  
**How to avoid:** Store only the last decision per TLS and convert movement tuples to arrays or strings. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]  
**Warning signs:** `json.dumps(payload)` fails or artifact size grows unexpectedly. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

## Code Examples

### Existing pressure action pattern

```python
scored = [
    (phase_score(controller, phase_idx, states, tls_movements.get(tls_id, []), queues, capacities, seed), -phase_idx, phase_idx)
    for phase_idx in greens
]
return max(scored)[2] if scored else current_phase
```

This is the existing deterministic phase selection pattern; the new finite-storage selector should preserve tie behavior. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

### Existing Phase 7 finite-storage static correction pattern

```python
score = pressure_score(movement, queues)
flags = state["spillback_blocking"].get(downstream, {})
if isinstance(flags, dict) and flags.get("blocking"):
    score -= 10.0
incident = state["incident_capacity_drop"]
if incident["active"] and incident["edge"] == downstream:
    score -= 5.0 * (1.0 - float(incident["factor"]))
```

This is static theory-checker code, not live runtime code; Phase 8 should decompose equivalent corrections into named audit components. [CITED: /home/samuel/projects/pi_light_OR/scripts/check_theory_separation.py]

### Existing completed row schema pattern

```python
"finite_storage_state": build_completed_finite_storage_state(
    latest_queues,
    capacities,
    current_phase=latest_current_phase,
    time_since_switch=latest_time_since_switch,
    incident_edge=target_edge if failure_mode_mechanism else None,
    capacity_drop_factor=0.35 if failure_mode_mechanism else None,
)
```

The new controller should use the same schema family for decision-state audit and completed row validation. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

## State of the Art Within This Codebase

| Old Approach | Current Phase 8 Approach | When Changed | Impact |
|--------------|--------------------------|--------------|--------|
| Pressure-equivalent v1.0 evidence | Bounded v1.1 finite-storage separation only when constraints bind | v1.1 roadmap | Prevents universal superiority claims. [CITED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md] |
| `full_dual_symbolic` in registry but not feasible | New `finite_storage_primal_dual` safe successor | Phase 8 | Avoids unsafe relabeling. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md] |
| Static Phase 7 score separation | Live runtime score decomposition and row audit | Phase 8 | Converts theory fixture logic into actuation-ready but claim-bounded implementation. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/07-theory-and-separation-package/07-01-SUMMARY.md] |
| Row-level finite-storage state only | Row-level finite-storage state plus action decomposition for the new controller | Phase 8 | Enables CTRL-04 auditability. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md] |

**Deprecated/outdated:** Treating v1.0 pressure-equivalent artifacts as dual superiority evidence is explicitly out of scope for v1.1. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]

## Test Plan

### CTRL-01: component keys and totals

- Add a pure unit test that calls `finite_storage_movement_score_decomposition()` and asserts keys exactly equal `{pressure, downstream_storage, spillback, switching, service, incident, total}`. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]
- Assert `total == pressure + downstream_storage + spillback + switching + service + incident` within float tolerance. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

### CTRL-03: slack reduction

- Build the Phase 7 `slack_recovery` queues/movements/state as a deterministic fixture. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json]
- Assert pressure phase scores and finite-storage phase scores are equal, or at least select the same/tied action. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json]

### CTRL-04: binding separation and audit

- Build the Phase 7 `storage_binding_two_phase_separation` fixture. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json]
- Assert pressure selects `phase_a`, finite-storage selects `phase_b`, `action_changed_vs_pressure` is true, and `changing_terms` includes `downstream_storage` and/or `spillback`. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json]

### CTRL-02: registry/selectability and guard

- Extend `test_controller_registry_smoke_names()` to include `finite_storage_primal_dual`. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py]
- Add a test that `choose_controller_action("finite_storage_primal_dual", ...)` returns the expected binding action. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
- Keep or add a test that `run_experiment(..., controller="full_dual_symbolic")` still returns `feasibility_status == "not_feasible"`. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py]

### Row audit

- Add a synthetic completed-row test or lightweight `run_experiment()` test verifying `action_decomposition` exists for `finite_storage_primal_dual` completed rows and contains `last_decision_by_tls`. [ASSUMED]
- Assert not-feasible rows remain schema-valid and are not forced to include fake action decompositions. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | Unit tests and scripts | ✓ | 3.14.4 | None needed. [VERIFIED: local command `python3 --version`] |
| pytest | Validation architecture | ✓ | 9.0.2 | Use direct `python3 tests/test_closed_loop_sumo.py` smoke only if pytest unavailable. [VERIFIED: local command `python3 -m pytest --version`] |
| SUMO | Optional closed-loop smoke | ✓ | 1.26.0 | Pure unit tests cover core logic if SUMO smoke is skipped. [VERIFIED: local command `sumo --version`] |
| TraCI / sumolib | SUMO runner imports | ✓ | import succeeded | No fallback for real SUMO run; pure tests avoid runtime dependency. [VERIFIED: local command `import traci, sumolib`] |

**Missing dependencies with no fallback:** none found for Phase 8 planning. [VERIFIED: local commands]

**Missing dependencies with fallback:** none found. [VERIFIED: local commands]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 [VERIFIED: local command `python3 -m pytest --version`] |
| Config file | none detected in required files; tests are runnable directly by module path. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py] |
| Quick run command | `python3 -m pytest tests/test_closed_loop_sumo.py -q` |
| Full relevant suite command | `python3 -m pytest tests/test_closed_loop_sumo.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CTRL-01 | Decomposition exposes required component keys and sums totals correctly | unit | `python3 -m pytest tests/test_closed_loop_sumo.py -q` | ✅ extend existing file [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py] |
| CTRL-02 | `finite_storage_primal_dual` is registered/selectable and `full_dual_symbolic` remains not feasible | unit/contract | `python3 -m pytest tests/test_closed_loop_sumo.py -q` | ✅ extend existing file [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py] |
| CTRL-03 | Slack fixture matches/ties max-pressure | unit | `python3 -m pytest tests/test_closed_loop_sumo.py -q` | ✅ extend existing file [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json] |
| CTRL-04 | Binding fixture changes action and row audit identifies changing terms | unit/contract | `python3 -m pytest tests/test_closed_loop_sumo.py -q` | ✅ extend existing file [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json] |

### Sampling Rate

- **Per task commit:** `python3 -m pytest tests/test_closed_loop_sumo.py -q`
- **Per wave merge:** `python3 -m pytest tests/test_closed_loop_sumo.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q`
- **Phase gate:** Add a short closed-loop command only after pure tests pass; do not use it to claim dominance. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

### Wave 0 Gaps

- [ ] Extend `tests/test_closed_loop_sumo.py` with pure finite-storage decomposition fixtures for CTRL-01/CTRL-03/CTRL-04. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py]
- [ ] Add optional row audit test for `finite_storage_primal_dual` completed row if a cheap SUMO smoke remains reliable. [ASSUMED]
- [ ] No new framework install required. [VERIFIED: local command `python3 -m pytest --version`]

## Recommended Verification Commands

Run from `/home/samuel/projects/pi_light_OR`. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]

```bash
python3 -m py_compile scripts/run_closed_loop_sumo.py tests/test_closed_loop_sumo.py
python3 -m pytest tests/test_closed_loop_sumo.py -q
python3 -m pytest tests/test_closed_loop_sumo.py tests/test_theory_separation.py tests/test_finite_storage_schema.py -q
python3 scripts/check_theory_separation.py --out /tmp/phase7_theory_separation_check.json
python3 scripts/run_closed_loop_sumo.py --network single --controllers finite_storage_primal_dual full_dual_symbolic --seeds 20260524 --steps 80 --warmup 20 --action-interval 10 --out /tmp/phase8_controller_smoke.json
```

The final SUMO smoke should verify selectability and not-feasible honesty only; it should not be interpreted as performance evidence. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Local experiment scripts have no authentication surface. [CITED: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md] |
| V3 Session Management | no | No web/session layer exists in Phase 8 scope. [CITED: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md] |
| V4 Access Control | no | Phase 8 does not introduce user roles or remote access. [CITED: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md] |
| V5 Input Validation | yes | Reuse argparse validation, controller registry checks, and finite-storage schema validators. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| V6 Cryptography | no | No cryptography or secrets are involved. [CITED: /home/samuel/projects/pi_light_OR/.planning/PROJECT.md] |

### Known Threat Patterns for This Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unsafe controller relabeling | Tampering/Repudiation | Keep `NOT_FEASIBLE_CONTROLLERS` guard and explicit tests. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Invalid nested JSON audit fields | Tampering | Keep audit JSON-serializable and optionally validate required audit keys. [ASSUMED] |
| Claim overreach from smoke output | Repudiation | Preserve claim framing and avoid dominance language in Phase 8 artifacts. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Correction coefficients change actions in slack regimes | Fails CTRL-03 and undermines theorem alignment | Require zero corrections in slack fixture and test exact/tie recovery. [CITED: /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json] |
| `finite_storage_state` built only at row end, not at decision time | Audit may not correspond to selected action | Build a decision-local finite-storage state inside the action interval loop for the audit helper. [ASSUMED] |
| Default CLI now runs new controller in broad smoke commands | More runtime and possible failures in existing scripts | Add targeted tests first; consider documenting CLI default behavior in plan. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| Renderer/CSV code encounters nested audit | Downstream artifact generation may fail | Keep audit out of metric schema and test renderer still ignores extra row fields. [CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py] |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Add `select_finite_storage_action_with_audit()` rather than changing `choose_controller_action()` return type. | Current Closed-Loop Action Selection Architecture | Planner may prefer a different integration shape, but compatibility risk is lower with a wrapper. |
| A2 | Use `action_decomposition` as the row-level field name. | Row-Level Audit Field Recommendation | If downstream tools expect `score_decomposition`, naming may need adjustment. |
| A3 | Initial coefficients split blocked downstream correction across storage and spillback weights. | Score Component Keys and Formula Recommendations | Poor coefficient calibration could over/under-separate binding fixtures. |
| A4 | Service urgency should be neutral unless it exceeds a threshold. | Score Component Keys and Formula Recommendations | If service should always affect ranking, slack recovery tests may need different neutral fixtures. |
| A5 | Store only last decision per TLS for row audit. | Row-Level Audit Field Recommendation | Later gates may require richer per-step audit history. |

## Open Questions (RESOLVED)

1. **RESOLVED — use `action_decomposition` as the row-level field name.**
   - What we know: Context permits either compact row-level field name. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md]
   - Resolution: Use `action_decomposition` because the row audit is action-selection centered; future Phase 9 gates can consume or rename from this explicit field if needed. [ASSUMED]

2. **RESOLVED — include service as a neutral-by-default component in Phase 8.**
   - What we know: CTRL-01 requires service correction to be represented. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
   - Resolution: Include the `service` component key and keep its default correction neutral unless service urgency exceeds the declared threshold. Add non-neutral service stress tests later only if Phase 9/10 scenarios need them. [ASSUMED]

## Sources

### Primary (HIGH confidence)

- `/home/samuel/projects/pi_light_OR/.planning/phases/08-live-finite-storage-primal-dual-controller/08-CONTEXT.md` — Phase 8 locked decisions, requirements, controller naming, decomposition keys, test expectations.
- `/home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py` — current registry, not-feasible guard, movement/phase/action selection, SUMO loop, row schema.
- `/home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py` — finite-storage state and objective component schemas/builders/validators.
- `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/phase7_theory_separation.json` — canonical slack and binding examples.
- `/home/samuel/projects/pi_light_OR/scripts/check_theory_separation.py` — Phase 7 static scoring formulas and payload generation.
- `/home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py` — existing test contracts for registry, pressure selection, not-feasible rows, schema, renderers.

### Secondary (MEDIUM confidence)

- `/home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_SEPARATION.md` — theory memo explaining bounded static separation and claim guardrails.
- `/home/samuel/projects/pi_light_OR/.planning/PROJECT.md`, `/home/samuel/projects/pi_light_OR/.planning/ROADMAP.md`, `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md`, `/home/samuel/projects/pi_light_OR/.planning/STATE.md` — milestone scope, claim discipline, and phase sequencing.
- `/home/samuel/projects/pi_light_OR/.planning/phases/07-theory-and-separation-package/07-01-SUMMARY.md` — Phase 7 completion decisions and readiness notes.

### Tertiary (LOW confidence)

- None from web search; web was intentionally not used per user instruction.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — local commands verified Python, SUMO, pytest, and TraCI/sumolib availability.
- Architecture: HIGH — based on direct reading of `run_closed_loop_sumo.py` and `tests/test_closed_loop_sumo.py`.
- Score formulas: MEDIUM — component keys and slack/binding behavior are locked by context and Phase 7, but coefficient split is an initial design recommendation.
- Pitfalls: HIGH for relabeling/schema/claim risks; MEDIUM for coefficient calibration risks.

**Research date:** 2026-05-24  
**Valid until:** 2026-06-23 for architecture; coefficient recommendations should be revisited after Phase 8 tests.
