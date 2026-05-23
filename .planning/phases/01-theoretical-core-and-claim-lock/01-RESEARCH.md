# Phase 1: Theoretical Core and Claim Lock - Research

**Researched:** 2026-05-22  
**Domain:** OR/control theory for capacitated traffic-signal networks and finite-dictionary symbolic recovery  
**Confidence:** HIGH for phase scope and existing artifacts; MEDIUM for literature positioning details that require final bibliographic cleanup

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
## Implementation Decisions

### Theory Scope
- Use a store-and-forward / CTM-lite continuous network relaxation with queue conservation, movement service, phase compatibility, and capacity/storage/supply constraints.
- Express movement dual sensitivity as generalized pressure: upstream value minus downstream value plus correction terms from binding storage, supply, phase/service, or corridor constraints.
- Treat ordinary max-pressure/backpressure equivalence as a positive structural result, not as a failure of the method.
- State binding-regime deviations as sufficient conditions or formal propositions rather than universal dominance claims.

### Claim Discipline
- Position the paper as OR/control methodology for capacitated signalized networks, not as a PI-Light enhancement paper.
- Keep the main claim conservative: dual sensitivity recovers pressure in slack or ranking-neutral regimes and may add scarcity-aware corrections in binding regimes.
- Avoid ADMM, robust optimization, column generation, bilevel optimization, freight/TR-E pivots, and GPU-heavy MARL as Phase 1 scope.
- Make Phase 3 the decisive kill gate for whether the empirical framing becomes dual advantage, pressure-equivalent symbolic recovery, or diagnostic framing.

### Recovery Link
- Include THRY-05 as a finite-dictionary recovery-regret or optimization-quality statement that bridges theory to sparse symbolic recovery in Phase 2.
- The recovery target should be oracle regret/value gap rather than imitation accuracy alone.
- Program size, neighbor use, and dual-price dependence should appear as explicit finite-dictionary constraints or penalties.
- The theory artifact should make later reviewer-facing checklist mapping straightforward for THRY-01 through THRY-05.

### Claude's Discretion
Claude may choose whether the Phase 1 artifact is a standalone technical memo, manuscript method-section draft, or both, provided the success criteria and verification checklist are satisfied. Claude may choose proposition names and exact notation, but should keep notation readable for OR/transportation reviewers.

### Deferred Ideas (OUT OF SCOPE)
## Deferred Ideas

- Empirical proof that dual beats pressure belongs to Phase 3 and Phase 4, not Phase 1.
- Full sparse recovery implementation belongs to Phase 2.
- Repository reproducibility hardening belongs to Phase 5.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| THRY-01 | The paper defines a continuous capacitated traffic-network relaxation with queue conservation, movement service, phase compatibility, and storage/supply/capacity constraints. | Use a short-horizon store-and-forward / CTM-lite LP with conservation, service, phase-compatibility, green-budget, service-bound, and storage/supply constraints; this aligns with existing Block 0 LP scaffold. [VERIFIED: codebase Read: scripts/run_dual_sanity.py] [CITED: https://eprints.gla.ac.uk/81374/] |
| THRY-02 | The paper derives a movement-level dual-sensitivity decomposition with interpretable upstream, downstream, storage/supply, and corridor/service terms. | Derive movement value from conservation-dual differences and add correction terms only when the primal model includes the corresponding storage, supply, phase/service, or corridor constraint. [VERIFIED: codebase Read: refine-logs/THEORY_AND_ATOMS.md] [CITED: https://support.sas.com/documentation/cdl/en/ormpug/66107/HTML/default/ormpug_optmodel_sect102.htm] |
| THRY-03 | The paper proves max-pressure/backpressure is a special case when storage/supply/corridor constraints are nonbinding or ranking-neutral. | State max-pressure as the slack-regime reduction of the dual score; Varaiya's max-pressure model is the foundational throughput/stability reference, and the local implementation scores phases by upstream-minus-downstream lane queues. [CITED: https://trid.trb.org/View/1279571] [VERIFIED: codebase Read: pi_light_code/agent/rule_based/max_pressure.py] |
| THRY-04 | The paper proves or formalizes a spillback/scarcity correction term showing how dual sensitivity can differ from ordinary pressure in binding regimes. | Use storage/supply shadow prices as correction terms and frame them as sufficient conditions for rank changes, not dominance claims; finite-capacity back-pressure literature identifies finite queues, non-work-conservation, and congestion propagation as relevant failure modes. [CITED: https://arxiv.org/abs/1309.6484] |
| THRY-05 | The paper states a recovery-regret or optimization-quality result for finite dictionary symbolic policy recovery. | Use a finite-class ERM/oracle-inequality style statement: learned policy risk/regret is compared to the best policy in the finite symbolic dictionary plus optimization/statistical slack; current sparse recovery already optimizes realized oracle regret. [CITED: https://gradml.mit.edu/supervised/learnability_and_vc/] [CITED: https://www.stat.cmu.edu/~cshalizi/sml/21/lectures/16/lecture-16.html] [VERIFIED: codebase Read: scripts/run_sparse_recovery.py] |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- The project identity is “PI-Light OR / Dual-Sensitivity Symbolic Traffic Control,” and it should be presented as OR-methodology for capacitated network traffic signal control rather than as a PI-Light enhancement. [VERIFIED: codebase Read: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Target reviewers are Transportation Research Part B / Transportation Science reviewers who expect mathematical modeling, structural insight, rigorous optimization formulation, and closed-loop computational evidence against strong max-pressure-style baselines. [VERIFIED: codebase Read: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Phase 1 recommendations must preserve claim discipline: generalized pressure with scarcity-aware corrections, not universal dominance over max-pressure. [VERIFIED: codebase Read: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Keep ADMM, robust optimization, column generation, bilevel optimization, freight/TR-E pivots, and GPU-heavy MARL outside Phase 1. [VERIFIED: codebase Read: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Experiments and validation should remain CPU-oriented with SUMO/TraCI, SciPy/HiGHS, AMPL/HiGHS where useful, and sparse MIP recovery; no GPU pipeline is required. [VERIFIED: codebase Read: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- New OR artifacts should be auditable, emit structured JSON/CSV when executable, and trace tables/figures back to raw artifacts. [VERIFIED: codebase Read: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- New Python scripts, if any are later added outside this research phase, should use lowercase snake_case, `main() -> None`, `argparse`, `Path`, JSON-serializable outputs, explicit exceptions, and compact JSON status printing. [VERIFIED: codebase Read: /home/samuel/projects/pi_light_OR/CLAUDE.md]
- Project skills are not present under `.claude/skills/` or `.agents/skills/`, so no additional skill rules apply. [VERIFIED: tool run: ls skill directories]

## Summary

Phase 1 should produce a theory/claim-lock artifact, not implementation code. The artifact should define a continuous capacitated store-and-forward / CTM-lite relaxation, derive movement-level dual sensitivities, prove ordinary max-pressure/backpressure as the slack or ranking-neutral special case, formalize binding-regime scarcity corrections, and state a finite-dictionary recovery-quality result. [VERIFIED: codebase Read: .planning/ROADMAP.md] [VERIFIED: codebase Read: .planning/REQUIREMENTS.md]

The strongest planning choice is to write both: (1) a standalone technical memo/checklist for reviewer-facing traceability and (2) a manuscript-method-section draft that can later be moved into the paper. This is allowed by the Phase 1 context and is safer than only drafting informal notes because THRY-01 through THRY-05 each need definitions, assumptions, propositions, and proof sketches. [VERIFIED: codebase Read: .planning/phases/01-theoretical-core-and-claim-lock/01-CONTEXT.md]

Existing project evidence supports the core structure but not universal performance claims: `scripts/run_dual_sanity.py` passes dual-vs-finite-difference and pressure-special-case gates, and `scripts/run_sparse_recovery.py` passes targeted sparse-recovery scaffolding; these are sanity/recovery artifacts, not closed-loop dominance evidence. [VERIFIED: tool run: dual sanity PASSED] [VERIFIED: tool run: sparse recovery PASSED] [VERIFIED: codebase Read: refine-logs/EXPERIMENT_RESULTS.md]

**Primary recommendation:** Plan Phase 1 as a theory artifact deliverable with five proposition blocks: model definition, dual movement-value lemma, pressure special-case theorem, scarcity-correction proposition, and finite-dictionary recovery-regret proposition; add a reviewer-facing checklist that maps each proposition to THRY-01 through THRY-05. [VERIFIED: codebase Read: .planning/ROADMAP.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Continuous capacitated relaxation | Theory / Manuscript | Existing LP sanity script | The relaxation is a mathematical object for the paper; `run_dual_sanity.py` is only evidence that the local LP scaffold is consistent with the definitions. [VERIFIED: codebase Read: scripts/run_dual_sanity.py] |
| Movement-level dual decomposition | Theory / Manuscript | Validation artifact | Dual values are reviewer-facing marginal-value objects; scripts can verify finite-difference consistency but should not define the paper notation by themselves. [CITED: https://support.sas.com/documentation/cdl/en/ormpug/66107/HTML/default/ormpug_optmodel_sect102.htm] |
| Max-pressure/backpressure special case | Theory / Manuscript | Baseline implementation | The proof owns the equivalence claim; `MaxPressure` provides implementation alignment by scoring phases through upstream-minus-downstream queues. [CITED: https://trid.trb.org/View/1279571] [VERIFIED: codebase Read: pi_light_code/agent/rule_based/max_pressure.py] |
| Binding-regime scarcity correction | Theory / Manuscript | Phase 3 static kill gate | Phase 1 should formalize sufficient rank-change/scarcity conditions; empirical strength is deliberately deferred to Phase 3. [VERIFIED: codebase Read: .planning/ROADMAP.md] [CITED: https://arxiv.org/abs/1309.6484] |
| Finite-dictionary recovery quality | Theory / Manuscript | Phase 2 sparse recovery | Phase 1 states the optimization-quality target; Phase 2 implements full K-atom recovery with penalties. [VERIFIED: codebase Read: .planning/REQUIREMENTS.md] [VERIFIED: codebase Read: scripts/run_sparse_recovery.py] |
| Reviewer-facing claim checklist | Planning / Manuscript QA | Theory memo | The checklist prevents overclaiming and maps THRY-01–THRY-05 to definitions/propositions/proof sketches. [VERIFIED: codebase Read: .planning/ROADMAP.md] |

## Standard Stack

### Core

| Library / Artifact | Version | Purpose | Why Standard |
|--------------------|---------|---------|--------------|
| Markdown technical memo under `refine-logs/` or phase docs | N/A | Lock definitions, assumptions, propositions, proof sketches, and claim checklist. | Existing research artifacts are Markdown, and Phase 1 is a theory/manuscript phase rather than a software-package phase. [VERIFIED: codebase Read: .planning/codebase/STRUCTURE.md] |
| LaTeX manuscript-method draft | TeX Live 2023 / pdfTeX 1.40.25 available | Convert theory into publication-ready notation and proposition/proof structure. | The repository includes an INFORMS Transportation Science template directory and LaTeX/BibTeX sources. [VERIFIED: codebase Read: .planning/codebase/STRUCTURE.md] [VERIFIED: tool run: pdflatex version] |
| `scipy.optimize.linprog(method="highs")` | SciPy 1.17.1 installed | Maintain consistency with Block 0 LP dual sanity checks and marginal extraction. | SciPy’s official `linprog` solves LP minimization in standard inequality/equality form and exposes marginals/dual values. [VERIFIED: tool run: Python import scipy] [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html] |
| `scipy.optimize.milp` | SciPy 1.17.1 installed | Ground THRY-05 in the existing finite-dictionary sparse recovery scaffold. | SciPy’s official `milp` solves mixed-integer linear programs with linear constraints, integrality, and HiGHS backend. [VERIFIED: tool run: Python import scipy] [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html] |
| SUMO / TraCI evidence context | SUMO 1.26.0, TraCI 1.26.0, sumolib 1.26.0 installed | Provide existing traffic-network state and sanity context; not required for writing the theory artifact. | Existing project uses SUMO/TraCI for state sampling and later closed-loop validation. [VERIFIED: tool run: sumo/netconvert/Python imports] [VERIFIED: codebase Read: .planning/codebase/TESTING.md] |

### Supporting

| Library / Artifact | Version | Purpose | When to Use |
|--------------------|---------|---------|-------------|
| `scripts/run_dual_sanity.py` | Project script | Verify dual movement rankings against finite-difference perturbations and pressure-special-case gates. | Use as a validation command after theory notation is locked to ensure notation remains consistent with code. [VERIFIED: codebase Read: scripts/run_dual_sanity.py] |
| `scripts/run_sparse_recovery.py` | Project script | Verify the current realized oracle-regret recovery scaffold and selected atom outputs. | Use only as support for THRY-05; do not treat it as full Phase 2 completion. [VERIFIED: codebase Read: scripts/run_sparse_recovery.py] |
| Transportation Science / TR-B venue scope pages | Current web pages accessed 2026-05-22 | Support OR/methodological framing and reviewer expectations. | Use for paper positioning, not for theorem content. [CITED: https://pubsonline.informs.org/page/trsc/editorial-statement] [CITED: https://www.sciencedirect.com/journal/transportation-research-part-b-methodological via WebSearch] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Markdown memo plus LaTeX method draft | Only a Markdown note | Faster, but weaker for manuscript integration and reviewer-facing theorem/proof polishing. [ASSUMED] |
| One-step relaxation | Full multi-period CTM-lite relaxation | Multi-period notation is more realistic but risks Phase 1 sprawl; use one-step for local marginal derivation and state multi-period extension as optional. [VERIFIED: codebase Read: refine-logs/THEORY_AND_ATOMS.md] |
| Conservative scarcity proposition | Universal dominance theorem | Universal dominance contradicts project constraints and known pressure-special-case framing. [VERIFIED: codebase Read: .planning/PROJECT.md] |
| Finite-class recovery-regret statement | Large learning-theory proof | Finite-class ERM/oracle inequality is enough for Phase 1 and matches the finite symbolic dictionary; deep statistical learning theory would distract from OR/control contribution. [CITED: https://gradml.mit.edu/supervised/learnability_and_vc/] [CITED: https://www.stat.cmu.edu/~cshalizi/sml/21/lectures/16/lecture-16.html] |

**Installation:**
```bash
# No new package installation is recommended for Phase 1.
# Use the existing Python/SciPy/SUMO/LaTeX environment and write theory artifacts only.
```

**Version verification performed:**
```bash
python3 --version                         # Python 3.14.4 [VERIFIED: tool run]
python -c "import numpy, scipy"           # numpy 2.4.3, scipy 1.17.1 [VERIFIED: tool run]
python -c "import traci, sumolib"         # traci 1.26.0, sumolib 1.26.0 [VERIFIED: tool run]
sumo --version                            # Eclipse SUMO 1.26.0 [VERIFIED: tool run]
netconvert --version                      # Eclipse SUMO netconvert 1.26.0 [VERIFIED: tool run]
pdflatex --version                        # pdfTeX 1.40.25 / TeX Live 2023 [VERIFIED: tool run]
```

## Package Legitimacy Audit

No external package installation is proposed for Phase 1, so the Package Legitimacy Gate is not applicable. [VERIFIED: phase scope]

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| None | — | — | — | — | Not run | No install planned |

**Packages removed due to slopcheck [SLOP] verdict:** none.  
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```text
Traffic-network state assumptions
  (queues, storage, turning/service, phase compatibility)
        |
        v
Continuous capacitated relaxation
  - conservation
  - movement service
  - phase/green feasibility
  - storage/supply/capacity constraints
        |
        v
LP/KKT dual objects
  - link conservation duals
  - storage/supply duals
  - phase/service/corridor duals if modeled
        |
        v
Movement-level generalized pressure
  score(i->j) = upstream link value - downstream link value + modeled correction terms
        |
        +--> Slack / ranking-neutral regime
        |       v
        |   Max-pressure/backpressure special case
        |
        +--> Binding storage/supply/corridor regime
        |       v
        |   Scarcity-aware correction and possible rank deviation
        |
        v
Finite symbolic dictionary recovery target
  - oracle regret / value gap
  - program size penalty
  - neighbor-use penalty
  - dual-price dependence penalty
        |
        v
Reviewer-facing claim checklist
  THRY-01 .. THRY-05 mapped to definitions/propositions/proofs
```

### Recommended Project Structure

```text
refine-logs/
├── THEORY_CORE_PHASE1.md          # recommended standalone theory memo [ASSUMED]
├── THEORY_CLAIM_CHECKLIST.md      # recommended reviewer-facing THRY mapping [ASSUMED]
└── THEORY_AND_ATOMS.md            # existing atom/theory freeze to update or cite [VERIFIED: codebase Read]
INFORMS-TRSC-Template-5-6-2025/
└── ...                            # manuscript-method LaTeX draft can later be integrated here [VERIFIED: codebase Read]
experiments/dual_sensitivity/
├── block0_dual_sanity.json        # existing sanity artifact [VERIFIED: codebase Read]
└── block1_sparse_recovery*.json   # existing recovery artifact family [VERIFIED: codebase Read]
```

### Pattern 1: Model-First, Script-Second Theory

**What:** Define the mathematical relaxation independently, then point to scripts only as validation artifacts. [VERIFIED: codebase Read: .planning/ROADMAP.md]

**When to use:** Use for THRY-01 through THRY-04 so the paper is not perceived as code-derived empiricism. [ASSUMED]

**Example:**
```text
Definition 1 (Capacitated movement-service relaxation).
Let L be links and M be permitted movements. For each movement m=(i,j), service u_m removes flow from i and adds flow to j subject to phase compatibility, service bounds, and downstream supply/storage feasibility.
```
Source: project model pattern in `refine-logs/THEORY_AND_ATOMS.md` and `scripts/run_dual_sanity.py`. [VERIFIED: codebase Read]

### Pattern 2: Explicit Sign Convention Box

**What:** Add a boxed sign-convention note explaining whether a dual is a cost increase or objective-improvement value, because SciPy/HiGHS reports minimization marginals and the project reports movement values as `lambda_up - lambda_down`. [VERIFIED: codebase Read: scripts/run_dual_sanity.py] [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html]

**When to use:** Use before the movement-value lemma and in any proof sketch using KKT conditions. [ASSUMED]

**Example:**
```text
Sign convention. We write V_l for the marginal congestion cost of one additional vehicle on link l. Under the implementation convention, movement value for m=(i,j) is V_i - V_j; positive value means serving m reduces the local relaxation objective to first order.
```
Source: SciPy marginals documentation and project implementation. [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html] [VERIFIED: codebase Read: scripts/run_dual_sanity.py]

### Pattern 3: Pressure as a Theorem, Not a Baseline Footnote

**What:** State pressure/backpressure equivalence as a formal special-case proposition. [VERIFIED: codebase Read: .planning/REQUIREMENTS.md]

**When to use:** Use for THRY-03 and the paper’s claim discipline. [VERIFIED: codebase Read: .planning/PROJECT.md]

**Example:**
```text
Proposition (Pressure special case).
If storage/supply/corridor constraints are nonbinding or ranking-neutral and the link value is a monotone queue weight V_l = w_l, then the dual movement ranking for m=(i,j) is identical to ranking w_i - w_j. If w_l=x_l, this is the ordinary pressure/backpressure score.
```
Source: project theory freeze and Varaiya max-pressure reference. [VERIFIED: codebase Read: refine-logs/THEORY_AND_ATOMS.md] [CITED: https://trid.trb.org/View/1279571]

### Pattern 4: Scarcity as Sufficient Rank-Change Conditions

**What:** Formalize binding-regime deviations using sufficient conditions such as “a downstream storage/supply shadow price changes the sign or rank ordering of two candidate movements.” [VERIFIED: codebase Read: .planning/phases/01-theoretical-core-and-claim-lock/01-CONTEXT.md]

**When to use:** Use for THRY-04; do not state that dual always beats pressure. [VERIFIED: codebase Read: .planning/PROJECT.md]

**Example:**
```text
Proposition (Scarcity-induced rank correction).
For movements a=(i,j) and b=(p,q), if ordinary pressure ranks a above b but the modeled downstream scarcity correction on j exceeds the pressure gap by more than the correction on q, then the dual score ranks b above a.
```
Source: finite-capacity back-pressure concern and project claim discipline. [CITED: https://arxiv.org/abs/1309.6484] [VERIFIED: codebase Read: .planning/PROJECT.md]

### Anti-Patterns to Avoid

- **Universal dominance language:** Do not write “dual sensitivity improves max-pressure” without regime qualifiers and Phase 3 evidence. [VERIFIED: codebase Read: .planning/PROJECT.md]
- **Unmodeled corridor atoms:** Do not claim a corridor dual unless the relaxation includes an explicit corridor/service-balance constraint. [VERIFIED: codebase Read: refine-logs/THEORY_AND_ATOMS.md]
- **Solver-sign ambiguity:** Do not mix SciPy minimization marginals, objective-improvement values, and pressure scores without a sign-convention box. [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html]
- **Imitation-only recovery theory:** Do not state THRY-05 as action-agreement accuracy; the locked recovery target is oracle regret/value gap. [VERIFIED: codebase Read: .planning/phases/01-theoretical-core-and-claim-lock/01-CONTEXT.md]
- **Optimization side quests:** Do not add ADMM, robust optimization, column generation, bilevel, or freight pivots in Phase 1. [VERIFIED: codebase Read: .planning/PROJECT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Max-pressure foundation | A new “pressure” definition with no citation | Varaiya max-pressure/backpressure framing plus project baseline implementation | The existing literature already establishes local max-pressure control and throughput/stability framing; novelty is generalized dual/scarcity and symbolic recovery. [CITED: https://trid.trb.org/View/1279571] [VERIFIED: codebase Read: pi_light_code/agent/rule_based/max_pressure.py] |
| Finite-capacity caveat | Ad hoc spillback explanation detached from literature | Capacity-aware back-pressure / finite-queue-capacity references | Finite queues can create non-work-conservation and congestion-propagation issues in prior back-pressure assumptions. [CITED: https://arxiv.org/abs/1309.6484] |
| Shadow-price interpretation | Custom marginal-value terminology | Standard LP dual/shadow-price sensitivity language | Official optimization documentation defines dual values/shadow prices as RHS sensitivity/marginal optimal-value rates. [CITED: https://support.sas.com/documentation/cdl/en/ormpug/66107/HTML/default/ormpug_optmodel_sect102.htm] |
| Recovery-quality statement | A bespoke generalization theorem from scratch | Finite-class ERM/oracle-inequality template adapted to oracle regret | Finite hypothesis-class learning has standard log-cardinality/generalization structure; oracle inequalities compare learned risk to best-in-class risk plus slack. [CITED: https://gradml.mit.edu/supervised/learnability_and_vc/] [CITED: https://www.stat.cmu.edu/~cshalizi/sml/21/lectures/16/lecture-16.html] |
| Phase 1 validation | Notebook-only manual checks | Existing script-gate commands plus reviewer checklist | Project validation pattern is script-based JSON gating, not pytest. [VERIFIED: codebase Read: .planning/codebase/TESTING.md] |

**Key insight:** The theory must make pressure equivalence mathematically expected and scarcity deviations mathematically legitimate; the empirical question of whether those deviations help belongs to the Phase 3 kill gate. [VERIFIED: codebase Read: .planning/ROADMAP.md]

## Common Pitfalls

### Pitfall 1: Overclaiming Against Max-Pressure

**What goes wrong:** The text implies dual sensitivity universally dominates max-pressure. [VERIFIED: codebase Read: .planning/PROJECT.md]  
**Why it happens:** Existing pilot artifacts show pressure/backpressure can tie dual in constructed cases, so positive evidence can be misread as dominance. [VERIFIED: codebase Read: refine-logs/EXPERIMENT_RESULTS.md]  
**How to avoid:** Use “recovers pressure in slack/ranking-neutral regimes and may add scarcity-aware corrections in binding regimes.” [VERIFIED: codebase Read: .planning/phases/01-theoretical-core-and-claim-lock/01-CONTEXT.md]  
**Warning signs:** Phrases like “beats max-pressure,” “dominates pressure,” or “superior controller” appear before Phase 3. [ASSUMED]

### Pitfall 2: Corridor Term Without Corridor Constraint

**What goes wrong:** The theory claims a corridor/service dual term without adding a corresponding primal corridor/service-balance constraint. [VERIFIED: codebase Read: refine-logs/THEORY_AND_ATOMS.md]  
**Why it happens:** Corridor language is attractive for traffic reviewers, but dual variables only exist for modeled constraints. [CITED: https://support.sas.com/documentation/cdl/en/ormpug/66107/HTML/default/ormpug_optmodel_sect102.htm]  
**How to avoid:** Either defer corridor terms or include a minimal explicit corridor/service constraint and label it optional. [VERIFIED: codebase Read: refine-logs/THEORY_AND_ATOMS.md]  
**Warning signs:** `CorridorValue(c)` appears in the atom table without a primal equation. [VERIFIED: codebase Read: refine-logs/THEORY_AND_ATOMS.md]

### Pitfall 3: Sign Convention Drift

**What goes wrong:** Proof notation says one score direction while code and finite differences use another. [VERIFIED: codebase Read: scripts/run_dual_sanity.py]  
**Why it happens:** Minimization dual marginals, objective-improvement values, and pressure scores have easy-to-flip signs. [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html]  
**How to avoid:** Add a sign-convention box and verify by `python3 scripts/run_dual_sanity.py`. [VERIFIED: tool run: dual sanity PASSED]  
**Warning signs:** The same movement is described as both penalized and preferred under identical state values. [ASSUMED]

### Pitfall 4: Treating Block 0/1 as Paper Evidence

**What goes wrong:** The paper claims closed-loop traffic-control benefit from LP sanity and offline sparse recovery only. [VERIFIED: codebase Read: refine-logs/EXPERIMENT_RESULTS.md]  
**Why it happens:** Existing Block 0/1 gates pass, but the roadmap explicitly requires Phase 3/4 before empirical claim interpretation. [VERIFIED: codebase Read: .planning/ROADMAP.md]  
**How to avoid:** Use Block 0/1 only as validation of theory consistency and recovery scaffold. [VERIFIED: codebase Read: refine-logs/EXPERIMENT_RESULTS.md]  
**Warning signs:** Static oracle regret is described as “traffic performance.” [ASSUMED]

### Pitfall 5: Recovery Statement Too Strong for Finite Data

**What goes wrong:** THRY-05 claims the recovered symbolic policy is globally optimal for traffic control. [ASSUMED]  
**Why it happens:** MILP optimality over the finite training sample can be confused with population control optimality. [CITED: https://www.stat.cmu.edu/~cshalizi/sml/21/lectures/16/lecture-16.html]  
**How to avoid:** State optimization quality as best-in-dictionary empirical regret plus solver gap/statistical slack, and separate empirical-sample optimality from out-of-sample traffic performance. [CITED: https://gradml.mit.edu/supervised/learnability_and_vc/] [VERIFIED: codebase Read: scripts/run_sparse_recovery.py]

## Code Examples

Verified patterns from official/project sources:

### Continuous Relaxation Skeleton

```text
minimize    Σ_l w_l x_l^+ + Σ_l ρ_l z_l
subject to  x_l^+ = x_l + d_l - Σ_m A_lm u_m                 ∀l
            x_l^+ ≤ S_l + z_l                                 ∀l
            Σ_{m∈p} u_m ≤ service/green feasible set           ∀phase or junction
            0 ≤ u_m ≤ U_m                                      ∀m
            x_l^+ ≥ 0, z_l ≥ 0                                 ∀l
```
Source: existing project theory freeze and Block 0 LP scaffold. [VERIFIED: codebase Read: refine-logs/THEORY_AND_ATOMS.md] [VERIFIED: codebase Read: scripts/run_dual_sanity.py]

### Movement Dual Value Pattern

```text
MovementValue(i,j) = LinkValue(i) - LinkValue(j) + modeled correction terms
```
Source: `scripts/run_dual_sanity.py` computes `equality_duals[up] - equality_duals[down]`; official optimization docs identify marginals/duals as shadow-price sensitivity values. [VERIFIED: codebase Read: scripts/run_dual_sanity.py] [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html]

### Finite-Dictionary Recovery-Regret Statement

```text
Let Π_K be the finite class of symbolic policies satisfying atom budget K,
neighbor budget B, and dual-price budget D. For sampled states s_n with oracle
movement values Q*(s_n,a), define empirical regret

R_hat(π) = (1/N) Σ_n [ max_a Q*(s_n,a) - Q*(s_n, π(s_n)) ].

The recovered policy π_hat should satisfy

R_hat(π_hat) ≤ min_{π∈Π_K} R_hat(π) + optimization_gap,

and the paper may separately state a finite-class generalization slack when
IID/sampling assumptions are declared.
```
Source: project sparse recovery objective and finite-class ERM/oracle-inequality references. [VERIFIED: codebase Read: scripts/run_sparse_recovery.py] [CITED: https://gradml.mit.edu/supervised/learnability_and_vc/] [CITED: https://www.stat.cmu.edu/~cshalizi/sml/21/lectures/16/lecture-16.html]

### Validation Commands

```bash
python3 scripts/run_dual_sanity.py --out experiments/dual_sensitivity/block0_dual_sanity.json
python3 scripts/run_sparse_recovery.py \
  --states experiments/dual_sensitivity/targeted_bottleneck_states.json \
  --out experiments/dual_sensitivity/block1_sparse_recovery_targeted.json
```
Source: existing project testing map and verified tool run. [VERIFIED: codebase Read: .planning/codebase/TESTING.md] [VERIFIED: tool run]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Max-pressure/backpressure under idealized/infinite-capacity assumptions | Capacity-aware or finite-storage-aware back-pressure variants address finite queues and congestion propagation | Capacity-aware back-pressure preprint 2013/revision 2014 | Phase 1 should acknowledge finite storage as a known issue and position dual scarcity terms as an OR-derived way to represent modeled scarcity, not as a claim that finite-capacity concerns are new. [CITED: https://arxiv.org/abs/1309.6484] |
| Signal optimization as timing settings only | Store-and-forward and constrained optimization models for congested networks support queue-conservation and green/split optimization | Store-and-forward congested-network work published 2009; signal MILP roots published 1975 | The relaxation should be recognizable to transportation/OR reviewers. [CITED: https://eprints.gla.ac.uk/81374/] [CITED: https://ideas.repec.org/a/inm/ortrsc/v9y1975i4p321-343.html] |
| Symbolic/control novelty as the paper identity | OR-derived dual sensitivity and finite-dictionary symbolic recovery as the identity | Project pivot documented 2026-05-22 | Avoid claiming symbolic TSC or neighbor awareness as novel by itself. [VERIFIED: codebase Read: .planning/PROJECT.md] |
| Action-agreement imitation quality | Oracle regret / value gap with complexity and neighbor penalties | Project context locked 2026-05-22 | THRY-05 and Phase 2 should optimize regret/value gap, not imitation accuracy alone. [VERIFIED: codebase Read: .planning/phases/01-theoretical-core-and-claim-lock/01-CONTEXT.md] |

**Deprecated/outdated for Phase 1:**
- “Dual beats pressure everywhere”: rejected by project constraints and pressure-special-case logic. [VERIFIED: codebase Read: .planning/PROJECT.md]
- “PI-Light extension paper”: rejected as the main identity; PI-Light should be predecessor/baseline/reference, not conceptual boundary. [VERIFIED: codebase Read: .planning/PROJECT.md]
- “Add ADMM/robust/bilevel as theory breadth”: explicitly out of scope for this phase. [VERIFIED: codebase Read: .planning/PROJECT.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Writing both a memo and manuscript-method draft is safer than only writing informal notes. | Summary / Standard Stack | Planner might over-scope Phase 1 if the user wants only one artifact. |
| A2 | TR-B / Transportation Science reviewers will value proposition-level formalization over code-derived explanation for this phase. | Architecture Patterns | Artifact could be heavier than necessary for an internal milestone. |
| A3 | Warning-sign phrasing such as “beats max-pressure” before Phase 3 should be treated as claim drift. | Common Pitfalls | Planner might make checklist too strict if internal drafts need exploratory language. |

## Open Questions (RESOLVED)

1. **RESOLVED: Include corridor/service terms only when explicitly modeled.**
   - Decision: Phase 1 will include storage/supply constraints as the primary binding-regime correction and may include a minimal optional corridor/service-balance constraint only if the memo writes the corresponding primal constraint explicitly.
   - Implementation consequence: Any corridor/service dual term must be labeled as optional/model-dependent; otherwise corridor terms are deferred and cannot appear as standalone claims.
   - Reason: Existing `THEORY_AND_ATOMS.md` defers corridor value until an explicit corridor constraint exists. [VERIFIED: codebase Read: refine-logs/THEORY_AND_ATOMS.md]

2. **RESOLVED: Final Phase 1 artifacts live in `refine-logs/` with planning evidence under `.planning/`.**
   - Decision: Execution should write the main theory artifact to `refine-logs/THEORY_AND_CLAIMS.md` and the reviewer-facing traceability artifact to `refine-logs/THEORY_REVIEW_CHECKLIST.md`.
   - Implementation consequence: No separate LaTeX manuscript draft is required in Phase 1; the Markdown theory memo should be LaTeX-ready in notation and structure so later manuscript work can migrate it.
   - Reason: Existing research notes live in `refine-logs/`, while phase docs under `.planning/phases/01-theoretical-core-and-claim-lock/` should remain workflow artifacts. [VERIFIED: codebase Read: .planning/codebase/STRUCTURE.md]

3. **RESOLVED: Use deterministic empirical recovery quality as required; make finite-sample statistics optional and explicitly assumption-bound.**
   - Decision: THRY-05 must state a finite-dictionary empirical oracle-regret/value-gap guarantee relative to the best policy in the constrained dictionary plus solver/optimization gap.
   - Implementation consequence: Any finite-sample or IID generalization corollary must be clearly labeled optional and must not imply global traffic-control optimality.
   - Reason: Existing sparse recovery optimizes realized oracle regret, and finite-class ERM/oracle-inequality references support only assumption-bound statistical slack. [CITED: https://gradml.mit.edu/supervised/learnability_and_vc/] [CITED: https://www.stat.cmu.edu/~cshalizi/sml/21/lectures/16/lecture-16.html]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Python | Existing validation scripts | ✓ | 3.14.4 | Not needed for writing theory if validation is skipped. [VERIFIED: tool run] |
| NumPy | Existing validation scripts | ✓ | 2.4.3 | None needed for theory-only writing. [VERIFIED: tool run] |
| SciPy | LP/MILP sanity and recovery gates | ✓ | 1.17.1 | Use existing JSON artifacts if rerun is not required. [VERIFIED: tool run] |
| SUMO | Later traffic-state context and downstream phases | ✓ | 1.26.0 | Not required for Phase 1 theory writing. [VERIFIED: tool run] |
| netconvert | Network generation in later phases | ✓ | 1.26.0 | Not required for Phase 1 theory writing. [VERIFIED: tool run] |
| TraCI / sumolib | SUMO state sampling in existing scripts | ✓ | 1.26.0 | Not required for Phase 1 theory writing. [VERIFIED: tool run] |
| LaTeX / pdfTeX | Optional manuscript-method draft compilation | ✓ | TeX Live 2023 / pdfTeX 1.40.25 | Write Markdown-only memo if compilation is not required. [VERIFIED: tool run] |
| latexmk | Optional LaTeX build convenience | ✓ | 4.83 | Use `pdflatex` directly. [VERIFIED: tool run] |
| amplpy | Optional AMPL backend | ✗ | — | Do not require AMPL in Phase 1; use existing SciPy/HiGHS evidence. [VERIFIED: tool run] |

**Missing dependencies with no fallback:** none for Phase 1 theory writing. [VERIFIED: environment audit]

**Missing dependencies with fallback:** `amplpy` is missing, but Phase 1 can rely on SciPy/HiGHS and existing artifacts. [VERIFIED: tool run]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | No dedicated pytest/unittest framework detected; validation is script-gate based. [VERIFIED: codebase Read: .planning/codebase/TESTING.md] |
| Config file | none detected for pytest/unittest. [VERIFIED: codebase Read: .planning/codebase/TESTING.md] |
| Quick run command | `python3 scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json` [VERIFIED: tool run] |
| Full suite command | `python3 scripts/run_dual_sanity.py && python3 scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json` [VERIFIED: codebase Read: .planning/codebase/TESTING.md] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| THRY-01 | Relaxation definitions include conservation, service, phase compatibility, and storage/supply/capacity constraints. | manual artifact checklist | `grep -E "conservation|service|phase|storage|supply|capacity" refine-logs/THEORY_CORE_PHASE1.md` | ❌ Wave 0 |
| THRY-02 | Dual decomposition maps upstream, downstream, storage/supply, and optional corridor/service terms. | manual artifact checklist + sanity script | `python3 scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json` | ✅ script exists; ❌ final memo |
| THRY-03 | Pressure/backpressure special case is stated and checked against nonbinding cases. | script gate + checklist | `python3 scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json` | ✅ script exists; ❌ final memo |
| THRY-04 | Binding-regime scarcity correction is stated as sufficient conditions without dominance language. | manual artifact checklist | `grep -E "scarcity|binding|sufficient|not.*domin|may" refine-logs/THEORY_CORE_PHASE1.md` | ❌ Wave 0 |
| THRY-05 | Finite-dictionary recovery-regret/quality statement is included and tied to oracle regret. | script gate + checklist | `python3 scripts/run_sparse_recovery.py --states experiments/dual_sensitivity/targeted_bottleneck_states.json --out /tmp/phase1_sparse_recovery_check.json` | ✅ script exists; ❌ final memo |

### Sampling Rate

- **Per task commit:** Run the relevant artifact checklist plus `python3 scripts/run_dual_sanity.py --out /tmp/phase1_dual_sanity_check.json` when notation changes affect dual/pressure definitions. [VERIFIED: codebase Read: .planning/codebase/TESTING.md]
- **Per wave merge:** Run dual sanity and targeted sparse recovery checks. [VERIFIED: tool run]
- **Phase gate:** Theory memo/checklist must map THRY-01 through THRY-05 and must avoid universal dominance claims before `/gsd:verify-work`. [VERIFIED: codebase Read: .planning/ROADMAP.md]

### Wave 0 Gaps

- [ ] `refine-logs/THEORY_CORE_PHASE1.md` — formal definitions/propositions/proof sketches for THRY-01 through THRY-05. [ASSUMED target path]
- [ ] `refine-logs/THEORY_CLAIM_CHECKLIST.md` — reviewer-facing mapping from requirement to theorem/proposition/check. [ASSUMED target path]
- [ ] Optional manuscript-method LaTeX draft — integrates the theory in paper-ready notation. [ASSUMED target path]

## Security Domain

Phase 1 is a theory/manuscript phase and should not add authentication, session, access-control, cryptographic, or web-input surfaces. [VERIFIED: phase scope] OWASP ASVS is a web application security verification standard, so most categories are not applicable to this phase. [CITED: https://owasp.org/www-project-application-security-verification-standard/]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No authentication feature is touched. [VERIFIED: phase scope] |
| V3 Session Management | no | No session-management feature is touched. [VERIFIED: phase scope] |
| V4 Access Control | no | No application access-control feature is touched. [VERIFIED: phase scope] |
| V5 Input Validation | limited | If lightweight checklist scripts are added later, validate file paths and fail fast using existing CLI patterns. [VERIFIED: codebase Read: .planning/codebase/STRUCTURE.md] |
| V6 Cryptography | no | Do not add cryptography or secret handling in Phase 1. [VERIFIED: phase scope] |

### Known Threat Patterns for Phase 1 Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Accidental disclosure of AMPL license IDs or local secrets in research notes | Information Disclosure | Do not commit AMPL activation commands or license IDs; existing results note says AMPL setup notes are outside the public repository. [VERIFIED: codebase Read: refine-logs/EXPERIMENT_RESULTS.md] |
| Dynamic code execution in PI-Light DSL is misunderstood as part of Phase 1 | Tampering / Elevation of Privilege | Do not modify or execute generated PI-Light DSL code in Phase 1; theory only. [VERIFIED: codebase Read: .planning/codebase/STRUCTURE.md] |

## Sources

### Primary (HIGH confidence)

- Project planning context: `/home/samuel/projects/pi_light_OR/.planning/phases/01-theoretical-core-and-claim-lock/01-CONTEXT.md` — locked Phase 1 scope and deferred ideas. [VERIFIED: codebase Read]
- Project requirements: `/home/samuel/projects/pi_light_OR/.planning/REQUIREMENTS.md` — THRY-01 through THRY-05. [VERIFIED: codebase Read]
- Project roadmap: `/home/samuel/projects/pi_light_OR/.planning/ROADMAP.md` — Phase 1 success criteria and verification/UAT. [VERIFIED: codebase Read]
- Project constraints: `/home/samuel/projects/pi_light_OR/.planning/PROJECT.md` and `/home/samuel/projects/pi_light_OR/CLAUDE.md` — claim discipline and out-of-scope items. [VERIFIED: codebase Read]
- Existing theory freeze: `/home/samuel/projects/pi_light_OR/refine-logs/THEORY_AND_ATOMS.md` — model, movement lemma, pressure special case, atom taxonomy. [VERIFIED: codebase Read]
- Existing validation scripts: `/home/samuel/projects/pi_light_OR/scripts/run_dual_sanity.py` and `/home/samuel/projects/pi_light_OR/scripts/run_sparse_recovery.py`. [VERIFIED: codebase Read]
- SciPy `linprog` official docs — LP form, HiGHS method, marginals/dual values. [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html]
- SciPy `milp` official docs — MILP form, integrality, HiGHS backend. [CITED: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html]
- SAS/OR dual values documentation — dual/shadow-price sensitivity interpretation. [CITED: https://support.sas.com/documentation/cdl/en/ormpug/66107/HTML/default/ormpug_optmodel_sect102.htm]
- Transportation Science editorial statement — journal scope includes mathematical models, advanced methodologies, traffic-flow theory, optimization, and transportation systems analysis. [CITED: https://pubsonline.informs.org/page/trsc/editorial-statement]

### Secondary (MEDIUM confidence)

- Varaiya max-pressure bibliographic/abstract record — local max-pressure, feasible demand stability, throughput framing. [CITED: https://trid.trb.org/View/1279571]
- Capacity-aware back-pressure preprint — finite queue capacities, non-work-conservation, congestion propagation, normalized pressure. [CITED: https://arxiv.org/abs/1309.6484]
- Aboudolas, Papageorgiou & Kosmatopoulos store-and-forward record — store-and-forward methods for congested urban networks. [CITED: https://eprints.gla.ac.uk/81374/]
- Gartner, Little & Gabbay Transportation Science MILP signal optimization record — cycle time, green splits, offsets, MILP signal setting. [CITED: https://ideas.repec.org/a/inm/ortrsc/v9y1975i4p321-343.html]
- Levin max-pressure review record — mathematical throughput properties and practical extensions. [CITED: https://experts.umn.edu/en/publications/max-pressure-traffic-signal-timing-a-summary-of-methodological-an/]
- MIT finite hypothesis-class learning notes — finite class ERM sample-complexity dependence on log-cardinality. [CITED: https://gradml.mit.edu/supervised/learnability_and_vc/]
- CMU ERM notes — risk, empirical risk, and empirical risk minimization definitions. [CITED: https://stat.cmu.edu/~cshalizi/sml/21/lectures/03/lecture-03.html]
- CMU model-selection notes — oracle inequality concept comparing learned risk to best-in-class risk plus complexity slack. [CITED: https://www.stat.cmu.edu/~cshalizi/sml/21/lectures/16/lecture-16.html]
- OWASP ASVS official page — web application security verification standard. [CITED: https://owasp.org/www-project-application-security-verification-standard/]

### Tertiary (LOW confidence)

- Transportation Research Part B official scope was identified via WebSearch but not successfully fetched due 403; use the ScienceDirect page for later manual bibliographic confirmation. [CITED: https://www.sciencedirect.com/journal/transportation-research-part-b-methodological via WebSearch]
- Specific artifact path names `refine-logs/THEORY_CORE_PHASE1.md` and `refine-logs/THEORY_CLAIM_CHECKLIST.md` are recommendations, not existing files. [ASSUMED]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new installs are needed; existing Python/SciPy/SUMO/LaTeX environment was probed. [VERIFIED: tool run]
- Architecture: HIGH — Phase 1 scope and existing artifact boundaries are directly specified by project planning files. [VERIFIED: codebase Read]
- Pitfalls: HIGH for claim-discipline pitfalls from project files; MEDIUM for reviewer-expectation wording. [VERIFIED: codebase Read] [ASSUMED]
- Literature positioning: MEDIUM — key references were found and official/record pages were checked, but final manuscript should still verify BibTeX metadata and publication details manually. [CITED: source URLs above]

**Research date:** 2026-05-22  
**Valid until:** 2026-06-21 for internal project context; 2026-06-05 for literature/source freshness before manuscript citation cleanup.
