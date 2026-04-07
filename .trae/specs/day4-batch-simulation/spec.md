# 批量跑仿真与三版本对照 (Day 4) Spec

## Why
为验证苏格拉底式对话智能体的有效性与安全性，需要进行批量仿真测试。通过对比“基线版本 (Baseline)”、“仅状态机版本 (FSM)”和“状态机+护栏版本 (FSM+Guardrail)”，评估状态机和护栏机制在认知修正、防止答案泄露等方面的实际作用，并输出量化指标供论文分析。

## What Changes
- 新增 `docs/experiment_versions.md`，定义三个对比版本的详细配置。
- 新增 `src/simulator.py`，实现基于大模型（如 DeepSeek）的模拟学生，根据学生画像与系统进行多轮自动对话测试。
- 修改/适配主流程以支持切换三种版本运行（Baseline / FSM / FSM+Guardrail）。
- 批量运行仿真实验（4个迷思 × 3类画像 × 3个版本 × N次）。
- 新增 `src/evaluator.py`（或指标抽取脚本），读取生成的日志，计算 8 项核心评估指标，输出 `results/summary_metrics.csv`。
- 创建人工抽样校验模板 `results/manual_audit.csv`。

## Impact
- Affected specs: 系统的自动化测试与量化评估流程。
- Affected code: `src/main.py`（增加版本切换配置），`src/graph.py`（增加逻辑旁路），新增 `src/simulator.py` 和 `src/evaluator.py`。

## ADDED Requirements
### Requirement: 系统版本切换
系统应支持通过参数切换三种运行模式：
- **Baseline**：跳过状态机和护栏，直接调用大模型（附带基础教学Prompt）进行回复。
- **FSM**：启用状态机路由与生成，但跳过输入和输出的安全护栏检查。
- **FSM+Guardrail**：启用完整架构，包括状态机和护栏。

### Requirement: 自动化仿真对话
系统应能读取 `data/simulation_profiles.json` 和 `data/misconceptions.json`，利用大模型扮演特定画像的学生，与智能体进行自动对话。当智能体判断问题解决（`resolved_flag=True`）或达到最大轮次（如 8 轮）时，自动结束当前会话并记录日志。

### Requirement: 核心指标计算
系统应能解析生成的日志文件（`turn_logs.jsonl` 和 `session_summary.jsonl`），自动计算识别准确率、认知修正率、拦截率等 8 项核心指标，并以表格形式输出以供对比。