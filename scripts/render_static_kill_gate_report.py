#!/usr/bin/env python3
"""Render the Phase 3 static kill-gate route report.

The renderer consumes the machine-readable Block 3 kill-gate JSON and writes a
human-readable Markdown report. It preserves the JSON route decision as the
single source of truth, keeps the interpretation static/sample-relative, and
never upgrades static one-step evidence into closed-loop traffic-control claims.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_ROUTE_FIELDS = {
    "experiment",
    "status",
    "input_states",
    "tls",
    "target_total_states",
    "num_examples_total",
    "sample_target_met",
    "preliminary_regimes",
    "regime_metrics",
    "route_decision",
    "route_confidence",
    "route_rationale",
    "route_caveats",
    "csv_out",
    "rules_out",
    "report_out",
}

ROUTE_DECISIONS = {"dual-improves-pressure", "pressure-equivalent", "diagnostic"}
FORBIDDEN_REPORT_PHRASES = [
    "closed-loop superiority",
    "travel time superiority",
    "travel-time superiority",
    "throughput superiority",
    "deployable performance superiority",
    "deployable control performance is proven",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--out", default="experiments/dual_sensitivity/block3_static_kill_gate_report.md")
    parser.add_argument("--fail-on-missing-route", action="store_true")
    return parser.parse_args()


def validate_payload(payload: dict[str, Any], fail_on_missing_route: bool) -> list[str]:
    missing = sorted(REQUIRED_ROUTE_FIELDS - set(payload))
    if missing and fail_on_missing_route:
        raise ValueError(f"Gate JSON is missing required route/report fields: {missing}")

    warnings: list[str] = []
    if missing:
        warnings.append(f"Missing optional-for-render fields: {', '.join(missing)}")

    route_decision = payload.get("route_decision")
    if fail_on_missing_route and route_decision not in ROUTE_DECISIONS:
        raise ValueError(
            f"route_decision must be one of {sorted(ROUTE_DECISIONS)}; got {route_decision!r}"
        )
    if route_decision is not None and route_decision not in ROUTE_DECISIONS:
        warnings.append(f"Unknown route_decision value: {route_decision!r}")

    if "regime_metrics" in payload and not isinstance(payload["regime_metrics"], list):
        raise ValueError("regime_metrics must be a list")
    return warnings


def fmt_bool(value: Any) -> str:
    return "yes" if bool(value) else "no"


def fmt_list(values: Any) -> str:
    if not values:
        return "None"
    if isinstance(values, list):
        return ", ".join(str(value) for value in values)
    return str(values)


def fmt_float(value: Any) -> str:
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return "n/a"


def route_implication(route_decision: str) -> list[str]:
    if route_decision == "dual-improves-pressure":
        return [
            "Prioritize Phase 4 closed-loop tests that stress storage, supply, spillback, and corridor-bottleneck mechanisms.",
            "Keep max-pressure/backpressure and capacity-aware pressure variants as first-class baselines before any stronger claim is considered.",
            "Treat the Phase 3 outcome only as permission to test a scarcity-aware generalized-pressure hypothesis, not as performance evidence.",
        ]
    if route_decision == "pressure-equivalent":
        return [
            "Route Phase 4 toward generalized-pressure symbolic recovery: compactness, traceability, and equivalence to pressure are the main static lessons.",
            "Prioritize honest pressure and capacity-aware pressure baselines, because the static evidence does not separate dual from pressure on oracle regret.",
            "Design at least one closed-loop failure-mode scenario to check whether dynamic effects create separation absent from this static sample.",
        ]
    return [
        "Route Phase 4 toward diagnostic framing: identify when dual signals underperform, are unsupported by the proxy schema, or are too weak for a positive claim.",
        "Prioritize stress tests and ablations that explain failure modes rather than trying to claim dual advantage.",
        "Keep any positive interpretation conditional until closed-loop evidence is independently generated and compared against strong pressure baselines.",
    ]


def proxy_limitations(payload: dict[str, Any]) -> list[str]:
    limitations: list[str] = []
    for note in payload.get("input_regime_status", []) or []:
        text = str(note)
        lowered = text.lower()
        if "proxy" in lowered or "unsupported" in lowered or "no explicit" in lowered:
            limitations.append(text)
    for caveat in payload.get("route_caveats", []) or []:
        text = str(caveat)
        lowered = text.lower()
        if "proxy" in lowered or "unsupported" in lowered or "sample" in lowered:
            limitations.append(text)
    if not limitations:
        limitations.append(
            "No unsupported regimes were recorded in the gate JSON; proxy labels, if present in regime names, remain static sample-relative evidence only."
        )
    return limitations


def render_metric_table(metrics: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Regime | Examples | Aligned | Disagreement | Dual win | Pressure win | Tie | Dual mean regret | Pressure mean regret | Δ regret pressure-dual | Dual worst | Pressure worst | Selected dual atoms | Selected pressure atoms | Scope |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for metric in metrics:
        lines.append(
            "| {regime} | {examples} | {aligned} | {disagreement} | {dual_win} | {pressure_win} | {tie} | {dual_mean} | {pressure_mean} | {delta} | {dual_worst} | {pressure_worst} | {dual_atoms} | {pressure_atoms} | {scope} |".format(
                regime=metric.get("regime", "unknown"),
                examples=metric.get("num_examples", "n/a"),
                aligned=metric.get("num_aligned_examples", metric.get("num_examples", "n/a")),
                disagreement=fmt_float(metric.get("dual_vs_pressure_disagreement_rate")),
                dual_win=fmt_float(metric.get("dual_win_rate")),
                pressure_win=fmt_float(metric.get("pressure_win_rate")),
                tie=fmt_float(metric.get("tie_rate")),
                dual_mean=fmt_float(metric.get("dual_mean_oracle_regret")),
                pressure_mean=fmt_float(metric.get("pressure_mean_oracle_regret")),
                delta=fmt_float(metric.get("mean_oracle_regret_delta_pressure_minus_dual")),
                dual_worst=fmt_float(metric.get("dual_worst_case_regret")),
                pressure_worst=fmt_float(metric.get("pressure_worst_case_regret")),
                dual_atoms=fmt_list(metric.get("selected_atoms_dual")),
                pressure_atoms=fmt_list(metric.get("selected_atoms_pressure")),
                scope=metric.get("claim_scope", "static_sample_relative"),
            )
        )
    return lines


def render_report(payload: dict[str, Any], gate_json_path: Path, out_path: Path) -> str:
    route_decision = str(payload.get("route_decision", "missing-route-decision"))
    route_confidence = str(payload.get("route_confidence", "UNKNOWN"))
    preliminary_regimes = payload.get("preliminary_regimes", [])
    metrics = list(payload.get("regime_metrics", []))

    lines = [
        "# Phase 3 Static Kill-Gate Route Report",
        "",
        "## Route Decision",
        "",
        f"- **Route decision:** `{route_decision}`",
        f"- **Route confidence:** `{route_confidence}`",
        f"- **Status:** `{payload.get('status', 'UNKNOWN')}`",
        f"- **Experiment:** `{payload.get('experiment', 'unknown')}`",
        "",
        "This is a static sample-relative, pre-closed-loop route decision. It does not claim closed-loop results, travel-time gains, throughput gains, deployable traffic-control performance, or universal dominance over max-pressure/backpressure.",
        "",
        "## Route Alias Mapping",
        "",
        "| JSON route | Human-readable meaning | Downstream framing |",
        "|---|---|---|",
        "| `dual-improves-pressure` | Static binding-regime evidence favors dual over pressure. | Strong mainline candidate: test scarcity-aware generalized pressure in Phase 4. |",
        "| `pressure-equivalent` | dual-recovers/ties pressure on static oracle-regret evidence. | Generalized-pressure symbolic recovery framing; no dominance claim. |",
        "| `diagnostic` | dual-underperforms, unsupported regimes dominate, or evidence is too weak for a positive route. | Diagnostic/limitations framing. |",
        "",
        "## Route Rationale",
        "",
        str(payload.get("route_rationale", "No route rationale recorded.")),
        "",
        "## Static-Only Scope and Claim Caveats",
        "",
        "- Phase 3 uses static/sample-relative one-step recovery metrics only.",
        "- Phase 3 is pre-closed-loop; closed-loop SUMO experiments are Phase 4 work.",
        "- The report documents claim routing before Phase 4 interpretation and does not treat static oracle regret as deployable control evidence.",
    ]
    for caveat in payload.get("route_caveats", []) or []:
        lines.append(f"- {caveat}")

    lines.extend(
        [
            "",
            "## Sample Sufficiency",
            "",
            f"- **Valid converted examples:** {payload.get('num_examples_total', 'n/a')}",
            f"- **Target valid examples:** {payload.get('target_total_states', 'n/a')}",
            f"- **Sample target met:** {fmt_bool(payload.get('sample_target_met', False))}",
            f"- **Preliminary regimes:** {fmt_list(preliminary_regimes)}",
            f"- **Raw samples by regime:** {json.dumps(payload.get('raw_samples_by_regime', {}), sort_keys=True)}",
            f"- **Valid examples by regime:** {json.dumps(payload.get('valid_examples_by_regime', {}), sort_keys=True)}",
            "",
            "## Per-Regime Metrics",
            "",
        ]
    )
    lines.extend(render_metric_table(metrics))

    lines.extend(["", "## Unsupported / Proxy Regime Limitations", ""])
    for limitation in proxy_limitations(payload):
        lines.append(f"- {limitation}")

    if payload.get("input_labeling_notes"):
        lines.extend(["", "## Input Labeling Notes", ""])
        for note in payload.get("input_labeling_notes", []):
            lines.append(f"- {note}")

    lines.extend(
        [
            "",
            "## Artifact Links",
            "",
            f"- Gate JSON: `{gate_json_path}`",
            f"- CSV metrics: `{payload.get('csv_out', '')}`",
            f"- Recovered rules: `{payload.get('rules_out', '')}`",
            f"- Rendered report: `{out_path}`",
            "",
            "## Phase 4 Implications / Priorities",
            "",
        ]
    )
    for implication in route_implication(route_decision):
        lines.append(f"- {implication}")

    report = "\n".join(lines).rstrip() + "\n"
    lowered = report.lower()
    forbidden = [phrase for phrase in FORBIDDEN_REPORT_PHRASES if phrase in lowered]
    if forbidden:
        raise ValueError(f"Rendered report contains forbidden superiority language: {forbidden}")
    return report


def main() -> None:
    args = parse_args()
    gate_json_path = Path(args.gate_json)
    out_path = Path(args.out)
    payload = json.loads(gate_json_path.read_text(encoding="utf-8"))
    warnings = validate_payload(payload, args.fail_on_missing_route)
    report = render_report(payload, gate_json_path, out_path)
    if warnings:
        report = report.rstrip() + "\n\n## Renderer Warnings\n\n" + "\n".join(f"- {warning}" for warning in warnings) + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(out_path),
                "gate_json": str(gate_json_path),
                "route_decision": payload.get("route_decision"),
                "warnings": warnings,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
