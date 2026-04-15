# Tasks
- [x] Task 1: 提取与分析核心评估指标
  - [x] SubTask 1.1: 查阅 `summary_metrics.csv` 和 `session_summary.jsonl`，记录认知纠正率、答案泄露率、以及最终停留状态（如“认知僵局”）。

- [x] Task 2: 审查教学表现与对话质量
  - [x] SubTask 2.1: 通过分析 `evaluation_results.json` 或 `manual_audit.csv` 中的实际对话片段，诊断助教引导策略是否仍然存在死板、类比不当或情绪应对不佳等问题。

- [x] Task 3: 排查系统级错误与异常
  - [x] SubTask 3.1: 检查 `app.log` 等运行日志，确认此前出现的大规模 API 错误（如 404、402 等）和护栏机制过度拦截问题。
  
# Task Dependencies
- Task 1, 2, 3 可并行进行。