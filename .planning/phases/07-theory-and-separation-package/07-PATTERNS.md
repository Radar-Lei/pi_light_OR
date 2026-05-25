# Phase 7: Theory and Separation Package - Pattern Map

**Mapped:** 2026-05-24  
**Files analyzed:** 4 new files  
**Analogs found:** 4 / 4  
**Scope:** read-only source/codebase mapping; only this PATTERNS artifact is written.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `refine-logs/THEORY_AND_SEPARATION.md` | technical memo / theory artifact | static prose, claim-audit surface | `refine-logs/THEORY_AND_CLAIMS.md` + `refine-logs/THEORY_AND_ATOMS.md` | exact |
| `scripts/check_theory_separation.py` | utility / deterministic checker-generator | transform + batch JSON artifact | `scripts/run_dual_sanity.py` + `scripts/finite_storage_schema.py` | exact |
| `tests/test_theory_separation.py` | test | request-response subprocess + validation assertions | `tests/test_finite_storage_schema.py` + `tests/test_claim_discipline.py` | exact |
| `experiments/dual_sensitivity/phase7_theory_separation.json` | config/data artifact | file-I/O JSON audit artifact | `experiments/dual_sensitivity/phase6_explicit_state_schema.json` + `experiments/dual_sensitivity/phase6_state_objective_fixtures.json` + `experiments/dual_sensitivity/block3_static_kill_gate.json` | exact |

## Pattern Assignments

### `refine-logs/THEORY_AND_SEPARATION.md` (technical memo, static prose / claim-audit surface)

**Primary analog:** `refine-logs/THEORY_AND_CLAIMS.md`  
**Secondary analog:** `refine-logs/THEORY_AND_ATOMS.md`

**Memo header and traceability pattern** (`refine-logs/THEORY_AND_CLAIMS.md` lines 0-5):

```markdown
# Theory and Claim-Lock Memo

**Date**: 2026-05-22  
**Phase**: 01 — Theoretical Core and Claim Lock  
**Requirements covered in this phase artifact**: THRY-01, THRY-02, THRY-03, THRY-04, THRY-05  
**Primary references**: `.planning/phases/01-theoretical-core-and-claim-lock/01-CONTEXT.md`, `.planning/phases/01-theoretical-core-and-claim-lock/01-RESEARCH.md`, `refine-logs/THEORY_AND_ATOMS.md`, `scripts/run_dual_sanity.py`, `pi_light_code/agent/rule_based/max_pressure.py`
```

**Copy/adapt for Phase 7:** use uppercase filename, top-level purpose, phase ID, requirement list `THRY-01` through `THRY-04`, and primary references to Phase 7 context/research plus Phase 6 schema/claim artifacts.

**Claim discipline pattern** (`refine-logs/THEORY_AND_CLAIMS.md` lines 11-25):

```markdown
## Claim-Discipline Guardrails

Allowed within this Phase 1 theory artifact:

- define a store-and-forward / CTM-lite continuous relaxation with queue conservation, movement service, phase compatibility, and storage/supply/capacity constraints;
- interpret LP/KKT shadow prices as movement-level marginal service values;
- state that dual sensitivity is a generalized pressure object that can reduce to pressure under slack or ranking-neutral conditions;
- state that storage, supply, phase/service, or corridor terms enter only when those primal constraints are explicitly modeled.

Not allowed in this memo:

- treating Phase 1 as closed-loop empirical evidence;
- claiming universal improvement over max-pressure or capacity-aware pressure baselines;
- adding ADMM, robust optimization, column generation, bilevel optimization, freight/TR-E pivots, or GPU-heavy MARL to the Phase 1 scope;
- introducing corridor or service-balance dual terms without writing the corresponding primal constraint.
```

**Copy/adapt for Phase 7:** keep the “Allowed / Not allowed” shape. Replace Phase 1 wording with: allowed = slack recovery theorem, explicit finite-storage binding separation, predeclared one-step objective improvement, constrained LP oracle regret candidate; not allowed = live controller, closed-loop SUMO, universal/deployable superiority, proxy-only evidence.

**Theory theorem/proof-section pattern** (`refine-logs/THEORY_AND_CLAIMS.md` lines 201-240):

```markdown
## THRY-03 — Pressure/Backpressure Special Case

### Theorem 1 — Pressure/backpressure is the slack-regime dual ranking

Consider the THRY-01 relaxation at a fixed local traffic state with a fixed set of feasible movements and phase-compatible movement groups. Suppose the following conditions hold for the movements being compared:

1. **Queue-value specialization**: the link value used by the relaxation is a monotone queue weight `w_l`, and in the ordinary pressure case `w_l = x_l`.
2. **Interior service perturbations**: upstream queues permit the compared infinitesimal services, next-queue lower bounds remain slack, and movement lower/upper service bounds do not bind non-neutrally.
3. **Slack or ranking-neutral scarcity and resources**: storage, supply, downstream receiving-capacity, phase/green resources, service-feasibility constraints, and optional corridor/service constraints are either nonbinding for the compared infinitesimal services or contribute the same additive or positive affine adjustment to all compared movement scores, so they do not change the ranking.
```

**Copy/adapt for Phase 7:** use this as the direct THRY-01 theorem template. Phase 7 should tighten assumptions to finite-storage v1.1 fields: infinite/nonbinding storage, no switching loss, fixed turning ratios, slack incident/service terms, and common/tie handling.

**Movement-value sign convention pattern** (`refine-logs/THEORY_AND_ATOMS.md` lines 35-45, 73-89):

```markdown
Let `lambda_l` denote the equality dual for the queue conservation constraint of link `l`, under the solver sign convention used by `scipy.optimize.linprog(method="highs")`.

- `lambda_l` is the marginal objective sensitivity of one additional vehicle in the conservation balance of link `l`,
- binding downstream storage changes `lambda_l` through the storage dual and overflow penalty,
- the movement value reported by the implementation is `lambda_up - lambda_down`.
```

```markdown
Then `lambda_l = w_l` up to the common solver sign convention, and therefore:

```text
MovementValue(i,j) = lambda_i - lambda_j = w_i - w_j.
```

If `w_l = x_l`, this is the ordinary pressure/backpressure movement ranking.
```

**Copy/adapt for Phase 7:** keep `lambda_up - lambda_down` exactly. Do not invert signs. Any finite-storage correction must be framed as explicit scarcity correction to downstream link value or an explicitly written constraint multiplier.

**Binding-rank-change pattern** (`refine-logs/THEORY_AND_CLAIMS.md` lines 260-316):

```markdown
## THRY-04 — Binding-Regime Scarcity Correction

### Proposition 1 — Sufficient binding-regime rank-change condition

Consider two candidate movements `a=(i,j)` and `b=(p,q)` ...

```text
D_a = P_a + C_a,
D_b = P_b + C_b,
```

where `C_a` and `C_b` collect only correction terms generated by explicit primal constraints ...

If ordinary pressure ranks movement `a` above movement `b` ... but the modeled scarcity correction satisfies

```text
C_b - C_a > P_a - P_b,
```

then the dual-sensitivity ranking places `b` above `a`.
```

**Copy/adapt for Phase 7:** this is the algebra for THRY-02. Phase 7 must add an explicit two-phase finite-storage example and a strict objective comparison, not just the sufficient condition.

---

### `scripts/check_theory_separation.py` (utility/checker-generator, transform + batch JSON)

**Primary analog:** `scripts/run_dual_sanity.py`  
**Schema analog:** `scripts/finite_storage_schema.py`  
**CLI/JSON artifact analog:** `scripts/generate_static_regime_states.py`

**Imports and standalone script pattern** (`scripts/run_dual_sanity.py` lines 0-18):

```python
#!/usr/bin/env python3
"""Block 0 sanity checks for dual-sensitivity-guided signal control.

This script uses a continuous one-step store-and-forward LP relaxation.
It validates whether dual/reduced-cost movement values match finite
objective perturbations and whether the nonbinding-storage special case
recovers a pressure-like ranking.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any
```

**Copy/adapt for Phase 7:** keep shebang, top-level scope docstring, `from __future__ import annotations`, `argparse/json/Path/Any`. Prefer stdlib; only import SciPy/NumPy if planner chooses LP validation. For the recommended lightweight checker, import only `finite_storage_schema` validators/builders.

**Dataclass scenario pattern** (`scripts/run_dual_sanity.py` lines 21-33):

```python
@dataclass(frozen=True)
class Scenario:
    name: str
    links: list[str]
    movements: list[tuple[int, int]]
    queue: np.ndarray
    downstream_capacity: np.ndarray
    demand: np.ndarray
    service_capacity: np.ndarray
    green_budget: float
    queue_weight: np.ndarray
    storage_penalty: np.ndarray
```

**Copy/adapt for Phase 7:** if using a structured object, define a frozen `SeparationCase` with fields like `name`, `links`, `phases`, `queues`, `capacities`, `finite_storage_state`, `action_objective_components`, and score parameters. If avoiding NumPy, use `dict[str, float]` and lists.

**Movement value and pressure convention** (`scripts/run_dual_sanity.py` lines 166-183):

```python
movement_values = []
pressure_scores = []
for m_idx, (up, down) in enumerate(s.movements):
    value = equality_duals[up] - equality_duals[down]
    movement_values.append(value)
    pressure_scores.append(s.queue_weight[up] - s.queue_weight[down])

return {
    "objective": float(res.fun),
    "x_next": x.tolist(),
    "service": u.tolist(),
    "overflow": z.tolist(),
    "queue_duals": equality_duals.tolist(),
    "green_budget_dual": float(upper_duals[0]),
    "storage_duals": upper_duals[1:].tolist(),
    "movement_values": movement_values,
    "pressure_scores": pressure_scores,
```

**Copy/adapt for Phase 7:** checker should recompute `pressure_scores` as upstream queue/weight minus downstream queue/weight, then recompute finite-storage scores as `pressure + declared_explicit_correction`. Record both score maps and selected actions in JSON.

**Ranking/check summary pattern** (`scripts/run_dual_sanity.py` lines 278-325):

```python
def ranking(values: list[float]) -> list[int]:
    return sorted(range(len(values)), key=lambda i: values[i], reverse=True)


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
```

**Copy/adapt for Phase 7:** define pure helpers such as `rank_actions(score_by_action)`, `score_pressure(case)`, `score_finite_storage(case)`, `objective_total(components, weights)`, `build_and_check_payload()`. Tests should import these helpers directly.

**CLI write/print/fail pattern** (`scripts/run_dual_sanity.py` lines 328-364):

```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=[
            "toy_nonbinding",
            "toy_storage_binding",
            "single_intersection_proxy",
            "arterial_bottleneck_proxy",
        ],
    )
    parser.add_argument("--epsilon", type=float, default=1e-3)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block0_dual_sanity.json")
    args = parser.parse_args()

    results = [summarize_scenario(build_scenario(name), args.epsilon) for name in args.scenarios]
    gate_a_pass = all(
        r["rank_match_finite_difference"] and r["pressure_special_case_pass"] for r in results
    )
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

**Copy/adapt for Phase 7:** default output must be `experiments/dual_sensitivity/phase7_theory_separation.json`; payload should include `experiment`, `status`, `requirements_covered`, `schema_version`, `criteria`, `examples`, and `claim_scope`. Exit nonzero only if validations fail.

**Schema validator import/use pattern** (`scripts/generate_static_regime_states.py` lines 17-22, 114-136):

```python
from finite_storage_schema import (
    build_finite_storage_state,
    build_objective_components,
    validate_state_objective_sample,
    write_schema_artifact,
)
```

```python
"finite_storage_state": build_finite_storage_state(
    normalized_queues,
    normalized_capacities,
    current_phase=int(time) % 4,
    time_since_switch=float(time % 10),
    incident_edge=incident_edge,
    capacity_drop_factor=capacity_drop_factor,
),
"objective_components": build_objective_components(
    normalized_queues,
    unfinished_vehicle_count=int(spillback_blocking_count),
    spillback_blocking_count=int(spillback_blocking_count),
    switching_count=switching_count,
    horizon=1.0,
),
...
validate_state_objective_sample(sample)
```

**Copy/adapt for Phase 7:** do not hand-roll state/objective required-field checks. Build or validate each example through Phase 6 helpers.

---

### `tests/test_theory_separation.py` (test, subprocess + direct validation)

**Primary analog:** `tests/test_finite_storage_schema.py`  
**Claim-audit analog:** `tests/test_claim_discipline.py`

**Test import and scripts path pattern** (`tests/test_finite_storage_schema.py` lines 1-24):

```python
#!/usr/bin/env python3
"""Behavior checks for explicit finite-storage state and objective schema."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from finite_storage_schema import (  # noqa: E402
    FINITE_STORAGE_STATE_FIELDS,
    OBJECTIVE_COMPONENT_FIELDS,
    build_objective_components_from_metrics,
    schema_artifact_payload,
    validate_finite_storage_state,
    validate_objective_components,
    validate_state_objective_sample,
)
```

**Copy/adapt for Phase 7:** import `build_and_check_phase7_payload` or similarly named pure function from `check_theory_separation.py`; keep `sys.path.insert(0, str(SCRIPTS))`; import validators from `finite_storage_schema`.

**Fixture pattern for explicit state/objective** (`tests/test_finite_storage_schema.py` lines 44-64):

```python
def explicit_state() -> dict[str, Any]:
    return {
        "downstream_storage": {"edge_a": 10.0, "edge_b": 8.0},
        "residual_receiving_capacity": {"edge_a": 7.0, "edge_b": 1.0},
        "spillback_blocking": {
            "edge_a": {"spillback": False, "blocking": False, "occupancy_ratio": 0.3},
            "edge_b": {"spillback": True, "blocking": True, "occupancy_ratio": 0.9},
        },
        "switching_loss_state": {"current_phase": 1, "time_since_switch": 5.0},
        "service_urgency": {"edge_a": 3.0, "edge_b": 9.0},
        "incident_capacity_drop": {"active": True, "edge": "edge_b", "factor": 0.5},
    }


def explicit_objective() -> dict[str, float]:
    return {
        "delay": 12.0,
        "unfinished_vehicle_penalty": 3.0,
        "spillback_blocking_time": 2.0,
        "switching_lost_time": 4.0,
    }
```

**Copy/adapt for Phase 7:** include deterministic two-phase fixtures inline or verify payload examples. Required tests: slack recovery/tie, binding action separation, strict objective improvement, schema validation, THRY markers, claim-safe wording.

**Subprocess CLI pattern** (`tests/test_claim_discipline.py` lines 17-30):

```python
def run_audit(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def read_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload
```

**Copy/adapt for Phase 7:** add `run_checker(*args)` with `SCRIPT = SCRIPTS / "check_theory_separation.py"`, use `tmp_path` for output, assert `returncode == 0`, read JSON, and assert status/requirements/fields.

**Validation error pattern** (`tests/test_finite_storage_schema.py` lines 77-102):

```python
def test_explicit_finite_storage_state_required_fields() -> None:
    assert FINITE_STORAGE_STATE_FIELDS == EXPECTED_STATE_FIELDS
    validate_finite_storage_state(explicit_state(), path=Path("fixture.json"), sample_idx=0)

    for missing_field in EXPECTED_STATE_FIELDS:
        invalid = explicit_state()
        invalid.pop(missing_field)
        try:
            validate_finite_storage_state(invalid, path=Path("fixture.json"), sample_idx=7)
        except ValueError as exc:
            message = str(exc)
            assert missing_field in message
            assert "fixture.json" in message
            assert "Sample 7" in message
        else:  # pragma: no cover - exercised only when implementation is broken
            raise AssertionError(f"missing {missing_field} was accepted")
```

**Copy/adapt for Phase 7:** use try/except assertions for malformed example payloads if direct validators are tested. For CLI failures, assert nonzero and useful stderr/status.

**Claim policy/audit test pattern** (`tests/test_claim_discipline.py` lines 33-49, 141-170):

```python
def test_claim_policy_encodes_bounded_claim() -> None:
    policy = bounded_claim_policy()

    assert policy["status"] == "PASSED"
    assert policy["permitted_claim"] == (
        "recover_or_tie_max_pressure_when_constraints_slack; "
        "improvement_claims_only_for_explicit_binding_finite_storage_spillback_switching_service_incident_regimes"
    )
```

```python
def test_bounded_claim_language_passes_claim_audit(tmp_path: Path) -> None:
    report = tmp_path / "bounded.md"
    ...
    report.write_text(
        "Slack regimes recover/tie max-pressure. Binding improvement needs explicit finite-storage "
        "evidence with objective components before any improvement claim.",
        encoding="utf-8",
    )
```

**Copy/adapt for Phase 7:** test the new memo/artifact surfaces with `audit_claim_discipline.py --paths refine-logs/THEORY_AND_SEPARATION.md experiments/dual_sensitivity/phase7_theory_separation.json --allow-missing-paths` in verification; unit tests can assert bounded language snippets and no forbidden hits.

---

### `experiments/dual_sensitivity/phase7_theory_separation.json` (JSON artifact, file-I/O audit artifact)

**Primary analogs:**
- `experiments/dual_sensitivity/phase6_explicit_state_schema.json`
- `experiments/dual_sensitivity/phase6_state_objective_fixtures.json`
- `experiments/dual_sensitivity/block3_static_kill_gate.json`

**Top-level status/schema pattern** (`phase6_explicit_state_schema.json` lines 1-22):

```json
{
  "experiment": "phase6_explicit_state_schema",
  "status": "PASSED",
  "generated_by": "scripts/finite_storage_schema.py",
  "requirements_covered": [
    "STATE-01",
    "STATE-02"
  ],
  "schema_version": "phase6_explicit_state_v1",
  "finite_storage_state_fields": [
    "downstream_storage",
    "incident_capacity_drop",
    "residual_receiving_capacity",
    "service_urgency",
    "spillback_blocking",
    "switching_loss_state"
  ],
  "objective_component_fields": [
    "delay",
    "spillback_blocking_time",
    "switching_lost_time",
    "unfinished_vehicle_penalty"
  ]
}
```

**Copy/adapt for Phase 7:** keep `status`, `generated_by`, `requirements_covered`, `schema_version`, and explicit field lists. Use `requirements_covered: ["THRY-01", "THRY-02", "THRY-03", "THRY-04"]`.

**Regime status and proxy caution pattern** (`phase6_state_objective_fixtures.json` lines 16-59):

```json
"regime_status": {
  "slack": {
    "status": "supported_synthetic",
    "num_samples": 3,
    "rationale": "Low-occupancy queue perturbation; storage constraints intended to be nonbinding."
  },
  "storage_binding": {
    "status": "supported_synthetic",
    "num_samples": 3,
    "rationale": "Downstream edge C32C4 filled near storage limit while upstream edge C22C3 remains queued."
  },
  "supply_binding_proxy": {
    "status": "proxy",
    "num_samples": 3,
    "rationale": "Proxy only: current sample-to-scenario conversion has no explicit per-movement supply constraint field; encoded as high downstream occupancy."
  }
},
...
"legacy_proxy_note": "Old v1.0 proxy regime labels are historical/insufficient for v1.1 binding-regime superiority evidence without validated finite_storage_state and objective_components."
```

**Copy/adapt for Phase 7:** include `examples` with `slack_recovery` and `storage_binding_two_phase_separation`. If any proxy examples are mentioned, label them explicitly as insufficient/non-final and not part of THRY-02/03 proof.

**Static/no-closed-loop scope pattern** (`block3_static_kill_gate.json` lines 1-15, 116-156):

```json
{
  "experiment": "block3_static_pressure_failure_kill_gate",
  "status": "PASSED",
  "scope": "static_sample_relative_only_no_closed_loop_claims",
  "input_states": [
    "/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/block3_regime_states.json"
  ],
```

```json
"regime_metrics": [
  {
    "regime": "corridor_bottleneck_proxy",
    "num_examples": 200,
    "num_aligned_examples": 200,
    "sample_target_met": true,
    "claim_scope": "static_sample_relative",
    "dual_library": "dual_sensitivity",
    "pressure_library": "pressure_backpressure",
    "dual_vs_pressure_disagreement_rate": 0.0,
    "dual_win_rate": 0.0,
    "pressure_win_rate": 0.0,
    "tie_rate": 1.0,
    "dual_mean_oracle_regret": 0.0,
    "pressure_mean_oracle_regret": 0.0
  }
]
```

**Copy/adapt for Phase 7:** use `scope: "theory_static_one_step_only_no_closed_loop_claims"`. Include per-example metrics such as `pressure_action`, `finite_storage_action`, `actions_separate`, `objective_margin`, `strict_objective_improvement`, and `claim_scope: "structural_one_step_binding_separation"`.

## Shared Patterns

### 1. CLI / JSON writer pattern

**Sources:** `scripts/run_dual_sanity.py` lines 328-364; `scripts/generate_static_regime_states.py` lines 463-499.

**Apply to:** `scripts/check_theory_separation.py`

Required conventions:

- `main() -> None` and `if __name__ == "__main__"`.
- `argparse.ArgumentParser()` with default `--out experiments/dual_sensitivity/phase7_theory_separation.json`.
- `Path(args.out).parent.mkdir(parents=True, exist_ok=True)`.
- `Path(args.out).write_text(json.dumps(payload, indent=2), encoding="utf-8")`.
- Print compact JSON status. Either indented like `run_dual_sanity.py` or compact separators like `generate_static_regime_states.py` is acceptable; prefer compact for gate output.
- Raise `SystemExit(1)` only when payload status is not `PASSED` or validation fails.

### 2. Phase 6 finite-storage schema pattern

**Source:** `scripts/finite_storage_schema.py` lines 9-23, 82-167, 170-216, 226-277.

**Apply to:** checker, JSON artifact, tests.

Required fields:

```python
FINITE_STORAGE_STATE_FIELDS = {
    "downstream_storage",
    "residual_receiving_capacity",
    "spillback_blocking",
    "switching_loss_state",
    "service_urgency",
    "incident_capacity_drop",
}
OBJECTIVE_COMPONENT_FIELDS = {
    "delay",
    "unfinished_vehicle_penalty",
    "spillback_blocking_time",
    "switching_lost_time",
}
SCHEMA_VERSION = "phase6_explicit_state_v1"
```

Do not create another schema. Use:

```python
validate_state_objective_sample(sample, path=out_path, sample_idx=idx)
validate_finite_storage_state(state)
validate_objective_components(components)
```

### 3. Claim audit pattern

**Sources:** `scripts/claim_policy.py` lines 12-39, 42-99; `scripts/audit_claim_discipline.py` lines 39-47, 124-196, 199-212.

**Apply to:** `refine-logs/THEORY_AND_SEPARATION.md`, `phase7_theory_separation.json`, tests/verification.

Allowed claim boundary from `claim_policy.py`:

```python
PERMITTED_CLAIM = (
    "recover_or_tie_max_pressure_when_constraints_slack; "
    "improvement_claims_only_for_explicit_binding_finite_storage_spillback_switching_service_incident_regimes"
)
```

Forbidden phrases to avoid as unbounded claims:

```python
FORBIDDEN_CLAIM_PATTERNS = [
    "dual universally beats pressure",
    "proves superiority",
    "deployable superiority",
    "static evidence proves closed-loop",
    "universal dominance",
    "universally dominates pressure",
]
```

Verification command pattern:

```bash
python3 scripts/audit_claim_discipline.py --paths refine-logs/THEORY_AND_SEPARATION.md experiments/dual_sensitivity/phase7_theory_separation.json --allow-missing-paths
```

### 4. Test structure pattern

**Sources:** `tests/test_finite_storage_schema.py` and `tests/test_claim_discipline.py`.

**Apply to:** `tests/test_theory_separation.py`

Recommended tests:

1. `test_slack_recovery_matches_pressure_or_tie` — slack example finite-storage action equals pressure action or tie set contains pressure action.
2. `test_binding_example_separates_actions_with_explicit_state` — storage-binding example has `pressure_action != finite_storage_action` and validates with `validate_state_objective_sample`.
3. `test_binding_example_strictly_improves_predeclared_objective` — `objective_margin > 0` and `strict_objective_improvement is True`.
4. `test_phase7_checker_cli_writes_parseable_artifact` — subprocess with `tmp_path`, `status == PASSED`, requirements covered.
5. `test_memo_requirement_markers_and_claim_safe_language` — memo contains `THRY-01` through `THRY-04` and does not include unbounded forbidden phrases.
6. `test_guarantee_candidate_is_constrained_lp_oracle_regret` — THRY-04 is finite-sample/oracle-relative, not closed-loop or deployment claim.

### 5. JSON artifact field pattern for Phase 7

**Apply to:** `experiments/dual_sensitivity/phase7_theory_separation.json`

Recommended top-level shape:

```json
{
  "experiment": "phase7_theory_separation",
  "status": "PASSED",
  "scope": "theory_static_one_step_only_no_closed_loop_claims",
  "generated_by": "scripts/check_theory_separation.py",
  "requirements_covered": ["THRY-01", "THRY-02", "THRY-03", "THRY-04"],
  "schema_version": "phase6_explicit_state_v1",
  "one_step_objective_definition": {
    "predeclared_before_action_comparison": true,
    "components": ["delay", "unfinished_vehicle_penalty", "spillback_blocking_time", "switching_lost_time"],
    "weights": {"delay": 1.0, "unfinished_vehicle_penalty": 1.0, "spillback_blocking_time": 1.0, "switching_lost_time": 1.0}
  },
  "criteria": {
    "slack_recovers_or_ties_pressure": true,
    "binding_example_separates_actions": true,
    "binding_example_has_strict_objective_improvement": true,
    "uses_explicit_finite_storage_state": true
  },
  "examples": []
}
```

For each example include:

- `name`, `regime`, `claim_scope`
- `links`, `phases` or `actions`, `movements`
- `queues`, `capacities`
- `finite_storage_state`, `objective_components`
- `pressure_scores`, `finite_storage_scores`
- `pressure_action`, `finite_storage_action`
- `action_objective_components`
- `action_objective_totals`
- `objective_margin`, `strict_objective_improvement`
- `validation_notes`

## Patterns Not to Reuse for Phase 7

### Do not reuse live controller / agent patterns

**Do not copy from:**

- `pi_light_code/agent/*`
- `pi_light_code/env/*`
- `pi_light_code/00_run_tiny_light.py`, `01_run_baseline.py`, `02_run_MCTS.py`, `03_run_viper.py`

**Reason:** Phase 7 is theory and static artifact scaffolding only. Controller wiring belongs to Phase 8. Avoid `pick_action`, `TSCEnv`, CityFlow engine loops, PI-Light DSL execution, MCTS synthesis, replay buffers, and learned agents.

### Do not reuse closed-loop SUMO execution patterns

**Do not copy for Phase 7:** live TraCI stepping, SUMO route generation, paired-seed long-horizon experiment loops, travel-time/throughput claims.

**Permitted only as static-pattern references:** JSON CLI/output discipline from `run_static_kill_gate.py`; schema generation and static samples from `generate_static_regime_states.py`.

### Do not reuse proxy-only evidence as final separation evidence

**Sources showing the boundary:**

- `generate_static_regime_states.py` lines 308-373 marks `supply_binding_proxy` and `corridor_bottleneck_proxy` as proxy-only.
- `phase6_state_objective_fixtures.json` lines 27-35 and 42-46 label supply/corridor/demand cases as proxy.

**Phase 7 rule:** THRY-02/THRY-03 must use explicit `finite_storage_state` and objective components, preferably storage/spillback or incident capacity drop. Proxy-only labels can be mentioned as historical/insufficient, not proof.

### Do not reinterpret Phase 3 pressure-equivalent evidence

**Source:** `block3_static_kill_gate.json` lines 116-156 shows pressure-equivalent/tie metrics in static sample-relative evidence.

**Phase 7 rule:** v1.0/Phase 3 artifacts are quarantine/historical equivalence evidence. Do not claim they support Phase 7 superiority. The new separation must be a mathematical/static one-step example with explicit fields.

## Risks and Verification Hooks

| Risk | Pattern-based mitigation | Verification hook |
|---|---|---|
| Sign convention inversion (`lambda_down - lambda_up`) | Copy `lambda_up - lambda_down` from `run_dual_sanity.py` and theory memos. | Unit test asserts pressure score for toy actions equals `queue_up - queue_down`; memo states sign convention. |
| Action separation without objective improvement | JSON must predeclare objective weights/components before action totals. | `test_binding_example_strictly_improves_predeclared_objective`; assert `objective_margin > 0`. |
| Proxy-only binding evidence leaks into theorem | Use Phase 6 schema validators and mark proxy regimes insufficient. | `validate_state_objective_sample` on every Phase 7 example; JSON `claim_scope` excludes proxy-only examples. |
| Unsupported claim language | Copy bounded claim policy; avoid forbidden phrases unnegated. | `python3 scripts/audit_claim_discipline.py --paths refine-logs/THEORY_AND_SEPARATION.md experiments/dual_sensitivity/phase7_theory_separation.json --allow-missing-paths`. |
| Controller / closed-loop scope creep | Keep all code in `scripts/check_theory_separation.py`; no `pi_light_code/`, no TraCI stepping. | Test/import scan or code review: no imports from `traci`, `sumolib`, `pi_light_code`, `cityflow`, `torch`. |
| Non-reproducible artifact | Checker generates JSON deterministically from hard-coded example or stable input; no random seed needed. | CLI subprocess writes tmp artifact; compare required keys/status and deterministic actions. |
| Overstated THRY-04 guarantee | Use constrained LP oracle regret as finite-sample/oracle-relative candidate only. | Test memo contains “constrained LP oracle regret” and excludes closed-loop/deployment guarantees. |

## Recommended Verification Commands

```bash
python3 scripts/check_theory_separation.py --out experiments/dual_sensitivity/phase7_theory_separation.json
python3 -m pytest tests/test_theory_separation.py -q
python3 -m pytest tests/test_finite_storage_schema.py tests/test_claim_discipline.py tests/test_theory_separation.py -q
python3 scripts/audit_claim_discipline.py --paths refine-logs/THEORY_AND_SEPARATION.md experiments/dual_sensitivity/phase7_theory_separation.json --allow-missing-paths
```

All commands are CPU/local-artifact oriented and should not require SUMO, GPU, CityFlow, or PI-Light controller execution.

## No Analog Found

None. All proposed Phase 7 files have strong local analogs.

## Metadata

**Analog search scope:** `refine-logs/`, `scripts/`, `tests/`, `experiments/dual_sensitivity/`, project `CLAUDE.md`, Phase 7 context/research.  
**Files scanned/read:** 17 source/planning/artifact files.  
**Project skills:** `.claude/skills/` and `.agents/skills/` were absent in the project root check.  
**Pattern extraction date:** 2026-05-24
