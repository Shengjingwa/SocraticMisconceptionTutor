# Tasks

- [x] Task 1: 将 FSM 状态传递给护栏系统
  - [x] SubTask 1.1: 在 `src/guardrails.py` 中更新 `apply_guardrails` 和 `check_output` 函数的签名，增加一个默认为 `"S0"` 的 `current_state` 字符串参数。
  - [x] SubTask 1.2: 在 `src/tutor_graph.py` 中的 `guardrail_node` 函数里，将当前的 FSM 状态（`decision.state`）作为 `current_state` 参数传递给 `apply_guardrails` 的调用。

- [x] Task 2: 基于状态的弹性护栏 Prompt 注入
  - [x] SubTask 2.1: 在 `src/guardrails.py` 的 `check_output` 函数中，根据 `current_state` 动态构建 `extra_instruction`。
  - [x] SubTask 2.2: 如果 `current_state` 在 `["S2", "S4"]` 中，注入【严格模式】提示词，强调绝对禁止提供任何实质性的正确答案或完整解题步骤。
  - [x] SubTask 2.3: 如果 `current_state` 为 `"S5"` 且连续触发护栏（`consecutive_triggers >= 2`），注入【弹性模式】提示词，大幅放宽判定标准，允许助教给出较多的知识铺垫和部分推导过程。
  - [x] SubTask 2.4: 确保这部分 `extra_instruction` 能够被正确拼接进最终发送给 LLM Judge 的 `judge_prompt` 中。

- [x] Task 3: 运行简单测试验证
  - [x] SubTask 3.1: 导入环境变量 `DASHSCOPE_API_KEY`，运行 `tests/simple_test.py`。
  - [x] SubTask 3.2: 确认系统能正常运行，没有抛出参数不匹配或其他运行时异常。

# Task Dependencies
- Task 2 依赖 Task 1 的参数传递。
- Task 3 依赖前两个任务的代码修改。