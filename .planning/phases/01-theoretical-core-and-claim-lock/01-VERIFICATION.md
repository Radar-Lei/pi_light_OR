---
phase: 01-theoretical-core-and-claim-lock
verified: 2026-05-22T17:00:08Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 1: Theoretical Core and Claim Lock Verification Report

**Phase Goal:** The project has a venue-credible OR/control theory core that explains dual movement sensitivity as generalized max-pressure and precisely states when pressure equivalence or scarcity correction should occur.
**Verified:** 2026-05-22T17:00:08Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|---|---|---|
| 1 | The manuscript notes or technical memo state a continuous capacitated network relaxation with queue conservation, movement service, phase compatibility, and capacity/storage/supply constraints. | VERIFIED | `refine-logs/THEORY_AND_CLAIMS.md` lines 57-119 define `THRY-01 — Continuous Capacitated Relaxation`, including queue conservation, phase compatibility, green/service budget, service bounds, and storage/supply/capacity constraints. |
| 2 | A reader can trace each movement-level dual-sensitivity term to upstream value, downstream value, storage/supply scarcity, or corridor/service correction. | VERIFIED | `refine-logs/THEORY_AND_CLAIMS.md` lines 120-199 separate `LinkDualPressure` from `FullServiceValue`, define upstream/downstream link values, storage/supply correction, phase/service correction, and model-dependent corridor correction. |
| 3 | The theory section clearly proves or formalizes why ordinary max-pressure/backpressure is recovered when binding constraints are absent or ranking-neutral. | VERIFIED | `THRY-03 — Pressure/Backpressure Special Case` in `refine-logs/THEORY_AND_CLAIMS.md` lines 201-259 states interior service, slack/ranking-neutral scarcity/resource assumptions and proves reduction to `x_i - x_j` phase scores. |
| 4 | The theory section identifies binding-regime conditions under which dual sensitivity may legitimately differ from ordinary pressure. | VERIFIED | `THRY-04 — Binding-Regime Scarcity Correction` in `refine-logs/THEORY_AND_CLAIMS.md` lines 260-327 states a sufficient rank-change inequality `C_b - C_a > P_a - P_b`, model-dependent correction terms, non-dominance language, and Phase 3 routing. |
| 5 | The symbolic recovery target has an explicit recovery-regret or finite-dictionary optimization-quality statement. | VERIFIED | `THRY-05 — Finite-Dictionary Symbolic Recovery Quality` in `refine-logs/THEORY_AND_CLAIMS.md` lines 328-416 defines `Pi(K,B,H,D)`, empirical oracle regret/value gap, solver gap proposition, and explicitly rejects global traffic-control optimality. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `refine-logs/THEORY_AND_CLAIMS.md` | Theory and claim-lock memo covering THRY-01 through THRY-05 | VERIFIED | Exists and passed `gsd-sdk query verify.artifacts` for all three plans. Substantive sections include definitions, theorem/propositions, proof sketches, validation alignment, and claim boundaries. |
| `refine-logs/THEORY_REVIEW_CHECKLIST.md` | Reviewer-facing checklist mapping THRY-01 through THRY-05 | VERIFIED | Exists and passed artifact verification. Lines 17-26 map each THRY requirement to memo section, theorem/proposition, proof status, validation evidence, allowed claim, disallowed claim, and status. |
| `.planning/phases/01-theoretical-core-and-claim-lock/01-REVIEW.md` | Clean review report | VERIFIED | Frontmatter reports `critical: 0`, `warning: 0`, `total: 0`, and `status: clean`. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `refine-logs/THEORY_AND_CLAIMS.md` | `scripts/run_dual_sanity.py` | Sign convention aligned to `equality_duals[up] - equality_duals[down]` | WIRED | `gsd-sdk verify.key-links` passed; memo lines 120-142 and 193-196 cite the implementation convention. |
| `refine-logs/THEORY_AND_CLAIMS.md` | `01-CONTEXT.md` | Locked generalized-pressure theory-scope decisions | WIRED | `gsd-sdk verify.key-links` passed; memo guardrails and THRY sections match context decisions. |
| `refine-logs/THEORY_AND_CLAIMS.md` | `pi_light_code/agent/rule_based/max_pressure.py` | Upstream-minus-downstream pressure phase score interpretation | WIRED | `gsd-sdk verify.key-links` passed; `max_pressure.py` lines 29-37 add upstream lane observation and subtract downstream lane observation. |
| `refine-logs/THEORY_AND_CLAIMS.md` | `.planning/ROADMAP.md` | Phase 3 kill-gate claim routing | WIRED | `gsd-sdk verify.key-links` passed; memo lines 319-327 route empirical usefulness to Phase 3. |
| `refine-logs/THEORY_AND_CLAIMS.md` | `scripts/run_sparse_recovery.py` | Oracle regret/value gap and finite dictionary constraints | WIRED | `gsd-sdk verify.key-links` passed; memo lines 389-398 align with sparse recovery outputs and regret objective. |
| `refine-logs/THEORY_REVIEW_CHECKLIST.md` | `refine-logs/THEORY_AND_CLAIMS.md` | Requirement-to-section mapping | WIRED | `gsd-sdk verify.key-links` passed; checklist rows map every THRY ID to the memo. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `refine-logs/THEORY_AND_CLAIMS.md` | Not applicable | Static theory memo | Not dynamic | N/A |
| `refine-logs/THEORY_REVIEW_CHECKLIST.md` | Not applicable | Static reviewer checklist | Not dynamic | N/A |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Dual sanity validation passes | `python /home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json` | Printed `{"status": "PASSED", "out": "/tmp/phase1_dual_sanity_check.json"}` and exited 0 | PASS |
| Sparse recovery scaffold validation passes | `python /home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py --states /home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/targeted_bottleneck_states.json --out /tmp/phase1_sparse_recovery_check.json` | Printed `{"status": "PASSED", "out": "/tmp/phase1_sparse_recovery_check.json", "num_examples": 16}` and exited 0 | PASS |
| Overclaim phrase gate | `grep -n -E "universally dominates|always beats|guarantees superiority|dominates max-pressure" ...` | No matches in phase theory/checklist/review artifacts | PASS |
| Debt-marker scan | `grep -n -E "TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER|placeholder|coming soon|not yet implemented|not available" ...` | No matches | PASS |

### Probe Execution

| Probe | Command | Result | Status |
|---|---|---|---|
| No phase probe scripts declared | N/A | Validation is script-gate based through `run_dual_sanity.py` and `run_sparse_recovery.py` | SKIP |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| THRY-01 | `01-01-PLAN.md`, `01-03-PLAN.md` | Continuous capacitated traffic-network relaxation with queue conservation, movement service, phase compatibility, and storage/supply/capacity constraints. | SATISFIED | REQUIREMENTS.md lines 11 and 83 map THRY-01 to Phase 1; memo lines 57-119 implement it; checklist row line 21 maps it to Definition 1. |
| THRY-02 | `01-01-PLAN.md`, `01-03-PLAN.md` | Movement-level dual-sensitivity decomposition with upstream, downstream, storage/supply, and corridor/service terms. | SATISFIED | REQUIREMENTS.md lines 12 and 84 map THRY-02 to Phase 1; memo lines 120-199 separate `LinkDualPressure` and `FullServiceValue`; checklist row line 22 covers validation scope and disallowed claims. |
| THRY-03 | `01-02-PLAN.md`, `01-03-PLAN.md` | Max-pressure/backpressure special case under nonbinding or ranking-neutral constraints. | SATISFIED | REQUIREMENTS.md lines 13 and 85 map THRY-03 to Phase 1; memo lines 201-259 state theorem and proof sketch; checklist row line 23 maps it to Theorem 1. |
| THRY-04 | `01-02-PLAN.md`, `01-03-PLAN.md` | Spillback/scarcity correction term showing how dual sensitivity can differ from ordinary pressure in binding regimes. | SATISFIED | REQUIREMENTS.md lines 14 and 86 map THRY-04 to Phase 1; memo lines 260-327 formalize sufficient rank-change and non-dominance; checklist row line 24 maps it to Proposition 1. |
| THRY-05 | `01-03-PLAN.md` | Recovery-regret or optimization-quality result for finite dictionary symbolic policy recovery. | SATISFIED | REQUIREMENTS.md lines 15 and 87 map THRY-05 to Phase 1; memo lines 328-416 state finite-dictionary regret/quality proposition; checklist row line 25 maps it to Proposition 2. |

No orphaned Phase 1 requirements found: `.planning/REQUIREMENTS.md` maps only THRY-01 through THRY-05 to Phase 1, and all appear in plan frontmatter.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| None | N/A | No unreferenced `TBD`, `FIXME`, `XXX`, `TODO`, `HACK`, or placeholder markers in phase artifacts | None | No blocker anti-pattern found. |
| `refine-logs/THEORY_AND_CLAIMS.md`, `refine-logs/THEORY_REVIEW_CHECKLIST.md` | Several | Mentions of `global traffic-control optimality` occur only in disallowed-claim / not-allowed contexts | Info | This is claim discipline, not an overclaim. Exact universal dominance phrase gate has no matches. |

### Human Verification Required

None.

### Gaps Summary

No blocking gaps found. The Phase 1 goal is achieved against the roadmap success criteria and the requested THRY-01 through THRY-05 requirements. The artifacts are substantive, cross-linked to validation scripts and the max-pressure baseline, avoid universal pressure-dominance claims, and the validation scripts pass in this verification run.

---

_Verified: 2026-05-22T17:00:08Z_
_Verifier: Claude (gsd-verifier)_
