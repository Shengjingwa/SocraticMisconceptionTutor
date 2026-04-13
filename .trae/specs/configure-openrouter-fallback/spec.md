# 配置 OpenRouter 优先回退至 DashScope Spec

## Why
为了优化 API 调用成本并提升系统的健壮性，用户希望优先使用 OpenRouter 提供的免费模型 `qwen/qwen3.6-plus:free` 进行助教交互生成。如果该模型因限流或其他原因调用失败，则系统应当平滑回退（Fallback）到 DashScope 的 `qwen-plus` 模型。与此同时，所有的 API 密钥都必须严格通过纯环境变量加载，避免任何硬编码风险。DeepSeek 模型的使用保持不变。

## What Changes
- 修改 `src/config.py`，更新 `get_tutor_llm()` 方法以构造 OpenRouter 模型（优先），并通过 Langchain 的 `with_fallbacks` 机制链式回退至 DashScope 模型。
- 确保 `OPENROUTER_API_KEY`、`DASHSCOPE_API_KEY`、`DEEPSEEK_API_KEY` 纯通过 `os.environ.get()` 加载。
- 进行一次快速的 Smoke Test 以验证模型切换和调用功能。

## Impact
- Affected specs: 模型调用策略、环境变量依赖、回退机制。
- Affected code: `src/config.py`, `tests/simple_test.py`

## ADDED Requirements
### Requirement: 优先使用 OpenRouter 且具备回退能力
系统 SHALL 优先尝试调用 `qwen/qwen3.6-plus:free`（基于 OpenRouter），若失败则自动回退至 DashScope 模型。

#### Scenario: 成功调用与自动回退
- **WHEN** OpenRouter 正常可用时
- **THEN** 系统使用 `qwen/qwen3.6-plus:free` 响应。
- **WHEN** OpenRouter 触发限流或失败时
- **THEN** 自动回退使用 `qwen-plus` (DashScope)。

## MODIFIED Requirements
### Requirement: 纯环境变量加载
所有的 API Key SHALL 纯粹通过环境变量获取，不保留任何明文默认值。

## REMOVED Requirements
无