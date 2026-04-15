# 实验套件结果分析报告 Spec

## Why
当前已在 `/workspace/experiments/suite_2026-04-15_23-24-10` 生成一组实验套件产物，需要形成一份可复现、可引用的分析报告以支撑论文写作与迭代决策。

## What Changes
- 对指定 suite 目录下的 `aggregate_summary.*`、`run_01/logs/*`、`run_01/results/*` 进行结构化读取与二次统计
- 输出一份面向论文写作的分析报告（定量结论 + 证据链接 + 失败模式 + 问题清单）
- **BREAKING**：无

## Impact
- Affected specs: 实验评估可复现性、指标解释口径、失败模式诊断
- Affected code: 无（仅分析与报告输出）

## ADDED Requirements
### Requirement: 实验分析报告
系统 SHALL 针对指定实验目录生成结构化分析报告，并明确数据来源文件路径与关键证据。

#### Scenario: 成功生成报告
- **WHEN** 用户提供实验目录 `/workspace/experiments/suite_2026-04-15_23-24-10`
- **THEN** 输出内容包含：
  - 版本级指标汇总（Baseline/FSM/FSM+Guardrail）
  - 画像级（P1/P2/P3）拆解与关键差异解释
  - 安全性相关（泄露率、护栏触发/原因分布、Max_Retries_Exceeded 样例）
  - 诊断相关（混淆矩阵/主要混淆项，重点关注 M-ELE-002→M-ELE-001）
  - 盲评相关（socratic/effectiveness 的均值与分布，若存在 evaluation_results.json）
  - 存在问题清单（问题→证据→可能原因→下一步验证建议）

## MODIFIED Requirements
### Requirement: 无
无既有功能修改。

## REMOVED Requirements
### Requirement: 无
**Reason**: 不涉及移除。
**Migration**: 无。

