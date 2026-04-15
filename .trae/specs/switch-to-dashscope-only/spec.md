# 切换为纯 DashScope 模型调用 Spec

## Why
用户希望简化并统一模型调用路径：所有大语言模型统一通过阿里云 DashScope (百炼) API 进行调用，彻底舍弃之前的 OpenRouter 调用及回退（Fallback）机制。同时，要求指定默认使用的模型名称（Qwen 模型为 `qwen3.6-plus`，DeepSeek 裁判模型为 `deepseek-v3.2`），并且严格禁止在代码中遗留任何明文 API 密钥，纯粹通过环境变量进行加载。

## What Changes
- 修改 `src/config.py`，移除 `get_tutor_llm()` 中关于 OpenRouter 及其 `with_fallbacks` 的链式回退逻辑，仅保留单一的 DashScope 模型调用。
- 将 `TUTOR_MODEL` 的默认值修改为 `qwen3.6-plus`，`JUDGE_MODEL` 的默认值修改为 `deepseek-v3.2`。
- 清理 `tests/simple_test.py` 和 `src/config.py` 中残留的 OpenRouter 相关配置项和硬编码。
- 使用指定的 `DASHSCOPE_API_KEY` 运行测试，确保调整后的纯 DashScope 链路能够正常跑通。

## Impact
- Affected specs: 模型调用策略、环境变量依赖、默认模型配置。
- Affected code: `src/config.py`, `tests/simple_test.py`

## ADDED Requirements
### Requirement: 纯 DashScope 模型调用
系统 SHALL 仅通过 DashScope 平台发起 LLM API 调用，不再依赖任何第三方中转（如 OpenRouter）或配置回退链路。

#### Scenario: 模型调用成功
- **WHEN** 配置了有效的 `DASHSCOPE_API_KEY`
- **THEN** 助教模型使用 `qwen3.6-plus` 生成回复，裁判模型使用 `deepseek-v3.2` 进行验证。

## MODIFIED Requirements
### Requirement: 默认模型名称变更
`TUTOR_MODEL` 默认值 SHALL 变更为 `qwen3.6-plus`；`JUDGE_MODEL` 默认值 SHALL 变更为 `deepseek-v3.2`。

## REMOVED Requirements
### Requirement: OpenRouter 调用与回退机制
**Reason**: 用户要求简化架构，统一在 DashScope 调用。
**Migration**: 移除 `src/config.py` 中关于 `ChatOpenAI(base_url="https://openrouter.ai/api/v1")` 的实例化与 `.with_fallbacks` 逻辑。