#!/usr/bin/env python3
"""Behavior checks for the Phase 3 static regime generator."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_static_regime_states.py"


EXPECTED_SAMPLE_FIELDS = {
    "time",
    "queues",
    "vehicle_counts",
    "capacities",
    "tls_movements",
    "regime",
    "regime_detail",
    "generated_by",
    "finite_storage_state",
    "objective_components",
}


EXPECTED_STATE_FIELDS = {
    "downstream_storage",
    "residual_receiving_capacity",
    "spillback_blocking",
    "switching_loss_state",
    "service_urgency",
    "incident_capacity_drop",
}


EXPECTED_OBJECTIVE_FIELDS = {
    "delay",
    "unfinished_vehicle_penalty",
    "spillback_blocking_time",
    "switching_lost_time",
}


EXPECTED_REGIMES = {
    "slack",
    "storage_binding",
    "incident_capacity_drop",
    "demand_shift_proxy",
}


def run_generator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_generator_emits_schema_compatible_regime_samples(tmp_path: Path) -> None:
    out = tmp_path / "block3_regime_states.json"
    result = run_generator("--target-per-regime", "10", "--out", str(out))

    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    regimes = {sample["regime"] for sample in payload["samples"]}

    assert EXPECTED_REGIMES <= regimes
    assert payload["num_samples"] == len(payload["samples"])
    assert payload["target_per_regime"] == 10
    assert "regime_status" in payload
    assert all(EXPECTED_SAMPLE_FIELDS <= set(sample) for sample in payload["samples"])
    assert all(set(sample["finite_storage_state"]) == EXPECTED_STATE_FIELDS for sample in payload["samples"])
    assert all(set(sample["objective_components"]) == EXPECTED_OBJECTIVE_FIELDS for sample in payload["samples"])
    assert all("proxy_reason" not in sample or "finite_storage_state" in sample for sample in payload["samples"])


def test_generator_rejects_invalid_cli_inputs(tmp_path: Path) -> None:
    bad_target = run_generator("--target-per-regime", "0", "--out", str(tmp_path / "bad.json"))
    bad_regime = run_generator("--regimes", "not_a_regime", "--out", str(tmp_path / "bad.json"))

    assert bad_target.returncode != 0
    assert "--target-per-regime must be positive" in bad_target.stderr
    assert bad_regime.returncode != 0
    assert "Unknown regimes" in bad_regime.stderr


def main() -> None:
    with tempfile.TemporaryDirectory() as raw_tmp:
        tmp_path = Path(raw_tmp)
        test_generator_emits_schema_compatible_regime_samples(tmp_path)
        test_generator_rejects_invalid_cli_inputs(tmp_path)


if __name__ == "__main__":
    main()
