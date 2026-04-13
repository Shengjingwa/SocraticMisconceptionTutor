# Tasks
- [ ] Task 1: 全面分析核心评估指标
  - [ ] SubTask 1.1: 分析 `summary_metrics.csv`，比较不同系统版本（Baseline, FSM, FSM+Guardrail）在认知纠正率、答案泄露率等指标上的表现，指出认知矫正率跌至 0% 的异常。
  - [ ] SubTask 1.2: 分析 `session_summary.jsonl`，发现绝大多数对话最终停留的状态为“认知僵局”并因达到最大轮数而终止。

- [ ] Task 2: 诊断系统运行错误与异常现象
  - [ ] SubTask 2.1: 分析 `app.log` 和 `pipeline_*.log`，找出影响实验正常运行的 API 接口错误（如 404 模型弃用、402 余额不足）。
  - [ ] SubTask 2.2: 审查 `manual_audit.csv`，发现并记录严重的内部思维链和系统指令泄露问题（如 `<think>` 标签和草稿直接输出给学生）。
  - [ ] SubTask 2.3: 诊断 LLM Judge 频繁触发误判拦截的原因，分析其对正常物理事实陈述的过度限制。

- [ ] Task 3: 分析教学表现与对话质量缺陷
  - [ ] SubTask 3.1: 审查 `evaluation_results.json` 和 `manual_audit.csv` 中的抽样对话，分析助教的教学逻辑和引导策略。
  - [ ] SubTask 3.2: 识别助教“过度教条化的苏格拉底式引导”、“生搬硬套物理类比（如水流、跑步）”以及“无视学生极度挫败情绪”导致教学死循环的问题。

# Task Dependencies
- Task 1, 2, 3 相互独立，可并行分析。