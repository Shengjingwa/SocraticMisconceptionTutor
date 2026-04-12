# Tasks
- [x] Task 1: 更新配置文件 `config.py`
  - [x] SubTask 1.1: 将基础 URL 更改为阿里云百炼兼容 API `https://dashscope.aliyuncs.com/compatible-mode/v1`。
  - [x] SubTask 1.2: 添加 `DASHSCOPE_API_KEY` 环境变量读取。
  - [x] SubTask 1.3: 分别定义 `TUTOR_MODEL = "qwen-plus"`（教学系统和模拟学生）和 `JUDGE_MODEL = "deepseek-v3"`（裁判）。
  - [x] SubTask 1.4: 增加或预留思考参数配置的支持（阿里云百炼模型可能无需特殊参数，或者可将 `enable_thinking` / `thinking` 等传递给额外参数 kwargs）。

- [x] Task 2: 改造各模块的 LLM 初始化
  - [x] SubTask 2.1: 在 `src/classifiers.py`, `src/generator.py`, `src/guardrails.py` 以及 `src/main.py` (如果有直接初始化) 中，将模型指定为 `TUTOR_MODEL`。
  - [x] SubTask 2.2: 在 `src/simulator.py` 中，将模拟学生的 LLM 指定为 `TUTOR_MODEL`。
  - [x] SubTask 2.3: 在 `src/llm_judge.py` 中，将裁判的 LLM 指定为 `JUDGE_MODEL`。

- [x] Task 3: 适配阿里云百炼的参数要求
  - [x] SubTask 3.1: 确保 `ChatOpenAI` 实例在创建时能正确传递鉴权 Header 和所需的模型标识。
