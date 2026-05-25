#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from claim_policy import FORBIDDEN_CLAIM_PATTERNS, forbidden_claim_hits
from finite_storage_schema import OBJECTIVE_COMPONENT_FIELDS

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
CORE_BASELINES = {
    "fixed_time",
    "actuated_local_pressure",
    "max_pressure",
    "capacity_aware_pressure",
    "cycle_pressure",
    "finite_storage_double_pressure",
    "finite_storage_primal_dual",
    "raw_neighbor_symbolic",
    "all_neighbor_symbolic",
    "random_permuted_dual",
}
NON_FIXED_CORE_BASELINES = CORE_BASELINES - {"fixed_time"}
REQUIRED_TOP_LEVEL = {"route_decision", "scenario_results", "aggregates", "baseline_coverage", "completion_gates"}

RENDERER_FORBIDDEN_PHRASES = ["max-pressure strawman"]
FORBIDDEN_PHRASES = list(dict.fromkeys([*FORBIDDEN_CLAIM_PATTERNS, *RENDERER_FORBIDDEN_PHRASES]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="experiments/dual_sensitivity/block4_closed_loop_suite.json")
    parser.add_argument("--out", default="experiments/dual_sensitivity/block4_closed_loop_suite_report.md")
    parser.add_argument("--csv-out", default="experiments/dual_sensitivity/block4_closed_loop_suite.csv")
    parser.add_argument("--fail-on-overclaim", action="store_true", default=True)
    return parser.parse_args()


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def md_cell(value: Any) -> str:
    return fmt(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def valid_completed_row(row: dict[str, Any]) -> bool:
    return (
        row.get("scenario_status") == "completed"
        and row.get("feasibility_status") in {"run", "completed"}
        and int(row.get("completed_vehicles", 0)) > 0
        and float(row.get("completion_rate", 0.0)) > 0.0
    )


def controller_actuation_evidence(rows: list[dict[str, Any]], scenario: str, controller: str) -> dict[str, Any]:
    if controller == "fixed_time":
        return {"passed": True, "switching_rows": "not_required"}
    relevant = [row for row in rows if row.get("scenario_tag") == scenario and row.get("controller") == controller]
    switching_rows = sum(1 for row in relevant if int(row.get("switching_count", 0)) > 0)
    no_switch_rows = sum(1 for row in relevant if row.get("no_switch_reason"))
    return {"passed": switching_rows > 0 or no_switch_rows == len(relevant), "switching_rows": switching_rows, "no_switch_rows": no_switch_rows}


def recompute_completion_gates(rows: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [row for row in rows if valid_completed_row(row)]
    gates: dict[str, Any] = {}
    for scenario in ["arterial_main", "grid_scalability"]:
        gates[scenario] = {}
        for controller in sorted(CORE_BASELINES):
            seeds = {int(row["seed"]) for row in completed if row.get("scenario_tag") == scenario and row.get("controller") == controller}
            actuation = controller_actuation_evidence(completed, scenario, controller)
            gates[scenario][controller] = {"completed_seeds": len(seeds), "actuation": actuation, "passed": len(seeds) >= 5 and bool(actuation["passed"])}
    gates["demand_shift_real_mechanism"] = any(
        row.get("scenario_tag") == "arterial_demand_shift"
        and row.get("demand_shift_mechanism")
        and row.get("demand_shift_mechanism") != "seed_only"
        and int(row.get("demand_shift_inserted_vehicles", 0)) >= max(2, (int(row.get("steps", 0)) - int(row.get("warmup", 0)) + 29) // 30)
        for row in completed
    )
    gates["failure_mode_real_mechanism"] = any(
        row.get("scenario_tag") == "arterial_bottleneck_failure_mode"
        and row.get("failure_mode_mechanism")
        and row.get("failure_mode_target_edge")
        and float(row.get("failure_mode_target_max_vehicles", 0.0)) > 0.0
        for row in completed
    )
    gates["failure_mode_pressure_rows"] = all(
        any(
            row.get("scenario_tag") == "arterial_bottleneck_failure_mode"
            and row.get("controller") == controller
            and row.get("failure_mode_mechanism")
            and row.get("failure_mode_target_edge")
            and float(row.get("failure_mode_target_max_vehicles", 0.0)) > 0.0
            for row in completed
        )
        for controller in ["max_pressure", "capacity_aware_pressure"]
    )
    return gates


def validate_payload(payload: dict[str, Any]) -> None:
    missing = REQUIRED_TOP_LEVEL - set(payload)
    if missing:
        raise ValueError(f"Block 4 payload missing required fields: {sorted(missing)}")
    if payload.get("route_decision") != "pressure-equivalent":
        raise ValueError("Phase 4 renderer expects Phase 3 route_decision=pressure-equivalent")
    rows = payload.get("scenario_results")
    if not isinstance(rows, list) or not rows:
        raise ValueError("scenario_results must be a non-empty list")
    gates = recompute_completion_gates(rows)
    if gates != payload.get("completion_gates"):
        raise ValueError("Stored completion_gates do not match gates recomputed from raw rows")
    for scenario in ["arterial_main", "grid_scalability"]:
        for controller in CORE_BASELINES:
            gate = gates[scenario][controller]
            if int(gate.get("completed_seeds", 0)) < 5 or not gate.get("passed"):
                raise ValueError(f"Completion/actuation gate failed for {scenario}/{controller}: {gate}")
    if not gates.get("demand_shift_real_mechanism"):
        raise ValueError("Demand-shift gate requires a real changed-demand mechanism")
    if not gates.get("failure_mode_real_mechanism") or not gates.get("failure_mode_pressure_rows"):
        raise ValueError("Failure-mode gate requires real manipulation, active target-edge traffic, and completed pressure rows")


def row_status(row: dict[str, Any]) -> str:
    if row.get("feasibility_status") == "not_feasible":
        return "not_feasible"
    return str(row.get("scenario_status", "completed"))


def aggregate_table(payload: dict[str, Any]) -> list[str]:
    lines = [
        "| Network | Scenario | Controller | Seeds | Avg travel time | Penalized travel time | Completion rate | Delay | Throughput | Mean queue | Max queue | Spillback | Blocking | Switching | Runtime sec |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload.get("aggregates", []):
        def mean(metric: str) -> str:
            return fmt(item.get(metric, {}).get("mean", 0.0))
        lines.append(
            "| {network} | {scenario} | {controller} | {seeds} | {travel} | {penalized} | {completion_rate} | {delay} | {throughput} | {mean_queue} | {max_queue} | {spillback} | {blocking} | {switching} | {runtime} |".format(
                network=md_cell(item.get("network", "")),
                scenario=md_cell(item.get("scenario_tag", "")),
                controller=md_cell(item.get("controller", "")),
                seeds=md_cell(item.get("n_seeds", 0)),
                travel=md_cell(mean("avg_travel_time")),
                penalized=md_cell(mean("penalized_avg_travel_time")),
                completion_rate=md_cell(mean("completion_rate")),
                delay=md_cell(mean("total_delay")),
                throughput=md_cell(mean("throughput")),
                mean_queue=md_cell(mean("mean_queue")),
                max_queue=md_cell(mean("max_queue")),
                spillback=md_cell(mean("spillback_count")),
                blocking=md_cell(mean("blocking_count")),
                switching=md_cell(mean("switching_count")),
                runtime=md_cell(mean("controller_runtime_sec")),
            )
        )
    return lines


def render_report(payload: dict[str, Any], input_path: Path) -> str:
    validate_payload(payload)
    coverage = payload.get("baseline_coverage", {})
    gates = payload.get("completion_gates", {})
    rows = payload.get("scenario_results", [])
    scenarios = sorted({str(row.get("scenario_tag")) for row in rows})
    networks = sorted({str(row.get("network")) for row in rows})
    demand_rows = [row for row in rows if row.get("demand_shift_mechanism")]
    failure_rows = [row for row in rows if row.get("failure_mode_mechanism")]

    lines = [
        "# Phase 4 Closed-Loop SUMO Evaluation Report",
        "",
        "## Route and Claim Discipline",
        "",
        f"- **Phase 3 route decision:** `{payload.get('route_decision')}`",
        "- **Claim framing:** generalized-pressure symbolic recovery under closed-loop SUMO evidence.",
        "- Pressure/backpressure and capacity-aware pressure are first-class baselines, not strawmen.",
        "- Results are simulator-, network-, horizon-, and seed-relative; they do not prove deployable real-world superiority.",
        "",
        "## Scenario and Network Coverage",
        "",
        f"- **Networks:** {', '.join(networks)}",
        f"- **Scenarios:** {', '.join(scenarios)}",
        f"- **Raw rows:** {len(rows)}",
        f"- **Aggregate rows:** {len(payload.get('aggregates', []))}",
        "",
        "## Baseline Coverage",
        "",
        "| Controller | Status | Reason |",
        "|---|---|---|",
    ]
    for controller, item in sorted(coverage.items()):
        lines.append(f"| {md_cell(controller)} | {md_cell(item.get('status', 'unknown'))} | {md_cell(item.get('unsupported_reason', ''))} |")

    lines.extend(
        [
            "",
            "## Completion Gates",
            "",
            "| Gate | Status |",
            "|---|---|",
        ]
    )
    for scenario in ["arterial_main", "grid_scalability"]:
        for controller in sorted(CORE_BASELINES):
            gate = gates[scenario][controller]
            lines.append(
                f"| {md_cell(scenario + '/' + controller)} | {md_cell(str(gate.get('completed_seeds')) + ' completed seeds; actuation=' + str(gate.get('actuation')) + '; passed=' + str(gate.get('passed')))} |"
            )
    lines.append(f"| demand_shift_real_mechanism | {md_cell(gates.get('demand_shift_real_mechanism'))} |")
    lines.append(f"| failure_mode_real_mechanism | {md_cell(gates.get('failure_mode_real_mechanism'))} |")
    lines.append(f"| failure_mode_pressure_rows | {md_cell(gates.get('failure_mode_pressure_rows'))} |")

    lines.extend(["", "## Main Arterial and Grid CI Summary", ""])
    lines.extend(aggregate_table(payload))

    lines.extend(
        [
            "",
            "## Robustness / Demand-Shift Summary",
            "",
            f"- Demand-shift mechanism(s): {', '.join(sorted({str(row.get('demand_shift_mechanism')) for row in demand_rows})) if demand_rows else 'None'}",
            f"- Demand-shift rows: {len(demand_rows)}",
            "",
            "## Bottleneck / Failure-Mode Summary",
            "",
            f"- Failure-mode mechanism(s): {', '.join(sorted({str(row.get('failure_mode_mechanism')) for row in failure_rows})) if failure_rows else 'None'}",
            f"- Failure-mode rows: {len(failure_rows)}",
            "",
            "## Runtime and Switching Summary",
            "",
            "Controller runtime and switching counts are included in the aggregate table and raw CSV rows.",
            "",
            "## Limitations and Next Evidence Needed",
            "",
            "- SUMO emitted emergency-braking warnings during some runs; interpret outputs as simulator diagnostics requiring follow-up tuning.",
            "- The main suite used the recorded short horizon to complete required seed gates locally; longer horizons remain future robustness work.",
            "- `local_pilight` and `full_dual_symbolic` are not claimed when not feasible; their unsupported reasons remain visible in baseline coverage.",
            "",
            "## Artifact Links",
            "",
            f"- Raw suite JSON: `{input_path}`",
            "- Smoke JSON: `experiments/dual_sensitivity/block4_closed_loop_smoke.json`",
            "- Phase 3 route report: `experiments/dual_sensitivity/block3_static_kill_gate_report.md`",
        ]
    )
    report = "\n".join(lines).rstrip() + "\n"
    forbidden = forbidden_claim_hits(report)
    lowered = report.lower()
    forbidden.extend(
        {"source": "rendered_report", "path": "rendered_report", "phrase": phrase}
        for phrase in RENDERER_FORBIDDEN_PHRASES
        if phrase in lowered
    )
    if forbidden:
        raise ValueError(f"Rendered report contains forbidden overclaim language: {forbidden}")
    return report


def csv_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in payload.get("scenario_results", []):
        output = {
            "row_type": "seed",
            "network": row.get("network", ""),
            "scenario_tag": row.get("scenario_tag", ""),
            "controller": row.get("controller", ""),
            "seed": row.get("seed", ""),
            "status": row_status(row),
            "steps": row.get("steps", ""),
            "warmup": row.get("warmup", ""),
            "action_interval": row.get("action_interval", ""),
            "sumocfg": row.get("sumocfg", ""),
            "net_file": row.get("net_file", ""),
            "unsupported_reason": row.get("unsupported_reason", ""),
            "travel_time_source": row.get("travel_time_source", ""),
            "unfinished_vehicle_count": row.get("unfinished_vehicle_count", ""),
            "demand_shift_mechanism": row.get("demand_shift_mechanism", ""),
            "demand_shift_inserted_vehicles": row.get("demand_shift_inserted_vehicles", ""),
            "failure_mode_mechanism": row.get("failure_mode_mechanism", ""),
            "failure_mode_target_edge": row.get("failure_mode_target_edge", ""),
            "failure_mode_target_max_vehicles": row.get("failure_mode_target_max_vehicles", ""),
            "failure_mode_start": row.get("failure_mode_start", ""),
            "failure_mode_end": row.get("failure_mode_end", ""),
            "ci_std_error": "",
            "ci95_low": "",
            "ci95_high": "",
        }
        output.update({field: row.get(field, 0.0) for field in METRIC_FIELDS})
        components = row.get("objective_components", {})
        if isinstance(components, dict):
            output.update({f"objective_{field}": components.get(field, "") for field in OBJECTIVE_COMPONENT_FIELDS})
        else:
            output.update({f"objective_{field}": "" for field in OBJECTIVE_COMPONENT_FIELDS})
        rows.append(output)
    for item in payload.get("aggregates", []):
        output = {
            "row_type": "aggregate",
            "network": item.get("network", ""),
            "scenario_tag": item.get("scenario_tag", ""),
            "controller": item.get("controller", ""),
            "seed": "aggregate",
            "status": f"n_seeds={item.get('n_seeds', 0)}",
            "steps": "",
            "warmup": "",
            "action_interval": "",
            "sumocfg": "",
            "net_file": "",
            "unsupported_reason": "",
            "travel_time_source": "aggregate",
            "unfinished_vehicle_count": "",
            "demand_shift_mechanism": "",
            "demand_shift_inserted_vehicles": "",
            "failure_mode_mechanism": "",
            "failure_mode_target_edge": "",
            "failure_mode_target_max_vehicles": "",
            "failure_mode_start": "",
            "failure_mode_end": "",
            "ci_std_error": item.get("avg_travel_time", {}).get("std_error", ""),
            "ci95_low": item.get("avg_travel_time", {}).get("ci95_low", ""),
            "ci95_high": item.get("avg_travel_time", {}).get("ci95_high", ""),
        }
        output.update({field: item.get(field, {}).get("mean", 0.0) for field in METRIC_FIELDS})
        rows.append(output)
    return rows


def write_csv(payload: dict[str, Any], csv_path: Path) -> None:
    validate_payload(payload)
    fieldnames = [
        "row_type",
        "network",
        "scenario_tag",
        "controller",
        "seed",
        "status",
        "steps",
        "warmup",
        "action_interval",
        "sumocfg",
        "net_file",
        "unsupported_reason",
        "travel_time_source",
        "unfinished_vehicle_count",
        "demand_shift_mechanism",
        "demand_shift_inserted_vehicles",
        "failure_mode_mechanism",
        "failure_mode_target_edge",
        "failure_mode_target_max_vehicles",
        "failure_mode_start",
        "failure_mode_end",
        "ci_std_error",
        "ci95_low",
        "ci95_high",
        *METRIC_FIELDS,
        *[f"objective_{field}" for field in sorted(OBJECTIVE_COMPONENT_FIELDS)],
    ]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows(payload))


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    report = render_report(payload, input_path)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    write_csv(payload, Path(args.csv_out))
    print(json.dumps({"out": str(out_path), "csv_out": args.csv_out, "route_decision": payload.get("route_decision")}, indent=2))


if __name__ == "__main__":
    main()
