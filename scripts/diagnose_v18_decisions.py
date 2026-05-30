#!/usr/bin/env python3
"""Diagnostic: compare v1.8 vs max_pressure per-decision on the same scenario.

Runs arterial_v1_5_storage_activation (seed=20261801) with both controllers,
captures every decision step, and outputs a merged diagnostic JSON showing
where they agree and where v1.8 deviates, along with dual-price breakdowns
that explain each deviation.

Usage:
    python scripts/diagnose_v18_decisions.py
    python scripts/diagnose_v18_decisions.py --out experiments/dual_sensitivity/v1_8_decision_diagnostic.json
"""
from __future__ import annotations

import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import traci

# Ensure scripts/ is on the import path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sample_sumo_states import build_network_metadata

# ---------------------------------------------------------------------------
# Reuse key functions from run_closed_loop_sumo.py without importing the
# whole module (it has top-level side-effects like CONTROLLER_REGISTRY).
# ---------------------------------------------------------------------------
from run_closed_loop_sumo import (
    NETWORKS,
    build_completed_finite_storage_state,
    build_downstream_adjacency,
    choose_controller_action,
    edge_observation,
    green_phases,
    initialize_dynamic_dual_state,
    phase_score,
    read_edge_free_flow_times,
    read_edge_speeds,
    read_tls_link_movements,
    read_tls_phase_states,
    resolve_network,
    scenario_effective_capacity_scale,
    scenario_stress_metadata,
    select_failure_edge,
    select_finite_storage_action_with_audit,
    update_completion_dual_state,
    update_dynamic_dual_state,
    DYNAMIC_V1_8_RC_CFS_PD_MPC_PARAMS,
    V1_8_CONTROLLER_IDS,
    FINITE_STORAGE_CONTROLLER_IDS,
    build_active_route_completion_state,
    unavailable_route_completion_state,
    DYNAMIC_V1_5_CONTROLLER_IDS,
    build_completion_state,
    state_storage_summary,
)

SCENARIO_TAG = "arterial_v1_5_storage_activation"
NETWORK = "arterial"
SEED = 20261801
STEPS = 3600
WARMUP = 900
ACTION_INTERVAL = 10

SUMOCFG = Path(
    "experiments/dual_sensitivity/v1_8_training_scaled_inputs/"
    "phase11_arterial_demand_1p0.sumocfg"
)


def _queue_snapshot(edge_ids: list[str]) -> dict[str, float]:
    """Capture current queue state from TraCI."""
    return {eid: float(traci.edge.getLastStepHaltingNumber(eid)) for eid in edge_ids}


def _vehicle_count_snapshot(edge_ids: list[str]) -> dict[str, float]:
    return {eid: float(traci.edge.getLastStepVehicleNumber(eid)) for eid in edge_ids}


def run_max_pressure_with_trace(
    network: str,
    seed: int,
    steps: int,
    warmup: int,
    action_interval: int,
    sumocfg_override: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run max_pressure and collect per-decision trace."""
    paths = resolve_network(network)
    sumocfg_path = Path(sumocfg_override)
    metadata = build_network_metadata(paths["net_file"])
    capacities = {str(k): float(v) for k, v in metadata["edge_capacity"].items()}
    effective_capacity_scale = scenario_effective_capacity_scale(SCENARIO_TAG)
    if effective_capacity_scale != 1.0:
        capacities = {
            edge: max(value * effective_capacity_scale, 1.0)
            for edge, value in capacities.items()
        }
    tls_movements = read_tls_link_movements(paths["net_file"])
    phase_states = read_tls_phase_states(paths["net_file"])
    edge_ids = sorted(capacities)

    cmd = [
        "sumo", "-c", str(sumocfg_path),
        "--seed", str(seed),
        "--no-step-log", "true",
        "--duration-log.disable", "true",
    ]
    traci.start(cmd)

    last_phase_by_tls: dict[str, int] = {}
    target_phase_by_tls: dict[str, int] = {}
    phase_since_by_tls: dict[str, int] = {}
    decision_trace: list[dict[str, Any]] = []

    try:
        for step in range(steps):
            traci.simulationStep()
            if step >= warmup and (step - warmup) % action_interval == 0:
                queues = _queue_snapshot(edge_ids)
                vehicle_counts = _vehicle_count_snapshot(edge_ids)
                for tls_id in sorted(tls_movements):
                    current_phase = int(traci.trafficlight.getPhase(tls_id))
                    previous_phase = last_phase_by_tls.get(tls_id)
                    if previous_phase is None:
                        last_phase_by_tls[tls_id] = current_phase
                        phase_since_by_tls[tls_id] = step - action_interval
                    elif previous_phase != current_phase:
                        phase_since_by_tls[tls_id] = step
                        last_phase_by_tls[tls_id] = current_phase

                    states = phase_states.get(tls_id, [])
                    greens = green_phases(states)
                    scored_phases = {}
                    for phase_idx in greens:
                        s = phase_score(
                            "max_pressure", phase_idx, states,
                            tls_movements.get(tls_id, []),
                            queues, capacities, seed,
                            vehicle_counts=vehicle_counts,
                        )
                        scored_phases[phase_idx] = s

                    best_phase = max(scored_phases, key=scored_phases.get) if scored_phases else current_phase

                    decision_trace.append({
                        "step": int(step),
                        "tls_id": str(tls_id),
                        "current_phase": int(current_phase),
                        "selected_action": int(best_phase),
                        "phase_scores": {str(k): float(v) for k, v in scored_phases.items()},
                        "queues": {str(k): float(v) for k, v in queues.items()},
                    })

                    # Apply the action
                    target_phase_by_tls.setdefault(tls_id, current_phase)
                    n_phases = max(len(states), 1)
                    current_state = states[current_phase] if current_phase < len(states) else ""
                    current_is_green = any(ch in "Gg" for ch in current_state)
                    phase_since = phase_since_by_tls.get(tls_id, step - action_interval)
                    if current_is_green and best_phase != current_phase and step - phase_since >= action_interval:
                        target_phase_by_tls[tls_id] = int(best_phase)
                    target = target_phase_by_tls.get(tls_id, current_phase)
                    if target != current_phase:
                        next_phase = (current_phase + 1) % n_phases
                        traci.trafficlight.setPhase(tls_id, int(next_phase))
                        phase_since_by_tls[tls_id] = step
                        if next_phase == target:
                            target_phase_by_tls[tls_id] = next_phase
                        last_phase_by_tls[tls_id] = int(next_phase)
    finally:
        traci.close(False)

    return {"controller": "max_pressure", "steps": steps, "warmup": warmup}, decision_trace


def run_v18_with_trace(
    network: str,
    seed: int,
    steps: int,
    warmup: int,
    action_interval: int,
    sumocfg_override: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run v1.8 controller and collect per-decision trace with dual breakdown."""
    paths = resolve_network(network)
    sumocfg_path = Path(sumocfg_override)
    metadata = build_network_metadata(paths["net_file"])
    capacities = {str(k): float(v) for k, v in metadata["edge_capacity"].items()}
    effective_capacity_scale = scenario_effective_capacity_scale(SCENARIO_TAG)
    if effective_capacity_scale != 1.0:
        capacities = {
            edge: max(value * effective_capacity_scale, 1.0)
            for edge, value in capacities.items()
        }
    tls_movements = read_tls_link_movements(paths["net_file"])
    phase_states = read_tls_phase_states(paths["net_file"])
    edge_ids = sorted(capacities)
    downstream_adjacency = build_downstream_adjacency(tls_movements)
    dynamic_dual_state = initialize_dynamic_dual_state(edge_ids)
    edge_speeds = read_edge_speeds(paths["net_file"])
    edge_free_flow_times = read_edge_free_flow_times(paths["net_file"])
    target_edge = select_failure_edge(edge_ids, tls_movements)

    cmd = [
        "sumo", "-c", str(sumocfg_path),
        "--seed", str(seed),
        "--no-step-log", "true",
        "--duration-log.disable", "true",
    ]
    traci.start(cmd)

    last_phase_by_tls: dict[str, int] = {}
    target_phase_by_tls: dict[str, int] = {}
    phase_since_by_tls: dict[str, int] = {}
    decision_trace: list[dict[str, Any]] = []

    try:
        for step in range(steps):
            traci.simulationStep()
            if step >= warmup and (step - warmup) % action_interval == 0:
                queues = _queue_snapshot(edge_ids)
                vehicle_counts = _vehicle_count_snapshot(edge_ids)

                # Update dual state (same as run_experiment)
                interval_state = build_completed_finite_storage_state(
                    queues, capacities,
                    vehicle_counts=vehicle_counts,
                    current_phase=None,
                    time_since_switch=float(action_interval),
                    incident_edge=None,
                    capacity_drop_factor=None,
                )
                update_dynamic_dual_state(
                    dynamic_dual_state, interval_state,
                    downstream_adjacency,
                    params=DYNAMIC_V1_8_RC_CFS_PD_MPC_PARAMS,
                )
                update_completion_dual_state(
                    dynamic_dual_state, interval_state,
                    step=step, warmup=warmup, steps=steps,
                    params=DYNAMIC_V1_8_RC_CFS_PD_MPC_PARAMS,
                )
                route_completion_state = unavailable_route_completion_state()

                for tls_id in sorted(tls_movements):
                    current_phase = int(traci.trafficlight.getPhase(tls_id))
                    previous_phase = last_phase_by_tls.get(tls_id)
                    if previous_phase is None:
                        last_phase_by_tls[tls_id] = current_phase
                        phase_since_by_tls[tls_id] = step - action_interval
                    elif previous_phase != current_phase:
                        phase_since_by_tls[tls_id] = step
                        last_phase_by_tls[tls_id] = current_phase

                    time_since_switch = float(
                        step - phase_since_by_tls.get(tls_id, step - action_interval)
                    )

                    decision_state = build_completed_finite_storage_state(
                        queues, capacities,
                        vehicle_counts=vehicle_counts,
                        current_phase=current_phase,
                        time_since_switch=time_since_switch,
                        incident_edge=None,
                        capacity_drop_factor=None,
                    )
                    completion_state = build_completion_state(
                        decision_state, queues, capacities,
                        downstream_adjacency,
                        step=step, warmup=warmup, steps=steps,
                    )

                    audit = select_finite_storage_action_with_audit(
                        tls_id, current_phase, phase_states, tls_movements,
                        queues, capacities, decision_state, seed,
                        controller="finite_storage_regime_calibrated_cfs_pd_mpc_v1_8",
                        dynamic_dual_state=dynamic_dual_state,
                        route_completion_state=route_completion_state,
                        step=step, warmup=warmup, steps=steps,
                        vehicle_counts=vehicle_counts,
                        completion_state=completion_state,
                        downstream_adjacency=downstream_adjacency,
                        effective_capacity_scale=effective_capacity_scale,
                        phase_since_step=phase_since_by_tls.get(tls_id, step - action_interval),
                        action_interval=action_interval,
                    )

                    # Compute max_pressure's choice for comparison
                    states = phase_states.get(tls_id, [])
                    greens = green_phases(states)
                    mp_scores = {}
                    for phase_idx in greens:
                        s = phase_score(
                            "max_pressure", phase_idx, states,
                            tls_movements.get(tls_id, []),
                            queues, capacities, seed,
                            vehicle_counts=vehicle_counts,
                        )
                        mp_scores[phase_idx] = s
                    mp_choice = max(mp_scores, key=mp_scores.get) if mp_scores else current_phase
                    mp_best_score = mp_scores.get(mp_choice, 0.0)

                    storage = state_storage_summary(decision_state)

                    decision_trace.append({
                        "step": int(step),
                        "tls_id": str(tls_id),
                        "current_phase": int(current_phase),
                        "v18_selected_action": int(audit["selected_action"]),
                        "v18_pressure_action": int(audit["pressure_action"]),
                        "v18_phase_scores": {
                            str(k): float(v)
                            for k, v in audit.get("phase_scores", {}).items()
                        },
                        "v18_regime": str(audit.get("regime", "")),
                        "v18_regime_scores": (
                            dict(audit.get("regime_info", {}).get("scores", {}))
                            if isinstance(audit.get("regime_info"), dict) else {}
                        ),
                        "v18_dual_components": {
                            str(k): dict(v) if isinstance(v, dict) else v
                            for k, v in audit.get("dual_components", {}).items()
                        },
                        "v18_predicted_J_H": dict(audit.get("predicted_J_H", {})),
                        "v18_predicted_unfinished_risk_H": dict(audit.get("predicted_unfinished_risk_H", {})),
                        "v18_predicted_spillback_risk_H": dict(audit.get("predicted_spillback_risk_H", {})),
                        "v18_safe_set": list(audit.get("safe_set", [])),
                        "v18_advantage": float(audit.get("advantage", 0.0)),
                        "v18_advantage_gate_active": bool(audit.get("advantage_gate_active", False)),
                        "v18_baseline_scores_max_pressure": {
                            str(k): float(v)
                            for k, v in audit.get("baseline_scores", {}).get("max_pressure", {}).items()
                        },
                        "max_pressure_choice": int(mp_choice),
                        "max_pressure_best_score": float(mp_best_score),
                        "max_pressure_all_scores": {
                            str(k): float(v) for k, v in mp_scores.items()
                        },
                        "agree": int(audit["selected_action"]) == int(mp_choice),
                        "queues": {str(k): float(v) for k, v in queues.items()},
                        "max_occupancy_ratio": float(storage["max_occupancy_ratio"]),
                        "min_residual_ratio": float(storage["min_residual_ratio"]),
                    })

                    # Apply the action
                    action = int(audit["selected_action"])
                    target_phase_by_tls.setdefault(tls_id, current_phase)
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
                            target_phase_by_tls[tls_id] = next_phase
                        last_phase_by_tls[tls_id] = int(next_phase)
    finally:
        traci.close(False)

    return {
        "controller": "finite_storage_regime_calibrated_cfs_pd_mpc_v1_8",
        "steps": steps,
        "warmup": warmup,
    }, decision_trace


def merge_traces(
    mp_trace: list[dict[str, Any]],
    v18_trace: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge two traces on (step, tls_id) and produce a unified comparison."""
    mp_index = {
        (r["step"], r["tls_id"]): r for r in mp_trace
    }

    merged: list[dict[str, Any]] = []
    for v18_row in v18_trace:
        key = (v18_row["step"], v18_row["tls_id"])
        mp_row = mp_index.get(key)
        if mp_row is None:
            continue

        agree = v18_row["agree"]

        merged.append({
            "step": v18_row["step"],
            "tls_id": v18_row["tls_id"],
            "current_phase": v18_row["current_phase"],
            "max_pressure_choice": mp_row["selected_action"],
            "max_pressure_scores": mp_row["phase_scores"],
            "v18_choice": v18_row["v18_selected_action"],
            "v18_internal_pressure_action": v18_row["v18_pressure_action"],
            "v18_phase_scores": v18_row["v18_phase_scores"],
            "v18_regime": v18_row["v18_regime"],
            "v18_regime_scores": v18_row["v18_regime_scores"],
            "v18_dual_components": v18_row["v18_dual_components"],
            "v18_predicted_J_H": v18_row["v18_predicted_J_H"],
            "v18_predicted_unfinished_risk_H": v18_row["v18_predicted_unfinished_risk_H"],
            "v18_predicted_spillback_risk_H": v18_row["v18_predicted_spillback_risk_H"],
            "v18_safe_set": v18_row["v18_safe_set"],
            "v18_advantage": v18_row["v18_advantage"],
            "v18_advantage_gate_active": v18_row["v18_advantage_gate_active"],
            "v18_baseline_mp_scores": v18_row["v18_baseline_scores_max_pressure"],
            "agree": agree,
            "queues": v18_row["queues"],
            "max_occupancy_ratio": v18_row["max_occupancy_ratio"],
            "min_residual_ratio": v18_row["min_residual_ratio"],
        })

    return merged


def summarize(merged: list[dict[str, Any]]) -> dict[str, Any]:
    """Produce a high-level summary of agreement/disagreement patterns."""
    total = len(merged)
    agree_count = sum(1 for r in merged if r["agree"])
    disagree_count = total - agree_count

    # Per-TLS breakdown
    tls_breakdown: dict[str, dict[str, int]] = {}
    for r in merged:
        tls = r["tls_id"]
        tls_breakdown.setdefault(tls, {"agree": 0, "disagree": 0, "total": 0})
        tls_breakdown[tls]["total"] += 1
        if r["agree"]:
            tls_breakdown[tls]["agree"] += 1
        else:
            tls_breakdown[tls]["disagree"] += 1

    # Regime breakdown for disagreements
    regime_disagree: dict[str, int] = {}
    regime_agree: dict[str, int] = {}
    for r in merged:
        regime = r["v18_regime"]
        if r["agree"]:
            regime_agree[regime] = regime_agree.get(regime, 0) + 1
        else:
            regime_disagree[regime] = regime_disagree.get(regime, 0) + 1

    # --- Safe set analysis ---
    # The safe_set from baseline_envelope_safe_selection filters phases whose
    # predicted_unfinished_risk exceeds the best baseline risk + eps_u.
    # When only one phase survives, phase_scores are irrelevant.
    safe_set_constrained = 0
    safe_set_single_phase: dict[int, int] = {}
    safe_set_all_phases = 0
    safe_set_constrained_agree = 0
    safe_set_constrained_disagree = 0
    safe_set_free_agree = 0
    safe_set_free_disagree = 0
    for r in merged:
        available_phases = sorted(r.get("v18_phase_scores", {}).keys())
        safe = r.get("v18_safe_set", [])
        if len(safe) <= 1:
            safe_set_constrained += 1
            if safe:
                safe_set_single_phase[safe[0]] = safe_set_single_phase.get(safe[0], 0) + 1
            if r["agree"]:
                safe_set_constrained_agree += 1
            else:
                safe_set_constrained_disagree += 1
        else:
            safe_set_all_phases += 1
            if r["agree"]:
                safe_set_free_agree += 1
            else:
                safe_set_free_disagree += 1

    # Phase switch patterns in disagreements (using internal pressure action)
    disagree_switches: list[dict[str, Any]] = []
    for r in merged:
        if not r["agree"]:
            mp_int = r["v18_internal_pressure_action"]
            v18_choice = r["v18_choice"]
            mp_score = float(r["max_pressure_scores"].get(str(mp_int), 0.0))
            v18_score = float(r["v18_phase_scores"].get(str(v18_choice), 0.0))
            # Decompose v18 dual components for the chosen phase
            v18_dual = r["v18_dual_components"].get(str(v18_choice), {})
            mp_dual = r["v18_dual_components"].get(str(mp_int), {})

            # Compute dual-component deltas to understand the tipping factor
            all_component_keys = sorted(set(list(v18_dual.keys()) + list(mp_dual.keys())))
            component_deltas = {
                k: float(v18_dual.get(k, 0.0)) - float(mp_dual.get(k, 0.0))
                for k in all_component_keys
            }

            disagree_switches.append({
                "step": r["step"],
                "tls_id": r["tls_id"],
                "internal_mp_phase": mp_int,
                "v18_choice_phase": v18_choice,
                "max_pressure_pressure_score": mp_score,
                "v18_phase_total_score": v18_score,
                "v18_chosen_dual_breakdown": v18_dual,
                "v18_mp_phase_dual_breakdown": mp_dual,
                "component_deltas_v18_minus_mp": component_deltas,
                "v18_regime": r["v18_regime"],
                "v18_regime_scores": r["v18_regime_scores"],
                "v18_safe_set": r.get("v18_safe_set", []),
                "v18_advantage": r.get("v18_advantage", 0.0),
                "v18_advantage_gate_active": r.get("v18_advantage_gate_active", False),
                "v18_predicted_J_H_chosen": r.get("v18_predicted_J_H", {}).get(str(v18_choice), 0.0),
                "v18_predicted_J_H_mp": r.get("v18_predicted_J_H", {}).get(str(mp_int), 0.0),
                "v18_predicted_unfinished_risk_chosen": r.get("v18_predicted_unfinished_risk_H", {}).get(str(v18_choice), 0.0),
                "v18_predicted_unfinished_risk_mp": r.get("v18_predicted_unfinished_risk_H", {}).get(str(mp_int), 0.0),
                "max_occupancy_ratio": r["max_occupancy_ratio"],
                "min_residual_ratio": r["min_residual_ratio"],
            })

    # Aggregate component delta analysis over all disagreements
    disagree = [r for r in merged if not r["agree"]]
    component_delta_totals: dict[str, dict[str, float]] = {}
    for r in disagree:
        mp_int = r["v18_internal_pressure_action"]
        v18_choice = r["v18_choice"]
        v18_dual = r["v18_dual_components"].get(str(v18_choice), {})
        mp_dual = r["v18_dual_components"].get(str(mp_int), {})
        all_keys = sorted(set(list(v18_dual.keys()) + list(mp_dual.keys())))
        for k in all_keys:
            delta = float(v18_dual.get(k, 0.0)) - float(mp_dual.get(k, 0.0))
            if k not in component_delta_totals:
                component_delta_totals[k] = {
                    "total_delta": 0.0,
                    "favor_v18_count": 0,
                    "favor_mp_count": 0,
                }
            component_delta_totals[k]["total_delta"] += delta
            if delta > 0:
                component_delta_totals[k]["favor_v18_count"] += 1
            elif delta < 0:
                component_delta_totals[k]["favor_mp_count"] += 1

    return {
        "total_decisions": total,
        "agree_count": agree_count,
        "disagree_count": disagree_count,
        "agreement_rate": float(agree_count / total) if total > 0 else 0.0,
        "tls_breakdown": tls_breakdown,
        "regime_agree_counts": regime_agree,
        "regime_disagree_counts": regime_disagree,
        "safe_set_analysis": {
            "single_phase_constrained": safe_set_constrained,
            "all_phases_available": safe_set_all_phases,
            "single_phase_distribution": safe_set_single_phase,
            "constrained_agree": safe_set_constrained_agree,
            "constrained_disagree": safe_set_constrained_disagree,
            "free_agree": safe_set_free_agree,
            "free_disagree": safe_set_free_disagree,
            "note": (
                "When safe_set has one phase, v18 is forced to that phase regardless "
                "of phase_scores. When safe_set has all phases, v18 and mp always agree."
            ),
        },
        "component_delta_analysis": {
            "note": (
                "Delta = v18_chosen_phase_component - mp_phase_component. "
                "Negative pressure delta means mp_phase has higher raw pressure. "
                "Positive storage_correction/release_bonus delta means v18_phase "
                "gains more from dual corrections."
            ),
            "components": component_delta_totals,
        },
        "disagreement_sample": disagree_switches[:80],
    }


def main() -> None:
    out_path = Path(
        "experiments/dual_sensitivity/v1_8_decision_diagnostic.json"
    )
    if not SUMOCFG.exists():
        print(json.dumps({"error": f"sumocfg not found: {SUMOCFG}", "status": "FAILED"}))
        sys.exit(1)

    print(json.dumps({"phase": "max_pressure", "status": "starting"}))
    t0 = time.perf_counter()
    mp_meta, mp_trace = run_max_pressure_with_trace(
        NETWORK, SEED, STEPS, WARMUP, ACTION_INTERVAL, SUMOCFG,
    )
    mp_elapsed = time.perf_counter() - t0
    print(json.dumps({
        "phase": "max_pressure",
        "status": "completed",
        "decisions": len(mp_trace),
        "elapsed_sec": round(mp_elapsed, 2),
    }))

    print(json.dumps({"phase": "v1.8", "status": "starting"}))
    t0 = time.perf_counter()
    v18_meta, v18_trace = run_v18_with_trace(
        NETWORK, SEED, STEPS, WARMUP, ACTION_INTERVAL, SUMOCFG,
    )
    v18_elapsed = time.perf_counter() - t0
    print(json.dumps({
        "phase": "v1.8",
        "status": "completed",
        "decisions": len(v18_trace),
        "elapsed_sec": round(v18_elapsed, 2),
    }))

    merged = merge_traces(mp_trace, v18_trace)
    summary = summarize(merged)

    payload = {
        "experiment": "v1_8_decision_diagnostic",
        "scenario_tag": SCENARIO_TAG,
        "network": NETWORK,
        "seed": SEED,
        "steps": STEPS,
        "warmup": WARMUP,
        "action_interval": ACTION_INTERVAL,
        "sumocfg": str(SUMOCFG),
        "controllers": ["max_pressure", "finite_storage_regime_calibrated_cfs_pd_mpc_v1_8"],
        "max_pressure_runtime_sec": round(mp_elapsed, 2),
        "v18_runtime_sec": round(v18_elapsed, 2),
        "summary": summary,
        "merged_decisions": merged,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "DONE",
        "out": str(out_path),
        "total_decisions": len(merged),
        "agreement_rate": summary["agreement_rate"],
        "disagree_count": summary["disagree_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
