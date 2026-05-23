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
    aggregate_metrics,
    apply_failure_mode,
    build_completed_finite_storage_state,
    choose_controller_action,
    load_route_metadata,
    resolve_network,
    run_experiment,
)
from render_closed_loop_report import render_report, write_csv  # noqa: E402
from run_closed_loop_suite import (  # noqa: E402
    aggregate_results,
    build_payload as build_suite_payload,
    build_suite_spec,
    completion_gates,
    gates_pass,
)


def test_controller_registry_smoke_names() -> None:
    expected = {
        "fixed_time",
        "actuated_local_pressure",
        "max_pressure",
        "capacity_aware_pressure",
        "local_pilight",
        "raw_neighbor_symbolic",
        "all_neighbor_symbolic",
        "random_permuted_dual",
        "full_dual_symbolic",
    }
    assert expected <= set(CONTROLLER_REGISTRY)


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
    validate_finite_storage_state(row["finite_storage_state"], path=Path("row.json"), sample_idx=0)
    validate_state_objective_sample(row, path=Path("row.json"), sample_idx=0)


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
        controllers=["fixed_time", "max_pressure"],
        arterial_seeds=[1, 2, 3, 4, 5],
        grid_seeds=[6, 7, 8, 9, 10],
        steps=100,
        warmup=20,
        action_interval=10,
    )
    names = {item["scenario_tag"] for item in spec}
    assert {"single_sanity", "arterial_main", "grid_scalability", "arterial_demand_shift", "arterial_bottleneck_failure_mode"} <= names
    assert len([item for item in spec if item["scenario_tag"] == "arterial_main" and item["controller"] == "fixed_time"]) == 5
    assert len([item for item in spec if item["scenario_tag"] == "grid_scalability" and item["controller"] == "max_pressure"]) == 5


def test_aggregate_results_and_completion_gates() -> None:
    rows = []
    for scenario in ["arterial_main", "grid_scalability"]:
        for controller in ["fixed_time", "max_pressure", "capacity_aware_pressure", "raw_neighbor_symbolic", "all_neighbor_symbolic", "random_permuted_dual"]:
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


def synthetic_payload() -> dict:
    rows = []
    for scenario, network in [("arterial_main", "arterial"), ("grid_scalability", "grid_4x4")]:
        for controller in ["fixed_time", "max_pressure", "capacity_aware_pressure", "raw_neighbor_symbolic", "all_neighbor_symbolic", "random_permuted_dual"]:
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


def test_renderer_rejects_missing_completion_gate() -> None:
    payload = synthetic_payload()
    payload["completion_gates"]["arterial_main"]["max_pressure"] = {"completed_seeds": 4, "passed": False}
    try:
        render_report(payload, Path("suite.json"))
    except ValueError as exc:
        assert "completion_gates" in str(exc) or "Completion/actuation gate failed" in str(exc)
    else:
        raise AssertionError("renderer should reject incomplete seed gates")


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
    test_choose_controller_action_prefers_pressure_phase()
    test_capacity_aware_penalizes_full_downstream()
    test_metric_aggregation_schema()
    test_completed_finite_storage_state_schema()
    test_not_feasible_controller_has_explicit_state_and_objective_components()
    test_route_metadata_loader()
    test_route_metadata_loader_rejects_missing_route()
    test_network_resolver_supports_phase4_networks()
    test_not_feasible_controller_metadata()
    test_failure_mode_restores_speed_after_window()
    test_suite_spec_contents_and_seed_counts()
    test_aggregate_results_and_completion_gates()
    test_suite_payload_includes_phase6_schema_metadata()
    test_renderer_report_and_csv()
    test_renderer_rejects_missing_completion_gate()
    test_completion_gates_reject_noop_controller_evidence()
    print("closed-loop SUMO tests ok")


if __name__ == "__main__":
    main()
