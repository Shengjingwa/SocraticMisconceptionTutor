# Fix API and Prompt Leaks Spec

## Why
本地测试运行结果表明存在两个主要问题：
1. `src/classifiers.py` 和 `src/guardrails.py` 在使用 LangChain 的 `with_structured_output` 默认（`json_schema`）时，由于 DeepSeek API 不支持此 `response_format`，引发了 HTTP 400 报错并触发原始回退解析（Raw Parsing），导致大量警告日志。
2. 审计结果发现，在生成回复时（`src/generator.py`），模型直接将提示词中的教学术语或支架内容生硬地拼接到输出中，如“先给你一个小支架：”或“如果你愿意，可以顺便检查这个情况：”，导致教学体验不自然，存在明显的提示词泄露。

## What Changes
- **修改分类器和护栏的结构化输出方式**：将 `with_structured_output` 的 `method` 参数从默认的 `json_schema` 更改为其他兼容的方式（例如 `json_mode` 或纯粹通过提示词结合 JSON 解析器）。
- **优化回复生成的系统提示词**：在 `src/generator.py` 的 `system_prompt` 护栏规则中明确禁止暴露教学术语（如“反例”、“类比”、“知识点”、“支架”等），要求模型将这些内容自然地融入对话，不要使用生硬的引导语。

## Impact
- Affected specs: 提升系统稳定性、减少 NLU 解析错误日志；提升教育对话的自然度和沉浸感。
- Affected code: `src/classifiers.py`, `src/guardrails.py`, `src/generator.py`

## MODIFIED Requirements
### Requirement: 稳定的自然语言理解与护栏解析
- **WHEN** 调用 DeepSeek 的 API 进行结构化输出时
- **THEN** 系统应使用与 DeepSeek 兼容的方法（如 `method="json_mode"` 或 `PydanticOutputParser`），确保不再出现 HTTP 400 Bad Request 错误。

### Requirement: 沉浸式与自然的苏格拉底式对话
- **WHEN** 生成回复使用“反例”或“类比”策略时
- **THEN** 回复中不得包含“小支架”、“顺便检查这个情况”、“采用的引导策略”等生硬的元语篇标记，必须完全自然地通过提问的方式融入对话语境中。
