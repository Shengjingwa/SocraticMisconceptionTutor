# Tasks

- [x] Task 1: 完善 OpenRouter 回退配置与环境变量加载
  - [x] SubTask 1.1: 审查 `src/config.py` 中的 `get_tutor_llm()`，确保 `openrouter_llm` 被配置为使用 `model="qwen/qwen3.6-plus:free"`，基础 URL 为 `https://openrouter.ai/api/v1`，并通过 `.with_fallbacks([dashscope_llm])` 链式回退至 `TUTOR_MODEL` (DashScope)。
  - [x] SubTask 1.2: 审查 `get_judge_llm()`，确保其仅加载 `JUDGE_MODEL`（DeepSeek）且保持不变。
  - [x] SubTask 1.3: 确认 `OPENROUTER_API_KEY`、`DASHSCOPE_API_KEY`、`DEEPSEEK_API_KEY` 在 `src/config.py` 中仅通过 `os.environ.get()` 加载，没有任何硬编码默认值。

- [x] Task 2: 执行基本功能测试
  - [x] SubTask 2.1: 导入环境变量 `DASHSCOPE_API_KEY` 和 `OPENROUTER_API_KEY`，执行 `tests/import_smoke_test.py` 或 `tests/simple_test.py`。
  - [x] SubTask 2.2: 确认模型能在不报错的情况下完成正常的交互与评价生成，从而证明回退链路或 OpenRouter 优先链路能够正确运行。

# Task Dependencies
- Task 2 依赖于 Task 1 的配置正确性。