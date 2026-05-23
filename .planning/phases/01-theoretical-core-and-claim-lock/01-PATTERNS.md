# Phase 1: Theoretical Core and Claim Lock - Pattern Map

**Mapped:** 2026-05-22
**Files analyzed:** 3 theory/document artifacts
**Analogs found:** 3 / 3

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `refine-logs/THEORY_CORE_PHASE1.md` | documentation / theory artifact | transform | `refine-logs/THEORY_AND_ATOMS.md` | exact |
| `refine-logs/THEORY_CLAIM_CHECKLIST.md` | documentation / validation checklist | transform | `refine-logs/EXPERIMENT_TRACKER.md` + `refine-logs/EXPERIMENT_RESULTS.md` | role-match |
| Optional manuscript-method LaTeX draft, e.g. `INFORMS-TRSC-Template-5-6-2025/dual_sensitivity_method_section.tex` or section integrated later into the TRSC template | manuscript component | transform | `INFORMS-TRSC-Template-5-6-2025/INFORMS-TRSC-Template.tex` | role-match |

## Pattern Assignments

### `refine-logs/THEORY_CORE_PHASE1.md` (documentation / theory artifact, transform)

**Analog:** `refine-logs/THEORY_AND_ATOMS.md`

**Purpose/header pattern** (lines 0-7):
```markdown
# Theory and OR-Mapped Atom Freeze

**Date**: 2026-05-22  
**Scope**: minimal primal-dual model, movement marginal-value lemma, pressure special case, and retained DSL atom taxonomy for the dual-sensitivity recovery paper.

## Purpose

This document freezes the theoretical core used by the current implementation and experiments. The goal is not to claim a new traffic-control optimality principle; it is to justify why dual sensitivities from a continuous relaxation are legitimate, interpretable inputs to sparse symbolic recovery.
```

**Continuous relaxation pattern** (lines 9-33):
```markdown
## Minimal Continuous Relaxation

For a short horizon, let:

- `x_l(t)` be queue / occupancy on link `l`,
- `d_l(t)` be exogenous arrivals,
- `S_l` be receiving/storage capacity,
- `u_m(t)` be continuous service assigned to movement `m`,
- `A_{lm}` be the signed movement-link incidence matrix, with `A_{lm}=1` when movement `m` removes flow from link `l` and `A_{lm}=-1` when it sends flow into link `l`,
- `z_l(t) >= 0` be overflow/slack for storage violation,
- `w_l >= 0` be queue weight,
- `rho_l >= 0` be storage/spillback penalty.

The one-step relaxation used in the current implementation is:

```text
minimize    sum_l w_l x^+_l + sum_l rho_l z_l
subject to  x^+_l = x_l + d_l - sum_m A_{lm} u_m              for all l
            x^+_l <= S_l + z_l                                for all l
            sum_m u_m <= G
            0 <= u_m <= U_m                                    for all m
            x^+_l >= 0, z_l >= 0                               for all l
```
```

**Dual sign-convention pattern** (lines 35-45):
```markdown
## Dual Objects

Let `lambda_l` denote the equality dual for the queue conservation constraint of link `l`, under the solver sign convention used by `scipy.optimize.linprog(method="highs")`. Let `mu_l <= 0` denote the inequality dual for the storage/supply constraint `x^+_l - z_l <= S_l`.

In the current minimization convention:

- `lambda_l` is the marginal objective sensitivity of one additional vehicle in the conservation balance of link `l`,
- binding downstream storage changes `lambda_l` through the storage dual and overflow penalty,
- the movement value reported by the implementation is `lambda_up - lambda_down`.

The finite-difference validation compares this value at the same zero-service marginal point by forcing a small `epsilon` service on each movement and measuring objective decrease.
```

**Movement-value lemma pattern** (lines 47-64):
```markdown
## Lemma 1 — Movement Marginal Service Value

For a feasible zero-service base point of the continuous relaxation, consider a small forced service perturbation `epsilon` on movement `m = i -> j`, with all other movement services fixed at zero and no active upper-service limit on `m` for sufficiently small `epsilon`.

Then the first-order objective improvement from serving movement `i -> j` is:

```text
Delta V_m / epsilon = lambda_i - lambda_j + o(1)
```

under the solver sign convention used in the implementation. When downstream storage or spillback constraints bind, their dual effects enter through `lambda_j`; equivalently, the downstream link value contains both queue-cost and receiving-capacity scarcity.
```

**Pressure special-case pattern** (lines 73-89):
```markdown
## Lemma 2 — Pressure / Backpressure Special Case

Assume:

1. linear queue objective with `w_l = x_l` or another monotone queue weight,
2. no binding downstream storage/supply constraints,
3. no corridor/service balance constraints,
4. fixed local movement topology,
5. infinitesimal service perturbations around the zero-service base point.

Then `lambda_l = w_l` up to the common solver sign convention, and therefore:

```text
MovementValue(i,j) = lambda_i - lambda_j = w_i - w_j.
```

If `w_l = x_l`, this is the ordinary pressure/backpressure movement ranking. Thus max-pressure is a special case of the dual movement-value score, not the novel component itself.
```

**OR-mapped atom taxonomy pattern** (lines 91-108):
```markdown
## Retained OR-Mapped Atom Taxonomy

Only atoms with a direct model variable, constraint, or dual interpretation should be retained.

| Atom | Current implementation name | OR source | Status |
|---|---|---|---|
| Local upstream queue | `upstream_queue` | queue state `x_i` | Retain as local baseline atom |
| Downstream queue penalty | `neg_downstream_queue` | queue state `x_j` | Retain as raw-neighbor baseline atom |
| Downstream storage slack | `downstream_slack` | storage capacity residual `S_j - x_j` | Retain when capacities are present |
| Downstream fullness | `neg_downstream_fullness` | normalized storage occupancy `x_j / S_j` | Retain as interpretable storage feature |
| Link value | `LinkValue(l)` | conservation dual `lambda_l` | Retain for theory/paper taxonomy |
| Downstream scarcity | `DownstreamScarcity(l)` | storage/supply dual effect in `lambda_l` or explicit `mu_l` | Retain when storage constraints bind |
| Movement value | `dual_sensitivity` / `MovementValue(i,j)` | `lambda_i - lambda_j` | Retain as primary dual atom |
| Value imbalance | `ValueImbalance(up,down)` | upstream-downstream dual difference | Retain as movement scoring atom |
| Pressure diagnostic | `pressure_backpressure` | special case `w_i - w_j` | Retain as diagnostic/strong baseline, not as a novelty claim |
| Random price | `random_price` | permuted dual ablation | Retain only as ablation |
| Corridor value | `CorridorValue(c)` | corridor/service balance dual | Deferred until the relaxation includes an explicit corridor constraint |
```

**Recovery objective pattern** (lines 119-129):
```markdown
## Recovery Objective Freeze

The offline recovery objective should be reported as:

```text
minimize realized_oracle_regret(policy)
       + lambda_complexity * selected_atom_count
       + lambda_neighbor * neighbor_atom_count
```

The primary metric is realized oracle regret under deterministic policy evaluation. Action agreement is secondary.
```

**Claim-boundary pattern** (lines 131-144):
```markdown
## Claim Boundary

Allowed claims after Block 0/1:

- dual movement values match finite-difference marginal service values in the continuous relaxation;
- pressure/backpressure is recovered as a nonbinding-storage special case;
- sparse offline recovery selects dual-sensitivity atoms and achieves lower realized oracle regret than raw/local/random atoms on passive+targeted state datasets.

Not yet allowed before closed-loop experiments:

- dual symbolic control improves real traffic performance;
- dual dominates max-pressure or C-MP;
- the method is robust on grids or demand shifts;
- the recovered program is deployable at scale beyond measured runtime.
```

**Planner guidance:** Expand this analog into THRY-01 through THRY-05 proposition blocks. Keep `THEORY_AND_ATOMS.md` as the consistency source; do not use Phase 1 to claim empirical dominance.

---

### `refine-logs/THEORY_CLAIM_CHECKLIST.md` (documentation / validation checklist, transform)

**Analog:** `refine-logs/EXPERIMENT_TRACKER.md` and `refine-logs/EXPERIMENT_RESULTS.md`

**Tracker-table pattern** from `refine-logs/EXPERIMENT_TRACKER.md` (lines 4-14):
```markdown
| ID | Block | Task | Status | Gate | Notes |
|---|---|---|---|---|---|
| B0.1 | Dual sanity | Implement continuous store-and-forward/CTM-lite relaxation | DONE | A | Implemented proxy SciPy LP in `scripts/run_dual_sanity.py`; no integer phase-dual story |
| B0.2 | Dual sanity | Extract duals for queue conservation, storage/supply, movement value | DONE | A | Queue/storage duals and movement values exported to JSON |
| B0.3 | Dual sanity | Run finite-difference validation | DONE | A | PASSED on toy/single/arterial proxy states; see `experiments/dual_sensitivity/block0_dual_sanity.json` |
| B0.4 | Theory | Derive dual-to-movement marginal-benefit lemma | DRAFTED | A | Drafted in `refine-logs/THEORY_AND_ATOMS.md`; needs paper-quality proof polish |
| B0.5 | Theory | Derive pressure/backpressure special case | DRAFTED | A | Drafted as nonbinding-storage special case in `refine-logs/THEORY_AND_ATOMS.md` |
| B1.1 | Recovery | Define OR-mapped DSL atom library | DONE | B | Frozen initial OR-mapped taxonomy in `refine-logs/THEORY_AND_ATOMS.md`; corridor atoms deferred until explicit corridor constraints exist |
| B1.2 | Recovery | Implement sparse MIP recovery objective | DONE | B | SciPy/HiGHS sparse MILP recovery implemented in `scripts/run_sparse_recovery.py` |
| B1.3 | Recovery | Build sampled-state datasets | DONE | B | TraCI arterial samples and targeted bottleneck/spillback topology states created |
| B1.4 | Recovery | Compare local/raw/all/random/dual DSL offline | DONE | B | Sparse recovery PASSED on targeted and combined states: dual selected with zero regret; raw/local/random worse |
```

**Gate-status pattern** from `refine-logs/EXPERIMENT_TRACKER.md` (lines 27-33):
```markdown
## Gate Status

- Gate A — Dual validity: PASSED for proxy LP, passive SUMO, and targeted SUMO sanity; formal lemma and optional AMPL validation still needed
- Gate B — Offline recovery: PASSED for sparse offline recovery; dual atom selected with zero regret on targeted and combined states, closed-loop validation pending
- Gate C — Arterial closed-loop: PENDING
- Gate D — Grid/demand generality: PENDING
- Gate E — Baseline honesty/runtime: PENDING
```

**Evidence-summary pattern** from `refine-logs/EXPERIMENT_RESULTS.md` (lines 13-24):
```markdown
## Block 0 — Dual Sanity

**Status**: PASSED

What was tested:

1. Continuous one-step store-and-forward LP proxy.
2. Queue-conservation duals and downstream storage duals.
3. Movement marginal values from upstream/downstream dual differences.
4. Finite-difference checks by forcing a small amount of service on each movement.
5. Pressure special-case ranking when storage constraints are nonbinding.
```

**Claim interpretation / next-step pattern** from `refine-logs/EXPERIMENT_RESULTS.md` (lines 157-170):
```markdown
## Gate Status

- Gate A — Dual validity: **PASSED for proxy LP, passive SUMO, and targeted SUMO; top-choice, exact full-rank, and tie-aware full-rank checks all pass after using a common zero-service marginal point**.
- Gate B — Offline recovery: **PASSED for targeted/combined offline sparse recovery; full claim still needs closed-loop SUMO validation**.
- Gate C/D/E: not started.

## Next Step

Recommended next implementation step:

1. Start Block 3 arterial closed-loop pilot with bottleneck/platoon scenarios.
2. Compare local/raw/random/dual recovered symbolic controllers against max-pressure and fixed/actuated baselines.
3. Keep pressure/backpressure as a strong diagnostic baseline and claim dual value only where it improves sparse symbolic recovery or deployability.
```

**Planner guidance:** Use a checklist table mapping `THRY-01` to `THRY-05` against: artifact section, proposition/lemma name, proof sketch present, evidence script/artifact, claim allowed, claim not allowed. Use status values such as `DONE`, `DRAFTED`, `NEEDS CHECK`, and `DEFERRED`.

---

### Optional manuscript-method LaTeX draft (manuscript component, transform)

**Analog:** `INFORMS-TRSC-Template-5-6-2025/INFORMS-TRSC-Template.tex`

**Document class and package pattern** (lines 13-35):
```latex
\documentclass[trsc,dblanonrev]{informs4}
% \documentclass[trsc,sglanonrev]{informs4}
\usepackage{eqndefns-left} % For checking the display equation width and equation environment definitions %
\RequirePackage{tgtermes}
\RequirePackage{newtxtext}
\RequirePackage{newtxmath}
\RequirePackage{bm}
\RequirePackage{endnotes}

\OneAndAHalfSpacedXII % Current default line spacing

% Optional LaTeX Packages
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{tikz}

% Natbib setup for author-number style
\usepackage{natbib}
```

**Method section / citation pattern** (lines 155-156):
```latex
\section{Methodology}\label{sec:Method}
We formulate the resource allocation problem as a two-stage stochastic programming problem, where the first stage involves decisions on resource allocation and the second stage represents the realization of uncertain parameters~\citep{smith2005,jones2010,brown2015}.
```

**Theorem/proof pattern** (lines 175-181):
```latex
\begin{theorem}[Optimality Conditions]\label{thm:Opt}
Let $x^*$ be an optimal solution to the stochastic programming problem. If the objective function and constraint functions are convex, then $x^*$ satisfies the Karush-Kuhn-Tucker (KKT) conditions.
\end{theorem}

\begin{proof}{Proof}
The proof follows from the convex optimization theory, which states that for convex objective and constraint functions, the KKT conditions are necessary and sufficient for optimality. Therefore, if $x^*$ is an optimal solution, it must satisfy the KKT conditions.\Halmos
\end{proof}
```

**Definition/lemma/remark pattern** (lines 263-277):
```latex
\begin{lemma}[Feasibility of Scenario Sets]\label{lem:FSS}
Given a set of scenarios $S$ generated from historical data and probabilistic forecasts, the scenario set $S$ is feasible if it captures the range of possible outcomes with sufficient coverage.
\end{lemma}

\begin{proof}{Proof}
The proof follows from the definition of feasibility, which requires that the scenario set $S$ includes a representative sample of possible outcomes. Feasibility ensures that the stochastic programming model adequately represents the uncertainty in the problem domain and provides meaningful solutions.\Halmos
\end{proof}

\begin{remark}
This stochastic programming model assumes that demand and supply parameters follow known probability distributions.
\end{remark}

\begin{definition}
A feasible solution to the resource allocation problem satisfies all constraints and requirements without violating any constraints.
\end{definition}
```

**Programmatic policy / oracle-regret analog** from `Programmatically_Interpretable_Reinforcement_Learning_original_paper/sec_algo.tex` (lines 14-18):
```latex
The {\em distance} between $e_\NN$ and the estimate $e$ of $e^*$ in a search iteration is defined as 
$
d(e_\NN, e) = \sum_{h \in \mathcal{H}} \norm{e(h) - e_\NN(h)}, 
$
where $\mathcal{H}$ is a set of ``interesting'' inputs (histories) and $\norm{\cdot}$ is a suitable norm.
```

**Planner guidance:** For manuscript draft, convert the Markdown proposition blocks into LaTeX `definition`, `lemma`, `proposition/theorem`, `proof`, and `remark` environments. Use OR/transportation notation; avoid copying the sample humanitarian text. Keep final citations in `\citep{...}` style.

---

## Shared Patterns

### Project claim discipline
**Source:** `CLAUDE.md` / project context and `refine-logs/THEORY_AND_ATOMS.md`  
**Apply to:** All Phase 1 artifacts

Concrete boundary from `refine-logs/THEORY_AND_ATOMS.md` (lines 131-144):
```markdown
Allowed claims after Block 0/1:

- dual movement values match finite-difference marginal service values in the continuous relaxation;
- pressure/backpressure is recovered as a nonbinding-storage special case;
- sparse offline recovery selects dual-sensitivity atoms and achieves lower realized oracle regret than raw/local/random atoms on passive+targeted state datasets.

Not yet allowed before closed-loop experiments:

- dual symbolic control improves real traffic performance;
- dual dominates max-pressure or C-MP;
- the method is robust on grids or demand shifts;
- the recovered program is deployable at scale beyond measured runtime.
```

### LP / dual extraction consistency
**Source:** `scripts/run_dual_sanity.py`  
**Apply to:** THRY-01, THRY-02, THRY-03 artifact sections

**Scenario structure** (lines 21-33):
```python
@dataclass(frozen=True)
class Scenario:
    name: str
    links: list[str]
    movements: list[tuple[int, int]]
    queue: np.ndarray
    downstream_capacity: np.ndarray
    demand: np.ndarray
    service_capacity: np.ndarray
    green_budget: float
    queue_weight: np.ndarray
    storage_penalty: np.ndarray
```

**LP construction and dual extraction** (lines 99-185):
```python
def solve_relaxation(s: Scenario, service_bonus: np.ndarray | None = None) -> dict[str, Any]:
    n_links = len(s.links)
    n_movements = len(s.movements)
    n_vars = n_links + n_movements + n_links
    x_slice = slice(0, n_links)
    u_slice = slice(n_links, n_links + n_movements)
    z_slice = slice(n_links + n_movements, n_vars)

    c = np.zeros(n_vars)
    c[x_slice] = s.queue_weight
    c[z_slice] = s.storage_penalty
    if service_bonus is not None:
        c[u_slice] -= service_bonus

    # queue conservation, green budget, storage/supply, service bounds ...

    res = linprog(..., method="highs")
    if not res.success:
        raise RuntimeError(f"LP failed for {s.name}: {res.message}")

    equality_duals = np.asarray(res.eqlin.marginals)
    upper_duals = np.asarray(res.ineqlin.marginals)

    movement_values = []
    pressure_scores = []
    for m_idx, (up, down) in enumerate(s.movements):
        value = equality_duals[up] - equality_duals[down]
        movement_values.append(value)
        pressure_scores.append(s.queue_weight[up] - s.queue_weight[down])
```

**Sanity summary pattern** (lines 282-325):
```python
def summarize_scenario(s: Scenario, eps: float) -> dict[str, Any]:
    solved = solve_relaxation(no_service_scenario(s))
    fd_values = finite_difference_service_values(s, eps)
    dual_values = solved["movement_values"]
    pressure_scores = solved["pressure_scores"]

    dual_rank = ranking(dual_values)
    fd_rank = ranking(fd_values)
    pressure_rank = ranking(pressure_scores)
    rank_match_fd = dual_rank == fd_rank
    rank_match_pressure = dual_rank == pressure_rank

    nonbinding_storage = all(abs(v) < 1e-8 for v in solved["storage_duals"])
    pressure_special_case_pass = (not nonbinding_storage) or rank_match_pressure
```

### Max-pressure baseline equivalence
**Source:** `pi_light_code/agent/rule_based/max_pressure.py`  
**Apply to:** THRY-03 pressure/backpressure special case

**Controller scoring pattern** (lines 16-37):
```python
def pick_action(self, n_obs, on_training):
    obs = n_obs[self.idx]
    if self.inter.current_phase_time < self.t_min:
        return self.current_phase

    max_pressure = -math.inf
    for phase_id in range(self.num_phase):
        pressure = self._get_pressure_for_phase(obs, phase_id)
        if pressure > max_pressure:
            max_pressure = pressure
            self.current_phase = phase_id
    return self.current_phase

def _get_pressure_for_phase(self, obs, phase_id):
    obs = obs[0]
    pressure = 0
    n_available_lane_link = self.inter.n_phase[phase_id].n_available_lanelink_id
    for lane_link in n_available_lane_link:
        start_lane_idx, end_lane_idx = lane_link[0], lane_link[1]
        pressure += obs[self.inter.n_lane_id.index(start_lane_idx)].item()
        pressure -= obs[self.inter.n_lane_id.index(end_lane_idx)].item()
    return pressure
```

### Finite-dictionary recovery quality
**Source:** `scripts/run_sparse_recovery.py`  
**Apply to:** THRY-05 and claim-checklist recovery rows

**Atom-library pattern** (lines 18-26):
```python
LIBRARIES = {
    "local_only": ["upstream_queue"],
    "raw_neighbor": ["upstream_queue", "neg_downstream_queue"],
    "all_neighbor": ["upstream_queue", "neg_downstream_queue", "downstream_slack", "neg_downstream_fullness"],
    "random_price": ["random_price"],
    "dual_sensitivity": ["dual_sensitivity"],
    "dual_plus_raw": ["dual_sensitivity", "upstream_queue", "neg_downstream_queue"],
    "pressure_backpressure": ["pressure_backpressure"],
}
```

**Regret objective and complexity penalty pattern** (lines 131-137):
```python
c = np.zeros(n_vars)
c[z_offset : z_offset + n_atoms] = complexity_penalty
for ex_idx, ex in enumerate(examples):
    best = float(np.max(ex["oracle"]))
    for m_idx, value in enumerate(ex["oracle"]):
        c[y_offsets[ex_idx] + m_idx] = best - float(value)
```

**Output metric pattern** (lines 220-233):
```python
return {
    "library": library,
    "budget": budget,
    "status": "PASSED",
    "objective": float(res.fun),
    "solve_time_sec": solve_time,
    "selected_atoms": selected,
    "weights": {atom: float(weights[j]) for j, atom in enumerate(atoms)},
    "program_complexity": len(selected),
    "realized_total_regret": total_regret,
    "realized_mean_regret": total_regret / len(examples) if examples else 0.0,
    "action_agreement": agreement / len(examples) if examples else 0.0,
    "results": rows_out,
}
```

### Script-gate validation pattern
**Source:** `scripts/run_dual_sanity.py` and `.planning/codebase/TESTING.md`  
**Apply to:** Checklist validation commands and evidence rows

**Gate output pattern** from `scripts/run_dual_sanity.py` (lines 344-364):
```python
results = [summarize_scenario(build_scenario(name), args.epsilon) for name in args.scenarios]
gate_a_pass = all(
    r["rank_match_finite_difference"] and r["pressure_special_case_pass"] for r in results
)
payload = {
    "experiment": "block0_dual_sanity",
    "status": "PASSED" if gate_a_pass else "FAILED",
    "epsilon": args.epsilon,
    "criteria": {
        "dual_rank_matches_finite_difference_rank": True,
        "pressure_rank_matches_dual_rank_when_storage_nonbinding": True,
    },
    "results": results,
}

out_path = Path(args.out)
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps({"status": payload["status"], "out": str(out_path)}, indent=2))
if not gate_a_pass:
    raise SystemExit(1)
```

## No Analog Found

No Phase 1 target artifact lacks a usable analog. The optional manuscript-method draft has only a venue/template analog, not a content-exact analog; use `refine-logs/THEORY_AND_ATOMS.md` for content and the TRSC template for LaTeX structure.

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| Optional manuscript-method LaTeX draft | manuscript component | transform | Role-match analog exists for LaTeX structure, but no project-specific dual-sensitivity manuscript section exists yet. |

## Metadata

**Analog search scope:** `/home/samuel/projects/pi_light_OR/refine-logs`, `/home/samuel/projects/pi_light_OR/scripts`, `/home/samuel/projects/pi_light_OR/pi_light_code/agent/rule_based`, `/home/samuel/projects/pi_light_OR/INFORMS-TRSC-Template-5-6-2025`, `/home/samuel/projects/pi_light_OR/Programmatically_Interpretable_Reinforcement_Learning_original_paper`

**Files scanned/read:** 13 primary files/directories: `01-CONTEXT.md`, `01-RESEARCH.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/TESTING.md`, `CLAUDE.md`, `refine-logs/THEORY_AND_ATOMS.md`, `refine-logs/FINAL_PROPOSAL.md`, `refine-logs/EXPERIMENT_TRACKER.md`, `refine-logs/EXPERIMENT_RESULTS.md`, `refine-logs/MANIFEST.md`, `scripts/run_dual_sanity.py`, `scripts/run_sparse_recovery.py`, `pi_light_code/agent/rule_based/max_pressure.py`, plus LaTeX template/algorithm analogs.

**Project skills:** No `.claude/skills/` or `.agents/skills/` directory exists under `/home/samuel/projects/pi_light_OR`.

**Pattern extraction date:** 2026-05-22
