# v1.4 Candidate Convergence

Status: `PASSED`
Protocol status: `LOCKED`
Fingerprint: `2c6460070f313f97e95032a3c8d666f6015f3a0e4cf612cb27960a03af1e3f5b`

## Rankings

| Rank | Workstream | Candidate | Status | Score | Lock Eligible |
|---:|---|---|---|---:|---|
| 1 | v1-4-score-controller | finite_storage_primal_dual_v1_4_score | candidate | 11 | True |
| 2 | v1-4-objective-weights | finite_storage_primal_dual_v1_4_weighted | candidate | 9 | True |
| 3 | v1-4-scenario-diagnostics | v1-4-scenario-diagnostics-diagnostic | archived | 7 | False |
| 4 | v1-4-symbolic-policy | finite_storage_symbolic_v1_4 | rejected | 6 | False |

## Selected Candidate

{
  "workstream_id": "v1-4-score-controller",
  "candidate_id": "finite_storage_primal_dual_v1_4_score",
  "candidate_controller_id": "finite_storage_primal_dual_v1_4_score",
  "status": "candidate",
  "score": 11,
  "eligible_for_lock": true,
  "criteria": {
    "non_worsening_behavior": "pass",
    "strict_positive_signal": "partial",
    "binding_activation": "pass",
    "auditability": "pass",
    "implementation_reproducibility": "pass"
  },
  "reasons": [
    "Targets the dominant bounded-harm and low-action-change failure modes directly.",
    "Keeps action decomposition as the primary audit surface."
  ],
  "mechanism_description": "Change the live controller score decomposition while preserving auditable action components.",
  "changed_score_or_objective_terms": [
    "downstream_storage",
    "spillback",
    "switching",
    "service"
  ],
  "action_decomposition_schema": "pressure_action, finite_storage_action, selected_action, component_totals, movement_decompositions",
  "reproducible_implementation_pointer": "python scripts/run_v14_workstream_pilots.py --workstream v1-4-score-controller",
  "artifact": "experiments/dual_sensitivity/v1_4_workstreams/v1-4-score-controller-pilot.json"
}
