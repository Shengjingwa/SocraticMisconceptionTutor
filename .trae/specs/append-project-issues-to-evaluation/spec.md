# Append Project Issues to Evaluation Spec

## Why
在之前的综合评估报告中，由于只侧重于现有架构和机制的总结，遗漏了用户明确要求的“分析存在的问题”部分。需要针对项目的工程实现和教育学设计维度，补充现有缺陷与不足的详细分析，以指导未来的系统迭代。

## What Changes
- 在 `docs/system_comprehensive_evaluation.md` 中新增“四、 项目存在的问题与改进建议”章节。
- 补充之前收集到的工程维度缺陷（如上下文记忆丢失、提示词构建硬编码、安全护栏规则脆弱、状态机路由硬编码等）。
- 补充之前收集到的教育学维度缺陷（如对迷思概念转变机制理解较浅、提问粒度不足、情感与动机维度缺失、学习者建模静态化等）。

## Impact
- Affected specs: 完善对智能体项目的整体架构与评估设计文档。
- Affected code: `docs/system_comprehensive_evaluation.md` 将被修改并追加内容。

## ADDED Requirements
### Requirement: Project Issues and Recommendations
系统必须在评估报告中明确指出项目当前在工程和教育学设计上存在的问题及改进建议。

#### Scenario: Success case
- **WHEN** 查阅 `docs/system_comprehensive_evaluation.md` 文件的最后部分
- **THEN** 能够看到详尽的“项目存在的问题与改进建议”章节，涵盖至少三个工程问题和三个教育学问题。