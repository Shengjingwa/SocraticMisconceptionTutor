# Introduce LangGraph Memory Spec

## Why
目前项目中对于上下文历史（对话记录）的管理，使用的是在 `router.py` 内手动维护一个普通的 list，并依赖 `history_summary` 简单的字符串累加进行截断。这会导致两个问题：一是在长程对话中，字符串截断很容易丢失关键的前期设定；二是未能充分利用 LangGraph 框架自带的持久化状态记忆能力（Checkpointer），使得项目难以支持“Time Travel”以及在框架层面优雅地清理多余 Token。

## What Changes
- 修改 `src/state.py`，将原先在 `SessionMemory` 中的 `messages` 升级为符合 LangGraph 标准的 `messages: Annotated[list[AnyMessage], add_messages]`。
- 修改 `src/graph.py`，编译 `workflow` 时注入 `checkpointer=MemorySaver()`，启用图层面的持久化记忆。
- 新增 `summarize_node`：在 `generate_node` 输出并确保通过护栏后，如果发现 `messages` 列表过长，系统将触发自动摘要，用大模型生成的浓缩摘要替换老旧消息，从而实现在保留记忆精度的同时节约 Token 消耗。
- 重构各处读取上下文的逻辑（如 `classifiers.py` 和 `generator.py`），使其适配新的 `AnyMessage` 对象。
- 使用 `tests/simple_test.py` 验证改动，确保系统稳定不报错。

## Impact
- Affected specs: 无
- Affected code: `src/state.py`, `src/graph.py`, `src/main.py`, `src/router.py`, `src/generator.py`, `src/classifiers.py`

## ADDED Requirements
### Requirement: 优雅的持久化对话上下文与动态截断
The system SHALL provide 原生的 LangGraph `MemorySaver` 来追踪每次调用的对话状态，并在历史对话超限时自动压缩。

#### Scenario: 会话消息过多时自动压缩
- **WHEN** 一场对话持续进行了 6 轮以上，导致 `messages` 对象累积过多
- **THEN** 系统图流转将进入 `summarize` 节点，使用 LLM 将前置消息压缩为一条摘要消息，并通过 `RemoveMessage` 删除被替换的明细，返回一个极简的、但保留核心信息的 `messages` 列表，继续驱动图流转。
