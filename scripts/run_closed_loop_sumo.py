#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import traci

from claim_policy import forbidden_claim_hits
from finite_storage_schema import (
    OBJECTIVE_COMPONENT_FIELDS,
    build_finite_storage_state,
    build_objective_components_from_metrics,
    validate_finite_storage_state,
    validate_state_objective_sample,
)
from sample_sumo_states import build_network_metadata

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
CONTROLLER_REGISTRY = {
    "fixed_time": "Deterministic cycle through green phases.",
    "actuated_local_pressure": "Queue-triggered local pressure with fixed-time fallback.",
    "max_pressure": "Movement score q_up - q_down.",
    "capacity_aware_pressure": "Pressure with downstream fullness penalty.",
    "local_pilight": "Real PI-Light/DSL baseline if adaptable; otherwise explicit not_feasible.",
    "raw_neighbor_symbolic": "Symbolic upstream queue minus downstream queue.",
    "all_neighbor_symbolic": "Symbolic pressure with downstream slack/fullness terms.",
    "random_permuted_dual": "Deterministic seed-based placebo movement score.",
    "full_dual_symbolic": "Per-TLS dual policy where feasible; otherwise explicit not_feasible.",
}
NETWORKS = {
    "single": {
        "sumocfg": Path("networks/single_intersection/single_intersection.sumocfg"),
        "net_file": Path("networks/single_intersection/single_intersection.net.xml"),
    },
    "arterial": {
        "sumocfg": Path("networks/arterial/arterial.sumocfg"),
        "net_file": Path("networks/arterial/arterial.net.xml"),
    },
    "grid_4x4": {
        "sumocfg": Path("networks/grid_4x4/grid_4x4.sumocfg"),
        "net_file": Path("networks/grid_4x4/grid_4x4.net.xml"),
    },
}
NOT_FEASIBLE_CONTROLLERS = {
    "local_pilight": "No safely adaptable PI-Light local DSL baseline is present in the SUMO runner interface.",
    "full_dual_symbolic": "Closed-loop per-TLS dual Scenario conversion is not yet safe for live SUMO actuation.",
}
CLAIM_FRAMING = (
    "Phase 3 selected pressure-equivalent; Phase 4 outputs are closed-loop SUMO evidence "
    "for generalized-pressure symbolic recovery, not universal dominance over pressure."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", choices=sorted(NETWORKS), default="single")
    parser.add_argument("--controllers", nargs="+", default=list(CONTROLLER_REGISTRY))
    parser.add_argument("--seeds", nargs="+", type=int, default=[20260523])
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--warmup", type=int, default=60)
    parser.add_argument("--action-interval", type=int, default=10)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block4_closed_loop_smoke.json")
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--scenario-tag", default="single_sanity")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    unknown = sorted(set(args.controllers) - set(CONTROLLER_REGISTRY))
    if unknown:
        raise ValueError(f"Unknown controllers: {unknown}. Available: {sorted(CONTROLLER_REGISTRY)}")
    if args.steps <= 0 or args.warmup < 0 or args.action_interval <= 0:
        raise ValueError("--steps and --action-interval must be positive; --warmup must be nonnegative")
    if not args.seeds:
        raise ValueError("At least one seed is required")


def load_route_metadata(route_json: Path) -> dict[str, str]:
    payload = json.loads(route_json.read_text(encoding="utf-8"))
    route_decision = payload.get("route_decision")
    if not route_decision:
        raise ValueError(f"Route JSON {route_json} is missing route_decision")
    return {
        "route_decision": str(route_decision),
        "route_confidence": str(payload.get("route_confidence", "UNKNOWN")),
        "route_json": str(route_json),
    }


def resolve_network(network: str) -> dict[str, Path]:
    resolved = NETWORKS[network]
    for path in resolved.values():
        if not path.exists():
            raise FileNotFoundError(path)
    return resolved


def read_tls_phase_states(net_file: Path) -> dict[str, list[str]]:
    root = ET.parse(net_file).getroot()
    phase_states: dict[str, list[str]] = {}
    for tls_logic in root.findall("tlLogic"):
        tls_id = tls_logic.get("id")
        if tls_id:
            phase_states[tls_id] = [phase.get("state", "") for phase in tls_logic.findall("phase")]
    return phase_states


def read_tls_link_movements(net_file: Path) -> dict[str, list[tuple[str, str]]]:
    root = ET.parse(net_file).getroot()
    indexed: dict[str, dict[int, tuple[str, str]]] = {}
    for conn in root.findall("connection"):
        tls_id = conn.get("tl")
        link_index = conn.get("linkIndex")
        from_edge = conn.get("from")
        to_edge = conn.get("to")
        if not tls_id or link_index is None or not from_edge or not to_edge:
            continue
        if from_edge.startswith(":") or to_edge.startswith(":"):
            continue
        indexed.setdefault(tls_id, {})[int(link_index)] = (from_edge, to_edge)
    return {tls: [moves[idx] for idx in sorted(moves)] for tls, moves in indexed.items()}


def read_edge_speeds(net_file: Path) -> dict[str, float]:
    root = ET.parse(net_file).getroot()
    speeds: dict[str, float] = {}
    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        if not edge_id or edge_id.startswith(":"):
            continue
        lane = edge.find("lane")
        if lane is not None and lane.get("speed") is not None:
            speeds[edge_id] = float(lane.get("speed", "13.89"))
    return speeds


def green_phases(states: list[str]) -> list[int]:
    greens = [idx for idx, state in enumerate(states) if any(ch in "Gg" for ch in state)]
    return greens or list(range(len(states)))


def movement_score(
    controller: str,
    movement: tuple[str, str],
    queues: dict[str, float],
    capacities: dict[str, float],
    seed: int = 0,
) -> float:
    upstream, downstream = movement
    up_q = float(queues.get(upstream, 0.0))
    down_q = float(queues.get(downstream, 0.0))
    pressure = up_q - down_q
    if controller in {"max_pressure", "raw_neighbor_symbolic"}:
        return pressure
    if controller == "actuated_local_pressure":
        return up_q if sum(queues.values()) >= 1.0 else 0.0
    if controller in {"capacity_aware_pressure", "all_neighbor_symbolic"}:
        cap = max(float(capacities.get(downstream, 1.0)), 1.0)
        fullness = down_q / cap
        slack = cap - down_q
        blocked_penalty = cap if fullness >= 0.85 else 0.0
        return pressure + 0.05 * slack - fullness * up_q - blocked_penalty
    if controller == "random_permuted_dual":
        key = sum(ord(ch) for ch in upstream + downstream) + int(seed)
        return pressure * (1.0 if key % 2 == 0 else -0.5)
    return 0.0


def phase_score(
    controller: str,
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
    capacities: dict[str, float],
    seed: int = 0,
) -> float:
    if not states:
        return 0.0
    state = states[phase_index % len(states)]
    score = 0.0
    for move_idx, movement in enumerate(movements):
        signal = state[move_idx] if move_idx < len(state) else "r"
        if signal in "Gg":
            score += movement_score(controller, movement, queues, capacities, seed)
    return score


def choose_controller_action(
    controller: str,
    tls_id: str,
    current_phase: int,
    step: int,
    action_interval: int,
    phase_states: dict[str, list[str]],
    tls_movements: dict[str, list[tuple[str, str]]],
    queues: dict[str, float],
    capacities: dict[str, float],
    seed: int = 0,
) -> int:
    states = phase_states.get(tls_id, [])
    greens = green_phases(states)
    if controller == "fixed_time" or (controller == "actuated_local_pressure" and sum(queues.values()) < 1.0):
        return greens[(step // action_interval) % len(greens)]
    scored = [
        (phase_score(controller, phase_idx, states, tls_movements.get(tls_id, []), queues, capacities, seed), -phase_idx, phase_idx)
        for phase_idx in greens
    ]
    return max(scored)[2] if scored else current_phase


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
    spillback_count = int(sum(obs["spillback"] for obs in observations))
    blocking_count = int(sum(obs["blocking"] for obs in observations))
    penalized_total = total_travel_time + unfinished * censor_penalty
    metrics = {
        "avg_travel_time": float(total_travel_time / completed) if completed else 0.0,
        "penalized_avg_travel_time": float(penalized_total / departed_total) if departed_total else 0.0,
        "total_delay": float(waiting_delay),
        "completed_vehicles": int(completed),
        "completion_rate": float(completed / departed_total) if departed_total else 0.0,
        "throughput": float(completed / horizon),
        "mean_queue": float(statistics.fmean(queues) if queues else 0.0),
        "max_queue": float(max(max_queues, default=0.0)),
        "spillback_count": spillback_count,
        "blocking_count": blocking_count,
        "switching_count": int(switching_count),
        "controller_runtime_sec": float(runtime),
        "travel_time_source": "conditional_on_arrival_with_censoring_penalty",
        "unfinished_vehicle_count": int(unfinished),
    }
    metrics["objective_components"] = build_objective_components_from_metrics(
        {
            "total_delay": metrics["total_delay"],
            "unfinished_vehicle_count": metrics["unfinished_vehicle_count"],
            "spillback_count": spillback_count,
            "blocking_count": blocking_count,
            "switching_count": switching_count,
        },
        horizon=float(horizon),
    )
    return metrics


def unavailable_finite_storage_state(reason: str) -> dict[str, Any]:
    state = {
        "downstream_storage": {"unavailable": 0.0},
        "residual_receiving_capacity": {"unavailable": 0.0},
        "spillback_blocking": {
            "unavailable": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0}
        },
        "switching_loss_state": {"current_phase": None, "time_since_switch": 0.0, "status_reason": reason},
        "service_urgency": {"unavailable": 0.0},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0, "status_reason": reason},
    }
    validate_finite_storage_state(state)
    return state


def build_completed_finite_storage_state(
    queues: dict[str, float],
    capacities: dict[str, float],
    *,
    current_phase: int | None,
    time_since_switch: float,
    incident_edge: str | None = None,
    capacity_drop_factor: float | None = None,
) -> dict[str, Any]:
    state = build_finite_storage_state(
        queues,
        capacities,
        current_phase=current_phase,
        time_since_switch=time_since_switch,
        incident_edge=incident_edge,
        capacity_drop_factor=capacity_drop_factor,
    )
    validate_finite_storage_state(state)
    return state


def validate_closed_loop_row(row: dict[str, Any]) -> None:
    validate_finite_storage_state(row["finite_storage_state"])
    validate_state_objective_sample(row)


def infeasible_row(
    network: str,
    controller: str,
    seed: int,
    steps: int,
    warmup: int,
    action_interval: int,
    route_metadata: dict[str, str],
    scenario_tag: str,
    reason: str,
) -> dict[str, Any]:
    row = {
        "network": network,
        "scenario_tag": scenario_tag,
        "controller": controller,
        "seed": int(seed),
        "steps": int(steps),
        "warmup": int(warmup),
        "action_interval": int(action_interval),
        "scenario_status": "not_feasible",
        "feasibility_status": "not_feasible",
        "unsupported_reason": reason,
        **route_metadata,
        **{field: 0.0 for field in METRIC_FIELDS},
        "completed_vehicles": 0,
        "completion_rate": 0.0,
        "spillback_count": 0,
        "blocking_count": 0,
        "switching_count": 0,
        "travel_time_source": "not_feasible",
        "unfinished_vehicle_count": 0,
        "objective_components": {field: 0.0 for field in OBJECTIVE_COMPONENT_FIELDS},
        "finite_storage_state": unavailable_finite_storage_state(reason),
    }
    validate_closed_loop_row(row)
    return row


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


def demand_shift_tick(step: int, warmup: int, route_ids: list[str], inserted: set[str]) -> str | None:
    if step < warmup or not route_ids or (step - warmup) % 30 != 0:
        return None
    veh_id = f"phase4_shift_{step}"
    if veh_id in inserted:
        return None
    traci.vehicle.add(veh_id, route_ids[(step // 30) % len(route_ids)], depart=str(max(step + 1, 1)))
    inserted.add(veh_id)
    return "traci_vehicle_insertion"


def select_failure_edge(edge_ids: list[str], tls_movements: dict[str, list[tuple[str, str]]]) -> str | None:
    incoming_counts: dict[str, int] = {}
    for movements in tls_movements.values():
        for upstream, _downstream in movements:
            if upstream in edge_ids:
                incoming_counts[upstream] = incoming_counts.get(upstream, 0) + 1
    if incoming_counts:
        return max(sorted(incoming_counts), key=lambda edge: incoming_counts[edge])
    return edge_ids[0] if edge_ids else None


def apply_failure_mode(step: int, warmup: int, target_edge: str | None, original_speed: float | None) -> str | None:
    if target_edge is None or original_speed is None:
        return None
    if warmup <= step < warmup + 120:
        traci.edge.setMaxSpeed(target_edge, max(original_speed * 0.35, 1.0))
        return "edge_speed_reduction"
    if step == warmup + 120:
        traci.edge.setMaxSpeed(target_edge, original_speed)
    return None


def run_experiment(
    network: str,
    controller: str,
    seed: int,
    steps: int,
    warmup: int,
    action_interval: int,
    route_metadata: dict[str, str],
    scenario_tag: str = "single_sanity",
) -> dict[str, Any]:
    if controller in NOT_FEASIBLE_CONTROLLERS:
        return infeasible_row(network, controller, seed, steps, warmup, action_interval, route_metadata, scenario_tag, NOT_FEASIBLE_CONTROLLERS[controller])

    paths = resolve_network(network)
    metadata = build_network_metadata(paths["net_file"])
    capacities = {str(k): float(v) for k, v in metadata["edge_capacity"].items()}
    tls_movements = read_tls_link_movements(paths["net_file"])
    phase_states = read_tls_phase_states(paths["net_file"])
    edge_ids = sorted(capacities)
    edge_speeds = read_edge_speeds(paths["net_file"])
    target_edge = select_failure_edge(edge_ids, tls_movements)
    cmd = ["sumo", "-c", str(paths["sumocfg"]), "--seed", str(seed), "--no-step-log", "true", "--duration-log.disable", "true"]
    traci.start(cmd)
    observations: list[dict[str, float]] = []
    departed: dict[str, float] = {}
    arrived_times: list[float] = []
    latest_queues = {edge_id: 0.0 for edge_id in edge_ids}
    latest_current_phase: int | None = None
    latest_time_since_switch = 0.0
    switching_count = 0
    controller_runtime = 0.0
    last_phase_by_tls: dict[str, int] = {}
    target_phase_by_tls: dict[str, int] = {}
    phase_since_by_tls: dict[str, int] = {}
    waiting_delay = 0.0
    demand_shift_mechanism = None
    failure_mode_mechanism = None
    inserted: set[str] = set()
    failure_target_max_vehicles = 0.0
    try:
        route_ids = list(traci.route.getIDList())
        original_speed = float(edge_speeds.get(target_edge, 13.89)) if target_edge else None
        for step in range(steps):
            if "bottleneck" in scenario_tag or "failure_mode" in scenario_tag:
                mechanism = apply_failure_mode(step, warmup, target_edge, original_speed)
                if mechanism:
                    failure_mode_mechanism = mechanism
            if "demand_shift" in scenario_tag:
                mechanism = demand_shift_tick(step, warmup, route_ids, inserted)
                if mechanism:
                    demand_shift_mechanism = mechanism
            traci.simulationStep()
            if target_edge:
                failure_target_max_vehicles = max(failure_target_max_vehicles, float(traci.edge.getLastStepVehicleNumber(target_edge)))
            sim_time = float(traci.simulation.getTime())
            for veh_id in traci.simulation.getDepartedIDList():
                departed.setdefault(str(veh_id), sim_time)
            for veh_id in traci.simulation.getArrivedIDList():
                start = departed.pop(str(veh_id), None)
                if start is not None:
                    arrived_times.append(max(sim_time - start, 0.0))
            queues = {edge_id: float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids}
            latest_queues = queues
            if step >= warmup and (step - warmup) % action_interval == 0:
                start = time.perf_counter()
                for tls_id in sorted(tls_movements):
                    current_phase = int(traci.trafficlight.getPhase(tls_id))
                    latest_current_phase = current_phase
                    latest_time_since_switch = float(step - phase_since_by_tls.get(tls_id, step))
                    previous_phase = last_phase_by_tls.get(tls_id)
                    if previous_phase is None:
                        last_phase_by_tls[tls_id] = current_phase
                        phase_since_by_tls[tls_id] = step - action_interval
                    elif previous_phase != current_phase:
                        phase_since_by_tls[tls_id] = step
                        last_phase_by_tls[tls_id] = current_phase
                        if target_phase_by_tls.get(tls_id) == current_phase:
                            switching_count += 1
                    action = choose_controller_action(controller, tls_id, current_phase, step, action_interval, phase_states, tls_movements, queues, capacities, seed)
                    target_phase_by_tls.setdefault(tls_id, current_phase)
                    states = phase_states.get(tls_id, [])
                    n_phases = max(len(states), 1)
                    current_state = states[current_phase] if current_phase < len(states) else ""
                    current_is_green = any(ch in "Gg" for ch in current_state)
                    phase_since = phase_since_by_tls.get(tls_id, step - action_interval)
                    if current_is_green and action != current_phase and step - phase_since >= action_interval:
                        target_phase_by_tls[tls_id] = int(action)
                    target = target_phase_by_tls.get(tls_id, current_phase)
                    if target != current_phase:
                        next_phase = (current_phase + 1) % n_phases
                        traci.trafficlight.setPhase(tls_id, int(next_phase))
                        phase_since_by_tls[tls_id] = step
                        if next_phase == target:
                            switching_count += 1
                            target_phase_by_tls[tls_id] = next_phase
                        last_phase_by_tls[tls_id] = int(next_phase)
                controller_runtime += time.perf_counter() - start
            if step >= warmup:
                waiting_delay += sum(float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids)
                observations.append(edge_observation(edge_ids, capacities))
    finally:
        traci.close(False)

    row = {
        "network": network,
        "scenario_tag": scenario_tag,
        "controller": controller,
        "seed": int(seed),
        "steps": int(steps),
        "warmup": int(warmup),
        "action_interval": int(action_interval),
        "scenario_status": "completed",
        "feasibility_status": "run",
        "sumocfg": str(paths["sumocfg"]),
        "net_file": str(paths["net_file"]),
        **route_metadata,
        **aggregate_metrics(observations, steps, warmup, departed, arrived_times, waiting_delay, controller_runtime, switching_count),
        "finite_storage_state": build_completed_finite_storage_state(
            latest_queues,
            capacities,
            current_phase=latest_current_phase,
            time_since_switch=latest_time_since_switch,
            incident_edge=target_edge if failure_mode_mechanism else None,
            capacity_drop_factor=0.35 if failure_mode_mechanism else None,
        ),
    }
    if demand_shift_mechanism:
        row["demand_shift_mechanism"] = demand_shift_mechanism
        row["demand_shift_inserted_vehicles"] = len(inserted)
    if failure_mode_mechanism:
        row["failure_mode_mechanism"] = failure_mode_mechanism
        row["failure_mode_target_edge"] = target_edge
        row["failure_mode_target_max_vehicles"] = failure_target_max_vehicles
        row["failure_mode_start"] = warmup
        row["failure_mode_end"] = warmup + 120
    if row["completed_vehicles"] == 0:
        row["smoke_notes"] = "Short horizon produced no completed vehicles; queue/switch/runtime metrics remain valid."
    validate_closed_loop_row(row)
    return row


def build_payload(args: argparse.Namespace, route_metadata: dict[str, str], rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "experiment": "block4_closed_loop_sumo",
        **route_metadata,
        "claim_framing": CLAIM_FRAMING,
        "networks": [args.network],
        "controllers": list(args.controllers),
        "seeds": list(args.seeds),
        "scenario_tag": args.scenario_tag,
        "steps": args.steps,
        "warmup": args.warmup,
        "action_interval": args.action_interval,
        "scenario_results": rows,
        "metric_schema": {field: "CLOP-04 metric" for field in METRIC_FIELDS},
    }
    forbidden = forbidden_claim_hits(json.dumps({"claim_framing": payload["claim_framing"]}))
    if forbidden:
        raise ValueError(f"Output contains forbidden claim language: {forbidden}")
    return payload


def main() -> None:
    args = parse_args()
    validate_args(args)
    route_metadata = load_route_metadata(Path(args.route_json))
    rows = [
        run_experiment(args.network, controller, seed, args.steps, args.warmup, args.action_interval, route_metadata, args.scenario_tag)
        for seed in args.seeds
        for controller in args.controllers
    ]
    payload = build_payload(args, route_metadata, rows)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "rows": len(rows), "route_decision": payload["route_decision"]}, indent=2))


if __name__ == "__main__":
    main()
