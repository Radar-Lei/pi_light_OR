#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from finite_storage_schema import (  # noqa: E402
    FINITE_STORAGE_STATE_FIELDS,
    OBJECTIVE_COMPONENT_FIELDS,
    validate_finite_storage_state,
    validate_state_objective_sample,
)
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
from render_closed_loop_report import render_report, write_csv  # noqa: E402
from render_paper_artifacts import validate_inputs as validate_paper_inputs  # noqa: E402
from reproduce_blocks import audit_artifacts, build_block_registry  # noqa: E402
from run_closed_loop_suite import (  # noqa: E402
    REQUIRED_STRONG_BASELINES,
    STRESS_SCENARIO_CATEGORIES,
    aggregate_results,
    build_payload as build_suite_payload,
    build_suite_spec,
    completion_gates,
    gates_pass,
    grid_fixed_time_counterexample_check,
    optimized_fixed_time_metadata,
    stress_scenario_coverage,
    strong_baseline_coverage,
)


def test_controller_registry_smoke_names() -> None:
    expected = {
        "fixed_time",
        "actuated_local_pressure",
        "max_pressure",
        "capacity_aware_pressure",
        "cycle_pressure",
        "finite_storage_double_pressure",
        "local_pilight",
        "raw_neighbor_symbolic",
        "all_neighbor_symbolic",
        "random_permuted_dual",
        "finite_storage_primal_dual",
        "full_dual_symbolic",
    }
    assert expected <= set(CONTROLLER_REGISTRY)
    assert "finite_storage_primal_dual" not in NOT_FEASIBLE_CONTROLLERS
    assert "cycle_pressure" not in NOT_FEASIBLE_CONTROLLERS
    assert "finite_storage_double_pressure" not in NOT_FEASIBLE_CONTROLLERS
    assert "local_pilight" in NOT_FEASIBLE_CONTROLLERS
    assert "full_dual_symbolic" in NOT_FEASIBLE_CONTROLLERS


def two_phase_fixture(binding: bool = False) -> tuple[dict[str, list[str]], dict[str, list[tuple[str, str]]], dict[str, float], dict[str, float], dict[str, object]]:
    if binding:
        queues = {"up_a": 30.0, "down_a": 10.0, "up_b": 15.0, "down_b": 2.0}
        capacities = {"up_a": 50.0, "down_a": 10.0, "up_b": 50.0, "down_b": 10.0}
    else:
        queues = {"up_a": 20.0, "down_a": 5.0, "up_b": 14.0, "down_b": 4.0}
        capacities = {"up_a": 40.0, "down_a": 40.0, "up_b": 40.0, "down_b": 40.0}
    state = build_completed_finite_storage_state(queues, capacities, current_phase=0, time_since_switch=30.0)
    if binding:
        state["residual_receiving_capacity"]["down_a"] = 0.0
        state["spillback_blocking"]["down_a"] = {"spillback": True, "blocking": True, "occupancy_ratio": 1.0}
    return {"J0": ["Gr", "rG"]}, {"J0": [("up_a", "down_a"), ("up_b", "down_b")]}, queues, capacities, state


def test_finite_storage_decomposition_keys_and_total() -> None:
    _phase_states, movements, queues, capacities, state = two_phase_fixture(binding=False)
    components = finite_storage_movement_decomposition(movements["J0"][0], queues, capacities, state)
    assert set(components) == FINITE_STORAGE_DECOMPOSITION_FIELDS
    assert components["total"] == sum(components[field] for field in FINITE_STORAGE_DECOMPOSITION_FIELDS - {"total"})


def test_finite_storage_isolated_correction_terms_are_nonzero() -> None:
    _phase_states, movements, queues, capacities, state = two_phase_fixture(binding=False)
    movement = movements["J0"][0]

    storage_state = json.loads(json.dumps(state))
    storage_state["residual_receiving_capacity"]["down_a"] = 0.0
    assert finite_storage_movement_decomposition(movement, queues, capacities, storage_state)["downstream_storage"] < 0.0

    spillback_state = json.loads(json.dumps(state))
    spillback_state["spillback_blocking"]["down_a"] = {"spillback": True, "blocking": True, "occupancy_ratio": 1.0}
    assert finite_storage_movement_decomposition(movement, queues, capacities, spillback_state)["spillback"] < 0.0

    service_state = json.loads(json.dumps(state))
    service_state["service_urgency"]["up_a"] = 0.95
    assert finite_storage_movement_decomposition(movement, queues, capacities, service_state)["service"] > 0.0

    incident_state = json.loads(json.dumps(state))
    incident_state["incident_capacity_drop"] = {"active": True, "edge": "down_a", "factor": 0.35}
    assert finite_storage_movement_decomposition(movement, queues, capacities, incident_state)["incident"] < 0.0
    upstream_incident_state = json.loads(json.dumps(state))
    upstream_incident_state["incident_capacity_drop"] = {"active": True, "edge": "up_a", "factor": 0.35}
    assert finite_storage_movement_decomposition(movement, queues, capacities, upstream_incident_state)["incident"] < 0.0

    switching_state = json.loads(json.dumps(state))
    switching_state["switching_loss_state"] = {"current_phase": 0, "time_since_switch": 2.0}
    phase = finite_storage_phase_decomposition(1, ["Gr", "rG"], movements["J0"], queues, capacities, switching_state, current_phase=0)
    assert phase["component_totals"]["switching"] < 0.0


def test_finite_storage_slack_recovers_pressure_action() -> None:
    phase_states, movements, queues, capacities, state = two_phase_fixture(binding=False)
    audit = select_finite_storage_action_with_audit("J0", 0, phase_states, movements, queues, capacities, state)
    assert audit["pressure_action"] == 0
    assert audit["finite_storage_action"] == 0
    for phase_audit in audit["phase_scores"].values():
        totals = phase_audit["component_totals"]
        assert totals["downstream_storage"] == 0.0
        assert totals["spillback"] == 0.0
        assert totals["switching"] == 0.0
        assert totals["service"] == 0.0
        assert totals["incident"] == 0.0


def test_finite_storage_binding_changes_action_and_terms() -> None:
    phase_states, movements, queues, capacities, state = two_phase_fixture(binding=True)
    audit = select_finite_storage_action_with_audit("J0", 0, phase_states, movements, queues, capacities, state)
    assert audit["pressure_action"] == 0
    assert audit["finite_storage_action"] == 1
    assert audit["selected_action"] == audit["finite_storage_action"]
    assert {"downstream_storage", "spillback"} & set(audit["changing_terms"])


def test_choose_controller_action_prefers_pressure_phase() -> None:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("in_a", "out_a"), ("in_b", "out_b")]}
    queues = {"in_a": 1.0, "out_a": 0.0, "in_b": 10.0, "out_b": 0.0}
    capacities = {"out_a": 20.0, "out_b": 20.0}

    action = choose_controller_action(
        "max_pressure",
        "J0",
        current_phase=0,
        step=20,
        action_interval=10,
        phase_states=phase_states,
        tls_movements=movements,
        queues=queues,
        capacities=capacities,
    )

    assert action == 1


def test_capacity_aware_penalizes_full_downstream() -> None:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("in_a", "out_a"), ("in_b", "out_b")]}
    queues = {"in_a": 10.0, "out_a": 10.0, "in_b": 8.0, "out_b": 0.0}
    capacities = {"out_a": 10.0, "out_b": 20.0}

    action = choose_controller_action(
        "capacity_aware_pressure",
        "J0",
        current_phase=0,
        step=20,
        action_interval=10,
        phase_states=phase_states,
        tls_movements=movements,
        queues=queues,
        capacities=capacities,
    )

    assert action == 1


def test_phase10_baseline_variants_are_selectable() -> None:
    phase_states = {"J0": ["Gr", "rG"]}
    movements = {"J0": [("in_a", "out_a"), ("in_b", "out_b")]}
    capacities = {"out_a": 10.0, "out_b": 20.0}

    cycle_action = choose_controller_action(
        "cycle_pressure",
        "J0",
        current_phase=0,
        step=20,
        action_interval=10,
        phase_states=phase_states,
        tls_movements=movements,
        queues={"in_a": 1.0, "out_a": 0.0, "in_b": 10.0, "out_b": 0.0},
        capacities=capacities,
    )
    assert cycle_action == 0

    double_pressure_action = choose_controller_action(
        "finite_storage_double_pressure",
        "J0",
        current_phase=0,
        step=20,
        action_interval=10,
        phase_states=phase_states,
        tls_movements=movements,
        queues={"in_a": 10.0, "out_a": 10.0, "in_b": 8.0, "out_b": 0.0},
        capacities=capacities,
    )
    assert double_pressure_action == 1


def test_metric_aggregation_schema() -> None:
    metrics = aggregate_metrics(
        observations=[
            {"total_queue": 2.0, "max_queue": 2.0, "active_vehicles": 4.0, "spillback": 0.0, "blocking": 0.0},
            {"total_queue": 4.0, "max_queue": 3.0, "active_vehicles": 5.0, "spillback": 1.0, "blocking": 1.0},
        ],
        steps=10,
        warmup=2,
        departed={"veh3": 2.0},
        arrived_times=[4.0, 6.0],
        waiting_delay=7.0,
        runtime=0.25,
        switching_count=3,
    )

    required = {
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
    }
    assert required <= set(metrics)
    assert metrics["completed_vehicles"] == 2
    assert metrics["avg_travel_time"] == 5.0
    assert metrics["total_delay"] == 7.0
    assert metrics["completion_rate"] == 2 / 3
    assert metrics["mean_queue"] == 3.0
    assert metrics["max_queue"] == 3.0
    assert metrics["spillback_count"] == 1
    assert metrics["blocking_count"] == 1
    assert metrics["switching_count"] == 3
    assert set(metrics["objective_components"]) == OBJECTIVE_COMPONENT_FIELDS
    assert metrics["objective_components"]["delay"] == 7.0
    assert metrics["objective_components"]["unfinished_vehicle_penalty"] == 8.0
    assert metrics["objective_components"]["spillback_blocking_time"] == 16.0
    assert metrics["objective_components"]["switching_lost_time"] == 6.0


def test_completed_finite_storage_state_schema() -> None:
    state = build_completed_finite_storage_state(
        queues={"edge_a": 2.0, "edge_b": 9.0},
        capacities={"edge_a": 10.0, "edge_b": 10.0},
        current_phase=1,
        time_since_switch=5.0,
        incident_edge="edge_b",
        capacity_drop_factor=0.35,
    )

    assert set(state) == FINITE_STORAGE_STATE_FIELDS
    validate_finite_storage_state(state, path=Path("row.json"), sample_idx=0)
    row = {"finite_storage_state": state, "objective_components": {field: 0.0 for field in OBJECTIVE_COMPONENT_FIELDS}}
    validate_state_objective_sample(row, path=Path("row.json"), sample_idx=0)


def test_not_feasible_controller_has_explicit_state_and_objective_components() -> None:
    row = run_experiment(
        network="single",
        controller="full_dual_symbolic",
        seed=1,
        steps=10,
        warmup=0,
        action_interval=5,
        route_metadata={"route_decision": "pressure-equivalent", "route_confidence": "MEDIUM", "route_json": "route.json"},
        scenario_tag="single_sanity",
    )

    assert row["feasibility_status"] == "not_feasible"
    assert set(row["finite_storage_state"]) == FINITE_STORAGE_STATE_FIELDS
    assert set(row["objective_components"]) == OBJECTIVE_COMPONENT_FIELDS
    assert all(value == 0.0 for value in row["objective_components"].values())
    assert "finite_storage_state_summary" not in row
    assert "action_decomposition" not in row
    validate_finite_storage_state(row["finite_storage_state"], path=Path("row.json"), sample_idx=0)
    validate_state_objective_sample(row, path=Path("row.json"), sample_idx=0)


def test_finite_storage_controller_run_experiment_row_audit() -> None:
    row = run_experiment(
        network="single",
        controller="finite_storage_primal_dual",
        seed=20260524,
        steps=80,
        warmup=20,
        action_interval=10,
        route_metadata={"route_decision": "pressure-equivalent", "route_confidence": "MEDIUM", "route_json": "route.json"},
        scenario_tag="single_sanity",
    )

    assert row["feasibility_status"] != "not_feasible"
    validate_state_objective_sample(row, path=Path("row.json"), sample_idx=0)
    audit = row["action_decomposition"]
    assert audit["controller"] == "finite_storage_primal_dual"
    assert audit["decision_scope"] == "last_action_decision_per_tls"
    assert audit["last_decision_by_tls"]
    for tls_audit in audit["last_decision_by_tls"].values():
        assert tls_audit["selected_action"] == tls_audit["finite_storage_action"]
        assert "pressure_action" in tls_audit
        assert "phase_scores" in tls_audit
        assert "selected_component_totals" in tls_audit
    assert "action_decomposition" not in METRIC_FIELDS
    metrics = aggregate_metrics(
        observations=[{"total_queue": 1.0, "max_queue": 1.0, "active_vehicles": 1.0, "spillback": 0.0, "blocking": 0.0}],
        steps=10,
        warmup=0,
        departed={},
        arrived_times=[],
        waiting_delay=1.0,
        runtime=0.0,
        switching_count=0,
    )
    assert "action_decomposition" not in metrics


def test_route_metadata_loader() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "route.json"
        path.write_text(json.dumps({"route_decision": "pressure-equivalent", "route_confidence": "MEDIUM"}), encoding="utf-8")
        metadata = load_route_metadata(path)
    assert metadata["route_decision"] == "pressure-equivalent"
    assert metadata["route_confidence"] == "MEDIUM"


def test_route_metadata_loader_rejects_missing_route() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "route.json"
        path.write_text(json.dumps({"status": "PASSED"}), encoding="utf-8")
        try:
            load_route_metadata(path)
        except ValueError as exc:
            assert "route_decision" in str(exc)
        else:
            raise AssertionError("missing route_decision should fail")


def test_network_resolver_supports_phase4_networks() -> None:
    assert resolve_network("single")["sumocfg"].name == "single_intersection.sumocfg"
    assert resolve_network("arterial")["sumocfg"].name == "arterial.sumocfg"
    assert resolve_network("grid_4x4")["sumocfg"].name == "grid_4x4.sumocfg"


def test_not_feasible_controller_metadata() -> None:
    row = run_experiment(
        network="single",
        controller="full_dual_symbolic",
        seed=1,
        steps=10,
        warmup=0,
        action_interval=5,
        route_metadata={"route_decision": "pressure-equivalent", "route_confidence": "MEDIUM", "route_json": "route.json"},
        scenario_tag="single_sanity",
    )
    assert row["feasibility_status"] == "not_feasible"
    assert "dual" in row["unsupported_reason"].lower()
    assert set(row["finite_storage_state"]) == FINITE_STORAGE_STATE_FIELDS
    assert set(row["objective_components"]) == OBJECTIVE_COMPONENT_FIELDS


def test_failure_mode_restores_speed_after_window() -> None:
    calls = []
    original_set_max_speed = apply_failure_mode.__globals__["traci"].edge.setMaxSpeed
    apply_failure_mode.__globals__["traci"].edge.setMaxSpeed = lambda edge, speed: calls.append((edge, speed))
    try:
        assert apply_failure_mode(10, 10, "edge1", 20.0) == "edge_speed_reduction"
        assert apply_failure_mode(130, 10, "edge1", 20.0) is None
    finally:
        apply_failure_mode.__globals__["traci"].edge.setMaxSpeed = original_set_max_speed
    assert calls == [("edge1", 7.0), ("edge1", 20.0)]


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


def test_aggregate_results_and_completion_gates() -> None:
    rows = []
    for scenario in ["arterial_main", "grid_scalability"]:
        for controller in ["fixed_time", "actuated_local_pressure", "max_pressure", "capacity_aware_pressure", "cycle_pressure", "finite_storage_double_pressure", "finite_storage_primal_dual", "raw_neighbor_symbolic", "all_neighbor_symbolic", "random_permuted_dual"]:
            for seed in range(5):
                rows.append(
                    {
                        "network": "arterial" if scenario == "arterial_main" else "grid_4x4",
                        "scenario_tag": scenario,
                        "controller": controller,
                        "seed": seed,
                        "scenario_status": "completed",
                        "feasibility_status": "run",
                        **{field: 1.0 for field in ["avg_travel_time", "penalized_avg_travel_time", "total_delay", "completed_vehicles", "completion_rate", "throughput", "mean_queue", "max_queue", "controller_runtime_sec"]},
                        "completed_vehicles": 1,
                        "completion_rate": 1.0,
                        "spillback_count": 0,
                        "blocking_count": 0,
                        "switching_count": 0 if controller == "fixed_time" else 1,
                    }
                )
    rows.append({"network": "arterial", "scenario_tag": "arterial_demand_shift", "controller": "max_pressure", "seed": 1, "steps": 100, "warmup": 20, "scenario_status": "completed", "feasibility_status": "run", "demand_shift_mechanism": "traci_vehicle_insertion", "demand_shift_inserted_vehicles": 3, **{field: 1.0 for field in ["avg_travel_time", "penalized_avg_travel_time", "total_delay", "completed_vehicles", "completion_rate", "throughput", "mean_queue", "max_queue", "controller_runtime_sec"]}, "completed_vehicles": 1, "completion_rate": 1.0, "spillback_count": 0, "blocking_count": 0, "switching_count": 1})
    rows.append({"network": "arterial", "scenario_tag": "arterial_bottleneck_failure_mode", "controller": "max_pressure", "seed": 1, "scenario_status": "completed", "feasibility_status": "run", "failure_mode_mechanism": "edge_speed_reduction", "failure_mode_target_edge": "edge1", "failure_mode_target_max_vehicles": 1, **{field: 1.0 for field in ["avg_travel_time", "penalized_avg_travel_time", "total_delay", "completed_vehicles", "completion_rate", "throughput", "mean_queue", "max_queue", "controller_runtime_sec"]}, "completed_vehicles": 1, "completion_rate": 1.0, "spillback_count": 0, "blocking_count": 0, "switching_count": 1})
    rows.append({"network": "arterial", "scenario_tag": "arterial_bottleneck_failure_mode", "controller": "capacity_aware_pressure", "seed": 1, "scenario_status": "completed", "feasibility_status": "run", "failure_mode_mechanism": "edge_speed_reduction", "failure_mode_target_edge": "edge1", "failure_mode_target_max_vehicles": 1, **{field: 1.0 for field in ["avg_travel_time", "penalized_avg_travel_time", "total_delay", "completed_vehicles", "completion_rate", "throughput", "mean_queue", "max_queue", "controller_runtime_sec"]}, "completed_vehicles": 1, "completion_rate": 1.0, "spillback_count": 0, "blocking_count": 0, "switching_count": 1})

    aggregates = aggregate_results(rows)
    gates = completion_gates(rows)
    assert aggregates
    assert gates_pass(gates)
    assert aggregates[0]["avg_travel_time"]["n_seeds"] >= 1
    assert "objective_components" not in aggregates[0]


def test_suite_payload_includes_phase6_schema_metadata() -> None:
    payload = build_suite_payload(
        profile="smoke",
        route_metadata={"route_decision": "pressure-equivalent", "route_confidence": "MEDIUM", "route_json": "route.json"},
        rows=[],
        controllers=["fixed_time", "max_pressure"],
        completion_gates_passed=False,
    )

    assert payload["objective_component_schema"]["fields"] == sorted(OBJECTIVE_COMPONENT_FIELDS)
    assert payload["objective_component_schema"]["component_builder"] == "build_objective_components_from_metrics"
    assert payload["finite_storage_state_schema"]["fields"] == sorted(FINITE_STORAGE_STATE_FIELDS)
    assert payload["finite_storage_state_schema"]["row_field"] == "finite_storage_state"
    assert payload["aggregates"] == []


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
    for controller in ["local_pilight", "full_dual_symbolic"]:
        rows.append(
            {
                "network": "single",
                "scenario_tag": "single_sanity",
                "controller": controller,
                "seed": 1,
                "scenario_status": "not_feasible",
                "feasibility_status": "not_feasible",
                "unsupported_reason": "guarded",
                "completed_vehicles": 0,
                "completion_rate": 0.0,
                "switching_count": 0,
                **{field: 0.0 for field in METRIC_FIELDS if field not in {"completed_vehicles", "completion_rate", "switching_count"}},
            }
        )
    for category, tags in STRESS_SCENARIO_CATEGORIES.items():
        for tag in tags:
            expected = "edge_speed_reduction" if any(token in tag for token in ["blockage", "spillback", "incident", "bottleneck"]) else "traci_vehicle_insertion" if any(token in tag for token in ["oversaturation", "turning_shock", "demand_shift"]) else "short_action_interval_switching_audit"
            row = {
                "network": "arterial",
                "scenario_tag": tag,
                "controller": "finite_storage_primal_dual",
                "seed": 1,
                "scenario_status": "completed",
                "feasibility_status": "run",
                "completed_vehicles": 1,
                "completion_rate": 1.0,
                "switching_count": 1,
                "stress_category": category,
                "stress_mechanism": expected,
                **{field: 1.0 for field in METRIC_FIELDS if field not in {"completed_vehicles", "completion_rate", "switching_count"}},
            }
            if expected == "edge_speed_reduction":
                row.update({"failure_mode_mechanism": expected, "failure_mode_target_edge": "edge1", "failure_mode_target_max_vehicles": 1})
            if expected == "traci_vehicle_insertion":
                row.update({"steps": 100, "warmup": 20, "demand_shift_mechanism": expected, "demand_shift_inserted_vehicles": 3})
            rows.append(row)
    return rows


def test_phase10_payload_includes_baseline_stress_and_scope_metadata() -> None:
    rows = phase10_synthetic_rows()
    controllers = REQUIRED_STRONG_BASELINES + ["local_pilight", "full_dual_symbolic"]
    payload = build_suite_payload(
        profile="smoke",
        route_metadata={"route_decision": "pressure-equivalent", "route_confidence": "MEDIUM", "route_json": "route.json"},
        rows=rows,
        controllers=controllers,
        completion_gates_passed=False,
    )

    assert set(REQUIRED_STRONG_BASELINES) <= set(payload["strong_baseline_coverage"]["required_feasible_baselines"])
    assert payload["strong_baseline_coverage"]["passed"]
    assert payload["strong_baseline_coverage"]["not_feasible_guards"]["local_pilight"]["status"] == "not_feasible"
    assert payload["stress_scenario_coverage"] == stress_scenario_coverage(rows)
    assert payload["stress_scenario_coverage"]["passed"]
    assert set(payload["stress_scenario_coverage"]["categories"]) == set(STRESS_SCENARIO_CATEGORIES)
    assert payload["grid_fixed_time_counterexample_check"]["status"] == "represented"
    assert payload["optimized_fixed_time_metadata"]["status"] == "documented_limit"
    assert payload["optimized_fixed_time_metadata"]["implemented_in_phase10"] is False
    assert payload["phase10_scope_caveats"]
    payload_text = json.dumps(payload).lower()
    assert "gate c" not in payload_text.replace("not gate c", "")
    assert "paired-seed dominance" in payload_text
    assert "manuscript claims" in payload_text


def test_phase10_coverage_fails_closed_when_required_evidence_missing() -> None:
    rows = phase10_synthetic_rows()
    missing_controller_rows = [row for row in rows if row.get("controller") != "cycle_pressure"]
    assert not strong_baseline_coverage(missing_controller_rows, REQUIRED_STRONG_BASELINES + ["local_pilight", "full_dual_symbolic"])["passed"]

    missing_guard_rows = [row for row in rows if row.get("controller") != "local_pilight"]
    assert not strong_baseline_coverage(missing_guard_rows, REQUIRED_STRONG_BASELINES + ["local_pilight", "full_dual_symbolic"])["passed"]

    missing_stress_rows = [row for row in rows if row.get("scenario_tag") != "arterial_spillback_stress"]
    assert not stress_scenario_coverage(missing_stress_rows)["passed"]

    forged_mechanism_rows = [dict(row) for row in rows]
    for row in forged_mechanism_rows:
        if row.get("scenario_tag") == "arterial_downstream_blockage":
            row.pop("failure_mode_mechanism", None)
    assert not stress_scenario_coverage(forged_mechanism_rows)["passed"]


def synthetic_payload() -> dict:
    rows = []
    for scenario, network in [("arterial_main", "arterial"), ("grid_scalability", "grid_4x4")]:
        for controller in ["fixed_time", "actuated_local_pressure", "max_pressure", "capacity_aware_pressure", "cycle_pressure", "finite_storage_double_pressure", "finite_storage_primal_dual", "raw_neighbor_symbolic", "all_neighbor_symbolic", "random_permuted_dual"]:
            for seed in range(5):
                rows.append({"network": network, "scenario_tag": scenario, "controller": controller, "seed": seed, "scenario_status": "completed", "feasibility_status": "run", **{field: 1.0 for field in ["avg_travel_time", "penalized_avg_travel_time", "total_delay", "completed_vehicles", "completion_rate", "throughput", "mean_queue", "max_queue", "controller_runtime_sec"]}, "completed_vehicles": 1, "completion_rate": 1.0, "spillback_count": 0, "blocking_count": 0, "switching_count": 0 if controller == "fixed_time" else 1})
    rows.append({"network": "arterial", "scenario_tag": "arterial_demand_shift", "controller": "max_pressure", "seed": 1, "steps": 100, "warmup": 20, "scenario_status": "completed", "feasibility_status": "run", "demand_shift_mechanism": "traci_vehicle_insertion", "demand_shift_inserted_vehicles": 3, **{field: 1.0 for field in ["avg_travel_time", "penalized_avg_travel_time", "total_delay", "completed_vehicles", "completion_rate", "throughput", "mean_queue", "max_queue", "controller_runtime_sec"]}, "completed_vehicles": 1, "completion_rate": 1.0, "spillback_count": 0, "blocking_count": 0, "switching_count": 1})
    rows.append({"network": "arterial", "scenario_tag": "arterial_bottleneck_failure_mode", "controller": "max_pressure", "seed": 1, "scenario_status": "completed", "feasibility_status": "run", "failure_mode_mechanism": "edge_speed_reduction", "failure_mode_target_edge": "edge1", "failure_mode_target_max_vehicles": 1, **{field: 1.0 for field in ["avg_travel_time", "penalized_avg_travel_time", "total_delay", "completed_vehicles", "completion_rate", "throughput", "mean_queue", "max_queue", "controller_runtime_sec"]}, "completed_vehicles": 1, "completion_rate": 1.0, "spillback_count": 0, "blocking_count": 0, "switching_count": 1})
    rows.append({"network": "arterial", "scenario_tag": "arterial_bottleneck_failure_mode", "controller": "capacity_aware_pressure", "seed": 1, "scenario_status": "completed", "feasibility_status": "run", "failure_mode_mechanism": "edge_speed_reduction", "failure_mode_target_edge": "edge1", "failure_mode_target_max_vehicles": 1, **{field: 1.0 for field in ["avg_travel_time", "penalized_avg_travel_time", "total_delay", "completed_vehicles", "completion_rate", "throughput", "mean_queue", "max_queue", "controller_runtime_sec"]}, "completed_vehicles": 1, "completion_rate": 1.0, "spillback_count": 0, "blocking_count": 0, "switching_count": 1})
    return {
        "route_decision": "pressure-equivalent",
        "scenario_results": rows,
        "aggregates": aggregate_results(rows),
        "baseline_coverage": {"fixed_time": {"status": "run"}, "max_pressure": {"status": "run"}, "capacity_aware_pressure": {"status": "run"}},
        "completion_gates": completion_gates(rows),
    }


def test_renderer_report_and_csv() -> None:
    payload = synthetic_payload()
    report = render_report(payload, Path("suite.json"))
    assert "pressure-equivalent" in report
    assert "generalized-pressure symbolic recovery" in report
    assert "max_pressure" in report and "capacity_aware_pressure" in report
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(tmp) / "suite.csv"
        write_csv(payload, csv_path)
        text = csv_path.read_text(encoding="utf-8")
    assert "controller" in text and "avg_travel_time" in text and "controller_runtime_sec" in text


def test_renderer_surfaces_phase6_objective_columns() -> None:
    payload = synthetic_payload()
    payload["scenario_results"][0]["objective_components"] = {
        "delay": 1.0,
        "unfinished_vehicle_penalty": 2.0,
        "spillback_blocking_time": 3.0,
        "switching_lost_time": 4.0,
    }
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(tmp) / "suite.csv"
        write_csv(payload, csv_path)
        text = csv_path.read_text(encoding="utf-8")
    assert "objective_delay" in text
    assert "objective_switching_lost_time" in text


def test_renderer_rejects_missing_completion_gate() -> None:
    payload = synthetic_payload()
    payload["completion_gates"]["arterial_main"]["max_pressure"] = {"completed_seeds": 4, "passed": False}
    try:
        render_report(payload, Path("suite.json"))
    except ValueError as exc:
        assert "completion_gates" in str(exc) or "Completion/actuation gate failed" in str(exc)
    else:
        raise AssertionError("renderer should reject incomplete seed gates")


def test_paper_artifacts_require_phase6_guard_artifacts() -> None:
    finite_state = {
        "downstream_storage": {"edge_a": 10.0},
        "residual_receiving_capacity": {"edge_a": 8.0},
        "spillback_blocking": {"edge_a": {"spillback": False, "blocking": False, "occupancy_ratio": 0.2}},
        "switching_loss_state": {"current_phase": 0, "time_since_switch": 5.0},
        "service_urgency": {"edge_a": 0.2},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0},
    }
    objective = {
        "delay": 1.0,
        "unfinished_vehicle_penalty": 0.0,
        "spillback_blocking_time": 0.0,
        "switching_lost_time": 0.0,
    }
    base_inputs = {
        "block0": {"status": "PASSED", "results": [1]},
        "sparse": {"status": "PASSED", "best_by_library": [1]},
        "static": {"status": "PASSED", "route_decision": "pressure-equivalent", "regime_metrics": [1]},
        "closed_loop": {
            "status": "PASSED",
            "route_decision": "pressure-equivalent",
            "completion_gates_passed": True,
            "metric_schema": {field: "metric" for field in [
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
            ]},
            "scenario_results": [1],
            "aggregates": [1],
        },
        "repro_manifest": {"status": "PASSED", "artifact_checks": [{"expected": True, "exists": True, "parse_status": "ok"}]},
        "phase6_claim_policy": {
            "status": "PASSED",
            "experiment": "phase6_claim_policy",
            "requirements_covered": ["CLAIM-01", "CLAIM-02"],
            "allowed_claims": {"slack_recovery_or_tie": {}, "binding_regime_improvement_only": {}},
        },
        "phase6_claim_audit": {
            "status": "PASSED",
            "experiment": "phase6_claim_audit",
            "requirements_covered": ["CLAIM-01", "CLAIM-02"],
            "forbidden_hits": [],
            "missing_paths": [],
            "parse_errors": [],
            "policy_validation_errors": [],
            "historical_evidence_quarantine": {"hits": []},
        },
        "phase6_explicit_state_schema": {
            "status": "PASSED",
            "experiment": "phase6_explicit_state_schema",
            "requirements_covered": ["STATE-01", "STATE-02"],
            "schema_version": "phase6_explicit_state_v1",
            "finite_storage_state_fields": sorted(FINITE_STORAGE_STATE_FIELDS),
            "objective_component_fields": sorted(OBJECTIVE_COMPONENT_FIELDS),
        },
        "phase6_state_objective_fixtures": {
            "status": "PASSED",
            "experiment": "phase6_state_objective_fixtures",
            "requirements_covered": ["STATE-01", "STATE-02"],
            "schema_version": "phase6_explicit_state_v1",
            "samples": [{"finite_storage_state": finite_state, "objective_components": objective}],
        },
    }
    validate_paper_inputs(base_inputs)
    missing_guard = dict(base_inputs)
    missing_guard.pop("phase6_claim_audit")
    try:
        validate_paper_inputs(missing_guard)
    except ValueError as exc:
        assert "phase6_claim_audit" in str(exc)
    else:
        raise AssertionError("missing Phase 6 claim audit should fail closed")

    placeholder_guard = dict(base_inputs)
    placeholder_guard["phase6_state_objective_fixtures"] = {
        "status": "PASSED",
        "experiment": "phase6_state_objective_fixtures",
    }
    try:
        validate_paper_inputs(placeholder_guard)
    except ValueError as exc:
        assert "phase6_state_objective_fixtures" in str(exc)
    else:
        raise AssertionError("status-only Phase 6 fixtures guard should fail closed")


def test_repro_registry_includes_phase6_guard_artifacts() -> None:
    registry = build_block_registry()
    phase6_blocks = [item for item in registry if item["block"] == "phase6_claim_state_guards"]
    assert phase6_blocks
    block = phase6_blocks[0]
    assert {"CLAIM-01", "CLAIM-02", "STATE-01", "STATE-02", "STATE-03"} <= set(block["requirements"])
    assert "experiments/dual_sensitivity/phase6_claim_policy.json" in block["expected_artifacts"]
    assert "experiments/dual_sensitivity/phase6_state_objective_fixtures.json" in block["expected_artifacts"]


def test_repro_audit_ignores_policy_metadata_for_forbidden_phrase_scan(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    artifact = tmp_path / "phase6_claim_policy.json"
    artifact.write_text(json.dumps({"status": "PASSED", "forbidden_patterns": ["dual universally beats pressure"]}), encoding="utf-8")
    registry = [
        {
            "block": "policy",
            "description": "policy",
            "commands": [],
            "expected_artifacts": ["phase6_claim_policy.json"],
            "runtime_profile": "short",
            "requirements": ["CLAIM-01"],
            "claim_note": "bounded policy metadata",
        }
    ]
    manifest = audit_artifacts(registry, tmp_path)
    assert manifest["status"] == "PASSED"
    assert manifest["claim_discipline"]["forbidden_phrases_present"] == []


def test_repro_audit_fails_expected_json_with_failed_status(tmp_path: Path) -> None:
    artifact = tmp_path / "failed_guard.json"
    artifact.write_text(json.dumps({"status": "FAILED"}), encoding="utf-8")
    registry = [
        {
            "block": "failed_guard",
            "description": "failed guard",
            "commands": [],
            "expected_artifacts": ["failed_guard.json"],
            "runtime_profile": "short",
            "requirements": ["CLAIM-01"],
            "claim_note": "failed status should fail closed",
        }
    ]

    manifest = audit_artifacts(registry, tmp_path)

    assert manifest["status"] == "FAILED"
    check = next(item for item in manifest["artifact_checks"] if item["path"] == "failed_guard.json")
    assert check["status_required"] is True
    assert check["status"] == "FAILED"


def test_completion_gates_reject_noop_controller_evidence() -> None:
    payload = synthetic_payload()
    for row in payload["scenario_results"]:
        if row["controller"] == "max_pressure" and row["scenario_tag"] in {"arterial_main", "grid_scalability"}:
            row["switching_count"] = 0
    gates = completion_gates(payload["scenario_results"])
    assert not gates_pass(gates)
    payload["completion_gates"] = gates
    try:
        render_report(payload, Path("suite.json"))
    except ValueError as exc:
        assert "actuation" in str(exc)
    else:
        raise AssertionError("renderer should reject no-op controller evidence")


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


if __name__ == "__main__":
    main()
