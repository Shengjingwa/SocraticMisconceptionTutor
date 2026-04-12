# 异常终止修复与柔性护栏拦截检查清单 (Checklist)

## 验证点

### 1. 稳定性验证 (Stability Verification)
- [ ] **SimulatedStudent 重试机制**：
  - 检查 `simulator.py` 中 `SimulatedStudent.generate_opening()` 和 `reply()` 是否添加了 `@retry`。
  - 检查 `simulator.py` 中 `SimulatedStudent.generate_opening()` 和 `reply()` 是否捕获了 `Exception`，并在抛出后返回 Mock 响应以防止程序崩溃。
  - 确认仿真测试运行时不再出现由于网络异常导致的 `termination_reason: "error"`。

### 2. 柔性护栏验证 (Soft Guardrail Verification)
- [ ] **拦截反馈传递**：
  - 检查 `graph.py` 中的 `guardrail_node` 是否在 `guardrail_triggered=True` 时不再强制转换状态为 `S2`。
  - 检查 `guardrail_result["guardrail_reason"]` 是否被正确注入到 `decision.meta["guardrail_feedback"]`。
- [ ] **LLM 重新生成**：
  - 检查 `generator.py` 中的 `generate_reply` 是否正确读取了 `decision.meta["guardrail_feedback"]`。
  - 检查提示词（Prompt）中是否正确附加了反馈要求，并且 `need_guardrail` 逻辑被更新，使得 LLM 可以自然地重写回复。
- [ ] **重试上限限制**：
  - 检查 `graph.py` 中是否在 `retries >= 3` 时触发兜底机制，返回安全的模板回复，并停止无限循环。

### 3. 系统测试与日志覆盖
- [ ] 运行 `python src/simulator.py`（至少完成一个有护栏触发的会话）。
- [ ] 检查 `turn_logs.jsonl`，验证 `guardrail_triggered` 和 `answer_leakage_flag` 被触发时，是否发生了同状态下的重试生成，且重写后的回复更符合当前状态的目标策略。
- [ ] 检查 `session_summary.jsonl` 中的 `abnormal_end_flag` 或 `termination_reason` 确保为正常结束。
