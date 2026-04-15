# 项目评估问题综合梳理 Spec

## Why
用户使用两个不同的 AI 工具对当前项目进行了评估（结果保存在 `/workspace/docs/project_evaluation.md` 和 `/workspace/docs/PROJECT_ISSUES.md` 中）。文档中指出了架构、实验设计、教育学理论及工程质量等多个维度的缺陷。为了明确下一步的优化方向，需要通过交叉验证代码库，筛选出真实存在的、仍未修复的核心问题，并按优先级整理成一份综合性的问题文档。本次任务仅限文档梳理，不修改任何现有代码。

## What Changes
- [文档生成] 基于 `/workspace/docs/` 下的两份评估报告，结合当前代码库实际情况（例如已修复的硬编码 API Key 问题将不被纳入），生成一份名为 `VERIFIED_PROJECT_ISSUES.md` 的综合问题文档。
- [优先级划分] 将真实存在的问题划分为“严重（Critical）”、“中等（Moderate）”和“轻微（Minor）”三个优先级，并简述问题所在及影响。

## Impact
- Affected specs: 明确项目的技术债与实验设计缺陷，为后续的迭代（如日志清洗、Baseline 公平性重构、多轮推理优化等）提供路线图。
- Affected code: 无代码变更。

## ADDED Requirements
### Requirement: 综合问题文档输出
系统 SHALL 输出一份结构化的 Markdown 文档，列出所有经交叉验证真实存在于当前项目中的问题及其优先级。

#### Scenario: 用户请求综合评估结果
- **WHEN** 用户请求基于两个 AI 评估报告整理项目真实存在的问题
- **THEN** 生成包含优先级排序的综合问题列表，过滤掉已经修复的历史问题（如明文 API Key）。

## MODIFIED Requirements
无

## REMOVED Requirements
无