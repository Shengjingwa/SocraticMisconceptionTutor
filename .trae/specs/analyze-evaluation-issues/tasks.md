# Tasks
- [ ] Task 1: 验证 `system_comprehensive_evaluation.md` 提到的问题
  - [ ] SubTask 1.1: 验证“上下文记忆丢失”问题是否真实存在（检查大模型调用时的 history_messages 构建逻辑）。
  - [ ] SubTask 1.2: 验证“安全护栏脆弱”问题是否依然存在（检查是否已经有 LLM Judge 机制，或依然纯依赖正则）。
  - [ ] SubTask 1.3: 验证“状态机流转逻辑硬编码”问题是否真实存在（检查 `router.py`）。
  - [ ] SubTask 1.4: 验证“NLU 解析与降级策略鲁棒性”问题（检查 `classifiers.py`）。
- [ ] Task 2: 制定短中长期改进方案
  - [ ] SubTask 2.1: 整理验证结果，编写一份包含短期（易实现的修复）、中期（架构重构）、长期（深度教育学引入）的改进方案总结，并直接输出给用户。
