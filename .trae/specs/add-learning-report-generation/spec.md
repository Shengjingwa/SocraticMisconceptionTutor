# Add Learning Report Generation Spec

## Why
目前系统在对话结束（如满足 `understanding_verified == True`）时，仅仅是停止回复，缺乏一个面向学生或教师的结构化形成性评价闭环。引入“学情诊断报告”可以明确告知学生本次纠正的误概念是什么，复盘纠正过程，并给出后续的学习建议，从而大幅提升教育辅导的实用性和可观测性。

## What Changes
- 在 `generator.py` 中新增 `generate_learning_report` 函数。
- 在 `main.py` 的核心处理逻辑（`_process_graph_result` 或 `step` 流程内）中，当检测到本次交互使得 `understanding_verified` 从 False 变为 True（即对话 `resolved` 达成）时，自动触发调用该函数生成诊断报告，并将其附加在最终的 `final_reply` 末尾，或作为独立字段返回并在控制台输出。
- 使用提供的百炼 API Key 进行一次简单的成功用例测试。

## Impact
- Affected specs: `main.py`, `generator.py`
- Affected code: 
  - `src/generator.py` (新增大模型生成报告的方法)
  - `src/main.py` (触发生成报告并修改返回结果)

## ADDED Requirements
### Requirement: 学情诊断总结报告
The system SHALL provide 当系统确认学生掌握概念时，自动生成一份包含“暴露迷思”、“纠正过程”、“后续建议”的学情总结。

#### Scenario: 成功验证概念并生成报告
- **WHEN** NLU 分类为“概念掌握验证”并且系统状态机也置为 `S6`，判定 `resolved == True`
- **THEN** 在回复给学生肯定反馈后，自动追加一段由大模型根据全量 `history_summary` 总结出的《学情诊断报告》。