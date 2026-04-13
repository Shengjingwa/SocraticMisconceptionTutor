# Tasks

- [x] Task 1: 优化 `data/misconceptions.json`
  - [x] SubTask 1.1: **重构类比 (Analogies)**。将 `analogies` 数组元素从纯文本字符串转换为包含 `model` (模型), `use_for` (用途), `boundary` (局限性边界声明) 的对象。
  - [x] SubTask 1.2: **重构反例 (Counterexamples)**。将 `counterexamples` 数组元素从纯文本字符串转换为包含 `scenario` (情境), `misconception_prediction` (错误预测), `actual_scientific_outcome` (科学事实), `conflict_focus` (冲突焦点) 的对象，增强归谬法的弹药。
  - [x] SubTask 1.3: **新增推理漏洞 (Reasoning Flaws)**。在每个误概念节点下新增 `reasoning_flaws` 数组，包含 `flaw_type` (漏洞类型) 和 `description` (错因描述)，以支持模型的溯源式共情。

- [x] Task 2: 优化 `data/simulation_profiles.json`
  - [x] SubTask 2.1: **柔性化学生画像**。重构 `P1`（固执型）、`P2`（动摇型）、`P3`（困惑型）的属性，引入 `traits` (认知灵活性、防御性) 和 `dynamic_states` (包含 `fallback_behavior`, `trigger_for_change`, `relaxed_state`)。
  - [x] SubTask 2.2: **调整行为规则**。在 `behavior_rule` 中明确，当遭遇高质量反例或思想实验时，学生应展现出态度软化和顿悟的倾向，而非为了对抗而对抗。

- [x] Task 3: 适配代码以读取新结构（极少量的代码修改）
  - [x] SubTask 3.1: 检查 `src/knowledge_base.py` 或 `src/generator.py` 中解析 `misconceptions.json` 的相关逻辑，确保大模型能够正确提取和拼接新的对象结构（例如，将对象的各个字段拼接成一段格式化的文本注入 Prompt）。

# Task Dependencies
- Task 1 和 Task 2 相对独立，均为数据结构的重构。
- Task 3 依赖 Task 1 和 Task 2 的数据结构确定，需要保证系统能正确读取新格式的 JSON。