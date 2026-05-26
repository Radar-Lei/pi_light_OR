# v1.4 Research: Pitfalls

## Scientific Pitfalls

1. Treating the desired strong claim as established.
   - Prevention: v1.4 requirements must say the claim is allowed only after a `PASSED` locked Gate C.

2. Post-hoc scenario or threshold selection.
   - Prevention: workstream pilots may select a candidate, but final scenarios, metrics, thresholds, and seeds must be locked before the main run.

3. Weakening baselines after a failed result.
   - Prevention: keep max-pressure, capacity-aware pressure, and finite-storage double-pressure as required comparators. Cycle/actuated pressure can remain context comparators.

4. Confusing static separation with closed-loop dominance.
   - Prevention: Phase 7/9 remain theory/static evidence only.

5. Tuning against the same rows used for confirmation.
   - Prevention: separate exploratory pilot seeds from confirmation seeds, and record this split in generated artifacts.

## Engineering Pitfalls

1. Controller relabeling.
   - Do not rename a weak controller as a new method without a distinct action decomposition and manifest.

2. Artifact drift.
   - Every v1.4 artifact should record generated script, input paths, candidate ID, spec fingerprint, and claim readiness.

3. Silent demand/scenario metadata changes.
   - Preserve the Phase 11 checks that reject metadata-only demand multipliers and invalid SUMO behavior provenance.

4. Over-broad metric families.
   - The v1.3 family had 279 comparisons. More comparisons make strict success harder. v1.4 should diagnose and justify the metric family before locking it, not grow it casually.

5. Workstream merge confusion.
   - Workstream outputs need explicit status: rejected, candidate, selected, or archived. Only one selected route should feed the main confirmation gate.

