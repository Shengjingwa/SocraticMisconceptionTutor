# 解决核心指标异常与护栏过度拦截 Spec

## Why
根据最新的实验日志和代码库审查，系统在 FSM+Guardrail 版本中出现了“认知纠正率（Cognitive Correction Rate）跌至 0%”的核心指标异常。同时，在教学对话中暴露了护栏过度拦截以及由于 API 模型配置错误（如 404 和 402）导致的系统崩溃问题。虽然上一轮已实装了 LLM Judge 的豁免规则和降级干预策略，但底层的 API 调用失败掩盖了这些修复的实际效果。为了恢复系统的教学有效性并确保评价指标能够真实反映系统表现，需要修复这些根本问题。

## What Changes
- **修复 API 配置错误**：更新 `src/config.py` 和测试脚本中使用的硬编码模型名称（如不存在的 `qwen3.6-plus` 或 `deepseek-v3.2`）为真实可用的模型名称，并移除无效的明文 API Key，改用纯环境变量加载。
- **优化认知纠正率评价逻辑**：当前认知纠正率仅依赖 NLU 对状态 `S6` 的单方面判定，缺乏教后测（Post-test）的验证。为了提高指标效度，增加学生通过自身语言解释概念的验证环节，确保认知纠正的真实性。
- **完善护栏的动态退避机制**：在 `guardrails.py` 或相关路由逻辑中，引入当护栏连续多次触发时的动态退避机制，允许系统在极度僵局时适度放宽拦截标准，避免陷入“模板化反问”的死循环。

## Impact
- Affected specs: 评价指标逻辑、系统可靠性、对话生成策略、护栏拦截机制。
- Affected code: `src/config.py`, `src/main.py`, `src/evaluator.py`, `tests/simple_test.py`, `src/guardrails.py`

## ADDED Requirements
### Requirement: 动态护栏退避机制
系统 SHALL 在护栏连续拦截多次（如超过 3 次）时，触发动态退避，暂时放宽判定标准，允许提供更直接的提示，以打破教学死锁。

#### Scenario: 护栏连续触发导致死锁
- **WHEN** LLM Judge 连续 3 次拦截助教回复。
- **THEN** 护栏模块降低判定敏感度，或直接交由降级干预策略接管，输出包含基础事实的引导回复。

## MODIFIED Requirements
### Requirement: 认知纠正率评价标准
系统的 `resolved` 状态判定 SHALL 不仅依赖 NLU 分类为 `S6`，还需增加独立的教后测验证机制，确认学生已用自己的语言正确解释了核心概念。

## REMOVED Requirements
### Requirement: 硬编码备用 API Key
**Reason**: 存在安全风险且导致 402 额度耗尽错误。
**Migration**: 移除代码中的所有明文 API Key，强制依赖环境变量 `DASHSCOPE_API_KEY` 等注入。