# Phase 6: Claim Discipline and Explicit State Foundation - Research

**Researched:** 2026-05-23 [VERIFIED: system currentDate]
**Domain:** CPU/SUMO/OR research repository claim guards, explicit finite-storage state schemas, finite-storage objective decomposition, and script-based validation gates [CITED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md]
**Confidence:** HIGH for repository integration patterns and Phase 6 scope; MEDIUM for finite-storage schema semantics because downstream Phase 7 theory may refine exact mathematical definitions [VERIFIED: codebase grep; CITED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md]

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

## Implementation Decisions

### Claim Guard Scope
- Treat v1.0 evidence as pressure-equivalent recovery/compression evidence only; do not allow it to support dual-superiority wording.
- Encode the permitted strong claim in repository-readable artifacts: slack constraints imply recovery/ties, binding constraints are the only allowed improvement domain.
- Make guard checks fail closed when reports or generated manuscript inputs use universal dominance or deployment-level wording unsupported by v1.1 gates.
- Keep final manuscript drafting out of scope; this phase may create claim templates, checks, and audit inputs only.

### Explicit State Schema
- Replace proxy-only binding labels with explicit finite-storage fields: downstream storage, residual receiving capacity, spillback/blocking indicators, switching-loss state, service urgency, and incident/capacity-drop state.
- Prefer JSON-serializable schema fields emitted by deterministic scripts under `scripts/` and artifacts under `experiments/dual_sensitivity/`.
- Preserve existing v1.0 artifacts as historical evidence, but mark them as insufficient for v1.1 binding-regime superiority.
- Use schema validation or explicit required-field checks in scripts rather than informal markdown-only discipline.

### Objective Decomposition
- Predeclare finite-storage objective components as delay, unfinished-vehicle penalty, spillback/blocking time, and switching lost-time terms.
- Emit objective decompositions in generated artifacts so later gates can verify which component supports any separation or performance claim.
- Keep component names stable and machine-readable for downstream gate and report scripts.
- Avoid adding unrelated objective terms unless required by later theory/controller phases.

### Repository Checks and Outputs
- Follow existing script-gate patterns: standalone snake_case Python CLIs, JSON status payloads, explicit nonzero exits for failed gates.
- Add lightweight checks that scan claim/report artifacts for forbidden superiority wording unless the relevant v1.1 evidence exists.
- Prefer deterministic fixtures and generated JSON over mocks; do not mock optimization or JSON output creation.
- Integrate with existing `refine-logs/` and `experiments/dual_sensitivity/` surfaces without creating final paper sections.

### Claude's Discretion
All unresolved implementation choices are delegated to Claude, with the constraint that the phase must remain fail-closed, CPU/SUMO-oriented, and aligned with existing script-based validation patterns.

### Deferred Ideas (OUT OF SCOPE)

## Deferred Ideas

- Final manuscript drafting, related work, and submission preparation remain deferred to v2.
- Large benchmark expansion and neural MARL baselines remain deferred unless the v1.1 core result survives.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CLAIM-01 | The project states the permitted strong claim as bounded: the method recovers or ties max-pressure when constraints are slack and only claims improvement when finite-storage, spillback, switching, service, or incident constraints bind. | Implement a machine-readable claim policy artifact and guard scanner that encode allowed slack/binding language and forbidden universal-dominance language. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md; VERIFIED: codebase grep] |
| CLAIM-02 | The repository prevents v1.0 pressure-equivalent static or closed-loop evidence from being described as dual superiority. | Extend existing forbidden phrase and source-artifact validation patterns in `reproduce_blocks.py`, `render_paper_artifacts.py`, and renderers so v1.0 artifacts remain historical pressure-equivalent evidence only. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py; CITED: /home/samuel/projects/pi_light_OR/scripts/render_paper_artifacts.py] |
| STATE-01 | Experiment state replaces proxy-only binding labels with explicit downstream storage, residual receiving capacity, spillback/blocking, phase-switching loss, service urgency, and incident/capacity-drop fields. | Add explicit JSON fields to state-generation/sample-conversion artifacts instead of relying on `*_proxy` regime labels currently emitted by `generate_static_regime_states.py`. [CITED: /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py] |
| STATE-02 | The finite-storage constrained objective predeclares delay, unfinished-vehicle penalty, spillback/blocking time, and switching lost-time terms. | Define stable objective component keys and emit component-level JSON decomposition for static fixtures and closed-loop rows. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md; VERIFIED: codebase grep] |
| STATE-03 | Static fixtures and closed-loop runners emit schema-validated artifacts containing the explicit state fields and objective components needed for audit. | Reuse explicit required-field validation from `run_static_kill_gate.py` and pytest/script checks to make missing state/objective fields fail closed. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py; CITED: /home/samuel/projects/pi_light_OR/tests/test_generate_static_regime_states.py] |
</phase_requirements>

## Summary

Phase 6 should be planned as a repository infrastructure phase, not as a manuscript-writing phase. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md] The planner should create tasks that add machine-readable claim policy, explicit finite-storage state schema, objective decomposition fields, and fail-closed guards around generated reports/artifacts. [CITED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md; VERIFIED: codebase grep]

The existing v1.0 repository already has a useful guard pattern: scripts emit JSON payloads, reports validate route decisions, and renderers scan for forbidden overclaim phrases. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py; CITED: /home/samuel/projects/pi_light_OR/scripts/render_static_kill_gate_report.py; CITED: /home/samuel/projects/pi_light_OR/scripts/render_closed_loop_report.py] Phase 6 should extend that pattern rather than inventing a new framework. [VERIFIED: codebase grep]

The critical planning boundary is that v1.0 evidence must remain pressure-equivalent recovery/compression evidence, while v1.1 improvement/separation claims are allowed only when explicit finite-storage/spillback/switching/service/incident state fields and objective components exist. [CITED: /home/samuel/projects/pi_light_OR/.planning/STATE.md; CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]

**Primary recommendation:** Use existing standalone Python CLI + JSON artifact + pytest/script gate patterns to add `claim_policy`, explicit `finite_storage_state`, and `objective_components` outputs, then make claim/report scanners fail closed on missing evidence or forbidden wording. [VERIFIED: codebase grep; CITED: /home/samuel/projects/pi_light_OR/.planning/codebase/CONVENTIONS.md]

## Project Constraints (from CLAUDE.md)

- The project is an OR-methodology traffic-network-control repository, not a PI-Light enhancement paper. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- The target audience expects mathematical modeling, structural insight, rigorous optimization formulation, and closed-loop computational evidence against strong max-pressure-style baselines. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- The project must be framed as OR / methodological traffic-network control rather than AI-controller benchmarking. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Static one-step LP/ranking evidence is insufficient; closed-loop SUMO multi-seed experiments against strong pressure-style baselines are mandatory for empirical claims. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- The core claim is generalized pressure with scarcity-aware corrections, not universal dominance over max-pressure. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Experiments should remain CPU-oriented using SUMO/TraCI, SciPy/HiGHS, AMPL/HiGHS where useful, and sparse MIP recovery; no GPU pipeline is required. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Scripts must emit auditable JSON/CSV artifacts and tables/figures must trace back to raw experiment outputs. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Max-pressure/backpressure and capacity/spillback-aware variants are first-class baselines, not strawmen. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- New Python scripts should use lowercase snake_case filenames, `argparse`, `Path`, JSON-serializable dictionaries, `main() -> None`, and an `if __name__ == "__main__"` guard. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- OR scripts should run from the repository root or with `PYTHONPATH=/home/samuel/projects/pi_light_OR/scripts` when importing between files in `scripts/`. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- For experiment gates, write a JSON artifact and exit nonzero only when the gate is truly failed. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Do not place new OR experiments inside `pi_light_code/`; keep OR/SUMO work in `scripts/` and outputs in `experiments/dual_sensitivity/`. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Before direct repo edits outside GSD workflow, use GSD entry points unless explicitly bypassed. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Claim policy and forbidden-phrase enforcement | Script / CLI research pipeline | Generated artifact layer | The repository uses standalone Python scripts to generate and validate JSON/report artifacts, so claim enforcement belongs in scripts that can fail closed before reports become evidence. [VERIFIED: codebase grep; CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py] |
| Explicit finite-storage state generation | SUMO/state artifact layer | LP/MILP conversion layer | State fields originate in SUMO metadata, static fixtures, or generated scenario dictionaries, then are consumed by recovery/gate scripts. [CITED: /home/samuel/projects/pi_light_OR/scripts/sample_sumo_states.py; CITED: /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py] |
| Objective decomposition | Optimization/gate layer | Closed-loop metric layer | Static objectives are computed in LP-style summaries, while closed-loop objective components come from metrics such as delay, unfinished vehicles, spillback/blocking, and switching counts. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py; CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py] |
| v1.0 historical evidence quarantine | Reproducibility/report layer | Claim policy layer | Existing reproducibility and paper-artifact scripts already validate source artifact status and route decisions before generating downstream artifacts. [CITED: /home/samuel/projects/pi_light_OR/scripts/render_paper_artifacts.py; CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py] |
| Schema validation | Script / CLI research pipeline | Pytest/script checks | Current sample validation is implemented as explicit required-field checks in scripts and behavior tests under `tests/`. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py; CITED: /home/samuel/projects/pi_light_OR/tests/test_generate_static_regime_states.py] |

## Standard Stack

### Core
| Library / Tool | Version | Purpose | Why Standard |
|----------------|---------|---------|--------------|
| Python | 3.14.4 available on host | Standalone CLIs, JSON schema checks, deterministic fixture generation | Existing repository scripts are Python CLIs and the host reports Python 3.14.4. [VERIFIED: local command; CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] |
| Python `argparse` | stdlib | CLI arguments for generators and gates | Python docs state `argparse` makes user-friendly command-line interfaces and supports `ArgumentParser`, `add_argument()`, and `parse_args()`. [CITED: https://docs.python.org/3/library/argparse.html] |
| Python `json` | stdlib | JSON artifact read/write and machine-readable claim/state/objective payloads | Python docs state `json.dumps` serializes Python objects to JSON strings and `json.loads` deserializes JSON to Python objects. [CITED: https://docs.python.org/3.14/library/json.html] |
| Python `pathlib.Path` | stdlib | File paths for CLI inputs/outputs | Existing scripts use `Path` for new file path parameters. [CITED: /home/samuel/projects/pi_light_OR/.planning/codebase/CONVENTIONS.md] |
| SUMO | 1.26.0 available on host | Local CPU traffic simulation and network metadata source | Host command reports `Eclipse SUMO sumo 1.26.0`, and project stack requires SUMO/TraCI for experiments. [VERIFIED: local command; CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] |
| TraCI / sumolib | 1.26.0 available on host | Python access to SUMO simulation state and network parsing | TraCI official docs show `import traci`, `traci.start`, repeated `traci.simulationStep()`, and `traci.close()`. [VERIFIED: local command; CITED: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html] |
| NumPy | 2.4.3 available on host | Numeric arrays and deterministic finite-storage component calculations | Existing OR scripts use NumPy arrays for queues, capacities, service, and scores. [VERIFIED: local command; CITED: /home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py] |
| SciPy | 1.17.1 available on host | LP/MILP summaries and future finite-storage oracle checks | SciPy docs state `linprog` solves linear programs with equality/inequality constraints and HiGHS methods expose success/status and marginals. [VERIFIED: local command; CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html] |
| pytest | 9.0.2 available on host | Fast behavior tests for schema/claim guard failures | Host command reports pytest 9.0.2 and repository has `tests/test_*.py` behavior checks. [VERIFIED: local command; VERIFIED: codebase grep] |

### Supporting
| Library / Tool | Version | Purpose | When to Use |
|----------------|---------|---------|-------------|
| `csv` stdlib | stdlib | CSV audit surfaces for tables and gate summaries | Use for regenerated tables/claim-audit summaries that need spreadsheet-style inspection. [CITED: /home/samuel/projects/pi_light_OR/scripts/render_paper_artifacts.py] |
| `datetime` stdlib | stdlib | Timestamping claim-policy/audit manifests | Use for reproducibility/claim-audit manifests that need generated-at metadata. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py] |
| `subprocess` stdlib | stdlib | Optional block orchestration and script execution | Use only for reproduction/block runners; direct validation scripts should expose pure functions where possible. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Explicit Python required-field checks | External JSON Schema package | Avoid external dependency installation and match existing repository fail-closed checks; external schema libraries can be deferred if schema complexity grows. [VERIFIED: codebase grep] |
| New test framework/config | Existing pytest-compatible tests plus script self-tests | Pytest is available and existing tests already use `test_*.py`; adding config is optional rather than required for Phase 6. [VERIFIED: local command; VERIFIED: codebase grep] |
| Markdown-only claim templates | Machine-readable JSON claim policy + scanner | Markdown-only discipline cannot fail closed, while scripts can scan generated artifacts and exit nonzero. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md] |

**Installation:** No new package installation is recommended for Phase 6. [VERIFIED: local command; CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md]

```bash
# No new packages required for Phase 6; use existing Python stdlib, SUMO/TraCI, NumPy/SciPy, and pytest.
```

**Version verification:** Versions were verified with `python3 --version`, `sumo --version`, `netconvert --version`, Python imports for `numpy`, `scipy`, `traci`, `sumolib`, and `python3 -m pytest --version`. [VERIFIED: local command]

## Package Legitimacy Audit

Phase 6 should not install external packages. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md]

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| none | n/a | n/a | n/a | n/a | n/a | No new packages recommended. [VERIFIED: research decision] |

**Packages removed due to slopcheck [SLOP] verdict:** none because no package installation is recommended. [VERIFIED: research decision]
**Packages flagged as suspicious [SUS]:** none because no package installation is recommended. [VERIFIED: research decision]

## Architecture Patterns

### System Architecture Diagram

```text
Phase 6 primary flow [VERIFIED: codebase grep]

CONTEXT/REQUIREMENTS/STATE
        |
        v
Machine-readable claim policy artifact
        |
        +--> Claim scanner CLI scans planning docs, refine logs, and generated reports
        |        |
        |        +--> forbidden wording found without v1.1 evidence --> FAILED + nonzero exit
        |        |
        |        +--> no forbidden wording or allowed with explicit evidence --> PASSED JSON
        |
        v
Finite-storage state schema helper
        |
        +--> static fixture generator emits explicit state fields
        |        |
        |        v
        |   schema validator checks required state fields
        |
        +--> closed-loop runner/report rows include objective components
                 |
                 v
          downstream Phase 7-12 gates consume explicit state/objective/claim-audit artifacts
```

### Recommended Project Structure

```text
scripts/
├── claim_policy.py                         # constants/helpers for allowed claims, forbidden phrases, evidence requirements [RECOMMENDED: codebase pattern]
├── audit_claim_discipline.py               # CLI scans repo/report artifacts and writes claim audit JSON [RECOMMENDED: codebase pattern]
├── finite_storage_schema.py                # reusable required-field validation and objective component helpers [RECOMMENDED: codebase pattern]
├── generate_static_regime_states.py        # extend to emit explicit finite_storage_state fields [CITED: /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py]
├── run_static_kill_gate.py                 # extend validation to require explicit fields for v1.1 state artifacts [CITED: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py]
└── run_closed_loop_sumo.py                 # extend rows with objective_components and explicit observed state summary [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
experiments/dual_sensitivity/
├── phase6_claim_policy.json                # bounded claim policy and forbidden wording [RECOMMENDED: Phase 6]
├── phase6_claim_audit.json                 # scanner output [RECOMMENDED: Phase 6]
├── phase6_explicit_state_schema.json       # schema documentation/artifact, not an external package schema [RECOMMENDED: Phase 6]
└── phase6_state_objective_fixtures.json    # deterministic explicit finite-storage fixture payload [RECOMMENDED: Phase 6]
tests/
├── test_claim_discipline.py                # forbidden wording and missing evidence fail closed [RECOMMENDED: Phase 6]
└── test_finite_storage_schema.py           # explicit fields/objective components are required [RECOMMENDED: Phase 6]
```

### Pattern 1: Fail-Closed Claim Guard
**What:** Store permitted claims, forbidden phrases, evidence prerequisites, and scanned artifact paths in a JSON-friendly policy, then make a CLI produce `PASSED` or `FAILED` and exit nonzero on failure. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py]
**When to use:** Use for any generated report, future manuscript-input artifact, or planning/refine-log text that could reinterpret v1.0 pressure-equivalent evidence as superiority. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
**Example:**
```python
# Source: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py and render_paper_artifacts.py
FORBIDDEN_PHRASES = [
    "dual universally beats pressure",
    "max-pressure strawman",
    "proves superiority",
    "deployable superiority",
    "static evidence proves closed-loop",
]
status = "PASSED" if expected_ok and not hits else "FAILED"
if manifest["status"] != "PASSED":
    raise SystemExit(1)
```

### Pattern 2: Explicit Required-Field Validation
**What:** Validate required fields at artifact ingestion before computing any gate metric, and raise `ValueError` with the missing fields. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py]
**When to use:** Use for `finite_storage_state`, `objective_components`, and future score-decomposition fields. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
**Example:**
```python
# Source: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py
REQUIRED_SAMPLE_FIELDS = {"time", "queues", "vehicle_counts", "capacities", "tls_movements"}
missing = REQUIRED_SAMPLE_FIELDS - set(sample)
if missing:
    raise ValueError(f"Sample {sample_idx} in {path} is missing fields: {sorted(missing)}")
```

### Pattern 3: Stable Objective Component Keys
**What:** Emit a nested `objective_components` object with predeclared keys: `delay`, `unfinished_vehicle_penalty`, `spillback_blocking_time`, and `switching_lost_time`. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
**When to use:** Use in deterministic fixtures and closed-loop rows so later gates can attribute any claimed separation to a specific objective component. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md]
**Example:**
```python
# Source: derived from existing run_closed_loop_sumo.py metric fields and STATE-02 requirements
objective_components = {
    "delay": float(waiting_delay),
    "unfinished_vehicle_penalty": float(unfinished * censor_penalty),
    "spillback_blocking_time": float(sum(obs["spillback"] + obs["blocking"] for obs in observations)),
    "switching_lost_time": float(switching_count * switching_lost_time_per_switch),
}
```

### Pattern 4: Explicit Finite-Storage State Object
**What:** Add a nested `finite_storage_state` object rather than top-level ad hoc fields. [RECOMMENDED: research synthesis]
**When to use:** Use for every generated explicit v1.1 state sample and every static/closed-loop audit row that supports binding-regime reasoning. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
**Example:**
```python
# Source: STATE-01 requirements + existing sample schema in sample_sumo_states.py
audit_state = {
    "downstream_storage": {edge: float(capacities[edge]) for edge in capacities},
    "residual_receiving_capacity": {edge: max(float(capacities[edge]) - float(queues.get(edge, 0.0)), 0.0) for edge in capacities},
    "spillback_blocking": {edge: float(queues.get(edge, 0.0)) / max(float(capacities[edge]), 1.0) >= 0.85 for edge in capacities},
    "switching_loss_state": {"current_phase": current_phase, "time_since_switch": time_since_switch},
    "service_urgency": {edge: float(queues.get(edge, 0.0)) for edge in capacities},
    "incident_capacity_drop": {"active": bool(capacity_drop_edge), "edge": capacity_drop_edge, "factor": capacity_drop_factor},
}
```

### Anti-Patterns to Avoid
- **Proxy labels as evidence:** Do not treat `supply_binding_proxy`, `corridor_bottleneck_proxy`, or `demand_shift_proxy` as final binding-state evidence because the current v1.0 generator explicitly marks some regimes as proxy/unsupported. [CITED: /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py; CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
- **Report-only discipline:** Do not rely only on Markdown caveats because Phase 6 requires schema validation or explicit required-field checks in scripts. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md]
- **Universal dominance wording:** Do not allow universal, deployment-level, or superiority wording without v1.1 binding evidence because the roadmap bounds improvement claims to binding regimes. [CITED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md]
- **New OR code inside `pi_light_code/`:** Do not place Phase 6 scripts under `pi_light_code/` because project conventions keep OR/SUMO experiments in `scripts/`. [CITED: /home/samuel/projects/pi_light_OR/.planning/codebase/STRUCTURE.md]
- **Mocking optimization/JSON output:** Do not mock solver or JSON output creation in gate tests because project testing conventions prefer deterministic fixtures and real artifact creation. [CITED: /home/samuel/projects/pi_light_OR/.planning/codebase/TESTING.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI parsing | Custom `sys.argv` parser | Python `argparse` | Official Python docs provide `ArgumentParser`, `add_argument()`, and `parse_args()` for CLI parsing. [CITED: https://docs.python.org/3/library/argparse.html] |
| JSON serialization | String concatenation or manual escaping | Python `json` | Official Python docs provide `json.dumps`, `json.dump`, `json.loads`, and `json.load`. [CITED: https://docs.python.org/3.14/library/json.html] |
| SUMO control loop | Manual simulator process protocol | TraCI Python API | SUMO docs show Python TraCI usage with `traci.start`, `simulationStep`, and `traci.close`. [CITED: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html] |
| LP shadow prices | Custom simplex or dual extraction | SciPy `linprog(method="highs")` | SciPy docs expose optimization result success/status and marginals described as dual values/shadow prices/Lagrange multipliers. [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html] |
| Claim discipline | Manual reviewer memory | Machine-readable claim policy + scanner | Existing scripts already implement forbidden-phrase scanning and fail-closed manifests. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py; CITED: /home/samuel/projects/pi_light_OR/scripts/render_paper_artifacts.py] |
| Schema validation | Informal Markdown checklist | Explicit required-field checks in Python | Existing `run_static_kill_gate.py` validates sample fields before gate computation. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py] |

**Key insight:** Phase 6 succeeds by making unsupported claims and missing finite-storage fields mechanically impossible to pass through the artifact pipeline, not by adding narrative caveats. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md]

## Common Pitfalls

### Pitfall 1: Reusing v1.0 pressure-equivalent artifacts as superiority evidence
**What goes wrong:** A report or table describes v1.0 static/closed-loop results as dual superiority. [CITED: /home/samuel/projects/pi_light_OR/.planning/STATE.md]
**Why it happens:** Existing artifacts have route decisions and performance tables, but v1.0 route is pressure-equivalent. [CITED: /home/samuel/projects/pi_light_OR/.planning/STATE.md; CITED: /home/samuel/projects/pi_light_OR/scripts/render_paper_artifacts.py]
**How to avoid:** Require a claim scanner to distinguish `pressure_equivalent_recovery` evidence from `binding_regime_separation` evidence. [RECOMMENDED: research synthesis]
**Warning signs:** Phrases such as `proves superiority`, `dual universally beats pressure`, `deployable superiority`, or `static evidence proves closed-loop` appear in generated artifacts. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py]

### Pitfall 2: Treating proxy regimes as explicit finite-storage states
**What goes wrong:** Proxy labels become evidence for spillback/supply/corridor constraints without explicit receiving-capacity or blocking fields. [CITED: /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py]
**Why it happens:** v1.0 generator preserves legacy sampled-state schema and marks unsupported regimes instead of modeling explicit constraints. [CITED: /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py]
**How to avoid:** Add `finite_storage_state` required fields and reject any v1.1 binding claim when those fields are missing. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
**Warning signs:** Regime names ending in `_proxy`, `proxy_reason`, or `unsupported_by_current_model` are present without new explicit fields. [CITED: /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py]

### Pitfall 3: Objective totals without component attribution
**What goes wrong:** Later gates cannot tell whether an observed separation is due to delay, unfinished vehicles, spillback/blocking, or switching lost time. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
**Why it happens:** Existing closed-loop metrics include delay, unfinished vehicle count, spillback count, blocking count, and switching count, but not a single predeclared objective-component object. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
**How to avoid:** Emit `objective_components` with stable keys in every explicit v1.1 fixture/result row. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md]
**Warning signs:** A result has `objective` or aggregate metrics but no `objective_components`. [VERIFIED: codebase grep]

### Pitfall 4: Overly narrow forbidden phrase list
**What goes wrong:** Claim guards miss paraphrases such as deployment-level, broad superiority, or dominance language. [RECOMMENDED: research synthesis]
**Why it happens:** Existing lists contain exact phrases and may not cover all v1.1 forbidden wording. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py; CITED: /home/samuel/projects/pi_light_OR/scripts/render_paper_artifacts.py]
**How to avoid:** Store forbidden patterns and allowed evidence prerequisites centrally in `claim_policy.py` or `phase6_claim_policy.json`. [RECOMMENDED: research synthesis]
**Warning signs:** Multiple scripts duplicate slightly different forbidden phrase lists. [VERIFIED: codebase grep]

### Pitfall 5: Tests lag behind codebase reality
**What goes wrong:** Planning assumes no test framework, but the repository now has pytest-compatible tests. [VERIFIED: codebase grep]
**Why it happens:** `.planning/codebase/TESTING.md` says no dedicated unit runner was configured at analysis time, while current filesystem contains `tests/test_*.py` and pytest is available. [CITED: /home/samuel/projects/pi_light_OR/.planning/codebase/TESTING.md; VERIFIED: local command]
**How to avoid:** Plan Phase 6 tests under `tests/` and run targeted pytest commands. [VERIFIED: codebase grep]
**Warning signs:** Plans only add manual scripts and omit `tests/test_claim_discipline.py` or `tests/test_finite_storage_schema.py`. [RECOMMENDED: research synthesis]

## Code Examples

Verified patterns from official and repository sources. [VERIFIED: codebase grep; CITED: official docs]

### CLI + JSON Artifact + Nonzero Gate Exit
```python
# Source: /home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py
payload = {
    "experiment": "block0_dual_sanity",
    "status": "PASSED" if gate_a_pass else "FAILED",
    "results": results,
}
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps({"status": payload["status"], "out": str(out_path)}, indent=2))
if not gate_a_pass:
    raise SystemExit(1)
```

### Required-Field Validation
```python
# Source: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py
missing = REQUIRED_SAMPLE_FIELDS - set(sample)
if missing:
    raise ValueError(f"Sample {sample_idx} in {path} is missing fields: {sorted(missing)}")
```

### Claim Scanner Pattern
```python
# Source: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py
lowered = path.read_text(encoding="utf-8").lower()
for phrase in FORBIDDEN_PHRASES:
    if phrase in lowered:
        hits.append({"path": rel_path, "phrase": phrase})
```

### SUMO / TraCI Loop Pattern
```python
# Source: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html and /home/samuel/projects/pi_light_OR/scripts/sample_sumo_states.py
traci.start(cmd)
try:
    for step in range(steps + 1):
        traci.simulationStep()
        queues = {edge_id: float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids}
finally:
    traci.close(False)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Proxy-only binding labels such as `supply_binding_proxy` and `corridor_bottleneck_proxy` | Explicit downstream storage, receiving capacity, spillback/blocking, switching, service urgency, and incident/capacity-drop fields | Required by v1.1 Phase 6 on 2026-05-23 | Downstream theory/gates can audit whether a binding claim is supported by actual state fields. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md; CITED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md] |
| v1.0 route language of pressure-equivalent generalized-pressure symbolic recovery | Bounded v1.1 claim policy: slack recovery/ties; improvements only in explicit binding regimes | v1.1 roadmap created 2026-05-23 | Prevents v1.0 artifacts from being reinterpreted as dual superiority. [CITED: /home/samuel/projects/pi_light_OR/.planning/STATE.md] |
| Duplicated forbidden phrase lists in multiple scripts | Central claim policy helper/artifact reused by scanners/renderers | Recommended for Phase 6 | Reduces drift between report, reproducibility, and paper-artifact guards. [VERIFIED: codebase grep; RECOMMENDED: research synthesis] |
| Metric-only closed-loop rows | Metric rows plus `objective_components` | Required by STATE-02/STATE-03 | Later separation gates can attribute objective improvement to predeclared components. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] |

**Deprecated/outdated:**
- Treating static one-step evidence as deployment-level performance evidence is out of scope and contradicted by project constraints. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Treating `full_dual_symbolic` or `local_pilight` as feasible without safe wiring is out of scope because v1.0 marks them not feasible. [CITED: /home/samuel/projects/pi_light_OR/.planning/STATE.md; CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
- Using proxy-only regime labels as final evidence is explicitly out of scope for v1.1. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | A central `claim_policy.py` plus JSON policy artifact is the best implementation shape. [ASSUMED] | Recommended Project Structure | Planner could choose a JSON-only or module-only approach; risk is minor if all scanners share a single source of truth. |
| A2 | `switching_lost_time` can initially be computed from `switching_count * switching_lost_time_per_switch`. [ASSUMED] | Architecture Patterns / Objective Example | Later theory/controller phases may require a different lost-time model; keep the component key stable and allow formula refinement. |
| A3 | `service_urgency` can initially use queue-derived urgency in explicit fixtures. [ASSUMED] | Architecture Patterns / State Example | Later service fairness/priority requirements may require a richer urgency definition. |
| A4 | Regex/substring claim scanning is sufficient for Phase 6 fail-closed guards. [ASSUMED] | Common Pitfalls | Sophisticated paraphrases may evade exact phrase scanning; mitigate by using broad forbidden stems and conservative allowed-evidence checks. |

## Open Questions

All Phase 6 planning questions are **RESOLVED** for implementation. These conclusions are scoped to Phase 6 infrastructure; later theory/controller phases may refine formulas without changing the Phase 6 artifact contracts.

1. **Claim policy location: Python constants plus JSON artifact.** [RESOLVED]
   - RESOLVED conclusion: Implement `scripts/claim_policy.py` as the reusable source of truth for renderers/scanners, and have it write `experiments/dual_sensitivity/phase6_claim_policy.json` for non-code audit. [VERIFIED: codebase grep]
   - Implementation implication: Plans must create both the Python helper and generated JSON policy artifact; downstream scripts import the helper rather than duplicating forbidden phrase lists.

2. **Phase 6 `switching_lost_time` formula: shared metric helper with explicit metadata.** [RESOLVED]
   - RESOLVED conclusion: Predeclare the stable key `switching_lost_time` and compute it in Phase 6 as `switching_count * switching_lost_time_per_switch` through a shared `build_objective_components_from_metrics()` helper. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]
   - Implementation implication: Static fixtures and closed-loop rows must use the same objective-helper contract, and generated schema/artifact metadata must name the formula and default parameter so Phase 7/8 can refine the parameter without renaming the component.

3. **Explicit finite-storage fields: new Phase 6/v1.1 artifacts only; do not backfill old v1.0 evidence.** [RESOLVED]
   - RESOLVED conclusion: Preserve old v1.0 artifacts as historical pressure-equivalent evidence and create new Phase 6 artifacts with explicit `finite_storage_state` and `objective_components`. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md]
   - Implementation implication: Claim and paper-artifact guards must fail closed when Phase 6 guard artifacts are missing, and must mark v1.0 proxy-only artifacts as insufficient for v1.1 binding-regime superiority instead of mutating them.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | All Phase 6 scripts/tests | ✓ | 3.14.4 | None needed. [VERIFIED: local command] |
| pytest | Phase 6 behavior tests | ✓ | 9.0.2 | Run test files directly as scripts if pytest is unavailable. [VERIFIED: local command; CITED: /home/samuel/projects/pi_light_OR/tests/test_generate_static_regime_states.py] |
| SUMO `sumo` | Optional closed-loop/objective state audit paths | ✓ | 1.26.0 | Static deterministic fixtures can validate schema without live SUMO. [VERIFIED: local command] |
| SUMO `netconvert` | Network regeneration if needed | ✓ | 1.26.0 | Use existing committed network XML assets if regeneration is not needed. [VERIFIED: local command; CITED: /home/samuel/projects/pi_light_OR/.planning/codebase/STRUCTURE.md] |
| TraCI | SUMO state sampling and closed-loop scripts | ✓ | 1.26.0 | Skip live SUMO checks and validate static fixtures only for fast Phase 6 tests. [VERIFIED: local command] |
| sumolib | Network metadata parsing | ✓ | 1.26.0 | Use existing artifact fixtures if network parsing is not required. [VERIFIED: local command] |
| NumPy | Numeric state/objective calculations | ✓ | 2.4.3 | Python lists/floats for simple schema tests. [VERIFIED: local command] |
| SciPy | LP/dual sanity compatibility | ✓ | 1.17.1 | Phase 6 claim/state schema tasks can avoid new solver work. [VERIFIED: local command] |

**Missing dependencies with no fallback:** None detected for Phase 6. [VERIFIED: local command]

**Missing dependencies with fallback:** None detected for required Phase 6 work. [VERIFIED: local command]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 available; existing tests are also directly executable Python files. [VERIFIED: local command; VERIFIED: codebase grep] |
| Config file | none detected in the checked project files; tests rely on direct imports and `sys.path` insertion. [VERIFIED: codebase grep; CITED: /home/samuel/projects/pi_light_OR/tests/test_closed_loop_sumo.py] |
| Quick run command | `python3 -m pytest /home/samuel/projects/pi_light_OR/tests/test_claim_discipline.py /home/samuel/projects/pi_light_OR/tests/test_finite_storage_schema.py -q` [RECOMMENDED: research synthesis] |
| Full suite command | `python3 -m pytest /home/samuel/projects/pi_light_OR/tests -q` [VERIFIED: local command; VERIFIED: codebase grep] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| CLAIM-01 | Claim policy permits slack recovery/ties and binding-only improvements. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | unit/schema | `python3 -m pytest /home/samuel/projects/pi_light_OR/tests/test_claim_discipline.py::test_claim_policy_encodes_bounded_claim -q` | ❌ Wave 0 |
| CLAIM-02 | Claim scanner fails on v1.0 superiority wording without v1.1 evidence. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | unit/integration | `python3 -m pytest /home/samuel/projects/pi_light_OR/tests/test_claim_discipline.py::test_v1_pressure_equivalent_superiority_wording_fails_closed -q` | ❌ Wave 0 |
| STATE-01 | Generated samples contain explicit finite-storage fields instead of proxy-only labels. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | unit/schema | `python3 -m pytest /home/samuel/projects/pi_light_OR/tests/test_finite_storage_schema.py::test_explicit_finite_storage_state_required_fields -q` | ❌ Wave 0 |
| STATE-02 | Objective decomposition contains delay, unfinished-vehicle penalty, spillback/blocking time, and switching lost-time terms. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | unit/schema | `python3 -m pytest /home/samuel/projects/pi_light_OR/tests/test_finite_storage_schema.py::test_objective_components_required_keys -q` | ❌ Wave 0 |
| STATE-03 | Static fixtures and closed-loop runners emit schema-validated artifacts and fail closed when fields are missing. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] | integration | `python3 -m pytest /home/samuel/projects/pi_light_OR/tests/test_finite_storage_schema.py::test_phase6_fixture_generation_and_validation -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** Run targeted tests for changed claim/schema code. [RECOMMENDED: research synthesis]
- **Per wave merge:** Run `python3 -m pytest /home/samuel/projects/pi_light_OR/tests -q`. [VERIFIED: local command]
- **Phase gate:** Run Phase 6 claim audit CLI plus full pytest suite before `/gsd:verify-work`. [RECOMMENDED: research synthesis]

### Wave 0 Gaps
- [ ] `/home/samuel/projects/pi_light_OR/tests/test_claim_discipline.py` — covers CLAIM-01 and CLAIM-02. [RECOMMENDED: research synthesis]
- [ ] `/home/samuel/projects/pi_light_OR/tests/test_finite_storage_schema.py` — covers STATE-01, STATE-02, and STATE-03. [RECOMMENDED: research synthesis]
- [ ] `/home/samuel/projects/pi_light_OR/scripts/claim_policy.py` or equivalent single source of truth — avoids duplicated forbidden phrase lists. [RECOMMENDED: research synthesis]
- [ ] `/home/samuel/projects/pi_light_OR/scripts/finite_storage_schema.py` or equivalent shared validation helper — avoids inconsistent required-field checks. [RECOMMENDED: research synthesis]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | No authentication surface is part of Phase 6 local research scripts. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] |
| V3 Session Management | no | No session management surface is part of Phase 6 local research scripts. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] |
| V4 Access Control | no | No deployed API or user role boundary is part of Phase 6. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md] |
| V5 Input Validation | yes | Validate JSON artifact schemas and CLI arguments with explicit required-field checks and finite-number checks. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py] |
| V6 Cryptography | no | Phase 6 does not handle secrets or cryptographic material. [VERIFIED: codebase grep] |

### Known Threat Patterns for local script/artifact stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Malformed JSON artifact bypasses claim/state checks | Tampering | Reject missing fields, wrong types, and non-finite numbers before computing summaries. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py] |
| Generated report overclaims evidence scope | Repudiation / Information Integrity | Central forbidden phrase scanning plus evidence-prerequisite checks. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py] |
| Path confusion from relative working directories | Tampering / Reliability | Use repository-root execution and `Path`-based explicit input/output paths. [CITED: /home/samuel/projects/pi_light_OR/.planning/codebase/CONVENTIONS.md] |
| Accidental execution of untrusted packages | Tampering | Do not add new package installs for Phase 6. [VERIFIED: research decision] |

## Sources

### Primary (HIGH confidence)
- `/home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md` — locked Phase 6 decisions, scope, and deferred work. [CITED: /home/samuel/projects/pi_light_OR/.planning/phases/06-claim-discipline-and-explicit-state-foundation/06-CONTEXT.md]
- `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md` — CLAIM-01, CLAIM-02, STATE-01, STATE-02, STATE-03. [CITED: /home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md]
- `/home/samuel/projects/pi_light_OR/.planning/ROADMAP.md` — Phase 6 goal and success criteria. [CITED: /home/samuel/projects/pi_light_OR/.planning/ROADMAP.md]
- `/home/samuel/projects/pi_light_OR/.planning/STATE.md` — v1.1 state, v1.0 pressure-equivalent decisions, and deferred items. [CITED: /home/samuel/projects/pi_light_OR/.planning/STATE.md]
- `/home/samuel/projects/pi_light_OR/CLAUDE.md` — project constraints, stack, architecture, and conventions. [CITED: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- `/home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py` — reproducibility manifest and forbidden phrase scanner pattern. [CITED: /home/samuel/projects/pi_light_OR/scripts/reproduce_blocks.py]
- `/home/samuel/projects/pi_light_OR/scripts/render_paper_artifacts.py` — source-artifact validation and paper-facing claim guard pattern. [CITED: /home/samuel/projects/pi_light_OR/scripts/render_paper_artifacts.py]
- `/home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py` — current proxy/unsupported regime generation. [CITED: /home/samuel/projects/pi_light_OR/scripts/generate_static_regime_states.py]
- `/home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py` — required-field validation, route decision, and gate payload pattern. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_static_kill_gate.py]
- `/home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py` — closed-loop metrics, not-feasible controller handling, and SUMO/TraCI loop. [CITED: /home/samuel/projects/pi_light_OR/scripts/run_closed_loop_sumo.py]

### Secondary (MEDIUM confidence)
- Python `argparse` docs — CLI parser API. [CITED: https://docs.python.org/3/library/argparse.html]
- Python `json` docs — JSON serialization/deserialization API. [CITED: https://docs.python.org/3.14/library/json.html]
- SUMO TraCI Python docs — `traci.start`, `simulationStep`, and `traci.close` usage. [CITED: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html]
- SciPy `linprog` docs — LP form, HiGHS methods, success/status, and marginals. [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html]

### Tertiary (LOW confidence)
- None from web search; no WebSearch results were used. [VERIFIED: research process]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions were verified locally and APIs were checked in official docs. [VERIFIED: local command; CITED: official docs]
- Architecture: HIGH — recommendations follow existing script/artifact/test patterns found in the repository. [VERIFIED: codebase grep]
- Pitfalls: HIGH for v1.0 overclaim/proxy risks because they are documented in planning and scripts; MEDIUM for exact v1.1 objective formulas because later theory/controller phases may refine them. [CITED: /home/samuel/projects/pi_light_OR/.planning/STATE.md; ASSUMED]

**Research date:** 2026-05-23 [VERIFIED: system currentDate]
**Valid until:** 2026-06-22 for repository integration patterns; revisit after Phase 7 theory finalizes exact finite-storage objective formulas. [ASSUMED]
