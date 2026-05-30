#!/usr/bin/env python3
"""V1.8 parameter sweep: 3 tau_adv x 3 eps_u = 9 combinations.

For each combination, runs 2 scenarios (storage_activation, switching_loss_sensitive)
with v1.8 and max_pressure controllers using seed=20261801, then compares metrics.

Usage:
    PYTHONPATH=scripts python scripts/sweep_v18_params.py
"""
from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path
from typing import Any

# Ensure scripts/ is importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_closed_loop_sumo as sim

SEED = 20261801
STEPS = 300
WARMUP = 60
ACTION_INTERVAL = 10
NETWORK = "arterial"
CONTROLLER_V18 = "finite_storage_regime_calibrated_cfs_pd_mpc_v1_8"
CONTROLLER_MP = "max_pressure"
ROUTE_JSON = Path("experiments/dual_sensitivity/block3_static_kill_gate.json")
OUT_PATH = Path("experiments/dual_sensitivity/v1_8_param_sweep.json")

SCENARIOS = [
    "arterial_v1_5_storage_activation",
    "arterial_switching_loss_sensitive",
]

TAU_ADV_VARIANTS = {
    "conservative": {
        "storage_binding": 0.05,
        "cascade_risk": 0.05,
        "switching_sensitive": 0.08,
        "coordination": 0.08,
        "slack": 0.10,
        "completion_critical": 0.10,
    },
    "moderate": {
        "storage_binding": 0.02,
        "cascade_risk": 0.02,
        "switching_sensitive": 0.05,
        "coordination": 0.05,
        "slack": 0.08,
        "completion_critical": 0.08,
    },
    "aggressive": {
        "storage_binding": 0.01,
        "cascade_risk": 0.01,
        "switching_sensitive": 0.03,
        "coordination": 0.03,
        "slack": 0.05,
        "completion_critical": 0.05,
    },
}

EPS_U_VARIANTS = {
    "tight": {
        "storage_binding": 0.05,
        "cascade_risk": 0.05,
        "switching_sensitive": 0.03,
        "coordination": 0.03,
        "slack": 0.00,
        "completion_critical": 0.00,
    },
    "medium": {
        "storage_binding": 0.10,
        "cascade_risk": 0.10,
        "switching_sensitive": 0.05,
        "coordination": 0.05,
        "slack": 0.00,
        "completion_critical": 0.00,
    },
    "wide": {
        "storage_binding": 0.20,
        "cascade_risk": 0.20,
        "switching_sensitive": 0.10,
        "coordination": 0.10,
        "slack": 0.00,
        "completion_critical": 0.00,
    },
}


def run_one(
    controller: str,
    scenario_tag: str,
    seed: int,
) -> dict[str, Any]:
    """Run a single experiment and return the metrics row."""
    route_metadata = sim.load_route_metadata(ROUTE_JSON)
    row = sim.run_experiment(
        network=NETWORK,
        controller=controller,
        seed=seed,
        steps=STEPS,
        warmup=WARMUP,
        action_interval=ACTION_INTERVAL,
        route_metadata=route_metadata,
        scenario_tag=scenario_tag,
    )
    return row


def extract_metrics(row: dict[str, Any]) -> dict[str, float]:
    """Extract the key comparison metrics from a result row."""
    return {
        "avg_travel_time": row.get("avg_travel_time", 0.0),
        "total_delay": row.get("total_delay", 0.0),
        "completion_rate": row.get("completion_rate", 0.0),
        "completed_vehicles": row.get("completed_vehicles", 0),
        "unfinished_vehicle_count": row.get("unfinished_vehicle_count", 0),
        "penalized_avg_travel_time": row.get("penalized_avg_travel_time", 0.0),
        "mean_queue": row.get("mean_queue", 0.0),
        "spillback_count": row.get("spillback_count", 0),
        "switching_count": row.get("switching_count", 0),
    }


def main() -> None:
    # Deep-copy the default params so we can restore them.
    default_params = copy.deepcopy(sim.DYNAMIC_V1_8_RC_CFS_PD_MPC_PARAMS)

    all_results: list[dict[str, Any]] = []
    comparison_table: list[dict[str, Any]] = []

    for tau_name, tau_vals in TAU_ADV_VARIANTS.items():
        for eps_name, eps_vals in EPS_U_VARIANTS.items():
            combo_label = f"{tau_name}__{eps_name}"
            print(f"\n{'='*60}")
            print(f"Combo: tau_adv={tau_name}, eps_u={eps_name}  [{combo_label}]")
            print(f"{'='*60}")

            # Override the global params in-place.
            sim.DYNAMIC_V1_8_RC_CFS_PD_MPC_PARAMS["tau_adv"] = dict(tau_vals)
            sim.DYNAMIC_V1_8_RC_CFS_PD_MPC_PARAMS["eps_u"] = dict(eps_vals)

            for scenario in SCENARIOS:
                print(f"\n  Scenario: {scenario}")
                t0 = time.perf_counter()

                # Run v1.8.
                v18_row = run_one(CONTROLLER_V18, scenario, SEED)
                v18_metrics = extract_metrics(v18_row)

                # Run max_pressure baseline.
                mp_row = run_one(CONTROLLER_MP, scenario, SEED)
                mp_metrics = extract_metrics(mp_row)

                elapsed = time.perf_counter() - t0
                print(f"    v1.8 ATT={v18_metrics['avg_travel_time']:.2f}  "
                      f"delay={v18_metrics['total_delay']:.1f}  "
                      f"completion={v18_metrics['completion_rate']:.3f}  "
                      f"unfinished={v18_metrics['unfinished_vehicle_count']}")
                print(f"    mp  ATT={mp_metrics['avg_travel_time']:.2f}  "
                      f"delay={mp_metrics['total_delay']:.1f}  "
                      f"completion={mp_metrics['completion_rate']:.3f}  "
                      f"unfinished={mp_metrics['unfinished_vehicle_count']}")

                # Compute deltas (negative delta means v1.8 is better for
                # travel time, delay, queue; positive delta for completion rate
                # means v1.8 is better).
                delta_att_pct = (
                    (v18_metrics["avg_travel_time"] - mp_metrics["avg_travel_time"])
                    / max(mp_metrics["avg_travel_time"], 1e-9) * 100.0
                )
                delta_delay_pct = (
                    (v18_metrics["total_delay"] - mp_metrics["total_delay"])
                    / max(mp_metrics["total_delay"], 1e-9) * 100.0
                )
                delta_completion = (
                    v18_metrics["completion_rate"] - mp_metrics["completion_rate"]
                )
                v18_beats_mp_att = v18_metrics["avg_travel_time"] < mp_metrics["avg_travel_time"]
                v18_beats_mp_delay = v18_metrics["total_delay"] < mp_metrics["total_delay"]

                comparison = {
                    "combo": combo_label,
                    "tau_adv": tau_name,
                    "eps_u": eps_name,
                    "tau_adv_values": dict(tau_vals),
                    "eps_u_values": dict(eps_vals),
                    "scenario": scenario,
                    "seed": SEED,
                    "v18": v18_metrics,
                    "max_pressure": mp_metrics,
                    "delta_att_pct": round(delta_att_pct, 2),
                    "delta_delay_pct": round(delta_delay_pct, 2),
                    "delta_completion_rate": round(delta_completion, 4),
                    "v18_beats_mp_att": v18_beats_mp_att,
                    "v18_beats_mp_delay": v18_beats_mp_delay,
                    "elapsed_sec": round(elapsed, 1),
                }
                comparison_table.append(comparison)

                all_results.append({
                    "combo": combo_label,
                    "tau_adv": tau_name,
                    "eps_u": eps_name,
                    "scenario": scenario,
                    "controller": CONTROLLER_V18,
                    "metrics": v18_metrics,
                })
                all_results.append({
                    "combo": combo_label,
                    "tau_adv": tau_name,
                    "eps_u": eps_name,
                    "scenario": scenario,
                    "controller": CONTROLLER_MP,
                    "metrics": mp_metrics,
                })

                print(f"    delta_ATT%={delta_att_pct:+.2f}%  "
                      f"delta_delay%={delta_delay_pct:+.2f}%  "
                      f"delta_completion={delta_completion:+.4f}  "
                      f"v18_wins_ATT={v18_beats_mp_att}  "
                      f"v18_wins_delay={v18_beats_mp_delay}  "
                      f"[{elapsed:.1f}s]")

    # Restore defaults.
    sim.DYNAMIC_V1_8_RC_CFS_PD_MPC_PARAMS.clear()
    sim.DYNAMIC_V1_8_RC_CFS_PD_MPC_PARAMS.update(default_params)

    # --- Summary ---
    print(f"\n{'='*60}")
    print("SWEEP SUMMARY")
    print(f"{'='*60}")

    # Per-combo win rate.
    combo_wins: dict[str, dict[str, int]] = {}
    for c in comparison_table:
        combo = c["combo"]
        if combo not in combo_wins:
            combo_wins[combo] = {"att_wins": 0, "delay_wins": 0, "total": 0}
        combo_wins[combo]["total"] += 1
        if c["v18_beats_mp_att"]:
            combo_wins[combo]["att_wins"] += 1
        if c["v18_beats_mp_delay"]:
            combo_wins[combo]["delay_wins"] += 1

    print(f"\n{'combo':<30s} {'ATT_wins':>10s} {'delay_wins':>12s} {'total':>6s}")
    print("-" * 62)
    best_combo = None
    best_score = -1
    for combo, wins in sorted(combo_wins.items()):
        score = wins["att_wins"] + wins["delay_wins"]
        print(f"{combo:<30s} {wins['att_wins']:>10d} {wins['delay_wins']:>12d} {wins['total']:>6d}")
        if score > best_score:
            best_score = score
            best_combo = combo
    print("-" * 62)
    print(f"Best combo: {best_combo}  (ATT+delay wins: {best_score}/{combo_wins[best_combo]['total']*2})")

    # Detailed table.
    print(f"\n{'tau_adv':<14s} {'eps_u':<10s} {'scenario':<45s} {'v18_ATT':>8s} {'mp_ATT':>8s} {'d_ATT%':>8s} {'v18_delay':>10s} {'mp_delay':>10s} {'d_delay%':>8s}")
    print("-" * 135)
    for c in comparison_table:
        print(f"{c['tau_adv']:<14s} {c['eps_u']:<10s} {c['scenario']:<45s} "
              f"{c['v18']['avg_travel_time']:>8.2f} {c['max_pressure']['avg_travel_time']:>8.2f} "
              f"{c['delta_att_pct']:>+7.2f}% "
              f"{c['v18']['total_delay']:>10.1f} {c['max_pressure']['total_delay']:>10.1f} "
              f"{c['delta_delay_pct']:>+7.2f}%")

    # Write output.
    payload = {
        "experiment": "v1_8_param_sweep",
        "grid": {
            "tau_adv_variants": {k: dict(v) for k, v in TAU_ADV_VARIANTS.items()},
            "eps_u_variants": {k: dict(v) for k, v in EPS_U_VARIANTS.items()},
        },
        "scenarios": SCENARIOS,
        "seed": SEED,
        "steps": STEPS,
        "warmup": WARMUP,
        "action_interval": ACTION_INTERVAL,
        "network": NETWORK,
        "controllers": [CONTROLLER_V18, CONTROLLER_MP],
        "comparison_table": comparison_table,
        "combo_wins": combo_wins,
        "best_combo": best_combo,
        "all_results": all_results,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nResults written to: {OUT_PATH}")


if __name__ == "__main__":
    main()
