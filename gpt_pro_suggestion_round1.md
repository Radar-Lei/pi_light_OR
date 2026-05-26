## 总体判断

我对当前 repo 的判断是：**研究工程化和 claim discipline 已经很强；但截至当前本地 v1.4 artifact，尚未达到 Transportation Science / Transportation Research Part B 所需的 closed-loop baseline-superiority 证据门槛。**

当前最稳、且已经能由仓库证据支撑的强 claim 是：

> **一个从有限容量交通网络松弛中导出的、可审计的 generalized-pressure / finite-storage primal-dual signal-control 框架；它在 slack 情况下恢复 pressure/backpressure 语义，在 binding/storage 情况下给出可解释的差异项，并用预注册、fail-closed 的 Gate C 机制约束任何未来 baseline-superiority claim。**

这个 claim 可以强，但强在**边界清楚、机制清楚、审计清楚**，不是强在“当前已经超过强 baselines”。README 已经把当前路线写成 pressure-equivalent generalized-pressure symbolic recovery，并明确说 Phase 3 发现 dual-sensitivity 和 pressure/backpressure 在 static kill gate 下打平，因此后续证据应解释为 generalized-pressure symbolic recovery，而不是 dual superiority。README 也把 max-pressure/backpressure 与 capacity-aware pressure 设为 first-class baselines，不是 strawmen。

本文件后续所有“超过 baselines / improves relative to baselines / closed-loop superiority”表述都必须按下面的状态机理解：

- **当前允许：** generalized-pressure recovery、finite-storage correction terms、locked protocol、fail-closed evaluation discipline、candidate selection / mechanism auditability。
- **当前不允许：** finite-storage primal-dual controller 已经超过 max-pressure、capacity-aware pressure、finite-storage double-pressure；dual sensitivity 广泛优于 pressure/backpressure；可部署真实世界性能优势。
- **只有在未来严格 Gate C artifact 为 `PASSED` 且 row audit 完整时才允许：** bounded closed-loop superiority relative to the named strong baselines in the locked finite-storage binding regimes。

本判断依据当前本地文件，而不是远端页面或提交描述：

- `README.md`
- `.planning/STATE.md`
- `experiments/dual_sensitivity/v1_4_summary.md`
- `experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json`
- `experiments/dual_sensitivity/v1_4_milestone_audit.md`
- `experiments/dual_sensitivity/v1_4_failure_diagnostics.md`
- `experiments/dual_sensitivity/v1_4_candidate_convergence.md`
- `experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json`

---

## 最新进度：v1.4 锁定了确认路线，但没有产生 baseline-superiority 证据

最关键的 v1.4 进展是：

1. **候选控制器已选定，但候选选择不是最终证据。** `v1_4_candidate_convergence.md` 显示候选收敛状态为 `PASSED`，protocol 为 `LOCKED`，选中的控制器是 `finite_storage_primal_dual_v1_4_score`。它的机制是修改 live controller score decomposition，同时保留可审计的 action components；改动项包括 `downstream_storage`、`spillback`、`switching`、`service`。这支持“机制路线已锁定”，不支持“已超过 baselines”。

2. **确认实验协议已经锁定。** `v1_4_locked_gate_c_protocol.json` 的状态是 `LOCKED`，选中控制器为 `finite_storage_primal_dual_v1_4_score`。比较对象包括 `max_pressure`、`capacity_aware_pressure`、`finite_storage_double_pressure`；binding scenarios 包括 downstream blockage、spillback stress、incident capacity drop、oversaturation、turning shock、switching-loss-sensitive；主指标包括 penalized travel time、delay、spillback、blocking、unfinished vehicles；demand multipliers 是 0.8、1.0、1.2。这支持“有强 baseline 的预注册确认设计”。

3. **最新 Gate C 证据仍是 `INCONCLUSIVE`。** `v1_4_summary.md` 直接显示：Package status = `INCONCLUSIVE`，Strict Gate C = `INCONCLUSIVE`，Closed-loop superiority claim allowed = `false`。

4. **当前 v1.4 确认证据为空，不是统计意义上的胜利。** `v1_4_gate_c_paired_evidence.json` 显示 main profile、3600 steps、900 warmup、dry_run=false，但 `actual_row_count=0`，`expected_row_count=1440`，`completed_row_count=0`，`all_rows_executed=false`。失败原因包括 “input artifact has no executed raw scenario rows”、“input artifact reports missing required executed rows”、“input artifact actual_row_count does not match expected_row_count”。

所以最准确的一句话是：

> **v1.4 已经把强 baseline-superiority claim 的考场和评分规则锁好了，但当前还没有交卷；因此不能写已经击败强 baselines。**

---

## 研究强项

### 1. 审稿友好型工程骨架已经很强

repo 结构成熟：`.planning` 记录 roadmap / milestone / review / verification；`scripts/` 提供实验、渲染、audit、table-generation 入口；`experiments/dual_sensitivity/` 存 raw JSON/CSV、reports、rules、manifests、paper-facing artifacts；`tests/` 覆盖 claim discipline、SUMO、finite storage schema、Phase 11/12、theory separation 等。

这对 Transportation Science / TRB 有利，因为它不是“跑了一些仿真图”，而是“有可复现实验合同、审计脚本、claim gate、artifact provenance”。

### 2. 研究问题有 OR / control / transportation methodology 味道

README 的研究问题是：movement-level dual sensitivities from a capacitated traffic-network relaxation 是否能作为 interpretable generalized-pressure principle，并被压缩成 auditable symbolic policies。这个问题本身适合 OR/control/transportation methodology，因为它把信号控制、有限容量约束、dual sensitivity、pressure principle 和 symbolic policy recovery 连在一起。

### 3. Baselines 不是 strawmen

当前 locked protocol 明确要求和 `max_pressure`、`capacity_aware_pressure`、`finite_storage_double_pressure` 比较，而不是只跟 fixed-time 或弱 baseline 比。这会提高可信度；但反过来，它也要求任何“超过 baselines”的 claim 必须真的由这些强 comparator 上的严格 Gate C 结果支撑。

### 4. Claim discipline 是亮点

Phase 12 summary 显示 claim audit status = `PASSED`，但 package status = `INCONCLUSIVE`；Phase 11 long-horizon paired-seed evidence = `FAILED`，Gate C = `INCONCLUSIVE`。这不是坏事。审稿时最怕 overclaim，而当前 repo 已经在机制上阻止 overclaim：`phase12_claim_audit.json` 和 `v1_4_claim_audit.json` 都把 claim discipline 单独审计；`.planning/STATE.md` 也明确写着 closed-loop superiority 必须等 strict v1.4 Gate C `PASSED` 才能允许。

---

## 当前最大短板

### 1. 现在不能投“dual beats pressure”的强 claim

README 明确写了 current route 是 pressure-equivalent，不显示 dual sensitivity 广泛压过 pressure；closed-loop SUMO evidence 也被限制为 local networks、finite horizons、fixed seed sets，不是可部署真实世界性能优势 claim。

`v1_4_failure_diagnostics.md` 也说明，Phase 11 source status 是 `FAILED`，Gate C 是 `INCONCLUSIVE`。已有诊断里 bounded-harm metric comparisons 有 48 个，non-worsening 只有 10 个，strict-positive signals 只有 4 个；finite-storage decisions 只在约 9.833% audited TLS decisions 中不同于 pressure。

这意味着：**如果论文 introduction 现在写 “dual-sensitivity controller outperforms pressure-based control”，会被当前 artifact 推翻。**

### 2. 当前 v1.4 confirmation evidence 是空的

v1.4 协议本身不错，但 `v1_4_gate_c_paired_evidence.json` 的 `actual_row_count=0 / expected_row_count=1440` 说明它还没有完成确认实验。当前不是“实验已经证明超过 baselines”，也不是“统计上没有赢”；当前状态是“关键确认实验尚未执行出可用行”。

### 3. 机制激活仍是风险点

`v1_4_failure_diagnostics.md` 里最致命的两点是 `controller_action_weakness high` 和 `insufficient_binding_activation medium`。如果 finite-storage controller 只有很少比例的 action 真正不同于 pressure，那么即使理论上有 storage/spillback 项，closed-loop 指标也很难显著变化。

这会直接影响 strong claim：不仅要说“公式不同”，还要证明“在 binding regimes 下，这些不同项足以改变动作，并且改变动作后改善系统指标”。当前 evidence 还没有证明这一链条。

---

## 下一步建议：先执行确认，不要提前写赢 baseline

### Step 1：先不要改模型，先把 locked Gate C 执行完整

这是当前最高优先级。不要在看到 v1.4 confirmation 结果前继续调 controller，否则容易进入 post-hoc tuning / p-hacking 的危险区。你已经有 locked protocol，下一步是按 locked protocol 执行 1440 行。

建议命令：

```bash
python scripts/run_v14_locked_gate_c.py \
  --protocol experiments/dual_sensitivity/v1_4_locked_gate_c_protocol.json \
  --out experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json \
  --progress-out experiments/dual_sensitivity/v1_4_locked_gate_c_execution.progress.json \
  --execution-row-limit 1440

python scripts/run_v14_gate_c_paired_evidence.py \
  --input experiments/dual_sensitivity/v1_4_locked_gate_c_execution.json \
  --out experiments/dual_sensitivity/v1_4_gate_c_paired_evidence.json \
  --strict
```

最终需要的是 row audit 中 `actual_row_count == expected_row_count == 1440`、`completed_row_count == 1440`、`all_rows_executed=true`，并且 strict evidence artifact 的 status 为 `PASSED`。在这些条件没有满足前，任何超过 baseline 的强 claim 都不能写成事实。

### Step 2：Gate C 之后按三种结果分叉

**如果 Gate C `PASSED`：**

可以写 baseline-superiority claim，但必须限定在 locked finite-storage binding regimes，不要写无边界 dominance。推荐主 claim 只能写成：

> We develop a finite-storage primal-dual generalized-pressure signal controller and, under a pre-registered paired-seed SUMO protocol, find evidence that it improves the locked primary finite-storage operational metrics relative to max-pressure, capacity-aware pressure, and finite-storage double-pressure baselines in the locked capacity-binding arterial regimes.

这句话的强度来自 **pre-registered、paired-seed、strong baselines、binding regimes、locked primary metrics**。它不能外推为“dual sensitivity 普遍优于 pressure”。

**如果 Gate C `INCONCLUSIVE`：**

不要投 closed-loop superiority。改成 theory/methodology paper：

> Dual sensitivities from a capacitated relaxation provide a constructive generalized-pressure representation: pressure is recovered in slack regimes, while finite-storage/binding regimes generate interpretable correction terms; the framework yields auditable symbolic controllers and a fail-closed evaluation protocol.

这个 claim 仍然可投，但文章重心应从“性能优越”改成“理论统一 + 可审计方法 + 负结果/边界发现”。

**如果 Gate C `FAILED`：**

不要把失败藏起来。把它当成诊断：说明 primal-dual finite-storage terms 在当前 live controller 中 action activation 不够，或者 objective 与 closed-loop performance mismatch。然后重新开 v1.5，但必须重新 lock protocol；v1.4 失败诊断已经把主要方向指向 controller action weakness、objective mismatch、binding activation、scenario sensitivity、baseline parity。

### Step 3：补一条机制链证据，不只是总指标

TS/TRB 审稿人会问：为什么 dual / finite-storage 项有用？paper 中应组织出完整链条：

1. **Theorem / proposition：** slack/infinite-storage 条件下，dual-sensitivity score 退化为 pressure/backpressure。
2. **Separation lemma：** downstream storage / spillback / blocking 约束 binding 时，dual term 与 pressure term 的 ranking 可以不同。
3. **Action activation table：** 在 locked scenarios 中，finite-storage controller 与 pressure 不同的 TLS decision 占比是多少。
4. **Mechanism-to-outcome table：** action difference 是否集中发生在 spillback/blocking 关键时刻。
5. **Outcome table：** paired-seed 下主指标是否改善。

只有第 5 项在 strict Gate C 里 `PASSED`，才能把“超过 baselines”写成结果；否则只能写成未来验证目标或诊断假设。

### Step 4：把 real-world / larger network 作为第二确认层

README 已经把下一步写成：扩展 explicit storage/supply/corridor fields、增加 longer horizons 和 larger real-world networks、把 CSV 图表转成 manuscript-ready figures。这个方向合理，但顺序上建议：

先完成 locked Gate C；如果 Gate C `PASSED`，再加 external validity layer。`networks/` 已有 `arterial`、`chengdu`、`grid_4x4`、`single_intersection`。如果要投 TS/TRB，Chengdu 或真实网络不应只是 appendix smoke test，而应成为 robustness / external validity 的核心证据之一。

最理想的实验层级：

- Layer 1：toy / static theory states，证明 separation。
- Layer 2：locked arterial binding scenarios，证明机制在受控环境下有效。
- Layer 3：grid / Chengdu / larger real network，证明不是只针对一个 arterial scenario 调出来的。
- Layer 4：ablation，去掉 downstream_storage、spillback、switching、service，证明每个项的贡献。

### Step 5：论文写作坚持“强但不越界”

**不要写：**

> Dual sensitivity outperforms max pressure for traffic signal control.

**当前可以写：**

> Finite-storage dual sensitivities provide a generalized-pressure principle that is equivalent to pressure in slack regimes and yields storage-aware corrections in binding regimes; the repository implements a locked, fail-closed paired-seed protocol for testing whether those corrections can outperform strong max-pressure-style baselines.

**只有 Gate C `PASSED` 后才可以写：**

> Under the locked paired-seed confirmation protocol, the resulting auditable controller improves the locked finite-storage arterial metrics relative to the named max-pressure-style baselines.

这两句话的区别很重要：第一句是当前已支撑的方法 claim；第二句是未来必须由 strict Gate C 支撑的结果 claim。

---

## 投稿定位

当前更稳的定位不是“已经证明 controller 击败 pressure baselines”，而是：

- **methodology/theory-first：** finite-storage generalized pressure from primal-dual network relaxation；
- **evaluation-discipline-first：** fail-closed paired-seed Gate C prevents baseline-superiority overclaim；
- **结果状态诚实：** current v1.4 strict Gate C is `INCONCLUSIVE` because 0/1440 locked rows are executed.

如果未来 Gate C `PASSED` 且补出 real/larger-network robustness，Transportation Science 的 match 会更好。TRB 也可以，但需要更强数学主线：capacitated relaxation -> dual sensitivity -> pressure recovery/separation -> controller；仿真应服务于理论机制，而不是成为文章唯一核心。

当前不建议以 closed-loop superiority 作为 TS/TRB 投稿主 claim。更稳的当前版本是 working paper / arXiv 风格的 generalized-pressure recovery and fail-closed evaluation framework；等 Gate C 真正 `PASSED` 后，再升级为 bounded baseline-superiority paper。

---

## 你现在最应该做的 7 件事

1. **执行 locked v1.4 Gate C 的 1440-row confirmation。** 当前最硬的 blocker 是 0/1440 executed rows，不是理论不够。

2. **把 Gate C 结果转成一张主表。** 行：六个 binding scenarios；列：三类 baselines、五个 primary metrics、paired CI、Holm-Bonferroni status、bounded harm / non-worsening / strict positive。

3. **加一张 action-decomposition 机制图。** 展示 pressure action、finite-storage action、selected action、component totals、movement decompositions；v1.4 selected candidate 已经把这个作为 audit surface。

4. **补 formal propositions。** 至少三个：pressure special case、binding separation、symbolic recovery fidelity / action equivalence。没有这些，TRB 会偏弱；有这些，TS 也更稳。

5. **补 external validity。** 用 `chengdu` 或更大网络做 robustness。它不能替代 locked Gate C，但可以在 Gate C 之后证明结果不是 handcrafted arterial stress scenario 的偶然现象。

6. **保留负结果，但放对位置。** Phase 11 failure / v1.4 diagnostics 可以变成“为什么我们需要 locked binding-regime confirmation”的动机，而不是论文的失败包袱。

7. **论文标题和摘要不要再以 PI-Light/RL 为中心。** 这个项目最有前途的方向不是 “interpretable RL for traffic signal control”，而是 **“finite-storage generalized pressure from primal-dual network relaxation”**。PI-Light 可以作为 predecessor context，而不是主贡献。

---

## 最终路线建议

**短期目标：执行并审计 v1.4 Gate C，而不是预设 v1.4 Gate C 必须 PASSED。**
没有 strict Gate C `PASSED`，不要写 closed-loop superiority。当前 repo 已经把裁判、考卷、评分标准准备好了；缺的是生成完整、可审计、非空的 locked confirmation evidence。

**中期目标：把 claim 从“dual sensitivity”升级为“finite-storage generalized pressure”。**
“Dual sensitivity”对审稿人可能抽象；“finite-storage generalized pressure”更容易和 max pressure/backpressure 文献对话，也更容易解释为什么 storage/spillback/bottleneck 下会有新项。

**投稿目标：先按 evidence 状态决定，不要反过来让投稿目标驱动 claim。**
Gate C 仍 `INCONCLUSIVE` 时，主 claim 应是 generalized-pressure recovery and fail-closed evaluation framework。Gate C `PASSED` 后，才考虑把 bounded baseline-superiority 升级成主 claim；如果还补出 larger-network robustness，再优先考虑 Transportation Science。
