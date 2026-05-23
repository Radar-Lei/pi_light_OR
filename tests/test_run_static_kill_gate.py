#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from run_static_kill_gate import compare_dual_pressure, decide_route, find_preliminary_regimes


def test_tie_aware_disagreement_is_not_a_win() -> None:
    dual_run = {
        "status": "SOLVED",
        "selected_atoms": ["dual_sensitivity"],
        "rule_text": "dual rule",
        "realized_mean_regret": 0.0,
        "max_regret": 0.0,
        "results": [
            {
                "source": "fixture.json#storage_binding_proxy#0",
                "scenario": "sumo_C3_t0",
                "chosen_movement": 1,
                "oracle_regret": 0.0,
            }
        ],
    }
    pressure_run = {
        "status": "SOLVED",
        "selected_atoms": ["pressure_backpressure"],
        "rule_text": "pressure rule",
        "realized_mean_regret": 0.0,
        "max_regret": 0.0,
        "results": [
            {
                "source": "fixture.json#storage_binding_proxy#0",
                "scenario": "sumo_C3_t0",
                "chosen_movement": 2,
                "oracle_regret": 0.0,
            }
        ],
    }

    metrics = compare_dual_pressure(
        regime="storage_binding_proxy",
        dual_run=dual_run,
        pressure_run=pressure_run,
        num_examples=1,
        min_regime_count=1,
        sample_target_met=False,
        equivalence_tolerance=1e-9,
        rules_path=Path("rules.txt"),
    )

    assert metrics["dual_vs_pressure_disagreement_rate"] == 1.0
    assert metrics["dual_win_rate"] == 0.0
    assert metrics["pressure_win_rate"] == 0.0
    assert metrics["tie_rate"] == 1.0
    assert metrics["mean_oracle_regret_delta_pressure_minus_dual"] == 0.0


def test_sample_shortfall_routes_to_diagnostic() -> None:
    metrics = [
        {
            "regime": "storage_binding_proxy",
            "num_examples": 16,
            "sample_target_met": False,
            "claim_scope": "preliminary_static_sample_relative",
            "dual_win_rate": 0.75,
            "pressure_win_rate": 0.0,
            "tie_rate": 0.25,
            "mean_oracle_regret_delta_pressure_minus_dual": 0.5,
        }
    ]

    route = decide_route(
        metrics,
        sample_target_met=False,
        dual_win_threshold=0.55,
        regret_improvement_threshold=0.05,
        equivalence_tolerance=1e-9,
    )

    assert route["route_decision"] == "diagnostic"
    assert route["route_confidence"] == "LOW"
    assert any("sample target" in caveat for caveat in route["route_caveats"])


def test_missing_requested_regime_routes_to_diagnostic() -> None:
    preliminary = find_preliminary_regimes(
        raw_counts={"slack": 200, "storage_binding_proxy": 200},
        valid_examples_by_regime={"slack": 200, "storage_binding_proxy": 0},
        runs_by_regime={
            "slack": [
                {"status": "SOLVED", "library": "dual_sensitivity", "realized_total_regret": 0.0, "program_complexity": 1},
                {"status": "SOLVED", "library": "pressure_backpressure", "realized_total_regret": 0.0, "program_complexity": 1},
            ],
            "storage_binding_proxy": [],
        },
        min_regime_count=30,
    )
    route = decide_route(
        metrics=[
            {
                "regime": "slack",
                "dual_win_rate": 0.0,
                "pressure_win_rate": 0.0,
                "mean_oracle_regret_delta_pressure_minus_dual": 0.0,
            }
        ],
        sample_target_met=False,
        dual_win_threshold=0.55,
        regret_improvement_threshold=0.05,
        equivalence_tolerance=1e-9,
        preliminary_regimes=preliminary,
    )

    assert preliminary == ["storage_binding_proxy"]
    assert route["route_decision"] == "diagnostic"
    assert any("storage_binding_proxy" in caveat for caveat in route["route_caveats"])


def main() -> None:
    test_tie_aware_disagreement_is_not_a_win()
    test_sample_shortfall_routes_to_diagnostic()
    test_missing_requested_regime_routes_to_diagnostic()
    print("static kill-gate tests ok")


if __name__ == "__main__":
    main()
