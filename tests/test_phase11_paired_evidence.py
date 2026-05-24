#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_phase11_paired_evidence import (  # noqa: E402
    BINDING_EVIDENCE_SCENARIOS,
    DEMAND_MULTIPLIER_PROVENANCE_KEYS,
    PROPOSED_CONTROLLER,
    REQUIRED_GATE_C_COMPARATORS,
    SLACK_CONTEXT_SCENARIOS,
    build_phase11_spec,
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


def main() -> None:
    test_phase11_constants_lock_binding_scope_and_comparators()
    test_main_spec_defaults_are_journal_grade_and_paired()
    test_pilot_spec_is_pipeline_validation_not_gate_c_evidence()
    test_demand_multiplier_contract_requires_actual_sumo_behavior_change()
    print("phase11 paired evidence tests ok")


if __name__ == "__main__":
    main()
