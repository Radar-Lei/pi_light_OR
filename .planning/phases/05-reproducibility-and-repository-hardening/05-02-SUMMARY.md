---
phase: 05-reproducibility-and-repository-hardening
plan: "02"
status: completed
completed: 2026-05-23
requirements:
  - REPR-03
  - REPR-04
---

# 05-02 Summary: Block-Oriented Reproduction and Artifact Audit

## Completed

- Created `scripts/reproduce_blocks.py` with a fixed block registry for `block0`, `sparse_recovery`, `static_kill_gate`, `closed_loop_smoke`, `closed_loop_main`, and `paper_artifacts`.
- Added `--list`, selected `--run --block ...`, and `--audit --manifest-out ...` modes.
- Generated `experiments/dual_sensitivity/reproducibility_manifest.json` mapping blocks to commands, artifacts, parse checks, row/result counts, and claim-discipline checks.

## Validation

- `python3 -m py_compile scripts/reproduce_blocks.py` passed.
- `python3 scripts/reproduce_blocks.py --list` exposes all required block names.
- `python3 scripts/reproduce_blocks.py --audit --manifest-out experiments/dual_sensitivity/reproducibility_manifest.json` produced `status=PASSED`.
- Manifest validation confirmed required core JSON/CSV artifacts exist and parse, requirements include REPR-03/REPR-04, and forbidden overclaim phrases are absent.

## Requirement Coverage

- REPR-03 satisfied by the block-oriented reproduction registry and CLI.
- REPR-04 partially satisfied by machine-checkable artifact audit manifest; 05-03 completes table/figure regeneration.
