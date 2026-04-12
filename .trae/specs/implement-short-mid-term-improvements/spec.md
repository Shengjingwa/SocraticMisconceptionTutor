# 短中长期改进方案落地 Spec

## Why
根据《综合评估报告》的分析，系统存在“上下文记忆丢失”、“安全护栏依赖正则兜底脆弱”、“状态机流转逻辑硬编码”以及“教育学设计缺乏情感维度”等问题。需要按照之前提出的短期（工程鲁棒性与上下文管理）与中期（状态机重构与情感分析）方案对项目进行改进。

## What Changes
- **上下文管理**：在 `generator.py` 和 `classifiers.py` 中，当对话轮数超过 `MAX_HISTORY_TURNS` 时，将截断的早期历史利用 `SessionMemory` 的 `history_summary` 机制动态拼接到系统提示词中，避免长对话“失忆”。
- **安全护栏鲁棒性**：为 `guardrails.py` 中的 LLM-Judge 调用增加 `tenacity` 的重试机制，降低因网络抖动导致的误判或降级到纯正则匹配。
- **情感分析与共情支架**：在 `classifiers.py` 中增加 `sentiment`（情绪）识别字段（如：焦虑/挫败、困惑、自信、平静）。在 `generator.py` 中，若学生情绪为负面，则触发情感支架（Empathy Scaffolding），让助教先共情鼓励再引导。
- **声明式状态机重构**：重构 `router.py`，将内部原本深层嵌套的 `if-elif` 状态转移逻辑提取为基于规则表（Rule-based declarative transitions）的设计，增强其可扩展性。

## Impact
- Affected specs: N/A
- Affected code: 
  - `src/classifiers.py` (NLU 输出结构及 Prompt)
  - `src/generator.py` (Prompt 拼接与情感支架)
  - `src/guardrails.py` (LLM Judge 重试)
  - `src/router.py` (SessionMemory 更新与状态机声明式重构)

## ADDED Requirements
### Requirement: 情感共情支架 (Empathy Scaffolding)
The system SHALL provide 基于学生当前情绪的自适应对话调整能力。

#### Scenario: 挫败感学生
- **WHEN** 分类器检测到学生输入带有“焦虑/挫败”情绪（例如：“物理太难了”）
- **THEN** 生成器必须在回复的开头附加共情或鼓励的语句（如：“没关系，这个概念确实有点绕，我们慢慢来”），再抛出引导问题。

## MODIFIED Requirements
### Requirement: 上下文记忆管理
- **原逻辑**：直接截断最近 `MAX_HISTORY_TURNS` 轮的对话。
- **新逻辑**：截断对话的同时，若存在历史总结（`history_summary`），应将其作为背景信息注入给大模型，供 NLU 和 Generator 参考。
