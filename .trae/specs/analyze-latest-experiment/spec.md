# 分析最新实验结果与日志 Spec

## Why
用户运行了一组新的完整实验流水线（包括 `simulator.py`, `evaluator.py`, `llm_judge.py`），日志保存在 `/workspace/logs/pipeline_2026-04-13_22-17-00.log` 等文件中。用户需要一份基于最新实验结果和日志的全面分析报告，以评估系统的教学表现，并发现可能存在的问题。由于这是纯分析任务，用户明确要求“暂时无需修改文件”。

## What Changes
- [分析] 提取并分析 `summary_metrics.csv` 和 `session_summary.jsonl` 中的核心评价指标（如认知纠正率、答案泄漏率、状态转移成功率）。
- [分析] 检查 `pipeline_*.log` 和 `app.log` 中的系统运行日志，排查报错、API 异常或逻辑死锁。
- [分析] 检查 `evaluation_results.json` 和 `manual_audit.csv`，评估 LLM Judge 对对话质量的打分和定性评价。
- **不修改任何代码**：只提供一份结构化的分析报告。

## Impact
- Affected specs: 实验数据分析与系统问题诊断。
- Affected code: 无（纯读操作）。

## ADDED Requirements
### Requirement: 实验结果综合分析与问题定位报告
系统 SHALL 提供针对最新批量仿真实验的综合分析报告，明确定位潜在的系统级或策略级问题（如 API 失效、路径硬编码、认知僵局等）。

#### Scenario: 用户请求分析最新实验数据
- **WHEN** 用户提供包含最新日志与结果的目录 (`/workspace/logs`, `/workspace/results`) 且要求“暂时无需修改文件”
- **THEN** 生成详细的分析报告并列出发现的所有潜在问题，不修改任何文件。

## MODIFIED Requirements
无

## REMOVED Requirements
无