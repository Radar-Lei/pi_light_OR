# Phase 3 Novelty Check — Dual-Price DSL Synthesis for Coordinated π-Light

**Date**: 2026-05-20
**Candidate method**: Dual-Price DSL Synthesis for Coordinated π-Light
**Scope**: 2020–2026 literature around symbolic/interpretable traffic signal control, neighbor-aware MARL, max-pressure/OR traffic control, Lagrangian/safe RL, store-and-forward or oracle-guided TSC, and optimization/program synthesis.

## Execution Notes

- `verify_papers.py` was not available in the exposed tool/runtime search path, so closest-prior-work entries below are marked `[UNVERIFIED]` per the novelty-check fallback policy.
- Codex MCP / external `gpt-5.5` reviewer tools were not exposed in the current tool list, so Phase C cross-model verification could not be executed. The assessment below is based on direct web searches and fetched abstracts/pages.
- No single paper was found that directly combines: **PI-Light-style symbolic DSL + OR dual/shadow-price neighbor features + optimization-based DSL synthesis/recovery + multi-intersection traffic signal coordination**.

## Proposed Method

Use OR dual variables / shadow prices from a store-and-forward or CTM-lite network relaxation as interpretable neighbor-aware features inside PI-Light-style symbolic priority programs, and replace PI-Light's original MCTS search with optimization-based DSL synthesis or recovery, e.g., MILP/CP-SAT, column generation, sparse mixed-integer feature selection, or oracle-to-rule fitting.

## Core Claims

1. **Optimization-based synthesis/recovery of PI-Light-style DSL rules for TSC**  
   Novelty: **MEDIUM-HIGH**  
   Closest: π-Light, π-eLight, SymLight, GP-based TSC, EvolveSignal, SignalClaw.  
   Assessment: Symbolic / programmatic TSC is no longer novel, but the search mechanisms found are MCTS, GP, LLM/evolutionary search, or neural/interpretable MARL. I did not find MILP/CP-SAT/column-generation synthesis over a PI-Light-style traffic DSL.

2. **Dual-price / shadow-price neighbor features for interpretable traffic-signal DSL policies**  
   Novelty: **HIGH**  
   Closest: max-pressure/backpressure variants, C-MP, capacity-aware pressure, older dual-variable traffic-capacity work, Lagrangian/safe RL.  
   Assessment: Dual/shadow-price interpretations exist in traffic optimization and Lagrangian RL, and pressure-based methods can be interpreted as marginal congestion logic. However, I did not find work using optimization dual prices as explicit symbolic DSL atoms/features in a PI-Light-like programmatic controller.

3. **Lagrangian-decomposed programmatic / symbolic control for multi-intersection TSC**  
   Novelty: **MEDIUM-HIGH**  
   Closest: constrained/safe RL with Lagrange multipliers, distributed optimization/ADMM traffic control, Lagrangian shaping in RL, coordinated MP/C-MP.  
   Assessment: Lagrangian methods are present in constrained RL and traffic optimization, but not in a programmatic traffic-signal DSL controller. This is a promising theoretical framing, but reviewers may see it as a recombination unless the decomposition-to-symbolic-policy link is made technically precise.

4. **Store-and-forward / CTM-lite OR oracle distillation into neighbor-aware symbolic traffic rules**  
   Novelty: **MEDIUM-HIGH**  
   Closest: OracleTSC, store-and-forward optimization toolboxes/models, distillation/compression in DRL-TSC, symbolic TSC methods.  
   Assessment: Oracle-informed TSC, store-and-forward optimization, and symbolic/distilled controllers exist separately. I did not find a direct store-and-forward OR oracle → PI-Light neighbor-aware DSL recovery pipeline.

## Closest Prior Work

| Paper | Year | Venue / Source | Overlap | Key Difference |
|---|---:|---|---|---|
| [UNVERIFIED] π-Light: Programmatic Interpretable Reinforcement Learning for Resource-Limited Traffic Signal Control | 2024 | AAAI | PI-Light DSL + MCTS for interpretable TSC | Local/programmatic policy; no OR dual prices, Lagrangian decomposition, MILP/CP-SAT synthesis, or neighbor-aware coordination found |
| [UNVERIFIED] π-eLight: Learning Interpretable Programmatic Policies for Effective Traffic Signal Control | 2026 | IEEE TMC | Direct continuation of PI-Light-style programmatic TSC | Search/details need full paper check; web metadata does not indicate OR dual-price or optimization-synthesis contribution |
| [UNVERIFIED] SymLight: Exploring Interpretable and Deployable Symbolic Policies for Traffic Signal Control | 2025/2026 | arXiv / OpenReview | Symbolic priority functions for TSC; MCTS-based discovery | Does not use OR dual prices, Lagrangian decomposition, OR oracle distillation, or MILP/CP-SAT DSL synthesis based on fetched abstract/page |
| [UNVERIFIED] Learning Traffic Signal Control via Genetic Programming | 2024 | GECCO / arXiv | Explainable tree-form phase-urgency functions via GP | GP search, not OR-price-guided DSL synthesis; no dual/shadow-price features found |
| [UNVERIFIED] Towards explainable traffic signal control for urban networks through genetic programming | 2024 | Swarm and Evolutionary Computation | Interpretable symbolic score rules | Genetic programming/symbolic regression; no dual-price/Lagrangian or PI-Light DSL synthesis evidence in accessible metadata |
| [UNVERIFIED] EvolveSignal | 2025 | arXiv | LLM-powered program synthesis for TSC strategies | Evolves Python heuristics; no OR dual prices or formal DSL optimization synthesis found |
| [UNVERIFIED] SignalClaw | 2026 | arXiv | LLM-guided evolutionary synthesis of interpretable TSC skills | LLM/evolutionary skill synthesis; no OR shadow-price or Lagrangian DSL features found |
| [UNVERIFIED] CoordLight | 2025/2026 | T-ITS / arXiv | Neighbor-aware multi-intersection coordination with attention | Neural MARL, not symbolic/DSL; no OR-price semantics |
| [UNVERIFIED] C-MP: Coordinated Max Pressure | 2024/2025 | arXiv / TRB-related | Decentralized coordinated max-pressure, platoon priority, stability | Strong max-pressure competitor; not PI-Light-style symbolic program synthesis and no oracle-to-rule DSL recovery |
| [UNVERIFIED] Distributed Traffic Signal Control via Coordinated Maximum Pressure-plus-Penalty | 2024/2025 | ITSC / ETH record | Distributed MP-plus-penalty / capacity-aware coordination | Optimization/MP family rather than interpretable DSL synthesis |
| [UNVERIFIED] Constrained traffic signal control under competing public transport priority requests via safe reinforcement learning | 2025 | Expert Systems with Applications | Lagrangian multipliers in constrained/safe RL for TSC | Deep RL constraint handling; not symbolic/programmatic, not PI-Light DSL |
| [UNVERIFIED] OracleTSC | 2026 | TMLR / OpenReview | Oracle-informed reward shaping for TSC | Oracle used for reward hurdle/regularization, not store-and-forward OR oracle distilled into symbolic rules |
| [UNVERIFIED] Store-and-forward with graph attention for emergency-responsive TSC | 2025 | Engineering Applications of AI | Store-and-forward + MARL/graph attention | Neighbor-aware neural method; not DSL symbolic recovery |

## Overall Novelty Assessment

- **Score**: **7.5 / 10**
- **Recommendation**: **PROCEED WITH CAUTION**
- **Key differentiator**: The full combination appears distinctive: optimization-derived marginal congestion prices become **interpretable neighbor features** inside a **PI-Light-style symbolic DSL**, while an **optimization-based recovery/synthesis procedure** replaces MCTS.
- **Main novelty risk**: Reviewers can decompose the contribution into known ingredients: symbolic TSC already exists; neighbor-aware MARL already exists; Lagrangian/safe RL already exists; max-pressure already has marginal-congestion intuition; store-and-forward/MPC signal control already exists. The paper must prove that the combination is not just feature engineering.
- **Most dangerous prior-work cluster**: SymLight / π-eLight / GP symbolic TSC for the symbolic-policy claim, and C-MP / coordinated max-pressure / capacity-aware backpressure for the traffic-theory claim.

## Suggested Positioning

1. **Do not claim novelty as “symbolic traffic signal control.”** That space is already occupied by π-Light, π-eLight, SymLight, GP-based TSC, EvolveSignal, and SignalClaw.
2. **Do not claim novelty as “neighbor-aware coordination.”** CoordLight and GAT/MARL approaches already cover that.
3. **Do not claim novelty as “uses Lagrange multipliers in RL.”** Safe/constrained RL papers already do that.
4. **Claim the specific bridge**: OR dual prices / Lagrangian coordination signals are transformed into compact, interpretable, neighbor-aware DSL atoms for PI-Light-style control.
5. **Make MCTS replacement concrete**: Prefer a small, demonstrable MILP/sparse feature-selection recovery problem over a vague “optimization-based synthesis” claim.
6. **Use OR oracle recovery as the empirical defense**: show that dual-price atoms recover oracle actions better than raw-neighbor, random-price, all-neighbor, and local-only symbolic baselines.
7. **Frame max-pressure/C-MP as theory/baseline, not enemy**: the method generalizes pressure intuition into a learned symbolic rule class with OR-derived marginal-value features.

## Survival Verdict

The idea **survives Phase 3 novelty check**, but only under a narrowed claim:

> Novel contribution = **dual/shadow-price-conditioned symbolic DSL recovery for neighbor-aware PI-Light coordination**, not generic symbolic TSC, not generic OR traffic control, and not generic neighbor-aware MARL.

Recommended next step: proceed to **Phase 4 external critical review**, with the reviewer prompt explicitly including the closest symbolic-TSC and max-pressure/C-MP works above.

## Search Sources Consulted

- π-Light AAAI page: https://ojs.aaai.org/index.php/AAAI/article/view/30103
- SymLight arXiv: https://arxiv.org/abs/2511.05790
- SymLight OpenReview: https://openreview.net/forum?id=8soGuDwlxK
- SignalClaw arXiv: https://arxiv.org/abs/2604.05535
- EvolveSignal arXiv: https://arxiv.org/abs/2509.03335
- CoordLight arXiv: https://arxiv.org/abs/2603.24366
- CoordLight GitHub: https://github.com/marmotlab/CoordLight
- C-MP arXiv: https://arxiv.org/abs/2407.01421
- OracleTSC OpenReview: https://openreview.net/forum?id=WmJu5MkoQD
- Learning TSC via GP: https://arxiv.org/abs/2403.17328
- XLight ScienceDirect record: https://www.sciencedirect.com/science/article/pii/S0957417425005603
- GP explainable TSC ScienceDirect record: https://www.sciencedirect.com/science/article/pii/S2210650224001263
- ETH C-MP-plus-penalty record: https://www.research-collection.ethz.ch/entities/publication/d655c5db-5b3b-4973-8917-e01ef75b417c
- Safe RL Lagrangian TSC record: https://fis.tu-dresden.de/portal/en/publications/constrained-traffic-signal-control-under-competing-public-transport-priority-requests-via-safe-reinforcement-learning%2864e3242b-a7da-4820-be3b-4991c9c33a48%29.html
