# Requirements: PI-Light OR / Dual-Sensitivity Symbolic Traffic Control

**Defined:** 2026-05-23
**Milestone:** v1.1 Explicit Finite-Storage Primal-Dual Separation
**Core Value:** Show that finite-storage primal-dual pressure control strictly generalizes max-pressure: it reduces to pressure when constraints are slack, adds scarcity-aware shadow-price corrections when storage, spillback, switching, service, or incident constraints bind, and can be deployed or compressed into auditable symbolic traffic-signal policies.

## v1.1 Requirements

Requirements for the finite-storage separation milestone. Each maps to roadmap phases.

### Claim Discipline

- [x] **CLAIM-01**: The project states the permitted strong claim as bounded: the method recovers or ties max-pressure when constraints are slack and only claims improvement when finite-storage, spillback, switching, service, or incident constraints bind.
- [x] **CLAIM-02**: The repository prevents v1.0 pressure-equivalent static or closed-loop evidence from being described as dual superiority.
- [ ] **CLAIM-03**: Generated reports and future manuscript inputs distinguish simulator-, network-, horizon-, and seed-relative evidence from deployment or universal-dominance claims.

### Explicit State and Objective

- [x] **STATE-01**: Experiment state replaces proxy-only binding labels with explicit downstream storage, residual receiving capacity, spillback/blocking, phase-switching loss, service urgency, and incident/capacity-drop fields.
- [x] **STATE-02**: The finite-storage constrained objective predeclares delay, unfinished-vehicle penalty, spillback/blocking time, and switching lost-time terms.
- [x] **STATE-03**: Static fixtures and closed-loop runners emit schema-validated artifacts containing the explicit state fields and objective components needed for audit.

### Theory and Separation

- [ ] **THRY-01**: The theoretical model proves a special-case theorem showing reduction to classical max-pressure/backpressure under infinite storage, no switching loss, fixed turning ratios, and slack operational constraints.
- [ ] **THRY-02**: The theory package proves or constructs a separation theorem/counterexample where finite storage, spillback, incident capacity drop, or switching loss causes the primal-dual controller and classical pressure to choose different phases.
- [ ] **THRY-03**: The separation result shows strict improvement in a one-step constrained objective, spillback penalty, Lyapunov drift, or equivalent auditable criterion relative to classical pressure.
- [ ] **THRY-04**: The milestone includes one additional guarantee candidate: throughput/bounded-drift under a finite-storage model, regret to a constrained LP oracle, or symbolic-compression error bound.

### Controller Integration

- [ ] **CTRL-01**: A live finite-storage primal-dual pressure controller computes movement/phase scores using queue pressure plus downstream storage, spillback, switching, service, and incident shadow-price corrections.
- [ ] **CTRL-02**: `full_dual_symbolic` or its finite-storage successor is safely wired into closed-loop SUMO without relabeling unsafe queue heuristics as the proposed method.
- [ ] **CTRL-03**: The controller reduces to the existing pressure-equivalent behavior in slack regimes according to deterministic unit or fixture tests.
- [ ] **CTRL-04**: Controller outputs include auditable score decompositions showing which shadow-price terms changed the action in binding regimes.

### Kill Gates

- [ ] **GATE-01**: Gate A verifies slack-regime special-case recovery, requiring high action agreement with max-pressure/backpressure and reporting ties as expected behavior.
- [ ] **GATE-02**: Gate B verifies binding-regime separation, requiring primal-dual actions to differ from pressure and improve the constrained oracle or one-step objective on explicit storage/spillback/switching/incident states.
- [ ] **GATE-03**: Gate C verifies closed-loop dominance only in predeclared binding stress regimes using paired-seed confidence intervals against the strongest feasible baselines.
- [ ] **GATE-04**: Gate outputs fail closed when explicit state fields, action decompositions, paired seeds, or baseline comparators are missing.

### Baselines and Experiments

- [ ] **EXP-01**: The experiment suite includes optimized fixed-time, actuated or semi-actuated control, classical max-pressure, capacity-aware pressure, and feasible cycle-based or finite-storage/double-pressure variants.
- [ ] **EXP-02**: The suite explains and tests the current grid fixed-time counterexample before using any broad performance language.
- [ ] **EXP-03**: Long-horizon closed-loop experiments use 3600–7200s horizons, appropriate warmup, demand multiplier sweeps, and paired seeds where computationally feasible.
- [ ] **EXP-04**: Stress scenarios include downstream blockage, spillback, incident/lane capacity drop, oversaturation, turning shock, and switching-loss-sensitive regimes.
- [ ] **EXP-05**: Statistical reports include paired bootstrap or paired t/Wilcoxon confidence intervals, effect sizes, and multiple-comparison handling where relevant.

### Reproducibility and Future Manuscript Inputs

- [ ] **REPRO-01**: All new result tables, figure-data files, and claim-audit summaries are generated from raw JSON/CSV artifacts rather than manual transcription.
- [ ] **REPRO-02**: Reproduction scripts can rerun the new finite-storage separation gates and long-horizon experiment summaries on CPU/SUMO without GPU dependencies.
- [ ] **REPRO-03**: Future manuscript-input claim templates and limitations reflect the bounded claim: strict generalization and binding-regime superiority, not universal dominance.

## v2 Requirements

Deferred to future milestones. Tracked but not in current roadmap.

### Manuscript Finalization

- **MS-01**: Draft the full TR-B / Transportation Science manuscript after v1.1 determines which strong claims survive.
- **MS-02**: Convert final finite-storage separation artifacts into polished paper figures, tables, captions, and theorem statements.
- **MS-03**: Run external review / kill-argument on the full manuscript before submission.

### Large Benchmark Expansion

- **BENCH-01**: Add RESCO, CityFlow, LibSignal, or a larger real-world benchmark if the v1.1 core result survives on the local SUMO suite.
- **BENCH-02**: Add PI-Light / PressLight / MPLight-style neural baselines as appendix evidence if they can be run honestly without shifting the paper into benchmark chasing.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Claiming universal superiority over max-pressure | v1.0 evidence is pressure-equivalent and the v1.1 claim is bounded to binding constraints. |
| Reusing proxy-only `supply_binding_proxy`, `corridor_bottleneck_proxy`, or `demand_shift_proxy` as final evidence | The strong claim requires explicit state fields and auditable objective terms. |
| Relabeling unsafe `full_dual_symbolic` or `local_pilight` heuristics as implemented baselines | v1.0 deliberately marked them not feasible; v1.1 must either wire them safely or keep them excluded. |
| Making RL benchmark performance the main contribution | TS/TR-B fit depends on mathematical structure, separation, and OR/control insight. |
| GPU-heavy MARL training as a milestone dependency | The project should remain CPU/SUMO/optimization oriented. |
| Starting final manuscript claims before the separation gates pass | Manuscript language must follow evidence, not precede it. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLAIM-01 | Phase 6 | Complete |
| CLAIM-02 | Phase 6 | Complete |
| CLAIM-03 | Phase 12 | Pending |
| STATE-01 | Phase 6 | Complete |
| STATE-02 | Phase 6 | Complete |
| STATE-03 | Phase 6 | Complete |
| THRY-01 | Phase 7 | Pending |
| THRY-02 | Phase 7 | Pending |
| THRY-03 | Phase 7 | Pending |
| THRY-04 | Phase 7 | Pending |
| CTRL-01 | Phase 8 | Pending |
| CTRL-02 | Phase 8 | Pending |
| CTRL-03 | Phase 8 | Pending |
| CTRL-04 | Phase 8 | Pending |
| GATE-01 | Phase 9 | Pending |
| GATE-02 | Phase 9 | Pending |
| GATE-03 | Phase 11 | Pending |
| GATE-04 | Phase 9 | Pending |
| EXP-01 | Phase 10 | Pending |
| EXP-02 | Phase 10 | Pending |
| EXP-03 | Phase 11 | Pending |
| EXP-04 | Phase 10 | Pending |
| EXP-05 | Phase 11 | Pending |
| REPRO-01 | Phase 12 | Pending |
| REPRO-02 | Phase 12 | Pending |
| REPRO-03 | Phase 12 | Pending |

**Coverage:**
- v1.1 requirements: 26 total
- Mapped to phases: 26
- Unmapped: 0
- Duplicate phase assignments: 0

---
*Requirements defined: 2026-05-23*
*Last updated: 2026-05-23 after v1.1 roadmap creation and traceability mapping*
