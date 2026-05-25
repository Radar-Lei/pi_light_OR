---
phase: 07-theory-and-separation-package
plan: 01
subsystem: theory-separation
tags: [python, pytest, json, finite-storage, max-pressure, theory, claim-audit]

requires:
  - phase: 06-claim-discipline-and-explicit-state-foundation
    provides: bounded claim policy, finite_storage_state schema, objective_components schema, and fail-closed audit surfaces
  - phase: 01-theoretical-core-and-claim-lock
    provides: movement-value sign convention and pressure/backpressure special-case theory
provides:
  - THRY-01 slack finite-storage recovery theorem/checker evidence
  - THRY-02 explicit binding storage/spillback action-separation example
  - THRY-03 strict predeclared one-step objective improvement artifact
  - THRY-04 constrained LP oracle regret guarantee candidate
  - Claim-safe Phase 7 theory memo and deterministic JSON checker artifact
affects: [phase-07, phase-08, phase-09, finite-storage, theory-separation, claim-discipline]

tech-stack:
  added: []
  patterns:
    - stdlib deterministic checker/generator
    - Phase 6 schema validator reuse
    - generated JSON artifact with THRY requirement coverage
    - pytest contract for static theory surfaces
    - claim audit with temporary Phase 7 outputs plus default repository audit refresh

key-files:
  created:
    - .planning/phases/07-theory-and-separation-package/07-CONTEXT.md
    - .planning/phases/07-theory-and-separation-package/07-RESEARCH.md
    - .planning/phases/07-theory-and-separation-package/07-PATTERNS.md
    - .planning/phases/07-theory-and-separation-package/07-VALIDATION.md
    - .planning/phases/07-theory-and-separation-package/07-01-PLAN.md
    - .planning/phases/07-theory-and-separation-package/07-01-SUMMARY.md
    - scripts/check_theory_separation.py
    - tests/test_theory_separation.py
    - experiments/dual_sensitivity/phase7_theory_separation.json
    - refine-logs/THEORY_AND_SEPARATION.md
  modified:
    - experiments/dual_sensitivity/phase6_claim_policy.json
    - experiments/dual_sensitivity/phase6_claim_audit.json

key-decisions:
  - "Phase 7 uses a deterministic stdlib analytic checker rather than LP dual extraction; SciPy dual validation remains optional future hardening."
  - "The minimal separation example uses explicit storage/spillback binding fields only; incident and switching examples are deferred unless later phases need them."
  - "Phase 7 claim audit for new surfaces writes to /tmp outputs, while the default Phase 6 audit artifacts are refreshed separately to include the new theory memo in repository-wide scan scope."
  - "Constrained LP oracle regret is the only Phase 7 additional guarantee candidate and is labeled finite-sample/oracle-relative."

patterns-established:
  - "Static theory examples validate with Phase 6 validate_state_objective_sample before becoming evidence artifacts."
  - "Binding action separation must pair pressure-vs-finite-storage action difference with positive predeclared one-step objective margin."
  - "Theory memo references generated JSON rather than manually inventing unvalidated numbers."

requirements-completed: [THRY-01, THRY-02, THRY-03, THRY-04]
completed: 2026-05-24
---

# Phase 07 Plan 01: Theory and Separation Package Summary

**Bounded finite-storage primal-dual theory package with deterministic slack-recovery and binding-separation artifacts**

## Accomplishments

- Created `scripts/check_theory_separation.py`, a stdlib deterministic checker that builds static Phase 7 examples, validates Phase 6 `finite_storage_state` and `objective_components`, recomputes pressure and finite-storage scores, and writes a passed JSON artifact.
- Generated `experiments/dual_sensitivity/phase7_theory_separation.json` with `status: PASSED`, THRY-01~THRY-04 coverage, slack recovery, storage/spillback binding action separation, strict one-step objective improvement, and constrained LP oracle regret metadata.
- Created `tests/test_theory_separation.py` covering slack recovery/tie behavior, explicit binding action separation, predeclared objective margin, checker CLI output, memo markers, claim-safe wording, and guarantee candidate boundaries.
- Created `refine-logs/THEORY_AND_SEPARATION.md` with THRY-01~THRY-04 theorem/counterexample/proof-sketch sections and explicit claim-discipline guardrails.
- Created Phase 7 planning context, research, patterns, validation, and executable plan artifacts.
- Refreshed Phase 6 claim policy/audit artifacts after default repository-wide audit so the new Phase 7 theory memo is included in checked paths and historical-evidence quarantine metadata.

## Files Created/Modified

- `.planning/phases/07-theory-and-separation-package/07-CONTEXT.md` - Phase 7 boundary, decisions, upstream interfaces, and autonomous defaults.
- `.planning/phases/07-theory-and-separation-package/07-RESEARCH.md` - implementation-ready research with resolved open questions.
- `.planning/phases/07-theory-and-separation-package/07-PATTERNS.md` - analog mapping for memo/checker/tests/JSON artifact patterns.
- `.planning/phases/07-theory-and-separation-package/07-VALIDATION.md` - Phase 7 validation strategy and fail-closed audit commands.
- `.planning/phases/07-theory-and-separation-package/07-01-PLAN.md` - executable plan checked PASS after blocker fixes.
- `.planning/phases/07-theory-and-separation-package/07-01-SUMMARY.md` - this summary.
- `scripts/check_theory_separation.py` - deterministic Phase 7 checker/generator.
- `tests/test_theory_separation.py` - pytest coverage for THRY-01~THRY-04 artifacts.
- `experiments/dual_sensitivity/phase7_theory_separation.json` - generated machine-readable theory separation artifact.
- `refine-logs/THEORY_AND_SEPARATION.md` - bounded theory memo.
- `experiments/dual_sensitivity/phase6_claim_policy.json` - refreshed default policy timestamp from repository-wide audit.
- `experiments/dual_sensitivity/phase6_claim_audit.json` - refreshed default audit including new Phase 7 memo path.

## Decisions Made

- Used a minimal two-phase storage/spillback example for THRY-02/THRY-03 to keep the proof auditable and avoid Phase 8 controller scope.
- Kept the finite-storage score in the checker as an analytic static score: pressure plus declared storage/scarcity corrections. This is a theory artifact, not runtime control code.
- Used unit nonnegative weights over Phase 6 objective component keys for the one-step objective.
- Routed Phase 7-specific claim audits to `/tmp/phase7_claim_policy.json` and `/tmp/phase7_claim_audit.json` to avoid overwriting repository-wide Phase 6 guard artifacts during targeted checks.

## Deviations from Plan

### Auto-fixed Issues

**1. Plan checker found red-test-only Task 1**
- **Issue:** Initial Task 1 verification would run pytest before `check_theory_separation.py` existed.
- **Fix:** Updated Task 1 to require compile-safe tests with deferred checker imports and verify via `python3 -m py_compile`.

**2. Plan checker found fail-open memo/audit verification**
- **Issue:** Initial Task 3 allowed missing memo paths through `--allow-missing-paths` and optional memo tests.
- **Fix:** Updated plan/research/validation so memo and JSON must exist and Phase 7 claim audit runs without missing-path allowance.

**3. Targeted Phase 7 claim audit initially rewrote default Phase 6 artifacts**
- **Issue:** Running `audit_claim_discipline.py` without explicit outputs writes default Phase 6 policy/audit files.
- **Fix:** Restored default repository-wide audit, then updated Phase 7 validation commands to write targeted audit outputs under `/tmp`.

## Issues Encountered

- None unresolved. The Phase 6 claim audit artifact legitimately changed after repository-wide audit because `refine-logs/THEORY_AND_SEPARATION.md` is now part of the scanned `refine-logs` directory.

## Known Stubs

None detected in Phase 7 created source/test/theory artifacts.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: theory_artifact_integrity | `scripts/check_theory_separation.py` | Static theory JSON crosses into future evidence surfaces; mitigated by deterministic generation and Phase 6 schema validation. |
| threat_flag: claim_surface | `refine-logs/THEORY_AND_SEPARATION.md` | Theory memo contains claim-facing language; mitigated by tests and `audit_claim_discipline.py`. |
| threat_flag: scope_boundary | `experiments/dual_sensitivity/phase7_theory_separation.json` | Static one-step artifact could be mistaken for closed-loop evidence; mitigated by explicit static/theory scope fields and memo guardrails. |

## Verification

- `python3 -m py_compile tests/test_theory_separation.py` — passed.
- `python3 scripts/check_theory_separation.py --out experiments/dual_sensitivity/phase7_theory_separation.json` — passed.
- `python3 -m pytest tests/test_theory_separation.py -q` — 6 passed.
- `python3 -m pytest tests/test_finite_storage_schema.py tests/test_claim_discipline.py tests/test_theory_separation.py -q` — 20 passed.
- `python3 scripts/audit_claim_discipline.py --paths refine-logs/THEORY_AND_SEPARATION.md experiments/dual_sensitivity/phase7_theory_separation.json --policy-out /tmp/phase7_claim_policy.json --audit-out /tmp/phase7_claim_audit.json` — passed.
- `python3 -m pytest tests -q` — 47 passed.

## Next Phase Readiness

- Phase 8 can consume the static score/action/objective decomposition concepts when implementing a live finite-storage primal-dual controller.
- Phase 9 can reuse `phase7_theory_separation.json` as a theory-backed input pattern for slack and binding kill gates.
- Phase 12 can include the bounded theory memo and generated JSON in future claim-input/reproducibility packaging without paper drafting.

---
*Phase: 07-theory-and-separation-package*  
*Completed: 2026-05-24*
