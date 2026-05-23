---
phase: 05-reproducibility-and-repository-hardening
plan: "01"
status: completed
completed: 2026-05-23
requirements:
  - REPR-01
  - REPR-02
---

# 05-01 Summary: Root Reproducibility Entrypoint and Environment

## Completed

- Created `environment.yml` for a CPU/SUMO/optimization workflow with Python, NumPy, SciPy, SUMO/TraCI/sumolib, pytest, pandas, and optional AMPL Python support.
- Created root `README.md` with research question, contribution claim, current status, repository layout, setup path, block-level reproduction commands, artifact paths, known limitations, next experiments, and claim discipline guardrails.

## Validation

- `environment.yml` content check passed: includes SUMO/SciPy/NumPy and excludes prohibited accelerator/model-serving dependencies and secret/license material.
- `README.md` content check passed: includes required reproducibility sections, references Phase 5 scripts, states `pressure-equivalent`, and avoids forbidden overclaim phrases.

## Requirement Coverage

- REPR-01 satisfied by `README.md`.
- REPR-02 satisfied by `environment.yml`.
