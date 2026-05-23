---
phase: 06-claim-discipline-and-explicit-state-foundation
reviewed: 2026-05-23T00:00:00Z
depth: standard
files_reviewed: 14
files_reviewed_list:
  - scripts/audit_claim_discipline.py
  - scripts/claim_policy.py
  - scripts/finite_storage_schema.py
  - scripts/generate_static_regime_states.py
  - scripts/render_closed_loop_report.py
  - scripts/render_paper_artifacts.py
  - scripts/reproduce_blocks.py
  - scripts/run_closed_loop_suite.py
  - scripts/run_closed_loop_sumo.py
  - scripts/run_static_kill_gate.py
  - tests/test_claim_discipline.py
  - tests/test_closed_loop_sumo.py
  - tests/test_finite_storage_schema.py
  - tests/test_generate_static_regime_states.py
findings:
  critical: 5
  warning: 2
  info: 0
  total: 7
status: issues_found
---

# Phase 6: Code Review Report

**Reviewed:** 2026-05-23T00:00:00Z
**Depth:** standard
**Files Reviewed:** 14
**Status:** issues_found

## Summary

审查范围覆盖 Phase 6 claim discipline、显式 finite_storage_state/objective_components schema、fail-closed gate、metadata scan exclusions，以及闭环/复现实验脚本的回归风险。当前实现存在多处 fail-open 缺陷：缺失扫描路径默认不失败、Phase 6 顶层 schema_version 未强制样本显式字段、过度宽松的禁用 claim 上下文判断、复现 manifest 不校验 artifact status、paper artifact 只接受状态占位符。这些问题会让 claim discipline 或 paper artifact gate 在证据缺失/失败 artifact/过度 claim 情况下仍然通过。

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: Claim audit 默认忽略缺失路径，导致扫描范围为空也可通过

**Severity:** BLOCKER
**File:** `scripts/audit_claim_discipline.py:45-46,57-64,164-166`
**Issue:** `--allow-missing-paths` 默认值为 `True`，`iter_scan_files()` 在路径不存在时直接返回空列表且不记录 `missing_paths`。因此默认 `DEFAULT_CLAIM_SCAN_PATHS` 中的关键报告、paper artifact、manifest 缺失时，audit 仍可能生成 `PASSED`，违反 Phase 6 fail-closed claim discipline。
**Fix:** 默认 fail closed；只有显式传 `--allow-missing-paths` 才允许跳过，并在 audit 中记录 skipped 路径。

```python
parser.add_argument("--allow-missing-paths", action="store_true", default=False)
parser.add_argument("--no-allow-missing-paths", dest="allow_missing_paths", action="store_false")

if not path.exists():
    missing.append(rel_path)
    if allow_missing_paths:
        return [], missing
    return [], missing
```

并保持 `missing_paths` 非空时 `status = "FAILED"`。

### CR-02: Static kill gate 不根据顶层 `schema_version` 强制验证 Phase 6 样本

**Severity:** BLOCKER
**File:** `scripts/run_static_kill_gate.py:111-118,167-179`
**Issue:** `sample_requires_explicit_phase6_validation()` 只检查单个 sample 内的 `schema_version` 或显式字段；但 `generate_static_regime_states.py` 将 `schema_version` 写在 payload 顶层。若一个 Phase 6 artifact 顶层声明 `phase6_explicit_state_v1`，但样本缺少 `finite_storage_state` / `objective_components`，当前 loader 会按 legacy 样本放行，破坏 STATE-01/STATE-02 的 fail-closed 约束。
**Fix:** 在读取文件时计算 artifact 级别的 Phase 6 标志，并传入 sample validation。

```python
artifact_schema_version = str(data.get("schema_version", ""))
force_explicit_phase6 = artifact_schema_version.startswith("phase6") or artifact_schema_version == SCHEMA_VERSION
...
validate_sample_schema(sample, path, sample_idx, force_explicit_phase6=force_explicit_phase6)
```

`validate_sample_schema()` 应在 `force_explicit_phase6` 为真时无条件调用 `validate_state_objective_sample()`。

### CR-03: Forbidden-claim negation heuristic 可被无关前文绕过

**Severity:** BLOCKER
**File:** `scripts/claim_policy.py:102-119,122-128`
**Issue:** `is_negated_or_bounded_context()` 在 phrase 前 240 个字符内只要出现任意 `not `、`no `、`without ` 等 marker，就会认为禁用 claim 被否定。无关句子如 “This is not a toy example. The method proves superiority.” 会让 `proves superiority` 不被报告，形成 claim audit 绕过。
**Fix:** 只允许紧邻 phrase 的限定/否定模式，或使用句子边界截断上下文。

```python
prefix = lowered[max(0, index - 40):index]
allowed_prefixes = (
    "does not ", "do not ", "must not ", "cannot ", "without evidence to ",
)
return any(prefix.rstrip().endswith(marker.rstrip()) for marker in allowed_prefixes)
```

并增加覆盖测试：前一句含 `not`、后一句含 `proves superiority` 必须失败。

### CR-04: Reproducibility audit 不校验 JSON artifact 的 `status`

**Severity:** BLOCKER
**File:** `scripts/reproduce_blocks.py:238-286`
**Issue:** `audit_artifacts()` 的 `expected_ok` 只要求预期 artifact 存在且可解析；`audit_file()` 虽读取 JSON 的 `status`，但不会要求预期 artifact 的 `status == "PASSED"`。因此 `phase6_claim_audit.json`、closed-loop suite、paper artifact manifest 等即使是 `FAILED`，复现 manifest 仍可为 `PASSED`。
**Fix:** 对 expected JSON artifact 增加状态门槛；没有 status 的 artifact 需列入允许清单，否则 fail closed。

```python
def artifact_passed(check: dict[str, Any]) -> bool:
    if not (check["exists"] and check.get("parse_status") == "ok"):
        return False
    if check["path"].endswith(".json"):
        return check.get("status") == "PASSED"
    return True

expected_ok = all(artifact_passed(check) for check in checks if check.get("expected"))
```

### CR-05: Paper artifact renderer 接受 status-only 的 Phase 6 guard 占位符

**Severity:** BLOCKER
**File:** `scripts/render_paper_artifacts.py:76-87`
**Issue:** `validate_inputs()` 对 Phase 6 guard artifact 只验证 `status == "PASSED"` 和 `experiment` 字段。一个缺少 `requirements_covered`、`forbidden_hits`、schema fields、fixtures samples 的占位 JSON 也会通过，导致 paper-facing tables/figures 可以在没有实际 claim audit 和显式 schema 证据的情况下生成。
**Fix:** 对每类 guard 做结构化校验。

```python
claim_audit = inputs["phase6_claim_audit"]
if claim_audit.get("requirements_covered") != ["CLAIM-01", "CLAIM-02"]:
    raise ValueError("phase6_claim_audit requirements mismatch")
if claim_audit.get("forbidden_hits"):
    raise ValueError("phase6_claim_audit contains forbidden hits")

schema = inputs["phase6_explicit_state_schema"]
if not {"downstream_storage", "residual_receiving_capacity"} <= set(schema.get("finite_storage_state_fields", [])):
    raise ValueError("phase6 schema artifact is incomplete")
```

同时应校验 `phase6_state_objective_fixtures.samples` 非空且每个 sample 含 `finite_storage_state` 和 `objective_components`。

## Warnings

### WR-01: Numeric schema validation accepts booleans and negative objective penalties

**Severity:** WARNING
**File:** `scripts/finite_storage_schema.py:44-47,144-153,224-253`
**Issue:** `_require_finite_number()` 使用 `isinstance(value, (int, float))`，Python 中 `bool` 是 `int` 的子类，因此 `True`/`False` 会被当作 1.0/0.0 接受。`validate_objective_components()` 也只要求 finite，不拒绝负的 delay、unfinished penalty、spillback time、switching lost time。显式 objective schema 会接受物理上无效的 objective artifact。
**Fix:** 数值字段默认拒绝 bool，并对 objective components 增加非负校验。

```python
if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
    raise ValueError(...)
...
component = _require_finite_number(...)
if component < 0.0:
    raise ValueError(f"{field} must be nonnegative")
```

### WR-02: `tests/test_closed_loop_sumo.py` 的手动入口写入未创建的 `/tmp` 子目录

**Severity:** WARNING
**File:** `tests/test_closed_loop_sumo.py:412-414,467-468`
**Issue:** `main()` 直接调用 `test_repro_audit_ignores_policy_metadata_for_forbidden_phrase_scan(Path("/tmp/test_repro_audit_metadata"))`，但该测试内部没有创建目录就执行 `artifact.write_text(...)`。以脚本方式运行该测试文件会因 `FileNotFoundError` 中断，降低回归测试可靠性。
**Fix:** 在测试内部创建目录，或在 `main()` 中使用 `TemporaryDirectory()`。

```python
def test_repro_audit_ignores_policy_metadata_for_forbidden_phrase_scan(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    artifact = tmp_path / "phase6_claim_policy.json"
    ...
```

---

_Reviewed: 2026-05-23T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
