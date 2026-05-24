# Phase 11: Long-Horizon Paired-Seed Evidence - Pattern Map

**Mapped:** 2026-05-24
**Files analyzed:** 3
**Analogs found:** 3 / 3

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/run_phase11_paired_evidence.py` | runner / utility / gate | batch + file-I/O + transform | `scripts/run_closed_loop_suite.py`, `scripts/run_slack_binding_gates.py`, `scripts/run_closed_loop_sumo.py` | exact for runner/gate shape; partial for paired bootstrap |
| `tests/test_phase11_paired_evidence.py` | test | transform + batch | `tests/test_closed_loop_sumo.py`, `tests/test_slack_binding_gates.py` | exact |
| `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` | generated artifact | file-I/O + batch | `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` | role-match |

## Pattern Assignments

### `scripts/run_phase11_paired_evidence.py` (runner / utility / gate, batch + file-I/O + transform)

**Primary analogs:**
- `scripts/run_closed_loop_suite.py` for profile/spec construction, controller/scenario constants, SUMO orchestration, aggregate/artifact writing.
- `scripts/run_slack_binding_gates.py` for fail-closed gate functions and payload validation.
- `scripts/run_closed_loop_sumo.py` for simulation primitive, row schema, finite-storage/action-decomposition validation.

**Imports pattern** — use stdlib-first, `Path`, `Any`, local script imports directly from `scripts/` (source: `scripts/run_closed_loop_suite.py` lines 1-13):
```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from finite_storage_schema import FINITE_STORAGE_STATE_FIELDS, OBJECTIVE_COMPONENT_FIELDS
from run_closed_loop_sumo import CONTROLLER_REGISTRY, METRIC_FIELDS, NOT_FEASIBLE_CONTROLLERS, load_route_metadata, run_experiment
```

For paired statistics, extend this import pattern with SciPy only where needed, matching RESEARCH.md guidance:
```python
from scipy import stats
```

**Controller/scenario declaration pattern** — copy the explicit constant style but narrow Phase 11 to binding evidence and strong comparators (source: `scripts/run_closed_loop_suite.py` lines 16-24, 40-84):
```python
REQUIRED_STRONG_BASELINES = [
    "fixed_time",
    "actuated_local_pressure",
    "max_pressure",
    "capacity_aware_pressure",
    "cycle_pressure",
    "finite_storage_double_pressure",
    "finite_storage_primal_dual",
]
```
```python
SCENARIOS = [
    ("single_sanity", "single"),
    ("arterial_main", "arterial"),
    ("grid_scalability", "grid_4x4"),
    ("arterial_demand_shift", "arterial"),
    ("arterial_bottleneck_failure_mode", "arterial"),
    ("arterial_downstream_blockage", "arterial"),
    ("arterial_spillback_stress", "arterial"),
    ("arterial_incident_capacity_drop", "arterial"),
    ("arterial_oversaturation", "arterial"),
    ("arterial_turning_shock", "arterial"),
    ("arterial_switching_loss_sensitive", "arterial"),
]
STRESS_SCENARIO_CATEGORIES = {
    "downstream_blockage": ["arterial_downstream_blockage"],
    "spillback": ["arterial_spillback_stress"],
    "incident_capacity_drop": ["arterial_incident_capacity_drop", "arterial_bottleneck_failure_mode"],
    "oversaturation": ["arterial_oversaturation"],
    "turning_shock": ["arterial_turning_shock", "arterial_demand_shift"],
    "switching_loss_sensitive": ["arterial_switching_loss_sensitive"],
}
STRESS_SCENARIO_MECHANISMS = {
    "arterial_downstream_blockage": "edge_speed_reduction",
    "arterial_spillback_stress": "edge_speed_reduction",
    "arterial_incident_capacity_drop": "edge_speed_reduction",
    "arterial_bottleneck_failure_mode": "edge_speed_reduction",
    "arterial_oversaturation": "traci_vehicle_insertion",
    "arterial_turning_shock": "traci_vehicle_insertion",
    "arterial_demand_shift": "traci_vehicle_insertion",
    "arterial_switching_loss_sensitive": "short_action_interval_switching_audit",
}
```

Phase 11 should define a narrower required binding list from the locked context:
```python
BINDING_EVIDENCE_SCENARIOS = [
    "arterial_downstream_blockage",
    "arterial_spillback_stress",
    "arterial_incident_capacity_drop",
    "arterial_oversaturation",
    "arterial_turning_shock",
    "arterial_switching_loss_sensitive",
]
REQUIRED_GATE_C_COMPARATORS = [
    "max_pressure",
    "capacity_aware_pressure",
    "finite_storage_double_pressure",
]
PROPOSED_CONTROLLER = "finite_storage_primal_dual"
```

**CLI pattern** — copy `parse_args()` structure, but use Phase 11 defaults: `--profile pilot|main`, `--steps 3600`, `--warmup 900`, paired seed list, and Phase 11 output path (source: `scripts/run_closed_loop_suite.py` lines 91-102):
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["smoke", "main"], default="smoke")
    parser.add_argument("--controllers", nargs="+", default=DEFAULT_CONTROLLERS)
    parser.add_argument("--arterial-seeds", nargs="+", type=int, default=[20260523, 20260524, 20260525, 20260526, 20260527])
    parser.add_argument("--grid-seeds", nargs="+", type=int, default=[20260601, 20260602, 20260603, 20260604, 20260605])
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--warmup", type=int, default=60)
    parser.add_argument("--action-interval", type=int, default=10)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block4_closed_loop_suite.json")
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    return parser.parse_args()
```

**Spec builder pattern** — copy tuple-to-dict expansion and explicit per-scenario/controller/seed rows. Do not reuse Phase 10 smoke semantics as evidence (source: `scripts/run_closed_loop_suite.py` lines 105-145):
```python
def build_suite_spec(
    profile: str,
    controllers: list[str],
    arterial_seeds: list[int],
    grid_seeds: list[int],
    steps: int,
    warmup: int,
    action_interval: int,
) -> list[dict[str, Any]]:
    if profile == "smoke":
        seeds_by_scenario = {
            scenario_tag: (grid_seeds[:1] if network == "grid_4x4" else arterial_seeds[:1])
            for scenario_tag, network in SCENARIOS
        }
        controllers_by_scenario = {name: controllers for name, _ in SCENARIOS}
    else:
        seeds_by_scenario = {
            scenario_tag: (grid_seeds[:5] if scenario_tag == "grid_scalability" else arterial_seeds[:5] if scenario_tag == "arterial_main" else arterial_seeds[:1])
            for scenario_tag, _network in SCENARIOS
        }
        stress_controllers = [c for c in controllers if c in {"fixed_time", "max_pressure", "capacity_aware_pressure", "cycle_pressure", "finite_storage_double_pressure", "finite_storage_primal_dual"}]
        controllers_by_scenario = {
            scenario_tag: (controllers if scenario_tag in {"single_sanity", "arterial_main", "grid_scalability"} else stress_controllers)
            for scenario_tag, _network in SCENARIOS
        }
    spec = []
    for scenario_tag, network in SCENARIOS:
        for seed in seeds_by_scenario[scenario_tag]:
            for controller in controllers_by_scenario[scenario_tag]:
                spec.append(
                    {
                        "network": network,
                        "scenario_tag": scenario_tag,
                        "controller": controller,
                        "seed": int(seed),
                        "steps": int(steps),
                        "warmup": int(warmup),
                        "action_interval": int(action_interval),
                    }
                )
    return spec
```

Phase 11 modifications:
- `main` profile should use the same seed set for proposed and every comparator per scenario.
- `pilot` may use fewer seeds/shorter horizons but must record actual profile, steps, warmup, and seeds.
- Binding scenarios are the only dominance evidence rows; `single_sanity`, `arterial_main`, and `grid_scalability` are context only.

**SUMO primitive pattern** — call `run_experiment(...)` directly; do not build a new TraCI loop (source: `scripts/run_closed_loop_suite.py` lines 369-389):
```python
def main() -> None:
    args = parse_args()
    unknown = sorted(set(args.controllers) - set(CONTROLLER_REGISTRY))
    if unknown:
        raise ValueError(f"Unknown controllers: {unknown}. Available: {sorted(CONTROLLER_REGISTRY)}")
    route_metadata = load_route_metadata(Path(args.route_json))
    spec = build_suite_spec(args.profile, args.controllers, args.arterial_seeds, args.grid_seeds, args.steps, args.warmup, args.action_interval)
    rows = [run_experiment(**item, route_metadata=route_metadata) for item in spec]
    gates = completion_gates(rows)
    completion_gates_passed = gates_pass(gates) if args.profile == "main" else False
    payload = build_payload(
        profile=args.profile,
        route_metadata=route_metadata,
        rows=rows,
        controllers=args.controllers,
        completion_gates_passed=completion_gates_passed,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "rows": len(rows), "aggregates": len(payload["aggregates"]), "completion_gates_passed": payload["completion_gates_passed"]}, indent=2))
```

**Closed-loop row schema pattern** — rely on these emitted metrics and audit fields (source: `scripts/run_closed_loop_sumo.py` lines 23-36, 410-457):
```python
METRIC_FIELDS = [
    "avg_travel_time",
    "penalized_avg_travel_time",
    "total_delay",
    "completed_vehicles",
    "completion_rate",
    "throughput",
    "mean_queue",
    "max_queue",
    "spillback_count",
    "blocking_count",
    "switching_count",
    "controller_runtime_sec",
]
```
```python
metrics = {
    "avg_travel_time": float(total_travel_time / completed) if completed else 0.0,
    "penalized_avg_travel_time": float(penalized_total / departed_total) if departed_total else 0.0,
    "total_delay": float(waiting_delay),
    "completed_vehicles": int(completed),
    "completion_rate": float(completed / departed_total) if departed_total else 0.0,
    "throughput": float(completed / horizon),
    "mean_queue": float(statistics.fmean(queues) if queues else 0.0),
    "max_queue": float(max(max_queues, default=0.0)),
    "spillback_count": spillback_count,
    "blocking_count": blocking_count,
    "switching_count": int(switching_count),
    "controller_runtime_sec": float(runtime),
    "travel_time_source": "conditional_on_arrival_with_censoring_penalty",
    "unfinished_vehicle_count": int(unfinished),
}
metrics["objective_components"] = build_objective_components_from_metrics(
    {
        "total_delay": metrics["total_delay"],
        "unfinished_vehicle_count": metrics["unfinished_vehicle_count"],
        "spillback_count": spillback_count,
        "blocking_count": blocking_count,
        "switching_count": switching_count,
    },
    horizon=float(horizon),
)
```

**Finite-storage/action-decomposition validation pattern** — Gate C should reuse this row contract and fail if proposed completed rows lack audit data (source: `scripts/run_closed_loop_sumo.py` lines 496-505, 771-776):
```python
def validate_closed_loop_row(row: dict[str, Any]) -> None:
    validate_finite_storage_state(row["finite_storage_state"])
    validate_state_objective_sample(row)
    if row.get("controller") == "finite_storage_primal_dual" and row.get("scenario_status") == "completed":
        action_decomposition = row.get("action_decomposition")
        if not isinstance(action_decomposition, dict):
            raise ValueError("finite_storage_primal_dual completed row requires action_decomposition")
        decisions = action_decomposition.get("last_decision_by_tls")
        if not isinstance(decisions, dict) or not decisions:
            raise ValueError("finite_storage_primal_dual action_decomposition requires nonempty last_decision_by_tls")
```
```python
if controller == "finite_storage_primal_dual":
    row["action_decomposition"] = {
        "controller": "finite_storage_primal_dual",
        "decision_scope": "last_action_decision_per_tls",
        "last_decision_by_tls": latest_action_decomposition_by_tls,
    }
```

**Stress metadata pattern** — Gate C should require explicit metadata, not infer from performance (source: `scripts/run_closed_loop_sumo.py` lines 599-613):
```python
def scenario_stress_metadata(scenario_tag: str) -> dict[str, Any]:
    mapping = {
        "arterial_downstream_blockage": ("downstream_blockage", "edge_speed_reduction"),
        "arterial_spillback_stress": ("spillback", "finite_storage_occupancy_stress"),
        "arterial_incident_capacity_drop": ("incident_capacity_drop", "edge_speed_reduction"),
        "arterial_oversaturation": ("oversaturation", "short_horizon_demand_pressure"),
        "arterial_turning_shock": ("turning_shock", "traci_vehicle_insertion"),
        "arterial_switching_loss_sensitive": ("switching_loss_sensitive", "short_action_interval_switching_audit"),
        "arterial_demand_shift": ("turning_shock", "traci_vehicle_insertion"),
        "arterial_bottleneck_failure_mode": ("incident_capacity_drop", "edge_speed_reduction"),
    }
    if scenario_tag not in mapping:
        return {}
    category, mechanism = mapping[scenario_tag]
    return {"stress_category": category, "stress_mechanism": mechanism}
```

**Fail-closed gate validation pattern** — structure validation as pure functions returning `PASSED`/`FAILED`/`INCONCLUSIVE` or raising `ValueError` on forged/malformed data; never silently skip (source: `scripts/run_slack_binding_gates.py` lines 86-98, 110-135):
```python
def validate_explicit_gate_example(example: dict[str, Any]) -> None:
    if "queues" not in example:
        raise ValueError(f"Example {example.get('name', '<unnamed>')} is missing queues")
    if "finite_storage_state" not in example:
        raise ValueError(f"Example {example.get('name', '<unnamed>')} is missing finite_storage_state")
    if "objective_components" not in example:
        raise ValueError(f"Example {example.get('name', '<unnamed>')} is missing objective_components")
    validate_state_objective_sample(
        {
            "finite_storage_state": example["finite_storage_state"],
            "objective_components": example["objective_components"],
        }
    )
```
```python
def validate_action_audit(audit: dict[str, Any]) -> None:
    required = {
        "pressure_action",
        "finite_storage_action",
        "selected_action",
        "pressure_phase_scores",
        "phase_scores",
        "selected_component_totals",
        "changing_terms",
    }
    missing = required - set(audit)
    if missing:
        raise ValueError(f"Action audit is missing fields: {sorted(missing)}")
    if audit["selected_action"] != audit["finite_storage_action"]:
        raise ValueError("Action audit selected_action must equal finite_storage_action")
```

**Payload scope / forbidden language pattern** — copy recursive key/phrase validation and adapt phrases for Phase 11 claim discipline (source: `scripts/run_slack_binding_gates.py` lines 331-360):
```python
def validate_payload_scope(payload: dict[str, Any]) -> None:
    payload_without_caveats = {key: value for key, value in payload.items() if key != "caveats"}
    normalized_keys = {_normalize_key(key) for key in _collect_keys(payload_without_caveats)}
    forbidden_present = {_normalize_key(key) for key in FORBIDDEN_AFFIRMATIVE_PAYLOAD_KEYS} & normalized_keys
    if forbidden_present:
        raise ValueError(f"Payload contains out-of-scope affirmative keys: {sorted(forbidden_present)}")
    non_caveat_text = json.dumps(payload_without_caveats).lower()
    forbidden_phrases = [phrase for phrase in FORBIDDEN_AFFIRMATIVE_PHRASES if phrase in non_caveat_text]
    if forbidden_phrases:
        raise ValueError(f"Payload contains out-of-scope affirmative language: {forbidden_phrases}")
```

For Phase 11, allowed language is bounded: `closed-loop paired-seed evidence in predeclared binding stress regimes, simulator/network/horizon/seed-relative`. Forbidden language should include universal dominance, deployment readiness, final manuscript claim, broad superiority over max-pressure outside binding regimes, and reuse of Phase 10 as superiority evidence.

**Artifact writing pattern** — use `Path(...).write_text(...)`, create parent directories, print compact JSON summary (source: `scripts/run_slack_binding_gates.py` lines 364-375):
```python
def write_gate_artifact(out_path: Path, phase7_path: Path) -> dict[str, Any]:
    examples = load_phase7_examples(phase7_path)
    payload = build_payload(examples, phase7_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = write_gate_artifact(Path(args.out), Path(args.phase7_json))
    print(json.dumps({"out": args.out, "status": payload["status"], "requirements_covered": payload["requirements_covered"]}, indent=2))
```

**Paired statistics pattern** — no direct in-code analog found. Use RESEARCH.md's official SciPy pattern, but wrap it in project-style pure helpers:
```python
result = stats.bootstrap(
    (paired_differences,),
    lambda x, axis: x.mean(axis=axis),
    paired=True,
    confidence_level=0.95,
    n_resamples=9999,
    method="BCa",
)
ci_low = float(result.confidence_interval.low)
ci_high = float(result.confidence_interval.high)
standard_error = float(result.standard_error)
```

Recommended helper shape:
```python
LOWER_IS_BETTER_METRICS = {
    "penalized_avg_travel_time",
    "total_delay",
    "spillback_count",
    "blocking_count",
    "unfinished_vehicle_count",
    "switching_count",
}
HIGHER_IS_BETTER_METRICS = {"throughput", "completion_rate", "completed_vehicles"}

def paired_difference(proposed: dict[str, Any], comparator: dict[str, Any], metric: str) -> float:
    if metric in LOWER_IS_BETTER_METRICS:
        return float(comparator[metric]) - float(proposed[metric])
    if metric in HIGHER_IS_BETTER_METRICS:
        return float(proposed[metric]) - float(comparator[metric])
    raise ValueError(f"Unknown metric direction for {metric}")
```

### `tests/test_phase11_paired_evidence.py` (test, transform + batch)

**Primary analogs:**
- `tests/test_closed_loop_sumo.py` for imports, synthetic rows, runner/spec/payload tests, direct-script `main()`.
- `tests/test_slack_binding_gates.py` for fail-closed validation tests and forbidden-language tests.

**Imports and path setup pattern** (source: `tests/test_closed_loop_sumo.py` lines 1-49):
```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_closed_loop_sumo import (  # noqa: E402
    CONTROLLER_REGISTRY,
    FINITE_STORAGE_DECOMPOSITION_FIELDS,
    METRIC_FIELDS,
    NOT_FEASIBLE_CONTROLLERS,
    aggregate_metrics,
    apply_failure_mode,
    build_completed_finite_storage_state,
    choose_controller_action,
    finite_storage_movement_decomposition,
    finite_storage_phase_decomposition,
    load_route_metadata,
    resolve_network,
    run_experiment,
    select_finite_storage_action_with_audit,
)
```

For Phase 11, import from `run_phase11_paired_evidence` the pure helpers first: `build_phase11_spec`, `paired_metric_summary`, `evaluate_gate_c`, `build_payload`, and `validate_payload_scope`.

**Spec/profile test pattern** — copy direct construction and assertions against scenario/controller/seed coverage (source: `tests/test_closed_loop_sumo.py` lines 399-415):
```python
def test_suite_spec_contents_and_seed_counts() -> None:
    spec = build_suite_spec(
        profile="main",
        controllers=["fixed_time", "max_pressure", "cycle_pressure", "finite_storage_double_pressure", "finite_storage_primal_dual"],
        arterial_seeds=[1, 2, 3, 4, 5],
        grid_seeds=[6, 7, 8, 9, 10],
        steps=100,
        warmup=20,
        action_interval=10,
    )
    names = {item["scenario_tag"] for item in spec}
    assert {"single_sanity", "arterial_main", "grid_scalability", "arterial_demand_shift", "arterial_bottleneck_failure_mode"} <= names
    assert {tag for tags in STRESS_SCENARIO_CATEGORIES.values() for tag in tags} <= names
    assert len([item for item in spec if item["scenario_tag"] == "arterial_main" and item["controller"] == "fixed_time"]) == 5
    assert len([item for item in spec if item["scenario_tag"] == "grid_scalability" and item["controller"] == "max_pressure"]) == 5
    assert any(item["scenario_tag"] == "arterial_spillback_stress" and item["controller"] == "finite_storage_primal_dual" for item in spec)
```

Phase 11-specific assertions:
- `main` profile defaults are 3600 steps and 900 warmup when invoked via CLI/default args.
- For every binding scenario, proposed and required comparators share identical seed sets.
- `pilot` profile records that it is not journal-grade dominance evidence if using reduced seeds/horizon.

**Synthetic row fixture pattern** — copy compact dictionaries with all `METRIC_FIELDS` and metadata (source: `tests/test_closed_loop_sumo.py` lines 466-521):
```python
def phase10_synthetic_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for controller in REQUIRED_STRONG_BASELINES:
        rows.append(
            {
                "network": "grid_4x4" if controller == "fixed_time" else "arterial",
                "scenario_tag": "grid_scalability" if controller == "fixed_time" else "arterial_main",
                "controller": controller,
                "seed": 1,
                "scenario_status": "completed",
                "feasibility_status": "run",
                "completed_vehicles": 1,
                "completion_rate": 1.0,
                "switching_count": 0 if controller == "fixed_time" else 1,
                **{field: 1.0 for field in METRIC_FIELDS if field not in {"completed_vehicles", "completion_rate", "switching_count"}},
            }
        )
```

Phase 11 synthetic fixtures must add:
- `finite_storage_state`
- `objective_components`
- `stress_category` and `stress_mechanism`
- `action_decomposition` for `finite_storage_primal_dual`
- seed-aligned rows for each `(scenario_tag, comparator, proposed)` pair

**Fail-closed test pattern** — copy try/except assertions that missing required fields raise `ValueError` or produce failed statuses (source: `tests/test_slack_binding_gates.py` lines 82-124):
```python
def test_missing_finite_storage_state_fails_closed() -> None:
    example = copy.deepcopy(slack_example())
    example.pop("finite_storage_state")
    try:
        validate_explicit_gate_example(example)
    except ValueError as exc:
        assert "finite_storage_state" in str(exc)
    else:
        raise AssertionError("missing finite_storage_state should fail closed")
```
```python
def test_missing_action_audit_field_fails_closed() -> None:
    audit = recompute_audit(slack_example())
    audit.pop("selected_action")
    try:
        validate_action_audit(audit)
    except ValueError as exc:
        assert "selected_action" in str(exc)
    else:
        raise AssertionError("missing action audit field should fail closed")
```

Phase 11 tests should cover at least:
- synthetic pass with paired seed rows;
- missing required binding scenario;
- missing `max_pressure`, `capacity_aware_pressure`, or `finite_storage_double_pressure` comparator;
- unpaired seed sets;
- missing/nonnull-invalid `stress_category` or `stress_mechanism`;
- missing `finite_storage_state` / `objective_components`;
- missing proposed `action_decomposition`;
- slack/control rows classified as `slack_regime_recovery_or_context`, not dominance evidence;
- forbidden universal/deployment/manuscript claim text.

**Forbidden language test pattern** (source: `tests/test_slack_binding_gates.py` lines 230-249):
```python
def test_payload_rejects_affirmative_forbidden_language_outside_caveats() -> None:
    payload = build_payload(canonical_examples(), PHASE7_JSON)
    payload["gate_b_binding_separation"]["interpretation"] = "closed-loop dominance"
    try:
        validate_payload_scope(payload)
    except ValueError as exc:
        assert "closed-loop dominance" in str(exc)
    else:
        raise AssertionError("affirmative forbidden language should fail closed")
```

**Direct executable test file pattern** — keep a `main()` that calls each test function and prints one compact success line (source: `tests/test_closed_loop_sumo.py` lines 792-829):
```python
def main() -> None:
    test_controller_registry_smoke_names()
    test_finite_storage_decomposition_keys_and_total()
    test_finite_storage_isolated_correction_terms_are_nonzero()
    test_finite_storage_slack_recovers_pressure_action()
    test_finite_storage_binding_changes_action_and_terms()
    test_choose_controller_action_prefers_pressure_phase()
    test_capacity_aware_penalizes_full_downstream()
    test_phase10_baseline_variants_are_selectable()
    test_metric_aggregation_schema()
    test_completed_finite_storage_state_schema()
    test_not_feasible_controller_has_explicit_state_and_objective_components()
    test_finite_storage_controller_run_experiment_row_audit()
    test_route_metadata_loader()
    test_route_metadata_loader_rejects_missing_route()
    test_network_resolver_supports_phase4_networks()
    test_not_feasible_controller_metadata()
    test_failure_mode_restores_speed_after_window()
    test_suite_spec_contents_and_seed_counts()
    test_aggregate_results_and_completion_gates()
    test_suite_payload_includes_phase6_schema_metadata()
    test_phase10_payload_includes_baseline_stress_and_scope_metadata()
    test_phase10_coverage_fails_closed_when_required_evidence_missing()
    test_renderer_report_and_csv()
    test_renderer_surfaces_phase6_objective_columns()
    test_renderer_rejects_missing_completion_gate()
    test_paper_artifacts_require_phase6_guard_artifacts()
    test_repro_registry_includes_phase6_guard_artifacts()
    test_repro_audit_ignores_policy_metadata_for_forbidden_phrase_scan(Path("/tmp/test_repro_audit_metadata"))
    with tempfile.TemporaryDirectory() as raw_tmp:
        test_repro_audit_fails_expected_json_with_failed_status(Path(raw_tmp))
    test_completion_gates_reject_noop_controller_evidence()
    print("closed-loop SUMO tests ok")
```

### `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` (generated artifact, file-I/O + batch)

**Analog:** `experiments/dual_sensitivity/phase10_baselines_stress_suite.json`

**Top-level artifact shape** — copy explicit top-level status, route metadata, profile, rows, and caveats, but Phase 11 must not claim Phase 10 smoke evidence as dominance evidence (source: `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` lines 1-8):
```json
{
  "experiment": "phase10_baselines_stress_suite",
  "status": "SMOKE_ONLY",
  "route_decision": "pressure-equivalent",
  "route_confidence": "MEDIUM",
  "route_json": "experiments/dual_sensitivity/block3_static_kill_gate.json",
  "claim_framing": "Phase 10 is baseline/stress-suite coverage capability evidence only, not Gate C, paired-seed dominance evidence, long-horizon statistics, or manuscript claims.",
  "profile": "smoke",
  "scenario_results": [
```

Phase 11 artifact should use:
```json
{
  "experiment": "phase11_long_horizon_paired_seed_evidence",
  "status": "PASSED | FAILED | INCONCLUSIVE | PILOT_ONLY",
  "profile": "pilot | main",
  "steps": 3600,
  "warmup": 900,
  "actual_seed_count": 20,
  "paired_seed_design": "same seeds for proposed and comparators within scenario",
  "scenario_results": [],
  "paired_statistics": [],
  "gate_c": {
    "binding_regime_dominance": [],
    "slack_regime_recovery_or_context": [],
    "inconclusive": [],
    "not_evidence": []
  }
}
```

**Row audit fields pattern** — row-level metrics, objective components, and finite-storage state remain nested audit fields, not flattened into aggregate summaries (source: `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` lines 10-44):
```json
{
  "network": "single",
  "scenario_tag": "single_sanity",
  "controller": "fixed_time",
  "seed": 20260523,
  "steps": 80,
  "warmup": 20,
  "action_interval": 10,
  "scenario_status": "completed",
  "feasibility_status": "run",
  "sumocfg": "networks/single_intersection/single_intersection.sumocfg",
  "net_file": "networks/single_intersection/single_intersection.net.xml",
  "route_decision": "pressure-equivalent",
  "route_confidence": "MEDIUM",
  "route_json": "experiments/dual_sensitivity/block3_static_kill_gate.json",
  "avg_travel_time": 51.904761904761905,
  "penalized_avg_travel_time": 56.964285714285715,
  "total_delay": 171.0,
  "completed_vehicles": 21,
  "completion_rate": 0.375,
  "throughput": 0.35,
  "mean_queue": 2.85,
  "max_queue": 5.0,
  "spillback_count": 0,
  "blocking_count": 0,
  "switching_count": 2,
  "controller_runtime_sec": 0.000396349118091166,
  "travel_time_source": "conditional_on_arrival_with_censoring_penalty",
  "unfinished_vehicle_count": 35,
  "objective_components": {
```

**Coverage metadata pattern** — copy baseline and stress coverage sections, but rename/reshape for Gate C evidence (source: `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` lines 55191-55364):
```json
"baseline_coverage": {
  "fixed_time": {
    "status": "run"
  },
  "actuated_local_pressure": {
    "status": "run"
  },
  "max_pressure": {
    "status": "run"
  },
  "capacity_aware_pressure": {
    "status": "run"
  },
  "cycle_pressure": {
    "status": "run"
  },
  "finite_storage_double_pressure": {
    "status": "run"
  },
  "finite_storage_primal_dual": {
    "status": "run"
  }
}
```
```json
"stress_scenario_coverage": {
  "categories": {
    "downstream_blockage": {
      "scenario_tags": [
        "arterial_downstream_blockage"
      ],
      "declared": true,
      "rows_present": [
        "arterial_downstream_blockage"
      ],
      "mechanisms_verified": {
        "arterial_downstream_blockage": true
      },
      "passed": true
    }
  },
  "passed": true
}
```

Phase 11 should additionally store:
- `required_gate_c_comparators` and per-scenario comparator coverage;
- `paired_seed_alignment` with seed sets per scenario/comparator;
- `statistical_family` / multiple-comparison metadata;
- `metric_direction` and `difference_definition` per statistic;
- caveat that Phase 12 must regenerate final manuscript inputs.

**Schema metadata pattern** — keep explicit schemas in artifact (source: `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` lines 55571-55610):
```json
"metric_schema": {
  "avg_travel_time": "CLOP-04 metric",
  "penalized_avg_travel_time": "CLOP-04 metric",
  "total_delay": "CLOP-04 metric",
  "completed_vehicles": "CLOP-04 metric",
  "completion_rate": "CLOP-04 metric",
  "throughput": "CLOP-04 metric",
  "mean_queue": "CLOP-04 metric",
  "max_queue": "CLOP-04 metric",
  "spillback_count": "CLOP-04 metric",
  "blocking_count": "CLOP-04 metric",
  "switching_count": "CLOP-04 metric",
  "controller_runtime_sec": "CLOP-04 metric"
},
"objective_component_schema": {
  "row_field": "objective_components",
  "fields": [
    "delay",
    "spillback_blocking_time",
    "switching_lost_time",
    "unfinished_vehicle_penalty"
  ],
  "component_builder": "build_objective_components_from_metrics",
  "aggregation_note": "Nested objective components remain row-level audit fields and are not CI-aggregated through METRIC_FIELDS."
},
"finite_storage_state_schema": {
  "row_field": "finite_storage_state",
  "fields": [
    "downstream_storage",
    "incident_capacity_drop",
    "residual_receiving_capacity",
    "service_urgency",
    "spillback_blocking",
    "switching_loss_state"
  ],
  "validation_helpers": [
    "validate_finite_storage_state",
    "validate_state_objective_sample"
  ]
}
```

## Shared Patterns

### CLI validation and route metadata
**Source:** `scripts/run_closed_loop_sumo.py` lines 75-108
**Apply to:** `scripts/run_phase11_paired_evidence.py`
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", choices=sorted(NETWORKS), default="single")
    parser.add_argument("--controllers", nargs="+", default=list(CONTROLLER_REGISTRY))
    parser.add_argument("--seeds", nargs="+", type=int, default=[20260523])
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--warmup", type=int, default=60)
    parser.add_argument("--action-interval", type=int, default=10)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block4_closed_loop_smoke.json")
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--scenario-tag", default="single_sanity")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    unknown = sorted(set(args.controllers) - set(CONTROLLER_REGISTRY))
    if unknown:
        raise ValueError(f"Unknown controllers: {unknown}. Available: {sorted(CONTROLLER_REGISTRY)}")
    if args.steps <= 0 or args.warmup < 0 or args.action_interval <= 0:
        raise ValueError("--steps and --action-interval must be positive; --warmup must be nonnegative")
    if not args.seeds:
        raise ValueError("At least one seed is required")


def load_route_metadata(route_json: Path) -> dict[str, str]:
    payload = json.loads(route_json.read_text(encoding="utf-8"))
    route_decision = payload.get("route_decision")
    if not route_decision:
        raise ValueError(f"Route JSON {route_json} is missing route_decision")
    return {
        "route_decision": str(route_decision),
        "route_confidence": str(payload.get("route_confidence", "UNKNOWN")),
        "route_json": str(route_json),
    }
```

### Independent aggregate pattern is not enough for Gate C
**Source:** `scripts/run_closed_loop_suite.py` lines 148-175
**Apply to:** use only as artifact context; do not use as primary Phase 11 evidence.
```python
def ci(values: list[float]) -> dict[str, float | int]:
    n = len(values)
    mean = statistics.fmean(values) if values else 0.0
    if n <= 1:
        se = 0.0
    else:
        se = statistics.stdev(values) / math.sqrt(n)
    delta = 1.96 * se
    return {"n_seeds": n, "mean": float(mean), "std_error": float(se), "ci95_low": float(mean - delta), "ci95_high": float(mean + delta)}


def aggregate_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("scenario_status") != "completed" or row.get("feasibility_status") not in {"run", "completed"}:
            continue
        groups[(str(row["network"]), str(row["scenario_tag"]), str(row["controller"]))].append(row)
```

Phase 11 must compute paired differences grouped by `(scenario_tag, seed, proposed_controller, comparator, metric)` before CI.

### Stress coverage fail-closed pattern
**Source:** `scripts/run_closed_loop_suite.py` lines 211-233
**Apply to:** Gate C required binding scenario checks.
```python
def stress_scenario_coverage(rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    declared_tags = {name for name, _network in SCENARIOS}
    runnable_rows = [row for row in rows or [] if row.get("scenario_status") == "completed" and row.get("feasibility_status") in {"run", "completed"}]
    categories = {}
    for category, scenario_tags in STRESS_SCENARIO_CATEGORIES.items():
        rows_by_tag = {tag: [row for row in runnable_rows if row.get("scenario_tag") == tag] for tag in scenario_tags}
        mechanism_checks = {}
        for tag, tag_rows in rows_by_tag.items():
            expected = STRESS_SCENARIO_MECHANISMS[tag]
            if expected == "edge_speed_reduction":
                mechanism_checks[tag] = any(row.get("failure_mode_mechanism") == expected for row in tag_rows)
            elif expected == "traci_vehicle_insertion":
                mechanism_checks[tag] = any(row.get("demand_shift_mechanism") == expected for row in tag_rows)
            else:
                mechanism_checks[tag] = any(row.get("stress_mechanism") == expected for row in tag_rows)
        categories[category] = {
            "scenario_tags": scenario_tags,
            "declared": all(tag in declared_tags for tag in scenario_tags),
            "rows_present": sorted(tag for tag, tag_rows in rows_by_tag.items() if tag_rows),
            "mechanisms_verified": mechanism_checks,
            "passed": all(tag in declared_tags for tag in scenario_tags) and all(rows_by_tag.values()) and all(mechanism_checks.values()),
        }
    return {"categories": categories, "passed": all(item["passed"] for item in categories.values())}
```

### Payload construction pattern
**Source:** `scripts/run_closed_loop_suite.py` lines 336-366
**Apply to:** Phase 11 artifact `build_payload(...)`.
```python
def build_payload(
    *,
    profile: str,
    route_metadata: dict[str, str],
    rows: list[dict[str, Any]],
    controllers: list[str],
    completion_gates_passed: bool,
) -> dict[str, Any]:
    gates = completion_gates(rows)
    baseline_scope = strong_baseline_coverage(rows, controllers)
    stress_scope = stress_scenario_coverage(rows)
    return {
        "experiment": "phase10_baselines_stress_suite",
        "status": "SMOKE_ONLY" if profile == "smoke" and baseline_scope["passed"] and stress_scope["passed"] else "PASSED" if completion_gates_passed else "FAILED",
        **route_metadata,
        "claim_framing": PHASE10_CLAIM_FRAMING,
        "profile": profile,
        "scenario_results": rows,
        "aggregates": aggregate_results(rows),
        "baseline_coverage": baseline_coverage(rows, controllers),
        "strong_baseline_coverage": baseline_scope,
        "stress_scenario_coverage": stress_scope,
        "grid_fixed_time_counterexample_check": grid_fixed_time_counterexample_check(rows),
        "optimized_fixed_time_metadata": optimized_fixed_time_metadata(),
        "phase10_scope_caveats": PHASE10_SCOPE_CAVEATS,
        "completion_gates": gates,
        "completion_gates_passed": completion_gates_passed,
        "metric_schema": {field: "CLOP-04 metric" for field in METRIC_FIELDS},
        "objective_component_schema": objective_component_schema(),
        "finite_storage_state_schema": finite_storage_state_schema(),
    }
```

### No authentication/security surface
**Source:** RESEARCH.md Security Domain
**Apply to:** all Phase 11 files.
- No auth/session/access-control patterns are needed.
- Validate local CLI args and JSON artifacts as the input-validation surface.
- Do not introduce credentials, network services, or secrets.

## No Analog Found

| File / Subcomponent | Role | Data Flow | Reason |
|---------------------|------|-----------|--------|
| `scripts/run_phase11_paired_evidence.py` paired bootstrap helper | utility | transform | No existing code uses `scipy.stats.bootstrap`, `ttest_rel`, or `wilcoxon`; use RESEARCH.md official SciPy snippets. |
| `scripts/run_phase11_paired_evidence.py` multiple-comparison adjustment helper | utility | transform | No existing Holm/Bonferroni or p-value adjustment helper found; implement small pure helper or record family-level CI scope. |

## Metadata

**Analog search scope:** `scripts/`, `tests/`, `experiments/dual_sensitivity/`
**Files scanned:** 8 candidate source/test files plus Phase 10 artifact shape
**Strong analogs read:**
- `scripts/run_closed_loop_suite.py`
- `scripts/run_closed_loop_sumo.py`
- `scripts/run_slack_binding_gates.py`
- `tests/test_closed_loop_sumo.py`
- `tests/test_slack_binding_gates.py`
- `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` targeted ranges

**Pattern extraction date:** 2026-05-24
