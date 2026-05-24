#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_phase11_paired_evidence import (  # noqa: E402
    BINDING_EVIDENCE_SCENARIOS,
    DEMAND_MULTIPLIER_PROVENANCE_KEYS,
    GATE_C_CONDITIONAL_PRIMARY_METRICS,
    GATE_C_PRIMARY_METRICS,
    GATE_C_STATISTICAL_FAMILY,
    PROPOSED_CONTROLLER,
    REQUIRED_GATE_C_COMPARATORS,
    SLACK_CONTEXT_SCENARIOS,
    build_payload,
    build_phase11_spec,
    generate_scaled_route_and_sumocfg,
    materialize_demand_inputs,
    evaluate_gate_c,
    evaluate_gate_c_primary_metric_rule,
    paired_metric_summary,
    validate_payload_scope,
)
from run_gate_c_paired_evidence import (  # noqa: E402
    build_gate_payload,
    load_input_payload,
    write_gate_artifact,
)


def test_main_spec_enforces_long_horizon_seed_and_multiplier_contracts() -> None:
    try:
        build_phase11_spec(profile="main", seeds=[1], demand_multipliers=[0.8, 1.0, 1.2])
    except ValueError as exc:
        assert "two paired seeds" in str(exc)
    else:
        raise AssertionError("one-seed main profile should fail validation")

    try:
        build_phase11_spec(profile="main", seeds=[1, 2], demand_multipliers=[1.0])
    except ValueError as exc:
        assert "0.8, 1.0, and 1.2" in str(exc)
    else:
        raise AssertionError("single-multiplier main profile should fail validation")

    try:
        build_phase11_spec(profile="main", seeds=[1, 2], steps=3599, warmup=900, demand_multipliers=[0.8, 1.0, 1.2])
    except ValueError as exc:
        assert "3600" in str(exc)
    else:
        raise AssertionError("sub-3600 main profile should fail validation")

    spec = build_phase11_spec(profile="main", seeds=[1, 2], steps=3600, warmup=900, demand_multipliers=[0.8, 1.0, 1.2])
    assert spec
    assert all(row["profile"] == "main" for row in spec)



def test_phase11_constants_lock_binding_scope_and_comparators() -> None:
    assert PROPOSED_CONTROLLER == "finite_storage_primal_dual"
    assert BINDING_EVIDENCE_SCENARIOS == (
        "arterial_downstream_blockage",
        "arterial_spillback_stress",
        "arterial_incident_capacity_drop",
        "arterial_oversaturation",
        "arterial_turning_shock",
        "arterial_switching_loss_sensitive",
    )
    assert REQUIRED_GATE_C_COMPARATORS == (
        "max_pressure",
        "capacity_aware_pressure",
        "finite_storage_double_pressure",
    )
    assert {"single_sanity", "arterial_main", "grid_scalability"} <= set(SLACK_CONTEXT_SCENARIOS)


def test_main_spec_defaults_are_journal_grade_and_paired() -> None:
    spec = build_phase11_spec(profile="main")
    assert len({row["seed"] for row in spec}) == 20
    assert {row["demand_multiplier"] for row in spec} == {0.8, 1.0, 1.2}
    assert spec
    assert {row["scenario_tag"] for row in spec} == set(BINDING_EVIDENCE_SCENARIOS)
    assert all(row["steps"] >= 3600 for row in spec)
    assert all(row["warmup"] >= 900 for row in spec)
    assert all(row["profile"] == "main" for row in spec)
    assert all(row["evidence_role"] == "gate_c_binding_dominance_candidate" for row in spec)

    required_controllers = {PROPOSED_CONTROLLER, *REQUIRED_GATE_C_COMPARATORS}
    for scenario in BINDING_EVIDENCE_SCENARIOS:
        for multiplier in {row["demand_multiplier"] for row in spec if row["scenario_tag"] == scenario}:
            by_controller = {
                row["controller"]: {row["seed"] for row in spec if row["scenario_tag"] == scenario and row["demand_multiplier"] == multiplier and row["controller"] == row["controller"]}
                for row in spec
                if row["scenario_tag"] == scenario and row["demand_multiplier"] == multiplier
            }
            assert required_controllers <= set(by_controller)
            seed_sets = [by_controller[controller] for controller in required_controllers]
            assert all(seed_set == seed_sets[0] for seed_set in seed_sets)


def test_pilot_spec_is_pipeline_validation_not_gate_c_evidence() -> None:
    spec = build_phase11_spec(profile="pilot", seeds=[1, 2], steps=300, warmup=60, demand_multipliers=[1.0])
    assert spec
    assert all(row["profile"] == "pilot" for row in spec)
    assert all(row["evidence_role"] == "pipeline_validation_not_gate_c_dominance" for row in spec)
    assert all(row["gate_c_eligible"] is False for row in spec)
    assert all(row["steps"] == 300 and row["warmup"] == 60 for row in spec)


def test_demand_multiplier_contract_requires_actual_sumo_behavior_change() -> None:
    spec = build_phase11_spec(profile="main", seeds=[7, 8], demand_multipliers=[0.8, 1.0, 1.2])
    multipliers = {row["demand_multiplier"] for row in spec}
    assert multipliers == {0.8, 1.0, 1.2}
    for row in spec:
        contract = row["demand_multiplier_contract"]
        assert set(DEMAND_MULTIPLIER_PROVENANCE_KEYS) <= set(contract)
        assert contract["requires_actual_sumo_behavior_change"] is True
        assert contract["metadata_only_valid"] is False
        assert contract["demand_scaling_method"] == "scaled_route_sumocfg_override"


_defused_tmp_error = None


def test_scaled_route_sumocfg_generation_changes_actual_demand_inputs() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        spec = build_phase11_spec(
            profile="main",
            seeds=[7, 8],
            controllers=[PROPOSED_CONTROLLER, *REQUIRED_GATE_C_COMPARATORS],
            demand_multipliers=[0.8, 1.0, 1.2],
        )
        enriched = materialize_demand_inputs(spec, Path(raw_tmp))
        by_multiplier = {}
        for row in enriched:
            by_multiplier.setdefault(row["demand_multiplier"], row["demand_multiplier_provenance"])
        assert set(by_multiplier) == {0.8, 1.0, 1.2}
        route_paths = {item["generated_route_file"] for item in by_multiplier.values()}
        cfg_paths = {item["generated_sumocfg"] for item in by_multiplier.values()}
        totals = {round(float(item["scaled_demand_total"]), 3) for item in by_multiplier.values()}
        assert len(route_paths) == 3
        assert len(cfg_paths) == 3
        assert len(totals) == 3
        for item in by_multiplier.values():
            assert Path(item["generated_route_file"]).exists()
            assert Path(item["generated_sumocfg"]).exists()
            cfg_root = ET.parse(item["generated_sumocfg"]).getroot()
            route_value = cfg_root.find("./input/route-files").get("value")
            assert route_value == str(Path(item["generated_route_file"]).resolve())
        assert by_multiplier[0.8]["scaled_demand_total"] < by_multiplier[1.0]["scaled_demand_total"] < by_multiplier[1.2]["scaled_demand_total"]


def test_sumocfg_override_argument_is_exposed_in_run_experiment() -> None:
    import inspect
    from run_closed_loop_sumo import run_experiment

    signature = inspect.signature(run_experiment)
    assert "sumocfg_override" in signature.parameters
    assert signature.parameters["sumocfg_override"].default is None


def test_main_fail_closed_payload_records_missing_executions() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        spec = build_phase11_spec(
            profile="main",
            seeds=[7, 8],
            steps=3600,
            warmup=900,
            demand_multipliers=[0.8, 1.0, 1.2],
        )
        enriched = materialize_demand_inputs(spec, Path(raw_tmp))
        route_metadata = {"route_decision": "pressure-equivalent", "route_confidence": "MEDIUM", "route_json": "synthetic.json"}
        payload = build_payload(
            profile="main",
            route_metadata=route_metadata,
            spec=enriched,
            rows=[],
            dry_run=False,
            execution_mode="fail_closed_runtime_guard",
            missing_row_reasons=["runtime guard prevented requested rows from starting"],
        )
    assert payload["profile"] == "main"
    assert payload["status"] == "INCONCLUSIVE"
    assert payload["steps"] >= 3600
    assert payload["warmup"] >= 900
    assert {0.8, 1.0, 1.2} <= set(payload["demand_multipliers"])
    assert payload["actual_row_count"] == 0
    assert payload["missing_row_key_count"] == payload["expected_row_count"]
    assert payload["all_rows_executed"] is False
    assert payload["demand_scaling_provenance"]
    assert any("runtime guard" in reason for reason in payload["missing_row_reasons"])


def test_dry_run_payload_records_phase11_schema_and_rejects_evidence_completion() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        spec = build_phase11_spec(
            profile="pilot",
            seeds=[7, 8],
            steps=120,
            warmup=30,
            demand_multipliers=[1.0],
        )
        enriched = materialize_demand_inputs(spec, Path(raw_tmp))
        placeholders = []
        route_metadata = {"route_decision": "pressure-equivalent", "route_confidence": "MEDIUM", "route_json": "synthetic.json"}
        payload = build_payload(
            profile="pilot",
            route_metadata=route_metadata,
            spec=enriched,
            rows=placeholders,
            dry_run=True,
            execution_mode="dry_run_spec_only",
            missing_row_reasons=["dry-run requested; no SUMO rows executed"],
        )
    assert payload["experiment"] == "phase11_long_horizon_paired_seed_evidence"
    assert payload["status"] == "PILOT_ONLY"
    assert payload["profile"] == "pilot"
    assert payload["paired_statistics"] == []
    assert payload["gate_c"]["status"] == "INCONCLUSIVE"
    assert payload["metric_schema"]["penalized_avg_travel_time"] == "CLOP-04 metric"
    assert payload["objective_component_schema"]["row_field"] == "objective_components"
    assert payload["finite_storage_state_schema"]["row_field"] == "finite_storage_state"
    assert payload["demand_scaling_provenance"]
    assert payload["all_rows_executed"] is False


def finite_storage_state() -> dict[str, Any]:
    return {
        "downstream_storage": {"edge": 10.0},
        "residual_receiving_capacity": {"edge": 8.0},
        "spillback_blocking": {"edge": {"spillback": False, "blocking": False, "occupancy_ratio": 0.2}},
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 15.0},
        "service_urgency": {"edge": 0.1},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }


def objective_components() -> dict[str, float]:
    return {
        "delay": 1.0,
        "unfinished_vehicle_penalty": 0.0,
        "spillback_blocking_time": 0.0,
        "switching_lost_time": 0.0,
    }


def make_row(
    scenario: str,
    controller: str,
    seed: int,
    *,
    demand_multiplier: float = 1.0,
    offset: float = 0.0,
) -> dict[str, Any]:
    row = {
        "network": "arterial",
        "scenario_tag": scenario,
        "controller": controller,
        "seed": seed,
        "profile": "main",
        "steps": 3600,
        "warmup": 900,
        "demand_multiplier": demand_multiplier,
        "scenario_status": "completed",
        "feasibility_status": "run",
        "stress_category": "switching_loss_sensitive" if scenario == "arterial_switching_loss_sensitive" else "spillback",
        "stress_mechanism": "short_action_interval_switching_audit" if scenario == "arterial_switching_loss_sensitive" else "finite_storage_occupancy_stress",
        "finite_storage_state": finite_storage_state(),
        "objective_components": objective_components(),
        "demand_multiplier_provenance": {
            "demand_multiplier": demand_multiplier,
            "demand_scaling_method": "scaled_route_sumocfg_override",
            "requires_actual_sumo_behavior_change": True,
            "metadata_only_valid": False,
            "base_demand_total": 100.0,
            "scaled_demand_total": 100.0 * demand_multiplier,
            "demand_source": "synthetic_scaled_route",
            "generated_route_file": "synthetic_scaled_route.rou.xml",
            "generated_sumocfg": "synthetic_scaled_route.sumocfg",
            "base_sumocfg": "networks/arterial/arterial.sumocfg",
        },
        "penalized_avg_travel_time": 100.0 + offset,
        "total_delay": 200.0 + offset,
        "spillback_count": 10.0 + offset,
        "blocking_count": 5.0 + offset,
        "unfinished_vehicle_count": 3.0 + offset,
        "switching_count": 4.0 + offset,
    }
    if controller == PROPOSED_CONTROLLER:
        row["action_decomposition"] = {
            "controller": PROPOSED_CONTROLLER,
            "decision_scope": "last_action_decision_per_tls",
            "last_decision_by_tls": {"J0": {"selected_action": 0, "pressure_action": 0}},
        }
    return row


def synthetic_rows(
    delta: float = 5.0,
    *,
    scenario: str = "arterial_spillback_stress",
    comparators: list[str] | None = None,
) -> list[dict[str, Any]]:
    rows = []
    if comparators is None:
        comparators = ["max_pressure"]
    for seed in [1, 2, 3, 4]:
        rows.append(make_row(scenario, PROPOSED_CONTROLLER, seed, offset=0.0))
        for comparator in comparators:
            rows.append(make_row(scenario, comparator, seed, offset=delta))
    return rows


def full_gate_rows(delta: float = 5.0) -> list[dict[str, Any]]:
    rows = []
    for scenario in BINDING_EVIDENCE_SCENARIOS:
        rows.extend(synthetic_rows(delta=delta, scenario=scenario, comparators=list(REQUIRED_GATE_C_COMPARATORS)))
    rows.append(make_row("single_sanity", PROPOSED_CONTROLLER, 1, offset=0.0))
    rows.append(make_row("single_sanity", "max_pressure", 1, offset=0.0))
    return rows


def test_primary_metric_constants_cover_all_d_11_04_metrics() -> None:
    assert GATE_C_PRIMARY_METRICS == (
        "penalized_avg_travel_time",
        "total_delay",
        "spillback_count",
        "blocking_count",
        "unfinished_vehicle_count",
    )
    assert GATE_C_CONDITIONAL_PRIMARY_METRICS["arterial_switching_loss_sensitive"] == ("switching_count",)
    assert GATE_C_STATISTICAL_FAMILY == "gate_c_primary_metrics_v1"


def test_paired_metric_summary_reports_direction_ci_effect_and_family_metadata() -> None:
    summary = paired_metric_summary(synthetic_rows(delta=5.0), "arterial_spillback_stress", 1.0, "max_pressure", "total_delay")
    assert summary["mean_paired_difference"] == 5.0
    assert summary["ci_low"] >= 0.0
    assert summary["ci_high"] >= summary["ci_low"]
    assert summary["n_seeds"] == 4
    assert summary["metric_direction"] == "lower_is_better"
    assert summary["difference_definition"] == "comparator_minus_proposed"
    assert summary["positive_means"] == "proposed_controller_better"
    assert summary["effect_size"] > 0.0
    assert summary["statistical_family"] == GATE_C_STATISTICAL_FAMILY
    assert summary["paired_seed_ids"] == [1, 2, 3, 4]


def test_gate_c_rule_pass_fail_inconclusive_and_missing_metric_cases() -> None:
    passed = evaluate_gate_c_primary_metric_rule(synthetic_rows(delta=5.0), scenarios=["arterial_spillback_stress"], comparators=["max_pressure"])
    assert passed["status"] == "PASSED"
    assert passed["family_metadata"]["method"] == "holm_bonferroni"
    assert {item["metric"] for item in passed["metric_results"]} == set(GATE_C_PRIMARY_METRICS)

    failed = evaluate_gate_c_primary_metric_rule(synthetic_rows(delta=-5.0), scenarios=["arterial_spillback_stress"], comparators=["max_pressure"])
    assert failed["status"] == "FAILED"
    assert any(item["classification"] == "bounded_harm" for item in failed["metric_results"])

    inconclusive = evaluate_gate_c_primary_metric_rule(synthetic_rows(delta=0.0), scenarios=["arterial_spillback_stress"], comparators=["max_pressure"])
    assert inconclusive["status"] == "INCONCLUSIVE"
    assert any(item["classification"] == "inconclusive" for item in inconclusive["metric_results"])

    missing_metric_rows = synthetic_rows(delta=5.0)
    missing_metric_rows[0].pop("total_delay")
    missing = evaluate_gate_c_primary_metric_rule(missing_metric_rows, scenarios=["arterial_spillback_stress"], comparators=["max_pressure"])
    assert missing["status"] == "FAILED"
    assert any("total_delay" in reason for reason in missing["reasons"])


def test_unpaired_and_switching_metric_fail_closed() -> None:
    unpaired = synthetic_rows(delta=5.0)
    unpaired = [row for row in unpaired if not (row["controller"] == "max_pressure" and row["seed"] == 4)]
    result = evaluate_gate_c_primary_metric_rule(unpaired, scenarios=["arterial_spillback_stress"], comparators=["max_pressure"])
    assert result["status"] == "FAILED"
    assert any("unpaired" in reason for reason in result["reasons"])

    switching_rows = synthetic_rows(delta=5.0, scenario="arterial_switching_loss_sensitive")
    for row in switching_rows:
        row.pop("switching_count")
    switching = evaluate_gate_c_primary_metric_rule(switching_rows, scenarios=["arterial_switching_loss_sensitive"], comparators=["max_pressure"])
    assert switching["status"] == "FAILED"
    assert any("switching_count" in reason for reason in switching["reasons"])


def test_gate_c_core_evaluator_passes_and_classifies_slack_context() -> None:
    result = evaluate_gate_c({"profile": "main", "steps": 3600, "warmup": 900, "scenario_results": full_gate_rows(delta=5.0)})
    assert result["status"] == "PASSED"
    assert result["binding_regime_dominance"]
    assert result["slack_regime_recovery_or_context"]
    assert not result["not_evidence"]


def test_gate_c_core_evaluator_fails_closed_on_missing_inputs() -> None:
    missing_scenario = [row for row in full_gate_rows(delta=5.0) if row["scenario_tag"] != "arterial_turning_shock"]
    result = evaluate_gate_c({"profile": "main", "steps": 3600, "warmup": 900, "scenario_results": missing_scenario})
    assert result["status"] == "FAILED"
    assert any("arterial_turning_shock" in reason for reason in result["reasons"])

    missing_comparator = [row for row in full_gate_rows(delta=5.0) if row["controller"] != "capacity_aware_pressure"]
    result = evaluate_gate_c({"profile": "main", "steps": 3600, "warmup": 900, "scenario_results": missing_comparator})
    assert result["status"] == "FAILED"
    assert any("capacity_aware_pressure" in reason for reason in result["reasons"])

    missing_metadata = copy.deepcopy(full_gate_rows(delta=5.0))
    missing_metadata[0].pop("stress_mechanism")
    result = evaluate_gate_c({"profile": "main", "steps": 3600, "warmup": 900, "scenario_results": missing_metadata})
    assert result["status"] == "FAILED"
    assert any("stress" in reason for reason in result["reasons"])

    missing_state = copy.deepcopy(full_gate_rows(delta=5.0))
    missing_state[0].pop("finite_storage_state")
    result = evaluate_gate_c({"profile": "main", "steps": 3600, "warmup": 900, "scenario_results": missing_state})
    assert result["status"] == "FAILED"
    assert any("finite_storage_state" in reason for reason in result["reasons"])

    missing_objective = copy.deepcopy(full_gate_rows(delta=5.0))
    missing_objective[0].pop("objective_components")
    result = evaluate_gate_c({"profile": "main", "steps": 3600, "warmup": 900, "scenario_results": missing_objective})
    assert result["status"] == "FAILED"
    assert any("objective_components" in reason for reason in result["reasons"])

    missing_action = copy.deepcopy(full_gate_rows(delta=5.0))
    for row in missing_action:
        if row["controller"] == PROPOSED_CONTROLLER:
            row.pop("action_decomposition")
            break
    result = evaluate_gate_c({"profile": "main", "steps": 3600, "warmup": 900, "scenario_results": missing_action})
    assert result["status"] == "FAILED"
    assert any("action_decomposition" in reason for reason in result["reasons"])


def test_gate_c_rejects_pilot_and_metadata_only_demand_artifacts() -> None:
    pilot = evaluate_gate_c({"profile": "pilot", "steps": 300, "warmup": 60, "scenario_results": full_gate_rows(delta=5.0)})
    assert pilot["status"] == "INCONCLUSIVE"
    assert any("main profile" in reason for reason in pilot["reasons"])

    metadata_only = copy.deepcopy(full_gate_rows(delta=5.0))
    metadata_only[0]["demand_multiplier_provenance"]["metadata_only_valid"] = True
    result = evaluate_gate_c({"profile": "main", "steps": 3600, "warmup": 900, "scenario_results": metadata_only})
    assert result["status"] == "FAILED"
    assert any("demand multiplier" in reason for reason in result["reasons"])


def test_validate_payload_scope_rejects_forbidden_claim_language() -> None:
    validate_payload_scope({"claim": "closed-loop paired-seed evidence in predeclared binding stress regimes"})
    for phrase in [
        "universal dominance",
        "deployment readiness",
        "final manuscript claim",
        "superior to max-pressure outside binding regimes",
        "Phase 10 proves superiority",
    ]:
        try:
            validate_payload_scope({"claim": phrase})
        except ValueError as exc:
            assert phrase.lower().split()[0] in str(exc).lower() or "forbidden" in str(exc).lower()
        else:
            raise AssertionError(f"forbidden claim language should fail: {phrase}")


def test_standalone_gate_checker_writes_inconclusive_output_for_missing_main_rows() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        input_path = Path(raw_tmp) / "phase11_input.json"
        out_path = Path(raw_tmp) / "phase11_gate.json"
        payload = {
            "experiment": "phase11_long_horizon_paired_seed_evidence",
            "status": "INCONCLUSIVE",
            "profile": "main",
            "steps": 3600,
            "warmup": 900,
            "dry_run": False,
            "actual_row_count": 0,
            "expected_row_count": 12,
            "all_rows_executed": False,
            "demand_scaling_method": "scaled_route_sumocfg_override",
            "demand_multipliers": [0.8, 1.0, 1.2],
            "demand_scaling_provenance": [
                {
                    "demand_multiplier": 1.0,
                    "demand_scaling_method": "scaled_route_sumocfg_override",
                    "requires_actual_sumo_behavior_change": True,
                    "metadata_only_valid": False,
                    "base_demand_total": 100.0,
                    "scaled_demand_total": 100.0,
                    "generated_route_file": "synthetic.rou.xml",
                    "generated_sumocfg": "synthetic.sumocfg",
                    "base_sumocfg": "base.sumocfg",
                }
            ],
            "scenario_results": [],
            "caveats": ["No dominance claim."],
        }
        input_path.write_text(json.dumps(payload), encoding="utf-8")
        result = write_gate_artifact(input_path, out_path)
        loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert result["status"] == "INCONCLUSIVE"
    assert loaded["experiment"] == "phase11_gate_c_paired_evidence"
    assert loaded["requirements_covered"] == ["GATE-03", "EXP-05"]
    assert loaded["gate_c_primary_metrics"] == list(GATE_C_PRIMARY_METRICS)
    assert loaded["gate_c_primary_metrics_v1"]["statistical_family"] == GATE_C_STATISTICAL_FAMILY
    assert loaded["binding_regime_dominance"] == []
    assert loaded["profile_eligibility"]["eligible"] is False
    assert loaded["demand_multiplier_provenance_summary"]["valid_actual_behavior"] is True
    assert any("no executed raw scenario rows" in reason for reason in loaded["reasons"])


def test_gate_checker_rejects_pilot_artifacts_and_forbidden_language() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        input_path = Path(raw_tmp) / "pilot.json"
        out_path = Path(raw_tmp) / "gate.json"
        pilot_payload = {
            "experiment": "phase11_long_horizon_paired_seed_evidence",
            "status": "PILOT_ONLY",
            "profile": "pilot",
            "steps": 120,
            "warmup": 30,
            "dry_run": True,
            "actual_row_count": 0,
            "expected_row_count": 0,
            "all_rows_executed": False,
            "scenario_results": full_gate_rows(delta=5.0),
            "demand_scaling_provenance": [],
        }
        input_path.write_text(json.dumps(pilot_payload), encoding="utf-8")
        result = write_gate_artifact(input_path, out_path)
    assert result["status"] == "INCONCLUSIVE"
    assert result["profile_eligibility"]["eligible"] is False
    assert any("pilot-only" in reason for reason in result["profile_eligibility"]["reasons"])

    with tempfile.TemporaryDirectory() as raw_tmp:
        bad_path = Path(raw_tmp) / "bad.json"
        bad_path.write_text(json.dumps({"claim": "universal dominance"}), encoding="utf-8")
        try:
            load_input_payload(bad_path)
        except ValueError as exc:
            assert "forbidden" in str(exc).lower()
        else:
            raise AssertionError("forbidden claim language should fail during checker input loading")


def main() -> None:
    test_main_spec_enforces_long_horizon_seed_and_multiplier_contracts()
    test_phase11_constants_lock_binding_scope_and_comparators()
    test_main_spec_defaults_are_journal_grade_and_paired()
    test_pilot_spec_is_pipeline_validation_not_gate_c_evidence()
    test_demand_multiplier_contract_requires_actual_sumo_behavior_change()
    test_scaled_route_sumocfg_generation_changes_actual_demand_inputs()
    test_sumocfg_override_argument_is_exposed_in_run_experiment()
    test_dry_run_payload_records_phase11_schema_and_rejects_evidence_completion()
    test_main_fail_closed_payload_records_missing_executions()
    test_primary_metric_constants_cover_all_d_11_04_metrics()
    test_paired_metric_summary_reports_direction_ci_effect_and_family_metadata()
    test_gate_c_rule_pass_fail_inconclusive_and_missing_metric_cases()
    test_unpaired_and_switching_metric_fail_closed()
    test_gate_c_core_evaluator_passes_and_classifies_slack_context()
    test_gate_c_core_evaluator_fails_closed_on_missing_inputs()
    test_gate_c_rejects_pilot_and_metadata_only_demand_artifacts()
    test_validate_payload_scope_rejects_forbidden_claim_language()
    test_standalone_gate_checker_writes_inconclusive_output_for_missing_main_rows()
    test_gate_checker_rejects_pilot_artifacts_and_forbidden_language()
    print("phase11 paired evidence tests ok")


if __name__ == "__main__":
    main()
