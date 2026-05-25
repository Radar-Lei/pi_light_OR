# Phase 12: Reproducibility and Future Claim Inputs - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-24
**Phase:** 12-Reproducibility and Future Claim Inputs
**Areas discussed:** Reproducibility package scope, future claim inputs, CPU/SUMO commands, provenance manifest, artifact format

---

## Reproducibility Package Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated Phase 12 package | Generate v1.1 reproducibility outputs from raw artifacts without editing paper text. | ✓ |
| Extend existing Phase 4 renderer only | Reuse old renderer semantics for all new outputs. | |
| Manual summary document | Write a human summary by hand. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Preserves raw-to-derived traceability and avoids manual transcription.

---

## Future Claim Inputs

| Option | Description | Selected |
|--------|-------------|----------|
| Bounded templates and claim-audit artifacts | Produce machine-readable future inputs with qualifiers and forbidden-claim checks. | ✓ |
| Draft manuscript prose | Start writing paper-facing claims now. | |
| Broad superiority summary | Summarize all v1.1 artifacts as dominance evidence. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Phase 12 must not draft the paper or convert INCONCLUSIVE evidence into claims.

---

## CPU/SUMO Commands

| Option | Description | Selected |
|--------|-------------|----------|
| Fast checks plus opt-in expensive runs | Provide reproducibility commands and keep long-horizon rows fail-closed unless explicitly executed. | ✓ |
| Always execute full long-horizon suite | Force 2160+ SUMO rows during Phase 12. | |
| Summary-only commands | Avoid rerunnable scripts and just document artifacts. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Matches CPU/SUMO constraint and current Phase 11 runtime guard behavior.

---

## Provenance Manifest

| Option | Description | Selected |
|--------|-------------|----------|
| Raw-to-derived manifest | Map every derived table/claim input to raw artifacts, statuses, and commands. | ✓ |
| Loose artifact list | List files without status or command provenance. | |
| Paper appendix outline | Organize outputs as future appendix prose. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Supports REPRO-01 and REPRO-02 without manuscript drafting.

---

## Artifact Format

| Option | Description | Selected |
|--------|-------------|----------|
| JSON authoritative, CSV/Markdown derived | Use JSON for machine-readable truth, CSV for table data, Markdown for human review. | ✓ |
| Markdown-only | Human-readable but weaker for verification. | |
| CSV-only | Useful for tables but too weak for status/caveat metadata. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Follows existing script-oriented artifact conventions.

---

## Claude's Discretion

- Exact Phase 12 script/test filenames and output names may be chosen during planning if they preserve `phase12_*` artifact family, fail-closed status propagation, and raw-to-derived traceability.
- Synthetic tests should validate claim audit and provenance before any expensive reproduction run.

## Deferred Ideas

- Full manuscript drafting, related work, captions, and submission preparation.
- Large benchmark expansion and neural/MARL baselines.
- Actually executing the full Phase 11 long-horizon SUMO suite as an expensive opt-in run.
