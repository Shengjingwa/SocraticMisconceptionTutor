# Tasks
- [x] Task 1: 更新配置文件 `config.py`
  - [x] SubTask 1.1: 将 `TUTOR_MODEL` 的默认值修改为 `"qwen3.6-plus"`。
  - [x] SubTask 1.2: 将 `JUDGE_MODEL` 的默认值修改为 `"deepseek-v3.2"`。
  - [x] SubTask 1.3: 增加或修改 `DEFAULT_LLM_KWARGS` 以包含 `{"enable_thinking": True}`。

- [x] Task 2: 改造各模块的 LLM 初始化以支持思考参数
  - [x] SubTask 2.1: 在 `src/classifiers.py`, `src/generator.py`, `src/guardrails.py`, `src/main.py`, `src/simulator.py`, `src/llm_judge.py` 中，确保在实例化 `ChatOpenAI` 时传入 `model_kwargs=config.DEFAULT_LLM_KWARGS`（或直接传递 `model_kwargs={"enable_thinking": True}`）。

- [x] Task 3: 运行简单测试验证
  - [x] SubTask 3.1: 编写或使用现有的简单测试脚本（如 `tests/run_simple_test.py`）。
  - [x] SubTask 3.2: 注入用户提供的 API Key，执行测试，确保模型调用能够成功返回结果且无 `APIError`。
