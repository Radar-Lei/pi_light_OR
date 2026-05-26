from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_phase11_paired_evidence as phase11  # noqa: E402
from run_closed_loop_sumo import CONTROLLER_REGISTRY, choose_controller_action  # noqa: E402
from run_v14_gate_c_paired_evidence import build_gate_payload  # noqa: E402
from run_v14_locked_gate_c import build_locked_spec, build_row_audit, load_protocol, write_locked_execution  # noqa: E402


SELECTED = "finite_storage_primal_dual_v1_4_score"
DEFAULT_PROPOSED = "finite_storage_primal_dual"


@pytest.fixture(autouse=True)
def restore_phase11_proposed_controller() -> None:
    phase11.set_proposed_controller(DEFAULT_PROPOSED)
    yield
    phase11.set_proposed_controller(DEFAULT_PROPOSED)


def valid_demand_provenance(multiplier: float = 1.0) -> dict[str, object]:
    return {
        "demand_multiplier": multiplier,
        "demand_scaling_method": phase11.DEMAND_SCALING_METHOD,
        "requires_actual_sumo_behavior_change": True,
        "metadata_only_valid": False,
        "base_demand_total": 100.0,
        "scaled_demand_total": 100.0 * multiplier,
        "generated_route_file": "dummy.rou.xml",
        "generated_sumocfg": "dummy.sumocfg",
        "base_sumocfg": "base.sumocfg",
    }


def completed_row(spec_row: dict[str, object], *, proposed_better: bool = True) -> dict[str, object]:
    controller = str(spec_row["controller"])
    is_selected = controller == SELECTED
    good = 5.0 if is_selected and proposed_better else 10.0
    row = {
        **spec_row,
        "scenario_status": "completed",
        "feasibility_status": "run",
        "stress_category": "synthetic_binding",
        "stress_mechanism": "synthetic_phase17_test",
        "finite_storage_state": {},
        "objective_components": {},
        "penalized_avg_travel_time": good,
        "total_delay": good,
        "spillback_count": good,
        "blocking_count": good,
        "unfinished_vehicle_count": good,
        "switching_count": good,
        "demand_multiplier_provenance": valid_demand_provenance(float(spec_row["demand_multiplier"])),
    }
    if is_selected:
        row["action_decomposition"] = {
            "controller": SELECTED,
            "decision_scope": "last_action_decision_per_tls",
            "last_decision_by_tls": {"tls0": {"selected_action": 0, "component_totals": {"total": 1.0}}},
        }
    return row


def synthetic_spec() -> list[dict[str, object]]:
    phase11.set_proposed_controller(SELECTED)
    return phase11.build_phase11_spec(
        profile="main",
        controllers=[SELECTED, *phase11.REQUIRED_GATE_C_COMPARATORS],
        seeds=[101, 102],
        steps=3600,
        warmup=900,
        demand_multipliers=[0.8, 1.0, 1.2],
    )


def synthetic_execution_payload(rows: list[dict[str, object]], spec: list[dict[str, object]], *, status: str = "PASSED") -> dict[str, object]:
    return {
        "experiment": "v1_4_locked_gate_c_execution",
        "status": status,
        "profile": "main",
        "steps": 3600,
        "warmup": 900,
        "dry_run": False,
        "all_rows_executed": len(rows) == len(spec),
        "actual_row_count": len(rows),
        "expected_row_count": len(spec),
        "scenario_results": rows,
        "required_comparators": list(phase11.REQUIRED_GATE_C_COMPARATORS),
        "selected_controller_id": SELECTED,
        "locked_protocol_status": "LOCKED",
        "locked_protocol_fingerprint": "synthetic",
        "row_audit": build_row_audit(rows, spec),
        "demand_scaling_provenance": [valid_demand_provenance(0.8), valid_demand_provenance(1.0), valid_demand_provenance(1.2)],
    }


def test_v14_selected_controller_is_registered_and_auditable() -> None:
    assert SELECTED in CONTROLLER_REGISTRY
    action = choose_controller_action(
        SELECTED,
        "tls0",
        0,
        10,
        10,
        {"tls0": ["Gr", "rG"]},
        {"tls0": [("a", "b"), ("c", "d")]},
        {"a": 5.0, "b": 1.0, "c": 1.0, "d": 0.0},
        {"a": 10.0, "b": 10.0, "c": 10.0, "d": 10.0},
    )
    assert action in {0, 1}


def test_locked_spec_consumes_phase16_protocol_and_preserves_comparators() -> None:
    protocol = load_protocol(ROOT / "experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json")
    spec = build_locked_spec(protocol)
    controllers = {row["controller"] for row in spec}
    assert protocol["selected_controller_id"] in controllers
    assert set(phase11.REQUIRED_GATE_C_COMPARATORS) <= controllers
    assert {row["scenario_tag"] for row in spec} == set(protocol["binding_scenarios"])
    assert len(spec) == len(protocol["binding_scenarios"]) * len(protocol["demand_multipliers"]) * len(protocol["seeds"]) * 4


def test_dry_run_locked_execution_writes_fail_closed_audit(tmp_path: Path) -> None:
    out = tmp_path / "v14_execution.json"
    payload = write_locked_execution(
        protocol_path=ROOT / "experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json",
        out_path=out,
        route_json=ROOT / "experiments/dual_sensitivity/block3_static_kill_gate.json",
        scaled_input_dir=tmp_path / "scaled",
        dry_run=True,
    )
    assert out.exists()
    assert payload["experiment"] == "v1_4_locked_gate_c_execution"
    assert payload["selected_controller_id"] == SELECTED
    assert set(phase11.REQUIRED_GATE_C_COMPARATORS) <= set(payload["required_comparators"])
    assert payload["row_audit"]["expected_row_count"] == 1440
    assert payload["row_audit"]["completed_row_count"] == 0
    assert payload["row_audit"]["missing_row_count"] == 1440
    assert payload["claim_ready"] is False


def test_row_audit_reports_missing_duplicate_bad_provenance_schema_and_unpaired() -> None:
    spec = synthetic_spec()
    rows = [completed_row(row) for row in spec]
    rows = rows[:-1]
    duplicate = dict(rows[0])
    duplicate["total_delay"] = 12345.0
    rows.append(duplicate)
    rows[1]["demand_multiplier_provenance"] = {"metadata_only_valid": True}
    selected_idx = next(idx for idx, row in enumerate(rows) if row["controller"] == SELECTED and idx != 0)
    rows[selected_idx].pop("action_decomposition", None)
    audit = build_row_audit(rows, spec)
    assert audit["missing_row_count"] >= 1
    assert audit["duplicate_row_count"] == 1
    assert audit["bad_provenance_row_count"] >= 1
    assert audit["schema_invalid_row_count"] >= 1
    assert audit["unpaired_group_count"] >= 1


def test_strict_v14_gate_emits_passed_failed_or_inconclusive() -> None:
    spec = synthetic_spec()
    rows = [completed_row(row) for row in spec]
    passed = build_gate_payload(synthetic_execution_payload(rows, spec), Path("synthetic.json"))
    assert passed["status"] == "PASSED"

    non_passed_source = build_gate_payload(synthetic_execution_payload(rows, spec, status="FAILED"), Path("synthetic.json"))
    assert non_passed_source["status"] == "INCONCLUSIVE"

    missing_metric_rows = [dict(row) for row in rows]
    missing_metric_rows[0].pop("total_delay")
    failed = build_gate_payload(synthetic_execution_payload(missing_metric_rows, spec), Path("synthetic.json"))
    assert failed["status"] == "FAILED"

    missing_action_rows = [dict(row) for row in rows]
    selected_idx = next(idx for idx, row in enumerate(missing_action_rows) if row["controller"] == SELECTED)
    missing_action_rows[selected_idx].pop("action_decomposition")
    failed_action = build_gate_payload(synthetic_execution_payload(missing_action_rows, spec), Path("synthetic.json"))
    assert failed_action["status"] == "FAILED"
    assert {passed["status"], non_passed_source["status"], failed["status"], failed_action["status"]} <= {"PASSED", "FAILED", "INCONCLUSIVE"}


def test_gate_artifact_json_round_trip(tmp_path: Path) -> None:
    spec = synthetic_spec()
    rows = [completed_row(row) for row in spec]
    payload = build_gate_payload(synthetic_execution_payload(rows, spec), Path("synthetic.json"))
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["experiment"] == "v1_4_gate_c_paired_evidence"
    assert loaded["claim_ready"] is False
