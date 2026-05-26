# v1.4 Research: Stack

## Scope

Milestone v1.4 should reuse the existing CPU/SUMO/Python stack. The goal is not to add a new optimizer ecosystem; it is to diagnose why the completed v1.3 Gate C failed, test candidate method changes in isolated workstreams, and lock one candidate into a new predeclared Gate C.

## Existing Stack to Preserve

- Python experiment scripts under `scripts/`.
- SUMO/TraCI closed-loop execution through `run_closed_loop_sumo.py` and suite wrappers.
- Existing Phase 11 paired-seed evidence runner and strict Gate C checker:
  - `scripts/run_phase11_paired_evidence.py`
  - `scripts/run_gate_c_paired_evidence.py`
  - `scripts/run_phase12_reproducibility_inputs.py`
- JSON/CSV artifacts under `experiments/dual_sensitivity/`.
- Pytest-based script and artifact contracts.

## Stack Additions Needed

1. v1.3 failure diagnostics script.
   - Read `phase11_long_horizon_paired_seed_evidence.json`.
   - Summarize bounded harm, inconclusive, and non-worsening metric families by scenario, demand multiplier, comparator, and metric.
   - Emit a compact diagnostic JSON and Markdown report for method selection.

2. Candidate method registry.
   - Add candidate controller IDs without replacing or relabeling the v1.3 `finite_storage_primal_dual` controller.
   - Each candidate must expose action decomposition fields compatible with Phase 6/8/9 audit expectations.

3. Workstream-local pilot runners.
   - Keep smoke/pilot outputs separate from final Gate C artifacts.
   - Mark exploratory outputs as not claim-ready.
   - Preserve row-level provenance and controller/scenario/seed/demand metadata.

4. v1.4 Gate C protocol generator.
   - Produce a locked spec from the selected candidate.
   - Reject threshold, metric, comparator, or scenario changes after lock.
   - Keep the existing fail-closed behavior for missing rows, non-PASSED source status, bad demand provenance, and overclaim language.

## Dependency Guidance

No required new third-party dependency is justified at the milestone start. If a workstream needs optimization, prefer existing SciPy/HiGHS or stdlib deterministic checks before adding packages.

