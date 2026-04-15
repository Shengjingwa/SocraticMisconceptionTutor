# Tasks
- [ ] Task 1: 优化 LLM Judge 护栏判定标准
  - [ ] SubTask 1.1: 审查并修改 `src/llm_judge.py` 或 `src/guardrails.py` 中的 LLM Judge 提示词，明确“允许提供基础事实/物理定义/客观现象，仅拦截直接给出本题最终结论或代替关键逻辑推导”的豁免标准，防止误伤。
  
- [ ] Task 2: 优化助教生成提示词与降级干预策略
  - [ ] SubTask 2.1: 在 `src/generator.py` 的 `system_prompt` 中，补充应对类比失效的规则：“若学生对当前类比（如水管、跑步等）感到困惑或排斥，必须立即停止类比，改用直观物理现象或拆解后的分步逻辑推导”。
  - [ ] SubTask 2.2: 在 `src/generator.py` 中，针对“焦虑/挫败”情绪或多次卡壳的学生，放宽“绝不直接给结论”的硬性限制，允许助教使用“提供部分直接解释 + 确认理解提问”的降级干预策略。

- [ ] Task 3: 优化拒绝策略模板
  - [ ] SubTask 3.1: 调整 `src/generator.py` 中的 `REFUSAL_REDIRECT_TEMPLATES`（如 `S2` 状态的模板），使其在拒绝直接给答案时更加柔和，并提供更有实质性内容的引导脚手架，而不是空洞的“我们一步一步想”。

- [ ] Task 4: 验证修复效果
  - [ ] SubTask 4.1: 运行 `python tests/import_smoke_test.py` 与 `python tests/simple_test.py`，确保核心链路无语法错误且可正常启动。

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 2
- Task 4 依赖 Task 1, 2, 3
