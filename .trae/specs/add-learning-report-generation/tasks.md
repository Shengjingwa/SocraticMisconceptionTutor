# Tasks
- [ ] Task 1: 编写生成报告的大模型函数
  - [ ] SubTask 1.1: 在 `src/generator.py` 中新增 `generate_learning_report(memory: SessionMemory)` 函数。
  - [ ] SubTask 1.2: 设计系统提示词，要求模型根据传入的 `memory.history_summary` 或历史消息，以 Markdown 格式输出三点内容：1. 本次暴露的误概念；2. 纠正过程简述；3. 后续学习建议。
  - [ ] SubTask 1.3: 调用配置好的 `ChatOpenAI` 执行生成。

- [ ] Task 2: 集成至主循环与测试验证
  - [ ] SubTask 2.1: 在 `src/main.py` 的 `_process_graph_result` 中，若 `understanding_verified` 为真且之前未生成过报告，则调用 `generate_learning_report`。
  - [ ] SubTask 2.2: 将生成的报告内容作为 `report` 字段加入到 `return_dict` 中，并在 `demo` 模式的控制台高亮打印输出。
  - [ ] SubTask 2.3: 编写/更新一个简单的测试脚本 `tests/test_learning_report.py`，使用指定的百炼 API Key 强制模拟一次解决的对话，确保学情报告正确生成。