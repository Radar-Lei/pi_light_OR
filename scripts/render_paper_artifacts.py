#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

FORBIDDEN_PHRASES = [
    "dual universally beats pressure",
    "max-pressure strawman",
    "proves superiority",
    "deployable superiority",
    "static evidence proves closed-loop",
]
REQUIRED_CLOSED_LOOP_METRICS = {
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="experiments/dual_sensitivity")
    parser.add_argument("--block0-json", default="experiments/dual_sensitivity/block0_dual_sanity.json")
    parser.add_argument("--sparse-json", default="experiments/dual_sensitivity/block2_sparse_recovery.json")
    parser.add_argument("--static-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--closed-loop-json", default="experiments/dual_sensitivity/block4_closed_loop_suite.json")
    parser.add_argument("--manifest-json", default="experiments/dual_sensitivity/reproducibility_manifest.json")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fail-on-overclaim", dest="fail_on_overclaim", action="store_true", default=True)
    group.add_argument("--no-fail-on-overclaim", dest="fail_on_overclaim", action="store_false")
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def load_inputs(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        "block0": Path(args.block0_json),
        "sparse": Path(args.sparse_json),
        "static": Path(args.static_json),
        "closed_loop": Path(args.closed_loop_json),
        "repro_manifest": Path(args.manifest_json),
    }
    payloads = {name: read_json(path) for name, path in paths.items()}
    payloads["paths"] = {name: str(path) for name, path in paths.items()}
    return payloads


def validate_inputs(inputs: dict[str, Any]) -> None:
    for name in ["block0", "sparse", "static", "closed_loop", "repro_manifest"]:
        if inputs[name].get("status") != "PASSED":
            raise ValueError(f"{name} source artifact is not PASSED")
    static_route = inputs["static"].get("route_decision")
    closed_route = inputs["closed_loop"].get("route_decision")
    if static_route != "pressure-equivalent":
        raise ValueError(f"Unexpected static route_decision: {static_route}")
    if closed_route != static_route:
        raise ValueError("Static and closed-loop route decisions differ")
    if not inputs["closed_loop"].get("completion_gates_passed"):
        raise ValueError("Closed-loop completion gates did not pass")
    schema = inputs["closed_loop"].get("metric_schema")
    if not isinstance(schema, dict):
        raise ValueError("closed_loop.metric_schema must be an object")
    missing_metrics = REQUIRED_CLOSED_LOOP_METRICS - set(schema)
    if missing_metrics:
        raise ValueError(f"closed_loop.metric_schema is missing metrics: {sorted(missing_metrics)}")
    required_nonempty = [
        ("block0", "results"),
        ("sparse", "best_by_library"),
        ("static", "regime_metrics"),
        ("closed_loop", "scenario_results"),
        ("closed_loop", "aggregates"),
        ("repro_manifest", "artifact_checks"),
    ]
    for name, key in required_nonempty:
        value = inputs[name].get(key)
        if not isinstance(value, list) or not value:
            raise ValueError(f"{name}.{key} must be a non-empty list")
    bad_checks = [
        check
        for check in inputs["repro_manifest"].get("artifact_checks", [])
        if check.get("expected") and (not check.get("exists") or check.get("parse_status") != "ok")
    ]
    if bad_checks:
        raise ValueError(f"Reproducibility manifest has missing/bad expected artifacts: {bad_checks}")


def claim_note(route_decision: str) -> str:
    return f"{route_decision} generalized-pressure symbolic recovery; simulator/network/horizon/seed-relative evidence."


def scalar(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.10g}"
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def table_row(table_id: str, panel: str, metric: str, value: Any, source_artifact: str, source_key: str, route_decision: str, **extra: Any) -> dict[str, Any]:
    row = {
        "table_id": table_id,
        "panel": panel,
        "metric": metric,
        "value": scalar(value),
        "source_artifact": source_artifact,
        "source_key": source_key,
        "route_decision": route_decision,
        "claim_note": claim_note(route_decision),
    }
    row.update({key: scalar(value) for key, value in extra.items()})
    return row


def build_tables(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    route_decision = str(inputs["static"].get("route_decision", inputs["closed_loop"].get("route_decision", "unknown")))
    paths = inputs["paths"]
    rows: list[dict[str, Any]] = []

    block0 = inputs["block0"]
    for key, value in block0.get("criteria", {}).items():
        rows.append(table_row("T0_dual_sanity", "criteria", key, value, paths["block0"], f"criteria.{key}", route_decision))
    for idx, result in enumerate(block0.get("results", [])):
        scenario = result.get("scenario", f"scenario_{idx}")
        rows.append(table_row("T0_dual_sanity", scenario, "dual_rank", result.get("dual_rank", []), paths["block0"], f"results[{idx}].dual_rank", route_decision))
        rows.append(table_row("T0_dual_sanity", scenario, "pressure_rank", result.get("pressure_rank", []), paths["block0"], f"results[{idx}].pressure_rank", route_decision))

    sparse = inputs["sparse"]
    best_rows = sparse.get("best_by_library") or sparse.get("summary", [])
    for idx, item in enumerate(best_rows):
        library = str(item.get("library", f"library_{idx}"))
        rows.append(
            table_row(
                "T1_sparse_recovery",
                library,
                "best_run",
                item.get("realized_mean_regret", ""),
                paths["sparse"],
                f"best_by_library[{idx}]",
                route_decision,
                selected_atoms=item.get("selected_atoms", []),
                program_complexity=item.get("program_complexity", ""),
                realized_total_regret=item.get("realized_total_regret", ""),
                max_regret=item.get("max_regret", ""),
                action_agreement=item.get("action_agreement", ""),
                source_rules_path=sparse.get("rules_out", ""),
            )
        )

    static = inputs["static"]
    rows.append(table_row("T2_static_kill_gate", "route", "route_decision", static.get("route_decision", ""), paths["static"], "route_decision", route_decision, route_confidence=static.get("route_confidence", "")))
    for idx, item in enumerate(static.get("regime_metrics", [])):
        regime = str(item.get("regime", f"regime_{idx}"))
        for metric in [
            "dual_vs_pressure_disagreement_rate",
            "dual_win_rate",
            "pressure_win_rate",
            "dual_mean_oracle_regret",
            "pressure_mean_oracle_regret",
            "mean_oracle_regret_delta_pressure_minus_dual",
            "dual_worst_case_regret",
            "pressure_worst_case_regret",
        ]:
            rows.append(table_row("T2_static_kill_gate", regime, metric, item.get(metric, ""), paths["static"], f"regime_metrics[{idx}].{metric}", route_decision))

    closed = inputs["closed_loop"]
    for idx, item in enumerate(closed.get("aggregates", [])):
        panel = f"{item.get('scenario_tag','')}/{item.get('controller','')}"
        for metric in ["avg_travel_time", "penalized_avg_travel_time", "completion_rate", "total_delay", "mean_queue", "max_queue", "spillback_count", "blocking_count", "switching_count", "controller_runtime_sec"]:
            value = item.get(metric, {}).get("mean", "") if isinstance(item.get(metric), dict) else item.get(metric, "")
            rows.append(
                table_row(
                    "T3_closed_loop",
                    panel,
                    metric,
                    value,
                    paths["closed_loop"],
                    f"aggregates[{idx}].{metric}",
                    route_decision,
                    network=item.get("network", ""),
                    scenario_tag=item.get("scenario_tag", ""),
                    controller=item.get("controller", ""),
                    n_seeds=item.get("n_seeds", ""),
                    ci95_low=item.get(metric, {}).get("ci95_low", "") if isinstance(item.get(metric), dict) else "",
                    ci95_high=item.get(metric, {}).get("ci95_high", "") if isinstance(item.get(metric), dict) else "",
                )
            )

    manifest = inputs["repro_manifest"]
    rows.append(table_row("T4_reproducibility", "audit", "status", manifest.get("status", ""), paths["repro_manifest"], "status", route_decision))
    rows.append(table_row("T4_reproducibility", "audit", "artifact_checks", len(manifest.get("artifact_checks", [])), paths["repro_manifest"], "artifact_checks", route_decision))
    return rows


def figure_row(figure_id: str, series: str, x_value: Any, y_value: Any, source_artifact: str, source_key: str, route_decision: str, **extra: Any) -> dict[str, Any]:
    row = {
        "figure_id": figure_id,
        "series": series,
        "x_value": scalar(x_value),
        "y_value": scalar(y_value),
        "source_artifact": source_artifact,
        "source_key": source_key,
        "route_decision": route_decision,
        "claim_note": claim_note(route_decision),
    }
    row.update({key: scalar(value) for key, value in extra.items()})
    return row


def build_figure_data(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    route_decision = str(inputs["static"].get("route_decision", inputs["closed_loop"].get("route_decision", "unknown")))
    paths = inputs["paths"]
    rows: list[dict[str, Any]] = []

    for idx, item in enumerate(inputs["static"].get("regime_metrics", [])):
        regime = item.get("regime", f"regime_{idx}")
        rows.append(figure_row("F1_static_dual_vs_pressure", "dual_mean_oracle_regret", regime, item.get("dual_mean_oracle_regret", ""), paths["static"], f"regime_metrics[{idx}].dual_mean_oracle_regret", route_decision))
        rows.append(figure_row("F1_static_dual_vs_pressure", "pressure_mean_oracle_regret", regime, item.get("pressure_mean_oracle_regret", ""), paths["static"], f"regime_metrics[{idx}].pressure_mean_oracle_regret", route_decision))
        rows.append(figure_row("F2_static_disagreement", "dual_vs_pressure_disagreement_rate", regime, item.get("dual_vs_pressure_disagreement_rate", ""), paths["static"], f"regime_metrics[{idx}].dual_vs_pressure_disagreement_rate", route_decision))

    for idx, item in enumerate(inputs["closed_loop"].get("aggregates", [])):
        x_value = f"{item.get('scenario_tag','')}/{item.get('controller','')}"
        for metric in ["avg_travel_time", "completion_rate", "mean_queue", "switching_count"]:
            value = item.get(metric, {}).get("mean", "") if isinstance(item.get(metric), dict) else item.get(metric, "")
            rows.append(
                figure_row(
                    "F3_closed_loop_aggregates",
                    metric,
                    x_value,
                    value,
                    paths["closed_loop"],
                    f"aggregates[{idx}].{metric}",
                    route_decision,
                    network=item.get("network", ""),
                    scenario_tag=item.get("scenario_tag", ""),
                    controller=item.get("controller", ""),
                    n_seeds=item.get("n_seeds", ""),
                )
            )
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def forbidden_hits(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> list[str]:
    checked_manifest = {
        "status": manifest.get("status"),
        "route_decision": manifest.get("route_decision"),
        "claim_framing": manifest.get("claim_discipline", {}).get("framing"),
    }
    text = json.dumps({"rows": rows, "manifest": checked_manifest}, sort_keys=True).lower()
    return [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]


def main() -> None:
    args = parse_args()
    inputs = load_inputs(args)
    validate_inputs(inputs)
    tables = build_tables(inputs)
    figures = build_figure_data(inputs)
    out_dir = Path(args.out_dir)
    tables_path = out_dir / "paper_tables.csv"
    figures_path = out_dir / "paper_figure_data.csv"
    manifest_path = out_dir / "paper_artifacts_manifest.json"
    route_decision = str(inputs["static"].get("route_decision", inputs["closed_loop"].get("route_decision", "unknown")))
    manifest = {
        "experiment": "paper_artifacts",
        "status": "PASSED",
        "generated_by": "scripts/render_paper_artifacts.py",
        "source_artifacts": inputs["paths"],
        "generated_artifacts": {
            "paper_tables": str(tables_path),
            "paper_figure_data": str(figures_path),
            "manifest": str(manifest_path),
        },
        "row_counts": {"paper_tables": len(tables), "paper_figure_data": len(figures)},
        "route_decision": route_decision,
        "claim_discipline": {
            "framing": claim_note(route_decision),
            "forbidden_phrases": FORBIDDEN_PHRASES,
            "forbidden_phrases_present": [],
        },
        "requirements_covered": ["REPR-04", "REPR-05"],
    }
    hits = forbidden_hits(tables + figures, manifest)
    manifest["claim_discipline"]["forbidden_phrases_present"] = hits
    if args.fail_on_overclaim and hits:
        manifest["status"] = "FAILED"
        raise ValueError(f"Generated paper artifacts contain forbidden overclaim language: {hits}")
    write_csv(tables, tables_path)
    write_csv(figures, figures_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"tables": str(tables_path), "figures": str(figures_path), "manifest": str(manifest_path), "status": manifest["status"]}, indent=2))


if __name__ == "__main__":
    main()
