# 全面分析最新实验结果 (v9) Spec

## Why
本次新跑批实验已生成新的主日志与结果文件（如 [pipeline_2026-04-14_22-14-21.log](file:///workspace/logs/pipeline_2026-04-14_22-14-21.log)、[summary_metrics.csv](file:///workspace/results/summary_metrics.csv)）。初步观察显示 **Abnormal Termination Rate 异常偏高**，且主日志中出现了 `LLM Judge failed: 1 validation error for GuardrailOutput` 与大量 `Connection error`，这会显著污染平均轮次、纠错率等核心指标的可解释性。

需要对 `/logs` 与 `/results` 进行一次只读、可复现的全面分析，输出一份“指标 + 案例 + 失效模式”三位一体的分析报告，并明确当前主要问题来源（模型调用稳定性、评测统计口径、策略行为退化等），为下一轮实验提供决策依据（本轮不修改代码）。

## What Changes
- [只读] 识别并读取 `/logs/pipeline_*.log` 最新主日志、[session_summary.jsonl](file:///workspace/logs/session_summary.jsonl)、[turn_logs.jsonl](file:///workspace/logs/turn_logs.jsonl)、[app.log](file:///workspace/logs/app.log)。
- [只读] 读取 `/results` 下的 [summary_metrics.csv](file:///workspace/results/summary_metrics.csv) 与 [manual_audit.csv](file:///workspace/results/manual_audit.csv)。
- 输出一份中文分析报告，至少覆盖：
  - 核心指标总览（Baseline / FSM / FSM+Guardrail）与对比解读
  - 终止原因分布（resolved / aborted / max_turns_reached / error）与对指标的污染程度
  - 护栏相关：拦截率、拒答成功率、泄题率是否可信；LLM Judge 失败/降级发生频次
  - 典型会话案例（至少 1 个成功、1 个失败/异常），定位“失败是教学失败还是工程失败”
  - 结论与问题清单（按优先级列出）
- **注意**：本任务为纯分析性质的只读操作，不修改任何业务代码与评测逻辑。

## Impact
- Affected specs: 无（仅分析操作）。
- Affected code: 无（仅读取日志与数据）。

## ADDED Requirements
### Requirement: 最新实验结果与日志分析报告
系统 SHALL 对最新实验产物进行只读分析并输出报告，报告 SHALL 同时包含“指标结论”和“问题定位”，并明确指出异常终止与护栏/评测稳定性对指标的影响边界。

#### Scenario: Success case
- **WHEN** 用户完成一次新实验跑批并要求分析
- **THEN** 输出一份结构化的中文分析报告，且报告能定位出异常终止的主因并给出可执行的后续建议（不涉及代码修改）。
