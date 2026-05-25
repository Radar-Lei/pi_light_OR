# Phase 12: Reproducibility and Future Claim Inputs - Context

**Gathered:** 2026-05-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 12 delivers an auditable reproducibility and future-claim input layer for the v1.1 finite-storage separation milestone. It must regenerate new evidence summaries, table/figure-data inputs, claim-audit summaries, and bounded future manuscript-input artifacts from raw JSON/CSV outputs rather than manual transcription.

This phase must not draft the paper, write related work, create final manuscript prose, perform submission preparation, expand benchmarks, or convert `INCONCLUSIVE` Phase 11 artifacts into performance claims. It may produce machine-readable future inputs and templates that explicitly preserve simulator-, network-, horizon-, seed-, profile-, and gate-status qualifiers.

</domain>

<decisions>
## Implementation Decisions

### D-12-01 Reproducibility Package Scope
- Build a dedicated Phase 12 reproducibility package/harness rather than editing final paper text. Recommended artifact family: `experiments/dual_sensitivity/phase12_*` plus generated CSV/Markdown/JSON inputs under the existing experiment artifact directory.
- The package must regenerate all new v1.1 result summaries from raw artifacts: Phase 7 theory/separation, Phase 9 Gate A/B, Phase 10 stress/baseline suite, Phase 11 paired evidence, and Phase 11 Gate C.
- Reports should distinguish source artifact status (`PASSED`, `FAILED`, `INCONCLUSIVE`, `PILOT_ONLY`) and must not summarize an inconclusive artifact as evidence of dominance.

### D-12-02 Future Claim Inputs and Claim Discipline
- Produce bounded future claim inputs, not manuscript prose. Acceptable outputs include machine-readable claim templates, limitations/caveat blocks, status-qualified bullet inputs, and claim-audit JSON/Markdown summaries.
- Every future claim input must preserve qualifiers: simulator/network/horizon/seed/profile/gate-status relative, binding-regime-only for superiority language, slack-regime recovery/tie as expected behavior, and no deployment or universal dominance language.
- Phase 12 must include a fail-closed claim audit that scans generated outputs for forbidden language and specifically prevents v1.0/Phase 10/Phase 11 `INCONCLUSIVE` artifacts from being described as superiority evidence.

### D-12-03 CPU/SUMO Reproduction Commands
- Provide a CPU/SUMO-oriented reproduction command or manifest that can rerun finite-storage separation gates and long-horizon summary/gate checks without GPU dependencies.
- The harness should include commands for fast validation (`tests/test_*` direct Python scripts) and artifact regeneration, while keeping expensive long-horizon SUMO execution opt-in or explicitly fail-closed if runtime guard remains active.
- Strict gates should fail nonzero unless the relevant status is `PASSED`; non-strict summary generation may emit `INCONCLUSIVE` artifacts for audit.

### D-12-04 Provenance Manifest and Raw-to-Derived Traceability
- Add a provenance manifest mapping each derived table/figure-data/claim-input file to its raw source artifacts and commands.
- Derived outputs must record input paths, input statuses, timestamps or generated-at metadata where existing patterns allow, requirements covered, and caveats.
- The manifest should make stale or missing upstream artifacts visible as `INCONCLUSIVE`/`FAILED`, not silently reuse old files.

### D-12-05 Artifact Format
- Prefer compact JSON as the authoritative machine-readable output, with CSV for table/figure-data and Markdown only for human-readable summaries.
- Do not flatten row-level `finite_storage_state`, `objective_components`, or `action_decomposition` into aggregate evidence unless the derived view clearly labels them as audit fields or links back to raw rows.
- Existing Phase 4 renderer style can be reused for Markdown/CSV mechanics, but Phase 12 should use v1.1 semantics and bounded claim wording.

### Claude's Discretion
- Downstream agents may choose exact filenames and command names if they preserve the Phase 12 artifact family, raw-to-derived traceability, CPU/SUMO constraints, and fail-closed claim discipline.
- Downstream agents may add fast synthetic tests for claim audit, provenance, and status propagation before running any expensive artifact regeneration.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Roadmap and requirements
- `.planning/ROADMAP.md` — Phase 12 scope, success criteria, and explicit paper-drafting boundary.
- `.planning/REQUIREMENTS.md` — Requirements `CLAIM-03`, `REPRO-01`, `REPRO-02`, and `REPRO-03`.
- `.planning/STATE.md` — Current milestone state, Phase 11 completion, and remaining Phase 12 focus.
- `.planning/PROJECT.md` — Current project framing, claim discipline, venue fit, and reproducibility constraints.

### Prior phase contracts and verification
- `.planning/phases/11-long-horizon-paired-seed-evidence/11-CONTEXT.md` — Phase 11 claim discipline, Gate C semantics, and Phase 12 handoff boundary.
- `.planning/phases/11-long-horizon-paired-seed-evidence/11-VERIFICATION.md` — Current Phase 11 verified behavior: main artifact is honest `INCONCLUSIVE`, strict Gate C fails nonzero for non-PASSED.
- `.planning/phases/10-strong-baselines-and-stress-scenario-suite/10-CONTEXT.md` — Phase 10 baseline/stress artifact is smoke/spec capability evidence, not dominance evidence.
- `.planning/phases/09-slack-and-binding-kill-gates/09-CONTEXT.md` — Gate A/B fail-closed pattern and separation/recovery distinction.
- `.planning/phases/07-theory-and-separation-package/07-CONTEXT.md` — Theory/separation package scope and bounded guarantee candidates.

### Source artifacts to consume
- `experiments/dual_sensitivity/phase7_theory_separation.json` — Phase 7 theory/separation artifact.
- `experiments/dual_sensitivity/phase9_slack_binding_gates.json` — Phase 9 Gate A/B artifact.
- `experiments/dual_sensitivity/phase10_baselines_stress_suite.json` — Phase 10 baseline/stress smoke/spec artifact.
- `experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json` — Phase 11 main paired-evidence artifact; currently expected to be `INCONCLUSIVE` unless long-horizon rows are executed.
- `experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json` — Phase 11 Gate C artifact; strict status controls dominance readiness.

### Code and tests
- `scripts/render_closed_loop_report.py` — Existing Markdown/CSV renderer pattern with claim-audit checks and raw JSON validation.
- `scripts/run_phase11_paired_evidence.py` — Phase 11 runner/statistics/evidence payload structure.
- `scripts/run_gate_c_paired_evidence.py` — Gate C strict/non-strict checker and status propagation pattern.
- `scripts/run_slack_binding_gates.py` — Gate A/B fail-closed artifact pattern.
- `scripts/check_theory_separation.py` — Phase 7 theory/separation checker pattern.
- `claim_policy.py` — Existing forbidden-claim policy helper.
- `tests/test_phase11_paired_evidence.py` — Direct assertion style for Phase 11 provenance, claim, and Gate C tests.
- `tests/test_slack_binding_gates.py` and `tests/test_theory_separation.py` — Direct assertion patterns for Phase 9 and Phase 7 artifacts.

### Codebase maps
- `.planning/codebase/ARCHITECTURE.md` — Script-oriented research pipeline and JSON artifact conventions.
- `.planning/codebase/TESTING.md` — Script-based tests/gates and direct assertion style.
- `.planning/codebase/INTEGRATIONS.md` — SUMO/TraCI, SciPy/HiGHS, local filesystem, and CPU-only constraints.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `claim_policy.py::forbidden_claim_hits` and related policy constants can enforce bounded language in generated Phase 12 outputs.
- `scripts/render_closed_loop_report.py` provides reusable patterns for validating raw payloads, rendering Markdown/CSV, escaping table cells, and failing on overclaim language.
- `scripts/run_gate_c_paired_evidence.py` provides strict vs non-strict gate semantics and source-status propagation that Phase 12 should preserve.
- `scripts/run_phase11_paired_evidence.py` exposes Phase 11 artifact schema, paired-statistics fields, demand provenance, and `INCONCLUSIVE` runtime-guard behavior.
- Phase 7/9/10/11 JSON artifacts under `experiments/dual_sensitivity/` are the raw inputs for Phase 12 derived files.

### Established Patterns
- Research scripts live under `scripts/`, use `argparse`, write JSON/CSV/Markdown under `experiments/dual_sensitivity/`, and print compact JSON summaries.
- Tests are lightweight direct Python assertion scripts in `tests/`; no pytest configuration is required.
- Gate outputs use explicit top-level `status`, `requirements_covered`, caveats, and fail-closed behavior.
- Existing generated reports must trace back to raw JSON artifacts; manual transcription is not acceptable.

### Integration Points
- A Phase 12 script can load upstream artifacts, validate required statuses/fields, and write a provenance manifest plus derived table/claim-input files.
- A Phase 12 test file should import pure helpers from the new script and use synthetic payloads to cover missing artifact, non-PASSED input, forbidden claim language, and raw-to-derived provenance.
- Reproduction commands should call existing scripts rather than duplicating SUMO/TraCI loops or solver logic.

### Missing Assets / Constraints
- No existing `scripts/run_reproducibility_check.py` or `tests/test_reproducibility.py` file exists; Phase 12 likely needs a new dedicated script and test.
- Current Phase 11 main/Gate C artifacts are expected `INCONCLUSIVE` because the runtime guard prevents 2160 long-horizon rows from executing; Phase 12 must preserve this as a limitation, not a result claim.

</code_context>

<specifics>
## Specific Ideas

Auto-selected decisions follow the conservative v1.1 boundary: produce reproducible future inputs and claim-audit artifacts from raw data, with strict status propagation and no manuscript drafting. The Phase 12 package should make it easy for later v2 manuscript work to see which claims survived and which are still inconclusive, without writing the manuscript now.

</specifics>

<deferred>
## Deferred Ideas

- Full TR-B / Transportation Science manuscript drafting, related work, polished captions, and submission prep remain v2 work.
- Large benchmark expansion (RESCO/CityFlow/LibSignal/neural MARL baselines) remains deferred unless v1.1 evidence justifies it.
- Actually executing all 2160 Phase 11 long-horizon SUMO rows may be done later as an opt-in expensive experiment; Phase 12 should package commands/status, not fake completion.

</deferred>

---

*Phase: 12-Reproducibility and Future Claim Inputs*
*Context gathered: 2026-05-24*
