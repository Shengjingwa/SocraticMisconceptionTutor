# Tasks
- [ ] Task 1: 全面分析核心评估指标
  - [ ] SubTask 1.1: 分析 `summary_metrics.csv`，比较不同系统版本（Baseline, FSM, FSM+Guardrail）在认知纠正率、答案泄露率等指标上的权衡与表现。
  - [ ] SubTask 1.2: 分析 `session_summary.jsonl` 中绝大部分对话最终停留的状态和终止原因（如 `max_turns_reached` 和 `认知僵局`）。

- [ ] Task 2: 分析教学表现与对话质量缺陷
  - [ ] SubTask 2.1: 审查 `evaluation_results.json` 及抽样对话，分析助教的教学逻辑和引导策略。
  - [ ] SubTask 2.2: 识别助教“苏格拉底式引导过于僵化”、“过度依赖类比”以及“无视负面情绪”导致教学有效性降低的问题。

- [ ] Task 3: 诊断系统运行错误与异常
  - [ ] SubTask 3.1: 分析 `app.log` 和 `pipeline_*.log`，找出影响实验正常运行的系统级错误。
  - [ ] SubTask 3.2: 识别 API 接口错误（如 404 模型弃用、402 余额不足）对实验流程的破坏性影响。
  - [ ] SubTask 3.3: 诊断 LLM Judge 频繁触发拦截的原因，分析其对教学进程的负面影响。

# Task Dependencies
- Task 1, 2, 3 相互独立，可并行分析。