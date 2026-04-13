# Tasks
- [x] Task 1: 升级全局 GraphState 结构
  - [x] SubTask 1.1: 在 `src/state.py` 中引入 `Annotated`, `add_messages`, `AnyMessage`。
  - [x] SubTask 1.2: 在 `GraphState` 中新增 `messages: Annotated[list[AnyMessage], add_messages]` 字段。
  - [x] SubTask 1.3: 清理 `router.py` 中 `SessionMemory` 里旧的 `messages` 字段，将上下文维护剥离给全局状态。

- [x] Task 2: 注入 MemorySaver 和更新入口调用
  - [x] SubTask 2.1: 在 `src/graph.py` 中，实例化 `MemorySaver()`，在 `workflow.compile(checkpointer=memory)` 时传入。
  - [x] SubTask 2.2: 在 `src/main.py` 的 `step` 和 `astep` 方法中，调用 `app_graph.invoke` 时使用 `{"messages": [HumanMessage(content=user_input)], ...}` 发送新输入，并在 config 中传入 `{"configurable": {"thread_id": self.memory.session_id}}` 以区分不同的对话实例。

- [x] Task 3: 适配大模型组件并引入动态压缩节点
  - [x] SubTask 3.1: 更新 `classifiers.py` 和 `generator.py`，使之能正确读取原生的 `state["messages"]` 并从中提取字符串形式的历史。
  - [x] SubTask 3.2: 在 `src/graph.py` 中，编写 `summarize_node`：如果 `messages` 的长度大于 `config.MAX_HISTORY_TURNS * 2`，让大模型总结这些消息并将其转化为新的 `SystemMessage` 存入，同时使用 `RemoveMessage` 指令从状态中移除旧记录。
  - [x] SubTask 3.3: 调整 `graph.py` 内部边的走向，确保最终生成的系统回复（AssistantMessage）能够正确被存入 `messages`，并且能够流经（或跳过）`summarize_node` 最后到达 `END`。

- [x] Task 4: 进行简单测试
  - [x] SubTask 4.1: 执行 `tests/simple_test.py`，观察流程图的正常流转与 `messages` 归约情况，确保没有引发异常。