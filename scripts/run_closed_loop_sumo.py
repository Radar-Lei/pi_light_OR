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
    "cycle_pressure": "Pressure with deterministic current-cycle hold bias.",
    "finite_storage_double_pressure": "Pressure with finite-storage receiving-capacity correction.",
    "local_pilight": "Real PI-Light/DSL baseline if adaptable; otherwise explicit not_feasible.",
    "raw_neighbor_symbolic": "Symbolic upstream queue minus downstream queue.",
    "all_neighbor_symbolic": "Symbolic pressure with downstream slack/fullness terms.",
    "random_permuted_dual": "Deterministic seed-based placebo movement score.",
    "finite_storage_primal_dual": "Finite-storage pressure rule with auditable storage, spillback, switching, service, and incident terms.",
    "finite_storage_primal_dual_v1_4_score": "v1.4 locked finite-storage score variant with stronger binding-regime terms.",
    "full_dual_symbolic": "Per-TLS dual policy where feasible; otherwise explicit not_feasible.",
}
FINITE_STORAGE_CONTROLLER_IDS = {
    "finite_storage_primal_dual",
    "finite_storage_primal_dual_v1_4_score",
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
    if controller not in CONTROLLER_REGISTRY:
        raise ValueError(f"Unknown controller: {controller}. Available: {sorted(CONTROLLER_REGISTRY)}")
    upstream, downstream = movement
    up_q = float(queues.get(upstream, 0.0))
    down_q = float(queues.get(downstream, 0.0))
    pressure = up_q - down_q
    if controller in {"max_pressure", "raw_neighbor_symbolic"}:
        return pressure
    if controller == "actuated_local_pressure":
        return up_q if sum(queues.values()) >= 1.0 else 0.0
    if controller in {"capacity_aware_pressure", "all_neighbor_symbolic", "finite_storage_double_pressure"}:
        cap = max(float(capacities.get(downstream, 1.0)), 1.0)
        fullness = down_q / cap
        slack = cap - down_q
        blocked_penalty = cap if fullness >= 0.85 else 0.0
        double_pressure = max(up_q - max(slack, 0.0), 0.0) if controller == "finite_storage_double_pressure" else 0.0
        return pressure + 0.05 * slack - fullness * up_q - blocked_penalty - double_pressure
    if controller == "random_permuted_dual":
        key = sum(ord(ch) for ch in upstream + downstream) + int(seed)
        return pressure * (1.0 if key % 2 == 0 else -0.5)
    return 0.0


FINITE_STORAGE_DECOMPOSITION_FIELDS = {
    "pressure",
    "downstream_storage",
    "spillback",
    "switching",
    "service",
    "incident",
    "total",
}
SERVICE_URGENCY_NEUTRAL_THRESHOLD = 0.85
MIN_SWITCHING_HOLD_TIME = 10.0


def _spillback_flags(state: dict[str, Any], edge: str) -> dict[str, Any]:
    flags = state.get("spillback_blocking", {}).get(edge, {})
    if isinstance(flags, bool):
        return {"spillback": flags, "blocking": flags, "occupancy_ratio": 1.0 if flags else 0.0}
    return flags if isinstance(flags, dict) else {}


def finite_storage_movement_decomposition(
    movement: tuple[str, str],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
) -> dict[str, float]:
    upstream, downstream = movement
    up_q = float(queues.get(upstream, 0.0))
    down_q = float(queues.get(downstream, 0.0))
    pressure = up_q - down_q
    capacity = max(float(capacities.get(downstream, finite_storage_state.get("downstream_storage", {}).get(downstream, 1.0))), 1.0)
    residual = float(finite_storage_state.get("residual_receiving_capacity", {}).get(downstream, capacity))
    downstream_storage = -max(capacity - max(residual, 0.0), 0.0) if residual < min(up_q, capacity) else 0.0
    flags = _spillback_flags(finite_storage_state, downstream)
    spillback = 0.0
    if bool(flags.get("spillback", False)):
        spillback -= 0.5 * capacity
    if bool(flags.get("blocking", False)):
        spillback -= 0.5 * capacity
    urgency = float(finite_storage_state.get("service_urgency", {}).get(upstream, 0.0))
    service = max(urgency - SERVICE_URGENCY_NEUTRAL_THRESHOLD, 0.0) * max(capacity, up_q, 1.0)
    incident_state = finite_storage_state.get("incident_capacity_drop", {})
    incident = 0.0
    incident_edge = incident_state.get("edge")
    if incident_state.get("active") and incident_edge in {upstream, downstream}:
        factor = max(float(incident_state.get("factor", 1.0)), 0.0)
        incident_capacity = max(float(capacities.get(str(incident_edge), capacity)), 1.0)
        incident = -(1.0 - min(factor, 1.0)) * incident_capacity
    components = {
        "pressure": float(pressure),
        "downstream_storage": float(downstream_storage),
        "spillback": float(spillback),
        "switching": 0.0,
        "service": float(service),
        "incident": float(incident),
    }
    components["total"] = float(sum(components.values()))
    return components


def finite_storage_phase_decomposition(
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    *,
    current_phase: int | None = None,
) -> dict[str, Any]:
    movement_decompositions = []
    totals = {field: 0.0 for field in FINITE_STORAGE_DECOMPOSITION_FIELDS}
    if states:
        state = states[phase_index % len(states)]
        for move_idx, movement in enumerate(movements):
            signal = state[move_idx] if move_idx < len(state) else "r"
            if signal in "Gg":
                decomposition = finite_storage_movement_decomposition(movement, queues, capacities, finite_storage_state)
                movement_decompositions.append({"movement": list(movement), "components": decomposition})
                for field in FINITE_STORAGE_DECOMPOSITION_FIELDS:
                    totals[field] += decomposition[field]
    switching_state = finite_storage_state.get("switching_loss_state", {})
    active_phase = current_phase if current_phase is not None else switching_state.get("current_phase")
    time_since_switch = float(switching_state.get("time_since_switch", MIN_SWITCHING_HOLD_TIME))
    if active_phase is not None and int(phase_index) != int(active_phase) and time_since_switch < MIN_SWITCHING_HOLD_TIME:
        totals["switching"] -= MIN_SWITCHING_HOLD_TIME - time_since_switch
    totals["total"] = sum(value for field, value in totals.items() if field != "total")
    return {
        "phase_index": int(phase_index),
        "score": float(totals["total"]),
        "component_totals": {field: float(totals[field]) for field in sorted(FINITE_STORAGE_DECOMPOSITION_FIELDS)},
        "movement_decompositions": movement_decompositions,
    }


def _score_weighted_decomposition(decomposition: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    weighted = dict(decomposition)
    component_totals = {
        field: float(value) * float(weights.get(field, 1.0))
        for field, value in dict(decomposition.get("component_totals", {})).items()
    }
    component_totals["total"] = sum(value for field, value in component_totals.items() if field != "total")
    weighted["component_totals"] = component_totals
    weighted["score"] = float(component_totals["total"])
    weighted["score_variant"] = "finite_storage_primal_dual_v1_4_score"
    weighted["score_weights"] = {field: float(weights.get(field, 1.0)) for field in sorted(FINITE_STORAGE_DECOMPOSITION_FIELDS)}
    return weighted


def select_finite_storage_action_with_audit(
    tls_id: str,
    current_phase: int,
    phase_states: dict[str, list[str]],
    tls_movements: dict[str, list[tuple[str, str]]],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    seed: int = 0,
    controller: str = "finite_storage_primal_dual",
) -> dict[str, Any]:
    states = phase_states.get(tls_id, [])
    greens = green_phases(states)
    movements = tls_movements.get(tls_id, [])
    score_weights = None
    if controller == "finite_storage_primal_dual_v1_4_score":
        score_weights = {
            "pressure": 1.0,
            "downstream_storage": 1.4,
            "spillback": 1.6,
            "switching": 1.25,
            "service": 1.35,
            "incident": 1.0,
            "total": 1.0,
        }
    finite_phase_scores = {}
    for phase_idx in greens:
        decomposition = finite_storage_phase_decomposition(
            phase_idx,
            states,
            movements,
            queues,
            capacities,
            finite_storage_state,
            current_phase=current_phase,
        )
        if score_weights is not None:
            decomposition = _score_weighted_decomposition(decomposition, score_weights)
        finite_phase_scores[int(phase_idx)] = decomposition
    pressure_phase_scores = {
        int(phase_idx): float(phase_score("max_pressure", phase_idx, states, movements, queues, capacities, seed))
        for phase_idx in greens
    }
    pressure_action = max((score, -phase_idx, phase_idx) for phase_idx, score in pressure_phase_scores.items())[2] if pressure_phase_scores else current_phase
    finite_storage_action = max(
        (audit["score"], -phase_idx, phase_idx) for phase_idx, audit in finite_phase_scores.items()
    )[2] if finite_phase_scores else current_phase
    selected_totals = finite_phase_scores.get(finite_storage_action, {}).get("component_totals", {})
    changing_terms = sorted(
        field for field in ["downstream_storage", "spillback", "switching", "service", "incident"] if abs(float(selected_totals.get(field, 0.0))) > 1e-9
    )
    if finite_storage_action != pressure_action:
        pressure_totals = finite_phase_scores.get(pressure_action, {}).get("component_totals", {})
        changing_terms = sorted(
            field
            for field in ["downstream_storage", "spillback", "switching", "service", "incident"]
            if abs(float(selected_totals.get(field, 0.0))) > 1e-9 or abs(float(pressure_totals.get(field, 0.0))) > 1e-9
        )
    return {
        "tls_id": tls_id,
        "controller": controller,
        "pressure_action": int(pressure_action),
        "finite_storage_action": int(finite_storage_action),
        "selected_action": int(finite_storage_action),
        "pressure_phase_scores": {str(phase): score for phase, score in pressure_phase_scores.items()},
        "phase_scores": {str(phase): audit for phase, audit in finite_phase_scores.items()},
        "selected_component_totals": selected_totals,
        "action_changed_relative_to_pressure": bool(finite_storage_action != pressure_action),
        "changing_terms": changing_terms,
    }


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
    if controller not in CONTROLLER_REGISTRY:
        raise ValueError(f"Unknown controller: {controller}. Available: {sorted(CONTROLLER_REGISTRY)}")
    states = phase_states.get(tls_id, [])
    greens = green_phases(states)
    if controller == "fixed_time" or (controller == "actuated_local_pressure" and sum(queues.values()) < 1.0):
        return greens[(step // action_interval) % len(greens)]
    if controller == "cycle_pressure" and step - (step // (2 * action_interval)) * (2 * action_interval) < action_interval:
        return current_phase if current_phase in greens else greens[(step // action_interval) % len(greens)]
    if controller in FINITE_STORAGE_CONTROLLER_IDS:
        finite_storage_state = build_completed_finite_storage_state(
            queues,
            capacities,
            current_phase=current_phase,
            time_since_switch=float(action_interval),
        )
        audit = select_finite_storage_action_with_audit(
            tls_id,
            current_phase,
            phase_states,
            tls_movements,
            queues,
            capacities,
            finite_storage_state,
            seed,
            controller=controller,
        )
        return int(audit["selected_action"])
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
    if row.get("controller") in FINITE_STORAGE_CONTROLLER_IDS and row.get("scenario_status") == "completed":
        action_decomposition = row.get("action_decomposition")
        if not isinstance(action_decomposition, dict):
            raise ValueError(f"{row.get('controller')} completed row requires action_decomposition")
        decisions = action_decomposition.get("last_decision_by_tls")
        if not isinstance(decisions, dict) or not decisions:
            raise ValueError(f"{row.get('controller')} action_decomposition requires nonempty last_decision_by_tls")


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


def scenario_stress_metadata(scenario_tag: str) -> dict[str, Any]:
    mapping = {
        "arterial_downstream_blockage": ("downstream_blockage", "edge_speed_reduction"),
        "arterial_spillback_stress": ("spillback", "finite_storage_occupancy_stress"),
        "arterial_incident_capacity_drop": ("incident_capacity_drop", "edge_speed_reduction"),
        "arterial_oversaturation": ("oversaturation", "short_horizon_demand_pressure"),
        "arterial_turning_shock": ("turning_shock", "traci_vehicle_insertion"),
        "arterial_switching_loss_sensitive": ("switching_loss_sensitive", "short_action_interval_switching_audit"),
        "arterial_demand_shift": ("turning_shock", "traci_vehicle_insertion"),
        "arterial_bottleneck_failure_mode": ("incident_capacity_drop", "edge_speed_reduction"),
    }
    if scenario_tag not in mapping:
        return {}
    category, mechanism = mapping[scenario_tag]
    return {"stress_category": category, "stress_mechanism": mechanism}


def run_experiment(
    network: str,
    controller: str,
    seed: int,
    steps: int,
    warmup: int,
    action_interval: int,
    route_metadata: dict[str, str],
    scenario_tag: str = "single_sanity",
    sumocfg_override: str | Path | None = None,
) -> dict[str, Any]:
    if controller not in CONTROLLER_REGISTRY:
        raise ValueError(f"Unknown controller: {controller}. Available: {sorted(CONTROLLER_REGISTRY)}")
    if controller in NOT_FEASIBLE_CONTROLLERS:
        return infeasible_row(network, controller, seed, steps, warmup, action_interval, route_metadata, scenario_tag, NOT_FEASIBLE_CONTROLLERS[controller])

    paths = resolve_network(network)
    sumocfg_path = Path(sumocfg_override) if sumocfg_override is not None else paths["sumocfg"]
    if not sumocfg_path.exists():
        raise FileNotFoundError(sumocfg_path)
    metadata = build_network_metadata(paths["net_file"])
    capacities = {str(k): float(v) for k, v in metadata["edge_capacity"].items()}
    tls_movements = read_tls_link_movements(paths["net_file"])
    phase_states = read_tls_phase_states(paths["net_file"])
    edge_ids = sorted(capacities)
    edge_speeds = read_edge_speeds(paths["net_file"])
    target_edge = select_failure_edge(edge_ids, tls_movements)
    stress_metadata = scenario_stress_metadata(scenario_tag)
    cmd = ["sumo", "-c", str(sumocfg_path), "--seed", str(seed), "--no-step-log", "true", "--duration-log.disable", "true"]
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
    failure_mode_active = False
    inserted: set[str] = set()
    failure_target_max_vehicles = 0.0
    latest_action_decomposition_by_tls: dict[str, Any] = {}
    try:
        route_ids = list(traci.route.getIDList())
        original_speed = float(edge_speeds.get(target_edge, 13.89)) if target_edge else None
        for step in range(steps):
            if any(token in scenario_tag for token in ["bottleneck", "failure_mode", "downstream_blockage", "incident_capacity_drop", "spillback_stress"]):
                mechanism = apply_failure_mode(step, warmup, target_edge, original_speed)
                failure_mode_active = warmup <= step < warmup + 120 and target_edge is not None
                if mechanism:
                    failure_mode_mechanism = mechanism
            if any(token in scenario_tag for token in ["demand_shift", "turning_shock", "oversaturation"]):
                mechanism = demand_shift_tick(step, warmup, route_ids, inserted)
                if mechanism:
                    demand_shift_mechanism = mechanism
            if "switching_loss_sensitive" in scenario_tag:
                failure_mode_mechanism = None
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
                    previous_phase = last_phase_by_tls.get(tls_id)
                    if previous_phase is None:
                        last_phase_by_tls[tls_id] = current_phase
                        phase_since_by_tls[tls_id] = step - action_interval
                    elif previous_phase != current_phase:
                        phase_since_by_tls[tls_id] = step
                        last_phase_by_tls[tls_id] = current_phase
                        if target_phase_by_tls.get(tls_id) == current_phase:
                            switching_count += 1
                    latest_time_since_switch = float(step - phase_since_by_tls.get(tls_id, step - action_interval))
                    if controller in FINITE_STORAGE_CONTROLLER_IDS:
                        decision_state = build_completed_finite_storage_state(
                            queues,
                            capacities,
                            current_phase=current_phase,
                            time_since_switch=latest_time_since_switch,
                            incident_edge=target_edge if failure_mode_active else None,
                            capacity_drop_factor=0.35 if failure_mode_active else None,
                        )
                        audit = select_finite_storage_action_with_audit(
                            tls_id,
                            current_phase,
                            phase_states,
                            tls_movements,
                            queues,
                            capacities,
                            decision_state,
                            seed,
                            controller=controller,
                        )
                        latest_action_decomposition_by_tls[tls_id] = audit
                        action = int(audit["selected_action"])
                    else:
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
        "sumocfg": str(sumocfg_path),
        "base_sumocfg": str(paths["sumocfg"]),
        "net_file": str(paths["net_file"]),
        **route_metadata,
        **aggregate_metrics(observations, steps, warmup, departed, arrived_times, waiting_delay, controller_runtime, switching_count),
        "finite_storage_state": build_completed_finite_storage_state(
            latest_queues,
            capacities,
            current_phase=latest_current_phase,
            time_since_switch=latest_time_since_switch,
            incident_edge=target_edge if failure_mode_active else None,
            capacity_drop_factor=0.35 if failure_mode_active else None,
        ),
        **stress_metadata,
    }
    if controller in FINITE_STORAGE_CONTROLLER_IDS:
        row["action_decomposition"] = {
            "controller": controller,
            "decision_scope": "last_action_decision_per_tls",
            "last_decision_by_tls": latest_action_decomposition_by_tls,
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
