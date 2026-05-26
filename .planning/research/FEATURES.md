# v1.4 Research: Features

## Evidence From v1.3

The completed v1.3 main artifact has 2160/2160 rows and `status: FAILED`. The strict Gate C companion is `INCONCLUSIVE` because its input artifact is `FAILED`. Phase 12 claim inputs allow Phase 7/9 static theory claims, but keep Phase 11/Gate C closed-loop superiority `claim_allowed=false`.

The primary metric rule is especially important:

- 279 Gate C primary metric comparisons.
- 48 `bounded_harm`.
- 221 `inconclusive`.
- 10 `non_worsening`.
- Only a few strict positive signals appear, concentrated in total-delay rows for selected oversaturation/turning-shock groups against capacity-aware and finite-storage double-pressure comparators.

This means v1.4 cannot be a simple rerun. The method needs a real mechanism change or a disciplined route decision that abandons the strong claim.

## Feature Categories

### Failure Diagnosis

- Identify which scenarios and demand multipliers produce bounded harm.
- Separate delay harm from spillback/blocking/unfinished/switching non-signals.
- Compare failures against max-pressure, capacity-aware pressure, and finite-storage double-pressure separately.
- Detect whether the proposed controller is too aggressive, too conservative, or indistinguishable from baselines in each regime.

### Candidate Method Workstreams

1. `v1-4-score-controller`
   - Change the live control score or decision rule.
   - Candidate ideas: normalized scarcity corrections, gating corrections only under verified binding, anti-gridlock hysteresis, phase-switch penalty calibration, or queue-release priority terms.

2. `v1-4-objective-weights`
   - Change objective component weights and decision thresholds.
   - Candidate ideas: learn/tune weights on exploratory pilot rows, then freeze them before confirmation; separate delay, unfinished vehicles, storage risk, and switching loss.

3. `v1-4-scenario-diagnostics`
   - Determine whether v1.3 scenarios actually activate the finite-storage mechanism enough to support a dominance claim.
   - Candidate ideas: audit binding intensity, action divergence from max-pressure, and whether stress mechanisms alter SUMO behavior rather than only metadata.

4. `v1-4-symbolic-policy`
   - Improve recovered symbolic policy behavior or compression after identifying a stronger oracle/candidate.
   - Candidate ideas: constrain symbolic rules to preserve non-worsening safety checks, recover separate binding-regime rule families, and reject compressed policies that lose Gate C pilot advantage.

### Candidate Selection

- Use pilot/smoke gates only to eliminate weak candidates.
- Require non-worsening on all primary metrics in the pilot family.
- Require at least one strict positive signal in every scenario/demand/comparator group selected for confirmation.
- Do not tune final thresholds after reading the main Gate C result.

### Confirmation Gate

- Lock one candidate method.
- Lock controller set, required comparators, scenarios, seeds, demand multipliers, primary metrics, thresholds, and failure rules.
- Run the new main Gate C and regenerate Phase 12 claim surfaces.
- Allow closed-loop superiority only if the locked Gate C artifact is `PASSED`.

