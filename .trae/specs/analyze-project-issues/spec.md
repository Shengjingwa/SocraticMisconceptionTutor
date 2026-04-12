# Analyze Project Issues Spec

## Why
根据 `/workspace/docs/PROJECT_ISSUES.md` 提供的一份外部（针对极早期原型的）评估报告，其指出的诸多问题（如：只有 `test.ipynb`、无依赖管理、无状态机、纯 RAG 检索生成等）反映的是该项目经历一系列大规模重构**之前**的早期形态。为了明确哪些指控在当前（最新）的架构下依然真实存在，哪些已经是过时信息，需要进行全盘梳理，并制定针对真实存在缺陷的短中长期解决清单。

## What Changes
- 通过阅读源码，核对 `PROJECT_ISSUES.md` 中指出的“无状态管理”、“无自动化测试”、“纯向量检索”、“缺乏依赖说明”等问题。
- 梳理出项目中**仍未解决或新出现的真实问题**（例如缺乏人类学生实验、学生模型粒度不够、未做知识泛化测试）。
- 产出一份结构化的短中长期修复与演进计划，供后续开发迭代参考。

## Impact
- Affected specs: 无直接代码修改，仅产出分析和计划文档。
- Affected code: 无

## ADDED Requirements
### Requirement: 诊断与路线图规划
The system SHALL provide 针对过时外部评估报告的过滤甄别，并基于项目最新形态输出有效的工程与教育学演进方案。

#### Scenario: 成功规划
- **WHEN** 任务执行完毕
- **THEN** 用户获得一份清晰的问题真伪判别报告，以及包含短期（Quick wins）、中期（Refactoring）、长期（Advanced Features）的改进方案清单。
