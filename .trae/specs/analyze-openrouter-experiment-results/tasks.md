# Tasks

- [ ] Task 1: 提取与对比核心评估指标
  - [ ] SubTask 1.1: 分析 `/workspace/results/summary_metrics.csv` 中的数据。记录 Baseline、FSM、FSM+Guardrail 之间的认知纠正率（Cognitive Correction Rate）、识别准确率和拦截率表现。检查此前的“虚高”和“归零”现象是否缓解。
  - [ ] SubTask 1.2: 从 `/workspace/logs/session_summary.jsonl` 中审查对话结束状态（如是否仍大量陷入“认知僵局”或耗尽 10 轮最大次数）。

- [ ] Task 2: 审查对话质量与策略降级机制效能
  - [ ] SubTask 2.1: 通过分析 `/workspace/results/manual_audit.csv` 中的实际对话片段，检查学生多次卡壳时是否成功触发了“降级干预策略”或“情感支架”，并成功打破了对话死循环。
  - [ ] SubTask 2.2: 检查 Baseline 是否不再泄漏标签，体现了朴素大语言模型的真实水平。

- [ ] Task 3: 诊断系统级异常与回退链路状态
  - [ ] SubTask 3.1: 检查 `/workspace/logs/app.log` 或 `/workspace/logs/pipeline_*.log`，确认之前频繁出现的 404 (Model Deprecated) 和 402 (Insufficient Quota) 错误是否已经被修复。
  - [ ] SubTask 3.2: 检查日志中是否有触发 Langchain `with_fallbacks` 相关的错误或警告，评估 OpenRouter 链路和 DashScope 回退链路的稳定性。

# Task Dependencies
- Task 1, 2, 3 可由数据分析和代码检索子代理（search agent）并行执行。
- 任务执行期间不得修改任何现有的源码或配置。