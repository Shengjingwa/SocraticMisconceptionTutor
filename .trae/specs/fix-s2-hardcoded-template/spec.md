# Fix S2 Hardcoded Template Spec

## Why
分析新实验结果（`summary_metrics.csv`）和人工审计日志（`manual_audit.csv`）后发现：在 `FSM+Guardrail` 版本中，Cognitive Correction Rate（认知纠正率）从 100.00% 下降到了 91.67%。
查阅日志发现，当学生表达挫败或试图转移话题（如“物理太难了，我们聊点别的吧”）时，NLU 会将其意图识别为 `Off_Topic` 或 `Direct_Answer_Seek`，导致 `risk_flag = True`，从而触发 `S2`（Refusal_And_Guidance）状态。
然而，在 `generator.py` 中，一旦处于 `S2` 或 `need_guardrail=True` 状态，系统会直接返回硬编码的模板回复（如“我先不直接代答，我们一起把关键关系想清楚。”）。这完全绕过了大模型生成和新加入的情感支架（Empathy Scaffolding），使得回复极其生硬且缺乏同理心，导致部分对话破裂和纠正率下降。

## What Changes
- 移除 `src/generator.py` 中针对 `S2` 或 `need_guardrail` 的硬编码模板直接返回逻辑。
- 将 `S2` 状态下的拒绝与重定向任务交给大模型生成。
- 为 `S2` 状态追加专门的重定向提示指令，确保大模型能用自然、委婉的口吻拒绝直接给出结论，或将话题拉回物理讨论，同时能够无缝结合情感支架。

## Impact
- Affected specs: 无
- Affected code: `src/generator.py`

## ADDED Requirements
### Requirement: 大模型自然重定向与拒绝
The system SHALL provide 使用大模型自然生成拒绝与话题重定向的能力，而不是生硬地返回预设模板。

#### Scenario: 学生因挫败试图转移话题
- **WHEN** 学生说“物理太难了，我们聊点别的吧”，意图被识别为 `Off_Topic`，进入 `S2` 状态
- **THEN** 生成器应将情感支架与重定向指令结合，通过大模型生成诸如“没关系，物理确实有点绕。我们先不聊太深的理论，想想之前提到的水车例子...”这样自然且带共情的回复。
