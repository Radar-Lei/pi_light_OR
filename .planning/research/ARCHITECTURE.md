# v1.4 Research: Architecture

## Existing Flow

The current evidence path is:

1. Controller execution through SUMO/TraCI.
2. Phase 11 paired-seed artifact generation.
3. Strict Gate C recomputation from raw rows.
4. Phase 12 reproducibility and claim input regeneration.
5. Claim audit guards against overclaiming.

v1.4 should preserve this shape. The new architecture adds an exploratory layer before the locked Gate C.

## Proposed v1.4 Flow

### Phase A: Failure Diagnosis

Input:
- `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json`
- `experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json`
- `experiments/dual_sensitivity/phase12_claim_inputs.json`

Output:
- `experiments/dual_sensitivity/v1_4_failure_diagnostics.json`
- `experiments/dual_sensitivity/v1_4_failure_diagnostics.md`

### Phase B: Parallel Workstream Exploration

Each workstream should have its own state and artifacts:

- `.planning/workstreams/v1-4-score-controller`
- `.planning/workstreams/v1-4-objective-weights`
- `.planning/workstreams/v1-4-scenario-diagnostics`
- `.planning/workstreams/v1-4-symbolic-policy`

Exploratory outputs should be named with `v1_4_pilot_*` or workstream-specific prefixes and must contain `claim_ready: false`.

### Phase C: Convergence and Lock

The main milestone should consolidate workstream outputs into a single locked protocol:

- candidate controller ID
- source commit/hash or manifest
- scenario family
- comparator set
- seeds
- demand multipliers
- metrics
- strict pass/fail rules
- artifact paths

### Phase D: Main Gate C and Claim Refresh

The selected method should flow through a v1.4 version of the Phase 11/13 machinery:

- run selected candidate against required baselines
- write full paired-seed evidence artifact
- run strict Gate C
- refresh Phase 12-style claim inputs
- fail closed on every non-PASSED source

## Integration Constraints

- Do not mutate v1.3 artifacts.
- Do not reuse pilot rows as final main rows unless the protocol was locked before those rows were generated.
- Do not remove strong baselines from the confirmation protocol.
- Do not weaken the all-primary-metric non-worsening requirement unless a new requirement explicitly records a scientifically defensible alternative and the old Gate C result remains non-claim-ready.

