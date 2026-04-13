# Introduce LangGraph Memory Spec

## Why
目前 `SessionMemory` 中的 `history_summary` 采取了简单的字符串截断拼接策略，长对话时容易丢失早期重要的学生误概念细节，导致教学偏离；同时原有的历史消息存储 `messages` 缺乏原生框架级支持。使用 LangGraph 的原生 `MemorySaver` 与 `add_messages` 结合总结节点，可以优雅地实现持久化状态记忆与滑动窗口摘要机制，达到 Token 消耗和记忆精度的完美平衡。

## What Changes
- 修改 `src/state.py`，在 `GraphState` 中引入 `messages: Annotated[list[AnyMessage], add_messages]` 字段。
- 修改 `src/graph.py`，编译 `app_graph` 时传入 `checkpointer=MemorySaver()`。
- 新增 `summarize_node`：在 `generate_node` 之后增加一个条件判断，若 `messages` 长度超过阈值（如 `MAX_HISTORY_TURNS`），则流转到 `summarize_node`。由大模型生成精简摘要并更新到 `memory.history_summary`，同时返回 `RemoveMessage` 对象以清理历史长消息。
- 修改 `src/main.py`，调用 `app_graph.invoke` 或 `ainvoke` 时传入 `config={"configurable": {"thread_id": self.memory.session_id}}`，并通过 `messages: [HumanMessage(content=user_input)]` 发送新消息。
- 移除 `router.py` 中手动向 `memory.messages` 和 `memory.history_summary` 追加文本的旧逻辑。

## Impact
- Affected specs: 无
- Affected code: `src/state.py`, `src/graph.py`, `src/main.py`, `src/router.py`, `src/generator.py`, `src/classifiers.py`

## ADDED Requirements
### Requirement: 原生智能记忆与自动压缩
The system SHALL provide 基于 LangGraph Memory 的原生状态持久化，并在消息过长时触发 LLM 摘要压缩。

#### Scenario: 历史对话超限
- **WHEN** 当前 `messages` 列表中的消息数超过阈值
- **THEN** 系统会自动触发 `summarize_node`，生成新的历史摘要并替换旧消息，保持大模型推理时的 Token 消耗处于可控范围内。