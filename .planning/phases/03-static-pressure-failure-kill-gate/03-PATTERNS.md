# Phase 3: Static Pressure-Failure Kill Gate - Pattern Map

**Mapped:** 2026-05-23
**Files analyzed:** 8
**Analogs found:** 8 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/generate_static_regime_states.py` | utility / generator | transform + file-I/O | `scripts/generate_targeted_bottleneck_states.py` | exact |
| `scripts/run_static_kill_gate.py` | utility / experiment runner | batch + transform + file-I/O | `scripts/run_sparse_recovery.py` | exact |
| `scripts/render_static_kill_gate_report.py` | utility / report renderer | transform + file-I/O | `scripts/run_sparse_recovery.py` (`render_rules_file`, JSON/CSV writer patterns) | role-match |
| `experiments/dual_sensitivity/block3_regime_states.json` | config / data artifact | file-I/O | `experiments/dual_sensitivity/targeted_bottleneck_states.json` via generator schema | exact |
| `experiments/dual_sensitivity/block3_static_kill_gate.json` | data artifact | batch result | `experiments/dual_sensitivity/block2_sparse_recovery.json` via `scripts/run_sparse_recovery.py` payload | exact |
| `experiments/dual_sensitivity/block3_static_kill_gate.csv` | data artifact | batch result | `scripts/run_sparse_recovery.py::write_csv` | exact |
| `experiments/dual_sensitivity/block3_static_kill_gate_rules.txt` | data artifact | report text | `scripts/run_sparse_recovery.py::render_rules_file` | exact |
| `experiments/dual_sensitivity/block3_static_kill_gate_report.md` | data artifact / report | transform + file-I/O | `scripts/run_sparse_recovery.py` output and stdout conventions | role-match |

## Pattern Assignments

### `scripts/generate_static_regime_states.py` (utility/generator, transform + file-I/O)

**Analog:** `scripts/generate_targeted_bottleneck_states.py`

**Imports pattern** (`scripts/generate_targeted_bottleneck_states.py` lines 7-15):
```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sumolib

from sample_sumo_states import build_network_metadata
```

**State sample schema pattern** (`scripts/generate_targeted_bottleneck_states.py` lines 18-26):
```python
def make_sample(time: float, queues: dict[str, float], capacities: dict[str, float], tls_movements: dict) -> dict:
    vehicle_counts = {edge: max(q, 0.0) for edge, q in queues.items()}
    return {
        "time": time,
        "queues": queues,
        "vehicle_counts": vehicle_counts,
        "capacities": capacities,
        "tls_movements": tls_movements,
    }
```

**Base queue generation pattern** (`scripts/generate_targeted_bottleneck_states.py` lines 29-30):
```python
def base_queues(capacities: dict[str, float]) -> dict[str, float]:
    return {edge: 0.05 * cap for edge, cap in capacities.items()}
```

**Synthetic bottleneck/state perturbation pattern** (`scripts/generate_targeted_bottleneck_states.py` lines 33-50):
```python
def generate(net_file: Path, tls: str) -> dict:
    metadata = build_network_metadata(net_file)
    capacities = metadata["edge_capacity"]
    tls_movements = metadata["tls_movements"]
    moves = tls_movements[tls]

    samples = []
    t = 0.0
    for idx, (up, down) in enumerate(moves[:12]):
        q = base_queues(capacities)
        q[up] = 0.65 * capacities[up]
        q[down] = 0.98 * capacities[down]
        for other_up, other_down in moves[:12]:
            if other_up != up:
                q[other_up] = max(q.get(other_up, 0.0), 0.35 * capacities[other_up])
            if other_down != down:
                q[other_down] = min(q.get(other_down, 0.0), 0.20 * capacities[other_down])
        samples.append(make_sample(t, q, capacities, tls_movements))
```

**Conflict-case generation pattern** (`scripts/generate_targeted_bottleneck_states.py` lines 53-78):
```python
# Conflict cases by incoming approach: all turns from the high-pressure approach
# feed storage-constrained downstream links, while a lower-pressure approach has one open turn.
by_up: dict[str, list[tuple[str, str]]] = {}
for up, down in moves[:12]:
    by_up.setdefault(up, []).append((up, down))
approaches = sorted(by_up)
for idx, blocked_up in enumerate(approaches):
    open_up = approaches[(idx + 1) % len(approaches)]
    q = base_queues(capacities)
    for other_up, other_down in moves[:12]:
        q[other_up] = 0.05 * capacities[other_up]
        q[other_down] = 0.05 * capacities[other_down]

    q[blocked_up] = 1.00 * capacities[blocked_up]
    blocked_downs = {blocked_down for _, blocked_down in by_up[blocked_up]}
    for blocked_down in blocked_downs:
        q[blocked_down] = 0.82 * capacities[blocked_down]

    open_down = next(
        (down for _, down in by_up[open_up] if down not in blocked_downs),
        by_up[open_up][0][1],
    )
    q[open_down] = 0.05 * capacities[open_down]
    q[open_up] = min(capacities[open_up], q[open_down] + 14.0)
    samples.append(make_sample(t, q, capacities, tls_movements))
```

**Payload + CLI + stdout pattern** (`scripts/generate_targeted_bottleneck_states.py` lines 80-101):
```python
return {
    "network": "arterial_targeted_bottleneck",
    "net_file": str(net_file),
    "tls": tls,
    "num_samples": len(samples),
    "samples": samples,
    "note": "Synthetic targeted states using arterial topology; designed to stress downstream scarcity vs pressure.",
}
...
parser = argparse.ArgumentParser()
parser.add_argument("--net-file", default="networks/arterial/arterial.net.xml")
parser.add_argument("--tls", default="C3")
parser.add_argument("--out", default="experiments/dual_sensitivity/targeted_bottleneck_states.json")
args = parser.parse_args()

payload = generate(Path(args.net_file), args.tls)
out_path = Path(args.out)
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps({"out": str(out_path), "num_samples": payload["num_samples"]}, indent=2))
```

**Phase 3 adaptation:**
- Reuse `build_network_metadata()` and the existing sample shape exactly.
- Add `regime`, `regime_detail`, `generated_by`, and optional perturbation metadata inside each `sample` while preserving `time`, `queues`, `vehicle_counts`, `capacities`, and `tls_movements`.
- Keep unsupported/proxy regime labels explicit: e.g. `corridor_bottleneck_proxy`, `demand_shift_proxy`, `unsupported_by_current_model`.

---

### `scripts/run_static_kill_gate.py` (utility/runner, batch + transform + file-I/O)

**Primary analog:** `scripts/run_sparse_recovery.py`

**Reusable imports and local-script import pattern** (`scripts/run_sparse_recovery.py` lines 1-17):
```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from run_dual_sanity import summarize_scenario
from run_sumo_sampled_recovery import scenario_from_sample
```

**Atom/library registry to reuse, not duplicate** (`scripts/run_sparse_recovery.py` lines 19-95):
```python
ATOM_REGISTRY: dict[str, dict[str, Any]] = {
    "upstream_queue": {
        "name": "upstream_queue",
        "family": "local",
        "requires_neighbor": False,
        "uses_dual": False,
        "is_placebo": False,
        "expression": "q_up(m)",
        "description": "Local upstream movement queue length.",
    },
    ...
    "pressure_backpressure": {
        "name": "pressure_backpressure",
        "family": "pressure",
        "requires_neighbor": True,
        "uses_dual": False,
        "is_placebo": False,
        "expression": "w_up(m) - w_down(m)",
        "description": "Ordinary pressure/backpressure score from the LP summary weights.",
    },
    "dual_sensitivity": {
        "name": "dual_sensitivity",
        "family": "dual",
        "requires_neighbor": True,
        "uses_dual": True,
        "is_placebo": False,
        "expression": "lambda_up(m) - lambda_down(m)",
        "description": "Genuine movement-level dual-sensitivity value from summarize_scenario().",
    },
    ...
}

LIBRARIES: dict[str, list[str]] = {
    "local_only": ["upstream_queue"],
    "raw_neighbor": ["upstream_queue", "neg_downstream_queue"],
    "all_neighbor": ["upstream_queue", "neg_downstream_queue", "downstream_slack", "neg_downstream_fullness"],
    "random_price": ["random_price"],
    "dual_sensitivity": ["dual_sensitivity"],
    "dual_plus_raw": ["dual_sensitivity", "upstream_queue", "neg_downstream_queue"],
    "pressure_backpressure": ["pressure_backpressure"],
    "full_symbolic": list(ATOM_REGISTRY),
}
```

**Validation helper pattern** (`scripts/run_sparse_recovery.py` lines 112-142):
```python
def validate_atom_registry() -> None:
    for atom, metadata in ATOM_REGISTRY.items():
        missing = REQUIRED_METADATA_FIELDS - set(metadata)
        if missing:
            raise ValueError(f"Atom {atom} is missing metadata fields: {sorted(missing)}")
        if metadata["name"] != atom:
            raise ValueError(f"Atom metadata name mismatch for {atom}: {metadata['name']}")
    unknown_by_library = {
        library: [atom for atom in atoms if atom not in ATOM_REGISTRY]
        for library, atoms in LIBRARIES.items()
    }
    unknown_by_library = {name: atoms for name, atoms in unknown_by_library.items() if atoms}
    if unknown_by_library:
        raise ValueError(f"Libraries reference unknown atoms: {unknown_by_library}")
    families = {str(metadata["family"]) for metadata in ATOM_REGISTRY.values()}
    missing_families = REQUIRED_ATOM_FAMILIES - families
    if missing_families:
        raise ValueError(f"Atom registry missing required families: {sorted(missing_families)}")


def select_library_names(requested_libraries: list[str] | None) -> list[str]:
    if not requested_libraries:
        return list(LIBRARIES)
    unknown = [name for name in requested_libraries if name not in LIBRARIES]
    if unknown:
        raise ValueError(f"Unknown libraries: {unknown}. Available libraries: {sorted(LIBRARIES)}")
    return requested_libraries
```

**Example loading pattern to reuse** (`scripts/run_sparse_recovery.py` lines 162-179):
```python
def load_examples(paths: list[Path], tls: str, max_samples: int, max_movements: int, epsilon: float) -> list[dict[str, Any]]:
    examples = []
    remaining = max_samples
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        samples = data["samples"] if remaining <= 0 else data["samples"][:remaining]
        for sample in samples:
            scenario = scenario_from_sample(sample, tls, max_movements)
            if scenario is None:
                continue
            summary = summarize_scenario(scenario, epsilon)
            example = build_example(summary)
            if example is not None:
                example["source"] = str(path)
                examples.append(example)
        if remaining > 0:
            remaining -= len(samples)
    return examples
```

**Feature/example construction pattern** (`scripts/run_sparse_recovery.py` lines 182-231):
```python
def build_example(summary: dict[str, Any]) -> dict[str, Any] | None:
    oracle_all = np.asarray(summary["finite_difference_values"], dtype=float)
    feasible = np.isfinite(oracle_all)
    if not np.any(feasible):
        return None

    link_to_idx = {link: idx for idx, link in enumerate(summary["links"])}
    queue = np.asarray(summary["queue"], dtype=float)
    cap = np.asarray(summary["downstream_capacity"], dtype=float)
    movements = summary["movements"]
    original_indices = np.flatnonzero(feasible)
    ...
    features_all = {
        "upstream_queue": np.asarray(up_q, dtype=float),
        "neg_downstream_queue": -np.asarray(down_q, dtype=float),
        "downstream_slack": np.asarray(down_slack, dtype=float),
        "neg_downstream_fullness": -np.asarray(down_fullness, dtype=float),
        "random_price": random_price,
        "dual_sensitivity": dual,
        "pressure_backpressure": np.asarray(summary["pressure_scores"], dtype=float),
    }
    ...
    return {
        "scenario": summary["scenario"],
        "source": "",
        "oracle": oracle,
        "oracle_best_local": int(np.argmax(oracle)),
        "oracle_best_movement": int(original_indices[int(np.argmax(oracle))]),
        "original_indices": original_indices,
        "features": features,
        "rank_match_finite_difference": bool(summary["rank_match_finite_difference"]),
        "nonbinding_storage": bool(summary["nonbinding_storage"]),
    }
```

**MILP recovery function to reuse** (`scripts/run_sparse_recovery.py` lines 547-563):
```python
def solve_library(
    examples: list[dict[str, Any]],
    library: str,
    atoms: list[str],
    budget: int,
    complexity_penalty: float,
    neighbor_penalty: float,
    dual_penalty: float,
    placebo_penalty: float,
    max_neighbor_atoms: int | None,
    max_dual_atoms: int | None,
    max_placebo_atoms: int | None,
    objective_mode: str,
    time_limit_sec: float,
    min_weight: float,
    tie_margin: float,
) -> dict[str, Any]:
```

**MILP failure handling pattern** (`scripts/run_sparse_recovery.py` lines 659-666):
```python
if not res.success or res.x is None:
    return {
        **base_payload,
        "status": "FAILED",
        "solver_status": int(res.status),
        "message": res.message,
        "solve_time_sec": solve_time,
    }
```

**Solved-run per-example result schema pattern** (`scripts/run_sparse_recovery.py` lines 685-751):
```python
rows_out = []
total_regret = 0.0
max_regret = 0.0
agreement = 0
...
rows_out.append(
    {
        "scenario": ex["scenario"],
        "source": ex["source"],
        "chosen_movement": chosen_movement,
        "oracle_best_movement": ex["oracle_best_movement"],
        "oracle_value_chosen": oracle_value_chosen,
        "oracle_value_best": best,
        "oracle_regret": regret,
        "action_agreement": bool(matched),
        "score_chosen": float(scores[chosen_local]),
        "score_oracle_best": float(scores[int(ex["oracle_best_local"])]),
        "movement_scores": [float(value) for value in scores],
        "selected_y_local": selected_y_local,
        "selected_y_values": [float(value) for value in y_values],
    }
)
...
run = {
    **base_payload,
    "status": "SOLVED",
    ...
    "selected_atoms": selected,
    "selected_atom_metadata": metadata_for_atoms(selected),
    "weights": {atom: float(weights[j]) for j, atom in enumerate(atoms)},
    "program_complexity": len(selected),
    ...
    "realized_total_regret": total_regret,
    "realized_mean_regret": total_regret / len(examples) if examples else 0.0,
    "max_regret": max_regret,
    "action_agreement": agreement / len(examples) if examples else 0.0,
    "penalty_breakdown": penalty_breakdown,
    "results": rows_out,
}
run["rule_text"] = render_rule_text(run, ATOM_REGISTRY)
return run
```

**CSV artifact pattern** (`scripts/run_sparse_recovery.py` lines 400-438):
```python
def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "experiment",
        "input_states",
        "tls",
        "library",
        "max_atoms",
        ...
        "rule_text_path",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
```

**JSON/rules output + compact stdout pattern** (`scripts/run_sparse_recovery.py` lines 905-993):
```python
input_states = [str(p) for p in state_paths]
csv_rows = csv_rows_for_runs("block2_sparse_recovery", input_states, args.tls, runs, rules_path, penalties_payload)
write_csv(csv_path, csv_rows)
rules_path.parent.mkdir(parents=True, exist_ok=True)
rules_path.write_text(render_rules_file(runs, note), encoding="utf-8")

payload = {
    "experiment": "block2_sparse_recovery",
    "status": "INCONCLUSIVE",
    "input_states": input_states,
    "tls": args.tls,
    "num_examples": len(examples),
    ...
    "runs": runs,
    "note": note,
}
...
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
...
print(
    json.dumps(
        {
            "status": payload["status"],
            "out": str(out_path),
            "csv_out": str(csv_path),
            "rules_out": str(rules_path),
            "num_examples": len(examples),
        },
        indent=2,
    )
)
```

**Phase 3 adaptation:**
- Import and call `validate_atom_registry()`, `select_library_names()`, `atoms_for_library()`, `load_examples()`, `solve_library()`, `render_rule_text()` / `render_rules_file()` patterns rather than copying atom formulas or MILP logic.
- For regime-level metrics, either split input samples by `sample["regime"]` into temporary in-memory groups or write small per-regime state payloads, then run `solve_library()` per regime.
- Primary comparison should be `dual_sensitivity` vs `pressure_backpressure`; `dual_plus_raw`, `full_symbolic`, `all_neighbor`, and `random_price` are secondary diagnostics.
- Gate on valid examples after `scenario_from_sample()`, not raw JSON `num_samples`.

---

### `scripts/render_static_kill_gate_report.py` (utility/report renderer, transform + file-I/O)

**Analog:** `scripts/run_sparse_recovery.py` rules renderer and output conventions.

**Rule text renderer pattern** (`scripts/run_sparse_recovery.py` lines 288-334):
```python
def render_rule_text(run: dict[str, Any], atom_metadata: dict[str, dict[str, Any]]) -> str:
    selected_atoms = list(run.get("selected_atoms", []))
    weights = dict(run.get("weights", {}))
    if not selected_atoms:
        expression = "0.0"
    else:
        terms = []
        for atom in selected_atoms:
            metadata = atom_metadata[atom]
            weight = float(weights.get(atom, 0.0))
            terms.append(f"{weight:.6g} * ({metadata['expression']})  # {atom}")
        expression = "\n  + ".join(terms)

    lines = [
        f"Run: library={run.get('library')}, max_atoms={run.get('max_atoms')}, "
        f"max_neighbor_atoms={run.get('max_neighbor_atoms')}, max_dual_atoms={run.get('max_dual_atoms')}, "
        f"max_placebo_atoms={run.get('max_placebo_atoms')}",
        "Counts: "
        f"program={run.get('program_complexity', 0)}, "
        ...
        "Rule: choose movement m maximizing score(m)",
        f"score(m) = {expression}",
        "Selected atoms:",
    ]
```

**Rules file section pattern** (`scripts/run_sparse_recovery.py` lines 337-348):
```python
def render_rules_file(runs: list[dict[str, Any]], note: str) -> str:
    sections = [
        "Phase 2 Sparse Recovery Rule Text",
        note,
        "Generated rules are finite-dictionary, sample-relative audit artifacts.",
    ]
    for run in runs:
        if run.get("status") != "SOLVED":
            continue
        sections.append("\n---\n")
        sections.append(str(run.get("rule_text", "")))
    return "\n".join(sections).rstrip() + "\n"
```

**Phase 3 adaptation:**
- Report generator should consume `block3_static_kill_gate.json` and render route decision, route confidence, regime metrics, sample caveats, unsupported/proxy regime notes, and links to CSV/rules artifacts.
- Keep report deterministic and traceable to JSON fields; do not manually transcribe spreadsheet values.
- Include explicit static-only caveat; do not use travel-time/throughput/closed-loop superiority language.

---

### `experiments/dual_sensitivity/block3_regime_states.json` (data artifact, file-I/O)

**Analog:** `sample_sumo_states.py` and `generate_targeted_bottleneck_states.py` state JSON.

**Sampled-state schema source** (`scripts/sample_sumo_states.py` lines 83-92):
```python
queues = {edge_id: float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids}
vehicle_counts = {edge_id: float(traci.edge.getLastStepVehicleNumber(edge_id)) for edge_id in edge_ids}
samples.append(
    {
        "time": float(traci.simulation.getTime()),
        "queues": queues,
        "vehicle_counts": vehicle_counts,
        "capacities": edge_capacity,
        "tls_movements": tls_movements,
    }
)
```

**Top-level payload schema source** (`scripts/sample_sumo_states.py` lines 119-129):
```python
payload = {
    "network": args.network,
    "sumocfg": str(sumocfg),
    "net_file": str(net_file),
    "seed": args.seed,
    "steps": args.steps,
    "sample_every": args.sample_every,
    "warmup": args.warmup,
    "num_samples": len(samples),
    "samples": samples,
}
```

**Targeted synthetic top-level schema source** (`scripts/generate_targeted_bottleneck_states.py` lines 80-87):
```python
return {
    "network": "arterial_targeted_bottleneck",
    "net_file": str(net_file),
    "tls": tls,
    "num_samples": len(samples),
    "samples": samples,
    "note": "Synthetic targeted states using arterial topology; designed to stress downstream scarcity vs pressure.",
}
```

**Phase 3 required additions:**
- Add per-sample `regime` and `regime_detail`.
- Add per-sample `generated_by` or top-level `generation_config` for reproducibility.
- Keep all existing fields so `scenario_from_sample()` continues to work without a new adapter.

---

### `experiments/dual_sensitivity/block3_static_kill_gate.json` (data artifact, batch result)

**Analog:** `run_sparse_recovery.py` payload.

**Payload schema source** (`scripts/run_sparse_recovery.py` lines 911-960):
```python
payload = {
    "experiment": "block2_sparse_recovery",
    "status": "INCONCLUSIVE",
    "input_states": input_states,
    "tls": args.tls,
    "num_examples": len(examples),
    "objective_mode": args.objective,
    "budgets": budgets,
    "max_atoms": budgets[0] if len(budgets) == 1 else None,
    "max_neighbor_atoms": args.max_neighbor_atoms,
    "max_dual_atoms": args.max_dual_atoms,
    "max_placebo_atoms": args.max_placebo_atoms,
    "penalties": penalties_payload,
    "libraries": library_names,
    "atom_families": sorted(allowed_families) if allowed_families is not None else "all",
    "atom_registry": ATOM_REGISTRY,
    "csv_out": str(csv_path),
    "rules_out": str(rules_path),
    ...
    "summary": compact_summary,
    "best_by_library": [...],
    "runs": runs,
    "note": note,
}
```

**Schema-gate pattern** (`scripts/run_sparse_recovery.py` lines 484-508):
```python
def gate_schema_complete(payload: dict[str, Any]) -> bool:
    required = {
        "experiment",
        "status",
        "input_states",
        "tls",
        "num_examples",
        "objective_mode",
        "budgets",
        "penalties",
        "atom_registry",
        ...
        "summary",
        "runs",
        "csv_out",
        "rules_out",
        "note",
    }
    if not required <= set(payload):
        return False
    solved = [run for run in payload.get("runs", []) if run.get("status") == "SOLVED"]
    return bool(solved) and all(solved_run_schema_complete(run) for run in solved)
```

**Phase 3 required output fields:**
- `experiment`: `block3_static_pressure_failure_kill_gate`
- `status`: `PASSED`, `INCONCLUSIVE`, or `FAILED`
- `input_states`, `tls`, `target_total_states`, `num_examples_total`, `sample_target_met`
- `preliminary_regimes`, `regime_metrics`, `route_decision`, `route_confidence`, `route_rationale`, `route_caveats`
- `runs` or `runs_by_regime`, `csv_out`, `rules_out`, `report_out`

---

### `experiments/dual_sensitivity/block3_static_kill_gate.csv` (data artifact, batch result)

**Analog:** `scripts/run_sparse_recovery.py::write_csv`.

**CSV row construction source** (`scripts/run_sparse_recovery.py` lines 351-397):
```python
def csv_rows_for_runs(
    experiment: str,
    input_states: list[str],
    tls: str,
    runs: list[dict[str, Any]],
    rules_path: Path,
    penalties: dict[str, float],
) -> list[dict[str, Any]]:
    rows = []
    for run in runs:
        selected_metadata = run.get("selected_atom_metadata", [])
        rows.append(
            {
                "experiment": experiment,
                "input_states": ";".join(input_states),
                "tls": tls,
                "library": run.get("library"),
                "max_atoms": run.get("max_atoms", run.get("budget")),
                ...
                "rule_text_path": str(rules_path),
            }
        )
    return rows
```

**Phase 3 CSV columns to add:**
- `regime`, `num_examples`, `sample_target_met`, `claim_scope`
- `dual_vs_pressure_disagreement_rate`, `dual_win_rate`, `pressure_win_rate`, `tie_rate`
- `dual_mean_oracle_regret`, `pressure_mean_oracle_regret`
- `mean_oracle_regret_delta_pressure_minus_dual`
- `dual_worst_case_regret`, `pressure_worst_case_regret`
- `selected_atoms_dual`, `selected_atoms_pressure`, `rule_text_path`

---

### `experiments/dual_sensitivity/block3_static_kill_gate_rules.txt` (data artifact, report text)

**Analog:** `scripts/run_sparse_recovery.py::render_rules_file`.

Use the same rule text pattern shown above. For Phase 3, group sections by regime first, then library/budget:

```text
Phase 3 Static Kill-Gate Rule Text
Generated rules are finite-dictionary, sample-relative audit artifacts.

---
Regime: storage_binding
Run: library=dual_sensitivity, max_atoms=1, ...
Rule: choose movement m maximizing score(m)
...
```

---

### `experiments/dual_sensitivity/block3_static_kill_gate_report.md` (data artifact/report, transform + file-I/O)

**Analog:** compact deterministic report style from JSON/rules outputs in `scripts/run_sparse_recovery.py`.

**Required sections:**
- Route decision: one of `dual-improves-pressure`, `pressure-equivalent`, `diagnostic`.
- Static-only scope and caveats.
- Sample sufficiency: `num_examples_total`, `target_total_states`, `sample_target_met`, preliminary regimes.
- Per-regime table with KILL-02 metrics.
- Unsupported/proxy regime limitations.
- Artifact links: JSON, CSV, rules file.

## Shared Patterns

### Scenario conversion: reuse `scenario_from_sample()`

**Source:** `scripts/run_sumo_sampled_recovery.py` lines 21-57  
**Apply to:** `run_static_kill_gate.py`, any schema validation that needs valid examples.

```python
def scenario_from_sample(sample: dict[str, Any], tls_id: str, max_movements: int) -> Scenario | None:
    movements_raw = sample["tls_movements"].get(tls_id, [])
    queues = sample["queues"]
    capacities = sample["capacities"]
    candidate_moves = []
    edge_set = set()
    for up, down in movements_raw:
        if up in queues and down in queues:
            candidate_moves.append((up, down))
            edge_set.add(up)
            edge_set.add(down)
    candidate_moves = candidate_moves[:max_movements]
    if not candidate_moves:
        return None

    ordered_edges = sorted(edge_set)
    edge_to_idx = {edge: i for i, edge in enumerate(ordered_edges)}
    movements = [(edge_to_idx[up], edge_to_idx[down]) for up, down in candidate_moves]
    queue = np.array([max(float(queues[e]), 0.0) for e in ordered_edges])
    cap = np.array([max(float(capacities[e]), 1.0) for e in ordered_edges])
    # Use a Lyapunov linearization weight. Add 1 to avoid all-zero states.
    queue_weight = queue + 1.0
    storage_penalty = np.where(queue >= 0.8 * cap, 20.0, 0.0)
    service_capacity = np.full(len(movements), 3.0)
    green_budget = min(12.0, 3.0 * len(movements))
    return Scenario(
        name=f"sumo_{tls_id}_t{sample['time']:.0f}",
        links=ordered_edges,
        movements=movements,
        queue=queue,
        downstream_capacity=cap,
        demand=np.zeros(len(ordered_edges)),
        service_capacity=service_capacity,
        green_budget=green_budget,
        queue_weight=queue_weight,
        storage_penalty=storage_penalty,
    )
```

**Do not duplicate:** state-to-`Scenario` edge filtering, capacity clamping, queue weights, storage penalty, service capacity, or green budget logic unless Phase 3 explicitly adds new fields such as `movement_service_capacity`.

### LP oracle / dual / pressure summaries: reuse `summarize_scenario()`

**Source:** `scripts/run_dual_sanity.py` lines 282-325  
**Apply to:** `run_static_kill_gate.py`, example construction, direct dual/pressure comparisons.

```python
def summarize_scenario(s: Scenario, eps: float) -> dict[str, Any]:
    solved = solve_relaxation(no_service_scenario(s))
    fd_values = finite_difference_service_values(s, eps)
    dual_values = solved["movement_values"]
    pressure_scores = solved["pressure_scores"]

    dual_rank = ranking(dual_values)
    fd_rank = ranking(fd_values)
    pressure_rank = ranking(pressure_scores)
    rank_match_fd = dual_rank == fd_rank
    rank_match_pressure = dual_rank == pressure_rank
    ...
    return {
        "scenario": s.name,
        "links": s.links,
        "movements": [
            {"up": s.links[up], "down": s.links[down]} for up, down in s.movements
        ],
        "queue": s.queue.tolist(),
        "downstream_capacity": s.downstream_capacity.tolist(),
        "objective": solved["objective"],
        "service": solved["service"],
        "queue_duals": solved["queue_duals"],
        "storage_duals": solved["storage_duals"],
        "green_budget_dual": solved["green_budget_dual"],
        "dual_movement_values": dual_values,
        "finite_difference_values": fd_values,
        "pressure_scores": pressure_scores,
        "dual_rank": dual_rank,
        "finite_difference_rank": fd_rank,
        "pressure_rank": pressure_rank,
        "dual_fd_correlation": corr,
        "rank_match_finite_difference": rank_match_fd,
        "nonbinding_storage": nonbinding_storage,
        "pressure_special_case_pass": pressure_special_case_pass,
    }
```

**Do not duplicate:** LP model construction, finite-difference oracle, dual movement value calculation, pressure score calculation, ranking, storage special-case check.

### Fail-fast LP error handling

**Source:** `scripts/run_dual_sanity.py` lines 146-156
```python
res = linprog(
    c,
    A_ub=np.array(a_ub),
    b_ub=np.array(b_ub),
    A_eq=np.array(a_eq),
    b_eq=np.array(b_eq),
    bounds=bounds,
    method="highs",
)
if not res.success:
    raise RuntimeError(f"LP failed for {s.name}: {res.message}")
```

**Apply to:** any Phase 3 extension that adds LP constraints. Prefer reusing existing function; if adding optional fields, keep informative `RuntimeError` messages.

### CLI validation pattern

**Source:** `scripts/run_sparse_recovery.py` lines 754-798
```python
parser = argparse.ArgumentParser()
parser.add_argument("--states", action="append", default=[])
parser.add_argument("--tls", default="C3")
parser.add_argument("--max-samples", type=int, default=0)
parser.add_argument("--max-movements", type=int, default=12)
parser.add_argument("--epsilon", type=float, default=1e-3)
parser.add_argument("--budgets", nargs="+", type=int, default=[1, 2])
...
if any(budget <= 0 for budget in budgets):
    raise ValueError(f"Atom budgets must be positive: {budgets}")
...
if args.time_limit_sec <= 0.0:
    raise ValueError("--time-limit-sec must be positive")
if args.min_weight < 0.0:
    raise ValueError("--min-weight must be nonnegative")
if args.tie_margin < 0.0:
    raise ValueError("--tie-margin must be nonnegative")
```

**Apply to:** all new Phase 3 scripts. Validate positive sample targets, nonnegative thresholds/tolerances, known libraries, known regimes, and positive time limits.

### Compact JSON stdout

**Sources:**
- `scripts/sample_sumo_states.py` lines 130-133
- `scripts/run_dual_sanity.py` lines 359-364
- `scripts/run_sparse_recovery.py` lines 982-993

```python
out_path = Path(args.out)
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps({"out": str(out_path), "num_samples": len(samples)}, indent=2))
```

```python
print(
    json.dumps(
        {
            "status": payload["status"],
            "out": str(out_path),
            "csv_out": str(csv_path),
            "rules_out": str(rules_path),
            "num_examples": len(examples),
        },
        indent=2,
    )
)
```

**Apply to:** generator, kill-gate runner, report renderer.

## Existing Structure

- OR/SUMO experiment code lives under `scripts/` and writes artifacts under `experiments/dual_sensitivity/`.
- Existing state fixtures share a stable schema: top-level `network`, optional `net_file`/`sumocfg`/`seed`, `num_samples`, `samples`; each sample has `time`, `queues`, `vehicle_counts`, `capacities`, and `tls_movements`.
- Existing optimization flow is:
  1. JSON sample → `scenario_from_sample()`
  2. `Scenario` → `summarize_scenario()`
  3. summary → `build_example()` atom features
  4. examples + library → `solve_library()`
  5. runs → JSON/CSV/rules artifacts + compact stdout
- Phase 3 should add regime grouping/routing on top of this flow, not replace it.

## New Scripts Should Reuse

| Need | Reuse From | Function/Pattern |
|------|------------|------------------|
| Network capacities and TLS movements | `scripts/sample_sumo_states.py` | `build_network_metadata()` |
| State sample schema | `scripts/sample_sumo_states.py`, `scripts/generate_targeted_bottleneck_states.py` | `time`, `queues`, `vehicle_counts`, `capacities`, `tls_movements` |
| Synthetic bottleneck queue perturbations | `scripts/generate_targeted_bottleneck_states.py` | `base_queues()`, `make_sample()`, `generate()` loops |
| Sample-to-scenario conversion | `scripts/run_sumo_sampled_recovery.py` | `scenario_from_sample()` |
| LP oracle / dual / pressure | `scripts/run_dual_sanity.py` | `summarize_scenario()` |
| Sparse examples | `scripts/run_sparse_recovery.py` | `load_examples()`, `build_example()` |
| Atom libraries and metadata | `scripts/run_sparse_recovery.py` | `ATOM_REGISTRY`, `LIBRARIES`, `atoms_for_library()` |
| MILP recovery | `scripts/run_sparse_recovery.py` | `solve_library()` |
| Rule text | `scripts/run_sparse_recovery.py` | `render_rule_text()`, `render_rules_file()` |
| CSV output | `scripts/run_sparse_recovery.py` | `csv_rows_for_runs()`, `write_csv()` style |
| JSON/stdout | all existing scripts | `Path.write_text(json.dumps(...))` + compact `print(json.dumps(...))` |

## Avoid Duplicate Implementation

- Do not rebuild the LP model or finite-difference oracle in Phase 3; use `summarize_scenario()`.
- Do not write a second SUMO sample adapter; use `scenario_from_sample()` and only extend it if explicit new JSON fields require it.
- Do not redefine atom formulas, atom families, or sparse-recovery MILP constraints; use `ATOM_REGISTRY`, `LIBRARIES`, and `solve_library()`.
- Do not treat `dual_plus_raw` as pure dual evidence; primary route comparison is `dual_sensitivity` vs `pressure_backpressure`.
- Do not aggregate slack and binding regimes before routing; compute per-regime metrics first.
- Do not claim supply-binding or corridor-bottleneck evidence unless explicit fields/model support exist; otherwise use proxy/unsupported labels.
- Do not claim closed-loop travel-time/throughput superiority in Phase 3 reports.
- Do not count raw samples toward the 1k target before conversion; count valid examples after `scenario_from_sample()` and `build_example()`.

## Metric Pattern for Phase 3

Use aligned run rows from `dual_sensitivity` and `pressure_backpressure`:

```python
dual_by_key = {(r["source"], r["scenario"]): r for r in dual_run["results"]}
pressure_by_key = {(r["source"], r["scenario"]): r for r in pressure_run["results"]}
keys = sorted(set(dual_by_key) & set(pressure_by_key))

for key in keys:
    d = dual_by_key[key]
    p = pressure_by_key[key]
    d_regret = float(d["oracle_regret"])
    p_regret = float(p["oracle_regret"])
    disagreement = d["chosen_movement"] != p["chosen_movement"]
    dual_win = d_regret < p_regret - tol
    pressure_win = p_regret < d_regret - tol
    tie = abs(d_regret - p_regret) <= tol
```

Required per-regime outputs:
- `dual_vs_pressure_disagreement_rate`
- `dual_win_rate`
- `pressure_win_rate`
- `tie_rate`
- `dual_mean_oracle_regret`
- `pressure_mean_oracle_regret`
- `mean_oracle_regret_delta_pressure_minus_dual`
- `dual_worst_case_regret`
- `pressure_worst_case_regret`
- recovered symbolic rules / selected atoms for both libraries

## Validation Commands

Existing substrate validation before implementing Phase 3:

```bash
PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py --out /tmp/block0_dual_sanity.json
```

```bash
PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py --states /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/targeted_bottleneck_states.json --budgets 1 2 3 --out /tmp/block2_sparse_recovery.json --csv-out /tmp/block2_sparse_recovery.csv --rules-out /tmp/block2_sparse_recovery_rules.txt
```

Expected Phase 3 quick validation command after implementation:

```bash
PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py --states /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/targeted_bottleneck_states.json --tls C3 --max-samples 16 --default-regime storage_binding_proxy --target-total-states 1000 --out /tmp/block3_static_kill_gate.json --csv-out /tmp/block3_static_kill_gate.csv --rules-out /tmp/block3_static_kill_gate_rules.txt --report-out /tmp/block3_static_kill_gate_report.md
```

Expected Phase 3 full validation command after implementation:

```bash
PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py --target-per-regime 200 --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_regime_states.json && PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts python3 /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py --states /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_regime_states.json --target-total-states 1000 --out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.json --csv-out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate.csv --rules-out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_rules.txt --report-out /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_static_kill_gate_report.md
```

Compile validation after new scripts exist:

```bash
python3 -m py_compile /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py /home/samuel/projects/pi_light_OR/scripts/render_static_kill_gate_report.py
```

## No Analog Found

None. All planned Phase 3 files have close analogs in the existing OR/SUMO script stack.

## Metadata

**Analog search scope:** `/home/samuel/projects/pi_light_OR/scripts`, `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity`  
**Files scanned/read:** 8 primary files/artifacts plus phase context/research/project instructions  
**Pattern extraction date:** 2026-05-23
