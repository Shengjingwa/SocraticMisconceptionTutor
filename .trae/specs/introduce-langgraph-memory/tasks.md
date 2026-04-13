# Tasks
- [ ] Task 1: 升级 GraphState 以支持原生消息归约
  - [ ] SubTask 1.1: 在 `src/state.py` 中引入 `from langgraph.graph.message import add_messages` 和 `from langchain_core.messages import AnyMessage`。
  - [ ] SubTask 1.2: 向 `GraphState` 中添加 `messages: Annotated[list[AnyMessage], add_messages]`。

- [ ] Task 2: 在图中引入 MemorySaver 与 Summarize 节点
  - [ ] SubTask 2.1: 在 `src/graph.py` 中导入 `MemorySaver` 并将其作为 `checkpointer` 传给 `workflow.compile()`。
  - [ ] SubTask 2.2: 在 `src/graph.py` 中新增 `finalize_node(state: GraphState)` 节点。该节点在护栏安全放行后（或 `baseline_node` 后）执行，负责将最终生成的 `final_reply` 打包为 `AIMessage` 并返回 `{"messages": [AIMessage(content=final_reply)]}`。如果 `messages` 长度超出阈值（如 `config.MAX_HISTORY_TURNS * 2`），则调用 LLM 压缩早期的消息为新的 `memory.history_summary`，并通过返回 `RemoveMessage` 对象将旧消息从状态中剔除。
  - [ ] SubTask 2.3: 修改图的流转边：将 `route_after_guardrail` 的 `end` 分支指向 `finalize` 节点，`baseline` 指向 `finalize`（若跳过护栏）或修改护栏后置流转，最后由 `finalize` 指向 `END`。

- [ ] Task 3: 改造现有节点以适配原生 `messages` 
  - [ ] SubTask 3.1: 在 `src/classifiers.py` 和 `src/generator.py` 中，不再从 `memory.messages` 中读取历史记录，而是直接从 `state["messages"]` 提取对话上下文。
  - [ ] SubTask 3.2: 在 `src/router.py` 的 `update_after_turn` 函数中，移除手动追加 `user_input` 和 `final_reply` 到 `memory.messages` 的逻辑，并移除简单的字符串截断拼接 `history_summary` 的逻辑。

- [ ] Task 4: 调整系统入口调用的传参
  - [ ] SubTask 4.1: 在 `src/main.py` 中，修改 `app_graph.invoke` 和 `ainvoke` 的调用。在 `inputs` 字典中传入 `{"messages": [HumanMessage(content=user_input)]}`，同时在第二个参数传入 `config={"configurable": {"thread_id": self.memory.session_id}}`，以激活每个会话独立的 LangGraph Memory。