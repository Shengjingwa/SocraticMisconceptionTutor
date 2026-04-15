# 分析最新实验流水线结果 Spec

## Why
用户运行了一组新的实验流水线（包括 `simulator.py`, `evaluator.py`, `llm_judge.py`），日志保存到了 `logs/pipeline_2026-04-13_23-07-11.log`。在之前修复了大量架构、公平性（A1）、日志污染（C2）、以及护栏退避等问题后，需要对最新的实验结果和日志进行全面分析，评估各项核心指标是否恢复正常，并找出可能仍然存在的问题。

## What Changes
- [分析] 全面分析 `/workspace/logs/pipeline_2026-04-13_23-07-11.log`、`/workspace/results/summary_metrics.csv`、`/workspace/logs/session_summary.jsonl` 等最新生成的文件。
- [分析] 对比修复前后的各项评估指标（如认知纠正率、识别准确率、答案泄露率），判断 Baseline、FSM、FSM+Guardrail 之间的消融实验效果。
- [分析] 检查新的护栏动态退避机制、API 回退（OpenRouter->DashScope）机制、以及“教后测”机制是否在日志中正常触发并发挥作用。
- [分析] 通过 `evaluation_results.json` 或 `manual_audit.csv` 定性评估教学质量和苏格拉底式引导效果。
- **不修改任何代码**：只提供分析报告与问题排查。

## Impact
- Affected specs: 实验数据分析与报告输出。
- Affected code: 无（纯只读分析任务）。

## ADDED Requirements
### Requirement: 实验流水线综合分析与问题定位
系统 SHALL 提供针对最新实验数据的综合分析报告，明确定位修复后各项指标的变化及潜在新问题。

#### Scenario: 用户请求生成最新实验流水线分析报告
- **WHEN** 用户提供包含日志与结果的目录 (`/workspace/logs`, `/workspace/results`) 且要求“暂时无需修改文件”
- **THEN** 生成详细的分析报告并列出发现的所有潜在问题。

## MODIFIED Requirements
无

## REMOVED Requirements
无