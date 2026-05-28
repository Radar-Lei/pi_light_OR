#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import traci

from claim_policy import forbidden_claim_hits
from finite_storage_schema import (
    OBJECTIVE_COMPONENT_FIELDS,
    build_finite_storage_state,
    build_objective_components_from_metrics,
    validate_finite_storage_state,
    validate_state_objective_sample,
)
from sample_sumo_states import build_network_metadata

METRIC_FIELDS = [
    "avg_travel_time",
    "penalized_avg_travel_time",
    "total_delay",
    "completed_vehicles",
    "completion_rate",
    "throughput",
    "mean_queue",
    "max_queue",
    "spillback_count",
    "blocking_count",
    "switching_count",
    "controller_runtime_sec",
]
CONTROLLER_REGISTRY = {
    "fixed_time": "Deterministic cycle through green phases.",
    "actuated_local_pressure": "Queue-triggered local pressure with fixed-time fallback.",
    "max_pressure": "Movement score q_up - q_down.",
    "capacity_aware_pressure": "Pressure with downstream fullness penalty.",
    "occupancy_capacity_aware_pressure": "Pressure with downstream fullness penalty computed from vehicle-count occupancy.",
    "cycle_pressure": "Pressure with deterministic current-cycle hold bias.",
    "finite_storage_double_pressure": "Pressure with finite-storage receiving-capacity correction.",
    "local_pilight": "Real PI-Light/DSL baseline if adaptable; otherwise explicit not_feasible.",
    "raw_neighbor_symbolic": "Symbolic upstream queue minus downstream queue.",
    "all_neighbor_symbolic": "Symbolic pressure with downstream slack/fullness terms.",
    "random_permuted_dual": "Deterministic seed-based placebo movement score.",
    "finite_storage_primal_dual": "Finite-storage pressure rule with auditable storage, spillback, switching, service, and incident terms.",
    "finite_storage_primal_dual_v1_4_score": "v1.4 locked finite-storage score variant with stronger binding-regime terms.",
    "finite_storage_dynamic_primal_dual_v1_5": "Dynamic finite-storage primal-dual pressure with occupancy-based storage duals, cascade prices, and upstream release values.",
    "finite_storage_dynamic_primal_dual_v1_5_r2_guarded": "Guarded v1.5 dynamic finite-storage primal-dual pressure with capped non-pressure corrections for post-holdout method revision.",
    "finite_storage_dynamic_primal_dual_v1_5_r3_double_release": "Post-r2 dynamic finite-storage controller using finite-storage double-pressure as a scaffold plus bounded release/service dual terms.",
    "finite_storage_dynamic_primal_dual_v1_5_r4_release_service": "Post-r3 dynamic finite-storage controller using finite-storage double-pressure scaffold with release/service dual terms only.",
    "finite_storage_dynamic_primal_dual_v1_5_r5_double_safe": "Post-r4 dynamic finite-storage controller with finite-storage-double safety fallback for completion-risk control.",
    "finite_storage_dynamic_primal_dual_v1_5_r6_terminal_flush": "Post-r5 dynamic finite-storage controller with terminal finite-storage-double flush fallback for completion-risk control.",
    "finite_storage_dynamic_primal_dual_v1_5_r7_double_filter": "Post-r6 dynamic finite-storage controller with per-action finite-storage-double score safety filter.",
    "finite_storage_dynamic_primal_dual_v1_5_r8_multi_baseline_filter": "Post-r7 dynamic finite-storage controller with per-action capacity-aware and finite-storage-double safety filters.",
    "finite_storage_dynamic_primal_dual_v1_5_r9_hold_only": "Post-r8 dynamic finite-storage controller that may only replace pressure switches with current-phase holds.",
    "finite_storage_dynamic_primal_dual_v1_5_r10_bounded_hold": "Post-r9 dynamic finite-storage controller that limits current-phase hold overrides to avoid starvation.",
    "finite_storage_dynamic_primal_dual_v1_5_r11_completion_risk": "Post-r10 dynamic finite-storage controller with explicit completion-risk service preservation.",
    "finite_storage_dynamic_primal_dual_v1_5_r12_route_completion": "Post-r11 dynamic finite-storage controller with receiver-constrained route completion prediction.",
    "finite_storage_dynamic_primal_dual_v1_5_r13_route_demand": "Post-r12 dynamic finite-storage controller with TraCI route-demand movement completion prediction.",
    "finite_storage_dynamic_primal_dual_v1_5_r14_route_demand_double_safe": "Post-r13 route-demand completion controller with finite-storage-double score veto.",
    "finite_storage_dynamic_primal_dual_v1_5_r15_horizon_model": "Post-r14 dynamic finite-storage controller with horizon-aware modeled completion scoring.",
    "finite_storage_dynamic_primal_dual_v1_5_r16_horizon_terminal": "Post-r15 horizon-aware completion model with terminal finite-storage-double lock.",
    "finite_storage_dynamic_primal_dual_v1_5_r17_horizon_capacity_terminal": "Post-r16 horizon-aware completion model with terminal capacity-aware lock.",
    "finite_storage_dynamic_primal_dual_v1_5_r18_horizon_balanced_terminal": "Post-r17 horizon-aware completion model with balanced capacity/double terminal lock.",
    "finite_storage_dynamic_primal_dual_v1_5_r19_horizon_double_anchored": "Post-r18 horizon-aware completion model with stronger finite-storage-double anchoring.",
    "finite_storage_dynamic_primal_dual_v1_5_r20_horizon_max_double_terminal": "Post-r19 horizon-aware completion model with balanced max-pressure/double terminal lock.",
    "finite_storage_dynamic_primal_dual_v1_5_r21_horizon_service_terminal": "Post-r20 horizon-aware completion model with terminal max/double completion-service guard.",
    "finite_storage_dynamic_primal_dual_v1_5_r22_horizon_completion_safety": "Post-r21 horizon-aware completion model with all-interval completion-safety veto.",
    "finite_storage_dynamic_primal_dual_v1_5_r23_horizon_dominance": "Post-r22 horizon-aware completion model with baseline-dominance filter for marginal horizon overrides.",
    "finite_storage_dynamic_primal_dual_v1_5_r24_staged_horizon": "Post-r23 staged horizon-completion model that delays route completion overrides until late-horizon risk.",
    "finite_storage_dynamic_primal_dual_v1_5_r25_staged_horizon_late_max": "Post-r24 staged horizon-completion model with late max-pressure completion lock.",
    "finite_storage_dynamic_primal_dual_v1_5_r26_relative_exit_urgency": "Post-r25 staged horizon-completion model with remaining-horizon relative exit urgency.",
    "finite_storage_dynamic_primal_dual_v1_5_r27_terminal_exit_protection": "Post-r26 staged horizon-completion model with late all-phase exit-protection guard.",
    "finite_storage_dynamic_primal_dual_v1_5_r28_max_pressure_envelope": "Post-r27 staged horizon-completion model with max-pressure completion envelope.",
    "finite_storage_dynamic_primal_dual_v1_5_r29_core_baseline_envelope": "Post-r28 staged horizon-completion model with all-core-baseline completion envelope.",
    "finite_storage_dynamic_primal_dual_v1_5_r30_double_envelope": "Post-r29 staged horizon-completion model with finite-storage-double completion envelope.",
    "finite_storage_dynamic_primal_dual_v1_5_r31_late_double_terminal": "Post-r30 staged horizon-completion model with later finite-storage-double terminal lock.",
    "finite_storage_dynamic_primal_dual_v1_5_r32_preterminal_double_guard": "Post-r31 staged horizon-completion model with a gated preterminal finite-storage-double guard.",
    "finite_storage_dynamic_primal_dual_v1_5_r33_midcourse_double_guard": "Post-r32 staged horizon-completion model with a midcourse finite-storage-double guard.",
    "finite_storage_dynamic_primal_dual_v1_5_r34_core_minimax_guard": "Post-r33 staged horizon-completion model with a gated minimax guard across core baselines.",
    "finite_storage_dynamic_primal_dual_v1_5_r35_deadline_urgency": "Post-r34 staged horizon-completion model with deadline-oriented route urgency.",
    "finite_storage_dynamic_primal_dual_v1_5_r36_late_deadline_anchor": "Post-r35 staged horizon-completion model with late gated deadline urgency.",
    "finite_storage_dynamic_primal_dual_v1_5_r37_late_deadline_service_anchor": "Post-r36 late deadline model with an explicit completion-service anchor.",
    "finite_storage_dynamic_primal_dual_v1_5_r38_capacity_rescue_guard": "Post-r37 late deadline model with a narrow capacity-aware completion-safety rescue guard.",
    "finite_storage_dynamic_primal_dual_v1_5_r39_capacity_score_envelope": "Post-r38 late deadline model with a capacity-aware score envelope on horizon overrides.",
    "finite_storage_dynamic_primal_dual_v1_5_r40_pressure_safe_horizon": "Post-r39 late deadline model that permits horizon overrides only inside a pressure-safe core-baseline envelope.",
    "finite_storage_dynamic_primal_dual_v1_5_r41_terminal_core_completion": "Post-r40 model with a locked terminal completion choice among core baselines.",
    "finite_storage_dynamic_primal_dual_v1_5_r42_tail_completion_rescue": "Post-r41 model with a late tail-completion rescue for pressure-safe horizon reverts.",
    "finite_storage_dynamic_primal_dual_v1_5_r43_staged_pressure_safe": "Post-r42 return to staged horizon with pressure-safe core-baseline guard and no deadline urgency.",
    "finite_storage_dynamic_primal_dual_v1_5_r44_loose_staged_pressure_safe": "Post-r43 staged horizon with a looser pressure-safe guard to recover action separation.",
    "finite_storage_dynamic_primal_dual_v1_5_r45_preterminal_pressure_safe": "Post-r44 staged horizon with pressure-safe guard limited to preterminal completion risk.",
    "finite_storage_dynamic_primal_dual_v1_5_r46_occupancy_safe_completion": "Post-r45 staged horizon with preterminal pressure-safe guard plus occupancy-gated completion-safety veto.",
    "finite_storage_dynamic_primal_dual_v1_5_r47_staged_severe_double_safe": "Post-r46 staged horizon with mid-severity occupancy-gated double-pressure safety fallback plus narrower emergency completion veto.",
    "finite_storage_dynamic_primal_dual_v1_5_r48_pressure_double_conflict_safe": "Post-r47 staged horizon with explicit pressure-vs-double conflict fallback in severe occupancy regimes.",
    "finite_storage_dynamic_primal_dual_v1_5_r49_early_pressure_double_conflict_safe": "Post-r48 pressure-vs-double conflict fallback activated immediately after warmup to catch early severe-occupancy misses.",
    "finite_storage_dynamic_primal_dual_v1_5_r50_completion_conflict_safe": "Post-r49 severe-risk completion-filter guard that fails closed to the shared pressure/double baseline when completion-only divergence appears unsafe.",
    "finite_storage_dynamic_primal_dual_v1_5_r51_core_consensus_safe": "Post-r50 severe-risk core consensus guard that fails closed when pressure, capacity, and double baselines all agree on a safer action.",
    "finite_storage_dynamic_primal_dual_v1_5_r52_raw_consensus_safe": "Post-r50 narrow severe-risk raw-score consensus guard that only catches non-completion-filter deviations from a shared pressure-capacity-double baseline.",
    "finite_storage_dynamic_primal_dual_v1_5_r53_post_veto_double_safe": "Post-r50 severe-risk post-veto double-safe guard that rechecks pressure-vs-double conflicts after completion-safety vetoes.",
    "finite_storage_dynamic_primal_dual_v1_5_r54_reactivated_dual_safe": "Post-r50 safety stack with reactivated storage and cascade dual prices to restore true dynamic primal-dual separation.",
    "finite_storage_dynamic_primal_dual_v1_5_r55_reactivated_dual_uncapped_safe": "Post-r54 reactivated dual stack without correction-cap guardrail suppression.",
    "finite_storage_dynamic_primal_dual_v1_5_r56_reactivated_dual_raw_consensus_safe": "Post-r55 uncapped reactivated dual stack with severe-risk raw-consensus fallback to shared core baselines.",
    "finite_storage_dynamic_primal_dual_v1_5_r57_reactivated_dual_capacity_completion_safe": "Post-r56 reactivated dual stack with a severe-risk completion-filter fail-close back to the shared pressure-capacity baseline.",
    "finite_storage_dynamic_primal_dual_v1_5_r58_reactivated_dual_post_veto_double_safe": "Post-r56 reactivated dual stack with severe-risk raw-consensus fallback plus post-veto double-safe correction.",
    "finite_storage_dynamic_primal_dual_v1_5_r59_reactivated_dual_narrow_post_veto_double_safe": "Post-r56 reactivated dual stack with a narrow post-veto double-safe correction only when completion veto happens outside the horizon filter and capacity agrees with double.",
    "finite_storage_dynamic_primal_dual_v1_5_r60_reactivated_dual_early_capacity_conflict_safe": "Post-r59 reactivated dual stack with an early-only completion-filter fail-close back to capacity when pressure and capacity agree against double.",
    "finite_storage_dynamic_primal_dual_v1_5_r61_reactivated_dual_mid_severe_early_capacity_conflict_safe": "Post-r59 reactivated dual stack with a mid-severe early completion-filter capacity correction that avoids extreme-occupancy overcorrection.",
    "finite_storage_dynamic_primal_dual_v1_5_r62_reactivated_dual_late_severe_raw_consensus_safe": "Post-r59 reactivated dual stack with a later, more severe raw-consensus fallback to recover dynamic action separation.",
    "finite_storage_dynamic_primal_dual_v1_5_r63_reactivated_dual_native_base_safe": "Post-r59 reactivated dual stack using the native finite-storage base instead of finite-storage-double scaffold, with the narrow post-veto safety correction preserved.",
    "finite_storage_dynamic_primal_dual_v1_5_r64_reactivated_dual_native_base_late_severe_safe": "Post-r63 native-base reactivated dual stack with a later, more severe raw-consensus fallback to recover separation without immediate consensus collapse.",
    "finite_storage_dynamic_primal_dual_v1_5_r65_reactivated_dual_native_capacity_score_rescue": "Post-r63 native-base reactivated dual stack with a score-aware capacity rescue for severe completion-filter conflicts against pressure-capacity consensus.",
    "finite_storage_dynamic_primal_dual_v1_5_r66_reactivated_dual_native_horizon_score_blend": "Post-r63 native-base reactivated dual stack whose route-horizon completion filter blends native dynamic scores directly instead of leaning on a double-pressure surrogate.",
    "finite_storage_dynamic_primal_dual_v1_5_r67_reactivated_dual_native_negative_total_penalty": "Post-r63 native-base reactivated dual stack whose route-horizon completion score softly penalizes actions with deeply negative native dynamic totals.",
    "finite_storage_dynamic_primal_dual_v1_5_r68_reactivated_dual_native_double_horizon_blend": "Post-r63 native-base reactivated dual stack whose route-horizon completion filter blends native dynamic scores with a reduced double-pressure surrogate instead of choosing only one side.",
    "finite_storage_dynamic_primal_dual_v1_5_r69_reactivated_dual_release_biased_native_base": "Post-r63 native-base reactivated dual stack with stronger upstream release value and milder storage/cascade suppression to recover actions that pressure-capacity baselines agree are safe to release.",
    "finite_storage_dynamic_primal_dual_v1_5_r70_reactivated_dual_descendant_release_native_base": "Post-r63 native-base reactivated dual stack whose upstream release price activates whenever slack exists anywhere on the downstream path, not only on the immediate child edge.",
    "finite_storage_dynamic_primal_dual_v1_5_r71_reactivated_dual_local_descendant_release_native_base": "Post-r63 native-base reactivated dual stack whose descendant-slack release support only activates when the immediate child still retains local receiving slack and the upstream occupancy is already severe.",
    "finite_storage_dynamic_primal_dual_v1_5_r72_reactivated_dual_release_risk_horizon_blend": "Post-r63 native-base reactivated dual stack whose route-horizon completion filter directly rewards release value and penalizes storage-spillback-cascade risk from the dynamic decomposition.",
    "finite_storage_dynamic_primal_dual_v1_5_r73_reactivated_dual_release_risk_late_conflict_safe": "Post-r72 release-risk horizon blend with a later, more severe completion-conflict fallback and a slightly delayed pressure-safe guard to recover method-body separation without reopening early safety misses.",
    "finite_storage_dynamic_primal_dual_v1_5_r74_reactivated_dual_negative_total_consensus_safe": "Post-r73 release-risk horizon blend with a narrow sanity guard that only fails closed when the selected action still has negative native total and negative pressure while all three core baselines agree on another action.",
    "finite_storage_dynamic_primal_dual_v1_5_r75_reactivated_dual_release_risk_negative_pressure_blend": "Post-r73 release-risk horizon blend that directly penalizes negative-pressure phases inside the horizon score, instead of relying on broader completion-conflict fallbacks.",
    "finite_storage_dynamic_primal_dual_v1_5_r76_reactivated_dual_release_risk_negative_total_blend": "Post-r75 release-risk horizon blend that directly penalizes phases whose native dynamic total is still negative, without reverting to broad safety fallbacks.",
    "finite_storage_dynamic_primal_dual_v1_5_r77_reactivated_dual_conditional_risk_blend": "Post-r75 release-risk horizon blend whose negative-pressure and negative-total penalties only activate in early severe spillback regimes, rather than globally.",
    "finite_storage_dynamic_primal_dual_v1_5_r78_reactivated_dual_conditional_risk_late_raw_consensus": "Post-r77 conditional-risk horizon blend that keeps early severe score-side penalties, while delaying raw-consensus fallback to later, more severe non-completion deviations.",
    "finite_storage_dynamic_primal_dual_v1_5_r79_reactivated_dual_negative_total_completion_conflict": "Post-r78 conditional-risk stack with a narrow completion-conflict fail-close that only fires when completion-filter picks a pressure-vs-double deviation whose native total is already materially negative.",
    "finite_storage_dynamic_primal_dual_v1_5_r80_reactivated_dual_negative_total_raw_consensus": "Post-r79 conditional-risk stack with a narrow non-completion raw-consensus fail-close that only fires when a shared pressure-capacity-double baseline is being overridden by a materially negative native total.",
    "finite_storage_dynamic_primal_dual_v1_5_r81_reactivated_dual_severe_negative_total_raw_consensus": "Post-r80 conditional-risk stack that narrows the non-completion raw-consensus fail-close to deeper negative-total deviations, preserving separation while still catching the worst early non-completion misses.",
    "finite_storage_dynamic_primal_dual_v1_5_r82_reactivated_dual_conditional_low_total_pressure_blend": "Post-r79 conditional-risk stack with an early-severe score-side penalty that demotes low-total, nonpositive-pressure completion candidates without flattening strong positive-pressure separation.",
    "finite_storage_dynamic_primal_dual_v1_5_r83_reactivated_dual_low_total_consensus_completion": "Post-r79 conditional-risk stack with a narrow early-severe completion-filter sanity guard that only catches low-total, nonpositive-pressure deviations away from a shared pressure-capacity-double baseline.",
    "finite_storage_dynamic_primal_dual_v1_5_r84_reactivated_dual_conditional_release_gate": "Post-r79 conditional-risk stack whose early-severe horizon score only preserves full release bonus for phases that still show positive pressure or enough native total, reducing weak completion-only deviations at the score source.",
    "finite_storage_dynamic_primal_dual_v1_5_r85_reactivated_dual_horizon_local_pressure": "Post-r79 conditional-risk stack that pushes weak completion candidates down at the route-horizon source by penalizing nonpositive local pressure inside the raw horizon completion score.",
    "finite_storage_dynamic_primal_dual_v1_5_r86_reactivated_dual_horizon_zero_slack_floor": "Post-r79 conditional-risk stack that removes the raw horizon slack floor only for nonpositive local-pressure movements, so zero-residual weak completion candidates stop receiving artificial positive credit.",
    "finite_storage_dynamic_primal_dual_v1_5_r87_reactivated_dual_low_signal_bonus_gate": "Post-r79 conditional-risk stack that strips release, storage-risk, and nonnegative-total completion bonuses only from early-severe low-signal candidates, preserving strong-separation actions while demoting weak completion-only deviations at the score source.",
    "finite_storage_dynamic_primal_dual_v1_5_r88_reactivated_dual_low_signal_bonus_scale": "Post-r87 conditional-risk stack that only trims a small fraction of the low-signal completion bonuses, targeting the weak 0.1-margin misrankings without flattening stronger separation.",
    "finite_storage_dynamic_primal_dual_v1_5_r89_reactivated_dual_low_signal_margin_cap": "Post-r79 conditional-risk stack that only caps thin-margin low-signal completion wins over the core baselines, removing weak 0.1-level bonus-only outranks without flattening stronger separation.",
    "finite_storage_dynamic_primal_dual_v1_5_r90_reactivated_dual_supported_margin_cap": "Post-r79 conditional-risk stack that only caps thin-margin low-signal completion wins when the best core baseline still carries real route-horizon support, avoiding r89's broad caps against bonus-only baselines.",
    "finite_storage_dynamic_primal_dual_v1_5_r91_reactivated_dual_supported_narrow_margin_cap": "Post-r90 conditional-risk stack that keeps the supported thin-margin cap but narrows the allowed win margin, trying to recover r79-level separation without reopening broad bonus-only outranks.",
    "finite_storage_dynamic_primal_dual_v1_5_r92_reactivated_dual_supported_score_gap_cap": "Post-r90 conditional-risk stack that only caps thin-margin low-signal completion wins when the best core baseline also holds a large raw route-horizon score advantage, targeting the real r79 weak outranks instead of all supported thin wins.",
    "finite_storage_dynamic_primal_dual_v1_5_r93_reactivated_dual_score_gap_consensus_safe": "Post-r92 conditional-risk stack that adds a very narrow non-completion fail-close when all core baselines agree and the selected action still has a deeply negative native total plus a large raw route-horizon score deficit.",
    "finite_storage_dynamic_primal_dual_v1_5_r94_reactivated_dual_supported_low_total_margin_cap": "Post-r92 conditional-risk stack that preserves the supported thin-win cap only for very-low-total completion deviations, aiming to remove the remaining weak early severe outranks without restoring r90's broader separation loss.",
    "finite_storage_dynamic_primal_dual_v1_5_r95_reactivated_dual_supported_negative_pressure_margin_cap": "Post-r92 conditional-risk stack that only caps thin-margin low-signal completion wins when the selected phase is already negative-pressure, targeting the narrowest r92-style weak outranks without touching neutral-pressure separation.",
    "finite_storage_dynamic_primal_dual_v1_5_r96_reactivated_dual_unique_movement_horizon": "Post-r92 route-horizon semantics fix that scores each aggregated completion movement once per phase, preventing duplicated lane entries from repeatedly reusing the same finishable-demand signal.",
    "finite_storage_dynamic_primal_dual_v1_5_r97_reactivated_dual_unique_residual_power_horizon": "Post-r92 route-horizon semantics fix that both deduplicates aggregated completion movements and steepens residual-capacity sensitivity, so low-slack downstreams stop outranking safer core-baseline completions on raw finishable volume alone.",
    "finite_storage_dynamic_primal_dual_v1_5_r98_reactivated_dual_unique_finishable_power_horizon": "Post-r96 route-horizon semantics fix that keeps unique aggregated movement accounting but applies diminishing returns to finishable-demand volume, reducing thin wins that arise only because one phase serves more repeated completion vehicles.",
    "finite_storage_dynamic_primal_dual_v1_5_r99_reactivated_dual_unique_finishable_ratio_horizon": "Post-r96 route-horizon semantics fix that normalizes completion credit by total movement demand, removing thin wins that survive only because one phase carries a larger completion volume despite similar per-vehicle finishability.",
    "finite_storage_dynamic_primal_dual_v1_5_r100_reactivated_dual_unique_finishable_power_time_weight_horizon": "Post-r98 route-horizon semantics fix that keeps unique aggregated movement accounting and diminishing returns on finishable volume, then sharpens time normalization so slower completion candidates lose more of their raw finishable advantage.",
    "finite_storage_dynamic_primal_dual_v1_5_r101_reactivated_dual_unique_finishable_power_conditional_time_weight_horizon": "Post-r98 route-horizon semantics fix that only sharpens time normalization for low-residual completion phases with no positive local-pressure support, preserving stronger separation where the selected phase still has real upstream pressure behind it.",
    "finite_storage_dynamic_primal_dual_v1_5_r102_reactivated_dual_unique_finishable_power_conditional_pressure_time_weight_horizon": "Post-r101 route-horizon semantics fix that only sharpens time normalization for no-positive-local-pressure completion phases when the whole phase also points into strongly pressured downstreams, narrowing the conditional suppression to the real weak-completion regimes.",
    "finite_storage_dynamic_primal_dual_v1_5_r103_reactivated_dual_unique_finishable_power_movement_pressure_time_weight_horizon": "Post-r101 route-horizon semantics fix that keeps the no-positive-local-pressure low-residual phase gate but only sharpens time normalization for the high-downstream-pressure low-residual movements inside that phase, avoiding r102's whole-phase suppression.",
    "finite_storage_dynamic_primal_dual_v1_5_r104_reactivated_dual_unique_finishable_power_no_risky_margin_cap": "Post-r103 route-horizon semantics fix that caps only thin completion-filter wins whose phase never triggered movement-level risky time normalization even though a core baseline still has a clearly better raw horizon score.",
    "finite_storage_dynamic_primal_dual_v1_5_r105_reactivated_dual_unique_finishable_power_no_risky_nonpositive_pressure_margin_cap": "Post-r104 route-horizon semantics fix that keeps the no-risky thin-win cap only when the selected completion phase itself has no positive local-pressure support, avoiding r104's over-capping of locally supported separations.",
    "finite_storage_dynamic_primal_dual_v1_5_r106_reactivated_dual_unique_finishable_power_secondary_time_weight_horizon": "Post-r103 route-horizon semantics fix that adds a gentler secondary time-normalization band for no-positive-local-pressure weak completion phases whose residual is only moderately slack, reducing thin wins at the score source instead of capping them afterward.",
    "finite_storage_dynamic_primal_dual_v1_5_r107_reactivated_dual_low_support_bonus_damping": "Post-r103 route-horizon semantics fix that directly damps release and storage-risk blend bonuses on no-risky no-positive-pressure thin wins when a core baseline still has materially stronger raw horizon support.",
    "finite_storage_dynamic_primal_dual_v1_5_r108_reactivated_dual_low_support_core_anchor": "Post-r103 route-horizon semantics fix that gives the shared core baseline a small anchor bonus only when no-risky no-positive-pressure thin wins appear despite materially weaker raw horizon support.",
    "finite_storage_dynamic_primal_dual_v1_5_r109_reactivated_dual_no_positive_pressure_finishable_count_horizon": "Post-r108 route-horizon semantics fix that normalizes finishable credit by positive finishable-movement count only inside no-positive-local-pressure phases that still point into materially pressured downstream routes, reducing raw score inflation from many moderate completion movements.",
    "finite_storage_dynamic_primal_dual_v1_5_r110_reactivated_dual_high_finishable_count_horizon": "Post-r109 route-horizon semantics fix that keeps the no-positive-pressure finishable-count normalization only for genuinely high-count completion phases, avoiding broad score suppression on smaller supported separations.",
    "finite_storage_dynamic_primal_dual_v1_5_r111_reactivated_dual_no_positive_pressure_movement_finishable_power_horizon": "Post-r108 route-horizon semantics fix that only increases finishable-demand concavity for multi-vehicle movements inside no-positive-local-pressure phases with materially pressured downstream routes, targeting raw horizon score inflation from 3-4 vehicle completion movements without flattening whole phases.",
    "finite_storage_dynamic_primal_dual_v1_5_r112_reactivated_dual_no_positive_pressure_big_finishable_count_horizon": "Post-r111 route-horizon semantics fix that additionally normalizes only the multi-vehicle completion movements when a no-positive-local-pressure phase contains multiple such movements, targeting the remaining raw wins driven by two-or-more 3-4 vehicle movements.",
    "finite_storage_dynamic_primal_dual_v1_5_r113_reactivated_dual_no_positive_pressure_multi_big_finishable_power_horizon": "Post-r112 route-horizon semantics fix that further increases finishable-demand concavity only for multi-vehicle completion movements when a no-positive-local-pressure phase contains multiple such movements, directly damping the remaining raw wins driven by high aggregate 3-4 vehicle finishable volume.",
    "finite_storage_dynamic_primal_dual_v1_5_r114_reactivated_dual_supported_big_finishable_sum_horizon": "Post-r92 route-horizon semantics fix that only normalizes multi-vehicle completion credit when a no-positive-local-pressure phase carries a very large aggregate multi-vehicle finishable volume, targeting the high-sum raw wins in the remaining storage-activation bad seed without broadly flattening smaller separations.",
    "full_dual_symbolic": "Per-TLS dual policy where feasible; otherwise explicit not_feasible.",
    "finite_storage_completion_safe_primal_dual_v1_6": "V1.6 completion-safe controller with dual completion-price mechanism and feasible-set filtering.",
}
FINITE_STORAGE_CONTROLLER_IDS = {
    "finite_storage_primal_dual",
    "finite_storage_primal_dual_v1_4_score",
    "finite_storage_dynamic_primal_dual_v1_5",
    "finite_storage_dynamic_primal_dual_v1_5_r2_guarded",
    "finite_storage_dynamic_primal_dual_v1_5_r3_double_release",
    "finite_storage_dynamic_primal_dual_v1_5_r4_release_service",
    "finite_storage_dynamic_primal_dual_v1_5_r5_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r6_terminal_flush",
    "finite_storage_dynamic_primal_dual_v1_5_r7_double_filter",
    "finite_storage_dynamic_primal_dual_v1_5_r8_multi_baseline_filter",
    "finite_storage_dynamic_primal_dual_v1_5_r9_hold_only",
    "finite_storage_dynamic_primal_dual_v1_5_r10_bounded_hold",
    "finite_storage_dynamic_primal_dual_v1_5_r11_completion_risk",
    "finite_storage_dynamic_primal_dual_v1_5_r12_route_completion",
    "finite_storage_dynamic_primal_dual_v1_5_r13_route_demand",
    "finite_storage_dynamic_primal_dual_v1_5_r14_route_demand_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r15_horizon_model",
    "finite_storage_dynamic_primal_dual_v1_5_r16_horizon_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r17_horizon_capacity_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r18_horizon_balanced_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r19_horizon_double_anchored",
    "finite_storage_dynamic_primal_dual_v1_5_r20_horizon_max_double_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r21_horizon_service_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r22_horizon_completion_safety",
    "finite_storage_dynamic_primal_dual_v1_5_r23_horizon_dominance",
    "finite_storage_dynamic_primal_dual_v1_5_r24_staged_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r25_staged_horizon_late_max",
    "finite_storage_dynamic_primal_dual_v1_5_r26_relative_exit_urgency",
    "finite_storage_dynamic_primal_dual_v1_5_r27_terminal_exit_protection",
    "finite_storage_dynamic_primal_dual_v1_5_r28_max_pressure_envelope",
    "finite_storage_dynamic_primal_dual_v1_5_r29_core_baseline_envelope",
    "finite_storage_dynamic_primal_dual_v1_5_r30_double_envelope",
    "finite_storage_dynamic_primal_dual_v1_5_r31_late_double_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r32_preterminal_double_guard",
    "finite_storage_dynamic_primal_dual_v1_5_r33_midcourse_double_guard",
    "finite_storage_dynamic_primal_dual_v1_5_r34_core_minimax_guard",
    "finite_storage_dynamic_primal_dual_v1_5_r35_deadline_urgency",
    "finite_storage_dynamic_primal_dual_v1_5_r36_late_deadline_anchor",
    "finite_storage_dynamic_primal_dual_v1_5_r37_late_deadline_service_anchor",
    "finite_storage_dynamic_primal_dual_v1_5_r38_capacity_rescue_guard",
    "finite_storage_dynamic_primal_dual_v1_5_r39_capacity_score_envelope",
    "finite_storage_dynamic_primal_dual_v1_5_r40_pressure_safe_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r41_terminal_core_completion",
    "finite_storage_dynamic_primal_dual_v1_5_r42_tail_completion_rescue",
    "finite_storage_dynamic_primal_dual_v1_5_r43_staged_pressure_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r44_loose_staged_pressure_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r45_preterminal_pressure_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r46_occupancy_safe_completion",
    "finite_storage_dynamic_primal_dual_v1_5_r47_staged_severe_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r48_pressure_double_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r49_early_pressure_double_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r50_completion_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r51_core_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r52_raw_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r53_post_veto_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r54_reactivated_dual_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r55_reactivated_dual_uncapped_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r56_reactivated_dual_raw_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r57_reactivated_dual_capacity_completion_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r58_reactivated_dual_post_veto_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r59_reactivated_dual_narrow_post_veto_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r60_reactivated_dual_early_capacity_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r61_reactivated_dual_mid_severe_early_capacity_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r62_reactivated_dual_late_severe_raw_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r63_reactivated_dual_native_base_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r64_reactivated_dual_native_base_late_severe_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r65_reactivated_dual_native_capacity_score_rescue",
    "finite_storage_dynamic_primal_dual_v1_5_r66_reactivated_dual_native_horizon_score_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r67_reactivated_dual_native_negative_total_penalty",
    "finite_storage_dynamic_primal_dual_v1_5_r68_reactivated_dual_native_double_horizon_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r69_reactivated_dual_release_biased_native_base",
    "finite_storage_dynamic_primal_dual_v1_5_r70_reactivated_dual_descendant_release_native_base",
    "finite_storage_dynamic_primal_dual_v1_5_r71_reactivated_dual_local_descendant_release_native_base",
    "finite_storage_dynamic_primal_dual_v1_5_r72_reactivated_dual_release_risk_horizon_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r73_reactivated_dual_release_risk_late_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r74_reactivated_dual_negative_total_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r75_reactivated_dual_release_risk_negative_pressure_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r76_reactivated_dual_release_risk_negative_total_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r77_reactivated_dual_conditional_risk_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r78_reactivated_dual_conditional_risk_late_raw_consensus",
    "finite_storage_dynamic_primal_dual_v1_5_r79_reactivated_dual_negative_total_completion_conflict",
    "finite_storage_dynamic_primal_dual_v1_5_r80_reactivated_dual_negative_total_raw_consensus",
    "finite_storage_dynamic_primal_dual_v1_5_r81_reactivated_dual_severe_negative_total_raw_consensus",
    "finite_storage_dynamic_primal_dual_v1_5_r82_reactivated_dual_conditional_low_total_pressure_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r83_reactivated_dual_low_total_consensus_completion",
    "finite_storage_dynamic_primal_dual_v1_5_r84_reactivated_dual_conditional_release_gate",
    "finite_storage_dynamic_primal_dual_v1_5_r85_reactivated_dual_horizon_local_pressure",
    "finite_storage_dynamic_primal_dual_v1_5_r86_reactivated_dual_horizon_zero_slack_floor",
    "finite_storage_dynamic_primal_dual_v1_5_r87_reactivated_dual_low_signal_bonus_gate",
    "finite_storage_dynamic_primal_dual_v1_5_r88_reactivated_dual_low_signal_bonus_scale",
    "finite_storage_dynamic_primal_dual_v1_5_r89_reactivated_dual_low_signal_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r90_reactivated_dual_supported_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r91_reactivated_dual_supported_narrow_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r92_reactivated_dual_supported_score_gap_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r93_reactivated_dual_score_gap_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r94_reactivated_dual_supported_low_total_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r95_reactivated_dual_supported_negative_pressure_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r96_reactivated_dual_unique_movement_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r97_reactivated_dual_unique_residual_power_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r98_reactivated_dual_unique_finishable_power_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r99_reactivated_dual_unique_finishable_ratio_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r100_reactivated_dual_unique_finishable_power_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r101_reactivated_dual_unique_finishable_power_conditional_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r102_reactivated_dual_unique_finishable_power_conditional_pressure_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r103_reactivated_dual_unique_finishable_power_movement_pressure_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r104_reactivated_dual_unique_finishable_power_no_risky_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r105_reactivated_dual_unique_finishable_power_no_risky_nonpositive_pressure_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r106_reactivated_dual_unique_finishable_power_secondary_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r107_reactivated_dual_low_support_bonus_damping",
    "finite_storage_dynamic_primal_dual_v1_5_r108_reactivated_dual_low_support_core_anchor",
    "finite_storage_dynamic_primal_dual_v1_5_r109_reactivated_dual_no_positive_pressure_finishable_count_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r110_reactivated_dual_high_finishable_count_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r111_reactivated_dual_no_positive_pressure_movement_finishable_power_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r112_reactivated_dual_no_positive_pressure_big_finishable_count_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r113_reactivated_dual_no_positive_pressure_multi_big_finishable_power_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r114_reactivated_dual_supported_big_finishable_sum_horizon",
    "finite_storage_completion_safe_primal_dual_v1_6",
}
NETWORKS = {
    "single": {
        "sumocfg": Path("networks/single_intersection/single_intersection.sumocfg"),
        "net_file": Path("networks/single_intersection/single_intersection.net.xml"),
    },
    "arterial": {
        "sumocfg": Path("networks/arterial/arterial.sumocfg"),
        "net_file": Path("networks/arterial/arterial.net.xml"),
    },
    "grid_4x4": {
        "sumocfg": Path("networks/grid_4x4/grid_4x4.sumocfg"),
        "net_file": Path("networks/grid_4x4/grid_4x4.net.xml"),
    },
}
NOT_FEASIBLE_CONTROLLERS = {
    "local_pilight": "No safely adaptable PI-Light local DSL baseline is present in the SUMO runner interface.",
    "full_dual_symbolic": "Closed-loop per-TLS dual Scenario conversion is not yet safe for live SUMO actuation.",
}
CLAIM_FRAMING = (
    "Phase 3 selected pressure-equivalent; Phase 4 outputs are closed-loop SUMO evidence "
    "for generalized-pressure symbolic recovery, not universal dominance over pressure."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", choices=sorted(NETWORKS), default="single")
    parser.add_argument("--controllers", nargs="+", default=list(CONTROLLER_REGISTRY))
    parser.add_argument("--seeds", nargs="+", type=int, default=[20260523])
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--warmup", type=int, default=60)
    parser.add_argument("--action-interval", type=int, default=10)
    parser.add_argument("--out", default="experiments/dual_sensitivity/block4_closed_loop_smoke.json")
    parser.add_argument("--route-json", default="experiments/dual_sensitivity/block3_static_kill_gate.json")
    parser.add_argument("--scenario-tag", default="single_sanity")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    unknown = sorted(set(args.controllers) - set(CONTROLLER_REGISTRY))
    if unknown:
        raise ValueError(f"Unknown controllers: {unknown}. Available: {sorted(CONTROLLER_REGISTRY)}")
    if args.steps <= 0 or args.warmup < 0 or args.action_interval <= 0:
        raise ValueError("--steps and --action-interval must be positive; --warmup must be nonnegative")
    if not args.seeds:
        raise ValueError("At least one seed is required")


def load_route_metadata(route_json: Path) -> dict[str, str]:
    payload = json.loads(route_json.read_text(encoding="utf-8"))
    route_decision = payload.get("route_decision")
    if not route_decision:
        raise ValueError(f"Route JSON {route_json} is missing route_decision")
    return {
        "route_decision": str(route_decision),
        "route_confidence": str(payload.get("route_confidence", "UNKNOWN")),
        "route_json": str(route_json),
    }


def resolve_network(network: str) -> dict[str, Path]:
    resolved = NETWORKS[network]
    for path in resolved.values():
        if not path.exists():
            raise FileNotFoundError(path)
    return resolved


def read_tls_phase_states(net_file: Path) -> dict[str, list[str]]:
    root = ET.parse(net_file).getroot()
    phase_states: dict[str, list[str]] = {}
    for tls_logic in root.findall("tlLogic"):
        tls_id = tls_logic.get("id")
        if tls_id:
            phase_states[tls_id] = [phase.get("state", "") for phase in tls_logic.findall("phase")]
    return phase_states


def read_tls_link_movements(net_file: Path) -> dict[str, list[tuple[str, str]]]:
    root = ET.parse(net_file).getroot()
    indexed: dict[str, dict[int, tuple[str, str]]] = {}
    for conn in root.findall("connection"):
        tls_id = conn.get("tl")
        link_index = conn.get("linkIndex")
        from_edge = conn.get("from")
        to_edge = conn.get("to")
        if not tls_id or link_index is None or not from_edge or not to_edge:
            continue
        if from_edge.startswith(":") or to_edge.startswith(":"):
            continue
        indexed.setdefault(tls_id, {})[int(link_index)] = (from_edge, to_edge)
    return {tls: [moves[idx] for idx in sorted(moves)] for tls, moves in indexed.items()}


def read_edge_speeds(net_file: Path) -> dict[str, float]:
    root = ET.parse(net_file).getroot()
    speeds: dict[str, float] = {}
    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        if not edge_id or edge_id.startswith(":"):
            continue
        lane = edge.find("lane")
        if lane is not None and lane.get("speed") is not None:
            speeds[edge_id] = float(lane.get("speed", "13.89"))
    return speeds


def read_edge_free_flow_times(net_file: Path) -> dict[str, float]:
    root = ET.parse(net_file).getroot()
    times: dict[str, float] = {}
    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        if not edge_id or edge_id.startswith(":"):
            continue
        lane = edge.find("lane")
        if lane is None:
            continue
        length = max(float(lane.get("length", "1.0")), 1.0)
        speed = max(float(lane.get("speed", "13.89")), 0.1)
        times[edge_id] = float(length / speed)
    return times


def green_phases(states: list[str]) -> list[int]:
    greens = [idx for idx, state in enumerate(states) if any(ch in "Gg" for ch in state)]
    return greens or list(range(len(states)))


def movement_score(
    controller: str,
    movement: tuple[str, str],
    queues: dict[str, float],
    capacities: dict[str, float],
    seed: int = 0,
    vehicle_counts: dict[str, float] | None = None,
) -> float:
    if controller not in CONTROLLER_REGISTRY:
        raise ValueError(f"Unknown controller: {controller}. Available: {sorted(CONTROLLER_REGISTRY)}")
    upstream, downstream = movement
    up_q = float(queues.get(upstream, 0.0))
    down_q = float(queues.get(downstream, 0.0))
    pressure = up_q - down_q
    if controller in {"max_pressure", "raw_neighbor_symbolic"}:
        return pressure
    if controller == "actuated_local_pressure":
        return up_q if sum(queues.values()) >= 1.0 else 0.0
    if controller in {"capacity_aware_pressure", "occupancy_capacity_aware_pressure", "all_neighbor_symbolic", "finite_storage_double_pressure"}:
        cap = max(float(capacities.get(downstream, 1.0)), 1.0)
        downstream_storage = float((vehicle_counts or queues).get(downstream, 0.0)) if controller == "occupancy_capacity_aware_pressure" else down_q
        fullness = downstream_storage / cap
        slack = cap - downstream_storage
        blocked_penalty = cap if fullness >= 0.85 else 0.0
        double_pressure = max(up_q - max(slack, 0.0), 0.0) if controller == "finite_storage_double_pressure" else 0.0
        return pressure + 0.05 * slack - fullness * up_q - blocked_penalty - double_pressure
    if controller == "random_permuted_dual":
        key = sum(ord(ch) for ch in upstream + downstream) + int(seed)
        return pressure * (1.0 if key % 2 == 0 else -0.5)
    return 0.0


FINITE_STORAGE_DECOMPOSITION_FIELDS = {
    "pressure",
    "downstream_storage",
    "spillback",
    "switching",
    "service",
    "incident",
    "total",
}
SERVICE_URGENCY_NEUTRAL_THRESHOLD = 0.85
MIN_SWITCHING_HOLD_TIME = 10.0
DYNAMIC_V1_5_PARAMS = {
    "storage_threshold": 0.72,
    "release_threshold": 0.70,
    "dual_step_size": 0.85,
    "release_step_size": 0.55,
    "dual_decay": 0.12,
    "alpha_release": 0.70,
    "beta_storage": 1.20,
    "gamma_cascade": 0.85,
    "delta_service": 0.35,
}
DYNAMIC_V1_6_PARAMS = {
    # Inherit v1.5 base parameters
    "storage_threshold": 0.72,
    "release_threshold": 0.70,
    "dual_step_size": 0.85,
    "release_step_size": 0.55,
    "dual_decay": 0.12,
    "alpha_release": 0.70,
    "beta_storage": 1.20,
    "gamma_cascade": 0.85,
    "delta_service": 0.35,
    # v1.6 completion parameters
    "nu_decay": 0.15,
    "nu_step_size": 0.80,
    "completion_deficit_threshold": 0.60,
    "completion_horizon_fraction": 0.70,
    "completion_safe_margin": 0.10,
    "kappa_completion": 1.00,
    "eta_completion": 0.50,
}
DYNAMIC_V1_5_R2_GUARDED_PARAMS = {
    "storage_threshold": 0.76,
    "release_threshold": 0.76,
    "dual_step_size": 0.55,
    "release_step_size": 0.35,
    "dual_decay": 0.18,
    "alpha_release": 0.45,
    "beta_storage": 0.70,
    "gamma_cascade": 0.45,
    "delta_service": 0.25,
    "correction_cap_ratio": 0.40,
    "correction_cap_floor": 3.0,
}
DYNAMIC_V1_5_R3_DOUBLE_RELEASE_PARAMS = {
    "storage_threshold": 0.78,
    "release_threshold": 0.72,
    "dual_step_size": 0.45,
    "release_step_size": 0.45,
    "dual_decay": 0.16,
    "alpha_release": 0.55,
    "beta_storage": 0.20,
    "gamma_cascade": 0.15,
    "delta_service": 0.40,
    "base_score_variant": "finite_storage_double_scaffold",
    "correction_cap_ratio": 0.25,
    "correction_cap_floor": 4.0,
}
DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS = {
    "storage_threshold": 0.80,
    "release_threshold": 0.72,
    "dual_step_size": 0.0,
    "release_step_size": 0.50,
    "dual_decay": 0.18,
    "alpha_release": 0.40,
    "beta_storage": 0.0,
    "gamma_cascade": 0.0,
    "delta_service": 0.55,
    "base_score_variant": "finite_storage_double_scaffold",
}
DYNAMIC_V1_5_R5_DOUBLE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS,
    "double_safety_fallback": 1.0,
}
DYNAMIC_V1_5_R6_TERMINAL_FLUSH_PARAMS = {
    **DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS,
    "terminal_flush_start_fraction": 0.70,
}
DYNAMIC_V1_5_R7_DOUBLE_FILTER_PARAMS = {
    **DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS,
    "double_score_safety_filter": 1.0,
    "double_score_safety_tolerance": 0.0,
}
DYNAMIC_V1_5_R8_MULTI_BASELINE_FILTER_PARAMS = {
    **DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS,
    "multi_baseline_safety_filter": 1.0,
    "baseline_score_safety_tolerance": 0.0,
}
DYNAMIC_V1_5_R9_HOLD_ONLY_PARAMS = {
    **DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS,
    "hold_only_safety_filter": 1.0,
}
DYNAMIC_V1_5_R10_BOUNDED_HOLD_PARAMS = {
    **DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS,
    "hold_only_safety_filter": 1.0,
    "max_dynamic_hold_time": 20.0,
}
DYNAMIC_V1_5_R11_COMPLETION_RISK_PARAMS = {
    **DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS,
    "completion_risk_filter": 1.0,
    "completion_risk_start_fraction": 0.45,
    "completion_risk_queue_threshold": 8.0,
    "completion_risk_occupancy_threshold": 0.70,
    "completion_service_tolerance": 0.0,
}
DYNAMIC_V1_5_R12_ROUTE_COMPLETION_PARAMS = {
    **DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS,
    "route_completion_prediction_filter": 1.0,
    "completion_risk_filter": 1.0,
    "completion_risk_start_fraction": 0.0,
    "completion_risk_queue_threshold": 6.0,
    "completion_risk_occupancy_threshold": 0.62,
    "route_completion_slack_floor": 0.05,
    "route_completion_occupancy_penalty": 0.25,
}
DYNAMIC_V1_5_R13_ROUTE_DEMAND_PARAMS = {
    **DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS,
    "route_demand_completion_filter": 1.0,
    "completion_risk_filter": 1.0,
    "completion_risk_start_fraction": 0.0,
    "completion_risk_queue_threshold": 4.0,
    "completion_risk_occupancy_threshold": 0.60,
    "route_demand_slack_floor": 0.02,
    "route_demand_queue_blend": 0.10,
    "route_demand_downstream_penalty": 0.30,
}
DYNAMIC_V1_5_R14_ROUTE_DEMAND_DOUBLE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R13_ROUTE_DEMAND_PARAMS,
    "route_demand_double_score_veto": 1.0,
    "route_demand_double_score_tolerance": 0.0,
}
DYNAMIC_V1_5_R15_HORIZON_MODEL_PARAMS = {
    **DYNAMIC_V1_5_R13_ROUTE_DEMAND_PARAMS,
    "route_demand_completion_filter": 0.0,
    "route_horizon_completion_filter": 1.0,
    "route_horizon_slack_floor": 0.02,
    "route_horizon_time_discount": 1.0,
    "route_horizon_downstream_penalty": 0.25,
    "route_horizon_double_blend": 0.35,
    "route_horizon_pressure_blend": 0.10,
}
DYNAMIC_V1_5_R16_HORIZON_TERMINAL_PARAMS = {
    **DYNAMIC_V1_5_R15_HORIZON_MODEL_PARAMS,
    "terminal_flush_start_fraction": 0.82,
    "terminal_flush_locks_dynamic": 1.0,
}
DYNAMIC_V1_5_R17_HORIZON_CAPACITY_TERMINAL_PARAMS = {
    **DYNAMIC_V1_5_R15_HORIZON_MODEL_PARAMS,
    "terminal_flush_start_fraction": 0.82,
    "terminal_flush_locks_dynamic": 1.0,
    "terminal_flush_action": "capacity_aware",
}
DYNAMIC_V1_5_R18_HORIZON_BALANCED_TERMINAL_PARAMS = {
    **DYNAMIC_V1_5_R15_HORIZON_MODEL_PARAMS,
    "terminal_flush_start_fraction": 0.82,
    "terminal_flush_locks_dynamic": 1.0,
    "terminal_flush_action": "balanced_capacity_double",
}
DYNAMIC_V1_5_R19_HORIZON_DOUBLE_ANCHORED_PARAMS = {
    **DYNAMIC_V1_5_R16_HORIZON_TERMINAL_PARAMS,
    "route_horizon_double_blend": 0.85,
    "route_horizon_pressure_blend": 0.05,
    "terminal_flush_start_fraction": 0.78,
}
DYNAMIC_V1_5_R20_HORIZON_MAX_DOUBLE_TERMINAL_PARAMS = {
    **DYNAMIC_V1_5_R15_HORIZON_MODEL_PARAMS,
    "route_horizon_double_blend": 0.75,
    "route_horizon_pressure_blend": 0.20,
    "terminal_flush_start_fraction": 0.78,
    "terminal_flush_locks_dynamic": 1.0,
    "terminal_flush_action": "balanced_max_double",
}
DYNAMIC_V1_5_R21_HORIZON_SERVICE_TERMINAL_PARAMS = {
    **DYNAMIC_V1_5_R15_HORIZON_MODEL_PARAMS,
    "route_horizon_double_blend": 0.75,
    "route_horizon_pressure_blend": 0.15,
    "terminal_flush_start_fraction": 0.78,
    "terminal_flush_locks_dynamic": 1.0,
    "terminal_flush_action": "completion_service_max_double",
}
DYNAMIC_V1_5_R22_HORIZON_COMPLETION_SAFETY_PARAMS = {
    **DYNAMIC_V1_5_R19_HORIZON_DOUBLE_ANCHORED_PARAMS,
    "completion_safety_veto": 1.0,
    "completion_safety_service_blend": 1.0,
    "completion_safety_tolerance": 0.0,
}
DYNAMIC_V1_5_R23_HORIZON_DOMINANCE_PARAMS = {
    **DYNAMIC_V1_5_R19_HORIZON_DOUBLE_ANCHORED_PARAMS,
    "route_horizon_baseline_dominance_filter": 1.0,
    "route_horizon_baseline_margin": 0.12,
}
DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R19_HORIZON_DOUBLE_ANCHORED_PARAMS,
    "completion_risk_start_fraction": 0.55,
    "completion_risk_queue_threshold": 1.0e9,
    "completion_risk_occupancy_threshold": 1.01,
}
DYNAMIC_V1_5_R25_STAGED_HORIZON_LATE_MAX_PARAMS = {
    **DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS,
    "terminal_flush_start_fraction": 0.88,
    "terminal_flush_action": "max_pressure",
}
DYNAMIC_V1_5_R26_RELATIVE_EXIT_URGENCY_PARAMS = {
    **DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS,
    "route_horizon_relative_time_urgency": 1.0,
    "route_horizon_urgency_power": 2.0,
}
DYNAMIC_V1_5_R27_TERMINAL_EXIT_PROTECTION_PARAMS = {
    **DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS,
    "terminal_flush_start_fraction": 1.10,
    "terminal_exit_protection_guard": 1.0,
    "terminal_exit_guard_start_fraction": 0.78,
    "terminal_exit_guard_horizon_blend": 2.0,
    "terminal_exit_guard_service_blend": 1.0,
    "terminal_exit_guard_double_blend": 0.25,
    "terminal_exit_guard_capacity_blend": 0.25,
    "terminal_exit_guard_pressure_blend": 0.10,
}
DYNAMIC_V1_5_R28_MAX_PRESSURE_ENVELOPE_PARAMS = {
    **DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS,
    "route_horizon_max_pressure_envelope": 1.0,
    "route_horizon_max_pressure_margin": 0.10,
    "route_horizon_max_pressure_service_blend": 0.50,
}
DYNAMIC_V1_5_R29_CORE_BASELINE_ENVELOPE_PARAMS = {
    **DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS,
    "route_horizon_core_baseline_envelope": 1.0,
    "route_horizon_core_baseline_margin": 0.10,
    "route_horizon_core_baseline_service_blend": 0.50,
}
DYNAMIC_V1_5_R30_DOUBLE_ENVELOPE_PARAMS = {
    **DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS,
    "route_horizon_double_pressure_envelope": 1.0,
    "route_horizon_double_pressure_margin": 0.10,
    "route_horizon_double_pressure_service_blend": 0.50,
}
DYNAMIC_V1_5_R31_LATE_DOUBLE_TERMINAL_PARAMS = {
    **DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS,
    "terminal_flush_start_fraction": 0.88,
}
DYNAMIC_V1_5_R32_PRETERMINAL_DOUBLE_GUARD_PARAMS = {
    **DYNAMIC_V1_5_R31_LATE_DOUBLE_TERMINAL_PARAMS,
    "route_horizon_double_pressure_envelope": 1.0,
    "route_horizon_double_pressure_margin": 0.0,
    "route_horizon_double_pressure_service_blend": 0.50,
    "route_horizon_double_pressure_envelope_start_fraction": 0.82,
}
DYNAMIC_V1_5_R33_MIDCOURSE_DOUBLE_GUARD_PARAMS = {
    **DYNAMIC_V1_5_R32_PRETERMINAL_DOUBLE_GUARD_PARAMS,
    "route_horizon_double_pressure_envelope_start_fraction": 0.70,
}
DYNAMIC_V1_5_R34_CORE_MINIMAX_GUARD_PARAMS = {
    **DYNAMIC_V1_5_R31_LATE_DOUBLE_TERMINAL_PARAMS,
    "route_horizon_core_minimax_guard": 1.0,
    "route_horizon_core_minimax_start_fraction": 0.70,
    "route_horizon_core_minimax_horizon_blend": 0.50,
    "route_horizon_core_minimax_service_blend": 0.50,
}
DYNAMIC_V1_5_R35_DEADLINE_URGENCY_PARAMS = {
    **DYNAMIC_V1_5_R31_LATE_DOUBLE_TERMINAL_PARAMS,
    "route_horizon_deadline_time_urgency": 1.0,
    "route_horizon_urgency_power": 2.0,
    "route_horizon_deadline_base_weight": 0.05,
}
DYNAMIC_V1_5_R36_LATE_DEADLINE_ANCHOR_PARAMS = {
    **DYNAMIC_V1_5_R35_DEADLINE_URGENCY_PARAMS,
    "completion_risk_start_fraction": 0.78,
    "route_horizon_deadline_base_weight": 0.25,
}
DYNAMIC_V1_5_R37_LATE_DEADLINE_SERVICE_ANCHOR_PARAMS = {
    **DYNAMIC_V1_5_R36_LATE_DEADLINE_ANCHOR_PARAMS,
    "route_horizon_service_blend": 0.35,
}
DYNAMIC_V1_5_R38_CAPACITY_RESCUE_GUARD_PARAMS = {
    **DYNAMIC_V1_5_R36_LATE_DEADLINE_ANCHOR_PARAMS,
    "route_horizon_capacity_rescue_guard": 1.0,
    "route_horizon_capacity_rescue_start_fraction": 0.78,
    "route_horizon_capacity_rescue_margin": 0.0,
    "route_horizon_capacity_rescue_service_blend": 0.25,
    "route_horizon_capacity_rescue_double_tolerance": 0.25,
}
DYNAMIC_V1_5_R39_CAPACITY_SCORE_ENVELOPE_PARAMS = {
    **DYNAMIC_V1_5_R36_LATE_DEADLINE_ANCHOR_PARAMS,
    "route_horizon_capacity_score_envelope": 1.0,
    "route_horizon_capacity_score_margin": 0.0,
}
DYNAMIC_V1_5_R40_PRESSURE_SAFE_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R36_LATE_DEADLINE_ANCHOR_PARAMS,
    "route_horizon_pressure_safe_guard": 1.0,
    "route_horizon_pressure_safe_min_completion_gain": 0.0,
    "route_horizon_pressure_safe_capacity_tolerance": 0.20,
    "route_horizon_pressure_safe_double_tolerance": 0.20,
}
DYNAMIC_V1_5_R41_TERMINAL_CORE_COMPLETION_PARAMS = {
    **DYNAMIC_V1_5_R40_PRESSURE_SAFE_HORIZON_PARAMS,
    "terminal_flush_start_fraction": 0.88,
    "terminal_flush_locks_dynamic": 1.0,
    "terminal_flush_action": "core_completion",
    "terminal_core_completion_horizon_blend": 1.0,
    "terminal_core_completion_service_blend": 0.25,
    "terminal_core_completion_core_blend": 0.15,
}
DYNAMIC_V1_5_R42_TAIL_COMPLETION_RESCUE_PARAMS = {
    **DYNAMIC_V1_5_R40_PRESSURE_SAFE_HORIZON_PARAMS,
    "route_horizon_tail_completion_rescue": 1.0,
    "route_horizon_tail_rescue_start_fraction": 0.86,
    "route_horizon_tail_rescue_min_completion_gain": 0.20,
    "route_horizon_tail_rescue_service_blend": 0.35,
    "route_horizon_tail_rescue_core_tolerance": 1.0,
}
DYNAMIC_V1_5_R43_STAGED_PRESSURE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS,
    "route_horizon_pressure_safe_guard": 1.0,
    "route_horizon_pressure_safe_min_completion_gain": 0.0,
    "route_horizon_pressure_safe_capacity_tolerance": 0.20,
    "route_horizon_pressure_safe_double_tolerance": 0.20,
}
DYNAMIC_V1_5_R44_LOOSE_STAGED_PRESSURE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R43_STAGED_PRESSURE_SAFE_PARAMS,
    "route_horizon_pressure_safe_min_completion_gain": 0.05,
    "route_horizon_pressure_safe_capacity_tolerance": 0.50,
    "route_horizon_pressure_safe_double_tolerance": 0.50,
}
DYNAMIC_V1_5_R45_PRETERMINAL_PRESSURE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R43_STAGED_PRESSURE_SAFE_PARAMS,
    "route_horizon_pressure_safe_start_fraction": 0.70,
}
DYNAMIC_V1_5_R46_OCCUPANCY_SAFE_COMPLETION_PARAMS = {
    **DYNAMIC_V1_5_R45_PRETERMINAL_PRESSURE_SAFE_PARAMS,
    "completion_safety_veto": 1.0,
    "completion_safety_service_blend": 0.35,
    "completion_safety_tolerance": 0.05,
    "completion_safety_start_fraction": 0.70,
    "completion_safety_occupancy_threshold": 0.85,
    "completion_safety_residual_threshold": 0.20,
}
DYNAMIC_V1_5_R47_STAGED_SEVERE_DOUBLE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R45_PRETERMINAL_PRESSURE_SAFE_PARAMS,
    "route_horizon_severe_double_guard": 1.0,
    "route_horizon_severe_double_start_fraction": 0.60,
    "route_horizon_severe_double_occupancy_threshold": 0.80,
    "route_horizon_severe_double_residual_threshold": 0.25,
    "route_horizon_severe_double_service_blend": 0.35,
    "route_horizon_severe_double_max_completion_advantage": 0.15,
    "route_horizon_severe_double_capacity_tolerance": 1.0,
    "completion_safety_veto": 1.0,
    "completion_safety_service_blend": 0.35,
    "completion_safety_tolerance": 0.05,
    "completion_safety_start_fraction": 0.85,
    "completion_safety_occupancy_threshold": 0.92,
    "completion_safety_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R48_PRESSURE_DOUBLE_CONFLICT_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R46_OCCUPANCY_SAFE_COMPLETION_PARAMS,
    "route_horizon_pressure_double_conflict_guard": 1.0,
    "route_horizon_pressure_double_conflict_start_fraction": 0.60,
    "route_horizon_pressure_double_conflict_occupancy_threshold": 0.80,
    "route_horizon_pressure_double_conflict_residual_threshold": 0.25,
}
DYNAMIC_V1_5_R49_EARLY_PRESSURE_DOUBLE_CONFLICT_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R48_PRESSURE_DOUBLE_CONFLICT_SAFE_PARAMS,
    "route_horizon_pressure_double_conflict_start_fraction": 0.0,
}
DYNAMIC_V1_5_R50_COMPLETION_CONFLICT_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R49_EARLY_PRESSURE_DOUBLE_CONFLICT_SAFE_PARAMS,
    "route_horizon_completion_conflict_guard": 1.0,
    "route_horizon_completion_conflict_start_fraction": 0.0,
    "route_horizon_completion_conflict_occupancy_threshold": 0.90,
    "route_horizon_completion_conflict_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R51_CORE_CONSENSUS_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R50_COMPLETION_CONFLICT_SAFE_PARAMS,
    "route_horizon_core_consensus_guard": 1.0,
    "route_horizon_core_consensus_start_fraction": 0.0,
    "route_horizon_core_consensus_occupancy_threshold": 0.90,
    "route_horizon_core_consensus_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R52_RAW_CONSENSUS_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R50_COMPLETION_CONFLICT_SAFE_PARAMS,
    "route_horizon_raw_consensus_guard": 1.0,
    "route_horizon_raw_consensus_start_fraction": 0.0,
    "route_horizon_raw_consensus_occupancy_threshold": 0.90,
    "route_horizon_raw_consensus_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R53_POST_VETO_DOUBLE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R50_COMPLETION_CONFLICT_SAFE_PARAMS,
    "post_completion_veto_double_conflict_guard": 1.0,
    "post_completion_veto_double_conflict_occupancy_threshold": 0.90,
    "post_completion_veto_double_conflict_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R54_REACTIVATED_DUAL_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R50_COMPLETION_CONFLICT_SAFE_PARAMS,
    "storage_threshold": 0.78,
    "release_threshold": 0.72,
    "dual_step_size": 0.45,
    "release_step_size": 0.45,
    "dual_decay": 0.16,
    "alpha_release": 0.55,
    "beta_storage": 0.20,
    "gamma_cascade": 0.15,
    "delta_service": 0.40,
    "correction_cap_ratio": 0.25,
    "correction_cap_floor": 4.0,
}
DYNAMIC_V1_5_R55_REACTIVATED_DUAL_UNCAPPED_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R54_REACTIVATED_DUAL_SAFE_PARAMS,
}
DYNAMIC_V1_5_R55_REACTIVATED_DUAL_UNCAPPED_SAFE_PARAMS.pop("correction_cap_ratio", None)
DYNAMIC_V1_5_R55_REACTIVATED_DUAL_UNCAPPED_SAFE_PARAMS.pop("correction_cap_floor", None)
DYNAMIC_V1_5_R56_REACTIVATED_DUAL_RAW_CONSENSUS_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R55_REACTIVATED_DUAL_UNCAPPED_SAFE_PARAMS,
    "route_horizon_raw_consensus_guard": 1.0,
    "route_horizon_raw_consensus_start_fraction": 0.0,
    "route_horizon_raw_consensus_occupancy_threshold": 0.90,
    "route_horizon_raw_consensus_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R57_REACTIVATED_DUAL_CAPACITY_COMPLETION_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R56_REACTIVATED_DUAL_RAW_CONSENSUS_SAFE_PARAMS,
    "route_horizon_capacity_completion_conflict_guard": 1.0,
    "route_horizon_capacity_completion_conflict_occupancy_threshold": 0.90,
    "route_horizon_capacity_completion_conflict_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R58_REACTIVATED_DUAL_POST_VETO_DOUBLE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R56_REACTIVATED_DUAL_RAW_CONSENSUS_SAFE_PARAMS,
    "post_completion_veto_double_conflict_guard": 1.0,
    "post_completion_veto_double_conflict_occupancy_threshold": 0.90,
    "post_completion_veto_double_conflict_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R59_REACTIVATED_DUAL_NARROW_POST_VETO_DOUBLE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R56_REACTIVATED_DUAL_RAW_CONSENSUS_SAFE_PARAMS,
    "post_completion_veto_double_conflict_guard": 1.0,
    "post_completion_veto_double_conflict_occupancy_threshold": 0.90,
    "post_completion_veto_double_conflict_residual_threshold": 0.10,
    "post_completion_veto_double_conflict_require_no_completion_filter": 1.0,
    "post_completion_veto_double_conflict_require_capacity_consensus": 1.0,
}
DYNAMIC_V1_5_R60_REACTIVATED_DUAL_EARLY_CAPACITY_CONFLICT_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R59_REACTIVATED_DUAL_NARROW_POST_VETO_DOUBLE_SAFE_PARAMS,
    "route_horizon_early_capacity_completion_conflict_guard": 1.0,
    "route_horizon_early_capacity_completion_conflict_start_fraction": 0.0,
    "route_horizon_early_capacity_completion_conflict_end_fraction": 0.08,
    "route_horizon_early_capacity_completion_conflict_occupancy_threshold": 0.90,
    "route_horizon_early_capacity_completion_conflict_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R61_REACTIVATED_DUAL_MID_SEVERE_EARLY_CAPACITY_CONFLICT_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R59_REACTIVATED_DUAL_NARROW_POST_VETO_DOUBLE_SAFE_PARAMS,
    "route_horizon_early_capacity_completion_conflict_guard": 1.0,
    "route_horizon_early_capacity_completion_conflict_start_fraction": 0.03,
    "route_horizon_early_capacity_completion_conflict_end_fraction": 0.04,
    "route_horizon_early_capacity_completion_conflict_occupancy_threshold": 0.90,
    "route_horizon_early_capacity_completion_conflict_occupancy_upper_threshold": 1.45,
    "route_horizon_early_capacity_completion_conflict_residual_threshold": 0.10,
}
DYNAMIC_V1_5_R62_REACTIVATED_DUAL_LATE_SEVERE_RAW_CONSENSUS_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R59_REACTIVATED_DUAL_NARROW_POST_VETO_DOUBLE_SAFE_PARAMS,
    "route_horizon_raw_consensus_start_fraction": 0.45,
    "route_horizon_raw_consensus_occupancy_threshold": 1.10,
    "route_horizon_raw_consensus_residual_threshold": 0.0,
}
DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R59_REACTIVATED_DUAL_NARROW_POST_VETO_DOUBLE_SAFE_PARAMS,
}
DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS.pop("base_score_variant", None)
DYNAMIC_V1_5_R64_REACTIVATED_DUAL_NATIVE_BASE_LATE_SEVERE_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS,
    "route_horizon_raw_consensus_start_fraction": 0.45,
    "route_horizon_raw_consensus_occupancy_threshold": 1.10,
    "route_horizon_raw_consensus_residual_threshold": 0.0,
}
DYNAMIC_V1_5_R65_REACTIVATED_DUAL_NATIVE_CAPACITY_SCORE_RESCUE_PARAMS = {
    **DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS,
    "route_horizon_native_capacity_score_rescue_guard": 1.0,
    "route_horizon_native_capacity_score_rescue_occupancy_threshold": 1.10,
    "route_horizon_native_capacity_score_rescue_residual_threshold": 0.0,
    "route_horizon_native_capacity_score_rescue_min_total_gap": 5.0,
    "route_horizon_native_capacity_score_rescue_selected_total_ceiling": -40.0,
}
DYNAMIC_V1_5_R66_REACTIVATED_DUAL_NATIVE_HORIZON_SCORE_BLEND_PARAMS = {
    **DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS,
    "route_horizon_double_blend": 0.0,
    "route_horizon_pressure_blend": 0.15,
    "route_horizon_native_score_blend": 1.0,
}
DYNAMIC_V1_5_R67_REACTIVATED_DUAL_NATIVE_NEGATIVE_TOTAL_PENALTY_PARAMS = {
    **DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS,
    "route_horizon_native_negative_total_penalty": 0.04,
}
DYNAMIC_V1_5_R68_REACTIVATED_DUAL_NATIVE_DOUBLE_HORIZON_BLEND_PARAMS = {
    **DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS,
    "route_horizon_double_blend": 0.25,
    "route_horizon_pressure_blend": 0.10,
    "route_horizon_native_score_blend": 1.25,
}
DYNAMIC_V1_5_R69_REACTIVATED_DUAL_RELEASE_BIASED_NATIVE_BASE_PARAMS = {
    **DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS,
    "release_threshold": 0.65,
    "release_step_size": 0.70,
    "dual_decay": 0.12,
    "alpha_release": 0.90,
    "beta_storage": 0.16,
    "gamma_cascade": 0.10,
}
DYNAMIC_V1_5_R70_REACTIVATED_DUAL_DESCENDANT_RELEASE_NATIVE_BASE_PARAMS = {
    **DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS,
    "release_descendant_slack_depth": 2.0,
    "release_descendant_slack_threshold": 0.05,
}
DYNAMIC_V1_5_R71_REACTIVATED_DUAL_LOCAL_DESCENDANT_RELEASE_NATIVE_BASE_PARAMS = {
    **DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS,
    "release_descendant_slack_depth": 2.0,
    "release_descendant_slack_threshold": 0.05,
    "release_local_child_slack_floor": 0.05,
    "release_descendant_support_weight": 0.35,
    "release_descendant_occupancy_threshold": 0.90,
}
DYNAMIC_V1_5_R72_REACTIVATED_DUAL_RELEASE_RISK_HORIZON_BLEND_PARAMS = {
    **DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS,
    "route_horizon_release_component_blend": 1.0,
    "route_horizon_storage_risk_component_blend": 1.0,
}
DYNAMIC_V1_5_R73_REACTIVATED_DUAL_RELEASE_RISK_LATE_CONFLICT_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R72_REACTIVATED_DUAL_RELEASE_RISK_HORIZON_BLEND_PARAMS,
    "route_horizon_completion_conflict_start_fraction": 0.10,
    "route_horizon_completion_conflict_occupancy_threshold": 1.10,
    "route_horizon_completion_conflict_residual_threshold": 0.0,
    "route_horizon_pressure_safe_start_fraction": 0.78,
    "route_horizon_pressure_safe_min_completion_gain": 0.05,
}
DYNAMIC_V1_5_R74_REACTIVATED_DUAL_NEGATIVE_TOTAL_CONSENSUS_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R73_REACTIVATED_DUAL_RELEASE_RISK_LATE_CONFLICT_SAFE_PARAMS,
    "route_horizon_negative_total_core_consensus_guard": 1.0,
    "route_horizon_negative_total_core_consensus_occupancy_threshold": 1.05,
    "route_horizon_negative_total_core_consensus_residual_threshold": 0.0,
    "route_horizon_negative_total_core_consensus_total_ceiling": -5.0,
}
DYNAMIC_V1_5_R75_REACTIVATED_DUAL_RELEASE_RISK_NEGATIVE_PRESSURE_BLEND_PARAMS = {
    **DYNAMIC_V1_5_R73_REACTIVATED_DUAL_RELEASE_RISK_LATE_CONFLICT_SAFE_PARAMS,
    "route_horizon_negative_pressure_component_blend": 2.0,
}
DYNAMIC_V1_5_R76_REACTIVATED_DUAL_RELEASE_RISK_NEGATIVE_TOTAL_BLEND_PARAMS = {
    **DYNAMIC_V1_5_R75_REACTIVATED_DUAL_RELEASE_RISK_NEGATIVE_PRESSURE_BLEND_PARAMS,
    "route_horizon_negative_total_component_blend": 1.0,
}
DYNAMIC_V1_5_R77_REACTIVATED_DUAL_CONDITIONAL_RISK_BLEND_PARAMS = {
    **DYNAMIC_V1_5_R75_REACTIVATED_DUAL_RELEASE_RISK_NEGATIVE_PRESSURE_BLEND_PARAMS,
    "route_horizon_negative_total_component_blend": 2.0,
    "route_horizon_conditional_risk_penalty": 1.0,
    "route_horizon_conditional_risk_start_fraction": 0.0,
    "route_horizon_conditional_risk_end_fraction": 0.25,
    "route_horizon_conditional_risk_occupancy_threshold": 1.05,
    "route_horizon_conditional_risk_residual_threshold": 0.0,
}
DYNAMIC_V1_5_R78_REACTIVATED_DUAL_CONDITIONAL_RISK_LATE_RAW_CONSENSUS_PARAMS = {
    **DYNAMIC_V1_5_R77_REACTIVATED_DUAL_CONDITIONAL_RISK_BLEND_PARAMS,
    "route_horizon_raw_consensus_start_fraction": 0.45,
    "route_horizon_raw_consensus_occupancy_threshold": 1.10,
    "route_horizon_raw_consensus_residual_threshold": 0.0,
}
DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS = {
    **DYNAMIC_V1_5_R78_REACTIVATED_DUAL_CONDITIONAL_RISK_LATE_RAW_CONSENSUS_PARAMS,
    "route_horizon_negative_total_completion_conflict_guard": 1.0,
    "route_horizon_negative_total_completion_conflict_occupancy_threshold": 0.90,
    "route_horizon_negative_total_completion_conflict_residual_threshold": 0.0,
    "route_horizon_negative_total_completion_conflict_total_ceiling": -5.0,
}
DYNAMIC_V1_5_R80_REACTIVATED_DUAL_NEGATIVE_TOTAL_RAW_CONSENSUS_PARAMS = {
    **DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS,
    "route_horizon_negative_total_raw_consensus_guard": 1.0,
    "route_horizon_negative_total_raw_consensus_occupancy_threshold": 0.90,
    "route_horizon_negative_total_raw_consensus_residual_threshold": 0.0,
    "route_horizon_negative_total_raw_consensus_total_ceiling": -5.0,
}
DYNAMIC_V1_5_R81_REACTIVATED_DUAL_SEVERE_NEGATIVE_TOTAL_RAW_CONSENSUS_PARAMS = {
    **DYNAMIC_V1_5_R80_REACTIVATED_DUAL_NEGATIVE_TOTAL_RAW_CONSENSUS_PARAMS,
    "route_horizon_negative_total_raw_consensus_total_ceiling": -20.0,
}
DYNAMIC_V1_5_R82_REACTIVATED_DUAL_CONDITIONAL_LOW_TOTAL_PRESSURE_BLEND_PARAMS = {
    **DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS,
    "route_horizon_low_total_pressure_penalty": 0.35,
    "route_horizon_low_total_pressure_total_ceiling": 2.0,
    "route_horizon_low_total_pressure_pressure_ceiling": 0.0,
}
DYNAMIC_V1_5_R83_REACTIVATED_DUAL_LOW_TOTAL_CONSENSUS_COMPLETION_PARAMS = {
    **DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS,
    "route_horizon_low_total_consensus_completion_guard": 1.0,
    "route_horizon_low_total_consensus_completion_start_fraction": 0.0,
    "route_horizon_low_total_consensus_completion_end_fraction": 0.15,
    "route_horizon_low_total_consensus_completion_occupancy_threshold": 1.05,
    "route_horizon_low_total_consensus_completion_residual_threshold": 0.0,
    "route_horizon_low_total_consensus_completion_total_ceiling": 2.0,
    "route_horizon_low_total_consensus_completion_pressure_ceiling": 0.0,
}
DYNAMIC_V1_5_R84_REACTIVATED_DUAL_CONDITIONAL_RELEASE_GATE_PARAMS = {
    **DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS,
    "route_horizon_conditional_release_gate": 1.0,
    "route_horizon_conditional_release_gate_total_floor": 2.0,
    "route_horizon_conditional_release_gate_pressure_floor": 0.0,
}
DYNAMIC_V1_5_R85_REACTIVATED_DUAL_HORIZON_LOCAL_PRESSURE_PARAMS = {
    **DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS,
    "route_horizon_local_pressure_penalty": 0.35,
    "route_horizon_local_pressure_floor": 0.5,
}
DYNAMIC_V1_5_R86_REACTIVATED_DUAL_HORIZON_ZERO_SLACK_FLOOR_PARAMS = {
    **DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS,
    "route_horizon_zero_slack_floor_for_nonpositive_pressure": 1.0,
    "route_horizon_zero_slack_floor_pressure_ceiling": 0.0,
}
DYNAMIC_V1_5_R87_REACTIVATED_DUAL_LOW_SIGNAL_BONUS_GATE_PARAMS = {
    **DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS,
    "route_horizon_low_signal_bonus_gate": 1.0,
    "route_horizon_low_signal_bonus_total_ceiling": 2.0,
    "route_horizon_low_signal_bonus_pressure_ceiling": 0.0,
    "route_horizon_low_signal_bonus_scale": 0.0,
}
DYNAMIC_V1_5_R88_REACTIVATED_DUAL_LOW_SIGNAL_BONUS_SCALE_PARAMS = {
    **DYNAMIC_V1_5_R87_REACTIVATED_DUAL_LOW_SIGNAL_BONUS_GATE_PARAMS,
    "route_horizon_low_signal_bonus_scale": 0.9,
}
DYNAMIC_V1_5_R89_REACTIVATED_DUAL_LOW_SIGNAL_MARGIN_CAP_PARAMS = {
    **DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS,
    "route_horizon_low_signal_bonus_gate": 1.0,
    "route_horizon_low_signal_bonus_total_ceiling": 2.0,
    "route_horizon_low_signal_bonus_pressure_ceiling": 0.0,
    "route_horizon_low_signal_bonus_scale": 1.0,
    "route_horizon_low_signal_margin_cap": 0.15,
    "route_horizon_low_signal_margin_epsilon": 1e-6,
}
DYNAMIC_V1_5_R90_REACTIVATED_DUAL_SUPPORTED_MARGIN_CAP_PARAMS = {
    **DYNAMIC_V1_5_R89_REACTIVATED_DUAL_LOW_SIGNAL_MARGIN_CAP_PARAMS,
    "route_horizon_low_signal_margin_core_horizon_floor": 0.5,
}
DYNAMIC_V1_5_R91_REACTIVATED_DUAL_SUPPORTED_NARROW_MARGIN_CAP_PARAMS = {
    **DYNAMIC_V1_5_R90_REACTIVATED_DUAL_SUPPORTED_MARGIN_CAP_PARAMS,
    "route_horizon_low_signal_margin_cap": 0.1,
}
DYNAMIC_V1_5_R92_REACTIVATED_DUAL_SUPPORTED_SCORE_GAP_CAP_PARAMS = {
    **DYNAMIC_V1_5_R90_REACTIVATED_DUAL_SUPPORTED_MARGIN_CAP_PARAMS,
    "route_horizon_low_signal_margin_core_score_advantage_floor": 2.0,
}
DYNAMIC_V1_5_R114_REACTIVATED_DUAL_SUPPORTED_BIG_FINISHABLE_SUM_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R92_REACTIVATED_DUAL_SUPPORTED_SCORE_GAP_CAP_PARAMS,
    "route_horizon_no_positive_pressure_big_finishable_sum_power": 0.5,
    "route_horizon_no_positive_pressure_big_finishable_sum_floor": 12.0,
    "route_horizon_no_positive_pressure_big_finishable_sum_max_local_pressure_ceiling": 0.0,
    "route_horizon_no_positive_pressure_big_finishable_sum_phase_downstream_pressure_floor": 1.0,
    "route_horizon_no_positive_pressure_big_finishable_sum_movement_finishable_floor": 1.0,
    "route_horizon_no_positive_pressure_big_finishable_sum_phase_residual_ceiling": 0.4,
}
DYNAMIC_V1_5_R93_REACTIVATED_DUAL_SCORE_GAP_CONSENSUS_SAFE_PARAMS = {
    **DYNAMIC_V1_5_R92_REACTIVATED_DUAL_SUPPORTED_SCORE_GAP_CAP_PARAMS,
    "route_horizon_score_gap_consensus_guard": 1.0,
    "route_horizon_score_gap_consensus_total_ceiling": -15.0,
    "route_horizon_score_gap_consensus_pressure_ceiling": 0.0,
    "route_horizon_score_gap_consensus_gap_floor": 2.0,
}
DYNAMIC_V1_5_R94_REACTIVATED_DUAL_SUPPORTED_LOW_TOTAL_MARGIN_CAP_PARAMS = {
    **DYNAMIC_V1_5_R92_REACTIVATED_DUAL_SUPPORTED_SCORE_GAP_CAP_PARAMS,
    "route_horizon_supported_low_total_margin_cap": 0.15,
    "route_horizon_supported_low_total_total_ceiling": 1.0,
    "route_horizon_supported_low_total_pressure_ceiling": 0.0,
}
DYNAMIC_V1_5_R95_REACTIVATED_DUAL_SUPPORTED_NEGATIVE_PRESSURE_MARGIN_CAP_PARAMS = {
    **DYNAMIC_V1_5_R92_REACTIVATED_DUAL_SUPPORTED_SCORE_GAP_CAP_PARAMS,
    "route_horizon_supported_negative_pressure_margin_cap": 0.15,
    "route_horizon_supported_negative_pressure_total_ceiling": 2.0,
    "route_horizon_supported_negative_pressure_ceiling": -1e-6,
}
DYNAMIC_V1_5_R96_REACTIVATED_DUAL_UNIQUE_MOVEMENT_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R92_REACTIVATED_DUAL_SUPPORTED_SCORE_GAP_CAP_PARAMS,
    "route_horizon_unique_movement_terms": 1.0,
}
DYNAMIC_V1_5_R97_REACTIVATED_DUAL_UNIQUE_RESIDUAL_POWER_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R96_REACTIVATED_DUAL_UNIQUE_MOVEMENT_HORIZON_PARAMS,
    "route_horizon_residual_power": 2.0,
}
DYNAMIC_V1_5_R98_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R96_REACTIVATED_DUAL_UNIQUE_MOVEMENT_HORIZON_PARAMS,
    "route_horizon_finishable_power": 0.5,
}
DYNAMIC_V1_5_R99_REACTIVATED_DUAL_UNIQUE_FINISHABLE_RATIO_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R96_REACTIVATED_DUAL_UNIQUE_MOVEMENT_HORIZON_PARAMS,
    "route_horizon_total_demand_power": 1.0,
}
DYNAMIC_V1_5_R100_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_TIME_WEIGHT_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R98_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_HORIZON_PARAMS,
    "route_horizon_time_weight_power": 2.0,
}
DYNAMIC_V1_5_R101_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_CONDITIONAL_TIME_WEIGHT_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R98_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_HORIZON_PARAMS,
    "route_horizon_conditional_phase_time_weight_power": 2.0,
    "route_horizon_conditional_phase_time_weight_max_local_pressure_ceiling": 0.0,
    "route_horizon_conditional_phase_time_weight_phase_residual_ceiling": 0.2,
    "route_horizon_conditional_phase_time_weight_local_pressure_ceiling": 0.0,
}
DYNAMIC_V1_5_R102_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_CONDITIONAL_PRESSURE_TIME_WEIGHT_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R101_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_CONDITIONAL_TIME_WEIGHT_HORIZON_PARAMS,
    "route_horizon_conditional_phase_time_weight_phase_downstream_pressure_floor": 1.0,
}
DYNAMIC_V1_5_R103_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_MOVEMENT_PRESSURE_TIME_WEIGHT_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R101_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_CONDITIONAL_TIME_WEIGHT_HORIZON_PARAMS,
    "route_horizon_conditional_phase_time_weight_movement_residual_ceiling": 0.2,
    "route_horizon_conditional_phase_time_weight_movement_downstream_pressure_floor": 1.0,
}
DYNAMIC_V1_5_R104_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_NO_RISKY_MARGIN_CAP_PARAMS = {
    **DYNAMIC_V1_5_R103_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_MOVEMENT_PRESSURE_TIME_WEIGHT_HORIZON_PARAMS,
    "route_horizon_no_risky_movement_margin_cap": 0.1,
    "route_horizon_no_risky_movement_score_advantage_floor": 1.0,
}
DYNAMIC_V1_5_R105_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_NO_RISKY_NONPOSITIVE_PRESSURE_MARGIN_CAP_PARAMS = {
    **DYNAMIC_V1_5_R104_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_NO_RISKY_MARGIN_CAP_PARAMS,
    "route_horizon_no_risky_movement_max_local_pressure_ceiling": 0.0,
}
DYNAMIC_V1_5_R106_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_SECONDARY_TIME_WEIGHT_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R103_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_MOVEMENT_PRESSURE_TIME_WEIGHT_HORIZON_PARAMS,
    "route_horizon_secondary_phase_time_weight_power": 1.5,
    "route_horizon_secondary_phase_time_weight_max_local_pressure_ceiling": 0.0,
    "route_horizon_secondary_phase_time_weight_phase_residual_ceiling": 0.4,
    "route_horizon_secondary_phase_time_weight_local_pressure_ceiling": 0.0,
    "route_horizon_secondary_phase_time_weight_movement_residual_floor": 0.2,
    "route_horizon_secondary_phase_time_weight_movement_residual_ceiling": 0.4,
    "route_horizon_secondary_phase_time_weight_movement_downstream_pressure_floor": 1.0,
}
DYNAMIC_V1_5_R107_REACTIVATED_DUAL_LOW_SUPPORT_BONUS_DAMPING_PARAMS = {
    **DYNAMIC_V1_5_R103_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_MOVEMENT_PRESSURE_TIME_WEIGHT_HORIZON_PARAMS,
    "route_horizon_low_support_bonus_damping_scale": 0.9,
    "route_horizon_low_support_bonus_damping_margin_cap": 0.15,
    "route_horizon_low_support_bonus_damping_score_advantage_floor": 1.0,
    "route_horizon_low_support_bonus_damping_max_local_pressure_ceiling": 0.0,
}
DYNAMIC_V1_5_R108_REACTIVATED_DUAL_LOW_SUPPORT_CORE_ANCHOR_PARAMS = {
    **DYNAMIC_V1_5_R103_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_MOVEMENT_PRESSURE_TIME_WEIGHT_HORIZON_PARAMS,
    "route_horizon_low_support_core_anchor_bonus": 0.11,
    "route_horizon_low_support_core_anchor_margin_cap": 0.15,
    "route_horizon_low_support_core_anchor_score_advantage_floor": 1.0,
    "route_horizon_low_support_core_anchor_max_local_pressure_ceiling": 0.0,
}
DYNAMIC_V1_5_R109_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_FINISHABLE_COUNT_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R108_REACTIVATED_DUAL_LOW_SUPPORT_CORE_ANCHOR_PARAMS,
    "route_horizon_no_positive_pressure_finishable_count_power": 0.5,
    "route_horizon_no_positive_pressure_finishable_count_max_local_pressure_ceiling": 0.0,
    "route_horizon_no_positive_pressure_finishable_count_phase_downstream_pressure_floor": 1.0,
}
DYNAMIC_V1_5_R110_REACTIVATED_DUAL_HIGH_FINISHABLE_COUNT_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R109_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_FINISHABLE_COUNT_HORIZON_PARAMS,
    "route_horizon_no_positive_pressure_finishable_count_min_count": 4.0,
}
DYNAMIC_V1_5_R111_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_MOVEMENT_FINISHABLE_POWER_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R108_REACTIVATED_DUAL_LOW_SUPPORT_CORE_ANCHOR_PARAMS,
    "route_horizon_conditional_movement_finishable_power": 0.35,
    "route_horizon_conditional_movement_finishable_power_max_local_pressure_ceiling": 0.0,
    "route_horizon_conditional_movement_finishable_power_phase_downstream_pressure_floor": 1.0,
    "route_horizon_conditional_movement_finishable_power_movement_finishable_floor": 1.0,
}
DYNAMIC_V1_5_R112_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_BIG_FINISHABLE_COUNT_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R111_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_MOVEMENT_FINISHABLE_POWER_HORIZON_PARAMS,
    "route_horizon_no_positive_pressure_big_finishable_count_power": 0.5,
    "route_horizon_no_positive_pressure_big_finishable_count_max_local_pressure_ceiling": 0.0,
    "route_horizon_no_positive_pressure_big_finishable_count_phase_downstream_pressure_floor": 1.0,
    "route_horizon_no_positive_pressure_big_finishable_count_movement_finishable_floor": 1.0,
    "route_horizon_no_positive_pressure_big_finishable_count_min_count": 2.0,
}
DYNAMIC_V1_5_R113_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_MULTI_BIG_FINISHABLE_POWER_HORIZON_PARAMS = {
    **DYNAMIC_V1_5_R112_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_BIG_FINISHABLE_COUNT_HORIZON_PARAMS,
    "route_horizon_no_positive_pressure_multi_big_finishable_power": 0.25,
    "route_horizon_no_positive_pressure_multi_big_finishable_power_max_local_pressure_ceiling": 0.0,
    "route_horizon_no_positive_pressure_multi_big_finishable_power_phase_downstream_pressure_floor": 1.0,
    "route_horizon_no_positive_pressure_multi_big_finishable_power_movement_finishable_floor": 1.0,
    "route_horizon_no_positive_pressure_multi_big_finishable_power_min_count": 2.0,
}
DYNAMIC_V1_5_CONTROLLER_IDS = {
    "finite_storage_dynamic_primal_dual_v1_5",
    "finite_storage_dynamic_primal_dual_v1_5_r2_guarded",
    "finite_storage_dynamic_primal_dual_v1_5_r3_double_release",
    "finite_storage_dynamic_primal_dual_v1_5_r4_release_service",
    "finite_storage_dynamic_primal_dual_v1_5_r5_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r6_terminal_flush",
    "finite_storage_dynamic_primal_dual_v1_5_r7_double_filter",
    "finite_storage_dynamic_primal_dual_v1_5_r8_multi_baseline_filter",
    "finite_storage_dynamic_primal_dual_v1_5_r9_hold_only",
    "finite_storage_dynamic_primal_dual_v1_5_r10_bounded_hold",
    "finite_storage_dynamic_primal_dual_v1_5_r11_completion_risk",
    "finite_storage_dynamic_primal_dual_v1_5_r12_route_completion",
    "finite_storage_dynamic_primal_dual_v1_5_r13_route_demand",
    "finite_storage_dynamic_primal_dual_v1_5_r14_route_demand_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r15_horizon_model",
    "finite_storage_dynamic_primal_dual_v1_5_r16_horizon_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r17_horizon_capacity_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r18_horizon_balanced_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r19_horizon_double_anchored",
    "finite_storage_dynamic_primal_dual_v1_5_r20_horizon_max_double_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r21_horizon_service_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r22_horizon_completion_safety",
    "finite_storage_dynamic_primal_dual_v1_5_r23_horizon_dominance",
    "finite_storage_dynamic_primal_dual_v1_5_r24_staged_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r25_staged_horizon_late_max",
    "finite_storage_dynamic_primal_dual_v1_5_r26_relative_exit_urgency",
    "finite_storage_dynamic_primal_dual_v1_5_r27_terminal_exit_protection",
    "finite_storage_dynamic_primal_dual_v1_5_r28_max_pressure_envelope",
    "finite_storage_dynamic_primal_dual_v1_5_r29_core_baseline_envelope",
    "finite_storage_dynamic_primal_dual_v1_5_r30_double_envelope",
    "finite_storage_dynamic_primal_dual_v1_5_r31_late_double_terminal",
    "finite_storage_dynamic_primal_dual_v1_5_r32_preterminal_double_guard",
    "finite_storage_dynamic_primal_dual_v1_5_r33_midcourse_double_guard",
    "finite_storage_dynamic_primal_dual_v1_5_r34_core_minimax_guard",
    "finite_storage_dynamic_primal_dual_v1_5_r35_deadline_urgency",
    "finite_storage_dynamic_primal_dual_v1_5_r36_late_deadline_anchor",
    "finite_storage_dynamic_primal_dual_v1_5_r37_late_deadline_service_anchor",
    "finite_storage_dynamic_primal_dual_v1_5_r38_capacity_rescue_guard",
    "finite_storage_dynamic_primal_dual_v1_5_r39_capacity_score_envelope",
    "finite_storage_dynamic_primal_dual_v1_5_r40_pressure_safe_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r41_terminal_core_completion",
    "finite_storage_dynamic_primal_dual_v1_5_r42_tail_completion_rescue",
    "finite_storage_dynamic_primal_dual_v1_5_r43_staged_pressure_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r44_loose_staged_pressure_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r45_preterminal_pressure_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r46_occupancy_safe_completion",
    "finite_storage_dynamic_primal_dual_v1_5_r47_staged_severe_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r48_pressure_double_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r49_early_pressure_double_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r50_completion_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r51_core_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r52_raw_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r53_post_veto_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r54_reactivated_dual_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r55_reactivated_dual_uncapped_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r56_reactivated_dual_raw_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r57_reactivated_dual_capacity_completion_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r58_reactivated_dual_post_veto_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r59_reactivated_dual_narrow_post_veto_double_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r60_reactivated_dual_early_capacity_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r61_reactivated_dual_mid_severe_early_capacity_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r62_reactivated_dual_late_severe_raw_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r63_reactivated_dual_native_base_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r64_reactivated_dual_native_base_late_severe_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r65_reactivated_dual_native_capacity_score_rescue",
    "finite_storage_dynamic_primal_dual_v1_5_r66_reactivated_dual_native_horizon_score_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r67_reactivated_dual_native_negative_total_penalty",
    "finite_storage_dynamic_primal_dual_v1_5_r68_reactivated_dual_native_double_horizon_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r69_reactivated_dual_release_biased_native_base",
    "finite_storage_dynamic_primal_dual_v1_5_r70_reactivated_dual_descendant_release_native_base",
    "finite_storage_dynamic_primal_dual_v1_5_r71_reactivated_dual_local_descendant_release_native_base",
    "finite_storage_dynamic_primal_dual_v1_5_r72_reactivated_dual_release_risk_horizon_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r73_reactivated_dual_release_risk_late_conflict_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r74_reactivated_dual_negative_total_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r75_reactivated_dual_release_risk_negative_pressure_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r76_reactivated_dual_release_risk_negative_total_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r77_reactivated_dual_conditional_risk_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r78_reactivated_dual_conditional_risk_late_raw_consensus",
    "finite_storage_dynamic_primal_dual_v1_5_r79_reactivated_dual_negative_total_completion_conflict",
    "finite_storage_dynamic_primal_dual_v1_5_r80_reactivated_dual_negative_total_raw_consensus",
    "finite_storage_dynamic_primal_dual_v1_5_r81_reactivated_dual_severe_negative_total_raw_consensus",
    "finite_storage_dynamic_primal_dual_v1_5_r82_reactivated_dual_conditional_low_total_pressure_blend",
    "finite_storage_dynamic_primal_dual_v1_5_r83_reactivated_dual_low_total_consensus_completion",
    "finite_storage_dynamic_primal_dual_v1_5_r84_reactivated_dual_conditional_release_gate",
    "finite_storage_dynamic_primal_dual_v1_5_r85_reactivated_dual_horizon_local_pressure",
    "finite_storage_dynamic_primal_dual_v1_5_r86_reactivated_dual_horizon_zero_slack_floor",
    "finite_storage_dynamic_primal_dual_v1_5_r87_reactivated_dual_low_signal_bonus_gate",
    "finite_storage_dynamic_primal_dual_v1_5_r88_reactivated_dual_low_signal_bonus_scale",
    "finite_storage_dynamic_primal_dual_v1_5_r89_reactivated_dual_low_signal_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r90_reactivated_dual_supported_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r91_reactivated_dual_supported_narrow_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r92_reactivated_dual_supported_score_gap_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r93_reactivated_dual_score_gap_consensus_safe",
    "finite_storage_dynamic_primal_dual_v1_5_r94_reactivated_dual_supported_low_total_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r95_reactivated_dual_supported_negative_pressure_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r96_reactivated_dual_unique_movement_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r97_reactivated_dual_unique_residual_power_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r98_reactivated_dual_unique_finishable_power_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r99_reactivated_dual_unique_finishable_ratio_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r100_reactivated_dual_unique_finishable_power_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r101_reactivated_dual_unique_finishable_power_conditional_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r102_reactivated_dual_unique_finishable_power_conditional_pressure_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r103_reactivated_dual_unique_finishable_power_movement_pressure_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r104_reactivated_dual_unique_finishable_power_no_risky_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r105_reactivated_dual_unique_finishable_power_no_risky_nonpositive_pressure_margin_cap",
    "finite_storage_dynamic_primal_dual_v1_5_r106_reactivated_dual_unique_finishable_power_secondary_time_weight_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r107_reactivated_dual_low_support_bonus_damping",
    "finite_storage_dynamic_primal_dual_v1_5_r108_reactivated_dual_low_support_core_anchor",
    "finite_storage_dynamic_primal_dual_v1_5_r109_reactivated_dual_no_positive_pressure_finishable_count_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r110_reactivated_dual_high_finishable_count_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r111_reactivated_dual_no_positive_pressure_movement_finishable_power_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r112_reactivated_dual_no_positive_pressure_big_finishable_count_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r113_reactivated_dual_no_positive_pressure_multi_big_finishable_power_horizon",
    "finite_storage_dynamic_primal_dual_v1_5_r114_reactivated_dual_supported_big_finishable_sum_horizon",
}
V1_6_CONTROLLER_IDS: set[str] = {
    "finite_storage_completion_safe_primal_dual_v1_6",
}
ACTION_SUMMARY_COMPONENTS = [
    "downstream_storage",
    "spillback",
    "switching",
    "service",
    "incident",
    "storage_price",
    "cascade_price",
    "release",
    "service_age",
    "guardrail",
    "double_pressure_scaffold",
]


def dynamic_v1_5_params_for_controller(controller: str) -> dict[str, float]:
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r114_reactivated_dual_supported_big_finishable_sum_horizon":
        return DYNAMIC_V1_5_R114_REACTIVATED_DUAL_SUPPORTED_BIG_FINISHABLE_SUM_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r113_reactivated_dual_no_positive_pressure_multi_big_finishable_power_horizon":
        return DYNAMIC_V1_5_R113_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_MULTI_BIG_FINISHABLE_POWER_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r112_reactivated_dual_no_positive_pressure_big_finishable_count_horizon":
        return DYNAMIC_V1_5_R112_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_BIG_FINISHABLE_COUNT_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r111_reactivated_dual_no_positive_pressure_movement_finishable_power_horizon":
        return DYNAMIC_V1_5_R111_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_MOVEMENT_FINISHABLE_POWER_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r110_reactivated_dual_high_finishable_count_horizon":
        return DYNAMIC_V1_5_R110_REACTIVATED_DUAL_HIGH_FINISHABLE_COUNT_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r109_reactivated_dual_no_positive_pressure_finishable_count_horizon":
        return DYNAMIC_V1_5_R109_REACTIVATED_DUAL_NO_POSITIVE_PRESSURE_FINISHABLE_COUNT_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r108_reactivated_dual_low_support_core_anchor":
        return DYNAMIC_V1_5_R108_REACTIVATED_DUAL_LOW_SUPPORT_CORE_ANCHOR_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r107_reactivated_dual_low_support_bonus_damping":
        return DYNAMIC_V1_5_R107_REACTIVATED_DUAL_LOW_SUPPORT_BONUS_DAMPING_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r106_reactivated_dual_unique_finishable_power_secondary_time_weight_horizon":
        return DYNAMIC_V1_5_R106_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_SECONDARY_TIME_WEIGHT_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r105_reactivated_dual_unique_finishable_power_no_risky_nonpositive_pressure_margin_cap":
        return DYNAMIC_V1_5_R105_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_NO_RISKY_NONPOSITIVE_PRESSURE_MARGIN_CAP_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r104_reactivated_dual_unique_finishable_power_no_risky_margin_cap":
        return DYNAMIC_V1_5_R104_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_NO_RISKY_MARGIN_CAP_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r103_reactivated_dual_unique_finishable_power_movement_pressure_time_weight_horizon":
        return DYNAMIC_V1_5_R103_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_MOVEMENT_PRESSURE_TIME_WEIGHT_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r102_reactivated_dual_unique_finishable_power_conditional_pressure_time_weight_horizon":
        return DYNAMIC_V1_5_R102_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_CONDITIONAL_PRESSURE_TIME_WEIGHT_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r101_reactivated_dual_unique_finishable_power_conditional_time_weight_horizon":
        return DYNAMIC_V1_5_R101_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_CONDITIONAL_TIME_WEIGHT_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r100_reactivated_dual_unique_finishable_power_time_weight_horizon":
        return DYNAMIC_V1_5_R100_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_TIME_WEIGHT_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r99_reactivated_dual_unique_finishable_ratio_horizon":
        return DYNAMIC_V1_5_R99_REACTIVATED_DUAL_UNIQUE_FINISHABLE_RATIO_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r98_reactivated_dual_unique_finishable_power_horizon":
        return DYNAMIC_V1_5_R98_REACTIVATED_DUAL_UNIQUE_FINISHABLE_POWER_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r97_reactivated_dual_unique_residual_power_horizon":
        return DYNAMIC_V1_5_R97_REACTIVATED_DUAL_UNIQUE_RESIDUAL_POWER_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r96_reactivated_dual_unique_movement_horizon":
        return DYNAMIC_V1_5_R96_REACTIVATED_DUAL_UNIQUE_MOVEMENT_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r95_reactivated_dual_supported_negative_pressure_margin_cap":
        return DYNAMIC_V1_5_R95_REACTIVATED_DUAL_SUPPORTED_NEGATIVE_PRESSURE_MARGIN_CAP_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r94_reactivated_dual_supported_low_total_margin_cap":
        return DYNAMIC_V1_5_R94_REACTIVATED_DUAL_SUPPORTED_LOW_TOTAL_MARGIN_CAP_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r93_reactivated_dual_score_gap_consensus_safe":
        return DYNAMIC_V1_5_R93_REACTIVATED_DUAL_SCORE_GAP_CONSENSUS_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r92_reactivated_dual_supported_score_gap_cap":
        return DYNAMIC_V1_5_R92_REACTIVATED_DUAL_SUPPORTED_SCORE_GAP_CAP_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r91_reactivated_dual_supported_narrow_margin_cap":
        return DYNAMIC_V1_5_R91_REACTIVATED_DUAL_SUPPORTED_NARROW_MARGIN_CAP_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r90_reactivated_dual_supported_margin_cap":
        return DYNAMIC_V1_5_R90_REACTIVATED_DUAL_SUPPORTED_MARGIN_CAP_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r89_reactivated_dual_low_signal_margin_cap":
        return DYNAMIC_V1_5_R89_REACTIVATED_DUAL_LOW_SIGNAL_MARGIN_CAP_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r88_reactivated_dual_low_signal_bonus_scale":
        return DYNAMIC_V1_5_R88_REACTIVATED_DUAL_LOW_SIGNAL_BONUS_SCALE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r87_reactivated_dual_low_signal_bonus_gate":
        return DYNAMIC_V1_5_R87_REACTIVATED_DUAL_LOW_SIGNAL_BONUS_GATE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r86_reactivated_dual_horizon_zero_slack_floor":
        return DYNAMIC_V1_5_R86_REACTIVATED_DUAL_HORIZON_ZERO_SLACK_FLOOR_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r85_reactivated_dual_horizon_local_pressure":
        return DYNAMIC_V1_5_R85_REACTIVATED_DUAL_HORIZON_LOCAL_PRESSURE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r84_reactivated_dual_conditional_release_gate":
        return DYNAMIC_V1_5_R84_REACTIVATED_DUAL_CONDITIONAL_RELEASE_GATE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r83_reactivated_dual_low_total_consensus_completion":
        return DYNAMIC_V1_5_R83_REACTIVATED_DUAL_LOW_TOTAL_CONSENSUS_COMPLETION_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r82_reactivated_dual_conditional_low_total_pressure_blend":
        return DYNAMIC_V1_5_R82_REACTIVATED_DUAL_CONDITIONAL_LOW_TOTAL_PRESSURE_BLEND_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r81_reactivated_dual_severe_negative_total_raw_consensus":
        return DYNAMIC_V1_5_R81_REACTIVATED_DUAL_SEVERE_NEGATIVE_TOTAL_RAW_CONSENSUS_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r80_reactivated_dual_negative_total_raw_consensus":
        return DYNAMIC_V1_5_R80_REACTIVATED_DUAL_NEGATIVE_TOTAL_RAW_CONSENSUS_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r79_reactivated_dual_negative_total_completion_conflict":
        return DYNAMIC_V1_5_R79_REACTIVATED_DUAL_NEGATIVE_TOTAL_COMPLETION_CONFLICT_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r78_reactivated_dual_conditional_risk_late_raw_consensus":
        return DYNAMIC_V1_5_R78_REACTIVATED_DUAL_CONDITIONAL_RISK_LATE_RAW_CONSENSUS_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r77_reactivated_dual_conditional_risk_blend":
        return DYNAMIC_V1_5_R77_REACTIVATED_DUAL_CONDITIONAL_RISK_BLEND_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r76_reactivated_dual_release_risk_negative_total_blend":
        return DYNAMIC_V1_5_R76_REACTIVATED_DUAL_RELEASE_RISK_NEGATIVE_TOTAL_BLEND_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r75_reactivated_dual_release_risk_negative_pressure_blend":
        return DYNAMIC_V1_5_R75_REACTIVATED_DUAL_RELEASE_RISK_NEGATIVE_PRESSURE_BLEND_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r74_reactivated_dual_negative_total_consensus_safe":
        return DYNAMIC_V1_5_R74_REACTIVATED_DUAL_NEGATIVE_TOTAL_CONSENSUS_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r73_reactivated_dual_release_risk_late_conflict_safe":
        return DYNAMIC_V1_5_R73_REACTIVATED_DUAL_RELEASE_RISK_LATE_CONFLICT_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r72_reactivated_dual_release_risk_horizon_blend":
        return DYNAMIC_V1_5_R72_REACTIVATED_DUAL_RELEASE_RISK_HORIZON_BLEND_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r71_reactivated_dual_local_descendant_release_native_base":
        return DYNAMIC_V1_5_R71_REACTIVATED_DUAL_LOCAL_DESCENDANT_RELEASE_NATIVE_BASE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r70_reactivated_dual_descendant_release_native_base":
        return DYNAMIC_V1_5_R70_REACTIVATED_DUAL_DESCENDANT_RELEASE_NATIVE_BASE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r69_reactivated_dual_release_biased_native_base":
        return DYNAMIC_V1_5_R69_REACTIVATED_DUAL_RELEASE_BIASED_NATIVE_BASE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r68_reactivated_dual_native_double_horizon_blend":
        return DYNAMIC_V1_5_R68_REACTIVATED_DUAL_NATIVE_DOUBLE_HORIZON_BLEND_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r67_reactivated_dual_native_negative_total_penalty":
        return DYNAMIC_V1_5_R67_REACTIVATED_DUAL_NATIVE_NEGATIVE_TOTAL_PENALTY_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r66_reactivated_dual_native_horizon_score_blend":
        return DYNAMIC_V1_5_R66_REACTIVATED_DUAL_NATIVE_HORIZON_SCORE_BLEND_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r65_reactivated_dual_native_capacity_score_rescue":
        return DYNAMIC_V1_5_R65_REACTIVATED_DUAL_NATIVE_CAPACITY_SCORE_RESCUE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r64_reactivated_dual_native_base_late_severe_safe":
        return DYNAMIC_V1_5_R64_REACTIVATED_DUAL_NATIVE_BASE_LATE_SEVERE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r63_reactivated_dual_native_base_safe":
        return DYNAMIC_V1_5_R63_REACTIVATED_DUAL_NATIVE_BASE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r62_reactivated_dual_late_severe_raw_consensus_safe":
        return DYNAMIC_V1_5_R62_REACTIVATED_DUAL_LATE_SEVERE_RAW_CONSENSUS_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r61_reactivated_dual_mid_severe_early_capacity_conflict_safe":
        return DYNAMIC_V1_5_R61_REACTIVATED_DUAL_MID_SEVERE_EARLY_CAPACITY_CONFLICT_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r60_reactivated_dual_early_capacity_conflict_safe":
        return DYNAMIC_V1_5_R60_REACTIVATED_DUAL_EARLY_CAPACITY_CONFLICT_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r59_reactivated_dual_narrow_post_veto_double_safe":
        return DYNAMIC_V1_5_R59_REACTIVATED_DUAL_NARROW_POST_VETO_DOUBLE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r58_reactivated_dual_post_veto_double_safe":
        return DYNAMIC_V1_5_R58_REACTIVATED_DUAL_POST_VETO_DOUBLE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r57_reactivated_dual_capacity_completion_safe":
        return DYNAMIC_V1_5_R57_REACTIVATED_DUAL_CAPACITY_COMPLETION_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r56_reactivated_dual_raw_consensus_safe":
        return DYNAMIC_V1_5_R56_REACTIVATED_DUAL_RAW_CONSENSUS_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r55_reactivated_dual_uncapped_safe":
        return DYNAMIC_V1_5_R55_REACTIVATED_DUAL_UNCAPPED_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r54_reactivated_dual_safe":
        return DYNAMIC_V1_5_R54_REACTIVATED_DUAL_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r53_post_veto_double_safe":
        return DYNAMIC_V1_5_R53_POST_VETO_DOUBLE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r52_raw_consensus_safe":
        return DYNAMIC_V1_5_R52_RAW_CONSENSUS_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r51_core_consensus_safe":
        return DYNAMIC_V1_5_R51_CORE_CONSENSUS_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r50_completion_conflict_safe":
        return DYNAMIC_V1_5_R50_COMPLETION_CONFLICT_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r49_early_pressure_double_conflict_safe":
        return DYNAMIC_V1_5_R49_EARLY_PRESSURE_DOUBLE_CONFLICT_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r48_pressure_double_conflict_safe":
        return DYNAMIC_V1_5_R48_PRESSURE_DOUBLE_CONFLICT_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r47_staged_severe_double_safe":
        return DYNAMIC_V1_5_R47_STAGED_SEVERE_DOUBLE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r46_occupancy_safe_completion":
        return DYNAMIC_V1_5_R46_OCCUPANCY_SAFE_COMPLETION_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r45_preterminal_pressure_safe":
        return DYNAMIC_V1_5_R45_PRETERMINAL_PRESSURE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r44_loose_staged_pressure_safe":
        return DYNAMIC_V1_5_R44_LOOSE_STAGED_PRESSURE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r43_staged_pressure_safe":
        return DYNAMIC_V1_5_R43_STAGED_PRESSURE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r42_tail_completion_rescue":
        return DYNAMIC_V1_5_R42_TAIL_COMPLETION_RESCUE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r41_terminal_core_completion":
        return DYNAMIC_V1_5_R41_TERMINAL_CORE_COMPLETION_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r40_pressure_safe_horizon":
        return DYNAMIC_V1_5_R40_PRESSURE_SAFE_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r39_capacity_score_envelope":
        return DYNAMIC_V1_5_R39_CAPACITY_SCORE_ENVELOPE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r38_capacity_rescue_guard":
        return DYNAMIC_V1_5_R38_CAPACITY_RESCUE_GUARD_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r37_late_deadline_service_anchor":
        return DYNAMIC_V1_5_R37_LATE_DEADLINE_SERVICE_ANCHOR_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r36_late_deadline_anchor":
        return DYNAMIC_V1_5_R36_LATE_DEADLINE_ANCHOR_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r35_deadline_urgency":
        return DYNAMIC_V1_5_R35_DEADLINE_URGENCY_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r34_core_minimax_guard":
        return DYNAMIC_V1_5_R34_CORE_MINIMAX_GUARD_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r33_midcourse_double_guard":
        return DYNAMIC_V1_5_R33_MIDCOURSE_DOUBLE_GUARD_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r32_preterminal_double_guard":
        return DYNAMIC_V1_5_R32_PRETERMINAL_DOUBLE_GUARD_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r31_late_double_terminal":
        return DYNAMIC_V1_5_R31_LATE_DOUBLE_TERMINAL_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r30_double_envelope":
        return DYNAMIC_V1_5_R30_DOUBLE_ENVELOPE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r29_core_baseline_envelope":
        return DYNAMIC_V1_5_R29_CORE_BASELINE_ENVELOPE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r28_max_pressure_envelope":
        return DYNAMIC_V1_5_R28_MAX_PRESSURE_ENVELOPE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r27_terminal_exit_protection":
        return DYNAMIC_V1_5_R27_TERMINAL_EXIT_PROTECTION_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r26_relative_exit_urgency":
        return DYNAMIC_V1_5_R26_RELATIVE_EXIT_URGENCY_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r25_staged_horizon_late_max":
        return DYNAMIC_V1_5_R25_STAGED_HORIZON_LATE_MAX_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r24_staged_horizon":
        return DYNAMIC_V1_5_R24_STAGED_HORIZON_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r23_horizon_dominance":
        return DYNAMIC_V1_5_R23_HORIZON_DOMINANCE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r22_horizon_completion_safety":
        return DYNAMIC_V1_5_R22_HORIZON_COMPLETION_SAFETY_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r21_horizon_service_terminal":
        return DYNAMIC_V1_5_R21_HORIZON_SERVICE_TERMINAL_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r20_horizon_max_double_terminal":
        return DYNAMIC_V1_5_R20_HORIZON_MAX_DOUBLE_TERMINAL_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r19_horizon_double_anchored":
        return DYNAMIC_V1_5_R19_HORIZON_DOUBLE_ANCHORED_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r18_horizon_balanced_terminal":
        return DYNAMIC_V1_5_R18_HORIZON_BALANCED_TERMINAL_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r17_horizon_capacity_terminal":
        return DYNAMIC_V1_5_R17_HORIZON_CAPACITY_TERMINAL_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r16_horizon_terminal":
        return DYNAMIC_V1_5_R16_HORIZON_TERMINAL_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r15_horizon_model":
        return DYNAMIC_V1_5_R15_HORIZON_MODEL_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r14_route_demand_double_safe":
        return DYNAMIC_V1_5_R14_ROUTE_DEMAND_DOUBLE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r13_route_demand":
        return DYNAMIC_V1_5_R13_ROUTE_DEMAND_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r12_route_completion":
        return DYNAMIC_V1_5_R12_ROUTE_COMPLETION_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r11_completion_risk":
        return DYNAMIC_V1_5_R11_COMPLETION_RISK_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r10_bounded_hold":
        return DYNAMIC_V1_5_R10_BOUNDED_HOLD_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r9_hold_only":
        return DYNAMIC_V1_5_R9_HOLD_ONLY_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r8_multi_baseline_filter":
        return DYNAMIC_V1_5_R8_MULTI_BASELINE_FILTER_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r7_double_filter":
        return DYNAMIC_V1_5_R7_DOUBLE_FILTER_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r6_terminal_flush":
        return DYNAMIC_V1_5_R6_TERMINAL_FLUSH_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r5_double_safe":
        return DYNAMIC_V1_5_R5_DOUBLE_SAFE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r4_release_service":
        return DYNAMIC_V1_5_R4_RELEASE_SERVICE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r3_double_release":
        return DYNAMIC_V1_5_R3_DOUBLE_RELEASE_PARAMS
    if controller == "finite_storage_dynamic_primal_dual_v1_5_r2_guarded":
        return DYNAMIC_V1_5_R2_GUARDED_PARAMS
    return DYNAMIC_V1_5_PARAMS


def _spillback_flags(state: dict[str, Any], edge: str) -> dict[str, Any]:
    flags = state.get("spillback_blocking", {}).get(edge, {})
    if isinstance(flags, bool):
        return {"spillback": flags, "blocking": flags, "occupancy_ratio": 1.0 if flags else 0.0}
    return flags if isinstance(flags, dict) else {}


def finite_storage_binding_active(finite_storage_state: dict[str, Any]) -> bool:
    capacities = finite_storage_state.get("downstream_storage", {})
    residual = finite_storage_state.get("residual_receiving_capacity", {})
    for edge, capacity in capacities.items():
        cap = max(float(capacity), 1.0)
        residual_ratio = float(residual.get(edge, cap)) / cap
        flags = _spillback_flags(finite_storage_state, str(edge))
        if residual_ratio <= 0.15 or bool(flags.get("spillback", False)) or bool(flags.get("blocking", False)):
            return True
    return False


def state_storage_summary(finite_storage_state: dict[str, Any]) -> dict[str, float]:
    capacities = finite_storage_state.get("downstream_storage", {})
    residual = finite_storage_state.get("residual_receiving_capacity", {})
    occupancy_values = [
        float(_spillback_flags(finite_storage_state, str(edge)).get("occupancy_ratio", 0.0))
        for edge in capacities
    ]
    residual_ratios = [
        float(residual.get(edge, float(capacity))) / max(float(capacity), 1.0)
        for edge, capacity in capacities.items()
    ]
    return {
        "max_occupancy_ratio": float(max(occupancy_values, default=0.0)),
        "min_residual_ratio": float(min(residual_ratios, default=1.0)),
    }


def init_action_decision_summary(controller: str) -> dict[str, Any]:
    return {
        "controller": controller,
        "total_decisions": 0,
        "action_changed_relative_to_pressure_count": 0,
        "binding_decision_count": 0,
        "binding_action_changed_count": 0,
        "selected_component_nonzero_counts": {field: 0 for field in ACTION_SUMMARY_COMPONENTS},
        "any_phase_component_nonzero_counts": {field: 0 for field in ACTION_SUMMARY_COMPONENTS},
        "double_safety_fallback_count": 0,
        "terminal_completion_fallback_count": 0,
        "double_score_safety_filter_count": 0,
        "multi_baseline_safety_filter_count": 0,
        "hold_only_safety_filter_count": 0,
        "max_hold_safety_filter_count": 0,
        "completion_risk_filter_count": 0,
        "route_completion_prediction_filter_count": 0,
        "route_demand_completion_filter_count": 0,
        "route_demand_double_score_veto_count": 0,
        "route_horizon_completion_filter_count": 0,
        "route_horizon_dominance_filter_count": 0,
        "terminal_exit_protection_guard_count": 0,
        "route_horizon_max_pressure_envelope_count": 0,
        "route_horizon_core_baseline_envelope_count": 0,
        "route_horizon_double_pressure_envelope_count": 0,
        "route_horizon_core_minimax_guard_count": 0,
        "route_horizon_capacity_rescue_guard_count": 0,
        "route_horizon_capacity_score_envelope_count": 0,
        "route_horizon_native_capacity_score_rescue_guard_count": 0,
        "route_horizon_severe_double_guard_count": 0,
        "route_horizon_pressure_double_conflict_guard_count": 0,
        "route_horizon_completion_conflict_guard_count": 0,
        "route_horizon_capacity_completion_conflict_guard_count": 0,
        "route_horizon_early_capacity_completion_conflict_guard_count": 0,
        "route_horizon_negative_total_completion_conflict_guard_count": 0,
        "route_horizon_low_total_consensus_completion_guard_count": 0,
        "route_horizon_negative_total_raw_consensus_guard_count": 0,
        "route_horizon_core_consensus_guard_count": 0,
        "route_horizon_raw_consensus_guard_count": 0,
        "post_completion_veto_double_conflict_guard_count": 0,
        "route_horizon_pressure_safe_guard_count": 0,
        "route_horizon_tail_completion_rescue_count": 0,
        "completion_safety_veto_count": 0,
        "max_occupancy_ratio_observed": 0.0,
        "min_residual_ratio_observed": 1.0,
    }


def update_action_decision_summary(
    summary: dict[str, Any],
    audit: dict[str, Any],
    finite_storage_state: dict[str, Any],
) -> None:
    summary["total_decisions"] = int(summary.get("total_decisions", 0)) + 1
    changed = bool(audit.get("action_changed_relative_to_pressure"))
    if changed:
        summary["action_changed_relative_to_pressure_count"] = int(summary.get("action_changed_relative_to_pressure_count", 0)) + 1
    if audit.get("double_safety_fallback_used"):
        summary["double_safety_fallback_count"] = int(summary.get("double_safety_fallback_count", 0)) + 1
    if audit.get("terminal_completion_fallback_used"):
        summary["terminal_completion_fallback_count"] = int(summary.get("terminal_completion_fallback_count", 0)) + 1
    if audit.get("double_score_safety_filter_used"):
        summary["double_score_safety_filter_count"] = int(summary.get("double_score_safety_filter_count", 0)) + 1
    if audit.get("multi_baseline_safety_filter_used"):
        summary["multi_baseline_safety_filter_count"] = int(summary.get("multi_baseline_safety_filter_count", 0)) + 1
    if audit.get("hold_only_safety_filter_used"):
        summary["hold_only_safety_filter_count"] = int(summary.get("hold_only_safety_filter_count", 0)) + 1
    if audit.get("max_hold_safety_filter_used"):
        summary["max_hold_safety_filter_count"] = int(summary.get("max_hold_safety_filter_count", 0)) + 1
    if audit.get("completion_risk_filter_used"):
        summary["completion_risk_filter_count"] = int(summary.get("completion_risk_filter_count", 0)) + 1
    if audit.get("route_completion_prediction_filter_used"):
        summary["route_completion_prediction_filter_count"] = int(summary.get("route_completion_prediction_filter_count", 0)) + 1
    if audit.get("route_demand_completion_filter_used"):
        summary["route_demand_completion_filter_count"] = int(summary.get("route_demand_completion_filter_count", 0)) + 1
    if audit.get("route_demand_double_score_veto_used"):
        summary["route_demand_double_score_veto_count"] = int(summary.get("route_demand_double_score_veto_count", 0)) + 1
    if audit.get("route_horizon_completion_filter_used"):
        summary["route_horizon_completion_filter_count"] = int(summary.get("route_horizon_completion_filter_count", 0)) + 1
    if audit.get("route_horizon_dominance_filter_used"):
        summary["route_horizon_dominance_filter_count"] = int(summary.get("route_horizon_dominance_filter_count", 0)) + 1
    if audit.get("terminal_exit_protection_guard_used"):
        summary["terminal_exit_protection_guard_count"] = int(summary.get("terminal_exit_protection_guard_count", 0)) + 1
    if audit.get("route_horizon_max_pressure_envelope_used"):
        summary["route_horizon_max_pressure_envelope_count"] = int(summary.get("route_horizon_max_pressure_envelope_count", 0)) + 1
    if audit.get("route_horizon_core_baseline_envelope_used"):
        summary["route_horizon_core_baseline_envelope_count"] = int(summary.get("route_horizon_core_baseline_envelope_count", 0)) + 1
    if audit.get("route_horizon_double_pressure_envelope_used"):
        summary["route_horizon_double_pressure_envelope_count"] = int(summary.get("route_horizon_double_pressure_envelope_count", 0)) + 1
    if audit.get("route_horizon_core_minimax_guard_used"):
        summary["route_horizon_core_minimax_guard_count"] = int(summary.get("route_horizon_core_minimax_guard_count", 0)) + 1
    if audit.get("route_horizon_capacity_rescue_guard_used"):
        summary["route_horizon_capacity_rescue_guard_count"] = int(summary.get("route_horizon_capacity_rescue_guard_count", 0)) + 1
    if audit.get("route_horizon_capacity_score_envelope_used"):
        summary["route_horizon_capacity_score_envelope_count"] = int(summary.get("route_horizon_capacity_score_envelope_count", 0)) + 1
    if audit.get("route_horizon_native_capacity_score_rescue_guard_used"):
        summary["route_horizon_native_capacity_score_rescue_guard_count"] = int(summary.get("route_horizon_native_capacity_score_rescue_guard_count", 0)) + 1
    if audit.get("route_horizon_severe_double_guard_used"):
        summary["route_horizon_severe_double_guard_count"] = int(summary.get("route_horizon_severe_double_guard_count", 0)) + 1
    if audit.get("route_horizon_pressure_double_conflict_guard_used"):
        summary["route_horizon_pressure_double_conflict_guard_count"] = int(summary.get("route_horizon_pressure_double_conflict_guard_count", 0)) + 1
    if audit.get("route_horizon_completion_conflict_guard_used"):
        summary["route_horizon_completion_conflict_guard_count"] = int(summary.get("route_horizon_completion_conflict_guard_count", 0)) + 1
    if audit.get("route_horizon_capacity_completion_conflict_guard_used"):
        summary["route_horizon_capacity_completion_conflict_guard_count"] = int(summary.get("route_horizon_capacity_completion_conflict_guard_count", 0)) + 1
    if audit.get("route_horizon_early_capacity_completion_conflict_guard_used"):
        summary["route_horizon_early_capacity_completion_conflict_guard_count"] = int(summary.get("route_horizon_early_capacity_completion_conflict_guard_count", 0)) + 1
    if audit.get("route_horizon_negative_total_completion_conflict_guard_used"):
        summary["route_horizon_negative_total_completion_conflict_guard_count"] = int(summary.get("route_horizon_negative_total_completion_conflict_guard_count", 0)) + 1
    if audit.get("route_horizon_low_total_consensus_completion_guard_used"):
        summary["route_horizon_low_total_consensus_completion_guard_count"] = int(summary.get("route_horizon_low_total_consensus_completion_guard_count", 0)) + 1
    if audit.get("route_horizon_negative_total_raw_consensus_guard_used"):
        summary["route_horizon_negative_total_raw_consensus_guard_count"] = int(summary.get("route_horizon_negative_total_raw_consensus_guard_count", 0)) + 1
    if audit.get("route_horizon_core_consensus_guard_used"):
        summary["route_horizon_core_consensus_guard_count"] = int(summary.get("route_horizon_core_consensus_guard_count", 0)) + 1
    if audit.get("route_horizon_raw_consensus_guard_used"):
        summary["route_horizon_raw_consensus_guard_count"] = int(summary.get("route_horizon_raw_consensus_guard_count", 0)) + 1
    if audit.get("post_completion_veto_double_conflict_guard_used"):
        summary["post_completion_veto_double_conflict_guard_count"] = int(summary.get("post_completion_veto_double_conflict_guard_count", 0)) + 1
    if audit.get("route_horizon_pressure_safe_guard_used"):
        summary["route_horizon_pressure_safe_guard_count"] = int(summary.get("route_horizon_pressure_safe_guard_count", 0)) + 1
    if audit.get("route_horizon_tail_completion_rescue_used"):
        summary["route_horizon_tail_completion_rescue_count"] = int(summary.get("route_horizon_tail_completion_rescue_count", 0)) + 1
    if audit.get("completion_safety_veto_used"):
        summary["completion_safety_veto_count"] = int(summary.get("completion_safety_veto_count", 0)) + 1
    binding = finite_storage_binding_active(finite_storage_state)
    if binding:
        summary["binding_decision_count"] = int(summary.get("binding_decision_count", 0)) + 1
        if changed:
            summary["binding_action_changed_count"] = int(summary.get("binding_action_changed_count", 0)) + 1
    storage = state_storage_summary(finite_storage_state)
    summary["max_occupancy_ratio_observed"] = max(
        float(summary.get("max_occupancy_ratio_observed", 0.0)),
        storage["max_occupancy_ratio"],
    )
    summary["min_residual_ratio_observed"] = min(
        float(summary.get("min_residual_ratio_observed", 1.0)),
        storage["min_residual_ratio"],
    )

    selected_counts = summary.setdefault("selected_component_nonzero_counts", {field: 0 for field in ACTION_SUMMARY_COMPONENTS})
    selected_totals = audit.get("selected_component_totals", {})
    if isinstance(selected_totals, dict):
        for field in ACTION_SUMMARY_COMPONENTS:
            if abs(float(selected_totals.get(field, 0.0))) > 1e-9:
                selected_counts[field] = int(selected_counts.get(field, 0)) + 1

    any_counts = summary.setdefault("any_phase_component_nonzero_counts", {field: 0 for field in ACTION_SUMMARY_COMPONENTS})
    phase_scores = audit.get("phase_scores", {})
    if isinstance(phase_scores, dict):
        active_fields = set()
        for phase in phase_scores.values():
            totals = phase.get("component_totals") if isinstance(phase, dict) else None
            if isinstance(totals, dict):
                for field in ACTION_SUMMARY_COMPONENTS:
                    if abs(float(totals.get(field, 0.0))) > 1e-9:
                        active_fields.add(field)
        for field in active_fields:
            any_counts[field] = int(any_counts.get(field, 0)) + 1


def finalize_action_decision_summary(summary: dict[str, Any]) -> dict[str, Any]:
    finalized = dict(summary)
    total = int(finalized.get("total_decisions", 0))
    binding = int(finalized.get("binding_decision_count", 0))
    changed = int(finalized.get("action_changed_relative_to_pressure_count", 0))
    binding_changed = int(finalized.get("binding_action_changed_count", 0))
    finalized["action_change_rate"] = float(changed / total) if total else 0.0
    finalized["binding_action_change_rate"] = float(binding_changed / binding) if binding else 0.0
    finalized["binding_decision_rate"] = float(binding / total) if total else 0.0
    finalized["double_safety_fallback_rate"] = float(int(finalized.get("double_safety_fallback_count", 0)) / total) if total else 0.0
    finalized["terminal_completion_fallback_rate"] = float(int(finalized.get("terminal_completion_fallback_count", 0)) / total) if total else 0.0
    finalized["double_score_safety_filter_rate"] = float(int(finalized.get("double_score_safety_filter_count", 0)) / total) if total else 0.0
    finalized["multi_baseline_safety_filter_rate"] = float(int(finalized.get("multi_baseline_safety_filter_count", 0)) / total) if total else 0.0
    finalized["hold_only_safety_filter_rate"] = float(int(finalized.get("hold_only_safety_filter_count", 0)) / total) if total else 0.0
    finalized["max_hold_safety_filter_rate"] = float(int(finalized.get("max_hold_safety_filter_count", 0)) / total) if total else 0.0
    finalized["completion_risk_filter_rate"] = float(int(finalized.get("completion_risk_filter_count", 0)) / total) if total else 0.0
    finalized["route_completion_prediction_filter_rate"] = float(int(finalized.get("route_completion_prediction_filter_count", 0)) / total) if total else 0.0
    finalized["route_demand_completion_filter_rate"] = float(int(finalized.get("route_demand_completion_filter_count", 0)) / total) if total else 0.0
    finalized["route_demand_double_score_veto_rate"] = float(int(finalized.get("route_demand_double_score_veto_count", 0)) / total) if total else 0.0
    finalized["route_horizon_completion_filter_rate"] = float(int(finalized.get("route_horizon_completion_filter_count", 0)) / total) if total else 0.0
    finalized["route_horizon_dominance_filter_rate"] = float(int(finalized.get("route_horizon_dominance_filter_count", 0)) / total) if total else 0.0
    finalized["terminal_exit_protection_guard_rate"] = float(int(finalized.get("terminal_exit_protection_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_max_pressure_envelope_rate"] = float(int(finalized.get("route_horizon_max_pressure_envelope_count", 0)) / total) if total else 0.0
    finalized["route_horizon_core_baseline_envelope_rate"] = float(int(finalized.get("route_horizon_core_baseline_envelope_count", 0)) / total) if total else 0.0
    finalized["route_horizon_double_pressure_envelope_rate"] = float(int(finalized.get("route_horizon_double_pressure_envelope_count", 0)) / total) if total else 0.0
    finalized["route_horizon_core_minimax_guard_rate"] = float(int(finalized.get("route_horizon_core_minimax_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_capacity_rescue_guard_rate"] = float(int(finalized.get("route_horizon_capacity_rescue_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_capacity_score_envelope_rate"] = float(int(finalized.get("route_horizon_capacity_score_envelope_count", 0)) / total) if total else 0.0
    finalized["route_horizon_native_capacity_score_rescue_guard_rate"] = float(int(finalized.get("route_horizon_native_capacity_score_rescue_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_severe_double_guard_rate"] = float(int(finalized.get("route_horizon_severe_double_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_pressure_double_conflict_guard_rate"] = float(int(finalized.get("route_horizon_pressure_double_conflict_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_completion_conflict_guard_rate"] = float(int(finalized.get("route_horizon_completion_conflict_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_capacity_completion_conflict_guard_rate"] = float(int(finalized.get("route_horizon_capacity_completion_conflict_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_early_capacity_completion_conflict_guard_rate"] = float(int(finalized.get("route_horizon_early_capacity_completion_conflict_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_negative_total_completion_conflict_guard_rate"] = float(int(finalized.get("route_horizon_negative_total_completion_conflict_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_low_total_consensus_completion_guard_rate"] = float(int(finalized.get("route_horizon_low_total_consensus_completion_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_negative_total_raw_consensus_guard_rate"] = float(int(finalized.get("route_horizon_negative_total_raw_consensus_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_core_consensus_guard_rate"] = float(int(finalized.get("route_horizon_core_consensus_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_raw_consensus_guard_rate"] = float(int(finalized.get("route_horizon_raw_consensus_guard_count", 0)) / total) if total else 0.0
    finalized["post_completion_veto_double_conflict_guard_rate"] = float(int(finalized.get("post_completion_veto_double_conflict_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_pressure_safe_guard_rate"] = float(int(finalized.get("route_horizon_pressure_safe_guard_count", 0)) / total) if total else 0.0
    finalized["route_horizon_tail_completion_rescue_rate"] = float(int(finalized.get("route_horizon_tail_completion_rescue_count", 0)) / total) if total else 0.0
    finalized["completion_safety_veto_rate"] = float(int(finalized.get("completion_safety_veto_count", 0)) / total) if total else 0.0
    for key in ["selected_component_nonzero_counts", "any_phase_component_nonzero_counts"]:
        counts = finalized.get(key, {})
        finalized[key] = {field: int(counts.get(field, 0)) for field in ACTION_SUMMARY_COMPONENTS}
    return finalized


def finite_storage_movement_decomposition(
    movement: tuple[str, str],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
) -> dict[str, float]:
    upstream, downstream = movement
    up_q = float(queues.get(upstream, 0.0))
    down_q = float(queues.get(downstream, 0.0))
    pressure = up_q - down_q
    capacity = max(float(capacities.get(downstream, finite_storage_state.get("downstream_storage", {}).get(downstream, 1.0))), 1.0)
    residual = float(finite_storage_state.get("residual_receiving_capacity", {}).get(downstream, capacity))
    downstream_storage = -max(capacity - max(residual, 0.0), 0.0) if residual < min(up_q, capacity) else 0.0
    flags = _spillback_flags(finite_storage_state, downstream)
    spillback = 0.0
    if bool(flags.get("spillback", False)):
        spillback -= 0.5 * capacity
    if bool(flags.get("blocking", False)):
        spillback -= 0.5 * capacity
    urgency = float(finite_storage_state.get("service_urgency", {}).get(upstream, 0.0))
    service = max(urgency - SERVICE_URGENCY_NEUTRAL_THRESHOLD, 0.0) * max(capacity, up_q, 1.0)
    incident_state = finite_storage_state.get("incident_capacity_drop", {})
    incident = 0.0
    incident_edge = incident_state.get("edge")
    if incident_state.get("active") and incident_edge in {upstream, downstream}:
        factor = max(float(incident_state.get("factor", 1.0)), 0.0)
        incident_capacity = max(float(capacities.get(str(incident_edge), capacity)), 1.0)
        incident = -(1.0 - min(factor, 1.0)) * incident_capacity
    components = {
        "pressure": float(pressure),
        "downstream_storage": float(downstream_storage),
        "spillback": float(spillback),
        "switching": 0.0,
        "service": float(service),
        "incident": float(incident),
    }
    components["total"] = float(sum(components.values()))
    return components


def finite_storage_phase_decomposition(
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    *,
    current_phase: int | None = None,
) -> dict[str, Any]:
    movement_decompositions = []
    totals = {field: 0.0 for field in FINITE_STORAGE_DECOMPOSITION_FIELDS}
    if states:
        state = states[phase_index % len(states)]
        for move_idx, movement in enumerate(movements):
            signal = state[move_idx] if move_idx < len(state) else "r"
            if signal in "Gg":
                decomposition = finite_storage_movement_decomposition(movement, queues, capacities, finite_storage_state)
                movement_decompositions.append({"movement": list(movement), "components": decomposition})
                for field in FINITE_STORAGE_DECOMPOSITION_FIELDS:
                    totals[field] += decomposition[field]
    switching_state = finite_storage_state.get("switching_loss_state", {})
    active_phase = current_phase if current_phase is not None else switching_state.get("current_phase")
    time_since_switch = float(switching_state.get("time_since_switch", MIN_SWITCHING_HOLD_TIME))
    if active_phase is not None and int(phase_index) != int(active_phase) and time_since_switch < MIN_SWITCHING_HOLD_TIME:
        totals["switching"] -= MIN_SWITCHING_HOLD_TIME - time_since_switch
    totals["total"] = sum(value for field, value in totals.items() if field != "total")
    return {
        "phase_index": int(phase_index),
        "score": float(totals["total"]),
        "component_totals": {field: float(totals[field]) for field in sorted(FINITE_STORAGE_DECOMPOSITION_FIELDS)},
        "movement_decompositions": movement_decompositions,
    }


def _score_weighted_decomposition(decomposition: dict[str, Any], weights: dict[str, float]) -> dict[str, Any]:
    weighted = dict(decomposition)
    component_totals = {
        field: float(value) * float(weights.get(field, 1.0))
        for field, value in dict(decomposition.get("component_totals", {})).items()
    }
    component_totals["total"] = sum(value for field, value in component_totals.items() if field != "total")
    weighted["component_totals"] = component_totals
    weighted["score"] = float(component_totals["total"])
    weighted["score_variant"] = "finite_storage_primal_dual_v1_4_score"
    weighted["score_weights"] = {field: float(weights.get(field, 1.0)) for field in sorted(FINITE_STORAGE_DECOMPOSITION_FIELDS)}
    return weighted


def build_downstream_adjacency(tls_movements: dict[str, list[tuple[str, str]]]) -> dict[str, list[str]]:
    adjacency: dict[str, set[str]] = {}
    for movements in tls_movements.values():
        for upstream, downstream in movements:
            adjacency.setdefault(str(upstream), set()).add(str(downstream))
            adjacency.setdefault(str(downstream), set())
    return {edge: sorted(children) for edge, children in adjacency.items()}


def initialize_dynamic_dual_state(edge_ids: list[str]) -> dict[str, dict[str, float]]:
    return {
        edge: {
            "storage_price": 0.0,
            "release_price": 0.0,
            "cascade_price": 0.0,
            "service_age": 0.0,
        }
        for edge in edge_ids
    }


def update_dynamic_dual_state(
    dual_state: dict[str, dict[str, float]],
    finite_storage_state: dict[str, Any],
    downstream_adjacency: dict[str, list[str]],
    params: dict[str, float] | None = None,
) -> dict[str, dict[str, float]]:
    params = params or DYNAMIC_V1_5_PARAMS
    decay = float(params["dual_decay"])
    storage_threshold = float(params["storage_threshold"])
    release_threshold = float(params["release_threshold"])
    for edge in finite_storage_state.get("downstream_storage", {}):
        dual_state.setdefault(
            str(edge),
            {"storage_price": 0.0, "release_price": 0.0, "cascade_price": 0.0, "service_age": 0.0},
        )

    def max_descendant_slack_ratio(edge: str, depth: int) -> float:
        frontier = list(downstream_adjacency.get(edge, []))
        visited: set[str] = set()
        best = 0.0
        remaining_depth = max(int(depth), 0)
        while frontier and remaining_depth > 0:
            next_frontier: list[str] = []
            for child in frontier:
                child = str(child)
                if child in visited:
                    continue
                visited.add(child)
                child_capacity = max(float(finite_storage_state.get("downstream_storage", {}).get(child, 1.0)), 1.0)
                child_residual = float(finite_storage_state.get("residual_receiving_capacity", {}).get(child, 0.0))
                best = max(best, child_residual / child_capacity)
                next_frontier.extend(downstream_adjacency.get(child, []))
            frontier = next_frontier
            remaining_depth -= 1

        return float(best)

    def max_immediate_child_slack_ratio(edge: str) -> float:
        best = 0.0
        for child in downstream_adjacency.get(edge, []):
            child_capacity = max(float(finite_storage_state.get("downstream_storage", {}).get(child, 1.0)), 1.0)
            child_residual = float(finite_storage_state.get("residual_receiving_capacity", {}).get(child, 0.0))
            best = max(best, child_residual / child_capacity)
        return float(best)

    for edge, values in dual_state.items():
        flags = _spillback_flags(finite_storage_state, edge)
        occupancy = float(flags.get("occupancy_ratio", 0.0))
        storage_violation = max(occupancy - storage_threshold, 0.0)
        service_violation = max(float(finite_storage_state.get("service_urgency", {}).get(edge, 0.0)) - SERVICE_URGENCY_NEUTRAL_THRESHOLD, 0.0)
        descendant_depth = int(params.get("release_descendant_slack_depth", 1.0))
        slack_threshold = float(params.get("release_descendant_slack_threshold", 0.15))
        descendant_slack_ratio = max_descendant_slack_ratio(str(edge), descendant_depth)
        immediate_child_slack_ratio = max_immediate_child_slack_ratio(str(edge))
        descendant_support_weight = float(params.get("release_descendant_support_weight", 1.0))
        local_child_slack_floor = params.get("release_local_child_slack_floor")
        descendant_occupancy_threshold = params.get("release_descendant_occupancy_threshold")
        local_child_support_ok = True
        if local_child_slack_floor is not None:
            local_child_support_ok = immediate_child_slack_ratio > float(local_child_slack_floor)
        severe_occupancy_ok = True
        if descendant_occupancy_threshold is not None:
            severe_occupancy_ok = occupancy > float(descendant_occupancy_threshold)
        release_support = 0.0
        if immediate_child_slack_ratio > slack_threshold:
            release_support = 1.0
        elif (
            descendant_slack_ratio > slack_threshold
            and local_child_support_ok
            and severe_occupancy_ok
        ):
            release_support = descendant_support_weight
        release_violation = max(occupancy - release_threshold, 0.0) * release_support
        values["storage_price"] = max(
            (1.0 - decay) * float(values.get("storage_price", 0.0))
            + float(params["dual_step_size"]) * storage_violation,
            0.0,
        )
        values["release_price"] = max(
            (1.0 - decay) * float(values.get("release_price", 0.0))
            + float(params["release_step_size"]) * release_violation,
            0.0,
        )
        values["service_age"] = max((1.0 - decay) * float(values.get("service_age", 0.0)) + service_violation, 0.0)

    for edge, values in dual_state.items():
        cascade = 0.0
        for child in downstream_adjacency.get(edge, []):
            child_state = dual_state.get(child, {})
            cascade += 0.70 * float(child_state.get("storage_price", 0.0))
            for grandchild in downstream_adjacency.get(child, []):
                cascade += 0.30 * float(dual_state.get(grandchild, {}).get("storage_price", 0.0))
        values["cascade_price"] = float(cascade)
    return dual_state


def update_completion_dual_state(
    dual_state: dict[str, dict[str, float]],
    finite_storage_state: dict[str, Any],
    *,
    step: int | None = None,
    warmup: int | None = None,
    steps: int | None = None,
    params: dict[str, float] | None = None,
) -> dict[str, dict[str, float]]:
    params = params or DYNAMIC_V1_6_PARAMS
    decay = float(params["nu_decay"])
    step_size = float(params["nu_step_size"])
    deficit_threshold = float(params["completion_deficit_threshold"])
    horizon_frac = float(params["completion_horizon_fraction"])
    total = (warmup or 0) + (steps or 300)
    remaining = max(total - (step or 0), 0)
    in_completion_zone = remaining / max(total, 1) <= (1.0 - horizon_frac)
    for edge in finite_storage_state.get("downstream_storage", {}):
        edge_str = str(edge)
        dual_state.setdefault(edge_str, {
            "storage_price": 0.0,
            "release_price": 0.0,
            "cascade_price": 0.0,
            "service_age": 0.0,
            "completion_price": 0.0,
        })
    if not in_completion_zone:
        for edge, values in dual_state.items():
            values["completion_price"] = max(
                (1.0 - decay) * float(values.get("completion_price", 0.0)),
                0.0,
            )
        return dual_state
    for edge, values in dual_state.items():
        occupancy = float(finite_storage_state.get("downstream_storage", {}).get(edge, 0.0))
        capacity = max(float(finite_storage_state.get("downstream_storage", {}).get(edge, 1.0)), 1.0)
        occupancy_ratio = min(occupancy / capacity, 1.0) if capacity > 0 else 0.0
        residual_cap = float(finite_storage_state.get("residual_receiving_capacity", {}).get(edge, 0.0))
        exit_demand = occupancy * (1.0 - occupancy_ratio * 0.5)
        exit_capacity = residual_cap + capacity * 0.1
        deficit_ratio = max(exit_demand - exit_capacity, 0.0) / max(exit_demand, 1.0) if exit_demand > 0 else 0.0
        deficit_violation = max(deficit_ratio - deficit_threshold, 0.0)
        values["completion_price"] = max(
            (1.0 - decay) * float(values.get("completion_price", 0.0))
            + step_size * deficit_violation,
            0.0,
        )
    return dual_state


def dynamic_v1_5_movement_decomposition(
    movement: tuple[str, str],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    dual_state: dict[str, dict[str, float]],
    params: dict[str, float] | None = None,
) -> dict[str, float]:
    params = params or DYNAMIC_V1_5_PARAMS
    upstream, downstream = movement
    up_q = float(queues.get(upstream, 0.0))
    down_q = float(queues.get(downstream, 0.0))
    upstream_queue = max(float(queues.get(upstream, 0.0)), 1.0)
    downstream_capacity = max(float(capacities.get(downstream, finite_storage_state.get("downstream_storage", {}).get(downstream, 1.0))), 1.0)
    if params.get("base_score_variant") == "finite_storage_double_scaffold":
        slack = downstream_capacity - down_q
        fullness = down_q / downstream_capacity
        blocked_penalty = downstream_capacity if fullness >= 0.85 else 0.0
        double_pressure = max(up_q - max(slack, 0.0), 0.0)
        base = {
            "pressure": float(up_q - down_q),
            "downstream_storage": 0.0,
            "spillback": 0.0,
            "switching": 0.0,
            "service": 0.0,
            "incident": 0.0,
            "double_pressure_scaffold": float(0.05 * slack - fullness * up_q - blocked_penalty - double_pressure),
        }
    else:
        base = finite_storage_movement_decomposition(movement, queues, capacities, finite_storage_state)
        base["double_pressure_scaffold"] = 0.0
    upstream_dual = dual_state.get(upstream, {})
    downstream_dual = dual_state.get(downstream, {})
    storage_price = -float(params["beta_storage"]) * float(downstream_dual.get("storage_price", 0.0)) * upstream_queue
    cascade_price = -float(params["gamma_cascade"]) * float(downstream_dual.get("cascade_price", 0.0)) * upstream_queue
    release_value = float(params["alpha_release"]) * float(upstream_dual.get("release_price", 0.0)) * upstream_queue
    service_age = float(params["delta_service"]) * float(upstream_dual.get("service_age", 0.0)) * downstream_capacity
    completion_price = -float(params.get("kappa_completion", 0.0)) * float(downstream_dual.get("completion_price", 0.0)) * upstream_queue
    components = {
        "pressure": float(base["pressure"]),
        "downstream_storage": float(base["downstream_storage"]),
        "spillback": float(base["spillback"]),
        "switching": float(base["switching"]),
        "service": float(base["service"]),
        "incident": float(base["incident"]),
        "storage_price": float(storage_price),
        "cascade_price": float(cascade_price),
        "release": float(release_value),
        "service_age": float(service_age),
        "double_pressure_scaffold": float(base.get("double_pressure_scaffold", 0.0)),
        "completion_price": float(completion_price),
    }
    components["total"] = float(sum(value for field, value in components.items() if field != "total"))
    return components


def dynamic_v1_5_phase_decomposition(
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    dual_state: dict[str, dict[str, float]],
    *,
    current_phase: int | None = None,
    params: dict[str, float] | None = None,
    score_variant: str = "finite_storage_dynamic_primal_dual_v1_5",
) -> dict[str, Any]:
    params = params or DYNAMIC_V1_5_PARAMS
    movement_decompositions = []
    totals: dict[str, float] = {
        "pressure": 0.0,
        "downstream_storage": 0.0,
        "spillback": 0.0,
        "switching": 0.0,
        "service": 0.0,
        "incident": 0.0,
        "storage_price": 0.0,
        "cascade_price": 0.0,
        "release": 0.0,
        "service_age": 0.0,
        "guardrail": 0.0,
        "total": 0.0,
    }
    if states:
        state = states[phase_index % len(states)]
        for move_idx, movement in enumerate(movements):
            signal = state[move_idx] if move_idx < len(state) else "r"
            if signal in "Gg":
                decomposition = dynamic_v1_5_movement_decomposition(
                    movement,
                    queues,
                    capacities,
                    finite_storage_state,
                    dual_state,
                    params=params,
                )
                movement_decompositions.append({"movement": list(movement), "components": decomposition})
                for field, value in decomposition.items():
                    totals[field] = totals.get(field, 0.0) + float(value)
    switching_state = finite_storage_state.get("switching_loss_state", {})
    active_phase = current_phase if current_phase is not None else switching_state.get("current_phase")
    time_since_switch = float(switching_state.get("time_since_switch", MIN_SWITCHING_HOLD_TIME))
    if active_phase is not None and int(phase_index) != int(active_phase) and time_since_switch < MIN_SWITCHING_HOLD_TIME:
        totals["switching"] -= MIN_SWITCHING_HOLD_TIME - time_since_switch
    totals["total"] = sum(value for field, value in totals.items() if field != "total")
    if "correction_cap_ratio" in params:
        pressure = float(totals.get("pressure", 0.0))
        protected_scaffold = float(totals.get("double_pressure_scaffold", 0.0))
        correction = float(totals["total"] - pressure - protected_scaffold)
        cap = float(params["correction_cap_ratio"]) * max(
            abs(pressure),
            float(params.get("correction_cap_floor", 0.0)),
            1.0,
        )
        if correction < -cap:
            guardrail = -cap - correction
            totals["guardrail"] = float(guardrail)
            totals["total"] = float(pressure + protected_scaffold - cap)
    return {
        "phase_index": int(phase_index),
        "score": float(totals["total"]),
        "component_totals": {field: float(totals[field]) for field in sorted(totals)},
        "movement_decompositions": movement_decompositions,
        "score_variant": score_variant,
    }


def phase_completion_service_score(
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
) -> float:
    if not states:
        return 0.0
    state = states[phase_index % len(states)]
    service = 0.0
    for move_idx, movement in enumerate(movements):
        signal = state[move_idx] if move_idx < len(state) else "r"
        if signal in "Gg":
            upstream, _downstream = movement
            service += max(float(queues.get(upstream, 0.0)), 0.0)
    return float(service)


def phase_route_completion_prediction_score(
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    params: dict[str, float] | None = None,
) -> float:
    params = params or {}
    if not states:
        return 0.0
    state = states[phase_index % len(states)]
    score = 0.0
    residuals = finite_storage_state.get("residual_receiving_capacity", {})
    storage_caps = finite_storage_state.get("downstream_storage", {})
    slack_floor = float(params.get("route_completion_slack_floor", 0.0))
    occupancy_penalty = float(params.get("route_completion_occupancy_penalty", 0.0))
    for move_idx, movement in enumerate(movements):
        signal = state[move_idx] if move_idx < len(state) else "r"
        if signal not in "Gg":
            continue
        upstream, downstream = movement
        upstream_queue = max(float(queues.get(upstream, 0.0)), 0.0)
        capacity = max(float(capacities.get(downstream, storage_caps.get(downstream, 1.0))), 1.0)
        residual_ratio = max(float(residuals.get(downstream, capacity)) / capacity, 0.0)
        occupancy = float(_spillback_flags(finite_storage_state, downstream).get("occupancy_ratio", 0.0))
        receiver_constrained_service = upstream_queue * max(residual_ratio, slack_floor)
        score += receiver_constrained_service - occupancy_penalty * upstream_queue * occupancy
    return float(score)


def movement_key(movement: tuple[str, str]) -> str:
    return f"{movement[0]}->{movement[1]}"


def build_active_route_completion_state(
    edge_ids: list[str],
    *,
    edge_free_flow_times: dict[str, float] | None = None,
    remaining_time: float | None = None,
) -> dict[str, Any]:
    edge_set = set(edge_ids)
    edge_free_flow_times = edge_free_flow_times or {}
    movement_demand: dict[str, float] = {}
    finishable_movement_demand: dict[str, float] = {}
    movement_remaining_time_sum: dict[str, float] = {}
    remaining_edge_demand = {edge: 0.0 for edge in edge_ids}
    active_vehicle_count = 0
    for veh_id in traci.vehicle.getIDList():
        try:
            current_edge = str(traci.vehicle.getRoadID(veh_id))
            route = [str(edge) for edge in traci.vehicle.getRoute(veh_id)]
            route_index = int(traci.vehicle.getRouteIndex(veh_id))
        except traci.TraCIException:
            continue
        if current_edge.startswith(":") or current_edge not in edge_set or not route:
            continue
        if route_index < 0 or route_index >= len(route) or route[route_index] != current_edge:
            try:
                route_index = route.index(current_edge)
            except ValueError:
                continue
        active_vehicle_count += 1
        for edge in route[route_index:]:
            if edge in remaining_edge_demand:
                remaining_edge_demand[edge] += 1.0
        if route_index + 1 < len(route):
            next_edge = route[route_index + 1]
            if next_edge in edge_set:
                key = f"{current_edge}->{next_edge}"
                movement_demand[key] = movement_demand.get(key, 0.0) + 1.0
                remaining_after_movement = sum(
                    float(edge_free_flow_times.get(edge, 0.0))
                    for edge in route[route_index + 1 :]
                    if edge in edge_set
                )
                movement_remaining_time_sum[key] = movement_remaining_time_sum.get(key, 0.0) + remaining_after_movement
                if remaining_time is None or remaining_after_movement <= max(float(remaining_time), 0.0):
                    finishable_movement_demand[key] = finishable_movement_demand.get(key, 0.0) + 1.0
    return {
        "movement_demand": movement_demand,
        "finishable_movement_demand": finishable_movement_demand,
        "movement_remaining_time_sum": movement_remaining_time_sum,
        "remaining_edge_demand": remaining_edge_demand,
        "active_vehicle_count": active_vehicle_count,
        "remaining_time": None if remaining_time is None else float(remaining_time),
    }


def unavailable_route_completion_state() -> dict[str, Any]:
    return {
        "movement_demand": {},
        "finishable_movement_demand": {},
        "movement_remaining_time_sum": {},
        "remaining_edge_demand": {},
        "active_vehicle_count": 0,
        "remaining_time": None,
    }


def phase_route_demand_completion_score(
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    route_completion_state: dict[str, Any],
    params: dict[str, float] | None = None,
) -> float:
    params = params or {}
    if not states:
        return 0.0
    state = states[phase_index % len(states)]
    score = 0.0
    residuals = finite_storage_state.get("residual_receiving_capacity", {})
    storage_caps = finite_storage_state.get("downstream_storage", {})
    movement_demand = route_completion_state.get("movement_demand", {})
    remaining_edge_demand = route_completion_state.get("remaining_edge_demand", {})
    slack_floor = float(params.get("route_demand_slack_floor", 0.0))
    queue_blend = float(params.get("route_demand_queue_blend", 0.0))
    downstream_penalty = float(params.get("route_demand_downstream_penalty", 0.0))
    for move_idx, movement in enumerate(movements):
        signal = state[move_idx] if move_idx < len(state) else "r"
        if signal not in "Gg":
            continue
        upstream, downstream = movement
        demand = float(movement_demand.get(movement_key(movement), 0.0))
        blended_demand = demand + queue_blend * max(float(queues.get(upstream, 0.0)) - demand, 0.0)
        capacity = max(float(capacities.get(downstream, storage_caps.get(downstream, 1.0))), 1.0)
        residual_ratio = max(float(residuals.get(downstream, capacity)) / capacity, 0.0)
        downstream_route_pressure = float(remaining_edge_demand.get(downstream, 0.0)) / capacity
        score += blended_demand * max(residual_ratio, slack_floor) - downstream_penalty * downstream_route_pressure
    return float(score)


def phase_route_horizon_completion_decomposition(
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    route_completion_state: dict[str, Any],
    params: dict[str, float] | None = None,
    *,
    queues: dict[str, float] | None = None,
) -> dict[str, Any]:
    params = params or {}
    if not states:
        return {
            "score": 0.0,
            "components": {
                "finishable_term": 0.0,
                "downstream_penalty": 0.0,
                "local_pressure_penalty": 0.0,
            },
            "movement_details": [],
        }
    state = states[phase_index % len(states)]
    score = 0.0
    finishable_term_total = 0.0
    downstream_penalty_total = 0.0
    local_pressure_penalty_total = 0.0
    residuals = finite_storage_state.get("residual_receiving_capacity", {})
    storage_caps = finite_storage_state.get("downstream_storage", {})
    finishable = route_completion_state.get("finishable_movement_demand", {})
    movement_demand = route_completion_state.get("movement_demand", {})
    remaining_time_sum = route_completion_state.get("movement_remaining_time_sum", {})
    remaining_edge_demand = route_completion_state.get("remaining_edge_demand", {})
    slack_floor = float(params.get("route_horizon_slack_floor", 0.0))
    residual_power = max(float(params.get("route_horizon_residual_power", 1.0)), 0.0)
    finishable_power = max(float(params.get("route_horizon_finishable_power", 1.0)), 0.0)
    total_demand_power = max(float(params.get("route_horizon_total_demand_power", 0.0)), 0.0)
    time_weight_power = max(float(params.get("route_horizon_time_weight_power", 1.0)), 0.0)
    conditional_phase_time_weight_power = max(
        float(params.get("route_horizon_conditional_phase_time_weight_power", time_weight_power)),
        0.0,
    )
    conditional_phase_time_weight_max_local_pressure_ceiling = float(
        params.get("route_horizon_conditional_phase_time_weight_max_local_pressure_ceiling", float("-inf"))
    )
    conditional_phase_time_weight_phase_residual_ceiling = float(
        params.get("route_horizon_conditional_phase_time_weight_phase_residual_ceiling", float("-inf"))
    )
    conditional_phase_time_weight_phase_downstream_pressure_floor = float(
        params.get("route_horizon_conditional_phase_time_weight_phase_downstream_pressure_floor", float("-inf"))
    )
    conditional_phase_time_weight_movement_residual_ceiling = float(
        params.get("route_horizon_conditional_phase_time_weight_movement_residual_ceiling", float("inf"))
    )
    conditional_phase_time_weight_movement_downstream_pressure_floor = float(
        params.get("route_horizon_conditional_phase_time_weight_movement_downstream_pressure_floor", float("-inf"))
    )
    conditional_phase_time_weight_local_pressure_ceiling = float(
        params.get("route_horizon_conditional_phase_time_weight_local_pressure_ceiling", float("inf"))
    )
    secondary_phase_time_weight_power = max(
        float(params.get("route_horizon_secondary_phase_time_weight_power", time_weight_power)),
        0.0,
    )
    secondary_phase_time_weight_max_local_pressure_ceiling = float(
        params.get("route_horizon_secondary_phase_time_weight_max_local_pressure_ceiling", float("-inf"))
    )
    secondary_phase_time_weight_phase_residual_ceiling = float(
        params.get("route_horizon_secondary_phase_time_weight_phase_residual_ceiling", float("-inf"))
    )
    secondary_phase_time_weight_local_pressure_ceiling = float(
        params.get("route_horizon_secondary_phase_time_weight_local_pressure_ceiling", float("inf"))
    )
    secondary_phase_time_weight_movement_residual_floor = float(
        params.get("route_horizon_secondary_phase_time_weight_movement_residual_floor", float("-inf"))
    )
    secondary_phase_time_weight_movement_residual_ceiling = float(
        params.get("route_horizon_secondary_phase_time_weight_movement_residual_ceiling", float("inf"))
    )
    secondary_phase_time_weight_movement_downstream_pressure_floor = float(
        params.get("route_horizon_secondary_phase_time_weight_movement_downstream_pressure_floor", float("-inf"))
    )
    no_positive_pressure_finishable_count_power = max(
        float(params.get("route_horizon_no_positive_pressure_finishable_count_power", 0.0)),
        0.0,
    )
    no_positive_pressure_finishable_count_max_local_pressure_ceiling = float(
        params.get("route_horizon_no_positive_pressure_finishable_count_max_local_pressure_ceiling", float("-inf"))
    )
    no_positive_pressure_finishable_count_phase_downstream_pressure_floor = float(
        params.get("route_horizon_no_positive_pressure_finishable_count_phase_downstream_pressure_floor", float("-inf"))
    )
    no_positive_pressure_finishable_count_min_count = max(
        int(float(params.get("route_horizon_no_positive_pressure_finishable_count_min_count", 2.0))),
        2,
    )
    conditional_movement_finishable_power = max(
        float(params.get("route_horizon_conditional_movement_finishable_power", finishable_power)),
        0.0,
    )
    conditional_movement_finishable_power_max_local_pressure_ceiling = float(
        params.get("route_horizon_conditional_movement_finishable_power_max_local_pressure_ceiling", float("-inf"))
    )
    conditional_movement_finishable_power_phase_downstream_pressure_floor = float(
        params.get("route_horizon_conditional_movement_finishable_power_phase_downstream_pressure_floor", float("-inf"))
    )
    conditional_movement_finishable_power_movement_finishable_floor = float(
        params.get("route_horizon_conditional_movement_finishable_power_movement_finishable_floor", float("inf"))
    )
    no_positive_pressure_big_finishable_count_power = max(
        float(params.get("route_horizon_no_positive_pressure_big_finishable_count_power", 0.0)),
        0.0,
    )
    no_positive_pressure_big_finishable_count_max_local_pressure_ceiling = float(
        params.get("route_horizon_no_positive_pressure_big_finishable_count_max_local_pressure_ceiling", float("-inf"))
    )
    no_positive_pressure_big_finishable_count_phase_downstream_pressure_floor = float(
        params.get("route_horizon_no_positive_pressure_big_finishable_count_phase_downstream_pressure_floor", float("-inf"))
    )
    no_positive_pressure_big_finishable_count_movement_finishable_floor = float(
        params.get("route_horizon_no_positive_pressure_big_finishable_count_movement_finishable_floor", float("inf"))
    )
    no_positive_pressure_big_finishable_count_min_count = max(
        int(float(params.get("route_horizon_no_positive_pressure_big_finishable_count_min_count", 2.0))),
        2,
    )
    no_positive_pressure_multi_big_finishable_power = max(
        float(params.get("route_horizon_no_positive_pressure_multi_big_finishable_power", finishable_power)),
        0.0,
    )
    no_positive_pressure_multi_big_finishable_power_max_local_pressure_ceiling = float(
        params.get("route_horizon_no_positive_pressure_multi_big_finishable_power_max_local_pressure_ceiling", float("-inf"))
    )
    no_positive_pressure_multi_big_finishable_power_phase_downstream_pressure_floor = float(
        params.get("route_horizon_no_positive_pressure_multi_big_finishable_power_phase_downstream_pressure_floor", float("-inf"))
    )
    no_positive_pressure_multi_big_finishable_power_movement_finishable_floor = float(
        params.get("route_horizon_no_positive_pressure_multi_big_finishable_power_movement_finishable_floor", float("inf"))
    )
    no_positive_pressure_multi_big_finishable_power_min_count = max(
        int(float(params.get("route_horizon_no_positive_pressure_multi_big_finishable_power_min_count", 2.0))),
        2,
    )
    no_positive_pressure_big_finishable_sum_power = max(
        float(params.get("route_horizon_no_positive_pressure_big_finishable_sum_power", 0.0)),
        0.0,
    )
    no_positive_pressure_big_finishable_sum_floor = max(
        float(params.get("route_horizon_no_positive_pressure_big_finishable_sum_floor", 0.0)),
        0.0,
    )
    no_positive_pressure_big_finishable_sum_max_local_pressure_ceiling = float(
        params.get("route_horizon_no_positive_pressure_big_finishable_sum_max_local_pressure_ceiling", float("-inf"))
    )
    no_positive_pressure_big_finishable_sum_phase_downstream_pressure_floor = float(
        params.get("route_horizon_no_positive_pressure_big_finishable_sum_phase_downstream_pressure_floor", float("-inf"))
    )
    no_positive_pressure_big_finishable_sum_movement_finishable_floor = float(
        params.get("route_horizon_no_positive_pressure_big_finishable_sum_movement_finishable_floor", float("inf"))
    )
    no_positive_pressure_big_finishable_sum_phase_residual_ceiling = float(
        params.get("route_horizon_no_positive_pressure_big_finishable_sum_phase_residual_ceiling", float("inf"))
    )
    time_discount = float(params.get("route_horizon_time_discount", 1.0))
    downstream_penalty = float(params.get("route_horizon_downstream_penalty", 0.0))
    local_pressure_penalty = float(params.get("route_horizon_local_pressure_penalty", 0.0))
    local_pressure_floor = float(params.get("route_horizon_local_pressure_floor", 0.0))
    remaining_horizon = route_completion_state.get("remaining_time")
    relative_urgency = bool(params.get("route_horizon_relative_time_urgency"))
    deadline_urgency = bool(params.get("route_horizon_deadline_time_urgency"))
    urgency_power = max(float(params.get("route_horizon_urgency_power", 1.0)), 0.0)
    deadline_base_weight = max(float(params.get("route_horizon_deadline_base_weight", 0.0)), 0.0)
    movement_details: list[dict[str, float | str]] = []
    unique_movement_terms = bool(params.get("route_horizon_unique_movement_terms"))
    seen_movement_keys: set[str] = set()
    green_movement_rows: list[dict[str, float | str]] = []
    for move_idx, movement in enumerate(movements):
        signal = state[move_idx] if move_idx < len(state) else "r"
        if signal not in "Gg":
            continue
        upstream, downstream = movement
        key = movement_key(movement)
        if unique_movement_terms and key in seen_movement_keys:
            continue
        seen_movement_keys.add(key)
        finishable_demand = float(finishable.get(key, 0.0))
        total_demand = max(float(movement_demand.get(key, 0.0)), finishable_demand, 1.0)
        avg_remaining_time = float(remaining_time_sum.get(key, 0.0)) / total_demand
        capacity = max(float(capacities.get(downstream, storage_caps.get(downstream, 1.0))), 1.0)
        residual_ratio = max(float(residuals.get(downstream, capacity)) / capacity, 0.0)
        downstream_route_pressure = float(remaining_edge_demand.get(downstream, 0.0)) / capacity
        local_pressure = 0.0
        if queues is not None:
            local_pressure = float(queues.get(upstream, 0.0)) - float(queues.get(downstream, 0.0))
        effective_slack_floor = slack_floor
        if (
            params.get("route_horizon_zero_slack_floor_for_nonpositive_pressure")
            and local_pressure <= float(params.get("route_horizon_zero_slack_floor_pressure_ceiling", 0.0))
        ):
            effective_slack_floor = 0.0
        if deadline_urgency and remaining_horizon is not None and float(remaining_horizon) > 0.0:
            finish_slack = max(float(remaining_horizon) - avg_remaining_time, 0.0) / max(float(remaining_horizon), 1.0)
            time_weight = deadline_base_weight + max(1.0 - finish_slack, 0.0) ** urgency_power
        elif relative_urgency and remaining_horizon is not None and float(remaining_horizon) > 0.0:
            finish_slack = max(float(remaining_horizon) - avg_remaining_time, 0.0) / max(float(remaining_horizon), 1.0)
            time_weight = finish_slack**urgency_power
        else:
            time_weight = 1.0 / (1.0 + time_discount * avg_remaining_time / 60.0)
        green_movement_rows.append(
            {
                "movement": movement_key(movement),
                "finishable_demand": float(finishable_demand),
                "total_demand": float(total_demand),
                "avg_remaining_time": float(avg_remaining_time),
                "residual_ratio": float(residual_ratio),
                "effective_slack_floor": float(effective_slack_floor),
                "downstream_route_pressure": float(downstream_route_pressure),
                "local_pressure": float(local_pressure),
                "time_weight": float(time_weight),
            }
        )
    phase_max_local_pressure = max(
        (float(row["local_pressure"]) for row in green_movement_rows),
        default=float("-inf"),
    )
    phase_min_residual_ratio = min(
        (float(row["residual_ratio"]) for row in green_movement_rows),
        default=float("inf"),
    )
    phase_max_downstream_route_pressure = max(
        (float(row["downstream_route_pressure"]) for row in green_movement_rows),
        default=float("-inf"),
    )
    positive_finishable_count = sum(1 for row in green_movement_rows if float(row["finishable_demand"]) > 0.0)
    positive_big_finishable_count = sum(
        1
        for row in green_movement_rows
        if float(row["finishable_demand"]) > no_positive_pressure_big_finishable_count_movement_finishable_floor
    )
    positive_big_finishable_sum = sum(
        float(row["finishable_demand"])
        for row in green_movement_rows
        if float(row["finishable_demand"]) > no_positive_pressure_big_finishable_sum_movement_finishable_floor
    )
    use_conditional_phase_time_weight = (
        conditional_phase_time_weight_power > time_weight_power
        and phase_max_local_pressure <= conditional_phase_time_weight_max_local_pressure_ceiling
        and phase_min_residual_ratio <= conditional_phase_time_weight_phase_residual_ceiling
        and phase_max_downstream_route_pressure >= conditional_phase_time_weight_phase_downstream_pressure_floor
    )
    use_secondary_phase_time_weight = (
        secondary_phase_time_weight_power > time_weight_power
        and phase_max_local_pressure <= secondary_phase_time_weight_max_local_pressure_ceiling
        and phase_min_residual_ratio <= secondary_phase_time_weight_phase_residual_ceiling
    )
    use_no_positive_pressure_finishable_count_normalization = (
        no_positive_pressure_finishable_count_power > 0.0
        and positive_finishable_count >= no_positive_pressure_finishable_count_min_count
        and phase_max_local_pressure <= no_positive_pressure_finishable_count_max_local_pressure_ceiling
        and phase_max_downstream_route_pressure
        >= no_positive_pressure_finishable_count_phase_downstream_pressure_floor
    )
    use_conditional_movement_finishable_power = (
        conditional_movement_finishable_power < finishable_power
        and phase_max_local_pressure <= conditional_movement_finishable_power_max_local_pressure_ceiling
        and phase_max_downstream_route_pressure >= conditional_movement_finishable_power_phase_downstream_pressure_floor
    )
    use_no_positive_pressure_big_finishable_count_normalization = (
        no_positive_pressure_big_finishable_count_power > 0.0
        and positive_big_finishable_count >= no_positive_pressure_big_finishable_count_min_count
        and phase_max_local_pressure <= no_positive_pressure_big_finishable_count_max_local_pressure_ceiling
        and phase_max_downstream_route_pressure
        >= no_positive_pressure_big_finishable_count_phase_downstream_pressure_floor
    )
    use_no_positive_pressure_multi_big_finishable_power = (
        no_positive_pressure_multi_big_finishable_power < finishable_power
        and positive_big_finishable_count >= no_positive_pressure_multi_big_finishable_power_min_count
        and phase_max_local_pressure <= no_positive_pressure_multi_big_finishable_power_max_local_pressure_ceiling
        and phase_max_downstream_route_pressure
        >= no_positive_pressure_multi_big_finishable_power_phase_downstream_pressure_floor
    )
    use_no_positive_pressure_big_finishable_sum_normalization = (
        no_positive_pressure_big_finishable_sum_power > 0.0
        and positive_big_finishable_sum >= no_positive_pressure_big_finishable_sum_floor
        and phase_max_local_pressure <= no_positive_pressure_big_finishable_sum_max_local_pressure_ceiling
        and phase_max_downstream_route_pressure >= no_positive_pressure_big_finishable_sum_phase_downstream_pressure_floor
        and phase_min_residual_ratio <= no_positive_pressure_big_finishable_sum_phase_residual_ceiling
    )
    for row in green_movement_rows:
        effective_time_weight_power = time_weight_power
        if (
            use_conditional_phase_time_weight
            and float(row["local_pressure"]) <= conditional_phase_time_weight_local_pressure_ceiling
            and float(row["residual_ratio"]) <= conditional_phase_time_weight_movement_residual_ceiling
            and float(row["downstream_route_pressure"]) >= conditional_phase_time_weight_movement_downstream_pressure_floor
        ):
            effective_time_weight_power = conditional_phase_time_weight_power
        elif (
            use_secondary_phase_time_weight
            and float(row["local_pressure"]) <= secondary_phase_time_weight_local_pressure_ceiling
            and secondary_phase_time_weight_movement_residual_floor < float(row["residual_ratio"])
            <= secondary_phase_time_weight_movement_residual_ceiling
            and float(row["downstream_route_pressure"]) >= secondary_phase_time_weight_movement_downstream_pressure_floor
        ):
            effective_time_weight_power = secondary_phase_time_weight_power
        effective_time_weight = float(row["time_weight"]) ** effective_time_weight_power
        effective_residual_ratio = max(float(row["residual_ratio"]), float(row["effective_slack_floor"])) ** residual_power
        finishable_demand = float(row["finishable_demand"])
        total_demand = float(row["total_demand"])
        effective_finishable_power = finishable_power
        if (
            use_conditional_movement_finishable_power
            and finishable_demand > conditional_movement_finishable_power_movement_finishable_floor
            and float(row["local_pressure"]) <= conditional_movement_finishable_power_max_local_pressure_ceiling
        ):
            effective_finishable_power = conditional_movement_finishable_power
        if (
            use_no_positive_pressure_multi_big_finishable_power
            and finishable_demand > no_positive_pressure_multi_big_finishable_power_movement_finishable_floor
            and float(row["local_pressure"]) <= no_positive_pressure_multi_big_finishable_power_max_local_pressure_ceiling
        ):
            effective_finishable_power = min(
                effective_finishable_power,
                no_positive_pressure_multi_big_finishable_power,
            )
        effective_finishable_demand = finishable_demand**effective_finishable_power if finishable_demand > 0.0 else 0.0
        effective_total_demand = total_demand**total_demand_power if total_demand > 0.0 else 1.0
        effective_finishable_count_scale = 1.0
        if use_no_positive_pressure_finishable_count_normalization and finishable_demand > 0.0:
            effective_finishable_count_scale = positive_finishable_count**no_positive_pressure_finishable_count_power
        effective_big_finishable_count_scale = 1.0
        if (
            use_no_positive_pressure_big_finishable_count_normalization
            and finishable_demand > no_positive_pressure_big_finishable_count_movement_finishable_floor
        ):
            effective_big_finishable_count_scale = (
                positive_big_finishable_count**no_positive_pressure_big_finishable_count_power
            )
        effective_big_finishable_sum_scale = 1.0
        if (
            use_no_positive_pressure_big_finishable_sum_normalization
            and finishable_demand > no_positive_pressure_big_finishable_sum_movement_finishable_floor
            and no_positive_pressure_big_finishable_sum_floor > 0.0
        ):
            effective_big_finishable_sum_scale = max(
                positive_big_finishable_sum / no_positive_pressure_big_finishable_sum_floor,
                1.0,
            ) ** no_positive_pressure_big_finishable_sum_power
        finishable_term = (
            effective_finishable_demand
            * effective_time_weight
            * effective_residual_ratio
            / max(effective_total_demand, 1e-9)
            / max(effective_finishable_count_scale, 1e-9)
            / max(effective_big_finishable_count_scale, 1e-9)
            / max(effective_big_finishable_sum_scale, 1e-9)
        )
        downstream_penalty_term = downstream_penalty * float(row["downstream_route_pressure"])
        local_pressure_penalty_term = local_pressure_penalty * max(local_pressure_floor - float(row["local_pressure"]), 0.0)
        score += finishable_term - downstream_penalty_term - local_pressure_penalty_term
        finishable_term_total += finishable_term
        downstream_penalty_total += downstream_penalty_term
        local_pressure_penalty_total += local_pressure_penalty_term
        movement_details.append(
            {
                "movement": row["movement"],
                "finishable_demand": float(finishable_demand),
                "effective_finishable_power": float(effective_finishable_power),
                "effective_finishable_demand": float(effective_finishable_demand),
                "effective_total_demand": float(effective_total_demand),
                "effective_finishable_count_scale": float(effective_finishable_count_scale),
                "effective_big_finishable_count_scale": float(effective_big_finishable_count_scale),
                "effective_big_finishable_sum_scale": float(effective_big_finishable_sum_scale),
                "total_demand": float(total_demand),
                "avg_remaining_time": float(row["avg_remaining_time"]),
                "residual_ratio": float(row["residual_ratio"]),
                "effective_residual_ratio": float(effective_residual_ratio),
                "effective_slack_floor": float(row["effective_slack_floor"]),
                "downstream_route_pressure": float(row["downstream_route_pressure"]),
                "local_pressure": float(row["local_pressure"]),
                "time_weight": float(row["time_weight"]),
                "effective_time_weight_power": float(effective_time_weight_power),
                "effective_time_weight": float(effective_time_weight),
                "finishable_term": float(finishable_term),
                "downstream_penalty_term": float(downstream_penalty_term),
                "local_pressure_penalty_term": float(local_pressure_penalty_term),
            }
        )
    return {
        "score": float(score),
        "components": {
            "finishable_term": float(finishable_term_total),
            "downstream_penalty": float(downstream_penalty_total),
            "local_pressure_penalty": float(local_pressure_penalty_total),
        },
        "movement_details": movement_details,
    }


def phase_route_horizon_completion_score(
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    route_completion_state: dict[str, Any],
    params: dict[str, float] | None = None,
    *,
    queues: dict[str, float] | None = None,
) -> float:
    return float(
        phase_route_horizon_completion_decomposition(
            phase_index,
            states,
            movements,
            capacities,
            finite_storage_state,
            route_completion_state,
            params,
            queues=queues,
        )["score"]
    )


def normalize_phase_scores(scores: dict[int, float]) -> dict[int, float]:
    if not scores:
        return {}
    values = list(scores.values())
    lo = min(values)
    hi = max(values)
    if abs(hi - lo) < 1e-9:
        return {phase: 0.0 for phase in scores}
    return {phase: float((score - lo) / (hi - lo)) for phase, score in scores.items()}


def completion_risk_active(
    dynamic_params: dict[str, float],
    finite_storage_state: dict[str, Any],
    queues: dict[str, float],
    *,
    step: int | None,
    warmup: int | None,
    steps: int | None,
) -> bool:
    if not dynamic_params.get("completion_risk_filter"):
        return False
    elapsed_fraction = 0.0
    if step is not None and warmup is not None and steps is not None and steps > warmup:
        elapsed_fraction = max(float(step - warmup), 0.0) / max(float(steps - warmup), 1.0)
    storage = state_storage_summary(finite_storage_state)
    return (
        elapsed_fraction >= float(dynamic_params.get("completion_risk_start_fraction", 1.0))
        or sum(max(float(value), 0.0) for value in queues.values())
        >= float(dynamic_params.get("completion_risk_queue_threshold", float("inf")))
        or storage["max_occupancy_ratio"] >= float(dynamic_params.get("completion_risk_occupancy_threshold", 1.0))
    )


def elapsed_fraction_at(step: int | None, warmup: int | None, steps: int | None) -> float | None:
    if step is None or warmup is None or steps is None or steps <= warmup:
        return None
    return max(float(step - warmup), 0.0) / max(float(steps - warmup), 1.0)


def fraction_gate_active(
    dynamic_params: dict[str, float],
    gate_key: str,
    *,
    step: int | None,
    warmup: int | None,
    steps: int | None,
) -> bool:
    if gate_key not in dynamic_params:
        return True
    elapsed_fraction = elapsed_fraction_at(step, warmup, steps)
    if elapsed_fraction is None:
        return False
    return elapsed_fraction >= float(dynamic_params[gate_key])


def completion_safety_veto_active(
    dynamic_params: dict[str, float],
    finite_storage_state: dict[str, Any],
    queues: dict[str, float],
    *,
    step: int | None,
    warmup: int | None,
    steps: int | None,
) -> bool:
    if not dynamic_params.get("completion_safety_veto"):
        return False
    if not completion_risk_active(dynamic_params, finite_storage_state, queues, step=step, warmup=warmup, steps=steps):
        return False
    if not fraction_gate_active(
        dynamic_params,
        "completion_safety_start_fraction",
        step=step,
        warmup=warmup,
        steps=steps,
    ):
        return False
    storage = state_storage_summary(finite_storage_state)
    occupancy_threshold = dynamic_params.get("completion_safety_occupancy_threshold")
    residual_threshold = dynamic_params.get("completion_safety_residual_threshold")
    if occupancy_threshold is not None and storage["max_occupancy_ratio"] >= float(occupancy_threshold):
        return True
    if residual_threshold is not None and storage["min_residual_ratio"] <= float(residual_threshold):
        return True
    return occupancy_threshold is None and residual_threshold is None


def completion_safe_feasible_set(
    phase_scores: dict[int, float],
    baseline_scores: dict[str, dict[int, float]],
    finite_storage_state: dict[str, Any],
    queues: dict[str, float],
    movements_by_phase: dict[int, list[tuple[str, str]]],
    *,
    step: int | None = None,
    warmup: int | None = None,
    steps: int | None = None,
    params: dict[str, float] | None = None,
) -> set[int]:
    params = params or DYNAMIC_V1_6_PARAMS
    margin = float(params["completion_safe_margin"])
    total = (warmup or 0) + (steps or 300)
    remaining = max(total - (step or 0), 0)
    horizon_frac = float(params["completion_horizon_fraction"])
    in_completion_zone = remaining / max(total, 1) <= (1.0 - horizon_frac)
    if not in_completion_zone:
        return set(phase_scores.keys())
    best_baseline_min = float("inf")
    for _bname, bscores in baseline_scores.items():
        bmax = max(bscores.values()) if bscores else 0.0
        best_baseline_min = min(best_baseline_min, bmax)
    safe_phases: set[int] = set()
    for pi, score in phase_scores.items():
        if score >= best_baseline_min - margin * abs(best_baseline_min) - 1e-9:
            safe_phases.add(pi)
    if not safe_phases:
        safe_phases = set(phase_scores.keys())
    return safe_phases


def select_finite_storage_action_with_audit(
    tls_id: str,
    current_phase: int,
    phase_states: dict[str, list[str]],
    tls_movements: dict[str, list[tuple[str, str]]],
    queues: dict[str, float],
    capacities: dict[str, float],
    finite_storage_state: dict[str, Any],
    seed: int = 0,
    controller: str = "finite_storage_primal_dual",
    dynamic_dual_state: dict[str, dict[str, float]] | None = None,
    route_completion_state: dict[str, Any] | None = None,
    step: int | None = None,
    warmup: int | None = None,
    steps: int | None = None,
) -> dict[str, Any]:
    states = phase_states.get(tls_id, [])
    greens = green_phases(states)
    movements = tls_movements.get(tls_id, [])
    score_weights = None
    if controller == "finite_storage_primal_dual_v1_4_score":
        score_weights = {
            "pressure": 1.0,
            "downstream_storage": 1.4,
            "spillback": 1.6,
            "switching": 1.25,
            "service": 1.35,
            "incident": 1.0,
            "total": 1.0,
        }
    finite_phase_scores = {}
    for phase_idx in greens:
        if controller in DYNAMIC_V1_5_CONTROLLER_IDS or controller in V1_6_CONTROLLER_IDS:
            decomposition = dynamic_v1_5_phase_decomposition(
                phase_idx,
                states,
                movements,
                queues,
                capacities,
                finite_storage_state,
                dynamic_dual_state or {},
                current_phase=current_phase,
                params=dynamic_v1_5_params_for_controller(controller) if controller in DYNAMIC_V1_5_CONTROLLER_IDS else DYNAMIC_V1_6_PARAMS,
                score_variant=controller,
            )
        else:
            decomposition = finite_storage_phase_decomposition(
                phase_idx,
                states,
                movements,
                queues,
                capacities,
                finite_storage_state,
                current_phase=current_phase,
            )
        if score_weights is not None:
            decomposition = _score_weighted_decomposition(decomposition, score_weights)
        finite_phase_scores[int(phase_idx)] = decomposition
    pressure_phase_scores = {
        int(phase_idx): float(phase_score("max_pressure", phase_idx, states, movements, queues, capacities, seed))
        for phase_idx in greens
    }
    pressure_action = max((score, -phase_idx, phase_idx) for phase_idx, score in pressure_phase_scores.items())[2] if pressure_phase_scores else current_phase
    finite_storage_action = max(
        (audit["score"], -phase_idx, phase_idx) for phase_idx, audit in finite_phase_scores.items()
    )[2] if finite_phase_scores else current_phase
    capacity_phase_scores = {
        int(phase_idx): float(
            phase_score(
                "capacity_aware_pressure",
                phase_idx,
                states,
                movements,
                queues,
                capacities,
                seed,
            )
        )
        for phase_idx in greens
    }
    capacity_action = (
        max((score, -phase_idx, phase_idx) for phase_idx, score in capacity_phase_scores.items())[2]
        if capacity_phase_scores
        else current_phase
    )
    double_pressure_phase_scores = {
        int(phase_idx): float(
            phase_score(
                "finite_storage_double_pressure",
                phase_idx,
                states,
                movements,
                queues,
                capacities,
                seed,
            )
        )
        for phase_idx in greens
    }
    double_pressure_action = (
        max((score, -phase_idx, phase_idx) for phase_idx, score in double_pressure_phase_scores.items())[2]
        if double_pressure_phase_scores
        else current_phase
    )
    dynamic_params = dynamic_v1_5_params_for_controller(controller) if controller in DYNAMIC_V1_5_CONTROLLER_IDS else (DYNAMIC_V1_6_PARAMS if controller in V1_6_CONTROLLER_IDS else {})
    safety_fallback_used = False
    terminal_fallback_used = False
    double_score_filter_used = False
    multi_baseline_filter_used = False
    hold_only_filter_used = False
    max_hold_filter_used = False
    completion_risk_filter_used = False
    route_completion_prediction_filter_used = False
    route_demand_completion_filter_used = False
    route_demand_double_score_veto_used = False
    route_horizon_completion_filter_used = False
    route_horizon_dominance_filter_used = False
    terminal_exit_protection_guard_used = False
    route_horizon_max_pressure_envelope_used = False
    route_horizon_core_baseline_envelope_used = False
    route_horizon_double_pressure_envelope_used = False
    route_horizon_core_minimax_guard_used = False
    route_horizon_capacity_rescue_guard_used = False
    route_horizon_capacity_score_envelope_used = False
    route_horizon_native_capacity_score_rescue_guard_used = False
    route_horizon_severe_double_guard_used = False
    route_horizon_pressure_double_conflict_guard_used = False
    route_horizon_completion_conflict_guard_used = False
    route_horizon_capacity_completion_conflict_guard_used = False
    route_horizon_early_capacity_completion_conflict_guard_used = False
    route_horizon_negative_total_completion_conflict_guard_used = False
    route_horizon_low_total_consensus_completion_guard_used = False
    route_horizon_score_gap_consensus_guard_used = False
    route_horizon_negative_total_raw_consensus_guard_used = False
    route_horizon_core_consensus_guard_used = False
    route_horizon_raw_consensus_guard_used = False
    post_completion_veto_double_conflict_guard_used = False
    route_horizon_pressure_safe_guard_used = False
    route_horizon_tail_completion_rescue_used = False
    completion_safety_veto_used = False
    if (
        "terminal_flush_start_fraction" in dynamic_params
        and step is not None
        and warmup is not None
        and steps is not None
        and steps > warmup
    ):
        elapsed_fraction = max(float(step - warmup), 0.0) / max(float(steps - warmup), 1.0)
        if elapsed_fraction >= float(dynamic_params["terminal_flush_start_fraction"]):
            terminal_action = str(dynamic_params.get("terminal_flush_action", "finite_storage_double"))
            if terminal_action == "balanced_capacity_double":
                normalized_capacity = normalize_phase_scores(capacity_phase_scores)
                normalized_double = normalize_phase_scores(double_pressure_phase_scores)
                candidates = sorted({int(capacity_action), int(double_pressure_action)})
                finite_storage_action = max(
                    candidates,
                    key=lambda phase_idx: (
                        min(normalized_capacity.get(phase_idx, 0.0), normalized_double.get(phase_idx, 0.0)),
                        normalized_capacity.get(phase_idx, 0.0) + normalized_double.get(phase_idx, 0.0),
                        pressure_phase_scores.get(phase_idx, float("-inf")),
                        -phase_idx,
                    ),
                )
            elif terminal_action == "balanced_max_double":
                normalized_pressure = normalize_phase_scores(pressure_phase_scores)
                normalized_double = normalize_phase_scores(double_pressure_phase_scores)
                candidates = sorted({int(pressure_action), int(double_pressure_action)})
                finite_storage_action = max(
                    candidates,
                    key=lambda phase_idx: (
                        min(normalized_pressure.get(phase_idx, 0.0), normalized_double.get(phase_idx, 0.0)),
                        normalized_pressure.get(phase_idx, 0.0) + normalized_double.get(phase_idx, 0.0),
                        pressure_phase_scores.get(phase_idx, float("-inf")),
                        -phase_idx,
                    ),
                )
            elif terminal_action == "completion_service_max_double":
                candidates = sorted({int(pressure_action), int(double_pressure_action)})
                terminal_service_scores = {
                    phase_idx: phase_completion_service_score(phase_idx, states, movements, queues)
                    for phase_idx in candidates
                }
                finite_storage_action = max(
                    candidates,
                    key=lambda phase_idx: (
                        terminal_service_scores.get(phase_idx, 0.0),
                        double_pressure_phase_scores.get(phase_idx, float("-inf")),
                        pressure_phase_scores.get(phase_idx, float("-inf")),
                        -phase_idx,
                    ),
                )
            elif terminal_action == "core_completion":
                candidates = sorted({int(pressure_action), int(capacity_action), int(double_pressure_action)})
                terminal_service_scores = {
                    phase_idx: phase_completion_service_score(phase_idx, states, movements, queues)
                    for phase_idx in candidates
                }
                route_completion_state_for_terminal = route_completion_state or unavailable_route_completion_state()
                terminal_horizon_scores = {
                    phase_idx: phase_route_horizon_completion_score(
                        phase_idx,
                        states,
                        movements,
                        capacities,
                        finite_storage_state,
                        route_completion_state_for_terminal,
                        dynamic_params,
                        queues=queues,
                    )
                    for phase_idx in candidates
                }
                normalized_horizon = normalize_phase_scores(terminal_horizon_scores)
                normalized_service = normalize_phase_scores(terminal_service_scores)
                normalized_pressure = normalize_phase_scores(pressure_phase_scores)
                normalized_capacity = normalize_phase_scores(capacity_phase_scores)
                normalized_double = normalize_phase_scores(double_pressure_phase_scores)
                horizon_blend = float(dynamic_params.get("terminal_core_completion_horizon_blend", 1.0))
                service_blend = float(dynamic_params.get("terminal_core_completion_service_blend", 0.0))
                core_blend = float(dynamic_params.get("terminal_core_completion_core_blend", 0.0))
                finite_storage_action = max(
                    candidates,
                    key=lambda phase_idx: (
                        horizon_blend * normalized_horizon.get(phase_idx, 0.0)
                        + service_blend * normalized_service.get(phase_idx, 0.0),
                        core_blend
                        * min(
                            normalized_pressure.get(phase_idx, 0.0),
                            normalized_capacity.get(phase_idx, 0.0),
                            normalized_double.get(phase_idx, 0.0),
                        ),
                        normalized_pressure.get(phase_idx, 0.0)
                        + normalized_capacity.get(phase_idx, 0.0)
                        + normalized_double.get(phase_idx, 0.0),
                        terminal_horizon_scores.get(phase_idx, float("-inf")),
                        terminal_service_scores.get(phase_idx, float("-inf")),
                        -phase_idx,
                    ),
                )
            elif terminal_action == "capacity_aware":
                finite_storage_action = int(capacity_action)
            elif terminal_action == "max_pressure":
                finite_storage_action = int(pressure_action)
            else:
                finite_storage_action = int(double_pressure_action)
            terminal_fallback_used = True
    if dynamic_params.get("double_score_safety_filter") and finite_storage_action != double_pressure_action:
        selected_double_score = double_pressure_phase_scores.get(int(finite_storage_action), float("-inf"))
        best_double_score = double_pressure_phase_scores.get(int(double_pressure_action), float("-inf"))
        tolerance = float(dynamic_params.get("double_score_safety_tolerance", 0.0))
        if selected_double_score + tolerance < best_double_score:
            finite_storage_action = int(double_pressure_action)
            double_score_filter_used = True
    if dynamic_params.get("multi_baseline_safety_filter"):
        tolerance = float(dynamic_params.get("baseline_score_safety_tolerance", 0.0))
        best_capacity_score = capacity_phase_scores.get(int(capacity_action), float("-inf"))
        best_double_score = double_pressure_phase_scores.get(int(double_pressure_action), float("-inf"))
        selected_capacity_score = capacity_phase_scores.get(int(finite_storage_action), float("-inf"))
        selected_double_score = double_pressure_phase_scores.get(int(finite_storage_action), float("-inf"))
        if (
            selected_capacity_score + tolerance < best_capacity_score
            or selected_double_score + tolerance < best_double_score
        ):
            candidates = sorted({int(capacity_action), int(double_pressure_action)})
            finite_storage_action = max(
                candidates,
                key=lambda phase_idx: (
                    min(
                        capacity_phase_scores.get(phase_idx, float("-inf")) - best_capacity_score,
                        double_pressure_phase_scores.get(phase_idx, float("-inf")) - best_double_score,
                    ),
                    capacity_phase_scores.get(phase_idx, float("-inf"))
                    + double_pressure_phase_scores.get(phase_idx, float("-inf")),
                    -phase_idx,
                ),
            )
            multi_baseline_filter_used = True
    if (
        dynamic_params.get("hold_only_safety_filter")
        and finite_storage_action != pressure_action
        and finite_storage_action != current_phase
    ):
        finite_storage_action = int(pressure_action)
        hold_only_filter_used = True
    if (
        "max_dynamic_hold_time" in dynamic_params
        and finite_storage_action != pressure_action
        and finite_storage_action == current_phase
        and float(finite_storage_state.get("switching_loss_state", {}).get("time_since_switch", 0.0))
        > float(dynamic_params["max_dynamic_hold_time"])
    ):
        finite_storage_action = int(pressure_action)
        max_hold_filter_used = True
    if dynamic_params.get("double_safety_fallback") and finite_storage_action != double_pressure_action:
        selected_pressure = pressure_phase_scores.get(int(finite_storage_action), 0.0)
        double_pressure = pressure_phase_scores.get(int(double_pressure_action), 0.0)
        margin = float(dynamic_params.get("double_safety_fallback", 0.0))
        if selected_pressure + margin < double_pressure:
            finite_storage_action = int(double_pressure_action)
            safety_fallback_used = True
    completion_service_scores = {
        int(phase_idx): phase_completion_service_score(phase_idx, states, movements, queues)
        for phase_idx in greens
    }
    route_completion_prediction_scores = {
        int(phase_idx): phase_route_completion_prediction_score(
            phase_idx,
            states,
            movements,
            queues,
            capacities,
            finite_storage_state,
            dynamic_params,
        )
        for phase_idx in greens
    }
    route_completion_state = route_completion_state or unavailable_route_completion_state()
    route_horizon_completion_decompositions = {
        int(phase_idx): phase_route_horizon_completion_decomposition(
            phase_idx,
            states,
            movements,
            capacities,
            finite_storage_state,
            route_completion_state,
            dynamic_params,
            queues=queues,
        )
        for phase_idx in greens
    }
    route_horizon_completion_scores = {
        int(phase_idx): float(decomp.get("score", 0.0))
        for phase_idx, decomp in route_horizon_completion_decompositions.items()
    }
    route_horizon_blend_details: dict[int, dict[str, float]] = {}
    route_horizon_capped_phases: list[int] = []
    if (
        not (terminal_fallback_used and dynamic_params.get("terminal_flush_locks_dynamic"))
        and
        dynamic_params.get("route_horizon_completion_filter")
        and completion_risk_active(dynamic_params, finite_storage_state, queues, step=step, warmup=warmup, steps=steps)
        and route_horizon_completion_scores
    ):
        normalized_horizon = normalize_phase_scores(route_horizon_completion_scores)
        normalized_double = normalize_phase_scores(double_pressure_phase_scores)
        normalized_pressure = normalize_phase_scores(pressure_phase_scores)
        normalized_service_for_horizon = normalize_phase_scores(completion_service_scores)
        normalized_native = normalize_phase_scores(
            {
                phase_idx: float(audit.get("score", float("-inf")))
                for phase_idx, audit in finite_phase_scores.items()
            }
        )
        normalized_release_component = normalize_phase_scores(
            {
                phase_idx: max(
                    float(finite_phase_scores.get(phase_idx, {}).get("component_totals", {}).get("release", 0.0)),
                    0.0,
                )
                for phase_idx in finite_phase_scores
            }
        )
        normalized_storage_risk_component = normalize_phase_scores(
            {
                phase_idx: -(
                    max(
                        -float(finite_phase_scores.get(phase_idx, {}).get("component_totals", {}).get("downstream_storage", 0.0)),
                        0.0,
                    )
                    + max(
                        -float(finite_phase_scores.get(phase_idx, {}).get("component_totals", {}).get("spillback", 0.0)),
                        0.0,
                    )
                    + max(
                        -float(finite_phase_scores.get(phase_idx, {}).get("component_totals", {}).get("storage_price", 0.0)),
                        0.0,
                    )
                    + max(
                        -float(finite_phase_scores.get(phase_idx, {}).get("component_totals", {}).get("cascade_price", 0.0)),
                        0.0,
                    )
                )
                for phase_idx in finite_phase_scores
            }
        )
        normalized_negative_pressure_component = normalize_phase_scores(
            {
                phase_idx: -max(
                    -float(finite_phase_scores.get(phase_idx, {}).get("component_totals", {}).get("pressure", 0.0)),
                    0.0,
                )
                for phase_idx in finite_phase_scores
            }
        )
        normalized_negative_total_component = normalize_phase_scores(
            {
                phase_idx: -max(
                    -float(finite_phase_scores.get(phase_idx, {}).get("component_totals", {}).get("total", 0.0)),
                    0.0,
                )
                for phase_idx in finite_phase_scores
            }
        )
        double_blend = float(dynamic_params.get("route_horizon_double_blend", 0.0))
        pressure_blend = float(dynamic_params.get("route_horizon_pressure_blend", 0.0))
        service_blend = float(dynamic_params.get("route_horizon_service_blend", 0.0))
        native_blend = float(dynamic_params.get("route_horizon_native_score_blend", 0.0))
        release_component_blend = float(dynamic_params.get("route_horizon_release_component_blend", 0.0))
        storage_risk_component_blend = float(dynamic_params.get("route_horizon_storage_risk_component_blend", 0.0))
        negative_pressure_component_blend = float(
            dynamic_params.get("route_horizon_negative_pressure_component_blend", 0.0)
        )
        negative_total_component_blend = float(
            dynamic_params.get("route_horizon_negative_total_component_blend", 0.0)
        )
        conditional_penalty_active = False
        if (
            dynamic_params.get("route_horizon_conditional_risk_penalty")
            or dynamic_params.get("route_horizon_low_total_pressure_penalty")
        ):
            storage = state_storage_summary(finite_storage_state)
            elapsed_fraction = elapsed_fraction_at(step, warmup, steps)
            start_fraction = float(dynamic_params.get("route_horizon_conditional_risk_start_fraction", 0.0))
            end_fraction = float(dynamic_params.get("route_horizon_conditional_risk_end_fraction", 1.0))
            occupancy_threshold = float(dynamic_params.get("route_horizon_conditional_risk_occupancy_threshold", 1.0))
            residual_threshold = float(dynamic_params.get("route_horizon_conditional_risk_residual_threshold", 0.0))
            conditional_penalty_active = (
                elapsed_fraction is not None
                and start_fraction <= elapsed_fraction <= end_fraction
                and (
                    storage["max_occupancy_ratio"] >= occupancy_threshold
                    or storage["min_residual_ratio"] <= residual_threshold
                )
            )
            if dynamic_params.get("route_horizon_conditional_risk_penalty") and not conditional_penalty_active:
                negative_pressure_component_blend = 0.0
                negative_total_component_blend = 0.0
        low_total_pressure_penalty = float(dynamic_params.get("route_horizon_low_total_pressure_penalty", 0.0))
        low_total_pressure_total_ceiling = float(
            dynamic_params.get("route_horizon_low_total_pressure_total_ceiling", 0.0)
        )
        low_total_pressure_pressure_ceiling = float(
            dynamic_params.get("route_horizon_low_total_pressure_pressure_ceiling", 0.0)
        )
        if low_total_pressure_penalty and not conditional_penalty_active:
            low_total_pressure_penalty = 0.0
        conditional_release_gate = bool(dynamic_params.get("route_horizon_conditional_release_gate"))
        conditional_release_gate_total_floor = float(
            dynamic_params.get("route_horizon_conditional_release_gate_total_floor", 0.0)
        )
        conditional_release_gate_pressure_floor = float(
            dynamic_params.get("route_horizon_conditional_release_gate_pressure_floor", 0.0)
        )
        if conditional_release_gate and not conditional_penalty_active:
            conditional_release_gate = False
        low_signal_bonus_gate = bool(dynamic_params.get("route_horizon_low_signal_bonus_gate"))
        low_signal_bonus_total_ceiling = float(dynamic_params.get("route_horizon_low_signal_bonus_total_ceiling", 0.0))
        low_signal_bonus_pressure_ceiling = float(
            dynamic_params.get("route_horizon_low_signal_bonus_pressure_ceiling", 0.0)
        )
        low_signal_bonus_scale = float(dynamic_params.get("route_horizon_low_signal_bonus_scale", 0.0))
        if low_signal_bonus_gate and not conditional_penalty_active:
            low_signal_bonus_gate = False
        native_negative_total_penalty = float(dynamic_params.get("route_horizon_native_negative_total_penalty", 0.0))
        blended_scores: dict[int, float] = {}
        route_horizon_blend_details = {}
        for phase_idx in route_horizon_completion_scores:
            phase_totals = finite_phase_scores.get(phase_idx, {}).get("component_totals", {})
            pressure_total = float(phase_totals.get("pressure", 0.0))
            selected_total = float(phase_totals.get("total", 0.0))
            horizon_term = normalized_horizon.get(phase_idx, 0.0)
            double_term = double_blend * normalized_double.get(phase_idx, 0.0)
            pressure_term = pressure_blend * normalized_pressure.get(phase_idx, 0.0)
            service_term = service_blend * normalized_service_for_horizon.get(phase_idx, 0.0)
            native_term = native_blend * normalized_native.get(phase_idx, 0.0)
            release_gate_open = (
                not conditional_release_gate
                or pressure_total > conditional_release_gate_pressure_floor
                or selected_total > conditional_release_gate_total_floor
            )
            low_signal_bonus_blocked = (
                low_signal_bonus_gate
                and pressure_total <= low_signal_bonus_pressure_ceiling
                and selected_total <= low_signal_bonus_total_ceiling
            )
            release_term = release_component_blend * (
                normalized_release_component.get(phase_idx, 0.0) if release_gate_open else 0.0
            )
            if low_signal_bonus_blocked:
                release_term *= low_signal_bonus_scale
            storage_risk_term = storage_risk_component_blend * normalized_storage_risk_component.get(phase_idx, 0.0)
            if low_signal_bonus_blocked:
                storage_risk_term *= low_signal_bonus_scale
            negative_pressure_term = (
                negative_pressure_component_blend * normalized_negative_pressure_component.get(phase_idx, 0.0)
            )
            negative_total_term = (
                negative_total_component_blend * normalized_negative_total_component.get(phase_idx, 0.0)
            )
            if low_signal_bonus_blocked:
                negative_total_term *= low_signal_bonus_scale
            low_total_pressure_penalty_term = low_total_pressure_penalty * (
                max(low_total_pressure_total_ceiling - selected_total, 0.0)
                if pressure_total <= low_total_pressure_pressure_ceiling
                else 0.0
            )
            native_negative_total_penalty_term = native_negative_total_penalty * max(
                -float(finite_phase_scores.get(phase_idx, {}).get("score", 0.0)),
                0.0,
            )
            blended_score = (
                horizon_term
                + double_term
                + pressure_term
                + service_term
                + native_term
                + release_term
                + storage_risk_term
                + negative_pressure_term
                + negative_total_term
                - low_total_pressure_penalty_term
                - native_negative_total_penalty_term
            )
            blended_scores[phase_idx] = blended_score
            route_horizon_blend_details[phase_idx] = {
                "horizon_term": float(horizon_term),
                "double_term": float(double_term),
                "pressure_term": float(pressure_term),
                "service_term": float(service_term),
                "native_term": float(native_term),
                "release_term": float(release_term),
                "storage_risk_term": float(storage_risk_term),
                "negative_pressure_term": float(negative_pressure_term),
                "negative_total_term": float(negative_total_term),
                "low_total_pressure_penalty_term": float(low_total_pressure_penalty_term),
                "native_negative_total_penalty_term": float(native_negative_total_penalty_term),
                "release_gate_open": float(1.0 if release_gate_open else 0.0),
                "low_signal_bonus_blocked": float(1.0 if low_signal_bonus_blocked else 0.0),
                "low_signal_bonus_scale": float(low_signal_bonus_scale if low_signal_bonus_blocked else 1.0),
                "blended_score": float(blended_score),
            }
        low_signal_margin_cap = float(dynamic_params.get("route_horizon_low_signal_margin_cap", -1.0))
        low_signal_margin_epsilon = float(dynamic_params.get("route_horizon_low_signal_margin_epsilon", 1e-6))
        low_signal_margin_core_horizon_floor = float(
            dynamic_params.get("route_horizon_low_signal_margin_core_horizon_floor", -1.0)
        )
        low_signal_margin_core_score_advantage_floor = float(
            dynamic_params.get("route_horizon_low_signal_margin_core_score_advantage_floor", -1.0)
        )
        supported_low_total_margin_cap = float(
            dynamic_params.get("route_horizon_supported_low_total_margin_cap", -1.0)
        )
        supported_low_total_total_ceiling = float(
            dynamic_params.get("route_horizon_supported_low_total_total_ceiling", float("-inf"))
        )
        supported_low_total_pressure_ceiling = float(
            dynamic_params.get("route_horizon_supported_low_total_pressure_ceiling", float("inf"))
        )
        supported_negative_pressure_margin_cap = float(
            dynamic_params.get("route_horizon_supported_negative_pressure_margin_cap", -1.0)
        )
        supported_negative_pressure_total_ceiling = float(
            dynamic_params.get("route_horizon_supported_negative_pressure_total_ceiling", float("-inf"))
        )
        supported_negative_pressure_ceiling = float(
            dynamic_params.get("route_horizon_supported_negative_pressure_ceiling", float("inf"))
        )
        no_risky_movement_margin_cap = float(
            dynamic_params.get("route_horizon_no_risky_movement_margin_cap", -1.0)
        )
        no_risky_movement_score_advantage_floor = float(
            dynamic_params.get("route_horizon_no_risky_movement_score_advantage_floor", -1.0)
        )
        no_risky_movement_max_local_pressure_ceiling = float(
            dynamic_params.get("route_horizon_no_risky_movement_max_local_pressure_ceiling", float("inf"))
        )
        low_support_bonus_damping_scale = float(
            dynamic_params.get("route_horizon_low_support_bonus_damping_scale", 1.0)
        )
        low_support_bonus_damping_margin_cap = float(
            dynamic_params.get("route_horizon_low_support_bonus_damping_margin_cap", -1.0)
        )
        low_support_bonus_damping_score_advantage_floor = float(
            dynamic_params.get("route_horizon_low_support_bonus_damping_score_advantage_floor", -1.0)
        )
        low_support_bonus_damping_max_local_pressure_ceiling = float(
            dynamic_params.get("route_horizon_low_support_bonus_damping_max_local_pressure_ceiling", float("inf"))
        )
        low_support_core_anchor_bonus = float(
            dynamic_params.get("route_horizon_low_support_core_anchor_bonus", 0.0)
        )
        low_support_core_anchor_margin_cap = float(
            dynamic_params.get("route_horizon_low_support_core_anchor_margin_cap", -1.0)
        )
        low_support_core_anchor_score_advantage_floor = float(
            dynamic_params.get("route_horizon_low_support_core_anchor_score_advantage_floor", -1.0)
        )
        low_support_core_anchor_max_local_pressure_ceiling = float(
            dynamic_params.get("route_horizon_low_support_core_anchor_max_local_pressure_ceiling", float("inf"))
        )
        route_horizon_base_time_weight_power = max(float(dynamic_params.get("route_horizon_time_weight_power", 1.0)), 0.0)
        baseline_candidates = sorted({int(pressure_action), int(capacity_action), int(double_pressure_action)})
        best_core_action = None
        best_core_blended_score = float("-inf")
        best_core_horizon_support = 0.0
        best_core_route_horizon_score = float("-inf")
        if baseline_candidates:
            best_core_action = max(
                baseline_candidates,
                key=lambda phase_idx: (
                    blended_scores.get(phase_idx, float("-inf")),
                    route_horizon_completion_scores.get(phase_idx, float("-inf")),
                    double_pressure_phase_scores.get(phase_idx, float("-inf")),
                    capacity_phase_scores.get(phase_idx, float("-inf")),
                    pressure_phase_scores.get(phase_idx, float("-inf")),
                    -phase_idx,
                ),
            )
            best_core_blended_score = blended_scores.get(best_core_action, float("-inf"))
            best_core_horizon_support = route_horizon_blend_details.get(best_core_action, {}).get("horizon_term", 0.0)
            best_core_route_horizon_score = route_horizon_completion_scores.get(best_core_action, float("-inf"))
        if low_support_core_anchor_bonus > 0.0 and baseline_candidates and best_core_action is not None:
            anchor_applied = False
            for phase_idx, detail in route_horizon_blend_details.items():
                if phase_idx in baseline_candidates:
                    continue
                phase_decomp = route_horizon_completion_decompositions.get(phase_idx, {})
                movement_details = phase_decomp.get("movement_details", [])
                if any(
                    float(movement.get("effective_time_weight_power", route_horizon_base_time_weight_power))
                    > route_horizon_base_time_weight_power
                    for movement in movement_details
                    if isinstance(movement, dict)
                ):
                    continue
                phase_max_local_pressure = max(
                    (
                        float(movement.get("local_pressure", float("-inf")))
                        for movement in movement_details
                        if isinstance(movement, dict)
                    ),
                    default=float("-inf"),
                )
                if phase_max_local_pressure > low_support_core_anchor_max_local_pressure_ceiling:
                    continue
                phase_route_horizon_score = route_horizon_completion_scores.get(phase_idx, float("-inf"))
                score_gap = best_core_route_horizon_score - phase_route_horizon_score
                if (
                    low_support_core_anchor_score_advantage_floor >= 0.0
                    and score_gap < low_support_core_anchor_score_advantage_floor
                ):
                    continue
                blended_score = blended_scores.get(phase_idx, float("-inf"))
                if (
                    blended_score > best_core_blended_score
                    and blended_score <= best_core_blended_score + low_support_core_anchor_margin_cap
                ):
                    anchor_applied = True
                    break
            if anchor_applied:
                core_detail = route_horizon_blend_details.get(best_core_action, {})
                core_detail["low_support_core_anchor_bonus"] = float(low_support_core_anchor_bonus)
                core_detail["pre_low_support_core_anchor_blended_score"] = float(best_core_blended_score)
                core_detail["blended_score"] = float(best_core_blended_score + low_support_core_anchor_bonus)
                blended_scores[best_core_action] = float(best_core_blended_score + low_support_core_anchor_bonus)
                best_core_blended_score = float(best_core_blended_score + low_support_core_anchor_bonus)
        if low_support_bonus_damping_scale < 1.0 and baseline_candidates and best_core_action is not None:
            for phase_idx, detail in route_horizon_blend_details.items():
                if phase_idx in baseline_candidates:
                    continue
                phase_decomp = route_horizon_completion_decompositions.get(phase_idx, {})
                movement_details = phase_decomp.get("movement_details", [])
                if any(
                    float(movement.get("effective_time_weight_power", route_horizon_base_time_weight_power))
                    > route_horizon_base_time_weight_power
                    for movement in movement_details
                    if isinstance(movement, dict)
                ):
                    continue
                phase_max_local_pressure = max(
                    (
                        float(movement.get("local_pressure", float("-inf")))
                        for movement in movement_details
                        if isinstance(movement, dict)
                    ),
                    default=float("-inf"),
                )
                if phase_max_local_pressure > low_support_bonus_damping_max_local_pressure_ceiling:
                    continue
                phase_route_horizon_score = route_horizon_completion_scores.get(phase_idx, float("-inf"))
                score_gap = best_core_route_horizon_score - phase_route_horizon_score
                if (
                    low_support_bonus_damping_score_advantage_floor >= 0.0
                    and score_gap < low_support_bonus_damping_score_advantage_floor
                ):
                    continue
                blended_score = blended_scores.get(phase_idx, float("-inf"))
                if not (
                    blended_score > best_core_blended_score
                    and blended_score <= best_core_blended_score + low_support_bonus_damping_margin_cap
                ):
                    continue
                pre_release_term = float(detail.get("release_term", 0.0))
                pre_storage_risk_term = float(detail.get("storage_risk_term", 0.0))
                if pre_release_term <= 0.0 and pre_storage_risk_term <= 0.0:
                    continue
                detail["pre_low_support_release_term"] = pre_release_term
                detail["pre_low_support_storage_risk_term"] = pre_storage_risk_term
                detail["release_term"] = pre_release_term * low_support_bonus_damping_scale
                detail["storage_risk_term"] = pre_storage_risk_term * low_support_bonus_damping_scale
                detail["low_support_bonus_damped"] = 1.0
                detail["low_support_bonus_damping_scale"] = float(low_support_bonus_damping_scale)
                detail["best_core_route_horizon_score"] = float(best_core_route_horizon_score)
                detail["route_horizon_score_gap_to_best_core"] = float(score_gap)
                detail["low_support_phase_max_local_pressure"] = float(phase_max_local_pressure)
                adjusted_blended_score = (
                    blended_score
                    - pre_release_term
                    - pre_storage_risk_term
                    + detail["release_term"]
                    + detail["storage_risk_term"]
                )
                blended_scores[phase_idx] = float(adjusted_blended_score)
                detail["blended_score"] = float(adjusted_blended_score)
        if low_signal_margin_cap >= 0.0 and baseline_candidates:
            for phase_idx, detail in route_horizon_blend_details.items():
                if phase_idx in baseline_candidates:
                    continue
                if not detail.get("low_signal_bonus_blocked"):
                    continue
                if (
                    low_signal_margin_core_horizon_floor >= 0.0
                    and best_core_horizon_support < low_signal_margin_core_horizon_floor
                ):
                    continue
                phase_route_horizon_score = route_horizon_completion_scores.get(phase_idx, float("-inf"))
                if (
                    low_signal_margin_core_score_advantage_floor >= 0.0
                    and best_core_route_horizon_score - phase_route_horizon_score
                    < low_signal_margin_core_score_advantage_floor
                ):
                    continue
                blended_score = blended_scores.get(phase_idx, float("-inf"))
                if (
                    blended_score > best_core_blended_score
                    and blended_score <= best_core_blended_score + low_signal_margin_cap
                ):
                    capped_score = best_core_blended_score - low_signal_margin_epsilon
                    blended_scores[phase_idx] = capped_score
                    detail["pre_cap_blended_score"] = float(blended_score)
                    detail["thin_margin_low_signal_capped"] = 1.0
                    detail["best_core_blended_score"] = float(best_core_blended_score)
                    detail["best_core_route_horizon_score"] = float(best_core_route_horizon_score)
                    detail["route_horizon_score_gap_to_best_core"] = float(
                        best_core_route_horizon_score - phase_route_horizon_score
                    )
                    detail["blended_score"] = float(capped_score)
                    route_horizon_capped_phases.append(int(phase_idx))
        if supported_low_total_margin_cap >= 0.0 and baseline_candidates and best_core_action is not None:
            for phase_idx, detail in route_horizon_blend_details.items():
                if phase_idx in baseline_candidates:
                    continue
                if detail.get("supported_low_total_margin_capped"):
                    continue
                if not detail.get("low_signal_bonus_blocked"):
                    continue
                if (
                    low_signal_margin_core_horizon_floor >= 0.0
                    and best_core_horizon_support < low_signal_margin_core_horizon_floor
                ):
                    continue
                phase_totals = finite_phase_scores.get(phase_idx, {}).get("component_totals", {})
                phase_total = float(phase_totals.get("total", 0.0))
                phase_pressure_total = float(phase_totals.get("pressure", 0.0))
                if phase_total > supported_low_total_total_ceiling:
                    continue
                if phase_pressure_total > supported_low_total_pressure_ceiling:
                    continue
                blended_score = blended_scores.get(phase_idx, float("-inf"))
                if (
                    blended_score > best_core_blended_score
                    and blended_score <= best_core_blended_score + supported_low_total_margin_cap
                ):
                    capped_score = best_core_blended_score - low_signal_margin_epsilon
                    blended_scores[phase_idx] = capped_score
                    detail["pre_supported_low_total_cap_blended_score"] = float(blended_score)
                    detail["supported_low_total_margin_capped"] = 1.0
                    detail["best_core_blended_score"] = float(best_core_blended_score)
                    detail["best_core_route_horizon_score"] = float(best_core_route_horizon_score)
                    detail["supported_low_total_total_ceiling"] = float(supported_low_total_total_ceiling)
                    detail["supported_low_total_pressure_ceiling"] = float(supported_low_total_pressure_ceiling)
                    detail["blended_score"] = float(capped_score)
                    route_horizon_capped_phases.append(int(phase_idx))
        if supported_negative_pressure_margin_cap >= 0.0 and baseline_candidates and best_core_action is not None:
            for phase_idx, detail in route_horizon_blend_details.items():
                if phase_idx in baseline_candidates:
                    continue
                if detail.get("supported_negative_pressure_margin_capped"):
                    continue
                if not detail.get("low_signal_bonus_blocked"):
                    continue
                if (
                    low_signal_margin_core_horizon_floor >= 0.0
                    and best_core_horizon_support < low_signal_margin_core_horizon_floor
                ):
                    continue
                phase_totals = finite_phase_scores.get(phase_idx, {}).get("component_totals", {})
                phase_total = float(phase_totals.get("total", 0.0))
                phase_pressure_total = float(phase_totals.get("pressure", 0.0))
                if phase_total > supported_negative_pressure_total_ceiling:
                    continue
                if phase_pressure_total > supported_negative_pressure_ceiling:
                    continue
                blended_score = blended_scores.get(phase_idx, float("-inf"))
                if (
                    blended_score > best_core_blended_score
                    and blended_score <= best_core_blended_score + supported_negative_pressure_margin_cap
                ):
                    capped_score = best_core_blended_score - low_signal_margin_epsilon
                    blended_scores[phase_idx] = capped_score
                    detail["pre_supported_negative_pressure_cap_blended_score"] = float(blended_score)
                    detail["supported_negative_pressure_margin_capped"] = 1.0
                    detail["best_core_blended_score"] = float(best_core_blended_score)
                    detail["best_core_route_horizon_score"] = float(best_core_route_horizon_score)
                    detail["supported_negative_pressure_total_ceiling"] = float(supported_negative_pressure_total_ceiling)
                    detail["supported_negative_pressure_ceiling"] = float(supported_negative_pressure_ceiling)
                    detail["blended_score"] = float(capped_score)
                    route_horizon_capped_phases.append(int(phase_idx))
        if no_risky_movement_margin_cap >= 0.0 and baseline_candidates and best_core_action is not None:
            for phase_idx, detail in route_horizon_blend_details.items():
                if phase_idx in baseline_candidates:
                    continue
                if detail.get("no_risky_movement_margin_capped"):
                    continue
                phase_decomp = route_horizon_completion_decompositions.get(phase_idx, {})
                movement_details = phase_decomp.get("movement_details", [])
                if any(
                    float(movement.get("effective_time_weight_power", route_horizon_base_time_weight_power))
                    > route_horizon_base_time_weight_power
                    for movement in movement_details
                    if isinstance(movement, dict)
                ):
                    continue
                phase_max_local_pressure = max(
                    (
                        float(movement.get("local_pressure", float("-inf")))
                        for movement in movement_details
                        if isinstance(movement, dict)
                    ),
                    default=float("-inf"),
                )
                if phase_max_local_pressure > no_risky_movement_max_local_pressure_ceiling:
                    continue
                phase_route_horizon_score = route_horizon_completion_scores.get(phase_idx, float("-inf"))
                score_gap = best_core_route_horizon_score - phase_route_horizon_score
                if (
                    no_risky_movement_score_advantage_floor >= 0.0
                    and score_gap < no_risky_movement_score_advantage_floor
                ):
                    continue
                blended_score = blended_scores.get(phase_idx, float("-inf"))
                if (
                    blended_score > best_core_blended_score
                    and blended_score <= best_core_blended_score + no_risky_movement_margin_cap
                ):
                    capped_score = best_core_blended_score - low_signal_margin_epsilon
                    blended_scores[phase_idx] = capped_score
                    detail["pre_no_risky_movement_cap_blended_score"] = float(blended_score)
                    detail["no_risky_movement_margin_capped"] = 1.0
                    detail["best_core_blended_score"] = float(best_core_blended_score)
                    detail["best_core_route_horizon_score"] = float(best_core_route_horizon_score)
                    detail["route_horizon_score_gap_to_best_core"] = float(score_gap)
                    detail["no_risky_movement_max_local_pressure"] = float(phase_max_local_pressure)
                    detail["blended_score"] = float(capped_score)
                    route_horizon_capped_phases.append(int(phase_idx))
        horizon_action = max(
            blended_scores,
            key=lambda phase_idx: (
                blended_scores.get(phase_idx, float("-inf")),
                route_horizon_completion_scores.get(phase_idx, float("-inf")),
                double_pressure_phase_scores.get(phase_idx, float("-inf")),
                -phase_idx,
            ),
        )
        finite_storage_action = int(horizon_action)
        score_gap_consensus_guard_enabled = bool(dynamic_params.get("route_horizon_score_gap_consensus_guard"))
        score_gap_consensus_total_ceiling = float(
            dynamic_params.get("route_horizon_score_gap_consensus_total_ceiling", float("-inf"))
        )
        score_gap_consensus_pressure_ceiling = float(
            dynamic_params.get("route_horizon_score_gap_consensus_pressure_ceiling", float("inf"))
        )
        score_gap_consensus_gap_floor = float(
            dynamic_params.get("route_horizon_score_gap_consensus_gap_floor", float("inf"))
        )
        score_gap_consensus_storage = state_storage_summary(finite_storage_state)
        if (
            score_gap_consensus_guard_enabled
            and not route_horizon_completion_filter_used
            and int(pressure_action) == int(capacity_action) == int(double_pressure_action)
            and score_gap_consensus_storage["max_occupancy_ratio"]
            >= float(dynamic_params.get("route_horizon_severe_occupancy_threshold", 1.0))
            and score_gap_consensus_storage["min_residual_ratio"]
            <= float(dynamic_params.get("route_horizon_low_residual_threshold", 0.0))
        ):
            baseline_action = int(pressure_action)
            selected_phase_totals_now = finite_phase_scores.get(int(finite_storage_action), {}).get("component_totals", {})
            selected_total_now = float(selected_phase_totals_now.get("total", 0.0))
            selected_pressure_now = float(selected_phase_totals_now.get("pressure", 0.0))
            selected_score_gap = float(
                route_horizon_completion_scores.get(baseline_action, float("-inf"))
                - route_horizon_completion_scores.get(int(finite_storage_action), float("-inf"))
            )
            if (
                int(finite_storage_action) != baseline_action
                and selected_total_now <= score_gap_consensus_total_ceiling
                and selected_pressure_now <= score_gap_consensus_pressure_ceiling
                and selected_score_gap >= score_gap_consensus_gap_floor
            ):
                finite_storage_action = baseline_action
                route_horizon_score_gap_consensus_guard_used = True
        if dynamic_params.get("route_horizon_baseline_dominance_filter"):
            best_baseline_action = max(
                baseline_candidates,
                key=lambda phase_idx: (
                    blended_scores.get(phase_idx, float("-inf")),
                    route_horizon_completion_scores.get(phase_idx, float("-inf")),
                    double_pressure_phase_scores.get(phase_idx, float("-inf")),
                    capacity_phase_scores.get(phase_idx, float("-inf")),
                    pressure_phase_scores.get(phase_idx, float("-inf")),
                    -phase_idx,
                ),
            )
            margin = float(dynamic_params.get("route_horizon_baseline_margin", 0.0))
            if (
                int(horizon_action) not in baseline_candidates
                and blended_scores.get(int(horizon_action), float("-inf"))
                <= blended_scores.get(int(best_baseline_action), float("-inf")) + margin
            ):
                finite_storage_action = int(best_baseline_action)
                route_horizon_dominance_filter_used = True
        if (
            dynamic_params.get("route_horizon_max_pressure_envelope")
            and int(finite_storage_action) != int(pressure_action)
        ):
            normalized_service = normalize_phase_scores(completion_service_scores)
            service_blend = float(dynamic_params.get("route_horizon_max_pressure_service_blend", 0.0))
            selected_completion_score = route_horizon_completion_scores.get(int(finite_storage_action), 0.0) + service_blend * normalized_service.get(int(finite_storage_action), 0.0)
            pressure_completion_score = route_horizon_completion_scores.get(int(pressure_action), 0.0) + service_blend * normalized_service.get(int(pressure_action), 0.0)
            margin = float(dynamic_params.get("route_horizon_max_pressure_margin", 0.0))
            if selected_completion_score <= pressure_completion_score + margin:
                finite_storage_action = int(pressure_action)
                route_horizon_max_pressure_envelope_used = True
        if dynamic_params.get("route_horizon_core_baseline_envelope"):
            normalized_service = normalize_phase_scores(completion_service_scores)
            service_blend = float(dynamic_params.get("route_horizon_core_baseline_service_blend", 0.0))
            baseline_candidates = sorted({int(pressure_action), int(capacity_action), int(double_pressure_action)})

            def core_completion_score(phase_idx: int) -> float:
                return route_horizon_completion_scores.get(int(phase_idx), 0.0) + service_blend * normalized_service.get(int(phase_idx), 0.0)

            best_core_action = max(
                baseline_candidates,
                key=lambda phase_idx: (
                    core_completion_score(phase_idx),
                    double_pressure_phase_scores.get(phase_idx, float("-inf")),
                    capacity_phase_scores.get(phase_idx, float("-inf")),
                    pressure_phase_scores.get(phase_idx, float("-inf")),
                    -phase_idx,
                ),
            )
            selected_completion_score = core_completion_score(int(finite_storage_action))
            best_core_completion_score = core_completion_score(int(best_core_action))
            margin = float(dynamic_params.get("route_horizon_core_baseline_margin", 0.0))
            if int(finite_storage_action) != int(best_core_action) and selected_completion_score <= best_core_completion_score + margin:
                finite_storage_action = int(best_core_action)
                route_horizon_core_baseline_envelope_used = True
        if (
            dynamic_params.get("route_horizon_double_pressure_envelope")
            and fraction_gate_active(
                dynamic_params,
                "route_horizon_double_pressure_envelope_start_fraction",
                step=step,
                warmup=warmup,
                steps=steps,
            )
            and int(finite_storage_action) != int(double_pressure_action)
        ):
            normalized_service = normalize_phase_scores(completion_service_scores)
            service_blend = float(dynamic_params.get("route_horizon_double_pressure_service_blend", 0.0))
            selected_completion_score = route_horizon_completion_scores.get(int(finite_storage_action), 0.0) + service_blend * normalized_service.get(int(finite_storage_action), 0.0)
            double_completion_score = route_horizon_completion_scores.get(int(double_pressure_action), 0.0) + service_blend * normalized_service.get(int(double_pressure_action), 0.0)
            margin = float(dynamic_params.get("route_horizon_double_pressure_margin", 0.0))
            if selected_completion_score <= double_completion_score + margin:
                finite_storage_action = int(double_pressure_action)
                route_horizon_double_pressure_envelope_used = True
        if (
            dynamic_params.get("route_horizon_core_minimax_guard")
            and fraction_gate_active(
                dynamic_params,
                "route_horizon_core_minimax_start_fraction",
                step=step,
                warmup=warmup,
                steps=steps,
            )
        ):
            normalized_capacity = normalize_phase_scores(capacity_phase_scores)
            normalized_service = normalize_phase_scores(completion_service_scores)
            horizon_blend = float(dynamic_params.get("route_horizon_core_minimax_horizon_blend", 0.0))
            service_blend = float(dynamic_params.get("route_horizon_core_minimax_service_blend", 0.0))
            candidates = sorted({int(finite_storage_action), int(pressure_action), int(capacity_action), int(double_pressure_action)})

            def core_minimax_score(phase_idx: int) -> tuple[float, float, float, float, float, int]:
                pressure_score = normalized_pressure.get(phase_idx, 0.0)
                capacity_score = normalized_capacity.get(phase_idx, 0.0)
                double_score = normalized_double.get(phase_idx, 0.0)
                completion_score = (
                    horizon_blend * normalized_horizon.get(phase_idx, 0.0)
                    + service_blend * normalized_service.get(phase_idx, 0.0)
                )
                return (
                    min(pressure_score, capacity_score, double_score),
                    pressure_score + capacity_score + double_score,
                    completion_score,
                    route_horizon_completion_scores.get(phase_idx, float("-inf")),
                    completion_service_scores.get(phase_idx, float("-inf")),
                    -phase_idx,
                )

            minimax_action = max(candidates, key=core_minimax_score)
            if int(minimax_action) != int(finite_storage_action):
                finite_storage_action = int(minimax_action)
                route_horizon_core_minimax_guard_used = True
        if (
            dynamic_params.get("route_horizon_capacity_rescue_guard")
            and fraction_gate_active(
                dynamic_params,
                "route_horizon_capacity_rescue_start_fraction",
                step=step,
                warmup=warmup,
                steps=steps,
            )
            and int(finite_storage_action) != int(capacity_action)
        ):
            normalized_service = normalize_phase_scores(completion_service_scores)
            service_blend = float(dynamic_params.get("route_horizon_capacity_rescue_service_blend", 0.0))
            margin = float(dynamic_params.get("route_horizon_capacity_rescue_margin", 0.0))
            double_tolerance = float(dynamic_params.get("route_horizon_capacity_rescue_double_tolerance", float("inf")))
            selected_action = int(finite_storage_action)
            capacity_action_int = int(capacity_action)
            selected_completion_score = route_horizon_completion_scores.get(selected_action, 0.0) + service_blend * normalized_service.get(selected_action, 0.0)
            capacity_completion_score = route_horizon_completion_scores.get(capacity_action_int, 0.0) + service_blend * normalized_service.get(capacity_action_int, 0.0)
            selected_double_score = normalized_double.get(selected_action, 0.0)
            capacity_double_score = normalized_double.get(capacity_action_int, 0.0)
            if (
                selected_completion_score + margin < capacity_completion_score
                and capacity_double_score + double_tolerance >= selected_double_score
            ):
                finite_storage_action = capacity_action_int
                route_horizon_capacity_rescue_guard_used = True
        if (
            dynamic_params.get("route_horizon_capacity_score_envelope")
            and int(finite_storage_action) != int(capacity_action)
        ):
            margin = float(dynamic_params.get("route_horizon_capacity_score_margin", 0.0))
            selected_capacity_score = capacity_phase_scores.get(int(finite_storage_action), float("-inf"))
            best_capacity_score = capacity_phase_scores.get(int(capacity_action), float("-inf"))
            if selected_capacity_score + margin < best_capacity_score:
                finite_storage_action = int(capacity_action)
                route_horizon_capacity_score_envelope_used = True
        if (
            dynamic_params.get("route_horizon_native_capacity_score_rescue_guard")
            and int(finite_storage_action) == int(double_pressure_action)
            and int(pressure_action) == int(capacity_action)
            and int(capacity_action) != int(double_pressure_action)
        ):
            storage = state_storage_summary(finite_storage_state)
            occupancy_threshold = float(
                dynamic_params.get("route_horizon_native_capacity_score_rescue_occupancy_threshold", 1.1)
            )
            residual_threshold = float(
                dynamic_params.get("route_horizon_native_capacity_score_rescue_residual_threshold", -1.0)
            )
            selected_total = float(finite_phase_scores.get(int(finite_storage_action), {}).get("score", float("-inf")))
            capacity_total = float(finite_phase_scores.get(int(capacity_action), {}).get("score", float("-inf")))
            min_total_gap = float(dynamic_params.get("route_horizon_native_capacity_score_rescue_min_total_gap", 0.0))
            selected_total_ceiling = float(
                dynamic_params.get("route_horizon_native_capacity_score_rescue_selected_total_ceiling", 0.0)
            )
            if (
                (storage["max_occupancy_ratio"] >= occupancy_threshold or storage["min_residual_ratio"] <= residual_threshold)
                and selected_total <= selected_total_ceiling
                and capacity_total >= selected_total + min_total_gap
            ):
                finite_storage_action = int(capacity_action)
                route_horizon_native_capacity_score_rescue_guard_used = True
        if (
            dynamic_params.get("route_horizon_pressure_safe_guard")
            and fraction_gate_active(
                dynamic_params,
                "route_horizon_pressure_safe_start_fraction",
                step=step,
                warmup=warmup,
                steps=steps,
            )
            and int(finite_storage_action) != int(pressure_action)
        ):
            normalized_capacity = normalize_phase_scores(capacity_phase_scores)
            selected_action = int(finite_storage_action)
            pressure_action_int = int(pressure_action)
            min_gain = float(dynamic_params.get("route_horizon_pressure_safe_min_completion_gain", 0.0))
            capacity_tolerance = float(dynamic_params.get("route_horizon_pressure_safe_capacity_tolerance", 0.0))
            double_tolerance = float(dynamic_params.get("route_horizon_pressure_safe_double_tolerance", 0.0))
            selected_completion = route_horizon_completion_scores.get(selected_action, 0.0)
            pressure_completion = route_horizon_completion_scores.get(pressure_action_int, 0.0)
            selected_capacity = normalized_capacity.get(selected_action, 0.0)
            pressure_capacity = normalized_capacity.get(pressure_action_int, 0.0)
            selected_double = normalized_double.get(selected_action, 0.0)
            pressure_double = normalized_double.get(pressure_action_int, 0.0)
            if (
                selected_completion < pressure_completion + min_gain
                or selected_capacity + capacity_tolerance < pressure_capacity
                or selected_double + double_tolerance < pressure_double
            ):
                finite_storage_action = pressure_action_int
                route_horizon_pressure_safe_guard_used = True
        if (
            dynamic_params.get("route_horizon_severe_double_guard")
            and fraction_gate_active(
                dynamic_params,
                "route_horizon_severe_double_start_fraction",
                step=step,
                warmup=warmup,
                steps=steps,
            )
            and int(finite_storage_action) != int(double_pressure_action)
        ):
            storage = state_storage_summary(finite_storage_state)
            occupancy_threshold = float(dynamic_params.get("route_horizon_severe_double_occupancy_threshold", 1.1))
            residual_threshold = float(dynamic_params.get("route_horizon_severe_double_residual_threshold", -1.0))
            severe = (
                storage["max_occupancy_ratio"] >= occupancy_threshold
                or storage["min_residual_ratio"] <= residual_threshold
            )
            if severe:
                normalized_horizon = normalize_phase_scores(route_horizon_completion_scores)
                normalized_capacity = normalize_phase_scores(capacity_phase_scores)
                normalized_service = normalize_phase_scores(completion_service_scores)
                service_blend = float(dynamic_params.get("route_horizon_severe_double_service_blend", 0.0))
                max_completion_advantage = float(
                    dynamic_params.get("route_horizon_severe_double_max_completion_advantage", 0.0)
                )
                capacity_tolerance = float(dynamic_params.get("route_horizon_severe_double_capacity_tolerance", 0.0))
                selected_action = int(finite_storage_action)
                double_action_int = int(double_pressure_action)
                selected_completion = normalized_horizon.get(selected_action, 0.0) + service_blend * normalized_service.get(selected_action, 0.0)
                double_completion = normalized_horizon.get(double_action_int, 0.0) + service_blend * normalized_service.get(double_action_int, 0.0)
                selected_capacity = normalized_capacity.get(selected_action, 0.0)
                double_capacity = normalized_capacity.get(double_action_int, 0.0)
                if (
                    double_completion + max_completion_advantage >= selected_completion
                    and double_capacity + capacity_tolerance >= selected_capacity
                ):
                    finite_storage_action = double_action_int
                    route_horizon_severe_double_guard_used = True
        if (
            dynamic_params.get("route_horizon_pressure_double_conflict_guard")
            and fraction_gate_active(
                dynamic_params,
                "route_horizon_pressure_double_conflict_start_fraction",
                step=step,
                warmup=warmup,
                steps=steps,
            )
            and not route_horizon_native_capacity_score_rescue_guard_used
            and int(finite_storage_action) == int(pressure_action)
            and int(double_pressure_action) != int(pressure_action)
        ):
            storage = state_storage_summary(finite_storage_state)
            occupancy_threshold = float(dynamic_params.get("route_horizon_pressure_double_conflict_occupancy_threshold", 1.1))
            residual_threshold = float(dynamic_params.get("route_horizon_pressure_double_conflict_residual_threshold", -1.0))
            if (
                storage["max_occupancy_ratio"] >= occupancy_threshold
                or storage["min_residual_ratio"] <= residual_threshold
            ):
                finite_storage_action = int(double_pressure_action)
                route_horizon_pressure_double_conflict_guard_used = True
        if (
            dynamic_params.get("route_horizon_core_consensus_guard")
            and fraction_gate_active(
                dynamic_params,
                "route_horizon_core_consensus_start_fraction",
                step=step,
                warmup=warmup,
                steps=steps,
            )
            and int(finite_storage_action) != int(pressure_action)
            and int(pressure_action) == int(capacity_action) == int(double_pressure_action)
        ):
            storage = state_storage_summary(finite_storage_state)
            occupancy_threshold = float(dynamic_params.get("route_horizon_core_consensus_occupancy_threshold", 1.1))
            residual_threshold = float(dynamic_params.get("route_horizon_core_consensus_residual_threshold", -1.0))
            if (
                storage["max_occupancy_ratio"] >= occupancy_threshold
                or storage["min_residual_ratio"] <= residual_threshold
            ):
                finite_storage_action = int(pressure_action)
                route_horizon_core_consensus_guard_used = True
        if (
            dynamic_params.get("route_horizon_tail_completion_rescue")
            and fraction_gate_active(
                dynamic_params,
                "route_horizon_tail_rescue_start_fraction",
                step=step,
                warmup=warmup,
                steps=steps,
            )
        ):
            normalized_capacity = normalize_phase_scores(capacity_phase_scores)
            normalized_service = normalize_phase_scores(completion_service_scores)
            service_blend = float(dynamic_params.get("route_horizon_tail_rescue_service_blend", 0.0))
            min_gain = float(dynamic_params.get("route_horizon_tail_rescue_min_completion_gain", 0.0))
            core_tolerance = float(dynamic_params.get("route_horizon_tail_rescue_core_tolerance", 0.0))

            def tail_completion_score(phase_idx: int) -> float:
                return normalized_horizon.get(phase_idx, 0.0) + service_blend * normalized_service.get(phase_idx, 0.0)

            def tail_core_floor(phase_idx: int) -> float:
                return min(
                    normalized_pressure.get(phase_idx, 0.0),
                    normalized_capacity.get(phase_idx, 0.0),
                    normalized_double.get(phase_idx, 0.0),
                )

            tail_action = max(
                route_horizon_completion_scores,
                key=lambda phase_idx: (
                    tail_completion_score(phase_idx),
                    tail_core_floor(phase_idx),
                    normalized_pressure.get(phase_idx, 0.0)
                    + normalized_capacity.get(phase_idx, 0.0)
                    + normalized_double.get(phase_idx, 0.0),
                    route_horizon_completion_scores.get(phase_idx, float("-inf")),
                    -phase_idx,
                ),
            )
            selected_action = int(finite_storage_action)
            tail_action_int = int(tail_action)
            if (
                tail_action_int != selected_action
                and tail_completion_score(tail_action_int) >= tail_completion_score(selected_action) + min_gain
                and tail_core_floor(tail_action_int) + core_tolerance >= tail_core_floor(selected_action)
            ):
                finite_storage_action = tail_action_int
                route_horizon_tail_completion_rescue_used = True
        if (
            dynamic_params.get("route_horizon_completion_conflict_guard")
            and fraction_gate_active(
                dynamic_params,
                "route_horizon_completion_conflict_start_fraction",
                step=step,
                warmup=warmup,
                steps=steps,
            )
            and int(finite_storage_action) != int(pressure_action)
            and int(pressure_action) == int(double_pressure_action)
        ):
            storage = state_storage_summary(finite_storage_state)
            occupancy_threshold = float(dynamic_params.get("route_horizon_completion_conflict_occupancy_threshold", 1.1))
            residual_threshold = float(dynamic_params.get("route_horizon_completion_conflict_residual_threshold", -1.0))
            if (
                storage["max_occupancy_ratio"] >= occupancy_threshold
                or storage["min_residual_ratio"] <= residual_threshold
            ):
                finite_storage_action = int(pressure_action)
                route_horizon_completion_conflict_guard_used = True
        if (
            dynamic_params.get("route_horizon_capacity_completion_conflict_guard")
            and int(finite_storage_action) != int(capacity_action)
            and int(pressure_action) == int(capacity_action)
        ):
            storage = state_storage_summary(finite_storage_state)
            occupancy_threshold = float(
                dynamic_params.get("route_horizon_capacity_completion_conflict_occupancy_threshold", 1.1)
            )
            residual_threshold = float(
                dynamic_params.get("route_horizon_capacity_completion_conflict_residual_threshold", -1.0)
            )
            if (
                storage["max_occupancy_ratio"] >= occupancy_threshold
                or storage["min_residual_ratio"] <= residual_threshold
            ):
                finite_storage_action = int(capacity_action)
                route_horizon_capacity_completion_conflict_guard_used = True
        if (
            dynamic_params.get("route_horizon_early_capacity_completion_conflict_guard")
            and step is not None
            and warmup is not None
            and steps is not None
            and steps > warmup
            and int(finite_storage_action) == int(double_pressure_action)
            and int(pressure_action) == int(capacity_action)
            and int(capacity_action) != int(double_pressure_action)
        ):
            elapsed_fraction = max(float(step - warmup), 0.0) / max(float(steps - warmup), 1.0)
            start_fraction = float(dynamic_params.get("route_horizon_early_capacity_completion_conflict_start_fraction", 0.0))
            end_fraction = float(dynamic_params.get("route_horizon_early_capacity_completion_conflict_end_fraction", 1.0))
            if start_fraction <= elapsed_fraction <= end_fraction:
                storage = state_storage_summary(finite_storage_state)
                occupancy_threshold = float(
                    dynamic_params.get("route_horizon_early_capacity_completion_conflict_occupancy_threshold", 1.1)
                )
                occupancy_upper_threshold = dynamic_params.get(
                    "route_horizon_early_capacity_completion_conflict_occupancy_upper_threshold"
                )
                residual_threshold = float(
                    dynamic_params.get("route_horizon_early_capacity_completion_conflict_residual_threshold", -1.0)
                )
                if (
                    (
                        storage["max_occupancy_ratio"] >= occupancy_threshold
                        or storage["min_residual_ratio"] <= residual_threshold
                    )
                    and (
                        occupancy_upper_threshold is None
                        or storage["max_occupancy_ratio"] <= float(occupancy_upper_threshold)
                    )
                ):
                    finite_storage_action = int(capacity_action)
                    route_horizon_early_capacity_completion_conflict_guard_used = True
        if (
            dynamic_params.get("route_horizon_negative_total_completion_conflict_guard")
            and int(finite_storage_action) != int(pressure_action)
            and int(pressure_action) == int(double_pressure_action)
        ):
            storage = state_storage_summary(finite_storage_state)
            occupancy_threshold = float(
                dynamic_params.get("route_horizon_negative_total_completion_conflict_occupancy_threshold", 1.1)
            )
            residual_threshold = float(
                dynamic_params.get("route_horizon_negative_total_completion_conflict_residual_threshold", -1.0)
            )
            total_ceiling = float(
                dynamic_params.get("route_horizon_negative_total_completion_conflict_total_ceiling", 0.0)
            )
            selected_total = float(
                finite_phase_scores.get(int(finite_storage_action), {}).get("component_totals", {}).get("total", 0.0)
            )
            if (
                (storage["max_occupancy_ratio"] >= occupancy_threshold or storage["min_residual_ratio"] <= residual_threshold)
                and selected_total <= total_ceiling
            ):
                finite_storage_action = int(pressure_action)
                route_horizon_negative_total_completion_conflict_guard_used = True
        if (
            dynamic_params.get("route_horizon_low_total_consensus_completion_guard")
            and int(finite_storage_action) != int(pressure_action)
            and int(pressure_action) == int(capacity_action) == int(double_pressure_action)
        ):
            storage = state_storage_summary(finite_storage_state)
            elapsed_fraction = elapsed_fraction_at(step, warmup, steps)
            start_fraction = float(
                dynamic_params.get("route_horizon_low_total_consensus_completion_start_fraction", 0.0)
            )
            end_fraction = float(
                dynamic_params.get("route_horizon_low_total_consensus_completion_end_fraction", 1.0)
            )
            occupancy_threshold = float(
                dynamic_params.get("route_horizon_low_total_consensus_completion_occupancy_threshold", 1.1)
            )
            residual_threshold = float(
                dynamic_params.get("route_horizon_low_total_consensus_completion_residual_threshold", -1.0)
            )
            selected_totals = finite_phase_scores.get(int(finite_storage_action), {}).get("component_totals", {})
            selected_total = float(selected_totals.get("total", 0.0))
            selected_pressure_component = float(selected_totals.get("pressure", 0.0))
            total_ceiling = float(
                dynamic_params.get("route_horizon_low_total_consensus_completion_total_ceiling", 0.0)
            )
            pressure_ceiling = float(
                dynamic_params.get("route_horizon_low_total_consensus_completion_pressure_ceiling", 0.0)
            )
            if (
                elapsed_fraction is not None
                and start_fraction <= elapsed_fraction <= end_fraction
                and (
                    storage["max_occupancy_ratio"] >= occupancy_threshold
                    or storage["min_residual_ratio"] <= residual_threshold
                )
                and selected_total <= total_ceiling
                and selected_pressure_component <= pressure_ceiling
            ):
                finite_storage_action = int(pressure_action)
                route_horizon_low_total_consensus_completion_guard_used = True
        if (
            dynamic_params.get("route_horizon_negative_total_core_consensus_guard")
            and int(finite_storage_action) != int(pressure_action)
            and int(pressure_action) == int(capacity_action) == int(double_pressure_action)
        ):
            storage = state_storage_summary(finite_storage_state)
            occupancy_threshold = float(
                dynamic_params.get("route_horizon_negative_total_core_consensus_occupancy_threshold", 1.05)
            )
            residual_threshold = float(
                dynamic_params.get("route_horizon_negative_total_core_consensus_residual_threshold", 0.0)
            )
            selected_totals = finite_phase_scores.get(int(finite_storage_action), {}).get("component_totals", {})
            selected_total = float(selected_totals.get("total", 0.0))
            selected_pressure_component = float(selected_totals.get("pressure", 0.0))
            total_ceiling = float(
                dynamic_params.get("route_horizon_negative_total_core_consensus_total_ceiling", -5.0)
            )
            if (
                selected_total <= total_ceiling
                and selected_pressure_component < 0.0
                and (
                    storage["max_occupancy_ratio"] >= occupancy_threshold
                    or storage["min_residual_ratio"] <= residual_threshold
                )
            ):
                finite_storage_action = int(pressure_action)
                route_horizon_core_consensus_guard_used = True
        route_horizon_completion_filter_used = True
    score_gap_consensus_guard_enabled = bool(dynamic_params.get("route_horizon_score_gap_consensus_guard"))
    score_gap_consensus_total_ceiling = float(
        dynamic_params.get("route_horizon_score_gap_consensus_total_ceiling", float("-inf"))
    )
    score_gap_consensus_pressure_ceiling = float(
        dynamic_params.get("route_horizon_score_gap_consensus_pressure_ceiling", float("inf"))
    )
    score_gap_consensus_gap_floor = float(
        dynamic_params.get("route_horizon_score_gap_consensus_gap_floor", float("inf"))
    )
    score_gap_consensus_storage = state_storage_summary(finite_storage_state)
    if (
        score_gap_consensus_guard_enabled
        and not route_horizon_completion_filter_used
        and int(pressure_action) == int(capacity_action) == int(double_pressure_action)
        and score_gap_consensus_storage["max_occupancy_ratio"]
        >= float(dynamic_params.get("route_horizon_severe_occupancy_threshold", 1.0))
        and score_gap_consensus_storage["min_residual_ratio"]
        <= float(dynamic_params.get("route_horizon_low_residual_threshold", 0.0))
    ):
        baseline_action = int(pressure_action)
        selected_phase_totals_now = finite_phase_scores.get(int(finite_storage_action), {}).get("component_totals", {})
        selected_total_now = float(selected_phase_totals_now.get("total", 0.0))
        selected_pressure_now = float(selected_phase_totals_now.get("pressure", 0.0))
        selected_score_gap = float(
            route_horizon_completion_scores.get(baseline_action, float("-inf"))
            - route_horizon_completion_scores.get(int(finite_storage_action), float("-inf"))
        )
        if (
            int(finite_storage_action) != baseline_action
            and selected_total_now <= score_gap_consensus_total_ceiling
            and selected_pressure_now <= score_gap_consensus_pressure_ceiling
            and selected_score_gap >= score_gap_consensus_gap_floor
        ):
            finite_storage_action = baseline_action
            route_horizon_score_gap_consensus_guard_used = True
    if (
        dynamic_params.get("terminal_exit_protection_guard")
        and step is not None
        and warmup is not None
        and steps is not None
        and steps > warmup
        and completion_risk_active(dynamic_params, finite_storage_state, queues, step=step, warmup=warmup, steps=steps)
    ):
        elapsed_fraction = max(float(step - warmup), 0.0) / max(float(steps - warmup), 1.0)
        if elapsed_fraction >= float(dynamic_params.get("terminal_exit_guard_start_fraction", 0.0)):
            normalized_horizon = normalize_phase_scores(route_horizon_completion_scores)
            normalized_service = normalize_phase_scores(completion_service_scores)
            normalized_double = normalize_phase_scores(double_pressure_phase_scores)
            normalized_capacity = normalize_phase_scores(capacity_phase_scores)
            normalized_pressure = normalize_phase_scores(pressure_phase_scores)
            horizon_blend = float(dynamic_params.get("terminal_exit_guard_horizon_blend", 1.0))
            service_blend = float(dynamic_params.get("terminal_exit_guard_service_blend", 0.0))
            double_blend = float(dynamic_params.get("terminal_exit_guard_double_blend", 0.0))
            capacity_blend = float(dynamic_params.get("terminal_exit_guard_capacity_blend", 0.0))
            pressure_blend = float(dynamic_params.get("terminal_exit_guard_pressure_blend", 0.0))
            terminal_exit_scores = {
                phase_idx: horizon_blend * normalized_horizon.get(phase_idx, 0.0)
                + service_blend * normalized_service.get(phase_idx, 0.0)
                + double_blend * normalized_double.get(phase_idx, 0.0)
                + capacity_blend * normalized_capacity.get(phase_idx, 0.0)
                + pressure_blend * normalized_pressure.get(phase_idx, 0.0)
                for phase_idx in greens
            }
            finite_storage_action = max(
                terminal_exit_scores,
                key=lambda phase_idx: (
                    terminal_exit_scores.get(phase_idx, float("-inf")),
                    route_horizon_completion_scores.get(phase_idx, float("-inf")),
                    completion_service_scores.get(phase_idx, float("-inf")),
                    double_pressure_phase_scores.get(phase_idx, float("-inf")),
                    capacity_phase_scores.get(phase_idx, float("-inf")),
                    pressure_phase_scores.get(phase_idx, float("-inf")),
                    -phase_idx,
                ),
            )
            terminal_exit_protection_guard_used = True
    route_demand_completion_scores = {
        int(phase_idx): phase_route_demand_completion_score(
            phase_idx,
            states,
            movements,
            queues,
            capacities,
            finite_storage_state,
            route_completion_state,
            dynamic_params,
        )
        for phase_idx in greens
    }
    if (
        not (terminal_fallback_used and dynamic_params.get("terminal_flush_locks_dynamic"))
        and
        not route_horizon_completion_filter_used
        and
        dynamic_params.get("route_demand_completion_filter")
        and completion_risk_active(dynamic_params, finite_storage_state, queues, step=step, warmup=warmup, steps=steps)
        and route_demand_completion_scores
    ):
        finite_storage_action = max(
            route_demand_completion_scores,
            key=lambda phase_idx: (
                route_demand_completion_scores.get(phase_idx, float("-inf")),
                double_pressure_phase_scores.get(phase_idx, float("-inf")),
                capacity_phase_scores.get(phase_idx, float("-inf")),
                pressure_phase_scores.get(phase_idx, float("-inf")),
                -phase_idx,
            ),
        )
        route_demand_completion_filter_used = True
        if dynamic_params.get("route_demand_double_score_veto") and finite_storage_action != double_pressure_action:
            selected_double_score = double_pressure_phase_scores.get(int(finite_storage_action), float("-inf"))
            best_double_score = double_pressure_phase_scores.get(int(double_pressure_action), float("-inf"))
            tolerance = float(dynamic_params.get("route_demand_double_score_tolerance", 0.0))
            if selected_double_score + tolerance < best_double_score:
                finite_storage_action = int(double_pressure_action)
                route_demand_double_score_veto_used = True
    if (
        not (terminal_fallback_used and dynamic_params.get("terminal_flush_locks_dynamic"))
        and
        not route_horizon_completion_filter_used
        and
        not route_demand_completion_filter_used
        and
        dynamic_params.get("route_completion_prediction_filter")
        and completion_risk_active(dynamic_params, finite_storage_state, queues, step=step, warmup=warmup, steps=steps)
        and route_completion_prediction_scores
    ):
        finite_storage_action = max(
            route_completion_prediction_scores,
            key=lambda phase_idx: (
                route_completion_prediction_scores.get(phase_idx, float("-inf")),
                double_pressure_phase_scores.get(phase_idx, float("-inf")),
                capacity_phase_scores.get(phase_idx, float("-inf")),
                pressure_phase_scores.get(phase_idx, float("-inf")),
                -phase_idx,
            ),
        )
        route_completion_prediction_filter_used = True
    if (
        not (terminal_fallback_used and dynamic_params.get("terminal_flush_locks_dynamic"))
        and
        not route_horizon_completion_filter_used
        and
        not route_demand_completion_filter_used
        and
        not route_completion_prediction_filter_used
        and completion_risk_active(dynamic_params, finite_storage_state, queues, step=step, warmup=warmup, steps=steps)
    ):
        selected_service = completion_service_scores.get(int(finite_storage_action), 0.0)
        baseline_candidates = sorted({int(pressure_action), int(capacity_action), int(double_pressure_action)})
        best_completion_action = max(
            baseline_candidates,
            key=lambda phase_idx: (
                completion_service_scores.get(phase_idx, 0.0),
                double_pressure_phase_scores.get(phase_idx, float("-inf")),
                capacity_phase_scores.get(phase_idx, float("-inf")),
                pressure_phase_scores.get(phase_idx, float("-inf")),
                -phase_idx,
            ),
        )
        best_service = completion_service_scores.get(int(best_completion_action), 0.0)
        tolerance = float(dynamic_params.get("completion_service_tolerance", 0.0))
        if selected_service + tolerance < best_service:
            finite_storage_action = int(best_completion_action)
            completion_risk_filter_used = True
    if completion_safety_veto_active(
        dynamic_params,
        finite_storage_state,
        queues,
        step=step,
        warmup=warmup,
        steps=steps,
    ):
        service_blend = float(dynamic_params.get("completion_safety_service_blend", 0.0))
        tolerance = float(dynamic_params.get("completion_safety_tolerance", 0.0))
        baseline_candidates = sorted({int(pressure_action), int(capacity_action), int(double_pressure_action)})

        def conservative_completion_score(phase_idx: int) -> float:
            return float(route_horizon_completion_scores.get(phase_idx, 0.0)) + service_blend * float(
                completion_service_scores.get(phase_idx, 0.0)
            )

        best_completion_action = max(
            baseline_candidates,
            key=lambda phase_idx: (
                conservative_completion_score(phase_idx),
                double_pressure_phase_scores.get(phase_idx, float("-inf")),
                capacity_phase_scores.get(phase_idx, float("-inf")),
                pressure_phase_scores.get(phase_idx, float("-inf")),
                -phase_idx,
            ),
        )
        selected_completion_score = conservative_completion_score(int(finite_storage_action))
        best_completion_score = conservative_completion_score(int(best_completion_action))
        if selected_completion_score + tolerance < best_completion_score:
            finite_storage_action = int(best_completion_action)
            completion_risk_filter_used = True
            completion_safety_veto_used = True
    if (
        dynamic_params.get("route_horizon_negative_total_raw_consensus_guard")
        and not route_horizon_completion_filter_used
        and not completion_safety_veto_used
        and int(finite_storage_action) != int(pressure_action)
        and int(pressure_action) == int(capacity_action) == int(double_pressure_action)
    ):
        storage = state_storage_summary(finite_storage_state)
        occupancy_threshold = float(
            dynamic_params.get("route_horizon_negative_total_raw_consensus_occupancy_threshold", 1.1)
        )
        residual_threshold = float(
            dynamic_params.get("route_horizon_negative_total_raw_consensus_residual_threshold", -1.0)
        )
        total_ceiling = float(
            dynamic_params.get("route_horizon_negative_total_raw_consensus_total_ceiling", 0.0)
        )
        selected_total = float(
            finite_phase_scores.get(int(finite_storage_action), {}).get("component_totals", {}).get("total", 0.0)
        )
        if (
            (storage["max_occupancy_ratio"] >= occupancy_threshold or storage["min_residual_ratio"] <= residual_threshold)
            and selected_total <= total_ceiling
        ):
            finite_storage_action = int(pressure_action)
            route_horizon_negative_total_raw_consensus_guard_used = True
    if (
        dynamic_params.get("route_horizon_raw_consensus_guard")
        and not route_horizon_completion_filter_used
        and not completion_safety_veto_used
        and fraction_gate_active(
            dynamic_params,
            "route_horizon_raw_consensus_start_fraction",
            step=step,
            warmup=warmup,
            steps=steps,
        )
        and int(finite_storage_action) != int(pressure_action)
        and int(pressure_action) == int(capacity_action) == int(double_pressure_action)
    ):
        storage = state_storage_summary(finite_storage_state)
        occupancy_threshold = float(dynamic_params.get("route_horizon_raw_consensus_occupancy_threshold", 1.1))
        residual_threshold = float(dynamic_params.get("route_horizon_raw_consensus_residual_threshold", -1.0))
        if (
            storage["max_occupancy_ratio"] >= occupancy_threshold
            or storage["min_residual_ratio"] <= residual_threshold
        ):
            finite_storage_action = int(pressure_action)
            route_horizon_raw_consensus_guard_used = True
    if (
        dynamic_params.get("post_completion_veto_double_conflict_guard")
        and completion_safety_veto_used
        and int(finite_storage_action) == int(pressure_action)
        and int(double_pressure_action) != int(pressure_action)
    ):
        if (
            dynamic_params.get("post_completion_veto_double_conflict_require_no_completion_filter")
            and route_horizon_completion_filter_used
        ):
            pass
        elif (
            dynamic_params.get("post_completion_veto_double_conflict_require_capacity_consensus")
            and int(capacity_action) != int(double_pressure_action)
        ):
            pass
        else:
            storage = state_storage_summary(finite_storage_state)
            occupancy_threshold = float(dynamic_params.get("post_completion_veto_double_conflict_occupancy_threshold", 1.1))
            residual_threshold = float(dynamic_params.get("post_completion_veto_double_conflict_residual_threshold", -1.0))
            if (
                storage["max_occupancy_ratio"] >= occupancy_threshold
                or storage["min_residual_ratio"] <= residual_threshold
            ):
                finite_storage_action = int(double_pressure_action)
                post_completion_veto_double_conflict_guard_used = True
    if controller in V1_6_CONTROLLER_IDS:
        safe_phases = completion_safe_feasible_set(
            {p: decomposition["score"] for p, decomposition in finite_phase_scores.items()},
            {
                "pressure": pressure_phase_scores,
                "capacity_aware": capacity_phase_scores,
                "double_pressure": double_pressure_phase_scores,
            },
            finite_storage_state, queues,
            {phase_idx: movements for phase_idx in greens},
            step=step, warmup=warmup, steps=steps, params=DYNAMIC_V1_6_PARAMS,
        )
        if safe_phases:
            best_safe_score = max(finite_phase_scores[p]["score"] for p in safe_phases if p in finite_phase_scores)
            finite_storage_action = max(
                (p for p in safe_phases if p in finite_phase_scores and finite_phase_scores[p]["score"] == best_safe_score),
                key=lambda p: finite_phase_scores[p]["score"],
            )
    selected_totals = finite_phase_scores.get(finite_storage_action, {}).get("component_totals", {})
    auditable_terms = ["downstream_storage", "spillback", "switching", "service", "incident"]
    if controller in DYNAMIC_V1_5_CONTROLLER_IDS:
        auditable_terms += ["storage_price", "cascade_price", "release", "service_age", "guardrail"]
    if controller in V1_6_CONTROLLER_IDS:
        auditable_terms += ["storage_price", "cascade_price", "release", "service_age", "guardrail", "completion_price"]
    changing_terms = sorted(
        field for field in auditable_terms if abs(float(selected_totals.get(field, 0.0))) > 1e-9
    )
    if finite_storage_action != pressure_action:
        pressure_totals = finite_phase_scores.get(pressure_action, {}).get("component_totals", {})
        changing_terms = sorted(
            field
            for field in auditable_terms
            if abs(float(selected_totals.get(field, 0.0))) > 1e-9 or abs(float(pressure_totals.get(field, 0.0))) > 1e-9
        )
    audit = {
        "tls_id": tls_id,
        "controller": controller,
        "pressure_action": int(pressure_action),
        "finite_storage_action": int(finite_storage_action),
        "capacity_aware_action": int(capacity_action),
        "finite_storage_double_action": int(double_pressure_action),
        "selected_action": int(finite_storage_action),
        "pressure_phase_scores": {str(phase): score for phase, score in pressure_phase_scores.items()},
        "capacity_aware_phase_scores": {str(phase): score for phase, score in capacity_phase_scores.items()},
        "finite_storage_double_phase_scores": {str(phase): score for phase, score in double_pressure_phase_scores.items()},
        "completion_service_phase_scores": {str(phase): score for phase, score in completion_service_scores.items()},
        "route_completion_prediction_phase_scores": {str(phase): score for phase, score in route_completion_prediction_scores.items()},
        "route_horizon_completion_phase_scores": {str(phase): score for phase, score in route_horizon_completion_scores.items()},
        "route_horizon_completion_phase_details": {str(phase): detail for phase, detail in route_horizon_completion_decompositions.items()},
        "route_horizon_blended_phase_details": {str(phase): detail for phase, detail in route_horizon_blend_details.items()},
        "route_horizon_capped_phases": [int(phase) for phase in route_horizon_capped_phases],
        "route_demand_completion_phase_scores": {str(phase): score for phase, score in route_demand_completion_scores.items()},
        "phase_scores": {str(phase): audit for phase, audit in finite_phase_scores.items()},
        "selected_component_totals": selected_totals,
        "action_changed_relative_to_pressure": bool(finite_storage_action != pressure_action),
        "changing_terms": changing_terms,
        "double_safety_fallback_used": bool(safety_fallback_used),
        "terminal_completion_fallback_used": bool(terminal_fallback_used),
        "double_score_safety_filter_used": bool(double_score_filter_used),
        "multi_baseline_safety_filter_used": bool(multi_baseline_filter_used),
        "hold_only_safety_filter_used": bool(hold_only_filter_used),
        "max_hold_safety_filter_used": bool(max_hold_filter_used),
        "completion_risk_filter_used": bool(completion_risk_filter_used),
        "route_completion_prediction_filter_used": bool(route_completion_prediction_filter_used),
        "route_demand_completion_filter_used": bool(route_demand_completion_filter_used),
        "route_demand_double_score_veto_used": bool(route_demand_double_score_veto_used),
        "route_horizon_completion_filter_used": bool(route_horizon_completion_filter_used),
        "route_horizon_dominance_filter_used": bool(route_horizon_dominance_filter_used),
        "terminal_exit_protection_guard_used": bool(terminal_exit_protection_guard_used),
        "route_horizon_max_pressure_envelope_used": bool(route_horizon_max_pressure_envelope_used),
        "route_horizon_core_baseline_envelope_used": bool(route_horizon_core_baseline_envelope_used),
        "route_horizon_double_pressure_envelope_used": bool(route_horizon_double_pressure_envelope_used),
        "route_horizon_core_minimax_guard_used": bool(route_horizon_core_minimax_guard_used),
        "route_horizon_capacity_rescue_guard_used": bool(route_horizon_capacity_rescue_guard_used),
        "route_horizon_capacity_score_envelope_used": bool(route_horizon_capacity_score_envelope_used),
        "route_horizon_native_capacity_score_rescue_guard_used": bool(route_horizon_native_capacity_score_rescue_guard_used),
        "route_horizon_severe_double_guard_used": bool(route_horizon_severe_double_guard_used),
        "route_horizon_pressure_double_conflict_guard_used": bool(route_horizon_pressure_double_conflict_guard_used),
        "route_horizon_completion_conflict_guard_used": bool(route_horizon_completion_conflict_guard_used),
        "route_horizon_capacity_completion_conflict_guard_used": bool(route_horizon_capacity_completion_conflict_guard_used),
        "route_horizon_early_capacity_completion_conflict_guard_used": bool(route_horizon_early_capacity_completion_conflict_guard_used),
        "route_horizon_negative_total_completion_conflict_guard_used": bool(
            route_horizon_negative_total_completion_conflict_guard_used
        ),
        "route_horizon_low_total_consensus_completion_guard_used": bool(
            route_horizon_low_total_consensus_completion_guard_used
        ),
        "route_horizon_score_gap_consensus_guard_used": bool(route_horizon_score_gap_consensus_guard_used),
        "route_horizon_negative_total_raw_consensus_guard_used": bool(
            route_horizon_negative_total_raw_consensus_guard_used
        ),
        "route_horizon_core_consensus_guard_used": bool(route_horizon_core_consensus_guard_used),
        "route_horizon_raw_consensus_guard_used": bool(route_horizon_raw_consensus_guard_used),
        "post_completion_veto_double_conflict_guard_used": bool(post_completion_veto_double_conflict_guard_used),
        "route_horizon_pressure_safe_guard_used": bool(route_horizon_pressure_safe_guard_used),
        "route_horizon_tail_completion_rescue_used": bool(route_horizon_tail_completion_rescue_used),
        "completion_safety_veto_used": bool(completion_safety_veto_used),
    }
    if controller in DYNAMIC_V1_5_CONTROLLER_IDS:
        audit["dynamic_dual_snapshot"] = {
            edge: {field: float(value) for field, value in values.items()}
            for edge, values in sorted((dynamic_dual_state or {}).items())
        }
        audit["dynamic_params"] = {
            field: float(value) if isinstance(value, (int, float)) else str(value)
            for field, value in sorted(dynamic_v1_5_params_for_controller(controller).items())
        }
    if controller in V1_6_CONTROLLER_IDS:
        audit["dynamic_dual_snapshot"] = {
            edge: {field: float(value) for field, value in values.items()}
            for edge, values in sorted((dynamic_dual_state or {}).items())
        }
        audit["dynamic_params"] = {
            field: float(value) if isinstance(value, (int, float)) else str(value)
            for field, value in sorted(DYNAMIC_V1_6_PARAMS.items())
        }
    return audit


def phase_score(
    controller: str,
    phase_index: int,
    states: list[str],
    movements: list[tuple[str, str]],
    queues: dict[str, float],
    capacities: dict[str, float],
    seed: int = 0,
    vehicle_counts: dict[str, float] | None = None,
) -> float:
    if not states:
        return 0.0
    state = states[phase_index % len(states)]
    score = 0.0
    for move_idx, movement in enumerate(movements):
        signal = state[move_idx] if move_idx < len(state) else "r"
        if signal in "Gg":
            score += movement_score(controller, movement, queues, capacities, seed, vehicle_counts=vehicle_counts)
    return score


def choose_controller_action(
    controller: str,
    tls_id: str,
    current_phase: int,
    step: int,
    action_interval: int,
    phase_states: dict[str, list[str]],
    tls_movements: dict[str, list[tuple[str, str]]],
    queues: dict[str, float],
    capacities: dict[str, float],
    seed: int = 0,
    vehicle_counts: dict[str, float] | None = None,
    dynamic_dual_state: dict[str, dict[str, float]] | None = None,
) -> int:
    if controller not in CONTROLLER_REGISTRY:
        raise ValueError(f"Unknown controller: {controller}. Available: {sorted(CONTROLLER_REGISTRY)}")
    states = phase_states.get(tls_id, [])
    greens = green_phases(states)
    if controller == "fixed_time" or (controller == "actuated_local_pressure" and sum(queues.values()) < 1.0):
        return greens[(step // action_interval) % len(greens)]
    if controller == "cycle_pressure" and step - (step // (2 * action_interval)) * (2 * action_interval) < action_interval:
        return current_phase if current_phase in greens else greens[(step // action_interval) % len(greens)]
    if controller in FINITE_STORAGE_CONTROLLER_IDS:
        finite_storage_state = build_completed_finite_storage_state(
            queues,
            capacities,
            vehicle_counts=vehicle_counts,
            current_phase=current_phase,
            time_since_switch=float(action_interval),
        )
        audit = select_finite_storage_action_with_audit(
            tls_id,
            current_phase,
            phase_states,
            tls_movements,
            queues,
            capacities,
            finite_storage_state,
            seed,
            controller=controller,
            dynamic_dual_state=dynamic_dual_state,
        )
        return int(audit["selected_action"])
    scored = [
        (
            phase_score(
                controller,
                phase_idx,
                states,
                tls_movements.get(tls_id, []),
                queues,
                capacities,
                seed,
                vehicle_counts=vehicle_counts,
            ),
            -phase_idx,
            phase_idx,
        )
        for phase_idx in greens
    ]
    return max(scored)[2] if scored else current_phase


def aggregate_metrics(
    observations: list[dict[str, float]],
    steps: int,
    warmup: int,
    departed: dict[str, float],
    arrived_times: list[float],
    waiting_delay: float,
    runtime: float,
    switching_count: int,
) -> dict[str, Any]:
    queues = [obs["total_queue"] for obs in observations]
    max_queues = [obs["max_queue"] for obs in observations]
    completed = len(arrived_times)
    unfinished = len(departed)
    departed_total = completed + unfinished
    horizon = max(steps - warmup, 1)
    total_travel_time = sum(arrived_times)
    censor_penalty = float(horizon)
    spillback_count = int(sum(obs["spillback"] for obs in observations))
    blocking_count = int(sum(obs["blocking"] for obs in observations))
    penalized_total = total_travel_time + unfinished * censor_penalty
    metrics = {
        "avg_travel_time": float(total_travel_time / completed) if completed else 0.0,
        "penalized_avg_travel_time": float(penalized_total / departed_total) if departed_total else 0.0,
        "total_delay": float(waiting_delay),
        "completed_vehicles": int(completed),
        "completion_rate": float(completed / departed_total) if departed_total else 0.0,
        "throughput": float(completed / horizon),
        "mean_queue": float(statistics.fmean(queues) if queues else 0.0),
        "max_queue": float(max(max_queues, default=0.0)),
        "spillback_count": spillback_count,
        "blocking_count": blocking_count,
        "switching_count": int(switching_count),
        "controller_runtime_sec": float(runtime),
        "travel_time_source": "conditional_on_arrival_with_censoring_penalty",
        "unfinished_vehicle_count": int(unfinished),
    }
    metrics["objective_components"] = build_objective_components_from_metrics(
        {
            "total_delay": metrics["total_delay"],
            "unfinished_vehicle_count": metrics["unfinished_vehicle_count"],
            "spillback_count": spillback_count,
            "blocking_count": blocking_count,
            "switching_count": switching_count,
        },
        horizon=float(horizon),
    )
    return metrics


def unavailable_finite_storage_state(reason: str) -> dict[str, Any]:
    state = {
        "downstream_storage": {"unavailable": 0.0},
        "residual_receiving_capacity": {"unavailable": 0.0},
        "spillback_blocking": {
            "unavailable": {"spillback": False, "blocking": False, "occupancy_ratio": 0.0}
        },
        "switching_loss_state": {"current_phase": None, "time_since_switch": 0.0, "status_reason": reason},
        "service_urgency": {"unavailable": 0.0},
        "incident_capacity_drop": {"active": False, "edge": None, "factor": 1.0, "status_reason": reason},
    }
    validate_finite_storage_state(state)
    return state


def build_completed_finite_storage_state(
    queues: dict[str, float],
    capacities: dict[str, float],
    *,
    vehicle_counts: dict[str, float] | None = None,
    current_phase: int | None,
    time_since_switch: float,
    incident_edge: str | None = None,
    capacity_drop_factor: float | None = None,
) -> dict[str, Any]:
    state = build_finite_storage_state(
        queues,
        capacities,
        vehicle_counts=vehicle_counts,
        current_phase=current_phase,
        time_since_switch=time_since_switch,
        incident_edge=incident_edge,
        capacity_drop_factor=capacity_drop_factor,
    )
    validate_finite_storage_state(state)
    return state


def validate_closed_loop_row(row: dict[str, Any]) -> None:
    validate_finite_storage_state(row["finite_storage_state"])
    validate_state_objective_sample(row)
    if row.get("controller") in FINITE_STORAGE_CONTROLLER_IDS and row.get("scenario_status") == "completed":
        action_decomposition = row.get("action_decomposition")
        if not isinstance(action_decomposition, dict):
            raise ValueError(f"{row.get('controller')} completed row requires action_decomposition")
        decisions = action_decomposition.get("last_decision_by_tls")
        if not isinstance(decisions, dict) or not decisions:
            raise ValueError(f"{row.get('controller')} action_decomposition requires nonempty last_decision_by_tls")


def infeasible_row(
    network: str,
    controller: str,
    seed: int,
    steps: int,
    warmup: int,
    action_interval: int,
    route_metadata: dict[str, str],
    scenario_tag: str,
    reason: str,
) -> dict[str, Any]:
    row = {
        "network": network,
        "scenario_tag": scenario_tag,
        "controller": controller,
        "seed": int(seed),
        "steps": int(steps),
        "warmup": int(warmup),
        "action_interval": int(action_interval),
        "scenario_status": "not_feasible",
        "feasibility_status": "not_feasible",
        "unsupported_reason": reason,
        **route_metadata,
        **{field: 0.0 for field in METRIC_FIELDS},
        "completed_vehicles": 0,
        "completion_rate": 0.0,
        "spillback_count": 0,
        "blocking_count": 0,
        "switching_count": 0,
        "travel_time_source": "not_feasible",
        "unfinished_vehicle_count": 0,
        "objective_components": {field: 0.0 for field in OBJECTIVE_COMPONENT_FIELDS},
        "finite_storage_state": unavailable_finite_storage_state(reason),
    }
    validate_closed_loop_row(row)
    return row


def edge_observation(edge_ids: list[str], capacities: dict[str, float]) -> dict[str, float]:
    queues = {edge_id: float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids}
    vehicles = {edge_id: float(traci.edge.getLastStepVehicleNumber(edge_id)) for edge_id in edge_ids}
    spillback = 0
    blocking = 0
    for edge_id, count in vehicles.items():
        cap = max(float(capacities.get(edge_id, 1.0)), 1.0)
        if count / cap >= 0.85:
            spillback += 1
            if queues.get(edge_id, 0.0) > 0.0:
                blocking += 1
    return {
        "total_queue": float(sum(queues.values())),
        "max_queue": float(max(queues.values(), default=0.0)),
        "active_vehicles": float(sum(vehicles.values())),
        "spillback": float(spillback),
        "blocking": float(blocking),
    }


def demand_shift_tick(step: int, warmup: int, route_ids: list[str], inserted: set[str]) -> str | None:
    if step < warmup or not route_ids or (step - warmup) % 30 != 0:
        return None
    veh_id = f"phase4_shift_{step}"
    if veh_id in inserted:
        return None
    traci.vehicle.add(veh_id, route_ids[(step // 30) % len(route_ids)], depart=str(max(step + 1, 1)))
    inserted.add(veh_id)
    return "traci_vehicle_insertion"


def select_failure_edge(edge_ids: list[str], tls_movements: dict[str, list[tuple[str, str]]]) -> str | None:
    incoming_counts: dict[str, int] = {}
    for movements in tls_movements.values():
        for upstream, _downstream in movements:
            if upstream in edge_ids:
                incoming_counts[upstream] = incoming_counts.get(upstream, 0) + 1
    if incoming_counts:
        return max(sorted(incoming_counts), key=lambda edge: incoming_counts[edge])
    return edge_ids[0] if edge_ids else None


def apply_failure_mode(step: int, warmup: int, target_edge: str | None, original_speed: float | None) -> str | None:
    if target_edge is None or original_speed is None:
        return None
    if warmup <= step < warmup + 120:
        traci.edge.setMaxSpeed(target_edge, max(original_speed * 0.35, 1.0))
        return "edge_speed_reduction"
    if step == warmup + 120:
        traci.edge.setMaxSpeed(target_edge, original_speed)
    return None


def scenario_stress_metadata(scenario_tag: str) -> dict[str, Any]:
    mapping = {
        "arterial_v1_5_storage_activation": ("v1_5_storage_activation", "diagnostic_effective_storage_capacity_scale"),
        "arterial_downstream_blockage": ("downstream_blockage", "edge_speed_reduction"),
        "arterial_spillback_stress": ("spillback", "finite_storage_occupancy_stress"),
        "arterial_incident_capacity_drop": ("incident_capacity_drop", "edge_speed_reduction"),
        "arterial_oversaturation": ("oversaturation", "short_horizon_demand_pressure"),
        "arterial_turning_shock": ("turning_shock", "traci_vehicle_insertion"),
        "arterial_switching_loss_sensitive": ("switching_loss_sensitive", "short_action_interval_switching_audit"),
        "arterial_demand_shift": ("turning_shock", "traci_vehicle_insertion"),
        "arterial_bottleneck_failure_mode": ("incident_capacity_drop", "edge_speed_reduction"),
    }
    if scenario_tag not in mapping:
        return {}
    category, mechanism = mapping[scenario_tag]
    return {"stress_category": category, "stress_mechanism": mechanism}


def scenario_effective_capacity_scale(scenario_tag: str) -> float:
    if "v1_5_storage_activation" in scenario_tag:
        return 0.10
    return 1.0


def run_experiment(
    network: str,
    controller: str,
    seed: int,
    steps: int,
    warmup: int,
    action_interval: int,
    route_metadata: dict[str, str],
    scenario_tag: str = "single_sanity",
    sumocfg_override: str | Path | None = None,
    collect_decision_trace: bool = False,
) -> dict[str, Any]:
    if controller not in CONTROLLER_REGISTRY:
        raise ValueError(f"Unknown controller: {controller}. Available: {sorted(CONTROLLER_REGISTRY)}")
    if controller in NOT_FEASIBLE_CONTROLLERS:
        return infeasible_row(network, controller, seed, steps, warmup, action_interval, route_metadata, scenario_tag, NOT_FEASIBLE_CONTROLLERS[controller])

    paths = resolve_network(network)
    sumocfg_path = Path(sumocfg_override) if sumocfg_override is not None else paths["sumocfg"]
    if not sumocfg_path.exists():
        raise FileNotFoundError(sumocfg_path)
    metadata = build_network_metadata(paths["net_file"])
    capacities = {str(k): float(v) for k, v in metadata["edge_capacity"].items()}
    effective_capacity_scale = scenario_effective_capacity_scale(scenario_tag)
    if effective_capacity_scale != 1.0:
        capacities = {edge: max(value * effective_capacity_scale, 1.0) for edge, value in capacities.items()}
    tls_movements = read_tls_link_movements(paths["net_file"])
    phase_states = read_tls_phase_states(paths["net_file"])
    edge_ids = sorted(capacities)
    downstream_adjacency = build_downstream_adjacency(tls_movements)
    dynamic_dual_state = initialize_dynamic_dual_state(edge_ids)
    edge_speeds = read_edge_speeds(paths["net_file"])
    edge_free_flow_times = read_edge_free_flow_times(paths["net_file"])
    target_edge = select_failure_edge(edge_ids, tls_movements)
    stress_metadata = scenario_stress_metadata(scenario_tag)
    cmd = ["sumo", "-c", str(sumocfg_path), "--seed", str(seed), "--no-step-log", "true", "--duration-log.disable", "true"]
    traci.start(cmd)
    observations: list[dict[str, float]] = []
    departed: dict[str, float] = {}
    arrived_times: list[float] = []
    latest_queues = {edge_id: 0.0 for edge_id in edge_ids}
    latest_vehicle_counts = {edge_id: 0.0 for edge_id in edge_ids}
    latest_current_phase: int | None = None
    latest_time_since_switch = 0.0
    switching_count = 0
    controller_runtime = 0.0
    last_phase_by_tls: dict[str, int] = {}
    target_phase_by_tls: dict[str, int] = {}
    phase_since_by_tls: dict[str, int] = {}
    waiting_delay = 0.0
    demand_shift_mechanism = None
    failure_mode_mechanism = None
    failure_mode_active = False
    inserted: set[str] = set()
    failure_target_max_vehicles = 0.0
    latest_action_decomposition_by_tls: dict[str, Any] = {}
    action_decision_summary = init_action_decision_summary(controller)
    decision_trace: list[dict[str, Any]] = []
    try:
        route_ids = list(traci.route.getIDList())
        original_speed = float(edge_speeds.get(target_edge, 13.89)) if target_edge else None
        for step in range(steps):
            if any(token in scenario_tag for token in ["bottleneck", "failure_mode", "downstream_blockage", "incident_capacity_drop", "spillback_stress"]):
                mechanism = apply_failure_mode(step, warmup, target_edge, original_speed)
                failure_mode_active = warmup <= step < warmup + 120 and target_edge is not None
                if mechanism:
                    failure_mode_mechanism = mechanism
            if any(token in scenario_tag for token in ["demand_shift", "turning_shock", "oversaturation"]):
                mechanism = demand_shift_tick(step, warmup, route_ids, inserted)
                if mechanism:
                    demand_shift_mechanism = mechanism
            if "switching_loss_sensitive" in scenario_tag:
                failure_mode_mechanism = None
            traci.simulationStep()
            if target_edge:
                failure_target_max_vehicles = max(failure_target_max_vehicles, float(traci.edge.getLastStepVehicleNumber(target_edge)))
            sim_time = float(traci.simulation.getTime())
            for veh_id in traci.simulation.getDepartedIDList():
                departed.setdefault(str(veh_id), sim_time)
            for veh_id in traci.simulation.getArrivedIDList():
                start = departed.pop(str(veh_id), None)
                if start is not None:
                    arrived_times.append(max(sim_time - start, 0.0))
            queues = {edge_id: float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids}
            vehicle_counts = {edge_id: float(traci.edge.getLastStepVehicleNumber(edge_id)) for edge_id in edge_ids}
            latest_queues = queues
            latest_vehicle_counts = vehicle_counts
            if step >= warmup and (step - warmup) % action_interval == 0:
                start = time.perf_counter()
                if controller in DYNAMIC_V1_5_CONTROLLER_IDS:
                    interval_state = build_completed_finite_storage_state(
                        queues,
                        capacities,
                        vehicle_counts=vehicle_counts,
                        current_phase=None,
                        time_since_switch=float(action_interval),
                        incident_edge=target_edge if failure_mode_active else None,
                        capacity_drop_factor=0.35 if failure_mode_active else None,
                    )
                    update_dynamic_dual_state(
                        dynamic_dual_state,
                        interval_state,
                        downstream_adjacency,
                        params=dynamic_v1_5_params_for_controller(controller) if controller in DYNAMIC_V1_5_CONTROLLER_IDS else DYNAMIC_V1_6_PARAMS,
                    )
                    if controller in V1_6_CONTROLLER_IDS:
                        update_completion_dual_state(
                            dynamic_dual_state,
                            interval_state,
                            step=step,
                            warmup=warmup,
                            steps=steps,
                            params=DYNAMIC_V1_6_PARAMS,
                        )
                route_completion_state = (
                    build_active_route_completion_state(
                        edge_ids,
                        edge_free_flow_times=edge_free_flow_times,
                        remaining_time=max(float(steps - step), 0.0),
                    )
                    if controller in DYNAMIC_V1_5_CONTROLLER_IDS
                    else unavailable_route_completion_state()
                )
                for tls_id in sorted(tls_movements):
                    current_phase = int(traci.trafficlight.getPhase(tls_id))
                    latest_current_phase = current_phase
                    previous_phase = last_phase_by_tls.get(tls_id)
                    if previous_phase is None:
                        last_phase_by_tls[tls_id] = current_phase
                        phase_since_by_tls[tls_id] = step - action_interval
                    elif previous_phase != current_phase:
                        phase_since_by_tls[tls_id] = step
                        last_phase_by_tls[tls_id] = current_phase
                        if target_phase_by_tls.get(tls_id) == current_phase:
                            switching_count += 1
                    latest_time_since_switch = float(step - phase_since_by_tls.get(tls_id, step - action_interval))
                    if controller in FINITE_STORAGE_CONTROLLER_IDS:
                        decision_state = build_completed_finite_storage_state(
                            queues,
                            capacities,
                            vehicle_counts=vehicle_counts,
                            current_phase=current_phase,
                            time_since_switch=latest_time_since_switch,
                            incident_edge=target_edge if failure_mode_active else None,
                            capacity_drop_factor=0.35 if failure_mode_active else None,
                        )
                        audit = select_finite_storage_action_with_audit(
                            tls_id,
                            current_phase,
                            phase_states,
                            tls_movements,
                            queues,
                            capacities,
                            decision_state,
                            seed,
                            controller=controller,
                            dynamic_dual_state=dynamic_dual_state if controller in DYNAMIC_V1_5_CONTROLLER_IDS else None,
                            route_completion_state=route_completion_state,
                            step=step,
                            warmup=warmup,
                            steps=steps,
                        )
                        latest_action_decomposition_by_tls[tls_id] = audit
                        update_action_decision_summary(action_decision_summary, audit, decision_state)
                        if collect_decision_trace:
                            storage = state_storage_summary(decision_state)
                            route_horizon_details = audit.get("route_horizon_completion_phase_details", {})
                            route_horizon_scores = audit.get("route_horizon_completion_phase_scores", {})
                            route_horizon_blends = audit.get("route_horizon_blended_phase_details", {})
                            route_horizon_capped_phases = list(audit.get("route_horizon_capped_phases", []))
                            decision_trace.append(
                                {
                                    "step": int(step),
                                    "tls_id": str(tls_id),
                                    "current_phase": int(current_phase),
                                    "selected_action": int(audit["selected_action"]),
                                    "pressure_action": int(audit["pressure_action"]),
                                    "capacity_aware_action": int(audit["capacity_aware_action"]),
                                    "finite_storage_double_action": int(audit["finite_storage_double_action"]),
                                    "action_changed_relative_to_pressure": bool(audit.get("action_changed_relative_to_pressure")),
                                    "route_horizon_completion_filter_used": bool(audit.get("route_horizon_completion_filter_used")),
                                    "route_horizon_pressure_safe_guard_used": bool(audit.get("route_horizon_pressure_safe_guard_used")),
                                    "route_horizon_severe_double_guard_used": bool(audit.get("route_horizon_severe_double_guard_used")),
                                    "route_horizon_completion_conflict_guard_used": bool(audit.get("route_horizon_completion_conflict_guard_used")),
                                    "route_horizon_capacity_completion_conflict_guard_used": bool(audit.get("route_horizon_capacity_completion_conflict_guard_used")),
                                    "route_horizon_early_capacity_completion_conflict_guard_used": bool(audit.get("route_horizon_early_capacity_completion_conflict_guard_used")),
                                    "route_horizon_native_capacity_score_rescue_guard_used": bool(audit.get("route_horizon_native_capacity_score_rescue_guard_used")),
                                    "route_horizon_low_total_consensus_completion_guard_used": bool(audit.get("route_horizon_low_total_consensus_completion_guard_used")),
                                    "route_horizon_core_consensus_guard_used": bool(audit.get("route_horizon_core_consensus_guard_used")),
                                    "route_horizon_raw_consensus_guard_used": bool(audit.get("route_horizon_raw_consensus_guard_used")),
                                    "post_completion_veto_double_conflict_guard_used": bool(audit.get("post_completion_veto_double_conflict_guard_used")),
                                    "completion_safety_veto_used": bool(audit.get("completion_safety_veto_used")),
                                    "completion_risk_filter_used": bool(audit.get("completion_risk_filter_used")),
                                    "max_occupancy_ratio": float(storage["max_occupancy_ratio"]),
                                    "min_residual_ratio": float(storage["min_residual_ratio"]),
                                    "selected_component_totals": dict(audit.get("selected_component_totals", {})),
                                    "selected_route_horizon_score": float(
                                        route_horizon_scores.get(str(audit.get("selected_action")), 0.0)
                                    ),
                                    "pressure_route_horizon_score": float(
                                        route_horizon_scores.get(str(audit.get("pressure_action")), 0.0)
                                    ),
                                    "capacity_route_horizon_score": float(
                                        route_horizon_scores.get(str(audit.get("capacity_aware_action")), 0.0)
                                    ),
                                    "double_route_horizon_score": float(
                                        route_horizon_scores.get(str(audit.get("finite_storage_double_action")), 0.0)
                                    ),
                                    "selected_route_horizon_blend": dict(
                                        route_horizon_blends.get(
                                            str(audit.get("selected_action")),
                                            {},
                                        )
                                    ),
                                    "pressure_route_horizon_blend": dict(
                                        route_horizon_blends.get(
                                            str(audit.get("pressure_action")),
                                            {},
                                        )
                                    ),
                                    "capacity_route_horizon_blend": dict(
                                        route_horizon_blends.get(
                                            str(audit.get("capacity_aware_action")),
                                            {},
                                        )
                                    ),
                                    "double_route_horizon_blend": dict(
                                        route_horizon_blends.get(
                                            str(audit.get("finite_storage_double_action")),
                                            {},
                                        )
                                    ),
                                    "route_horizon_capped_phases": route_horizon_capped_phases,
                                    "selected_route_horizon_details": dict(
                                        route_horizon_details.get(
                                            str(audit.get("selected_action")),
                                            {},
                                        )
                                    ),
                                    "pressure_route_horizon_details": dict(
                                        route_horizon_details.get(
                                            str(audit.get("pressure_action")),
                                            {},
                                        )
                                    ),
                                    "capacity_route_horizon_details": dict(
                                        route_horizon_details.get(
                                            str(audit.get("capacity_aware_action")),
                                            {},
                                        )
                                    ),
                                    "double_route_horizon_details": dict(
                                        route_horizon_details.get(
                                            str(audit.get("finite_storage_double_action")),
                                            {},
                                        )
                                    ),
                                }
                            )
                        action = int(audit["selected_action"])
                    else:
                        action = choose_controller_action(
                            controller,
                            tls_id,
                            current_phase,
                            step,
                            action_interval,
                            phase_states,
                            tls_movements,
                            queues,
                            capacities,
                            seed,
                            vehicle_counts=vehicle_counts,
                        )
                    target_phase_by_tls.setdefault(tls_id, current_phase)
                    states = phase_states.get(tls_id, [])
                    n_phases = max(len(states), 1)
                    current_state = states[current_phase] if current_phase < len(states) else ""
                    current_is_green = any(ch in "Gg" for ch in current_state)
                    phase_since = phase_since_by_tls.get(tls_id, step - action_interval)
                    if current_is_green and action != current_phase and step - phase_since >= action_interval:
                        target_phase_by_tls[tls_id] = int(action)
                    target = target_phase_by_tls.get(tls_id, current_phase)
                    if target != current_phase:
                        next_phase = (current_phase + 1) % n_phases
                        traci.trafficlight.setPhase(tls_id, int(next_phase))
                        phase_since_by_tls[tls_id] = step
                        if next_phase == target:
                            switching_count += 1
                            target_phase_by_tls[tls_id] = next_phase
                        last_phase_by_tls[tls_id] = int(next_phase)
                controller_runtime += time.perf_counter() - start
            if step >= warmup:
                waiting_delay += sum(float(traci.edge.getLastStepHaltingNumber(edge_id)) for edge_id in edge_ids)
                observations.append(edge_observation(edge_ids, capacities))
    finally:
        traci.close(False)

    row = {
        "network": network,
        "scenario_tag": scenario_tag,
        "controller": controller,
        "seed": int(seed),
        "steps": int(steps),
        "warmup": int(warmup),
        "action_interval": int(action_interval),
        "scenario_status": "completed",
        "feasibility_status": "run",
        "sumocfg": str(sumocfg_path),
        "base_sumocfg": str(paths["sumocfg"]),
        "net_file": str(paths["net_file"]),
        "effective_capacity_scale": float(effective_capacity_scale),
        **route_metadata,
        **aggregate_metrics(observations, steps, warmup, departed, arrived_times, waiting_delay, controller_runtime, switching_count),
        "finite_storage_state": build_completed_finite_storage_state(
            latest_queues,
            capacities,
            vehicle_counts=latest_vehicle_counts,
            current_phase=latest_current_phase,
            time_since_switch=latest_time_since_switch,
            incident_edge=target_edge if failure_mode_active else None,
            capacity_drop_factor=0.35 if failure_mode_active else None,
        ),
        **stress_metadata,
    }
    if controller in FINITE_STORAGE_CONTROLLER_IDS:
        row["action_decomposition"] = {
            "controller": controller,
            "decision_scope": "last_action_decision_per_tls",
            "last_decision_by_tls": latest_action_decomposition_by_tls,
            "decision_summary": finalize_action_decision_summary(action_decision_summary),
        }
        if collect_decision_trace:
            row["decision_trace"] = decision_trace
    if demand_shift_mechanism:
        row["demand_shift_mechanism"] = demand_shift_mechanism
        row["demand_shift_inserted_vehicles"] = len(inserted)
    if failure_mode_mechanism:
        row["failure_mode_mechanism"] = failure_mode_mechanism
        row["failure_mode_target_edge"] = target_edge
        row["failure_mode_target_max_vehicles"] = failure_target_max_vehicles
        row["failure_mode_start"] = warmup
        row["failure_mode_end"] = warmup + 120
    if row["completed_vehicles"] == 0:
        row["smoke_notes"] = "Short horizon produced no completed vehicles; queue/switch/runtime metrics remain valid."
    validate_closed_loop_row(row)
    return row


def build_payload(args: argparse.Namespace, route_metadata: dict[str, str], rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "experiment": "block4_closed_loop_sumo",
        **route_metadata,
        "claim_framing": CLAIM_FRAMING,
        "networks": [args.network],
        "controllers": list(args.controllers),
        "seeds": list(args.seeds),
        "scenario_tag": args.scenario_tag,
        "steps": args.steps,
        "warmup": args.warmup,
        "action_interval": args.action_interval,
        "scenario_results": rows,
        "metric_schema": {field: "CLOP-04 metric" for field in METRIC_FIELDS},
    }
    forbidden = forbidden_claim_hits(json.dumps({"claim_framing": payload["claim_framing"]}))
    if forbidden:
        raise ValueError(f"Output contains forbidden claim language: {forbidden}")
    return payload


def main() -> None:
    args = parse_args()
    validate_args(args)
    route_metadata = load_route_metadata(Path(args.route_json))
    rows = [
        run_experiment(args.network, controller, seed, args.steps, args.warmup, args.action_interval, route_metadata, args.scenario_tag)
        for seed in args.seeds
        for controller in args.controllers
    ]
    payload = build_payload(args, route_metadata, rows)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out_path), "rows": len(rows), "route_decision": payload["route_decision"]}, indent=2))


if __name__ == "__main__":
    main()
