# Phase 11: Long-Horizon Paired-Seed Evidence - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-24
**Phase:** 11-Long-Horizon Paired-Seed Evidence
**Areas discussed:** Evidence scope, experiment profile, comparator set, paired statistics, Gate C fail-closed rule, claim discipline

---

## Evidence Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Binding stress regimes only | Gate C uses Phase 10 explicit binding stress tags; slack scenarios are context only. | ✓ |
| All scenarios | Mix slack and binding scenarios into one dominance family. | |
| Phase 10 smoke reuse | Treat Phase 10 smoke rows as dominance evidence. | |

**User's choice:** Auto-selected recommended default.
**Notes:** User requested autonomous progress unless necessary. This preserves bounded claim discipline.

---

## Experiment Profile

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated Phase 11 profile | New long-horizon paired-seed artifact with pilot/main split if needed. | ✓ |
| Overload Phase 10 profile | Extend Phase 10 artifact semantics into dominance evidence. | |
| Only synthetic statistics | Build stats without SUMO run path. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Avoids reinterpreting Phase 10 capability evidence.

---

## Comparator Set

| Option | Description | Selected |
|--------|-------------|----------|
| Strong feasible pressure/storage baselines | Require max_pressure, capacity_aware_pressure, finite_storage_double_pressure; include others as context. | ✓ |
| All registered controllers | Require every controller including guarded infeasible paths. | |
| Weak operational baselines only | Compare mainly against fixed_time/actuated. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Prevents strawman dominance.

---

## Paired Statistics

| Option | Description | Selected |
|--------|-------------|----------|
| Paired bootstrap default | Use same seed pairs, report CI/effect size/sample size and multiple-comparison handling. | ✓ |
| Independent aggregate CI | Reuse Phase 10 mean CI by controller. | |
| Raw means only | Avoid uncertainty reporting. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Satisfies EXP-05 and journal-grade paired evidence.

---

## Gate C Fail-Closed Rule

| Option | Description | Selected |
|--------|-------------|----------|
| Machine-readable fail-closed checker | Missing rows/metadata/pairs/comparators/action audit fail or become inconclusive. | ✓ |
| Prose-only summary | Human-readable interpretation without executable gate checks. | |
| Best-effort skip missing data | Silently skip missing pairs or comparators. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Mirrors Phase 9 gate discipline.

---

## Claim Discipline

| Option | Description | Selected |
|--------|-------------|----------|
| Simulator/network/horizon/seed-relative binding evidence only | Allow bounded evidence language and preserve Phase 12/v2 boundaries. | ✓ |
| Broad superiority claim | Claim universal dominance over max-pressure. | |
| Manuscript-ready language | Begin final paper claims in Phase 11. | |

**User's choice:** Auto-selected recommended default.
**Notes:** Keeps Phase 11 inside milestone scope.

---

## Claude's Discretion

- Exact seed IDs, runner names, bootstrap iteration count, and pilot/main command details may be chosen during planning/execution if artifacts record them.
- Synthetic tests should validate Gate C and statistics before expensive SUMO runs.

## Deferred Ideas

- Tuned fixed-time baseline.
- Neural/RL benchmark expansion.
- Manuscript table/claim generation.
