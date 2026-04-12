# Resolve LLM Homogeneity Spec

## Why
当前系统在评估过程中存在“三重 LLM 同源问题”：SimulatedStudent（模拟学生）、SocraticTutorApp（教学系统）和 LLM Judge 均使用 `deepseek-chat`。这会导致系统性高估（因为它们有相同的生成风格和理解偏好），削弱了评估的客观性。
为解决此问题，需要将 `SimulatedStudent` 和教学系统（分类、路由生成、护栏等）切换为使用 `qwen-plus`（注：当前阿里云主流模型为 `qwen-plus` 或 `qwen-max`，用户提到 `qwen3.6-plus`，将配置为相应的 Qwen 模型）；而 `LLM Judge` 使用 `deepseek-v3` (或用户提及的 `deepseek-v3.2` 对应版本)。所有模型均通过阿里云百炼 API 访问，并开启思考过程（`enable_thinking` 或其等效配置，如兼容时传参）。

## What Changes
- 修改 `src/config.py`，将统一的单模型配置拆分为“教学系统/模拟器模型”和“Judge 模型”。
- 调整基础 URL（BASE_URL）为阿里云百炼 API 地址（`https://dashscope.aliyuncs.com/compatible-mode/v1`）。
- 更改模型标识符：教学系统使用 `qwen-plus`（或最新的 qwen 版本），Judge 使用 `deepseek-v3`。
- 在 `ChatOpenAI` 初始化时，加入针对阿里云百炼支持的特殊参数（如支持的话，配置思考过程或通过 prompt 促使思考）。
- 修改 `main.py`, `simulator.py`, `llm_judge.py`, `guardrails.py`, `classifiers.py` 等文件中对 LLM 的初始化逻辑，确保它们引用正确的专属配置。
- **BREAKING**: 环境变量 `DEEPSEEK_API_KEY` 应更名为通用的 `DASHSCOPE_API_KEY`（或阿里云百炼对应的 API Key 环境变量）。

## Impact
- Affected specs: 评估指标可能会发生显著变化（由于打破了同源偏好）。
- Affected code: `src/config.py`, 各个涉及 LLM 实例化的业务模块。

## ADDED Requirements
### Requirement: 异源模型评估
The system SHALL provide 使用不同基座模型分别扮演学生、教师和裁判的能力。

#### Scenario: 运行评估
- **WHEN** 运行 `simulator.py` 和 `llm_judge.py` 时
- **THEN** 教师和学生间的交互通过 Qwen API 产生，而裁判打分通过 DeepSeek API 产生，两者均通过阿里云百炼统一接入，并启用深度思考。

## MODIFIED Requirements
### Requirement: LLM 初始化
由原先的统一初始化改为分别初始化。增加对阿里云百炼 API 兼容模式的支持。
