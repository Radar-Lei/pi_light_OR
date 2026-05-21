# Pipeline Summary

**Problem**: compact programmatic traffic-signal policies need OR-principled network-coupling signals rather than raw neighbor-state augmentation.  
**Final Method Thesis**: continuous store-and-forward/CTM-lite dual sensitivities can guide sparse recovery of compact symbolic traffic-signal programs with interpretable neighbor coordination.  
**Final Verdict**: READY WITH NARROWED CLAIM  
**Date**: 2026-05-20

## Final Deliverables

- Proposal: `refine-logs/FINAL_PROPOSAL.md`
- Review summary: `refine-logs/REVIEW_SUMMARY.md`
- Refinement report: `refine-logs/REFINEMENT_REPORT.md`
- Experiment plan: `refine-logs/EXPERIMENT_PLAN.md`
- Experiment tracker: `refine-logs/EXPERIMENT_TRACKER.md`

## Contribution Snapshot

- **Dominant contribution**: OR dual-sensitivity-guided symbolic recovery for deployable network signal control.
- **Optional supporting contribution**: periodic dual recomputation for demand-shift robustness if nominal prices fail.
- **Explicitly rejected complexity**: PI-Light-extension-first framing, integer-MILP shadow prices, method menu, GPU-heavy MARL, raw imitation-only recovery.

## Must-Prove Claims

1. Dual sensitivities are meaningful OR coordination signals, not disguised queue/slack heuristics.
2. Sparse MIP recovery yields compact symbolic policies with low oracle regret.
3. Dual-guided symbolic policies beat raw/all/random/local symbolic policies under equal complexity in coupled SUMO networks.
4. The method is CPU-feasible and deployable online.

## First Runs to Launch

1. Block 0 dual finite-difference and pressure-special-case sanity.
2. Block 1 offline sparse recovery on single + arterial sampled states.
3. Block 3 three-seed arterial pilot with local/raw/random/dual symbolic variants plus max-pressure.

## Main Risks

- **Risk**: duals collapse to ordinary pressure.  
  **Mitigation**: prove pressure special case and test storage-binding scenarios where downstream scarcity adds value.

- **Risk**: dual-guided atoms do not outperform raw/random atoms.  
  **Mitigation**: stop after Gate B and revise atom mapping/relaxation.

- **Risk**: C-MP/MPC dominates.  
  **Mitigation**: claim interpretability, compactness, and regret recovery rather than absolute performance dominance.

- **Risk**: reviewer sees PI-Light derivative framing.  
  **Mitigation**: frame as general programmatically interpretable RL/control extended by OR dual sensitivities.

## Next Action

Proceed to implementation / experiment bridge for Block 0 and Block 1.
