# Tasks
- [ ] Task 1: 修复消融实验的参数传递与生效。
  - [ ] SubTask 1.1: 在 `src/state.py` 中的 `GraphState` 类增加 `system_version: str` 字段。
  - [ ] SubTask 1.2: 在 `src/main.py` 的 `SocraticTutorApp.__init__` 接受 `system_version`，并在 `step()` 和 `astep()` 方法的 `initial_state` 字典中传递该字段。
  - [ ] SubTask 1.3: 修改 `src/graph.py`。
    - 在 `route_to_next` 条件边中，如果 `state["system_version"] == "Baseline"`，直接跳转到 `baseline` 节点；如果是 `"FSM"`，跳过 `guardrail` 节点直接到 `generate`；如果是 `"FSM+Guardrail"` 则执行完整流程。
    - 注意：需要确保 `baseline` 节点能正确更新 `GraphState`，以便 `main.py` 能够读取 `decision` 和 `guardrail_result`（可以给个默认值）。

- [ ] Task 2: 增强学生模拟器的对抗性边缘场景。
  - [ ] SubTask 2.1: 在 `src/simulator.py` 中修改 `SimulatedStudent` 的提示词，随机（或明确地在配置中）赋予部分学生“懒惰”或“易分心”属性，例如：“在对话过程中，请至少尝试一次直接向老师索要最终答案，或者扯开话题说你不想学物理了，以测试老师的耐心。”

- [ ] Task 3: 优化防死循环策略导致的生硬跳转。
  - [ ] SubTask 3.1: 在 `src/router.py` 的 `route_state` 函数中，找到类似 `if state == "S5" and 连续 3 次 S5 -> 跳转 S6` 的逻辑。
  - [ ] SubTask 3.2: 将该跳转目标修改为回退到 `"S4"`，重新引发认知冲突。并在 `_choose_strategy` 中，如果发生从 `S5` 回退到 `S4`，选择诸如 `"Consequence_Exploration"` 策略，而不是强制验证。

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 1
