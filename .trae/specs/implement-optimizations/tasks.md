# Tasks
- [x] Task 1: 落实短期优化（工程与算法）
  - [x] SubTask 1.1: 修改 `src/classifiers.py`，在 `system_prompt` 中加入“认知僵局”、“概念掌握验证”等状态的 3-5 个具体 Few-shot 示例，避免因误判导致对话提前结束。
  - [x] SubTask 1.2: 修改 `src/main.py`，在 `SocraticTutorApp` 中新增 `astep(self, user_input: str)` 异步方法，内部调用 `await app_graph.ainvoke(initial_state)`。
- [x] Task 2: 落实中期优化（教育学与策略）
  - [x] SubTask 2.1: 优化 `src/router.py` 中的 `_choose_strategy` 方法。弃用完全随机选择，引入基于历史轮次（`turn_count`）和上一次状态/策略的**启发式动态策略选择**（如在认知冲突状态卡住 2 次后强制使用“提供类比”策略）。
  - [x] SubTask 2.2: 新建 `src/llm_judge.py` 脚本。该脚本应能读取 `logs/turn_logs.jsonl` 和 `logs/session_summary.jsonl`，使用大语言模型（LLM）从“苏格拉底度（1-5）”和“教学有效性（1-5）”两个维度，对历史对话进行后置打分评估，并将结果保存至 `logs/evaluation_results.json`。

# Task Dependencies
- Task 2 depends on Task 1
