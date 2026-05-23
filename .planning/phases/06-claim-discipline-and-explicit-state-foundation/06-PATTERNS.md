# Phase 6: Claim Discipline and Explicit State Foundation - Pattern Map

**Mapped:** 2026-05-23
**Files analyzed:** 13
**Analogs found:** 13 / 13

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/claim_policy.py` | utility/config | transform | `scripts/reproduce_blocks.py` | exact |
| `scripts/audit_claim_discipline.py` | utility/CLI gate | batch + file-I/O | `scripts/reproduce_blocks.py` | exact |
| `scripts/finite_storage_schema.py` | utility/schema | validation + transform | `scripts/run_static_kill_gate.py` | exact |
| `scripts/generate_static_regime_states.py` | generator | batch + file-I/O | `scripts/generate_static_regime_states.py` | exact self-modification |
| `scripts/run_static_kill_gate.py` | gate/runner | batch + validation + file-I/O | `scripts/run_static_kill_gate.py` | exact self-modification |
| `scripts/run_closed_loop_sumo.py` | SUMO runner | event-driven + streaming simulation | `scripts/run_closed_loop_sumo.py` | exact self-modification |
| `scripts/run_closed_loop_suite.py` | suite runner | batch aggregation | `scripts/run_closed_loop_suite.py` | exact self-modification |
| `scripts/render_paper_artifacts.py` | renderer/audit gate | transform + file-I/O | `scripts/render_paper_artifacts.py` | exact self-modification |
| `scripts/reproduce_blocks.py` | reproducibility/audit gate | batch + file-I/O | `scripts/reproduce_blocks.py` | exact self-modification |
| `tests/test_claim_discipline.py` | test | request-response-style unit + file-I/O fixtures | `tests/test_run_static_kill_gate.py` | role-match |
| `tests/test_finite_storage_schema.py` | test | schema validation + file-I/O fixtures | `tests/test_generate_static_regime_states.py` | exact |
| `experiments/dual_sensitivity/phase6_claim_policy.json` | artifact/config | file-I/O | `scripts/reproduce_blocks.py` manifest payload | exact |
| `experiments/dual_sensitivity/phase6_claim_audit.json`, `phase6_explicit_state_schema.json`, `phase6_state_objective_fixtures.json` | artifacts | batch + file-I/O | `scripts/run_static_kill_gate.py`, `scripts/run_dual_sanity.py` payloads | exact |

## Pattern Assignments

### `scripts/claim_policy.py` (utility/config, transform)

**Analog:** `scripts/reproduce_blocks.py`

**Imports pattern** (`scripts/reproduce_blocks.py` lines 0-9):
```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
```

**Central policy constants pattern** (`scripts/reproduce_blocks.py` lines 11-22):
```python
FORBIDDEN_PHRASES = [
    "dual universally beats pressure",
    "max-pressure strawman",
    "proves superiority",
    "deployable superiority",
    "static evidence proves closed-loop",
]
TEXT_CLAIM_CHECKS = [
    "README.md",
    "experiments/dual_sensitivity/block3_static_kill_gate_report.md",
    "experiments/dual_sensitivity/block4_closed_loop_suite_report.md",
]
```

**Policy payload pattern** (`scripts/reproduce_blocks.py` lines 272-278):
```python
"claim_discipline": {
    "route_decision": "pressure-equivalent",
    "framing": "pressure-equivalent generalized-pressure symbolic recovery",
    "forbidden_phrases": FORBIDDEN_PHRASES,
    "forbidden_phrases_present": hits,
},
"requirements_covered": ["REPR-03", "REPR-04"],
```

**Copy guidance:** keep forbidden phrase lists and allowed claim/evidence categories in one module. Export JSON-serializable dictionaries; avoid duplicating the current phrase lists in renderers.

---

### `scripts/audit_claim_discipline.py` (utility/CLI gate, batch + file-I/O)

**Analog:** `scripts/reproduce_blocks.py`

**CLI pattern** (`scripts/reproduce_blocks.py` lines 157-164):
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List known reproduction blocks")
    parser.add_argument("--audit", action="store_true", help="Audit expected artifacts and write a manifest")
    parser.add_argument("--run", action="store_true", help="Run one selected block")
    parser.add_argument("--block", default=None, help="Block name to run, or all")
    parser.add_argument("--manifest-out", default="experiments/dual_sensitivity/reproducibility_manifest.json")
    return parser.parse_args()
```

**Scanner pattern** (`scripts/reproduce_blocks.py` lines 233-243):
```python
def forbidden_phrase_hits(root: Path) -> list[dict[str, str]]:
    hits = []
    for rel_path in TEXT_CLAIM_CHECKS:
        path = root / rel_path
        if not path.exists():
            continue
        lowered = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lowered:
                hits.append({"path": rel_path, "phrase": phrase})
    return hits
```

**Fail-closed status pattern** (`scripts/reproduce_blocks.py` lines 246-253):
```python
def audit_artifacts(registry: list[dict[str, Any]], root: Path) -> dict[str, Any]:
    expected_paths = {path for item in registry for path in item["expected_artifacts"]}
    artifact_paths = sorted(expected_paths | set(TEXT_CLAIM_CHECKS))
    checks = [audit_file(root / rel_path, rel_path, expected_paths) for rel_path in artifact_paths]
    expected_ok = all(check["exists"] and check.get("parse_status") == "ok" for check in checks if check.get("expected"))
    hits = forbidden_phrase_hits(root)
    status = "PASSED" if expected_ok and not hits else "FAILED"
```

**Write + nonzero exit pattern** (`scripts/reproduce_blocks.py` lines 295-300):
```python
if args.audit:
    manifest = audit_artifacts(registry, root)
    write_manifest(manifest, root / args.manifest_out)
    print(json.dumps({"manifest_out": args.manifest_out, "status": manifest["status"]}, indent=2))
    if manifest["status"] != "PASSED":
        raise SystemExit(1)
```

**Copy guidance:** scan `.planning`, `refine-logs`, and generated artifacts; fail closed on forbidden universal dominance unless explicit Phase 6 binding evidence exists.

---

### `scripts/finite_storage_schema.py` (utility/schema, validation + transform)

**Analog:** `scripts/run_static_kill_gate.py`

**Required-field constants pattern** (`scripts/run_static_kill_gate.py` lines 31-35):
```python
REQUIRED_SAMPLE_FIELDS = {"time", "queues", "vehicle_counts", "capacities", "tls_movements"}
PRIMARY_DUAL_LIBRARY = "dual_sensitivity"
PRIMARY_PRESSURE_LIBRARY = "pressure_backpressure"
DEFAULT_LIBRARIES = [PRIMARY_DUAL_LIBRARY, PRIMARY_PRESSURE_LIBRARY]
ROUTE_DECISIONS = {"dual-improves-pressure", "pressure-equivalent", "diagnostic"}
```

**Numeric validation pattern** (`scripts/run_static_kill_gate.py` lines 104-107):
```python
def validate_numeric_mapping(sample: dict[str, Any], path: Path, sample_idx: int, field: str) -> None:
    for key, value in sample[field].items():
        if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise ValueError(f"Sample {sample_idx} in {path} field {field}.{key} must be a finite number")
```

**Required-field fail-closed pattern** (`scripts/run_static_kill_gate.py` lines 110-120):
```python
def validate_sample_schema(sample: dict[str, Any], path: Path, sample_idx: int) -> None:
    missing = REQUIRED_SAMPLE_FIELDS - set(sample)
    if missing:
        raise ValueError(f"Sample {sample_idx} in {path} is missing fields: {sorted(missing)}")
    if not isinstance(sample["time"], (int, float)) or not math.isfinite(float(sample["time"])):
        raise ValueError(f"Sample {sample_idx} in {path} field time must be a finite number")
    for field in ["queues", "vehicle_counts", "capacities", "tls_movements"]:
        if not isinstance(sample[field], dict):
            raise ValueError(f"Sample {sample_idx} in {path} field {field} must be an object")
```

**Copy guidance:** add `FINITE_STORAGE_STATE_FIELDS` and `OBJECTIVE_COMPONENT_FIELDS`, then mirror this explicit missing-field and finite-number style. Do not introduce an external JSON schema dependency.

---

### `scripts/generate_static_regime_states.py` (generator, batch + file-I/O)

**Analog:** `scripts/generate_static_regime_states.py`

**Script caveat/docstring pattern** (lines 0-8):
```python
#!/usr/bin/env python3
"""Generate labeled static-regime states for the Phase 3 kill gate.

The output deliberately preserves the existing sampled-state schema consumed by
`scenario_from_sample()`: each supported/proxy sample includes time, queues,
vehicle_counts, capacities, and tls_movements. Regimes that the current sample
schema cannot encode as explicit primal constraints are marked as proxy or
unsupported instead of being upgraded into stronger corridor/supply claims.
"""
```

**Sample builder pattern** (lines 75-105):
```python
def make_sample(
    time: float,
    queues: dict[str, float],
    capacities: dict[str, float],
    tls_movements: dict[str, list[tuple[str, str]]],
    regime: str,
    regime_detail: str,
    generated_by: dict[str, Any],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_capacities = {edge: float(capacity) for edge, capacity in capacities.items()}
    normalized_queues = {
        edge: clamp_queue(queues.get(edge, 0.0), normalized_capacities.get(edge, 1.0))
        for edge in normalized_capacities
    }
    sample = {
        "time": float(time),
        "queues": normalized_queues,
        "vehicle_counts": {edge: max(value, 0.0) for edge, value in normalized_queues.items()},
        "capacities": normalized_capacities,
        "tls_movements": tls_movements,
        "regime": regime,
        "regime_detail": regime_detail,
        "generated_by": generated_by,
    }
    if extra:
        sample.update(extra)
    missing = SAMPLE_REQUIRED_FIELDS - set(sample)
    if missing:
        raise ValueError(f"Internal sample schema error; missing fields: {sorted(missing)}")
    return sample
```

**Payload artifact pattern** (lines 393-415):
```python
return {
    "network": "arterial_static_regime_block3",
    "net_file": str(args.net_file),
    "tls": args.tls,
    "num_samples": len(samples),
    "target_per_regime": args.target_per_regime,
    "counts_by_regime": counts_by_regime,
    "regime_status": regime_status,
    "generation_config": {
        "script": SCRIPT_NAME,
        "seed": args.seed,
        "regimes": args.regimes,
        "target_per_regime": args.target_per_regime,
        "capacity_drop_factors": args.capacity_drop_factors,
        "demand_shift_factors": args.demand_shift_factors,
    },
    "samples": samples,
    "sample_sufficiency_note": (
        "Raw generated sample counts are preliminary. Final KILL-03 sufficiency is "
        "determined by run_static_kill_gate.py after scenario_from_sample() and "
        "build_example() conversion into valid examples."
    ),
}
```

**Copy guidance:** extend `make_sample()` to include nested `finite_storage_state` from `finite_storage_schema.py`; keep proxy caveats for legacy regimes and add explicit Phase 6 fixtures under `experiments/dual_sensitivity/` instead of mutating v1.0 artifacts.

---

### `scripts/run_static_kill_gate.py` (gate/runner, batch + validation + file-I/O)

**Analog:** `scripts/run_static_kill_gate.py`

**Load + validate samples pattern** (lines 152-166):
```python
for path in paths:
    data = json.loads(path.read_text(encoding="utf-8"))
    samples = data.get("samples")
    if not isinstance(samples, list):
        raise ValueError(f"State file {path} must contain a samples list")
    file_regime_status = data.get("regime_status")
    if isinstance(file_regime_status, dict):
        for regime, status in file_regime_status.items():
            input_regime_status.append(f"{regime}: {status.get('status', 'unknown')} - {status.get('rationale', '')}")
    selected = samples if remaining <= 0 else samples[:remaining]
    for sample_idx, sample in enumerate(selected):
        if not isinstance(sample, dict):
            raise ValueError(f"Sample {sample_idx} in {path} must be an object")
        validate_sample_schema(sample, path, sample_idx)
```

**Claim-scope route discipline pattern** (lines 392-400):
```python
caveats = [
    "Route is based on static/sample-relative one-step recovery metrics only; closed-loop claims are deferred.",
]
if not metrics:
    return {
        "route_decision": "diagnostic",
        "route_confidence": "LOW",
        "route_rationale": "No solved regime metrics were available.",
        "route_caveats": caveats + ["No regime evidence was available for routing."],
    }
```

**Payload + artifacts pattern** (lines 635-672):
```python
payload = {
    "experiment": "block3_static_pressure_failure_kill_gate",
    "status": "PASSED" if regime_metrics and route["route_decision"] in ROUTE_DECISIONS else "FAILED",
    "scope": "static_sample_relative_only_no_closed_loop_claims",
    "input_states": [str(path) for path in state_paths],
    "input_regime_status": input_regime_status,
    "input_labeling_notes": labeling_notes,
    "tls": args.tls,
    "target_total_states": args.target_total_states,
    "min_regime_count": args.min_regime_count,
    "raw_samples_by_regime": raw_counts,
    "valid_examples_by_regime": valid_examples_by_regime,
    "num_examples_total": num_examples_total,
    "sample_target_met": sample_target_met,
    "preliminary_regimes": preliminary_regimes,
    "thresholds": {
        "dual_win_threshold": args.dual_win_threshold,
        "regret_improvement_threshold": args.regret_improvement_threshold,
        "equivalence_tolerance": args.equivalence_tolerance,
    },
    "objective_mode": args.objective,
    "budgets": args.budgets,
    "libraries": library_names,
    "atom_registry": ATOM_REGISTRY,
    "regime_metrics": regime_metrics,
    "runs_by_regime": runs_by_regime_payload,
    "csv_out": str(csv_path),
    "rules_out": str(rules_path),
    "report_out": str(report_path),
    "out": str(out_path),
    "note": note,
    **route,
}
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(render_report(payload, out_path, report_path), encoding="utf-8")
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
```

**Copy guidance:** require Phase 6 explicit fields before any binding-regime improvement route. Include objective component validation in sample ingestion and route payload.

---

### `scripts/run_closed_loop_sumo.py` (SUMO runner, event-driven + streaming simulation)

**Analog:** `scripts/run_closed_loop_sumo.py`

**Metric schema constants pattern** (lines 15-28):
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

**Claim framing pattern** (lines 58-63):
```python
CLAIM_FRAMING = (
    "Phase 3 selected pressure-equivalent; Phase 4 outputs are closed-loop SUMO evidence "
    "for generalized-pressure symbolic recovery, not universal dominance over pressure."
)
FORBIDDEN_CLAIM_PHRASES = ["dual universally beats pressure", "max-pressure strawman", "static evidence proves closed-loop"]
```

**Objective-source metrics pattern** (lines 223-257):
```python
def aggregate_metrics(
    observations: list[dict[str, float]],
    steps: int,
    warmup: int,
    departed: dict[str, float],
    arrived_times: list[float],
    waiting_delay: float,
    runtime: float,
    switching_count: int,
) -> dict[str, Any]:
    queues = [obs["total_queue"] for obs in observations]
    max_queues = [obs["max_queue"] for obs in observations]
    completed = len(arrived_times)
    unfinished = len(departed)
    departed_total = completed + unfinished
    horizon = max(steps - warmup, 1)
    total_travel_time = sum(arrived_times)
    censor_penalty = float(horizon)
    penalized_total = total_travel_time + unfinished * censor_penalty
    return {
        "avg_travel_time": float(total_travel_time / completed) if completed else 0.0,
        "penalized_avg_travel_time": float(penalized_total / departed_total) if departed_total else 0.0,
        "total_delay": float(waiting_delay),
        "completed_vehicles": int(completed),
        "completion_rate": float(completed / departed_total) if departed_total else 0.0,
        "throughput": float(completed / horizon),
        "mean_queue": float(statistics.fmean(queues) if queues else 0.0),
        "max_queue": float(max(max_queues, default=0.0)),
        "spillback_count": int(sum(obs["spillback"] for obs in observations)),
        "blocking_count": int(sum(obs["blocking"] for obs in observations)),
        "switching_count": int(switching_count),
        "controller_runtime_sec": float(runtime),
        "travel_time_source": "conditional_on_arrival_with_censoring_penalty",
        "unfinished_vehicle_count": int(unfinished),
    }
```

**Observed finite-storage proxy pattern** (lines 294-311):
```python
def edge_observation(edge_ids: list[str], capacities: dict[str, float]) -> dict[str, float]:
    queues = {edge_id: float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids}
    vehicles = {edge_id: float(traci.edge.getLastStepVehicleNumber(edge_id)) for edge_id in edge_ids}
    spillback = 0
    blocking = 0
    for edge_id, count in vehicles.items():
        cap = max(float(capacities.get(edge_id, 1.0)), 1.0)
        if count / cap >= 0.85:
            spillback += 1
            if queues.get(edge_id, 0.0) > 0.0:
                blocking += 1
    return {
        "total_queue": float(sum(queues.values())),
        "max_queue": float(max(queues.values(), default=0.0)),
        "active_vehicles": float(sum(vehicles.values())),
        "spillback": float(spillback),
        "blocking": float(blocking),
    }
```

**TraCI lifecycle pattern** (lines 368-442):
```python
cmd = ["sumo", "-c", str(paths["sumocfg"]), "--seed", str(seed), "--no-step-log", "true", "--duration-log.disable", "true"]
traci.start(cmd)
observations: list[dict[str, float]] = []
...
try:
    route_ids = list(traci.route.getIDList())
    original_speed = float(edge_speeds.get(target_edge, 13.89)) if target_edge else None
    for step in range(steps):
        ...
        traci.simulationStep()
        ...
        if step >= warmup:
            waiting_delay += sum(float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids)
            observations.append(edge_observation(edge_ids, capacities))
finally:
    traci.close(False)
```

**Copy guidance:** add `objective_components` to returned metrics and row payloads using the existing delay/unfinished/spillback/blocking/switching variables. Add `finite_storage_state_summary` or equivalent observed explicit state fields without weakening the TraCI close-in-finally pattern.

---

### `scripts/run_closed_loop_suite.py` (suite runner, batch aggregation)

**Analog:** `scripts/run_closed_loop_suite.py`

**Spec generation pattern** (lines 56-104):
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
            "single_sanity": arterial_seeds[:1],
            "arterial_main": arterial_seeds[:1],
            "grid_scalability": grid_seeds[:1],
            "arterial_demand_shift": arterial_seeds[:1],
            "arterial_bottleneck_failure_mode": arterial_seeds[:1],
        }
        controllers_by_scenario = {name: controllers for name, _ in SCENARIOS}
    else:
        seeds_by_scenario = {
            "single_sanity": arterial_seeds[:1],
            "arterial_main": arterial_seeds[:5],
            "grid_scalability": grid_seeds[:5],
            "arterial_demand_shift": arterial_seeds[:1],
            "arterial_bottleneck_failure_mode": arterial_seeds[:1],
        }
```

**Aggregation pattern** (lines 118-134):
```python
def aggregate_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get("scenario_status") != "completed" or row.get("feasibility_status") not in {"run", "completed"}:
            continue
        groups[(str(row["network"]), str(row["scenario_tag"]), str(row["controller"]))].append(row)
    aggregates = []
    for (network, scenario_tag, controller), group in sorted(groups.items()):
        item: dict[str, Any] = {"network": network, "scenario_tag": scenario_tag, "controller": controller}
        seeds = sorted({int(row["seed"]) for row in group})
        item["seeds"] = seeds
        item["n_seeds"] = len(seeds)
        for metric in METRIC_FIELDS:
            vals = [float(row.get(metric, 0.0)) for row in group]
            item[metric] = ci(vals)
        aggregates.append(item)
    return aggregates
```

**Suite payload pattern** (lines 219-235):
```python
payload = {
    "experiment": "block4_closed_loop_suite",
    "status": "PASSED" if completion_gates_passed else "SMOKE_ONLY" if args.profile == "smoke" else "FAILED",
    **route_metadata,
    "claim_framing": CLAIM_FRAMING,
    "profile": args.profile,
    "scenario_results": rows,
    "aggregates": aggregate_results(rows),
    "baseline_coverage": baseline_coverage(rows, args.controllers),
    "completion_gates": gates,
    "completion_gates_passed": completion_gates_passed,
    "metric_schema": {field: "CLOP-04 metric" for field in METRIC_FIELDS},
}
out_path = Path(args.out)
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
```

**Copy guidance:** update `METRIC_FIELDS` consumers when adding objective components, or keep objective components as nested objects and add a separate schema key to avoid breaking scalar CI aggregation.

---

### `scripts/render_paper_artifacts.py` (renderer/audit gate, transform + file-I/O)

**Analog:** `scripts/render_paper_artifacts.py`

**Source validation pattern** (lines 68-85):
```python
def validate_inputs(inputs: dict[str, Any]) -> None:
    for name in ["block0", "sparse", "static", "closed_loop", "repro_manifest"]:
        if inputs[name].get("status") != "PASSED":
            raise ValueError(f"{name} source artifact is not PASSED")
    static_route = inputs["static"].get("route_decision")
    closed_route = inputs["closed_loop"].get("route_decision")
    if static_route != "pressure-equivalent":
        raise ValueError(f"Unexpected static route_decision: {static_route}")
    if closed_route != static_route:
        raise ValueError("Static and closed-loop route decisions differ")
    if not inputs["closed_loop"].get("completion_gates_passed"):
        raise ValueError("Closed-loop completion gates did not pass")
    schema = inputs["closed_loop"].get("metric_schema")
    if not isinstance(schema, dict):
        raise ValueError("closed_loop.metric_schema must be an object")
    missing_metrics = REQUIRED_CLOSED_LOOP_METRICS - set(schema)
    if missing_metrics:
        raise ValueError(f"closed_loop.metric_schema is missing metrics: {sorted(missing_metrics)}")
```

**Generated rows traceability pattern** (lines 119-131):
```python
def table_row(table_id: str, panel: str, metric: str, value: Any, source_artifact: str, source_key: str, route_decision: str, **extra: Any) -> dict[str, Any]:
    row = {
        "table_id": table_id,
        "panel": panel,
        "metric": metric,
        "value": scalar(value),
        "source_artifact": source_artifact,
        "source_key": source_key,
        "route_decision": route_decision,
        "claim_note": claim_note(route_decision),
    }
    row.update({key: scalar(value) for key, value in extra.items()})
    return row
```

**Overclaim guard pattern** (lines 271-278):
```python
def forbidden_hits(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> list[str]:
    checked_manifest = {
        "status": manifest.get("status"),
        "route_decision": manifest.get("route_decision"),
        "claim_framing": manifest.get("claim_discipline", {}).get("framing"),
    }
    text = json.dumps({"rows": rows, "manifest": checked_manifest}, sort_keys=True).lower()
    return [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
```

**Copy guidance:** integrate central claim policy here by importing from `claim_policy.py`; validate Phase 6 evidence fields before rendering any future paper-facing artifact.

---

### `scripts/reproduce_blocks.py` (reproducibility/audit gate, batch + file-I/O)

**Analog:** `scripts/reproduce_blocks.py`

**Registry pattern** (lines 29-39):
```python
def build_block_registry() -> list[dict[str, Any]]:
    return [
        {
            "block": "block0",
            "description": "Block 0 dual finite-difference sanity checks",
            "commands": [["python3", "scripts/run_dual_sanity.py", "--out", "experiments/dual_sensitivity/block0_dual_sanity.json"]],
            "expected_artifacts": ["experiments/dual_sensitivity/block0_dual_sanity.json"],
            "runtime_profile": "short",
            "requirements": ["REPR-03", "REPR-04"],
            "claim_note": "Dual sanity only; not closed-loop evidence.",
        },
```

**Artifact parse audit pattern** (lines 208-230):
```python
def audit_file(path: Path, rel_path: str, expected_paths: set[str]) -> dict[str, Any]:
    check: dict[str, Any] = {"path": rel_path, "exists": path.exists(), "expected": rel_path in expected_paths}
    if not path.exists():
        check["parse_status"] = "missing"
        return check
    try:
        if path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            check.update({"parse_status": "ok", **json_count(payload)})
            if isinstance(payload, dict):
                for key in ["experiment", "status", "route_decision"]:
                    if key in payload:
                        check[key] = payload[key]
        elif path.suffix == ".csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            check.update({"parse_status": "ok", "row_count": len(rows)})
        else:
            text = path.read_text(encoding="utf-8")
            check.update({"parse_status": "ok", "byte_length": len(text.encode("utf-8"))})
    except Exception as exc:  # noqa: BLE001
        check.update({"parse_status": "error", "error": str(exc)})
    return check
```

**Copy guidance:** add Phase 6 claim policy/audit/schema/fixture artifacts to registry once generated. Keep `claim_note` bounded: v1.0 evidence is pressure-equivalent only.

---

### `tests/test_claim_discipline.py` (test, unit + file-I/O fixtures)

**Analog:** `tests/test_run_static_kill_gate.py`

**Import path pattern** (`tests/test_run_static_kill_gate.py` lines 0-10):
```python
#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_static_kill_gate import compare_dual_pressure, decide_route, find_preliminary_regimes
```

**Fail-closed route assertion pattern** (`tests/test_run_static_kill_gate.py` lines 63-87):
```python
def test_sample_shortfall_routes_to_diagnostic() -> None:
    metrics = [
        {
            "regime": "storage_binding_proxy",
            "num_examples": 16,
            "sample_target_met": False,
            "claim_scope": "preliminary_static_sample_relative",
            "dual_win_rate": 0.75,
            "pressure_win_rate": 0.0,
            "tie_rate": 0.25,
            "mean_oracle_regret_delta_pressure_minus_dual": 0.5,
        }
    ]

    route = decide_route(
        metrics,
        sample_target_met=False,
        dual_win_threshold=0.55,
        regret_improvement_threshold=0.05,
        equivalence_tolerance=1e-9,
    )

    assert route["route_decision"] == "diagnostic"
    assert route["route_confidence"] == "LOW"
    assert any("sample target" in caveat for caveat in route["route_caveats"])
```

**Direct-executable test pattern** (`tests/test_run_static_kill_gate.py` lines 124-132):
```python
def main() -> None:
    test_tie_aware_disagreement_is_not_a_win()
    test_sample_shortfall_routes_to_diagnostic()
    test_missing_requested_regime_routes_to_diagnostic()
    print("static kill-gate tests ok")


if __name__ == "__main__":
    main()
```

**Copy guidance:** test forbidden universal dominance, missing evidence, and allowed bounded slack/binding language with real temp files rather than mocks.

---

### `tests/test_finite_storage_schema.py` (test, schema validation + file-I/O fixtures)

**Analog:** `tests/test_generate_static_regime_states.py`

**Subprocess CLI test pattern** (`tests/test_generate_static_regime_states.py` lines 35-42):
```python
def run_generator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
```

**Generated artifact schema assertion pattern** (`tests/test_generate_static_regime_states.py` lines 45-58):
```python
def test_generator_emits_schema_compatible_regime_samples(tmp_path: Path) -> None:
    out = tmp_path / "block3_regime_states.json"
    result = run_generator("--target-per-regime", "10", "--out", str(out))

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    regimes = {sample["regime"] for sample in payload["samples"]}

    assert EXPECTED_REGIMES <= regimes
    assert payload["num_samples"] == len(payload["samples"])
    assert payload["target_per_regime"] == 10
    assert "regime_status" in payload
    assert all(EXPECTED_SAMPLE_FIELDS <= set(sample) for sample in payload["samples"])
```

**Invalid input assertion pattern** (`tests/test_generate_static_regime_states.py` lines 60-67):
```python
def test_generator_rejects_invalid_cli_inputs(tmp_path: Path) -> None:
    bad_target = run_generator("--target-per-regime", "0", "--out", str(tmp_path / "bad.json"))
    bad_regime = run_generator("--regimes", "not_a_regime", "--out", str(tmp_path / "bad.json"))

    assert bad_target.returncode != 0
    assert "--target-per-regime must be positive" in bad_target.stderr
    assert bad_regime.returncode != 0
    assert "Unknown regimes" in bad_regime.stderr
```

**Copy guidance:** assert required `finite_storage_state` fields and `objective_components` keys on deterministic generated JSON. Include negative tests for missing fields and non-finite values.

---

### `experiments/dual_sensitivity/phase6_*.json` (artifacts, file-I/O)

**Analogs:** `scripts/run_dual_sanity.py`, `scripts/run_static_kill_gate.py`, `scripts/reproduce_blocks.py`

**Simple status payload pattern** (`scripts/run_dual_sanity.py` lines 348-364):
```python
payload = {
    "experiment": "block0_dual_sanity",
    "status": "PASSED" if gate_a_pass else "FAILED",
    "epsilon": args.epsilon,
    "criteria": {
        "dual_rank_matches_finite_difference_rank": True,
        "pressure_rank_matches_dual_rank_when_storage_nonbinding": True,
    },
    "results": results,
}

out_path = Path(args.out)
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps({"status": payload["status"], "out": str(out_path)}, indent=2))
if not gate_a_pass:
    raise SystemExit(1)
```

**Manifest metadata pattern** (`scripts/reproduce_blocks.py` lines 253-279):
```python
return {
    "experiment": "reproducibility_manifest",
    "status": status,
    "generated_by": "scripts/reproduce_blocks.py --audit",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "blocks": [
        {
            "block": item["block"],
            "description": item["description"],
            "commands": commands_text(item["commands"]),
            "command": " && ".join(commands_text(item["commands"])),
            "expected_artifacts": item["expected_artifacts"],
            "runtime_profile": item["runtime_profile"],
            "requirements": item["requirements"],
            "claim_note": item["claim_note"],
        }
        for item in registry
    ],
    "artifact_checks": checks,
```

**Copy guidance:** Phase 6 artifacts should include `experiment`, `status`, `generated_by`, `requirements_covered`, and stable schema/policy keys. Use `indent=2` and compact printed status.

## Shared Patterns

### Standalone Python CLI structure
**Source:** `scripts/run_static_kill_gate.py`, `scripts/reproduce_blocks.py`, `scripts/generate_static_regime_states.py`
**Apply to:** all new Phase 6 scripts
```python
def main() -> None:
    args = parse_args()
    ...


if __name__ == "__main__":
    main()
```

### Fail-closed JSON gates
**Source:** `scripts/run_dual_sanity.py` lines 359-364 and `scripts/reproduce_blocks.py` lines 295-300
**Apply to:** claim audit, schema validation, fixture generation
```python
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps({"status": payload["status"], "out": str(out_path)}, indent=2))
if not gate_a_pass:
    raise SystemExit(1)
```

### Required-field validation
**Source:** `scripts/run_static_kill_gate.py` lines 110-120
**Apply to:** `finite_storage_state`, `objective_components`, generated state fixtures, closed-loop rows
```python
missing = REQUIRED_SAMPLE_FIELDS - set(sample)
if missing:
    raise ValueError(f"Sample {sample_idx} in {path} is missing fields: {sorted(missing)}")
```

### Claim discipline and forbidden wording
**Source:** `scripts/render_paper_artifacts.py` lines 68-85 and 271-278; `scripts/reproduce_blocks.py` lines 233-243
**Apply to:** audit scanner, renderers, reproducibility manifest, paper artifacts
```python
text = json.dumps({"rows": rows, "manifest": checked_manifest}, sort_keys=True).lower()
return [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
```

### Artifact traceability
**Source:** `scripts/render_paper_artifacts.py` lines 119-131
**Apply to:** any Phase 6 generated CSV/JSON audit row
```python
row = {
    "table_id": table_id,
    "panel": panel,
    "metric": metric,
    "value": scalar(value),
    "source_artifact": source_artifact,
    "source_key": source_key,
    "route_decision": route_decision,
    "claim_note": claim_note(route_decision),
}
```

### SUMO runner lifecycle
**Source:** `scripts/run_closed_loop_sumo.py` lines 368-442; `scripts/sample_sumo_states.py` lines 76-96
**Apply to:** closed-loop explicit state/objective integration
```python
traci.start(cmd)
try:
    for step in range(steps):
        traci.simulationStep()
        ...
finally:
    traci.close(False)
```

### Test import path and direct execution
**Source:** `tests/test_run_static_kill_gate.py` lines 6-10 and 124-132
**Apply to:** new tests under `tests/`
```python
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
```

## No Analog Found

No Phase 6 file lacks a close repository analog. The only new semantic content is the exact finite-storage schema and claim-policy vocabulary; implementation shape is covered by existing script/gate/test patterns.

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| none | n/a | n/a | All requested files map to existing CLI, gate, schema, runner, test, or artifact patterns. |

## Metadata

**Analog search scope:** `/home/samuel/projects/pi_light_OR/scripts`, `/home/samuel/projects/pi_light_OR/tests`, `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity`, `/home/samuel/projects/pi_light_OR/CLAUDE.md`
**Files scanned:** 22 script/test/artifact surfaces plus Phase 6 CONTEXT/RESEARCH and project instructions
**Pattern extraction date:** 2026-05-23
