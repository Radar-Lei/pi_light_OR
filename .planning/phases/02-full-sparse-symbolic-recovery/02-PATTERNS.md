# Phase 2: Full Sparse Symbolic Recovery - Pattern Map

**Mapped:** 2026-05-23
**Scope:** 只读探索 Phase 2 sparse recovery 相关代码模式
**Files analyzed:** 3 source files + Phase context/research
**Analogs found:** 3 / 3

## File Classification

| New/Modified File / Region | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `/home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py` | experiment runner + MILP recovery solver | batch + transform + file-I/O | same file, existing Block 1 sparse scaffold | exact |
| `/home/samuel/projects/pi_light_OR/scripts/run_sumo_sampled_recovery.py::scenario_from_sample` | scenario conversion utility | transform | imported by `run_sparse_recovery.py::load_examples` | exact reuse |
| `/home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py::summarize_scenario` | LP oracle/dual summarizer | transform + optimization | imported by `run_sparse_recovery.py::load_examples` | exact reuse |

## 现有结构

### `/home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py`

**Imports pattern** (lines 1-15): standalone script, `argparse` + `json` + `Path` + NumPy/SciPy, direct imports from sibling scripts.

```python
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from run_dual_sanity import summarize_scenario
from run_sumo_sampled_recovery import scenario_from_sample
```

**Atom/library scaffold** (lines 18-26): current library is string-only; Phase 2 should wrap/replace with metadata registry while preserving named libraries.

```python
LIBRARIES = {
    "local_only": ["upstream_queue"],
    "raw_neighbor": ["upstream_queue", "neg_downstream_queue"],
    "all_neighbor": ["upstream_queue", "neg_downstream_queue", "downstream_slack", "neg_downstream_fullness"],
    "random_price": ["random_price"],
    "dual_sensitivity": ["dual_sensitivity"],
    "dual_plus_raw": ["dual_sensitivity", "upstream_queue", "neg_downstream_queue"],
    "pressure_backpressure": ["pressure_backpressure"],
}
```

**Input pipeline** (lines 29-47): `load_examples()` reads state JSON, calls `scenario_from_sample()`, then `summarize_scenario()`, then `build_example()`.

```python
scenario = scenario_from_sample(sample, tls, max_movements)
if scenario is None:
    continue
summary = summarize_scenario(scenario, epsilon)
example = build_example(summary)
```

**Feature construction** (lines 49-99): `build_example()` computes oracle values and atom feature vectors. Existing atoms cover upstream queue, negative downstream queue, downstream slack/fullness, random dual placebo, dual sensitivity, and pressure/backpressure.

```python
features_all = {
    "upstream_queue": np.asarray(up_q, dtype=float),
    "neg_downstream_queue": -np.asarray(down_q, dtype=float),
    "downstream_slack": np.asarray(down_slack, dtype=float),
    "neg_downstream_fullness": -np.asarray(down_fullness, dtype=float),
    "random_price": random_price,
    "dual_sensitivity": dual,
    "pressure_backpressure": np.asarray(summary["pressure_scores"], dtype=float),
}
```

**Normalization pattern** (lines 101-107): feature matrices are normalized per atom by max absolute value across examples.

```python
scale = float(np.max(np.abs(values))) if values.size else 1.0
scales[atom] = scale if scale > 1e-12 else 1.0
return [np.vstack([ex["features"][atom] / scales[atom] for atom in atoms]) for ex in examples]
```

**MILP pattern** (lines 110-233): `solve_library()` owns objective, binary atom selection variables, action choice variables, constraints, solve call, and realized regret/action agreement output.

Key regions:
- Lines 118-127: atoms, matrices, variable layout.
- Lines 131-137: regret-first objective coefficients; complexity penalty currently on selected atoms.
- Lines 159-162: weight-selection linking constraints and total atom budget.
- Lines 164-177: big-M choice constraints.
- Lines 180-186: SciPy `milp()` with HiGHS backend and fixed 60s time limit.
- Lines 197-233: selected atoms, weights, realized regret, action agreement, per-example results.

**CLI/output pattern** (lines 236-343): `main()` defines arguments, loops over budgets/libraries, builds compact summary, writes JSON, prints compact JSON status.

```python
parser.add_argument("--states", action="append", default=[])
parser.add_argument("--tls", default="C3")
parser.add_argument("--max-samples", type=int, default=0)
parser.add_argument("--max-movements", type=int, default=12)
parser.add_argument("--epsilon", type=float, default=1e-3)
parser.add_argument("--budgets", nargs="+", type=int, default=[1, 2])
parser.add_argument("--complexity-penalty", type=float, default=1e-4)
parser.add_argument("--min-weight", type=float, default=0.1)
parser.add_argument("--tie-margin", type=float, default=1e-6)
parser.add_argument("--out", default="experiments/dual_sensitivity/block1_sparse_recovery.json")
```

Output currently includes top-level fields `experiment`, `status`, `input_states`, `tls`, `num_examples`, `budgets`, gates, `summary`, `best_by_library`, `runs`, `note`, then writes JSON via `Path(args.out).write_text(...)` and prints `{"status", "out", "num_examples"}`.

## 需要修改的函数/区域

### 1. Atom metadata registry near `LIBRARIES` (lines 18-26)

Add explicit metadata next to existing atom names. Do not infer family from string prefixes.

Required metadata fields for Phase 2:
- `name`
- `family`: local / capacity / raw_neighbor / pressure / dual / placebo
- `requires_neighbor`
- `uses_dual`
- `is_placebo`
- `expression`
- `description`

Keep `LIBRARIES` as named views over atom names for backward compatibility, and add a `full_symbolic` library containing all allowed Phase 2 atoms.

### 2. Feature construction in `build_example()` (lines 49-99)

Reuse the existing feature keys. Add new atoms only if their values can be computed from `summary`, queues, capacities, movements, dual values, or pressure scores. Do not add corridor/service atoms unless Phase 1 constraints provide explicit primal quantities.

### 3. MILP objective and constraints in `solve_library()` (lines 110-233)

Current objective is already regret-first:

```python
best = float(np.max(ex["oracle"]))
for m_idx, value in enumerate(ex["oracle"]):
    c[y_offsets[ex_idx] + m_idx] = best - float(value)
```

Extend this by adding metadata-driven soft penalties on selected-atom variables `z_j`, while preserving realized regret separately from penalty objective.

Add hard constraints after the total budget constraint around line 162:

```python
add({z_offset + j: 1.0 for j in neighbor_atom_indices}, 0.0, max_neighbor_atoms)
add({z_offset + j: 1.0 for j in dual_atom_indices}, 0.0, max_dual_atoms)
add({z_offset + j: 1.0 for j in placebo_atom_indices}, 0.0, max_placebo_atoms)
```

Make `time_limit` configurable instead of fixed at line 185.

### 4. Solver return payload in `solve_library()` (lines 220-233)

Add fields required by Phase 2:
- `max_atoms`, `max_neighbor_atoms`, `max_dual_atoms`, `max_placebo_atoms`
- `objective_value_with_penalties`
- `selected_atom_metadata`
- `neighbor_atom_count`, `dual_atom_count`, `placebo_atom_count`, `pressure_atom_count`, `raw_neighbor_atom_count`, `capacity_atom_count`
- `penalty_breakdown`
- `max_regret`
- `rule_text`
- per-example `oracle_value_chosen`, `oracle_value_best`, `action_agreement`, `score_chosen`, `score_oracle_best`

### 5. CLI and artifact writing in `main()` (lines 236-343)

Add or clarify:
- `--libraries`
- `--atom-families`
- `--max-atoms` as a clearer single-run alias while preserving `--budgets`
- `--max-neighbor-atoms`
- `--max-dual-atoms`
- `--max-placebo-atoms`
- `--neighbor-penalty`
- `--dual-penalty`
- `--placebo-penalty`
- `--csv-out`
- `--rules-out`
- `--time-limit-sec`
- `--objective`, default `oracle_regret`

Extend output from JSON-only to JSON + CSV + rule text, with defaults derived from `--out`.

## 最近似实现模式

### Scenario conversion: `/home/samuel/projects/pi_light_OR/scripts/run_sumo_sampled_recovery.py::scenario_from_sample`

**Pattern** (lines 21-57): convert sampled SUMO dictionaries into `Scenario`; return `None` for unusable samples.

```python
def scenario_from_sample(sample: dict[str, Any], tls_id: str, max_movements: int) -> Scenario | None:
    movements_raw = sample["tls_movements"].get(tls_id, [])
    queues = sample["queues"]
    capacities = sample["capacities"]
    candidate_moves = []
    edge_set = set()
    ...
    if not candidate_moves:
        return None
    ...
    return Scenario(...)
```

Use this directly; do not duplicate SUMO topology logic inside `run_sparse_recovery.py`.

### Oracle/dual summary: `/home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py::summarize_scenario`

**Pattern** (lines 282-325): solve no-service LP, compute finite-difference oracle values, dual movement values, pressure scores, rankings, correlation, and special-case flags; return JSON-serializable dict.

```python
def summarize_scenario(s: Scenario, eps: float) -> dict[str, Any]:
    solved = solve_relaxation(no_service_scenario(s))
    fd_values = finite_difference_service_values(s, eps)
    dual_values = solved["movement_values"]
    pressure_scores = solved["pressure_scores"]
    ...
    return {
        "scenario": s.name,
        "links": s.links,
        "movements": [{"up": s.links[up], "down": s.links[down]} for up, down in s.movements],
        "queue": s.queue.tolist(),
        "downstream_capacity": s.downstream_capacity.tolist(),
        "dual_movement_values": dual_values,
        "finite_difference_values": fd_values,
        "pressure_scores": pressure_scores,
        ...
    }
```

Use this as the sole oracle/value source. Phase 2 should not implement a second LP or finite-difference path.

### Script artifact pattern

Both `run_dual_sanity.py` and `run_sparse_recovery.py` use:

```python
out_path = Path(args.out)
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps({"status": status, "out": str(out_path), ...}, indent=2))
```

Copy this pattern for JSON, and use analogous `Path` handling for CSV and rules TXT.

## Shared Patterns

### Error handling

- LP failure in `/home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py` lines 155-156 raises `RuntimeError`.
- MILP failure in `/home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py` lines 188-195 returns a structured failed run payload instead of crashing.
- Invalid sampled scenarios return `None` and are skipped in `/home/samuel/projects/pi_light_OR/scripts/run_sumo_sampled_recovery.py` lines 33-34 and `/home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py` lines 36-38.

### Output status convention

Use `PASSED`, `FAILED`, or `INCONCLUSIVE` status fields. For Phase 2, status should gate schema/recovery completeness and K > 1 solve availability, not whether dual beats pressure; Phase 3 owns that claim.

### Claim discipline

The output note should state that Phase 2 produces finite-dictionary, sample-relative sparse recovery artifacts and defers dual-vs-pressure empirical claim routing to Phase 3.

## No Analog Found

| Needed Capability | Reason | Recommended Pattern |
|---|---|---|
| CSV writer | Current recovery script writes JSON only | Use stdlib `csv.DictWriter` in `main()` or helper |
| Rule text renderer | Current script has weights but no symbolic text output | Add pure formatting helper over selected atoms + metadata + weights |
| Atom metadata registry | Current `LIBRARIES` is string-only | Add explicit registry next to `LIBRARIES` |
| Neighbor/dual/placebo hard budgets | Current MILP only has total atom budget | Add linear constraints over selected atom variables `z_j` |

## 验证命令

Run from project root `/home/samuel/projects/pi_light_OR`.

### Quick Phase 2 validation

```bash
python3 scripts/run_sparse_recovery.py \
  --states experiments/dual_sensitivity/targeted_bottleneck_states.json \
  --budgets 1 2 3 \
  --out experiments/dual_sensitivity/block2_sparse_recovery.json \
  --csv-out experiments/dual_sensitivity/block2_sparse_recovery.csv \
  --rules-out experiments/dual_sensitivity/block2_sparse_recovery_rules.txt
```

### Full script-chain validation

```bash
python3 scripts/run_dual_sanity.py && \
python3 scripts/run_sumo_sampled_recovery.py && \
python3 scripts/run_sparse_recovery.py \
  --states experiments/dual_sensitivity/arterial_sampled_states.json \
  --states experiments/dual_sensitivity/targeted_bottleneck_states.json \
  --budgets 1 2 3 \
  --out experiments/dual_sensitivity/block2_sparse_recovery_combined.json \
  --csv-out experiments/dual_sensitivity/block2_sparse_recovery_combined.csv \
  --rules-out experiments/dual_sensitivity/block2_sparse_recovery_combined_rules.txt
```

## Metadata

**Analog search scope:** `/home/samuel/projects/pi_light_OR/scripts/`, Phase 2 context/research files
**Files scanned:** 5
**Pattern extraction date:** 2026-05-23
