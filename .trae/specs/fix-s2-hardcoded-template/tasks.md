# Tasks
- [x] Task 1: 移除 `generator.py` 中的硬编码拦截模板
  - [x] SubTask 1.1: 在 `src/generator.py` 中，移除 `if decision.need_guardrail or decision.state == "S2":` 语句块直接 `return` 模板回复的代码。
  - [x] SubTask 1.2: 保留 `REFUSAL_REDIRECT_TEMPLATES` 供极少数场景下（如 LLM 请求崩溃）作为兜底使用，或将其合并到最终的 `except Exception` 兜底处理中。

- [x] Task 2: 为 `S2` 状态增加专门的系统指令
  - [x] SubTask 2.1: 在 `src/generator.py` 构建 `messages` 时，如果 `decision.state == "S2"` 或 `decision.need_guardrail`，则向 `messages` 中追加一条强指令（例如：“【重定向指令】学生刚刚试图直接索要答案或偏离主题。请用自然、委婉的口吻拒绝直接给出结论，或将话题拉回当前的物理讨论，并提出一个简单的引导问题。”）。
  - [x] SubTask 2.2: 确保该逻辑与情感支架（Empathy Scaffolding）能够共同作用，即如果学生情绪为“焦虑/挫败”，大模型能同时看到“情感支架”和“重定向指令”。
