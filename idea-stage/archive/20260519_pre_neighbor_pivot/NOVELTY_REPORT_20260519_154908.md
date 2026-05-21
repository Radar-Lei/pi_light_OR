# Novelty Check Report — OR-Certified Interpretable Priority Rules

**Date**: 2026-05-19
**Scope**: Phase 3 deep novelty check for the top idea and two components:
1. OR-certified interpretable priority rules for signalized networks.
2. AMPL/OR oracle → PI-Light DSL rule recovery with certificate.
3. Finite-storage effective pressure / spillback-aware interpretable priority rule.

## Read/Search Coverage

Sources used:
- WebSearch queries over 2024–2026 symbolic/interpretable TSC, max-pressure variants, finite storage/spillback, phase constraints, MPC stability, and oracle/distillation.
- WebFetch abstracts/pages for SymLight, SignalClaw, C-MP, and Capacity-aware Back-pressure.
- Local prior Phase 1 materials: PI-Light paper/code, PIRL paper, Obsidian landscape map.

Caveat: `verify_papers.py` was not resolved in the project, so papers discovered only by WebSearch are treated as web-located, not database-verified. Claims below avoid relying on fabricated IDs; unknown DOI/arXiv fields are omitted.

## Proposed Method

Define a broad class of **interpretable additive lane-link priority rules** for traffic-signal phase selection. Classic max-pressure is one special case; PI-Light-style DSL programs are compact searchable instances. The paper studies which rules admit throughput/stability or certification guarantees under finite storage, spillback, minimum green, yellow loss, phase order, and NEMA-like constraints, with AMPL/HiGHS for oracle/certification and SUMO for validation.

## Core Claims and Novelty

### Claim 1 — Unified priority-rule class connecting max-pressure and PI-Light DSL

**Novelty**: MEDIUM-HIGH

Closest work:
- PI-Light (AAAI 2024): DSL/MCTS searches lane-link priority programs, sums values by phase, selects max phase.
- SymLight (ICLR 2026 submission/arXiv 2025): symbolic priority functions for TSC via MCTS.
- SignalClaw (2026): LLM/evolutionary synthesis of interpretable signal-control skills.
- GPLight+, TPET, PI-eLight: symbolic/evolutionary/programmatic TSC policy search cluster.

Assessment:
- The additive priority-rule form itself is not novel; PI-Light and recent symbolic TSC work already occupy that space.
- The novel part is **not** “we define/search symbolic priority rules.”
- The potential novelty is the unification with max-pressure theory and OR certification: classic MP as a theorem-friendly special case, PI-Light DSL as deployable/searchable instances.

Verdict: Novel only if framed as **OR-certified priority-rule class**, not as new symbolic policy search.

### Claim 2 — Stability/throughput certification under finite storage and realistic phase constraints

**Novelty**: MEDIUM

Closest work:
- Varaiya (2013): foundational max-pressure stability.
- Capacity-aware back-pressure: finite-capacity normalized pressure.
- Pressure releasing policy under finite queue capacities.
- Max-pressure with cyclical phase structure.
- Cycle-based max-pressure and dynamic/switching-loss MP variants.
- MPC for urban traffic signals with stability guarantees, including finite storage and NEMA-like constraints.
- Enhanced queue-based Max-Pressure traffic signal control (TRC 2026): stability-preserving MP refinements with lane/shared-lane/saturation features.
- C-MP (TRB 2025): coordinated MP with maximum-stability proof.
- CV-MP and CMPP-style recent MP variants.

Assessment:
- Many pieces already exist: finite storage, switching loss, cycle constraints, capacity-aware pressure, coordinated MP, and MPC stability.
- The exact combination with **interpretable PI-Light-style DSL rules and a certification/recovery workflow** was not found.
- A strong theorem claiming broad novelty over finite storage + realistic constraints would be risky. Existing work may cover parts of the proof space.

Verdict: Proceed with caution. Use a precise, limited guarantee or certification procedure rather than overclaiming a new universal stability theorem.

### Claim 3 — AMPL/OR oracle to DSL rule recovery with mismatch/cost certificate

**Novelty**: HIGH-MEDIUM

Closest work:
- PIRL: neural oracle guides program search.
- VIPER / decision-tree extraction: policy extraction from RL/DNN oracle.
- PI-Light / PI-eLight / SymLight: direct symbolic policy search.
- MPC+RL traffic signal control papers: combine MPC and RL, but not necessarily DSL recovery.
- OracleTSC: oracle-informed reward/regularization for interpretable LLM-based TSC.
- XGBoost-to-decision-tree or decision-tree extraction TSC work.

Assessment:
- Distillation/extraction is not new.
- But I did not find direct prior work doing **OR/MPC/AMPL traffic-signal oracle → PI-Light-style DSL priority rule → formal action-disagreement or cost-loss certificate**.
- This may be the cleanest unique bridge between OR and PI-Light.

Verdict: Strong candidate as a secondary/empirical contribution or even a co-primary contribution if the recovery result is strong.

### Claim 4 — Finite-storage effective pressure / spillback-aware interpretable penalty

**Novelty**: LOW-MEDIUM as standalone; MEDIUM as component

Closest work:
- Capacity-aware back-pressure / normalized pressure.
- Backpressure considering downstream link capacity.
- Position-weighted backpressure.
- Travel-time / spatial-distribution max-pressure variants.
- Real-time decentralized TSC considering queue spillbacks.
- Enhanced queue-based Max-Pressure (TRC 2026).

Assessment:
- A downstream storage/slack penalty is very likely to be viewed as a known finite-capacity/backpressure idea.
- It is still valuable as an interpretable component inside the broader priority-rule class, especially if derived as a shadow-price or DSL-recoverable term.

Verdict: Do not make this the headline. Fold into the main rule class and emphasize certification/deployability.

## Closest Prior Work Table

| Paper / line | Year | Venue/source | Overlap | Key difference for our positioning |
|---|---:|---|---|---|
| Varaiya, Max pressure control of signalized intersections | 2013 | TRC | Foundational MP stability; phase argmax pressure | Not PI-Light/DSL/interpretable policy recovery; idealized assumptions. |
| Capacity-aware back-pressure traffic signal control | 2014/2015 | arXiv / IEEE TCNS | Finite-capacity normalized pressure, spillback mitigation | Not DSL/programmatic priority-rule certification; not PI-Light bridge. |
| Max-pressure with cyclical phase structure | 2020 | TRC | Realistic cycle/phase-order constraints with stability | Not finite-storage DSL rule recovery; focuses on MP variant. |
| Learning max pressure with phase switching loss | 2022 | TRC | Switching-loss-aware MP + learning | Not broad OR-certified interpretable DSL class. |
| MPC for Urban Traffic Signals with Stability Guarantees | 2023/2024 | OSTI/NSF PDF | Finite storage, NEMA constraints, stability | MPC controller, not compact PI-Light-style deployable priority rules. |
| C-MP coordinated max-pressure | 2025 | TRB / arXiv | Coordinated MP, platoon priority, maximum stability | Priority adjustment but not DSL/PI-Light/OR certificate recovery. |
| Enhanced queue-based Max-Pressure | 2026 | TRC | Lane-structured queue-based MP, stability-preserving refinements | High overlap on MP refinement; less on interpretable DSL/program recovery. |
| PI-Light | 2024 | AAAI | Lane-link DSL priority programs, MCTS search, deployment | No throughput/stability/finite-storage/phase-constraint OR guarantees. |
| SymLight | 2025/2026 | arXiv/OpenReview | Symbolic priority functions, deployable policies | No OR stability guarantee found; not finite-storage/phase-constraint certification. |
| SignalClaw | 2026 | arXiv | Interpretable synthesized skills | No OR certification/stability guarantee found. |
| VIPER / decision-tree extraction line | 2018+ | NeurIPS / follow-ups | Policy extraction from oracle | Neural/RL oracle, not AMPL/OR traffic-signal oracle with cost certificate. |

## Overall Novelty Assessment

**Score**: 7/10 if positioned correctly; 4/10 if positioned as “a new max-pressure variant”; 3/10 if positioned as “a new symbolic policy search method.”

**Recommendation**: PROCEED WITH CAUTION.

**Key differentiator**:
The strongest unique delta is the three-way bridge:

> max-pressure / OR stability theory + PI-Light-style interpretable priority DSL + AMPL/SUMO certification/recovery under realistic constraints.

No single located paper appears to combine all three. But many papers cover individual components, so the paper must avoid overclaiming and make the integration mathematically precise.

## Reviewer Risk

A TS/TRC reviewer could say:

1. “Finite-storage/backpressure variants already exist.”
2. “Cycle/phase constraints in MP already exist.”
3. “Symbolic priority functions for TSC already exist.”
4. “MPC with stability guarantees under NEMA constraints already exists.”

The defense must be:

- We are not merely proposing another MP formula.
- We are not merely searching symbolic rules.
- We provide a certification/recovery framework explaining when compact deployable rules inherit OR guarantees or approximate an OR oracle.
- We empirically test the exact deployment gap: finite storage + realistic phases + SUMO + compact interpretable rules.

## Suggested Positioning

Best title direction:

**OR-Certified Interpretable Priority Rules for Signalized Networks**

Avoid putting “Max-Pressure” in the main method name unless the rule is literally a max-pressure variant. Use max-pressure as:
- a special case,
- a theoretical anchor,
- a baseline,
- and a certificate source.

Better contribution framing:

1. **Unified rule class**: additive lane-link priority rules covering classic MP and PI-Light-style DSL programs.
2. **Certification problem**: given realistic storage/phase constraints, certify whether a rule is feasible/stabilizing over a demand region or quantify its gap to an OR oracle.
3. **Recovery problem**: solve constrained OR/MPC oracle states with AMPL, then recover the simplest DSL rule and report exact disagreement/cost certificates.
4. **SUMO validation**: show the certified/recovered rules are deployable and competitive under spillback and phase constraints.

## Recommended Phase 4 Review Prompt

Ask an external reviewer to judge this sharpened claim:

> We do not propose a new symbolic search algorithm. We propose an OR certification and recovery framework for interpretable additive priority rules. Classic max-pressure is a theorem-friendly member of the class; PI-Light DSL rules are deployable members. We certify or recover compact rules under finite storage and realistic phase constraints, then validate in SUMO.

This version has the best chance of surviving the “already done” objection.

## Sources to cite/check next

- Varaiya 2013 Max pressure: https://www.sciencedirect.com/science/article/pii/S0968090X13001782
- Capacity-aware back-pressure: https://arxiv.org/abs/1309.6484
- Max-pressure cyclical phase structure: https://www.sciencedirect.com/science/article/pii/S0968090X20307324
- MPC for Urban Traffic Signals with Stability Guarantees: https://www.osti.gov/servlets/purl/1995694
- Enhanced queue-based Max-Pressure: https://www.sciencedirect.com/science/article/pii/S0968090X26000264
- C-MP: https://arxiv.org/abs/2407.01421
- PI-Light: https://ojs.aaai.org/index.php/AAAI/article/view/30103
- SymLight: https://arxiv.org/abs/2511.05790
- SignalClaw: https://arxiv.org/abs/2604.05535
- Max-pressure with phase switching loss: https://www.sciencedirect.com/science/article/pii/S0968090X22001139
