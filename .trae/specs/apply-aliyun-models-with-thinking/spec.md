# Apply Aliyun Models with Thinking Spec

## Why
为了解决模拟学生、教学系统和 LLM Judge 使用同一 LLM（同源问题）导致的评估偏差，用户决定使用阿里云百炼 API 提供的不同模型：教学系统和模拟学生使用 `qwen3.6-plus`，而 LLM Judge 使用 `deepseek-v3.2`。同时要求所有模型都启用 `enable_thinking` 以提升推理质量，并进行简单验证测试。

## What Changes
- 更新 `src/config.py` 中的默认模型名称为 `qwen3.6-plus` 和 `deepseek-v3.2`。
- 修改 `ChatOpenAI` 初始化逻辑，在各处调用（`main.py`, `simulator.py`, `llm_judge.py`, `classifiers.py`, `generator.py`, `guardrails.py` 等）中传递 `model_kwargs={"enable_thinking": True}`。
- 使用用户提供的 API Key（`sk-6b719e16c7d047b7afaf97bd64b02501`）运行一个简单的测试脚本，确保模型调用正常无报错。

## Impact
- Affected specs: 覆盖并深化之前的 `resolve-llm-homogeneity` 逻辑。
- Affected code: `src/config.py` 以及所有实例化 `ChatOpenAI` 的文件。

## ADDED Requirements
### Requirement: 异构模型与思考能力配置
The system SHALL provide 针对不同角色配置异构模型，并统一开启 `enable_thinking` 的能力。

#### Scenario: 成功开启并运行
- **WHEN** 系统启动且发起 LLM 调用时
- **THEN** 将使用指定的阿里云百炼兼容端点，向对应模型（`qwen3.6-plus` / `deepseek-v3.2`）发送请求，并在参数中携带 `enable_thinking=True`。
