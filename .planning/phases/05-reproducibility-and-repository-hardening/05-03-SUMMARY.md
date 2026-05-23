---
phase: 05-reproducibility-and-repository-hardening
plan: "03"
status: completed
completed: 2026-05-23
requirements:
  - REPR-04
  - REPR-05
---

# 05-03 Summary: Paper Tables and Figure Data from Raw Artifacts

## Completed

- Created `scripts/render_paper_artifacts.py` with deterministic raw-artifact extraction functions: `load_inputs`, `build_tables`, `build_figure_data`, `write_csv`, and `main`.
- Generated `experiments/dual_sensitivity/paper_tables.csv` from Block 0, sparse recovery, static kill-gate, closed-loop suite, and reproducibility manifest inputs.
- Generated `experiments/dual_sensitivity/paper_figure_data.csv` with plot-ready static and closed-loop metric series.
- Generated `experiments/dual_sensitivity/paper_artifacts_manifest.json` recording source artifacts, generated artifacts, row counts, route decision, claim discipline, and requirements covered.
- Re-ran `scripts/reproduce_blocks.py --audit` so `reproducibility_manifest.json` now records paper artifacts as existing and parseable.

## Validation

- `python3 -m py_compile scripts/render_paper_artifacts.py` passed.
- `python3 scripts/render_paper_artifacts.py --out-dir experiments/dual_sensitivity` produced status `PASSED`.
- Paper artifact assertions passed: required table IDs exist, all table/figure rows include `source_artifact`, route decision is `pressure-equivalent`, requirements include REPR-04/REPR-05, and forbidden overclaim phrases are absent from generated content.
- Final reproducibility audit passed and includes `paper_tables.csv`, `paper_figure_data.csv`, and `paper_artifacts_manifest.json`.

## Requirement Coverage

- REPR-04 completed by structured raw artifact audit plus generated table/figure CSV outputs.
- REPR-05 satisfied by script-generated paper-facing tables and figure data with row-level source traceability.
