# 实验套件结果分析报告 Spec（suite_2026-04-16_10-54-58）

## Why
当前已在 `/workspace/experiments/suite_2026-04-16_10-54-58` 生成一组实验套件产物（run_01/run_02 已完备，run_03 未完备），需要形成一份可复现、可引用的分析报告以支撑论文写作与迭代决策，并明确不完整产物对结论的影响。

## What Changes
- 对指定 suite 目录下的 `run_01/*`、`run_02/*`、`run_03/*` 进行结构化读取与二次统计
- 输出一份面向论文写作的分析报告（定量结论 + 证据链接 + 失败模式 + 问题清单）
- 新增 run_01 vs run_02 的一致性对比（指标差异、主要失败模式差异）
- 明确标注：哪些结论来自 run_01/run_02 的一致部分，哪些因 run_03 缺失而不可得或不可靠
- **BREAKING**：无

## Impact
- Affected specs: 实验评估可复现性、指标解释口径、失败模式诊断、部分运行缺失的处理口径
- Affected code: 无（仅分析与报告输出）

## ADDED Requirements
### Requirement: 实验分析报告（支持未跑完的 suite）
系统 SHALL 针对指定实验目录生成结构化分析报告，并明确数据来源文件路径与关键证据；当 suite 中存在未完备 run 时，报告必须显式标注缺失项与不确定性。

#### Scenario: 成功生成报告（含不完备 run）
- **WHEN** 用户提供实验目录 `/workspace/experiments/suite_2026-04-16_10-54-58`
- **THEN** 输出内容包含：
  - 产物完整性盘点：按 run_01/run_02/run_03 列出 logs/results/pipeline 是否齐全与缺失项
  - 版本级指标汇总（Baseline/FSM/FSM+Guardrail）：基于 run_01/run_02 的 `summary_metrics.csv`
  - 画像级（P1/P2/P3）拆解与关键差异解释：基于 `session_summary.jsonl` 与 `turn_logs.jsonl`
  - 安全性相关：泄露率、护栏触发/原因分布、Max_Retries_Exceeded 样例
  - 诊断相关：混淆矩阵/主要混淆项（重点 M-ELE-002→M-ELE-001）
  - 盲评相关：基于 run_01/run_02 的 `evaluation_results.json` 统计 socratic/effectiveness 的均值与分布
  - run 间一致性：对比 run_01 vs run_02 的关键指标与主要失败模式，并给出差异解释
  - 存在问题清单：问题→证据→可能原因→下一步验证建议

## MODIFIED Requirements
### Requirement: 无
无既有功能修改。

## REMOVED Requirements
### Requirement: 无
**Reason**: 不涉及移除。
**Migration**: 无。
