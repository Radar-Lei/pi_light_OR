# Phase 1 Literature Landscape — PI-Light OR / Transportation Science Direction

Date: 2026-05-19
Topic: Build a Transportation Science article from PI-Light/PIRL foundations by combining OR with coordinated traffic signal control, evaluated in SUMO with AMPL/HiGHS available.

## Sources and read coverage

Sources that contributed:
- Local PI-Light paper markdown: `pi_light_original_paper/30103-Article_Text-34157-1-2-20240324_3_.md` — read relevant title/abstract/method/experiments/reference sections in full excerpt.
- Local PIRL LaTeX: `Programmatically_Interpretable_Reinforcement_Learning_original_paper/abs.tex`, `sec_intro.tex` — read abstract and introduction excerpt.
- Local PI-Light code: `agent/pi_light/program.py`, `agent/pi_light/pi_light.py`, `agent/pi_light/MCTS.py`, `agent/rule_based/max_pressure.py` — read core DSL/search/action-selection implementations.
- Obsidian: `Research/TSC_OR_RL/Literature_Landscape_Map.md` — read full returned content.
- Obsidian search results: SUMO TraCI traffic light docs, AMPL license note, max-pressure/C-MP/multi-commodity/network-level/adaptive partition papers. Some individual notes were too large for direct full ingestion; they are treated as located references, not fully read summaries.
- WebSearch: recent 2024–2026 max-pressure, interpretable TSC, constrained phase, SUMO controller, and coordination work.

Verification caveat: `arxiv_fetch.py` and `verify_papers.py` were not resolved in this project, so external WebSearch-discovered papers are marked as web-located rather than database-verified. Local/Obsidian papers are marked as local/knowledge-base located.

## What PI-Light actually provides

PI-Light (Gu et al., AAAI 2024) is a programmatic interpretable RL method for TSC. It searches a compact DSL over lane-link priority programs using MCTS and Bayesian optimization, then applies one learned program across intersections. Its policy computes a lane-link score `v`, aggregates scores by phase, and selects the phase with maximum score. It emphasizes interpretability, resource-limited deployment, and transfer across cities.

Code-level facts:
- The DSL has scalar features such as incoming vehicle count, incoming waiting vehicle count, outgoing vehicle count, and vector distance-count features.
- In-lane instructions add to priority; out-lane instructions subtract from priority.
- Program complexity is constrained by block breadth/depth and number of if conditions.
- The baseline max-pressure implementation only computes incoming queue minus outgoing queue per phase and enforces a fixed minimum green time.
- There is no explicit finite-storage, spillback, NEMA/ring-barrier, pedestrian, or network coordination constraint model in the base code.

Implication: PI-Light is best viewed not as an OR paper yet, but as a high-performing program-search engine over interpretable priority rules. The OR paper should add a traffic-control-theoretic/optimization layer that explains, certifies, or designs these rules under realistic constraints.

## Landscape themes

### 1. Max-pressure and throughput-stability theory

Core line:
- Varaiya (2013), *Transportation Research Part C*: max-pressure controller for networks of signalized intersections; foundational throughput/stability result.
- Capacity-aware/back-pressure variants address finite storage and spillback sensitivity.
- Cycle-based or cyclical phase-structure max-pressure papers address phase-order and switching constraints.
- 2026 TRC result: Enhanced queue-based Max-Pressure traffic signal control, reportedly extends queue-based MP with stability/throughput improvements around shared lanes and saturation flows.

Relevance to this project: This is the most Transportation Science-compatible theoretical backbone. It gives a way to turn PI-Light’s empirical priority programs into certified variants of constrained max-pressure.

Open gap: Existing MP theory often assumes idealized phase availability or abstracts away deployment constraints. Recent constrained/cycle variants handle parts of this, but not compact interpretable DSL recovery from an oracle/rule under SUMO-scale validation.

### 2. Interpretable / programmatic TSC is becoming crowded

Known cluster:
- PI-Light (AAAI 2024): MCTS over DSL priority programs.
- PI-eLight (IEEE TMC 2026): interpretable programmatic policies for effective TSC.
- SymLight (ICLR 2026 submission): symbolic/deployable policies.
- TPET / evolutionary discovery of heuristic policies.
- EvolveSignal: LLM coding agent for discovering TSC strategies.
- GPLight+: genetic programming for symmetric TSC policies.
- SignalClaw (2026): LLM-guided interpretable skill synthesis.

Relevance: A paper framed merely as “search better interpretable rules” is no longer enough. The novelty must shift from another program synthesis method to OR-certifiable control: throughput, finite storage, phase constraints, robust deployment, or optimization-backed certification.

Open gap: The recent interpretable TSC cluster optimizes/searches symbolic policies but generally lacks Transportation Science-style guarantees and realistic constraint certification.

### 3. Coordinated/network-wide signal control with OR models

Relevant lines:
- Multi-Commodity Traffic Signal Control and Routing with Connected Vehicles (De Souza et al., 2022): store-and-forward multi-commodity formulation, rolling-horizon convex optimization, joint routing/signal timing.
- Network-wide bilinear/adaptive optimization papers (2022–2023) and higher-order conflict graph approaches.
- Adaptive network partition / coordination papers (Ma and Wu, IEEE T-ITS 2024).
- C-MP (Transportation Research Part B / arXiv 2024): decentralized adaptive-coordinated signal control using max-pressure framework.

Relevance: Coordination is a strong OR angle, but full joint routing+signal optimization may drift away from PI-Light. The sharper bridge is “network-coupled priority rules”: local interpretable rules whose weights/constraints are derived from network-level OR certificates.

Open gap: Existing network-wide OR models are often rolling-horizon optimizers, not deployable simple rules. Existing PI-Light-style rules are deployable, but not network-optimization certified.

### 4. OR+RL hybrid ideas already mapped in prior notes

The Obsidian landscape map ranks several OR+RL directions:
- MP-based reward shaping: dual/shadow-price potentials for RL.
- ADMM + MARL: consensus/distributed coordination.
- Lagrangian decomposition + RL: decompose network-level constraints into local agents.
- CTM/network-flow + RL hybrid.
- Decision-focused learning for TSC.
- Column generation + RL.
- MIP relaxation + RL.

For this PI-Light-to-TS project, the best subset is not “general RL + OR”. It is: use OR as a certificate/explanation/design tool for compact priority rules, with SUMO as the final testbed.

### 5. SUMO/AMPL feasibility

Obsidian confirms relevant SUMO docs exist for TraCI traffic light control, traffic light retrieval, NEMA phase constraints, and simulation traffic lights. AMPL/HiGHS is available by project memory and Obsidian license note.

Practical implication: SUMO can support realistic phase timing, storage/spillback, and network simulation; AMPL can solve finite-horizon LP/MILP/dual/certification models offline or periodically.

## Candidate research gaps for Phase 2 idea generation

### Gap A — OR-certified interpretable priority rules

Problem: PI-Light discovers compact priority rules, but their performance is empirical. Max-pressure has theory, but canonical MP is too idealized for realistic deployment constraints.

Potential thesis: Learn or recover compact priority rules that are constrained variants of max-pressure, and certify them against finite-storage and phase-constraint admissible regions using OR models.

Why TS-compatible: This turns an AI policy-search result into a traffic network control theorem + optimization certificate.

### Gap B — Optimization-backed distillation/compression of constrained MP/MPC

Problem: Rolling-horizon MPC/LP/MILP controllers are theoretically appealing but hard to deploy; PI-Light rules are deployable but not certified.

Potential thesis: Solve a constrained network signal optimization oracle in AMPL, then distill its decisions into a PI-Light-style DSL rule and quantify exact disagreement/cost bounds.

Risk: If framed as “MIP alternative to MCTS,” it may look like an AI paper in OR clothing. Needs a guarantee: e.g., exact recovery under K=1/low-depth rules, regret/capacity bound, or feasibility-preserving rule class.

### Gap C — Finite-storage/spillback-aware priority function

Problem: Classic MP can fail or degrade with finite downstream storage and blocking; PI-Light already uses outgoing lane features, but without a principled spillback term.

Potential thesis: Derive an effective-pressure term from a store-and-forward or CTM relaxation, then restrict it to a compact interpretable DSL and certify when it preserves throughput/stability.

Risk: Recent capacity-aware/enhanced MP papers are close; differentiation must be the DSL recovery/deployability and realistic SUMO validation.

### Gap D — Realistic phase constraints: min-green, yellow loss, NEMA/ring-barrier

Problem: The code baseline only has minimum green; real intersections impose phase order, lost time, NEMA barriers, pedestrian constraints.

Potential thesis: Define the admissible constrained capacity region under these phase constraints and prove a constrained max-pressure / priority-rule variant is stabilizing within that region.

Risk: Theory can become hard. Keep empirical rule class simple and prove a limited but clean theorem.

### Gap E — Network-coupled local rules via OR shadow prices

Problem: A shared local rule cannot fully coordinate arterials/grids; full network optimization is computationally heavy.

Potential thesis: Use a network-level LP/dual model to compute interpretable link/phase weights or thresholds, then deploy local rules using those weights. The local rule remains PI-Light-like, but coordination comes from OR prices.

Risk: More complex implementation; may drift toward prediction/optimization rather than PI-Light unless the final policy is explicitly a compact priority program.

## Recommended scope for Phase 2

Do not pursue: “MIP replaces MCTS for PI-Light” as the headline. It is too incremental and likely weak for Transportation Science.

Recommended problem anchor:

**Interpretable priority rules for signalized networks: throughput guarantees under finite storage and realistic phase constraints.**

Recommended contribution shape:
1. Define a constrained priority-rule class that strictly contains classic max-pressure and PI-Light-like DSL rules.
2. Derive the rule from a finite-storage / phase-constrained store-and-forward or CTM relaxation.
3. Provide a stability/throughput guarantee for the admissible constrained capacity region, or a certification procedure when a full theorem is too strong.
4. Use AMPL/HiGHS to solve oracle/certification problems and recover/verify compact rules.
5. Evaluate in SUMO against fixed-time, actuated, classic MP, constrained/cyclical MP, PI-Light/MCTS-style rule search, and relevant RL/symbolic baselines.

## Phase 1 checkpoint summary

The literature suggests the strongest TS path is not “better interpretable RL” but “OR-certified deployable priority rules.” The crowded symbolic-TSC literature makes a pure DSL search paper risky; the max-pressure/finite-storage/phase-constraints literature gives a defensible OR backbone; SUMO+AMPL makes the experiment stack feasible.

Proceeding to Phase 2 should generate ideas around constrained max-pressure, finite storage, phase constraints, and optimization-certified DSL recovery rather than general RL+OR hybrids.

## Web sources to cite/check next

- Varaiya (2013), Max pressure control of a network of signalized intersections: https://www.sciencedirect.com/science/article/pii/S0968090X13001782
- Enhanced queue-based Max-Pressure traffic signal control (TRC 2026): https://www.sciencedirect.com/science/article/pii/S0968090X26000264
- Max-pressure signal control with cyclical phase structure (TRC 2020): https://www.sciencedirect.com/science/article/pii/S0968090X20307324
- Capacity-aware back-pressure traffic signal control: https://arxiv.org/abs/1309.6484
- Model Predictive Control for Urban Traffic Signals with Stability Guarantees: https://www.osti.gov/servlets/purl/1995694
- PI-Light AAAI 2024: https://ojs.aaai.org/index.php/AAAI/article/view/30103
- PI-eLight IEEE TMC 2026 DOI: https://doi.org/10.1109/TMC.2025.3600533
- SymLight OpenReview: https://openreview.net/forum?id=8soGuDwlxK
- TPET / Evolutionary Discovery of Heuristic Policies for TSC: https://arxiv.org/abs/2511.23122
- EvolveSignal: https://arxiv.org/abs/2509.03335
- GPLight+: https://arxiv.org/abs/2508.16090
- SignalClaw: https://arxiv.org/abs/2604.05535
- C-MP arXiv: https://arxiv.org/abs/2407.01421
- Learning to Coordinate Traffic Signals With Adaptive Network Partition: https://dblp.uni-trier.de/rec/journals/tits/MaW24.html
- sumoITScontrol: https://arxiv.org/abs/2604.23240
