# 修复 VERIFIED_PROJECT_ISSUES 综合问题 Spec

## Why
根据 `VERIFIED_PROJECT_ISSUES.md` 中的综合评估报告，项目中存在多项影响实验公平性、评估有效性、护栏逻辑及工程质量的问题。除开明确被排除的“P1 认知状态分类缺乏多轮推理”和“P3 迷思概念库覆盖面极窄”外，我们需要彻底修复剩下的所有严重（Critical）、中等（Moderate）和轻微（Minor）问题，以确保系统具备真实可靠的教学有效性和严谨的实验架构。

## What Changes
- **修复标签泄漏与 Baseline 不公 (A1)**：为 Baseline 节点重写专属的 System Prompt，切断对 FSM 策略指令和真值概念的直接读取，确保对比实验的基线公平。
- **修复评估数据污染与无隔离 (C2)**：在每次启动新一轮仿真测试时，自动清理旧日志，确保单次 `summary_metrics.csv` 统计只包含当前批次的实验数据。
- **修复实验样本量不足与对抗模拟偏差 (E1 & E2)**：将 `num_runs` 的默认值提升，并移除 `simulation_profiles.json` 中要求模拟学生强制“索要答案或跑题”的人为对抗指令。
- **修复降级策略运算符优先级 Bug (P5)**：修正 `generator.py` 中的 `and/or` 优先级错误，确保仅在“（处于 S5 且卡壳）或（感到焦虑）”时才触发降级。
- **修复护栏覆盖盲区与逻辑矛盾 (A2)**：修正 `tutor_graph.py` 中的 `is_already_safe` 变量控制流语义；并在 `guardrails.py` 中补充当迷思概念未知时的通用输出泄露检测兜底逻辑。
- **修复核心评估指标定义缺陷 (V1)**：重构 `evaluator.py` 中的计算逻辑，使 `Identification Accuracy` 和 `Transition Success Rate` 的分母和分子具备真实的区分度。
- **修复正则过度清理 (C5)**：修改或移除 `generator.py` 中盲目删除括号内容的正则，保护 LLM 生成的物理公式。
- **修复死代码 (A3) 与入口漂移 (Documentation Drift)**：清理不可达图分支，并将 `main.py` 的默认执行入口调整为 `chat()` 以对齐文档。

## Impact
- Affected specs: 实验数据隔离与指标计算、状态图路由控制流、提示词安全防护与生成策略。
- Affected code: `src/tutor_graph.py`, `src/simulator.py`, `src/evaluator.py`, `src/generator.py`, `src/guardrails.py`, `src/main.py`, `data/simulation_profiles.json`.

## ADDED Requirements
### Requirement: 实验批次隔离
系统 SHALL 在每次执行批量仿真 (`simulator.py`) 时生成独立的日志或在启动前清理旧日志，防止数据污染。

#### Scenario: 运行新的仿真实验
- **WHEN** 用户执行 `python src/simulator.py`
- **THEN** 旧的 `turn_logs.jsonl` 和 `session_summary.jsonl` 被清理/隔离，评估结果纯净。

## MODIFIED Requirements
### Requirement: Baseline 公平性
Baseline SHALL 作为无策略指令、无前置标签注入的朴素大语言模型基线，仅提供通用的物理助教角色设定。

### Requirement: 护栏无盲区防护
LLM Judge SHALL 在任何情况下（即使未识别出具体迷思概念）都对助教的输出执行泄露答案检测。

## REMOVED Requirements
### Requirement: 模拟学生对抗行为
**Reason**: 人为注入的“必须尝试索要答案或跑题”导致模拟场景偏离真实学生认知行为。
**Migration**: 移除 `simulation_profiles.json` 中相关强制指令。