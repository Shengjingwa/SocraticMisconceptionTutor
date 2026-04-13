# Tasks

- [ ] Task 1: 移除 OpenRouter 并统一使用 DashScope 模型配置
  - [ ] SubTask 1.1: 审查 `src/config.py`，移除 `OPENROUTER_API_KEY` 的读取以及 `openrouter_llm` 的实例化逻辑。
  - [ ] SubTask 1.2: 移除 `get_tutor_llm()` 中的 `.with_fallbacks([dashscope_llm])`，使其仅返回 `dashscope_llm`。
  - [ ] SubTask 1.3: 将 `TUTOR_MODEL` 的默认值修改为 `qwen3.6-plus`，将 `JUDGE_MODEL` 的默认值修改为 `deepseek-v3.2`。
  - [ ] SubTask 1.4: 审查 `tests/simple_test.py` 等测试文件，移除任何与 OpenRouter 有关的环境变量（如 `os.environ["OPENROUTER_API_KEY"]`），确保纯环境变量加载，无明文遗留。

- [ ] Task 2: 执行基本功能测试并验证纯 DashScope 链路
  - [ ] SubTask 2.1: 在终端中 export 用户提供的 `DASHSCOPE_API_KEY`。
  - [ ] SubTask 2.2: 执行 `tests/simple_test.py`，确认新的模型组合（`qwen3.6-plus` 和 `deepseek-v3.2`）能够通过 API 成功完成一轮正常的交互和评估生成。

# Task Dependencies
- Task 2 依赖于 Task 1 的配置正确性。