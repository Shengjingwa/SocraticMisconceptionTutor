# 异常终止修复与柔性护栏拦截任务拆解 (Implementation Tasks)

## 任务列表

### 1. 修复模拟器异常终止 (Fix Simulator Abnormal Termination)
- [ ] 检查并修改 `src/simulator.py`。
- [ ] 为 `SimulatedStudent.generate_opening()` 中的 `self.llm.invoke` 添加 `@retry` 装饰器，参数与 `config.py` 中的 `RETRY_STOP_ATTEMPT`, `RETRY_MIN_WAIT`, `RETRY_MAX_WAIT` 保持一致。
- [ ] 为 `SimulatedStudent.reply()` 中的 `self.llm.invoke` 添加相同的 `@retry` 装饰器。
- [ ] 捕获所有底层的异常（如果达到最大重试次数），返回一条友好的 Mock 字符串，确保程序不会崩溃（可记录警告日志）。

### 2. 柔性护栏设计 (Soft Guardrail Interception)
- [ ] 检查并修改 `src/graph.py` 中的 `guardrail_node` 函数。
- [ ] 当 `guardrail_result["guardrail_triggered"]` 并且 `answer_leakage_flag` 为 True 时：
  - 复制当前的 `decision.meta`，增加 `guardrail_retries`。
  - 将 `guardrail_result["guardrail_reason"]` 注入到 `decision.meta["guardrail_feedback"]`。
  - 创建新的 `RouteDecision`，**保留**原有的 `state`, `state_name`, `strategy` 和 `next_goal`，设置 `need_guardrail=False`（不再强制转换到 `S2` 状态）。
  - 只有在 `retries >= 3` 的时候，才使用默认的 `S2` 兜底模板并返回 `regeneration_required: False`。

### 3. 生成器提示词与反馈集成 (Generator Prompt & Feedback Integration)
- [ ] 检查并修改 `src/generator.py` 中的 `generate_reply` 函数。
- [ ] 判断如果 `decision.meta` 中存在 `guardrail_feedback`：
  - 在传递给 LLM 的对话消息历史末尾，或者在 `SystemMessage` 之后，添加一条特殊的反馈提示，例如：`"注意：你之前的回答因为【{feedback}】被拦截。请重写回复，坚决避免直接给出答案或完成关键推理，并继续执行当前的教学策略：{strategy}"`。
- [ ] 修改硬拒绝逻辑：原来判断 `decision.need_guardrail` 或者 `decision.state == "S2"` 会直接使用模板。现在只有在 `decision.state == "S2"` 时才使用模板，使得柔性拦截能够执行到 LLM 的重新生成逻辑。

### 4. 日志记录与验证 (Logging & Verification)
- [ ] 运行 `python src/simulator.py` 进行局部测试，或者运行单元测试，确保异常不再抛出。
- [ ] 检查 `logs/session_summary.jsonl`，确认异常终止率为 0。
- [ ] 验证护栏触发后的重新生成是否更加自然，而不是直接回答“我不会直接给你标准答案”。
