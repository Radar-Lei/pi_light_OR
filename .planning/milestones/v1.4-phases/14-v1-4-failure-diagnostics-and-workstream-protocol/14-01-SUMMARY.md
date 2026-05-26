---
phase: 14-v1-4-failure-diagnostics-and-workstream-protocol
plan: 01
status: complete
completed: 2026-05-26
---

# Plan 14-01 Summary

Created `scripts/run_v14_failure_diagnostics.py` and generated:

- `experiments/dual_sensitivity/v1_4_failure_diagnostics.json`
- `experiments/dual_sensitivity/v1_4_failure_diagnostics.md`

The diagnostic records the v1.3 strict Gate C status as `INCONCLUSIVE`, Phase 11 as `FAILED`, and summarizes 279 primary metric comparisons across bounded harm, inconclusive, non-worsening, and strict-positive-signal categories.

Verification: `python scripts/run_v14_failure_diagnostics.py` passed.
