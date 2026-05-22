# Requirements: PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

**Defined:** 2026-05-22
**Core Value:** Show that network-optimization dual sensitivities provide a generalized max-pressure principle that reduces to pressure when constraints are slack and adds scarcity-aware corrections when storage, supply, or corridor bottleneck constraints bind, and that this principle can be compressed into compact symbolic traffic-signal policies.

## v1 Requirements

Requirements for the TR-B / Transportation Science paper-building milestone. Each maps to roadmap phases.

### Theory

- [ ] **THRY-01**: The paper defines a continuous capacitated traffic-network relaxation with queue conservation, movement service, phase compatibility, and storage/supply/capacity constraints.
- [ ] **THRY-02**: The paper derives a movement-level dual-sensitivity decomposition with interpretable upstream, downstream, storage/supply, and corridor/service terms.
- [x] **THRY-03**: The paper proves max-pressure/backpressure is a special case when storage/supply/corridor constraints are nonbinding or ranking-neutral.
- [x] **THRY-04**: The paper proves or formalizes a spillback/scarcity correction term showing how dual sensitivity can differ from ordinary pressure in binding regimes.
- [ ] **THRY-05**: The paper states a recovery-regret or optimization-quality result for finite dictionary symbolic policy recovery.

### Recovery Algorithm

- [ ] **RECV-01**: The code implements K-atom sparse symbolic recovery beyond one-atom pilots.
- [ ] **RECV-02**: The recovery objective optimizes oracle regret or value gap, not imitation accuracy alone.
- [ ] **RECV-03**: The recovery formulation includes explicit penalties or constraints for program size, neighbor atom count, and dual-price atom count.
- [ ] **RECV-04**: The atom library includes local queue/pressure, downstream capacity/slack, raw neighbor queue, pressure/backpressure, dual sensitivity/price imbalance, and random/permuted dual placebo families.
- [ ] **RECV-05**: Recovery outputs include auditable program text/rules, selected atoms, solve time, oracle regret, action agreement, program length, neighbor count, and dual atom count.

### Static Kill-Gate Evidence

- [ ] **KILL-01**: Static benchmarks include slack, downstream storage-binding, supply-binding, corridor-bottleneck, incident/capacity-drop, and demand-shift regimes.
- [ ] **KILL-02**: Each static regime reports dual-vs-pressure disagreement rate, dual win rate, mean oracle regret, worst-case regret, and recovered symbolic rules.
- [ ] **KILL-03**: The static benchmark contains enough sampled states per regime to support stable conclusions, with a target of at least 1k states for the main pressure-failure analysis.
- [ ] **KILL-04**: The analysis explicitly identifies whether dual sensitivity only recovers pressure, improves over pressure in binding regimes, or fails to match pressure.
- [ ] **KILL-05**: Claim routing is documented: strong dual advantage supports TR-B/TS mainline; pressure tie routes to generalized pressure / symbolic recovery framing; dual underperformance routes to diagnostic framing.

### Closed-Loop Evaluation

- [ ] **CLOP-01**: Closed-loop SUMO experiments include single-intersection sanity, 5-intersection arterial main case, grid scalability, and robustness/demand-shift scenarios.
- [ ] **CLOP-02**: Closed-loop baselines include fixed-time, actuated/local pressure, max-pressure/backpressure, capacity- or spillback-aware pressure, local PI-Light, raw-neighbor symbolic, all-neighbor symbolic, random/permuted dual, and full dual-symbolic policy where feasible.
- [ ] **CLOP-03**: Main closed-loop comparisons run enough seeds for confidence intervals, with a target of 5–10 seeds for arterial and grid experiments.
- [ ] **CLOP-04**: Closed-loop outputs report average travel time, total delay, throughput/completed vehicles, mean and max queues, spillback/blocking counts, switching counts, and controller runtime.
- [ ] **CLOP-05**: Experiments include at least one scenario designed so ordinary pressure can fail due to storage, supply, spillback, or corridor bottleneck effects.

### Reproducibility and Repository

- [ ] **REPR-01**: The root README states the research question, contribution claim, current status, reproduction commands for key blocks, known limitations, and next experiments.
- [ ] **REPR-02**: The project includes an environment specification for the CPU/SUMO/optimization workflow.
- [ ] **REPR-03**: Experiment scripts are organized or named by block so Block 0, static recovery, closed-loop, and table generation can be run reproducibly.
- [ ] **REPR-04**: All experiments write structured JSON/CSV artifacts sufficient to regenerate reported tables and figures.
- [ ] **REPR-05**: Paper tables and figures are generated from raw artifacts by scripts rather than manual transcription.

### Manuscript

- [ ] **PAPR-01**: The manuscript introduction frames the contribution as OR/control methodology for capacitated traffic signal networks, not PI-Light enhancement.
- [ ] **PAPR-02**: The related-work section positions max-pressure/backpressure, adaptive signal control, interpretable/programmatic policies, and OR dual sensitivity without overclaiming novelty.
- [ ] **PAPR-03**: The method section presents the continuous relaxation, dual-sensitivity extraction, symbolic recovery formulation, and algorithmic pipeline.
- [ ] **PAPR-04**: The experiment section separates sanity, static kill-gate, closed-loop main results, robustness, runtime, and ablations.
- [ ] **PAPR-05**: The limitations/threats section honestly addresses cases where dual ties pressure, simulator realism, oracle approximation, recovery scalability, and logistics/TR-E non-fit.

## v2 Requirements

Deferred unless v1 evidence supports expansion.

### Extensions

- **EXT-01**: Add freight/logistics objective and metrics for a possible Transportation Research Part E pivot.
- **EXT-02**: Add larger real-world network case studies beyond the initial Chengdu-style assets.
- **EXT-03**: Add neural MARL baselines as secondary comparisons if CPU-feasible or if published checkpoints are available.
- **EXT-04**: Add robust optimization, ADMM, column generation, or bilevel formulations only after the main dual-symbolic recovery claim is validated.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Universal claim that dual beats pressure in all regimes | Current and expected theory says pressure is a special case under slack constraints |
| PI-Light enhancement as paper identity | Too weak for TR-B / Transportation Science and invites AI-paper criticism |
| Static one-step ranking as final empirical evidence | Closed-loop traffic control evidence is required |
| Freight/logistics TR-E framing | Current problem is traffic-network control unless explicitly pivoted to freight corridors |
| GPU-heavy MARL training as required evidence | Project should remain CPU/SUMO/optimization oriented |
| Multiple optimization side frameworks in the main method | ADMM/robust/column-generation/bilevel side lines dilute the clean main contribution |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| THRY-01 | Phase 1 | Pending |
| THRY-02 | Phase 1 | Pending |
| THRY-03 | Phase 1 | Complete |
| THRY-04 | Phase 1 | Complete |
| THRY-05 | Phase 1 | Pending |
| RECV-01 | Phase 2 | Pending |
| RECV-02 | Phase 2 | Pending |
| RECV-03 | Phase 2 | Pending |
| RECV-04 | Phase 2 | Pending |
| RECV-05 | Phase 2 | Pending |
| KILL-01 | Phase 3 | Pending |
| KILL-02 | Phase 3 | Pending |
| KILL-03 | Phase 3 | Pending |
| KILL-04 | Phase 3 | Pending |
| KILL-05 | Phase 3 | Pending |
| CLOP-01 | Phase 4 | Pending |
| CLOP-02 | Phase 4 | Pending |
| CLOP-03 | Phase 4 | Pending |
| CLOP-04 | Phase 4 | Pending |
| CLOP-05 | Phase 4 | Pending |
| REPR-01 | Phase 5 | Pending |
| REPR-02 | Phase 5 | Pending |
| REPR-03 | Phase 5 | Pending |
| REPR-04 | Phase 5 | Pending |
| REPR-05 | Phase 5 | Pending |
| PAPR-01 | Phase 6 | Pending |
| PAPR-02 | Phase 6 | Pending |
| PAPR-03 | Phase 6 | Pending |
| PAPR-04 | Phase 6 | Pending |
| PAPR-05 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-22*
*Last updated: 2026-05-22 after initial definition*
