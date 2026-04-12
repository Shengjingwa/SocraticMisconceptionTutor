# Tasks
- [ ] Task 1: 增强安全护栏与上下文管理的鲁棒性（短期方案）
  - [x] SubTask 1.1: 在 `src/guardrails.py` 中的 `check_output` 里，为 `structured_llm.invoke` 增加 `@retry` 装饰器，参数与 `config.py` 中的配置一致。
  - [x] SubTask 1.2: 在 `src/generator.py` 和 `src/classifiers.py` 中，当截断历史对话时，如果 `memory.history_summary` 存在且非空，则将其作为早期对话背景附加到 `SystemMessage` 或对话开头，提供全局上下文。

- [x] Task 2: 引入情感分析与共情支架（中期方案 - 情感分析）
  - [x] SubTask 2.1: 在 `src/classifiers.py` 中，为 `NLUOutput` 增加 `sentiment` 字段（枚举：焦虑/挫败、困惑、自信、平静），更新系统 Prompt 让其提取此字段，并更新 `PerceptionResult` 和后备解析逻辑。
  - [x] SubTask 2.2: 在 `src/router.py` 中，更新 `SessionMemory` 或在流转时将 `sentiment` 透传给 `RouteDecision`（可通过 `meta` 字典）。
  - [x] SubTask 2.3: 在 `src/generator.py` 中，如果检测到学生的 `sentiment` 是 `焦虑/挫败` 或 `困惑`，在 `system_prompt` 中追加一条【情感支架】指令，要求大模型在回复开头先用简短的话语共情并鼓励学生。

- [x] Task 3: 声明式状态机重构（中期方案 - 状态机重构）
  - [x] SubTask 3.1: 在 `src/router.py` 中，将硬编码的 `if target == "S4" and memory.recent_states.count("S4") >= 2` 等防死循环和状态转移逻辑，提取为统一的字典配置或独立的验证函数，减少 `route_state` 内部复杂的嵌套判断，使其结构更为清晰、声明式（Declarative）。
