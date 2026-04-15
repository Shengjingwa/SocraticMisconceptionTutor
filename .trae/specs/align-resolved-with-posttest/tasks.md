# Tasks
- [x] Task 1: 梳理现有 resolved 判定链路与依赖点
  - [x] 定位 `resolved_flag` 生成位置（会话内存、日志写入、termination_reason）
  - [x] 梳理 `verify_post_test` 的调用条件与输入依赖（state/cognitive_state/confidence/messages）
- [x] Task 2: 实现统一的 post-test 驱动 resolved 判定
  - [x] 将 resolved 的触发条件从“必须 S6”调整为“post-test 通过即可”
  - [x] 保持对 FSM/FSM+Guardrail 的行为兼容（不改变其主要路由，仅调整验收门槛）
- [x] Task 3: 为 Baseline 增加最小收口（触发 post-test）
  - [x] 定义触发点（例如接近 max_turns 或检测到掌握信号）
  - [x] 生成 1 条简短、可解析的 post-test prompt（要求学生解释机制而非只给结论）
  - [x] 将 post-test 的通过/失败写入 session_summary 的字段与终止原因
- [x] Task 4: 更新 evaluator 输出口径
  - [x] 确保 `Cognitive Correction Rate` 基于新 `resolved_flag`
  - [x] 如需兼容论文呈现，新增/保留“旧口径/过程质量”字段（可选，需在 spec 执行时决定）
- [x] Task 5: 回归验证（最小实验）
  - [x] `python -m py_compile src/*.py`
  - [x] `SIMULATION_SMOKE=1 python src/experiment_suite.py --runs 1 --no-judge`（仅验证流水线不报错、resolved 可产生）

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 2
- Task 5 depends on Task 2, Task 3, Task 4
