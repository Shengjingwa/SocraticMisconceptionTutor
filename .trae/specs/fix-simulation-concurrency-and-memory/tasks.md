# Tasks
- [ ] Task 1: 修复 turn_id/turn_count 数据污染
  - [ ] SubTask 1.1: 在 [main.py](file:///workspace/src/main.py) 中将 `self.memory` 与 `final_state["memory"]` 对齐（优先采用图返回的 memory），再执行 `update_after_turn`。
  - [ ] SubTask 1.2: 在 [graph.py](file:///workspace/src/graph.py) 的 `baseline_node` 中确保 `turn_count` 递增（返回 `"memory": new_memory`）。
  - [ ] SubTask 1.3: 在 [router.py](file:///workspace/src/router.py) 的 `update_after_turn` 中恢复/实现对 `history_summary` 的更新逻辑（与 Memory 摘要链路保持一致）。

- [ ] Task 2: 修复 LangGraph Memory 节点的就地修改风险
  - [ ] SubTask 2.1: 在 [graph.py](file:///workspace/src/graph.py) 的摘要/终结节点中使用 `model_copy(deep=True)` 更新 `history_summary`，禁止就地修改。
  - [ ] SubTask 2.2: 明确 `thread_id` 传递口径：交互模式与仿真模式都确保 `thread_id == session_id`，避免检查点串会话。

- [ ] Task 3: 修复并发仿真日志混行与 JSONL 并发写入风险
  - [ ] SubTask 3.1: 在 [logger.py](file:///workspace/src/logger.py) 为 `log_turn/log_session` 引入进程内互斥（lock），保证并发写入的行完整性。
  - [ ] SubTask 3.2: 在 [simulator.py](file:///workspace/src/simulator.py) 将 `print()` 输出改为 `logger_instance.info()`（或新增可关的 console 输出开关），每条包含 `session_id`。
  - [ ] SubTask 3.3: 为批量仿真增加“静默控制台日志”开关，避免 `StreamHandler` 与并发输出相互干扰（可通过环境变量控制）。

- [ ] Task 4: 修复会话异常未标记问题
  - [ ] SubTask 4.1: 在 [simulator.py](file:///workspace/src/simulator.py) 捕获模拟学生/教师关键调用异常时，写入会话级风险标记（例如 memory 的 error_events 或 app 层 flag）。
  - [ ] SubTask 4.2: 在 [main.py](file:///workspace/src/main.py) 的 `end_session()` 根据风险标记写入 `abnormal_end_flag=True` 与具体 `termination_reason`。

- [ ] Task 5: 轻量验证
  - [ ] SubTask 5.1: 运行 `tests/simple_test.py`，确认主对话仍可用。
  - [ ] SubTask 5.2: 以 `SIMULATION_CONCURRENCY=2` 运行一次小规模仿真（可只跑 1 个 misconception × 1 个 profile × 1 个 version），检查 `turn_id` 递增、`turn_count` 正确、日志不混行。

# Task Dependencies
- Task 2 依赖 Task 1（memory 同步口径先统一）
- Task 5 依赖 Task 1-4

