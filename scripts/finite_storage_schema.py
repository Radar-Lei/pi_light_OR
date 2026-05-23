#!/usr/bin/env python3
"""Explicit finite-storage state and objective-component schema helpers."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

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
DEFAULT_SWITCHING_LOST_TIME_PER_SWITCH = 2.0


def _context(path: Path | None, sample_idx: int | None) -> str:
    parts = []
    if sample_idx is not None:
        parts.append(f"Sample {sample_idx}")
    if path is not None:
        parts.append(f"in {path}")
    if not parts:
        return "Artifact"
    return " ".join(parts)


def _require_object(value: Any, field: str, *, path: Path | None, sample_idx: int | None) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{_context(path, sample_idx)} field {field} must be an object")
    return value


def _require_finite_number(value: Any, field: str, *, path: Path | None, sample_idx: int | None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{_context(path, sample_idx)} field {field} must be a finite number")
    return float(value)


def _validate_numeric_mapping(
    mapping: Any,
    field: str,
    *,
    path: Path | None,
    sample_idx: int | None,
    allow_bool: bool = False,
) -> None:
    obj = _require_object(mapping, field, path=path, sample_idx=sample_idx)
    for key, value in obj.items():
        item_field = f"{field}.{key}"
        if allow_bool and isinstance(value, bool):
            continue
        _require_finite_number(value, item_field, path=path, sample_idx=sample_idx)


def _validate_spillback_blocking(value: Any, *, path: Path | None, sample_idx: int | None) -> None:
    mapping = _require_object(value, "spillback_blocking", path=path, sample_idx=sample_idx)
    for edge, flags in mapping.items():
        field = f"spillback_blocking.{edge}"
        if isinstance(flags, bool):
            continue
        flag_obj = _require_object(flags, field, path=path, sample_idx=sample_idx)
        for name in ["spillback", "blocking"]:
            if name not in flag_obj:
                raise ValueError(f"{_context(path, sample_idx)} field {field}.{name} is required")
            if not isinstance(flag_obj[name], bool):
                raise ValueError(f"{_context(path, sample_idx)} field {field}.{name} must be a boolean")
        if "occupancy_ratio" in flag_obj:
            _require_finite_number(flag_obj["occupancy_ratio"], f"{field}.occupancy_ratio", path=path, sample_idx=sample_idx)


def validate_finite_storage_state(state: dict[str, Any], *, path: Path | None = None, sample_idx: int | None = None) -> None:
    if not isinstance(state, dict):
        raise ValueError(f"{_context(path, sample_idx)} field finite_storage_state must be an object")
    missing = FINITE_STORAGE_STATE_FIELDS - set(state)
    if missing:
        raise ValueError(f"{_context(path, sample_idx)} finite_storage_state is missing fields: {sorted(missing)}")

    _validate_numeric_mapping(state["downstream_storage"], "finite_storage_state.downstream_storage", path=path, sample_idx=sample_idx)
    _validate_numeric_mapping(
        state["residual_receiving_capacity"],
        "finite_storage_state.residual_receiving_capacity",
        path=path,
        sample_idx=sample_idx,
    )
    _validate_spillback_blocking(state["spillback_blocking"], path=path, sample_idx=sample_idx)
    _validate_numeric_mapping(state["service_urgency"], "finite_storage_state.service_urgency", path=path, sample_idx=sample_idx)

    switching = _require_object(
        state["switching_loss_state"],
        "finite_storage_state.switching_loss_state",
        path=path,
        sample_idx=sample_idx,
    )
    if "current_phase" not in switching:
        raise ValueError(f"{_context(path, sample_idx)} field switching_loss_state.current_phase is required")
    if switching["current_phase"] is not None:
        _require_finite_number(
            switching["current_phase"],
            "finite_storage_state.switching_loss_state.current_phase",
            path=path,
            sample_idx=sample_idx,
        )
    _require_finite_number(
        switching.get("time_since_switch"),
        "finite_storage_state.switching_loss_state.time_since_switch",
        path=path,
        sample_idx=sample_idx,
    )

    incident = _require_object(
        state["incident_capacity_drop"],
        "finite_storage_state.incident_capacity_drop",
        path=path,
        sample_idx=sample_idx,
    )
    for field in ["active", "edge", "factor"]:
        if field not in incident:
            raise ValueError(f"{_context(path, sample_idx)} field incident_capacity_drop.{field} is required")
    if not isinstance(incident["active"], bool):
        raise ValueError(f"{_context(path, sample_idx)} field incident_capacity_drop.active must be a boolean")
    if incident["edge"] is not None and not isinstance(incident["edge"], str):
        raise ValueError(f"{_context(path, sample_idx)} field incident_capacity_drop.edge must be a string or null")
    factor = _require_finite_number(
        incident["factor"],
        "finite_storage_state.incident_capacity_drop.factor",
        path=path,
        sample_idx=sample_idx,
    )
    if factor < 0.0:
        raise ValueError(f"{_context(path, sample_idx)} field incident_capacity_drop.factor must be nonnegative")


def validate_objective_components(
    components: dict[str, Any], *, path: Path | None = None, sample_idx: int | None = None
) -> None:
    if not isinstance(components, dict):
        raise ValueError(f"{_context(path, sample_idx)} field objective_components must be an object")
    missing = OBJECTIVE_COMPONENT_FIELDS - set(components)
    if missing:
        raise ValueError(f"{_context(path, sample_idx)} objective_components is missing fields: {sorted(missing)}")
    for field in OBJECTIVE_COMPONENT_FIELDS:
        component = _require_finite_number(components[field], f"objective_components.{field}", path=path, sample_idx=sample_idx)
        if component < 0.0:
            raise ValueError(f"{_context(path, sample_idx)} field objective_components.{field} must be nonnegative")


def validate_state_objective_sample(
    sample: dict[str, Any], *, path: Path | None = None, sample_idx: int | None = None
) -> None:
    if not isinstance(sample, dict):
        raise ValueError(f"{_context(path, sample_idx)} sample must be an object")
    for field in ["finite_storage_state", "objective_components"]:
        if field not in sample:
            raise ValueError(f"{_context(path, sample_idx)} is missing required field {field}")
    validate_finite_storage_state(sample["finite_storage_state"], path=path, sample_idx=sample_idx)
    validate_objective_components(sample["objective_components"], path=path, sample_idx=sample_idx)


def build_finite_storage_state(
    queues: dict[str, float],
    capacities: dict[str, float],
    *,
    current_phase: int | None = None,
    time_since_switch: float | None = None,
    incident_edge: str | None = None,
    capacity_drop_factor: float | None = None,
) -> dict[str, Any]:
    normalized_capacities = {edge: max(float(capacity), 0.0) for edge, capacity in capacities.items()}
    normalized_queues = {edge: max(float(queues.get(edge, 0.0)), 0.0) for edge in normalized_capacities}
    residual = {
        edge: max(capacity - normalized_queues.get(edge, 0.0), 0.0)
        for edge, capacity in normalized_capacities.items()
    }
    spillback_blocking = {}
    service_urgency = {}
    for edge, capacity in normalized_capacities.items():
        denominator = max(capacity, 1.0)
        occupancy_ratio = normalized_queues.get(edge, 0.0) / denominator
        spillback = occupancy_ratio >= 0.85
        blocking = spillback and normalized_queues.get(edge, 0.0) > 0.0 and residual[edge] <= 0.15 * denominator
        spillback_blocking[edge] = {
            "spillback": bool(spillback),
            "blocking": bool(blocking),
            "occupancy_ratio": float(occupancy_ratio),
        }
        service_urgency[edge] = float(occupancy_ratio)

    factor = 1.0 if capacity_drop_factor is None else float(capacity_drop_factor)
    state = {
        "downstream_storage": {edge: float(value) for edge, value in normalized_capacities.items()},
        "residual_receiving_capacity": {edge: float(value) for edge, value in residual.items()},
        "spillback_blocking": spillback_blocking,
        "switching_loss_state": {
            "current_phase": current_phase,
            "time_since_switch": float(0.0 if time_since_switch is None else time_since_switch),
        },
        "service_urgency": service_urgency,
        "incident_capacity_drop": {
            "active": incident_edge is not None,
            "edge": incident_edge,
            "factor": factor,
        },
    }
    validate_finite_storage_state(state)
    return state


def _metric_value(metrics: dict[str, Any], *names: str, default: float = 0.0) -> float:
    for name in names:
        if name in metrics and metrics[name] is not None:
            return _require_finite_number(metrics[name], name, path=None, sample_idx=None)
    return float(default)


def build_objective_components_from_metrics(
    metrics: dict[str, Any], *, horizon: float = 1.0, switching_lost_time_per_switch: float = DEFAULT_SWITCHING_LOST_TIME_PER_SWITCH
) -> dict[str, float]:
    safe_horizon = _require_finite_number(horizon, "horizon", path=None, sample_idx=None)
    if safe_horizon <= 0.0:
        raise ValueError("Artifact field horizon must be positive")
    safe_switching_lost_time = _require_finite_number(
        switching_lost_time_per_switch,
        "switching_lost_time_per_switch",
        path=None,
        sample_idx=None,
    )
    if safe_switching_lost_time < 0.0:
        raise ValueError("Artifact field switching_lost_time_per_switch must be nonnegative")

    delay = _metric_value(metrics, "delay", "total_delay")
    unfinished = _metric_value(metrics, "unfinished_vehicle_count", "unfinished_vehicles")
    spillback_blocking_count = _metric_value(metrics, "spillback_blocking_count", default=-1.0)
    if spillback_blocking_count < 0.0:
        spillback_blocking_count = _metric_value(metrics, "spillback_count") + _metric_value(metrics, "blocking_count")
    switching_count = _metric_value(metrics, "switching_count")

    components = {
        "delay": float(delay),
        "unfinished_vehicle_penalty": float(unfinished * safe_horizon),
        "spillback_blocking_time": float(spillback_blocking_count * safe_horizon),
        "switching_lost_time": float(switching_count * safe_switching_lost_time),
    }
    validate_objective_components(components)
    return components


def build_objective_components(
    queues: dict[str, float],
    *,
    unfinished_vehicle_count: int = 0,
    spillback_blocking_count: int = 0,
    switching_count: int = 0,
    horizon: float = 1.0,
    switching_lost_time_per_switch: float = DEFAULT_SWITCHING_LOST_TIME_PER_SWITCH,
) -> dict[str, float]:
    delay = sum(max(float(value), 0.0) for value in queues.values())
    return build_objective_components_from_metrics(
        {
            "total_delay": delay,
            "unfinished_vehicle_count": unfinished_vehicle_count,
            "spillback_blocking_count": spillback_blocking_count,
            "switching_count": switching_count,
        },
        horizon=horizon,
        switching_lost_time_per_switch=switching_lost_time_per_switch,
    )


def schema_artifact_payload() -> dict[str, Any]:
    return {
        "experiment": "phase6_explicit_state_schema",
        "status": "PASSED",
        "generated_by": "scripts/finite_storage_schema.py",
        "requirements_covered": ["STATE-01", "STATE-02"],
        "schema_version": SCHEMA_VERSION,
        "finite_storage_state_fields": sorted(FINITE_STORAGE_STATE_FIELDS),
        "objective_component_fields": sorted(OBJECTIVE_COMPONENT_FIELDS),
        "finite_storage_state_contract": {
            "downstream_storage": "edge -> finite storage capacity",
            "residual_receiving_capacity": "edge -> max(storage - queue, 0)",
            "spillback_blocking": "edge -> explicit spillback/blocking indicators and occupancy ratio",
            "switching_loss_state": "current_phase plus time_since_switch",
            "service_urgency": "edge -> queue-derived urgency ratio",
            "incident_capacity_drop": "active flag, affected edge, and remaining capacity factor",
        },
        "objective_formula_metadata": {
            "shared_builder": "build_objective_components_from_metrics",
            "delay": "metrics.delay or metrics.total_delay",
            "unfinished_vehicle_penalty": "unfinished_vehicle_count * horizon",
            "spillback_blocking_time": "spillback_blocking_count * horizon, or (spillback_count + blocking_count) * horizon",
            "switching_lost_time": "switching_count * switching_lost_time_per_switch",
            "default_switching_lost_time_per_switch": DEFAULT_SWITCHING_LOST_TIME_PER_SWITCH,
        },
        "legacy_proxy_note": (
            "Old v1.0 proxy fields and regime labels are historical/insufficient for v1.1 "
            "binding-regime superiority evidence unless finite_storage_state and objective_components validate."
        ),
    }


def write_schema_artifact(path: Path) -> dict[str, Any]:
    payload = schema_artifact_payload()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
