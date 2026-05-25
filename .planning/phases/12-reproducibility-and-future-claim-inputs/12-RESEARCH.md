# Phase 12: Reproducibility and Future Claim Inputs - Research

**Researched:** 2026-05-24 [VERIFIED: prompt currentDate]  
**Domain:** Python/SUMO research-artifact reproducibility, provenance manifests, bounded claim-audit inputs [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/phases/12-reproducibility-and-future-claim-inputs/12-CONTEXT.md]  
**Confidence:** HIGH for codebase contracts and artifact schemas; MEDIUM for future filename choices because exact names are delegated to implementation discretion [VERIFIED: codebase + CONTEXT.md]

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
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

### Deferred Ideas (OUT OF SCOPE)
## Deferred Ideas

- Full TR-B / Transportation Science manuscript drafting, related work, polished captions, and submission prep remain v2 work.
- Large benchmark expansion (RESCO/CityFlow/LibSignal/neural MARL baselines) remains deferred unless v1.1 evidence justifies it.
- Actually executing all 2160 Phase 11 long-horizon SUMO rows may be done later as an opt-in expensive experiment; Phase 12 should package commands/status, not fake completion.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CLAIM-03 | Generated reports and future manuscript inputs distinguish simulator-, network-, horizon-, and seed-relative evidence from deployment or universal-dominance claims. [VERIFIED: REQUIREMENTS.md] | Use a Phase 12 claim-input JSON plus fail-closed generated-output scanner that preserves simulator/network/horizon/seed/profile/gate-status qualifiers and rejects universal/deployment language. [VERIFIED: CONTEXT.md + scripts/claim_policy.py + scripts/run_gate_c_paired_evidence.py] |
| REPRO-01 | All new result tables, figure-data files, and claim-audit summaries are generated from raw JSON/CSV artifacts rather than manual transcription. [VERIFIED: REQUIREMENTS.md] | Build a single derived-artifact generator that reads Phase 7/9/10/11 JSON sources, emits JSON/CSV/Markdown outputs, and records raw source paths/statuses in a provenance manifest. [VERIFIED: CONTEXT.md + scripts/render_closed_loop_report.py pattern] |
| REPRO-02 | Reproduction scripts can rerun the new finite-storage separation gates and long-horizon experiment summaries on CPU/SUMO without GPU dependencies. [VERIFIED: REQUIREMENTS.md] | Manifest should call existing CPU/SUMO scripts: `check_theory_separation.py`, `run_slack_binding_gates.py`, Phase 11 summary runner, and Gate C checker; long-horizon execution remains opt-in/fail-closed by runtime guard. [VERIFIED: CONTEXT.md + scripts/run_phase11_paired_evidence.py + environment probe] |
| REPRO-03 | Future manuscript-input claim templates and limitations reflect the bounded claim: strict generalization and binding-regime superiority, not universal dominance. [VERIFIED: REQUIREMENTS.md] | Generate machine-readable templates/caveats only, not prose drafts, with status-qualified claim categories: slack recovery/tie, static binding separation, Phase 10 smoke/spec context, Phase 11/Gate C inconclusive or passed. [VERIFIED: CONTEXT.md + REQUIREMENTS.md] |
</phase_requirements>

## Summary

Phase 12 should be implemented as a dedicated Python artifact generator under `scripts/` that consumes existing v1.1 raw artifacts and writes `experiments/dual_sensitivity/phase12_*` JSON/CSV/Markdown outputs; it should not edit or draft manuscript text. [VERIFIED: CONTEXT.md + codebase conventions in CLAUDE.md] The authoritative output should be compact JSON, with CSV used only for table/figure-data inputs and Markdown used only for human-readable summaries. [VERIFIED: CONTEXT.md]

The critical planning fact is that current Phase 11 main and Gate C artifacts are `INCONCLUSIVE`: the main artifact reports `actual_row_count=0`, `expected_row_count=2160`, `all_rows_executed=False`, and `execution_mode=fail_closed_runtime_guard`; Gate C also reports `INCONCLUSIVE`. [VERIFIED: artifact probe of experiments/dual_sensitivity/phase11_long_horizon_paired_seed_evidence.json and phase11_gate_c_paired_evidence.json] Phase 12 must therefore package this as an auditable limitation and reproduction command surface, not as dominance evidence. [VERIFIED: CONTEXT.md + STATE.md]

**Primary recommendation:** Create `scripts/run_phase12_reproducibility_inputs.py` plus `tests/test_phase12_reproducibility_inputs.py`; the script should load Phase 7/9/10/11 artifacts, propagate statuses fail-closed, emit `phase12_reproducibility_package.json`, `phase12_provenance_manifest.json`, `phase12_table_inputs.csv`, `phase12_claim_inputs.json`, `phase12_claim_audit.json`, `phase12_reproduction_manifest.json`, and a bounded human summary Markdown. [VERIFIED: codebase conventions + CONTEXT.md; filename choices MEDIUM because CONTEXT.md delegates exact names]

## Project Constraints (from CLAUDE.md)

- New OR/research pipeline scripts should live under `scripts/` and write outputs under `experiments/dual_sensitivity/`. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Use lowercase snake_case for new Python scripts/modules and functions. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- New standalone scripts should use `main() -> None` and `if __name__ == "__main__":`. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Use `argparse` for CLI arguments, `Path` for path parameters, JSON-serializable dictionaries for summaries, and compact JSON status printing. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Use 4-space indentation and PEP 8-style spacing; no repository formatter/linter config is detected. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Avoid adding barrel files in `scripts/`; scripts should expose reusable pure functions plus a CLI `main()`. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Run OR scripts from the repository root or set `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts` when importing between files in `scripts/`. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Direct repository edits should occur inside the GSD workflow; this research file is produced as the requested GSD research artifact. [VERIFIED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Do not commit `.venv/`, `.env*`, AMPL license/setup material, or secrets; `.env` files are ignored and should not be read/committed. [VERIFIED: /home/samuel/projects/pi_light_OR/.planning/codebase/INTEGRATIONS.md]
- No project skills were found under `.claude/skills/` or `.agents/skills/`. [VERIFIED: directory check]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Load and validate Phase 7/9/10/11 raw artifacts | Local artifact-processing script | Local filesystem | Phase 12 is offline reproducibility packaging over JSON/CSV artifacts, not a service or simulator control loop. [VERIFIED: CONTEXT.md + codebase artifact paths] |
| Derive result tables and figure-data inputs | Local artifact-processing script | CSV writer | `csv.DictWriter` is appropriate for dictionary-to-row table outputs with explicit fieldnames. [CITED: https://docs.python.org/3/library/csv.html] |
| Generate bounded future claim inputs | Local artifact-processing script | Claim-policy helper | Existing `claim_policy.forbidden_claim_hits` and Phase 11 scope validators already encode forbidden language checks. [VERIFIED: scripts/claim_policy.py + scripts/run_phase11_paired_evidence.py] |
| Record raw-to-derived provenance | Local artifact-processing script | Local filesystem | Derived outputs must map to raw source artifacts, statuses, commands, requirements, timestamps, and caveats. [VERIFIED: CONTEXT.md] |
| Rerun finite-storage gates and summaries | Existing Python CLI scripts | SUMO/TraCI for optional long-horizon execution | Phase 12 should call existing scripts rather than duplicate SUMO loops; long-horizon execution stays opt-in/fail-closed. [VERIFIED: CONTEXT.md + scripts/run_phase11_paired_evidence.py] |
| Validate Phase 12 behavior | Direct Python assertion tests | Optional pytest discovery | Current test style is direct `tests/test_*.py` scripts with `main()` runners and no pytest config. [VERIFIED: tests directory + CLAUDE.md] |

## Standard Stack

### Core
| Library / Component | Version | Purpose | Why Standard |
|---------------------|---------|---------|--------------|
| Python stdlib `json` | Python 3.12.3 via `python`; Python 3.14.4 via `python3` [VERIFIED: environment probe] | Read/write authoritative machine-readable JSON outputs. [CITED: https://docs.python.org/3/library/json.html] | Official `json.dump`, `json.dumps`, `json.load`, and `json.loads` APIs serialize/deserialize JSON. [CITED: https://docs.python.org/3/library/json.html] |
| Python stdlib `csv` | Python 3.12.3/3.14.4 [VERIFIED: environment probe] | Emit table/figure-data CSVs. [CITED: https://docs.python.org/3/library/csv.html] | `csv.DictWriter` maps dictionaries onto output rows, requires explicit `fieldnames`, and supports `writeheader()`. [CITED: https://docs.python.org/3/library/csv.html] |
| Python stdlib `argparse` | Python 3.12.3/3.14.4 [VERIFIED: environment probe] | Provide reproducible CLI entry points. [CITED: https://docs.python.org/3/library/argparse.html] | `ArgumentParser.add_argument()` defines options and `parse_args()` returns a populated namespace. [CITED: https://docs.python.org/3/library/argparse.html] |
| Existing `scripts/claim_policy.py` | Internal Phase 6 helper [VERIFIED: codebase read] | Enforce bounded claim language and detect forbidden phrases. [VERIFIED: scripts/claim_policy.py] | It already defines `FORBIDDEN_CLAIM_PATTERNS`, `PERMITTED_CLAIM`, and `forbidden_claim_hits`. [VERIFIED: scripts/claim_policy.py] |
| Existing Phase 7/9/10/11 runner/checker scripts | Internal v1.1 scripts [VERIFIED: codebase read] | Regenerate source artifacts and status checks. [VERIFIED: CONTEXT.md] | Reusing these scripts avoids a second simulator/statistics implementation. [VERIFIED: CONTEXT.md + scripts/run_phase11_paired_evidence.py] |

### Supporting
| Library / Component | Version | Purpose | When to Use |
|---------------------|---------|---------|-------------|
| SUMO CLI `sumo` | 1.26.0 [VERIFIED: environment probe] | Optional CPU long-horizon SUMO execution and reproduction commands. [VERIFIED: environment probe + INTEGRATIONS.md] | Only for opt-in reruns; default Phase 12 generation should not require completing all 2160 rows. [VERIFIED: CONTEXT.md + Phase 11 artifact] |
| SUMO `netconvert` | 1.26.0 [VERIFIED: environment probe] | Network generation support for existing SUMO workflows. [VERIFIED: environment probe + INTEGRATIONS.md] | Include in environment manifest because existing network scripts require it. [VERIFIED: INTEGRATIONS.md] |
| `traci` / `sumolib` | 1.26.0 each [VERIFIED: environment probe] | Python SUMO integration for existing runners. [VERIFIED: environment probe + INTEGRATIONS.md] | Required only when executing SUMO-backed scripts, not for pure Phase 12 artifact derivation. [VERIFIED: CONTEXT.md + INTEGRATIONS.md] |
| SciPy `stats.bootstrap` | SciPy 1.17.1 installed [VERIFIED: environment probe] | Existing Phase 11 paired-statistics computation. [VERIFIED: scripts/run_phase11_paired_evidence.py] | Do not recompute a competing statistics engine in Phase 12; consume Phase 11 paired statistics and statuses. [VERIFIED: CONTEXT.md] |
| NumPy | 1.26.4 installed [VERIFIED: environment probe] | Existing numerical pipeline dependency. [VERIFIED: environment probe] | Mention in reproduction manifest for upstream scripts, but Phase 12 can be mostly stdlib. [VERIFIED: codebase patterns] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Stdlib JSON/CSV + internal scripts | Pandas DataFrame pipeline [ASSUMED] | Not recommended: no new package is needed for compact deterministic JSON/CSV outputs, and adding Pandas would expand dependency surface without Phase 12 requiring complex analytics. [VERIFIED: CONTEXT.md + codebase no-install pattern; package alternative itself ASSUMED] |
| Existing `claim_policy.py` scanner | New regex-only scanner [ASSUMED] | Not recommended: a new scanner could diverge from Phase 6/11 bounded-claim rules and miss existing negation/bounded-context handling. [VERIFIED: scripts/claim_policy.py] |
| Reuse Phase 11 runner/checker | New SUMO loop in Phase 12 [ASSUMED] | Not recommended: Phase 11 already owns long-horizon row execution, demand scaling, paired statistics, and Gate C status propagation. [VERIFIED: scripts/run_phase11_paired_evidence.py + scripts/run_gate_c_paired_evidence.py] |

**Installation:**
```bash
# No new external packages required for Phase 12. [VERIFIED: CONTEXT.md + codebase stdlib patterns]
```

**Version verification:** Python, SUMO, netconvert, SciPy, NumPy, TraCI, and sumolib were probed in this environment; versions are documented in Environment Availability. [VERIFIED: environment probe]

## Package Legitimacy Audit

No new external package installation is recommended for Phase 12, so the package legitimacy gate is not triggered. [VERIFIED: Standard Stack recommendation] Existing installed dependencies are inherited from the project environment and are not newly introduced by this phase. [VERIFIED: environment probe + CONTEXT.md]

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| none | n/a | n/a | n/a | n/a | n/a | No new package installs. [VERIFIED: research recommendation] |

**Packages removed due to slopcheck [SLOP] verdict:** none. [VERIFIED: no new packages]  
**Packages flagged as suspicious [SUS]:** none. [VERIFIED: no new packages]

## Architecture Patterns

### System Architecture Diagram

```text
Raw v1.1 artifacts
  ├─ Phase 7 theory/separation JSON (status PASSED currently) [VERIFIED: artifact probe]
  ├─ Phase 9 Gate A/B JSON (status PASSED currently) [VERIFIED: artifact probe]
  ├─ Phase 10 baseline/stress JSON (status SMOKE_ONLY currently) [VERIFIED: artifact probe]
  ├─ Phase 11 paired evidence JSON (status INCONCLUSIVE currently) [VERIFIED: artifact probe]
  └─ Phase 11 Gate C JSON (status INCONCLUSIVE currently) [VERIFIED: artifact probe]
          │
          ▼
Phase 12 loader and source-status validator
          │
          ├─ if missing/unparseable source → mark derived package FAILED/INCONCLUSIVE, do not silently reuse stale files [VERIFIED: CONTEXT.md]
          ├─ if source status != PASSED → preserve source status and caveats, do not upgrade evidence [VERIFIED: CONTEXT.md + Gate C pattern]
          └─ if generated text has forbidden language → write audit details and fail strict mode [VERIFIED: claim_policy.py]
          │
          ▼
Derived outputs under experiments/dual_sensitivity/phase12_*
  ├─ authoritative JSON package and claim inputs [VERIFIED: CONTEXT.md]
  ├─ CSV table/figure-data rows with source-status columns [VERIFIED: CONTEXT.md]
  ├─ provenance manifest mapping derived files → raw sources + commands [VERIFIED: CONTEXT.md]
  ├─ reproduction manifest with fast and opt-in expensive commands [VERIFIED: CONTEXT.md]
  └─ human-readable Markdown summary, explicitly not manuscript prose [VERIFIED: CONTEXT.md]
```

### Recommended Project Structure

```text
scripts/
├── run_phase12_reproducibility_inputs.py      # Phase 12 loader, status propagation, claim audit, and derived artifact writer. [VERIFIED: codebase conventions; filename MEDIUM]
└── claim_policy.py                            # Existing bounded-claim helper to reuse. [VERIFIED: codebase]

tests/
└── test_phase12_reproducibility_inputs.py     # Synthetic tests for provenance, status propagation, missing artifacts, and forbidden claims. [VERIFIED: test conventions; filename MEDIUM]

experiments/dual_sensitivity/
├── phase12_reproducibility_package.json       # Authoritative machine-readable package. [VERIFIED: CONTEXT.md; filename MEDIUM]
├── phase12_provenance_manifest.json           # Raw-to-derived traceability manifest. [VERIFIED: CONTEXT.md; filename MEDIUM]
├── phase12_table_inputs.csv                   # Table/figure-data rows with statuses and qualifiers. [VERIFIED: CONTEXT.md; filename MEDIUM]
├── phase12_claim_inputs.json                  # Machine-readable future claim templates/caveats, not manuscript text. [VERIFIED: CONTEXT.md; filename MEDIUM]
├── phase12_claim_audit.json                   # Generated-output forbidden-language audit. [VERIFIED: CONTEXT.md; filename MEDIUM]
├── phase12_reproduction_manifest.json         # CPU/SUMO rerun commands and strict/non-strict modes. [VERIFIED: CONTEXT.md; filename MEDIUM]
└── phase12_summary.md                         # Human-readable audit summary; not a paper draft. [VERIFIED: CONTEXT.md; filename MEDIUM]
```

### Pattern 1: Source Registry With Required Status Semantics

**What:** Define a fixed registry for Phase 7/9/10/11 inputs with `path`, `experiment`, `requirements`, `expected_status_policy`, `commands`, and `evidence_role`. [VERIFIED: CONTEXT.md + reproduce_blocks.py pattern]

**When to use:** Use at the start of the Phase 12 script so every downstream row can be traced to a raw source and its status. [VERIFIED: CONTEXT.md]

**Prescriptive schema:**
```python
# Source: codebase pattern in scripts/reproduce_blocks.py and Phase 12 context. [VERIFIED: codebase + CONTEXT.md]
SOURCE_REGISTRY = {
    "phase7_theory_separation": {
        "path": "experiments/dual_sensitivity/phase7_theory_separation.json",
        "accepted_statuses": {"PASSED"},
        "evidence_role": "static_theory_separation",
        "rerun_command": "python scripts/check_theory_separation.py --out experiments/dual_sensitivity/phase7_theory_separation.json",
    },
    "phase11_gate_c": {
        "path": "experiments/dual_sensitivity/phase11_gate_c_paired_evidence.json",
        "accepted_statuses": {"PASSED"},
        "evidence_role": "closed_loop_binding_gate_c",
        "rerun_command": "python scripts/run_gate_c_paired_evidence.py --strict",
    },
}
```

### Pattern 2: Status-Preserving Derived Evidence Rows

**What:** Derived CSV/JSON rows must include `source_path`, `source_experiment`, `source_status`, `evidence_role`, `requirements_covered`, `network`, `horizon`, `warmup`, `seed_count`, `profile`, `gate_status`, and `caveat`. [VERIFIED: CONTEXT.md + Phase 11 schema]

**When to use:** Use for every result table/figure-data input so inconclusive or smoke-only sources are visible in the same row as the metric. [VERIFIED: CONTEXT.md]

**Example:**
```python
# Source: Python csv DictWriter documentation and project artifact schemas. [CITED: https://docs.python.org/3/library/csv.html] [VERIFIED: Phase 11 artifact schema]
fieldnames = [
    "derived_artifact", "source_path", "source_status", "evidence_role",
    "network", "scenario_tag", "profile", "steps", "warmup", "seed_count",
    "metric", "value", "gate_status", "claim_allowed", "caveat",
]
```

### Pattern 3: Fail-Closed Claim Audit Over Generated Outputs

**What:** Collect generated JSON prose fields, Markdown text, and CSV text, then run `forbidden_claim_hits` plus Phase-12-specific forbidden phrases before marking strict mode as passed. [VERIFIED: scripts/claim_policy.py + scripts/audit_claim_discipline.py]

**When to use:** After all outputs are rendered and before CLI exit status is decided. [VERIFIED: codebase gate pattern]

**Forbidden additions for Phase 12:** include universal/deployment language, manuscript-drafting language, and source-upgrading phrases such as `Phase 10 proves superiority`, `Phase 11 inconclusive dominance`, or `Gate C passed` when Gate C source status is not `PASSED`. [VERIFIED: CONTEXT.md + Phase 11 validators]

### Pattern 4: Strict vs Non-Strict Modes

**What:** Non-strict generation may emit `INCONCLUSIVE` derived artifacts for audit; strict mode must exit nonzero unless relevant source statuses and generated claim audits are `PASSED`. [VERIFIED: CONTEXT.md + scripts/run_gate_c_paired_evidence.py]

**When to use:** Add CLI flags like `--strict`, `--allow-inconclusive-summary`, and `--out-dir`; default should be safe non-strict package generation, with `--strict` for release gates. [VERIFIED: CONTEXT.md; exact flag names MEDIUM]

### Anti-Patterns to Avoid

- **Manual transcription of result values:** It breaks REPRO-01 because derived tables/figures must come from raw JSON/CSV artifacts. [VERIFIED: REQUIREMENTS.md]
- **Upgrading `INCONCLUSIVE` to claim-ready:** Phase 11 main/Gate C artifacts are currently inconclusive and must not become performance/dominance claims. [VERIFIED: artifact probe + CONTEXT.md]
- **Flattening nested audit fields into aggregate metrics:** `finite_storage_state`, `objective_components`, and `action_decomposition` should remain row-level audit fields or links, not aggregate evidence. [VERIFIED: CONTEXT.md + Phase 11 schema]
- **Starting manuscript drafting:** Future claim inputs may be machine-readable templates/caveats; polished prose, related work, captions, and submission preparation are out of scope. [VERIFIED: CONTEXT.md]
- **Duplicating SUMO/TraCI loops in Phase 12:** Phase 11 owns execution and Gate C statistics; Phase 12 should call existing commands and package results. [VERIFIED: scripts/run_phase11_paired_evidence.py + CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Claim discipline | A new ad hoc regex scanner | `scripts/claim_policy.py::forbidden_claim_hits` plus Phase 11 validators | Existing helpers encode bounded/negated context and forbidden broad-superiority patterns. [VERIFIED: scripts/claim_policy.py] |
| Long-horizon execution | A second SUMO runner | `scripts/run_phase11_paired_evidence.py` | Existing runner owns demand scaling, paired seeds, profile constraints, runtime guard, and payload schema. [VERIFIED: script read] |
| Gate C status | A new dominance checker | `scripts/run_gate_c_paired_evidence.py` | Existing checker refuses to upgrade non-PASSED source artifacts and supports strict mode. [VERIFIED: script read] |
| CSV mechanics | String concatenation | Python `csv.DictWriter` | Official API maps dictionaries to rows and writes headers with explicit fieldnames. [CITED: https://docs.python.org/3/library/csv.html] |
| JSON framing | Multiple `json.dump()` calls to one file | One JSON object/list per file via `json.dumps(..., indent=2)` or a single `json.dump` | Python docs warn JSON is not a framed protocol, so repeated dumps to the same file can create invalid JSON. [CITED: https://docs.python.org/3/library/json.html] |
| Reproduction manifest | Free-text commands only | Structured command records with `runtime_profile`, `strict`, `expected_artifacts`, `requirements`, and `claim_note` | Existing reproducibility registry pattern already uses structured block metadata. [VERIFIED: scripts/reproduce_blocks.py] |

**Key insight:** Phase 12 is a provenance/status-propagation problem, not a new experiment or manuscript-writing problem; the safest plan is to make evidence boundaries machine-readable and fail-closed. [VERIFIED: CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Treating Phase 11 INCONCLUSIVE as performance evidence
**What goes wrong:** Derived claim inputs accidentally state or imply closed-loop dominance even though Phase 11 rows were not executed. [VERIFIED: artifact probe + CONTEXT.md]  
**Why it happens:** The Phase 11 spec exists and Gate C tooling exists, but the main artifact currently has zero executed rows due to the runtime guard. [VERIFIED: Phase 11 artifact probe]  
**How to avoid:** Copy `source_status`, `actual_row_count`, `expected_row_count`, `all_rows_executed`, `profile_eligibility`, and `reasons` into Phase 12 outputs. [VERIFIED: Phase 11 schema]  
**Warning signs:** Any generated claim row saying `dominance`, `superiority`, `wins`, or `Gate C passed` while source Gate C status is not `PASSED`. [VERIFIED: CONTEXT.md]

### Pitfall 2: Mixing Phase 10 smoke/spec coverage with dominance evidence
**What goes wrong:** Phase 10 `SMOKE_ONLY` baseline/stress capability evidence is described as closed-loop superiority evidence. [VERIFIED: Phase 10 artifact probe + CONTEXT.md]  
**Why it happens:** Phase 10 contains scenario rows and aggregates, but its `claim_framing` says it is not Gate C/paired-seed dominance evidence. [VERIFIED: Phase 10 artifact probe]  
**How to avoid:** Give Phase 10 rows `evidence_role=baseline_stress_capability_context` and `claim_allowed=false` for dominance language. [VERIFIED: CONTEXT.md]  
**Warning signs:** Generated outputs cite Phase 10 in a `binding_regime_superiority` template. [VERIFIED: CONTEXT.md]

### Pitfall 3: Losing raw-to-derived traceability
**What goes wrong:** A derived CSV row cannot be traced back to exact raw artifact path/status/command. [VERIFIED: CONTEXT.md]  
**Why it happens:** Table renderers can focus on values and omit provenance. [VERIFIED: Phase 4 renderer pattern shows separate input path link]  
**How to avoid:** Make provenance fields mandatory and create a manifest entry for every derived file. [VERIFIED: CONTEXT.md]  
**Warning signs:** Derived files have metrics but no `source_path`, `source_status`, or `generated_by`. [VERIFIED: CONTEXT.md]

### Pitfall 4: Flattening nested audit fields into aggregate evidence
**What goes wrong:** `finite_storage_state`, `objective_components`, or `action_decomposition` are summarized as if they were aggregate performance metrics. [VERIFIED: CONTEXT.md]  
**Why it happens:** CSV generation may tempt flattening nested JSON fields. [VERIFIED: CONTEXT.md]  
**How to avoid:** Include references/counts/schema links, and only expose nested objects as audit fields or raw-row links. [VERIFIED: CONTEXT.md + Phase 11 objective schema note]

### Pitfall 5: Strict mode semantics are too permissive
**What goes wrong:** `--strict` exits 0 when required source artifacts are missing, stale, or not `PASSED`. [VERIFIED: CONTEXT.md]  
**Why it happens:** Summary generation and gate validation have different semantics. [VERIFIED: CONTEXT.md]  
**How to avoid:** Non-strict can generate audit packages with `INCONCLUSIVE`; strict must fail nonzero unless relevant evidence and claim audit pass. [VERIFIED: CONTEXT.md + Gate C strict pattern]

## Code Examples

Verified patterns from official and codebase sources:

### JSON load/write as one framed object
```python
# Source: Python json official docs. [CITED: https://docs.python.org/3/library/json.html]
import json
from pathlib import Path

payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
out_path.write_text(json.dumps(derived_payload, indent=2), encoding="utf-8")
```

### CSV table input generation
```python
# Source: Python csv official docs. [CITED: https://docs.python.org/3/library/csv.html]
import csv

with csv_path.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
```

### CLI pattern
```python
# Source: Python argparse official docs and project script convention. [CITED: https://docs.python.org/3/library/argparse.html] [VERIFIED: CLAUDE.md]
import argparse

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="experiments/dual_sensitivity")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()
```

### Phase 12 claim audit pattern
```python
# Source: scripts/claim_policy.py. [VERIFIED: codebase]
from claim_policy import forbidden_claim_hits

hits = forbidden_claim_hits(rendered_text, source="phase12_generated_outputs")
if strict and hits:
    raise SystemExit(1)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual paper-facing artifact transcription | Script-generated JSON/CSV/manifest outputs from raw artifacts | v1.0 Phase 5 and v1.1 Phase 12 scope [VERIFIED: PROJECT.md + CONTEXT.md] | Planner should create generation and validation tasks, not writing tasks. [VERIFIED: CONTEXT.md] |
| Proxy-only binding labels | Explicit finite-storage state/objective fields and action decompositions | v1.1 Phase 6/8/9 [VERIFIED: STATE.md + scripts] | Phase 12 must preserve nested audit fields and not summarize them as unsupported aggregates. [VERIFIED: CONTEXT.md] |
| Broad dual-superiority framing | Bounded slack recovery/tie plus binding-regime-only improvement language | v1.1 Phase 6 [VERIFIED: REQUIREMENTS.md + claim_policy.py] | Claim templates must include qualifiers and source-status gates. [VERIFIED: CONTEXT.md] |
| Phase 10 smoke/spec evidence as possible context | Gate C paired-seed evidence as the only closed-loop dominance gate | v1.1 Phase 11 [VERIFIED: REQUIREMENTS.md + Phase 11 scripts] | Phase 12 cannot cite Phase 10 or inconclusive Phase 11 artifacts as dominance. [VERIFIED: CONTEXT.md] |

**Deprecated/outdated:**
- Treating v1.0 pressure-equivalent artifacts as superiority evidence is explicitly prohibited. [VERIFIED: STATE.md + claim_policy.py]
- Treating `local_pilight` or unsafe old `full_dual_symbolic` paths as feasible proposed-method evidence is prohibited; Phase 8 introduced the safe `finite_storage_primal_dual` successor. [VERIFIED: STATE.md]
- Drafting final manuscript prose before v1.1 evidence survives is out of scope for this milestone. [VERIFIED: ROADMAP.md + CONTEXT.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Pandas was considered as an alternative but is not recommended for this phase. [ASSUMED] | Standard Stack / Alternatives Considered | Low: adding Pandas would be a planner decision requiring package verification, but stdlib JSON/CSV already satisfies the locked artifact format. |
| A2 | Exact Phase 12 output filenames recommended here are acceptable as long as they preserve the `phase12_*` family. [ASSUMED] | Summary / Project Structure | Medium: planner may choose different exact names, but CONTEXT.md explicitly delegates exact filenames and command names. |

## Open Questions (RESOLVED)

1. **Should strict Phase 12 mode require Phase 10 `SMOKE_ONLY` to become `PASSED`?** [RESOLVED]
   - Decision: Treat Phase 10 `SMOKE_ONLY` as acceptable only for `baseline_stress_capability_context`, never for superiority templates or dominance evidence.
   - Applied in plan: 12-01 requires Phase 10 claim rows to use `claim_allowed=false` for dominance language; 12-02 validates that smoke/spec coverage remains context-only.

2. **Should Markdown output be generated by default?** [RESOLVED]
   - Decision: Generate one clearly labeled audit summary Markdown by default, with JSON remaining authoritative and CSV limited to table/figure-data inputs.
   - Applied in plan: 12-01 and 12-02 include `phase12_summary.md` as a human audit summary and require claim-audit scanning; manuscript prose remains out of scope.

3. **Should full 2160-row Phase 11 execution be callable from Phase 12?** [RESOLVED]
   - Decision: Include the long-horizon command only in `phase12_reproduction_manifest.json` as opt-in/fail-closed; do not run it during default Phase 12 validation.
   - Applied in plan: 12-01 builds the command surface and 12-02 explicitly forbids executing the opt-in 2160-row SUMO command during artifact generation.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| `python` | Direct test scripts and Phase 12 generator | ✓ [VERIFIED: environment probe] | 3.12.3 [VERIFIED: environment probe] | `python3` is also available. [VERIFIED: environment probe] |
| `python3` | Project documented runtime command style | ✓ [VERIFIED: environment probe] | 3.14.4 [VERIFIED: environment probe] | `python` 3.12.3 for compatibility if needed. [VERIFIED: environment probe] |
| SUMO `sumo` | Optional CPU long-horizon execution | ✓ [VERIFIED: environment probe] | 1.26.0 [VERIFIED: environment probe] | None for actual SUMO execution; Phase 12 can still generate non-strict audit summaries from existing artifacts. [VERIFIED: CONTEXT.md] |
| SUMO `netconvert` | Network-generation reproduction support | ✓ [VERIFIED: environment probe] | 1.26.0 [VERIFIED: environment probe] | None for network regeneration. [VERIFIED: INTEGRATIONS.md] |
| `scipy` | Existing Phase 11 statistics and upstream scripts | ✓ [VERIFIED: environment probe] | 1.17.1 [VERIFIED: environment probe] | Do not recompute statistics in Phase 12; consume existing artifacts if SciPy unavailable. [VERIFIED: CONTEXT.md] |
| `numpy` | Existing numerical pipeline | ✓ [VERIFIED: environment probe] | 1.26.4 [VERIFIED: environment probe] | Phase 12 pure packaging can avoid NumPy. [VERIFIED: Standard Stack recommendation] |
| `traci` | SUMO Python integration in upstream scripts | ✓ [VERIFIED: environment probe] | 1.26.0 [VERIFIED: environment probe] | No fallback for actual TraCI execution; default Phase 12 can package status. [VERIFIED: CONTEXT.md] |
| `sumolib` | SUMO network parsing in upstream scripts | ✓ [VERIFIED: environment probe] | 1.26.0 [VERIFIED: environment probe] | No fallback for SUMO parsing; default Phase 12 can package status. [VERIFIED: CONTEXT.md] |

**Missing dependencies with no fallback:** none detected for default Phase 12 packaging. [VERIFIED: environment probe]

**Missing dependencies with fallback:** none detected. [VERIFIED: environment probe]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Direct Python assertion scripts in `tests/test_*.py`; no pytest configuration is required. [VERIFIED: tests directory + CLAUDE.md] |
| Config file | none detected for pytest/unittest. [VERIFIED: CLAUDE.md + tests directory] |
| Quick run command | `python tests/test_phase12_reproducibility_inputs.py` [VERIFIED: project test pattern; file not yet created] |
| Full suite command | `for f in tests/test_*.py; do python "$f"; done` [VERIFIED: test files have direct `main()` runners] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CLAIM-03 | Generated claim inputs preserve simulator/network/horizon/seed/profile/gate-status qualifiers and reject deployment/universal dominance language. [VERIFIED: REQUIREMENTS.md] | unit | `python tests/test_phase12_reproducibility_inputs.py::test_claim_inputs_preserve_qualifiers` is a pytest-style target; direct script should call the function from `main()`. [ASSUMED exact function name] | ❌ Wave 0 |
| REPRO-01 | Derived JSON/CSV/Markdown outputs are generated from raw artifacts and every derived file has provenance entries. [VERIFIED: REQUIREMENTS.md] | unit/integration | `python tests/test_phase12_reproducibility_inputs.py` [VERIFIED: project test pattern] | ❌ Wave 0 |
| REPRO-02 | Reproduction manifest contains CPU/SUMO commands, fast validation commands, strict Gate C command, and opt-in long-horizon command without GPU requirements. [VERIFIED: REQUIREMENTS.md + CONTEXT.md] | unit | `python tests/test_phase12_reproducibility_inputs.py` [VERIFIED: project test pattern] | ❌ Wave 0 |
| REPRO-03 | Claim templates represent slack recovery/tie and binding-regime-only superiority while leaving INCONCLUSIVE sources as limitations. [VERIFIED: REQUIREMENTS.md + CONTEXT.md] | unit | `python tests/test_phase12_reproducibility_inputs.py` [VERIFIED: project test pattern] | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python tests/test_phase12_reproducibility_inputs.py` plus any directly touched existing test, such as `python tests/test_phase11_paired_evidence.py`. [VERIFIED: test pattern]
- **Per wave merge:** `for f in tests/test_*.py; do python "$f"; done`. [VERIFIED: tests have direct main runners]
- **Phase gate:** Run Phase 12 generator in non-strict mode, inspect output statuses, run claim audit, then run strict mode expecting nonzero if Gate C remains `INCONCLUSIVE`. [VERIFIED: CONTEXT.md + Phase 11 current status]

### Wave 0 Gaps
- [ ] `tests/test_phase12_reproducibility_inputs.py` — covers CLAIM-03, REPRO-01, REPRO-02, REPRO-03. [VERIFIED: no existing Phase 12 test file]
- [ ] `scripts/run_phase12_reproducibility_inputs.py` — generator under test. [VERIFIED: no existing Phase 12 script]
- [ ] Synthetic fixture builders for source artifacts with `PASSED`, `FAILED`, `INCONCLUSIVE`, `PILOT_ONLY`, and `SMOKE_ONLY` statuses. [VERIFIED: required by CONTEXT.md status propagation]
- [ ] Test case asserting current real Phase 11 artifacts remain `INCONCLUSIVE` unless source status changes. [VERIFIED: artifact probe]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no [VERIFIED: INTEGRATIONS.md] | No user login/auth provider exists in this offline research pipeline. [VERIFIED: INTEGRATIONS.md] |
| V3 Session Management | no [VERIFIED: INTEGRATIONS.md] | No web/session layer exists. [VERIFIED: INTEGRATIONS.md] |
| V4 Access Control | no [VERIFIED: INTEGRATIONS.md] | Local filesystem research scripts only; do not add external service access. [VERIFIED: INTEGRATIONS.md] |
| V5 Input Validation | yes [VERIFIED: artifact-processing scope] | Validate JSON object type, required top-level keys, source statuses, artifact paths, and generated-output claim language before strict success. [VERIFIED: CONTEXT.md + existing gate patterns] |
| V6 Cryptography | no [VERIFIED: INTEGRATIONS.md] | No crypto/secrets feature; do not read/commit `.env` or AMPL license data. [VERIFIED: INTEGRATIONS.md] |

### Known Threat Patterns for offline artifact generation

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Stale or missing artifact reused silently | Tampering | Record `exists`, `parse_status`, `source_status`, `generated_at`, and fail/inconclusive status in provenance manifest. [VERIFIED: CONTEXT.md] |
| Claim overstatement in generated outputs | Spoofing / Repudiation | Run `claim_policy.forbidden_claim_hits` over generated text/JSON/CSV and fail strict mode on hits. [VERIFIED: scripts/claim_policy.py] |
| Path traversal via CLI inputs | Tampering | Prefer default project-root-relative paths and validate expected source registry paths; do not scan secrets or `.env`. [VERIFIED: INTEGRATIONS.md + CONTEXT.md] |
| Invalid JSON from repeated writes | Tampering | Write one complete JSON object/list per file; Python docs warn JSON is not framed for repeated dump calls. [CITED: https://docs.python.org/3/library/json.html] |

## Sources

### Primary (HIGH confidence)
- `/home/samuel/projects/pi_light_OR/.planning/phases/12-reproducibility-and-future-claim-inputs/12-CONTEXT.md` — Phase 12 locked decisions, boundaries, canonical refs, and raw artifact list. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md` — CLAIM-03, REPRO-01, REPRO-02, REPRO-03 definitions. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/.planning/STATE.md` — current milestone state and Phase 11 inconclusive warning. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/CLAUDE.md` — project conventions and constraints. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/scripts/claim_policy.py` — bounded claim policy and forbidden claim helper. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/scripts/run_phase11_paired_evidence.py` — Phase 11 schema, runtime guard, paired statistics, and Gate C evaluation. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/scripts/run_gate_c_paired_evidence.py` — strict/non-strict Gate C status propagation. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/scripts/run_slack_binding_gates.py` — Gate A/B fail-closed artifact pattern. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/scripts/check_theory_separation.py` — Phase 7 theory artifact generation pattern. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/scripts/render_closed_loop_report.py` — JSON/CSV/Markdown rendering and claim-audit pattern. [VERIFIED: file read]
- `/home/samuel/projects/pi_light_OR/tests/test_phase11_paired_evidence.py` and `/home/samuel/projects/pi_light_OR/tests/test_slack_binding_gates.py` — direct assertion test style. [VERIFIED: file read]
- Existing artifacts under `/home/samuel/projects/pi_light_OR/experiments/dual_sensitivity/` — current Phase 7/9/10/11 statuses. [VERIFIED: artifact probe]

### Secondary (MEDIUM confidence)
- [Python `json` documentation](https://docs.python.org/3/library/json.html) — JSON serialization APIs and framing caution. [CITED: docs.python.org]
- [Python `csv` documentation](https://docs.python.org/3/library/csv.html) — `DictWriter`, `fieldnames`, `writeheader`, and `newline=''` guidance. [CITED: docs.python.org]
- [Python `argparse` documentation](https://docs.python.org/3/library/argparse.html) — CLI parser/add_argument/parse_args behavior. [CITED: docs.python.org]
- [SciPy `stats.bootstrap` documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html) — bootstrap CI parameters and paired resampling. [CITED: docs.scipy.org]

### Tertiary (LOW confidence)
- None used for implementation-critical claims. [VERIFIED: research process]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Uses existing project scripts plus Python stdlib; no new external packages are required. [VERIFIED: codebase + official Python docs]
- Architecture: HIGH — Phase boundaries, artifact paths, and status semantics are locked in CONTEXT.md and existing scripts. [VERIFIED: CONTEXT.md + script reads]
- Pitfalls: HIGH — Current Phase 11/10 statuses were directly probed and match CONTEXT.md warnings. [VERIFIED: artifact probe]
- Filename recommendations: MEDIUM — CONTEXT.md permits downstream agents to choose exact filenames/command names. [VERIFIED: CONTEXT.md]

**Research date:** 2026-05-24 [VERIFIED: prompt currentDate]  
**Valid until:** 2026-06-23 for codebase/artifact schema assumptions unless Phase 11 rows are executed or Phase 12 context changes first. [ASSUMED]
