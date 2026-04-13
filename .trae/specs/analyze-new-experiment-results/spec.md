# 分析新实验结果与日志 Spec

## Why
用户运行了一组新的实验，需要全面分析实验结果和日志（位于 `/workspace/logs` 和 `/workspace/results`）以评估系统的表现，并发现可能存在的问题。由于 API 错误和系统配置问题，实验中出现了大量异常，导致后续数据受到影响。同时，引入的 FSM+Guardrail 机制导致认知矫正率跌至 0%，暴露了教学策略和护栏机制的潜在缺陷。

## What Changes
- [分析] 全面分析 `summary_metrics.csv`、`session_summary.jsonl` 和 `evaluation_results.json` 中的评估指标，评估不同版本（Baseline, FSM, FSM+Guardrail）的教学有效性。
- [分析] 检查 `app.log` 和 `pipeline_*.log` 中的系统运行错误，包括 LLM 接口调用失败（404 模型弃用、402 余额不足）和护栏机制频繁拦截的问题。
- [分析] 分析人工审计和对话记录，发现助教在教学策略中存在的“类比滥用”、“过度拒绝”和“无视负面情绪”等导致教学死锁和认知僵局的问题。
- [不修改代码] 本次任务仅进行日志和结果的分析与问题发现，暂不修改任何代码或文件。

## Impact
- Affected specs: 实验数据分析、系统异常排查、教学策略评估。
- Affected code: 无（只读分析任务）。

## ADDED Requirements
### Requirement: 实验结果全面分析报告
系统 SHALL 提供一份详细的实验结果分析报告，包括核心指标对比、教学质量缺陷剖析以及系统运行异常诊断。

#### Scenario: 用户请求分析新实验结果
- **WHEN** 用户提供新的实验日志和结果目录（`/workspace/logs`, `/workspace/results`）
- **THEN** 生成涵盖指标、教学表现和系统错误的综合分析报告，指出 API 失效、护栏过严、类比不当等具体问题。

## MODIFIED Requirements
无

## REMOVED Requirements
无