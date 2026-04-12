# Tasks
- [x] Task 1: 修复 `src/graph.py` 中的状态机路由顺序。
  - [x] SubTask 1.1: 移除原有的 `route_to_next` 条件边（`"route" -> "guardrail" | "generate"`）。
  - [x] SubTask 1.2: 新增 `route_after_route(state: GraphState) -> str`，根据 `system_version` 决定是跳往 `baseline` 还是 `generate`。
  - [x] SubTask 1.3: 新增 `route_after_generate(state: GraphState) -> str`，在 `system_version == "FSM+Guardrail"` 且 `regeneration_required` 时流转至 `guardrail`，否则至 `END`。
  - [x] SubTask 1.4: 新增 `route_after_guardrail(state: GraphState) -> str`，如果 `regeneration_required` 为 `True`，则返回 `generate`，否则返回 `END`。
  - [x] SubTask 1.5: 重新配置 `workflow.add_conditional_edges`，将逻辑串联为 `route -> generate -> guardrail -> generate`。

- [x] Task 2: 增强护栏拦截和分类风险标记。
  - [x] SubTask 2.1: 在 `src/classifiers.py` 中，修改 `risk_flag` 逻辑，将 `result.intent == "Off_Topic"` 也纳入 `True` 的条件。
  - [x] SubTask 2.2: 在 `src/graph.py` 的 `guardrail_node` 中，当 `guardrail_result.get("answer_leakage_flag", False)` 为 `True` 时，无论是否 `is_already_safe`，都要强制返回 `regeneration_required: True`。

# Task Dependencies
- Task 2 depends on Task 1
