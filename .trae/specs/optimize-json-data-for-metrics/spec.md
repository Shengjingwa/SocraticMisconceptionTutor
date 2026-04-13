# 优化 JSON 数据提升核心指标 Spec

## Why
根据前期的评估结果与日志分析，FSM+Guardrail 系统在教学质量上受到“机械共情”、“类比死锁”以及“对抗模拟偏差”的制约。为了在不修改核心代码逻辑的前提下大幅提升认知纠正率和教学有效性，必须对底层驱动大模型的 JSON 数据进行深度重构。精简并结构化类比边界、丰富极端反例、注入推理漏洞分析，以及松绑模拟学生画像，是改变模型上下文输入、触发其深层教学能力的根本途径。

## What Changes
- **重构 `misconceptions.json`**：
  - 将原有的 `analogies` 字符串数组升级为包含 `model`, `use_for`, `boundary` 的对象数组，明确类比失效边界，打破类比死锁。
  - 将原有的 `counterexamples` 字符串数组升级为包含 `scenario`, `misconception_prediction`, `actual_scientific_outcome`, `conflict_focus` 的对象数组，强化认知冲突的力度。
  - 新增 `reasoning_flaws` 字段，提供错因溯源分析，帮助模型实现精准的认知共情而非机械安慰。
- **松绑 `simulation_profiles.json`**：
  - 将刚性的学生画像（如“固执型”）重构为具备动态转变机制的“条件固执型”，增加 `dynamic_states`（包含 `fallback_behavior`, `trigger_for_change`, `relaxed_state`），使模拟学生在面对高质量的归谬反问时能够自然表现出顿悟和态度软化，从而提高 S6 状态的触发率。
- **同步更新 `knowledge_chunks.json`**（如需）：确保知识切片与重构后的 `misconceptions.json` 保持结构一致。

## Impact
- Affected specs: 知识库数据结构、模拟学生行为逻辑、大模型上下文注入。
- Affected code: `data/misconceptions.json`, `data/simulation_profiles.json` (纯数据文件修改，可能需要极少量的代码适配以兼容新的 JSON 结构，如 `src/knowledge_base.py` 或 `src/generator.py` 中解析 JSON 的部分)。

## ADDED Requirements
### Requirement: 结构化的类比与边界声明
知识库 SHALL 提供带有明确失效边界的类比对象，确保大模型在使用类比时能够及时进行“类比熔断”。

#### Scenario: 助教使用类比解释电流
- **WHEN** 助教提取 `misconceptions.json` 中的水流类比
- **THEN** 助教同时获取并遵循 `boundary` 约束，不为类比的局限性（如漏水）进行辩护。

### Requirement: 动态柔性的模拟学生画像
模拟学生 SHALL 在面对高质量的认知冲突引导时展现出态度转变。

#### Scenario: 固执型学生面对极端反例
- **WHEN** 助教提出无法反驳的极端反例（如串联1000个灯泡）
- **THEN** 固执型学生根据 `trigger_for_change` 规则，态度从抗拒转为困惑或短暂的自我怀疑，推动对话进展。

## MODIFIED Requirements
### Requirement: 认知冲突反例提供
反例数据 SHALL 被结构化为情境、错误预测与科学事实的对比，以增强大模型生成归谬反问的逻辑清晰度。

## REMOVED Requirements
无