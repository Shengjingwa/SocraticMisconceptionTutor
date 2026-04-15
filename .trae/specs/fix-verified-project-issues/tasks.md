# Tasks

- [ ] Task 1: 修复严重问题 (Critical Issues) - 架构、日志与实验公平性
  - [ ] SubTask 1.1: **修复 Baseline 公平性 (A1)**。在 `src/tutor_graph.py` 中为 `baseline_node` 创建独立的 `generate_baseline_reply` 逻辑，只提供通用的“物理助教”系统提示词，**绝不**注入 `knowledge_chunks` 中的 FSM 策略和具体迷思概念细节。
  - [ ] SubTask 1.2: **修复日志追加污染 (C2)**。在 `src/simulator.py` 入口处（如 `main()` 中）加入清理 `logs/turn_logs.jsonl` 和 `logs/session_summary.jsonl` 旧数据的逻辑，保证每次批量仿真的数据纯净。
  - [ ] SubTask 1.3: **修复样本极少与对抗模拟 (E1 & E2)**。将 `src/simulator.py` 中的 `num_runs` 默认值提高（如 3）。在 `data/simulation_profiles.json` 中删除“必须至少尝试一次索要答案或跑题”等强制对抗指令。

- [ ] Task 2: 修复中等问题 (Moderate Issues) - 护栏、指标与降级策略
  - [ ] SubTask 2.1: **修复降级策略运算符优先级 (P5)**。在 `src/generator.py` 中将 `decision.state == "S5" and memory.recent_states.count("S5") >= 3 or sentiment == "焦虑/挫败"` 修改为明确的括号优先级 `(decision.state == "S5" and memory.recent_states.count("S5") >= 3) or sentiment == "焦虑/挫败"`。
  - [ ] SubTask 2.2: **修复护栏盲区与语义矛盾 (A2 & Guardrail Gap)**。在 `src/tutor_graph.py` 中修正 `is_already_safe` 为 `not decision.need_guardrail`。在 `src/guardrails.py` 的 `check_output` 中，若 `misconception` 为空，使用一个通用的物理题答案泄露判断 Prompt，不直接返回安全。
  - [ ] SubTask 2.3: **修复评估指标定义缺陷 (V1)**。在 `src/evaluator.py` 中，`Identification Accuracy` 的分母应为“所有执行了分类的轮次总数”（不仅是分类非 Unknown 的轮次）。`Transition Success Rate` 修改为仅当 `decision.state` 为目标状态且不为 "Unknown" 时才计为分子，或根据有效推进轮次重新定义。

- [ ] Task 3: 修复轻微问题 (Minor Issues) - 正则、死代码与文档漂移
  - [ ] SubTask 3.1: **修复正则过度清理 (C5)**。在 `src/generator.py` 的 `_clean_reply` 中，移除 `re.sub(r'[（\(].*?[）\)]', '', text)`，以保护物理公式。
  - [ ] SubTask 3.2: **修复不可达死分支 (A3)**。在 `src/tutor_graph.py` 中，清理多余的不可达图分支或将 `route_after_generate` 中的硬编码 `guardrail` 修正为条件返回（若当前直接进入 `END` 或 `finalize` 则正确路由）。
  - [ ] SubTask 3.3: **修复入口漂移 (Documentation Drift)**。在 `src/main.py` 底部，将默认执行的方法从 `demo()` 修改为交互式的 `chat()`，使其与文档中的“体验 Demo”描述保持一致。

# Task Dependencies
- Task 1, 2, 3 可以并行交由子代理处理。
- 所有修复需确保核心运行链路（`tests/simple_test.py`、`tests/import_smoke_test.py` 和 `src/simulator.py`）不发生崩溃。