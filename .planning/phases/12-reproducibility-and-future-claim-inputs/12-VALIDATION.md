# Phase 12: Validation Strategy

**Generated:** 2026-05-24
**Phase:** Reproducibility and Future Claim Inputs

## Test Framework

- Use direct Python assertion scripts under `tests/test_*.py`.
- Do not require pytest configuration.
- Default quick validation command: `python tests/test_phase12_reproducibility_inputs.py`.
- Full repository validation command: `for f in tests/test_*.py; do python "$f"; done`.

## Requirements to Tests

| Requirement | Required behavior | Validation command |
|---|---|---|
| CLAIM-03 | Generated claim inputs preserve simulator, network, horizon, seed, profile, and gate-status qualifiers; deployment or universal-dominance language is rejected. | `python tests/test_phase12_reproducibility_inputs.py` |
| REPRO-01 | Derived JSON, CSV, Markdown, and claim-audit outputs are generated from raw Phase 7/9/10/11 artifacts and every derived file has provenance. | `python tests/test_phase12_reproducibility_inputs.py` |
| REPRO-02 | Reproduction manifest contains CPU/SUMO commands for fast validation, artifact regeneration, strict gates, and opt-in long-horizon execution without GPU dependencies. | `python tests/test_phase12_reproducibility_inputs.py` |
| REPRO-03 | Future claim inputs express bounded slack recovery/tie and binding-regime-only superiority, while INCONCLUSIVE or smoke-only sources remain limitations/context. | `python tests/test_phase12_reproducibility_inputs.py` |

## Required Synthetic Coverage

- Missing or unparseable upstream artifact is surfaced as `FAILED` or `INCONCLUSIVE`, not silently ignored.
- Non-`PASSED` upstream statuses propagate to derived package status and claim eligibility.
- Phase 10 `SMOKE_ONLY` or equivalent capability evidence cannot become dominance evidence.
- Phase 11 and Gate C `INCONCLUSIVE` sources cannot produce superiority claims.
- Generated JSON/CSV/Markdown text is scanned through claim policy and Phase-12-specific forbidden phrases.
- Every derived output path appears in the provenance manifest with raw source paths, source statuses, commands, requirements, and caveats.
- Strict mode exits nonzero unless required evidence statuses and claim audit pass.
- Non-strict mode may write an auditable `INCONCLUSIVE` package.

## Phase Gate Commands

```bash
python tests/test_phase12_reproducibility_inputs.py
python scripts/run_phase12_reproducibility_inputs.py --out-dir experiments/dual_sensitivity
python scripts/run_phase12_reproducibility_inputs.py --out-dir experiments/dual_sensitivity --strict
```

If the current Phase 11 Gate C artifact remains `INCONCLUSIVE`, the strict command is expected to exit nonzero; that fail-closed behavior is part of the validation contract.

## Full Validation

```bash
for f in tests/test_*.py; do python "$f"; done
```

## Wave 0 Gaps

- `scripts/run_phase12_reproducibility_inputs.py` does not exist yet.
- `tests/test_phase12_reproducibility_inputs.py` does not exist yet.
- Phase 12 generated artifacts do not exist yet.

These gaps are implementation targets, not blockers to planning.
