#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
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
    build_phase11_spec,
    evaluate_gate_c,
    evaluate_gate_c_primary_metric_rule,
    paired_metric_summary,
    validate_payload_scope,
)


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
    spec = build_phase11_spec(profile="main", seeds=[7], demand_multipliers=[0.8, 1.0, 1.2])
    multipliers = {row["demand_multiplier"] for row in spec}
    assert multipliers == {0.8, 1.0, 1.2}
    for row in spec:
        contract = row["demand_multiplier_contract"]
        assert set(DEMAND_MULTIPLIER_PROVENANCE_KEYS) <= set(contract)
        assert contract["requires_actual_sumo_behavior_change"] is True
        assert contract["metadata_only_valid"] is False
        assert contract["demand_scaling_method"] in {"route_demand_scaling", "insertion_intensity_scaling"}


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
            "demand_scaling_method": "route_demand_scaling",
            "requires_actual_sumo_behavior_change": True,
            "metadata_only_valid": False,
            "base_demand_total": 100.0,
            "scaled_demand_total": 100.0 * demand_multiplier,
            "demand_source": "synthetic_scaled_route",
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


def main() -> None:
    test_phase11_constants_lock_binding_scope_and_comparators()
    test_main_spec_defaults_are_journal_grade_and_paired()
    test_pilot_spec_is_pipeline_validation_not_gate_c_evidence()
    test_demand_multiplier_contract_requires_actual_sumo_behavior_change()
    test_primary_metric_constants_cover_all_d_11_04_metrics()
    test_paired_metric_summary_reports_direction_ci_effect_and_family_metadata()
    test_gate_c_rule_pass_fail_inconclusive_and_missing_metric_cases()
    test_unpaired_and_switching_metric_fail_closed()
    test_gate_c_core_evaluator_passes_and_classifies_slack_context()
    test_gate_c_core_evaluator_fails_closed_on_missing_inputs()
    test_gate_c_rejects_pilot_and_metadata_only_demand_artifacts()
    test_validate_payload_scope_rejects_forbidden_claim_language()
    print("phase11 paired evidence tests ok")


if __name__ == "__main__":
    main()
