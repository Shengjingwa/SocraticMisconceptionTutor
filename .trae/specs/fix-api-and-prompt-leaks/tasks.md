# Tasks
- [x] Task 1: 修复 API 的 `with_structured_output` 参数，以支持 DeepSeek 模型。
  - [x] SubTask 1.1: 在 `src/classifiers.py` 中将 `llm.with_structured_output(NLUOutput)` 更改为使用 `method="json_mode"` 或者更改提示词使用 `PydanticOutputParser`。若使用 `json_mode`，需在 prompt 中确保包含 "json" 等词汇。
  - [x] SubTask 1.2: 在 `src/guardrails.py` 中将 `llm.with_structured_output(GuardrailOutput)` 更改为使用 `method="json_mode"` 或者更改提示词使用 `PydanticOutputParser`。若使用 `json_mode`，需在 prompt 中确保包含 "json" 等词汇。

- [x] Task 2: 修复 `src/generator.py` 中回复生成的生硬提示词和教学术语泄露问题。
  - [x] SubTask 2.1: 修改 `src/generator.py` 中的 `system_prompt`，在【安全护栏规则】中增加一条禁止暴露“支架”、“反例”、“类比”等教育设计术语的规则。
  - [x] SubTask 2.2: 在 `system_prompt` 中强调，必须将辅助信息自然地转化为口语化对话，避免僵硬地照搬原文或加入明显的元语篇前缀（如“先给你一个小支架：”）。
