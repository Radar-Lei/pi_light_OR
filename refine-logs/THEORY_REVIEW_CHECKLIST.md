# Theory Review Checklist

**Date**: 2026-05-22  
**Phase**: 01 — Theoretical Core and Claim Lock  
**Artifact under review**: `refine-logs/THEORY_AND_CLAIMS.md`

## Purpose

This checklist maps Phase 1 requirements THRY-01 through THRY-05 to the theory memo sections, proposition blocks, proof sketches, validation sources, and claim boundaries. It is a reviewer-facing gate: every theory claim must be traceable to a written model/proposition and must preserve the Phase 3 routing discipline for empirical dual-vs-pressure claims.

## Gate Status

- Gate A — Continuous relaxation and dual validity: **DRAFTED / SCRIPT-CHECKED FOR BLOCK 0 LINK-DUAL CASES** through `THRY-01`, `THRY-02`, and `scripts/run_dual_sanity.py`.
- Gate B — Pressure special case and scarcity correction: **DRAFTED / CLAIM-BOUNDED** through `THRY-03`, `THRY-04`, and Phase 3 routing language; phase-specific, service-resource, and corridor corrections are proof-only until targeted validation scenarios exist.
- Gate C — Finite-dictionary recovery quality: **DRAFTED / SCAFFOLD-CHECKED FOR EMPIRICAL REGRET TARGETS** through `THRY-05` and `scripts/run_sparse_recovery.py`.
- Gate D — Closed-loop traffic performance: **DEFERRED** to Phase 4 after the Phase 3 static pressure-failure kill gate.

## THRY Requirement Traceability

| Requirement | Requirement summary | `THEORY_AND_CLAIMS.md` section | Theorem / lemma / proposition | Proof-sketch status | Validation command or file assertion | Allowed claim | Disallowed claim | Status |
|---|---|---|---|---|---|---|---|---|
| THRY-01 | Define a continuous capacitated traffic-network relaxation with queue conservation, movement service, phase compatibility, and storage/supply/capacity constraints. | `THRY-01 — Continuous Capacitated Relaxation` | `Definition 1 — Capacitated movement-service relaxation` | Present through model statement, assumptions, proof-ready properties, and implementation-alignment notes. | `grep -q "queue conservation" refine-logs/THEORY_AND_CLAIMS.md` and `python scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json` | The memo defines a store-and-forward / CTM-lite LP relaxation suitable for LP dual sensitivity analysis. | The relaxation alone proves closed-loop traffic-control optimality or deployment-ready advantage. | DONE |
| THRY-02 | Derive movement-level dual-sensitivity decomposition with upstream, downstream, storage/supply, and optional corridor/service terms. | `THRY-02 — Movement-Level Dual-Sensitivity Decomposition` and `Sign Convention for Dual Movement Values` | `Lemma 1 — Movement marginal service value` | Present through KKT/LP sensitivity proof sketch and finite-difference alignment. | `grep -q "dual-sensitivity decomposition" refine-logs/THEORY_AND_CLAIMS.md` and `python scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json`; the script checks the Block 0 link-dual/finite-difference comparison, not phase-specific or corridor reduced-cost terms. | Link-dual pressure is an interpretable marginal component, and full service value may add explicit reduced-cost corrections from written constraints. | Unmodeled corridor/service dual terms exist without a corresponding primal constraint, or Block 0 scripts validate every generalized reduced-cost case. | DONE |
| THRY-03 | Prove pressure/backpressure is a special case when storage/supply/corridor constraints are nonbinding or ranking-neutral. | `THRY-03 — Pressure/Backpressure Special Case` | `Theorem 1 — Pressure/backpressure is the slack-regime dual ranking` | Present through theorem assumptions, algebraic reduction, implementation alignment, and script-gate alignment. | `grep -q "THRY-03" refine-logs/THEORY_AND_CLAIMS.md` and `python scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json`; the script validates nonbinding storage/link-dual pressure cases, while active phase/resource-bound assumptions remain proof obligations. | Ordinary pressure/backpressure is recovered in interior slack or ranking-neutral regimes and remains a strong baseline. | Pressure equivalence means the proposed dual-sensitivity view is unnecessary, or scarcity-aware terms are beneficial in every regime. | DONE |
| THRY-04 | Formalize spillback/scarcity correction showing how dual sensitivity can differ from ordinary pressure in binding regimes. | `THRY-04 — Binding-Regime Scarcity Correction` | `Proposition 1 — Sufficient binding-regime rank-change condition` | Present through sufficient rank-change inequality and model-dependent correction interpretation. | `grep -q "binding-regime" refine-logs/THEORY_AND_CLAIMS.md` and `grep -Eq "scarcity|storage|supply" refine-logs/THEORY_AND_CLAIMS.md`; this is a source assertion/proof check, not a script validation of phase-specific or corridor correction dynamics. | Binding storage/supply or written service-feasibility multipliers can legitimately change movement rankings when their correction exceeds the pressure gap. | Every binding constraint improves closed-loop control, or any scarcity correction establishes empirical dominance before Phase 3. | DONE |
| THRY-05 | State a recovery-regret or optimization-quality result for finite dictionary symbolic policy recovery. | `THRY-05 — Finite-Dictionary Symbolic Recovery Quality` | `Proposition 2 — Deterministic finite-dictionary empirical recovery quality` | Present through finite-class definition, empirical oracle-regret target, solver-gap statement, and optional IID finite-sample corollary. | `grep -q "THRY-05" refine-logs/THEORY_AND_CLAIMS.md` and `python scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json --out /tmp/phase1_sparse_recovery_check.json`; the script checks the existing targeted sparse-recovery scaffold and empirical regret output fields, not full Phase 2 recovery completeness. | Recovered symbolic policies can be evaluated by empirical oracle regret/value gap relative to the best policy in the same finite dictionary plus optimization gap. | Action agreement alone proves recovery quality, finite-dictionary recovery proves global traffic-control optimality, or the scaffold proves full Phase 2 implementation is complete. | DONE |

## Claim-Discipline Gate

Before using any Phase 1 theory language in manuscript or experiment summaries, apply this gate:

1. The claim must name the relevant THRY section and proposition.
2. The claim must distinguish model-internal optimization quality from closed-loop SUMO performance.
3. The claim must route empirical dual-vs-pressure interpretation to **Phase 3**.
4. The claim must not convert a finite-sample or finite-dictionary statement into a global traffic-control optimality statement.

### Blocked Phrase Patterns

Do not use the following universal-dominance patterns as manuscript claims before Phase 3/Phase 4 evidence. They are written here as split tokens so automated artifact scans do not mistake the checklist for an asserted claim:

- `universally` + `dominates`
- `always` + `beats`
- `guarantees` + `superiority`
- `dominates` + `max-pressure`

Safer replacements:

- “recovers pressure/backpressure in slack or ranking-neutral regimes”
- “may add scarcity-aware corrections when explicitly modeled constraints bind”
- “is evaluated by empirical oracle regret/value gap within a finite dictionary”
- “Phase 3 determines whether the evidence supports dual advantage, pressure-equivalent symbolic recovery, or diagnostic framing”

## Reviewer Audit Checklist

- [x] THRY-01 maps to a model definition with conservation, service, phase feasibility, and storage/supply constraints.
- [x] THRY-02 maps to a movement-value lemma and a sign convention aligned with finite-difference validation.
- [x] THRY-03 maps to a pressure/backpressure special-case theorem rather than an anti-pressure claim.
- [x] THRY-04 maps to a sufficient rank-change proposition and Phase 3 empirical routing.
- [x] THRY-05 maps to a finite-dictionary empirical oracle-regret/value-gap proposition with program-size, neighbor-use, and dual-price dependence budgets or penalties.
- [x] No Phase 1 row claims global traffic-control optimality.
- [x] No Phase 1 row claims Phase 1 evidence settles empirical ordering against pressure-style or capacity-aware pressure baselines.
