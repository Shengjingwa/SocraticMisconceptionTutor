# Experiment Results Analysis Spec

## Why
根据用户提供的108组批量仿真实验统计数据（`results/summary_metrics.csv`），三个版本（Baseline, FSM, FSM+Guardrail）在各项核心指标上表现出了显著差异。为了从教育学与系统架构设计的角度理解这些差异，需要对实验结果进行深度分析，找出数据背后的原因，为后续项目的优化方向和论文撰写提供理论依据。

## What Changes
- 撰写一份 Markdown 格式的实验结果分析报告 `docs/experiment_analysis.md`。
- 报告将包含对每个核心指标（如意图/概念识别准确率、认知纠正率、平均对话轮数、拒绝成功率与护栏拦截率等）的详细原因分析。

## Impact
- Affected specs: 辅助学术论文撰写，不涉及系统核心运行逻辑的修改。
- Affected code: `docs/experiment_analysis.md`（新增）

## ADDED Requirements
### Requirement: 实验数据分析报告
系统需要生成一份逻辑清晰、结构严谨的分析报告，涵盖以下几点：
1. **Identification Accuracy (识别准确率) 分析**：解释为何仅在 FSM+Guardrail 版本中达到 100%，而 Baseline 和 FSM 为 0%。
2. **Cognitive Correction Rate (认知纠正率) 分析**：探讨为何三个版本的纠正率均偏低（12.50% - 16.00%），以及 FSM+Guardrail 为何表现最好。
3. **Avg Turns (平均轮数) 分析**：分析对话轮数较短（1.19 - 1.40轮）的系统与教育学原因。
4. **Guardrail Metrics (护栏拦截与拒绝成功率) 分析**：阐述 Refusal Success Rate (100%) 与 Guardrail Interception Rate (2.86%) 在 FSM+Guardrail 版本中的有效性。
5. **Answer Leakage & Transition Success (答案泄露与状态流转) 分析**：分析基础 LLM 在防止答案泄露方面的能力，以及状态机流转的稳定性（100%）。

#### Scenario: Success case
- **WHEN** 实验分析报告生成完成
- **THEN** 用户可以直接将其作为硕士毕业论文的实验分析章节素材使用。
