# 异常终止修复与柔性护栏拦截 (Improve Stability and Soft Guardrail)

## 1. 目标与背景

当前系统的 `FSM+Guardrail` 版本在评估中暴露了两个主要问题：
1. **异常终止率过高 (7.14%)**：部分会话在未完成交互时直接因 `error` 终止。排查发现，这是由于仿真环境 `simulator.py` 中的 `SimulatedStudent` 调用 LLM 时缺乏网络异常和限速的重试机制，导致请求失败并抛出异常，进而中断了整个会话。
2. **护栏拦截生硬 (模板硬拒绝)**：当 `guardrail_node` 拦截到助教回答泄露答案时，系统会强制将状态切换为 `S2 (Refusal_And_Guidance)` 并触发硬编码的模板回复（如：“我不会直接给你标准答案...”）。这种生硬的拒绝打破了对话的连贯性，导致“柔性引导”失败。

本规格说明书旨在修复上述稳定性问题，并将护栏拦截升级为基于 LLM 动态生成的“柔性护栏”。

## 2. 异常终止修复 (Stability Fix)

### 2.1 问题根因
`simulator.py` 中的 `SimulatedStudent` 类在 `generate_opening()` 和 `reply()` 方法中直接调用了 `self.llm.invoke()`。当遇到 OpenAI/DeepSeek API 的临时网络错误、Rate Limit 时，调用会抛出异常。外层的 `try-except` 捕获后直接调用 `app.end_session("error")`，导致异常终止。

### 2.2 解决方案
- 在 `src/simulator.py` 中引入 `tenacity` 重试机制。
- 对 `student.generate_opening()` 和 `student.reply()` 的 LLM 调用包裹 `@retry(stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT), wait=wait_exponential(...))`。
- 当达到最大重试次数后，如果依然失败，则返回一个 fallback 的 mock 回复以维持对话继续，而不是直接崩溃（或者让其在日志中明确记录为 API 失败，但至少降低临时波动的报错率）。

## 3. 柔性护栏拦截设计 (Soft Guardrail Design)

### 3.1 核心思路
将“硬模板拒绝”改为“带反馈的 LLM 重新生成（Reflection & Self-Correction）”。当判别器（Judge）发现生成的回复泄漏答案时，将判别器的具体理由（Reason）作为反馈传回给生成器（Generator），要求生成器在不改变当前教学策略和状态的前提下，重写回复。

### 3.2 路由与状态流转修改 (`src/graph.py`)
- 在 `guardrail_node` 中：
  - 如果检测到 `answer_leakage_flag`（或因为其他安全原因触发），**不要**将 `decision.state` 强制改为 `S2`，也**不要**设置 `need_guardrail=True`。
  - 保持原有的 `decision.state` 和 `decision.strategy`。
  - 将判别器的反馈理由（`guardrail_result["guardrail_reason"]`）注入到 `decision.meta["guardrail_feedback"]` 中。
  - 将 `guardrail_retries` 计数加 1。
  - 返回 `regeneration_required: True`。
- 如果重试次数超过 3 次，依然采用兜底的模板回复，以保证安全性。

### 3.3 生成器提示词修改 (`src/generator.py`)
- 在 `generate_reply` 函数中：
  - 检查 `decision.meta` 中是否存在 `guardrail_feedback`。
  - 如果存在，说明当前是一次“重新生成（Regeneration）”。
  - 在传递给 LLM 的 `messages` 中，追加一条系统或用户提示（例如：`"注意：你上一次的回复因为【{feedback}】被拦截。请在保持当前教学策略的前提下，重新组织语言，坚决避免直接给出答案或完成推理，而是通过提问或类比引导学生。"`）。
  - 移除 `decision.need_guardrail` 的模板直接拦截逻辑（除非作为重试耗尽的 fallback）。

## 4. 预期收益
- **异常终止率** 预期从 7.14% 降至 0%（排除极端 API 服务宕机情况）。
- **教学连贯性** 提升，不再出现突兀的“我不会直接给你标准答案”，而是自然地退回到提问或支架引导。
