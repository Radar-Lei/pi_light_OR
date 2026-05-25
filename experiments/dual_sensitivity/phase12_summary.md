# Phase 12 Reproducibility and Future-Claim Input Summary

This audit summary is generated from raw Phase 7/9/10/11 artifacts and is not manuscript prose.

- Package status: INCONCLUSIVE
- Requirements covered: CLAIM-03, REPRO-01, REPRO-02, REPRO-03
- Claim audit status: PASSED

## Source Statuses
- phase7_theory_separation: PASSED
- phase9_slack_binding_gates: PASSED
- phase10_baselines_stress_suite: SMOKE_ONLY
- phase11_long_horizon_paired_seed_evidence: FAILED
- phase11_gate_c_paired_evidence: INCONCLUSIVE

## Claim Inputs
- phase7_theory_separation: category=static_binding_separation_and_slack_recovery; allowed=True; status=PASSED; network=unknown; horizon=unknown; seeds=unknown; profile=unknown; gate_status=PASSED
- phase9_slack_binding_gates: category=slack_recovery_tie_and_static_binding_separation; allowed=True; status=PASSED; network=unknown; horizon=unknown; seeds=unknown; profile=unknown; gate_status=PASSED
- phase10_baselines_stress_suite: category=baseline_stress_capability_context; allowed=False; status=SMOKE_ONLY; network=single,arterial,grid_4x4; horizon=80; seeds=2; profile=smoke; gate_status=SMOKE_ONLY
- phase11_long_horizon_paired_seed_evidence: category=limitations_and_reproduction_notes; allowed=False; status=FAILED; network=arterial; horizon=3600; seeds=20; profile=main; gate_status=FAILED
- phase11_gate_c_paired_evidence: category=closed_loop_gate_c_status; allowed=False; status=INCONCLUSIVE; network=unknown; horizon=3600; seeds=unknown; profile=main; gate_status=FAILED

## Caveats
- A main artifact with missing executions is fail-closed as INCONCLUSIVE or FAILED, not a dominance claim.
- Gate A/B static checks only; no Gate C paired-seed closed-loop evidence
- Gate C is limited to Phase 11 predeclared binding stress regimes and required pressure/storage-aware comparators.
- Gate C must be PASSED before binding-regime closed-loop superiority inputs are claim-eligible
- No Gate C, paired-seed dominance, baseline suite, stress scenarios, long-horizon evidence, or closed-loop superiority claim.
- Phase 10 smoke rows are capability context only and are not imported as paired-seed dominance evidence.
- Phase 12 must regenerate final manuscript inputs and claim templates from raw Phase 11 artifacts.
- Phase 12 must regenerate final manuscript inputs and claim templates from raw artifacts.
- Pilot or spec-only artifacts validate plumbing only and are not Gate C dominance evidence.
- Pilot, dry-run, spec-only, metadata-only-demand, or missing-execution artifacts are not completed Gate C evidence.
- Slack/control rows are context only and cannot satisfy dominance evidence.
- long-horizon rows must be fully executed before supporting Gate C claims
- smoke/spec capability context only; not dominance or superiority evidence
- source status FAILED is not accepted for claim-ready evidence
- source status INCONCLUSIVE is not accepted for claim-ready evidence
- static theory/separation only; no closed-loop or deployment claim
