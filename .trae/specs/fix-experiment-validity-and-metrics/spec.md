# Fix Experiment Validity and Metrics Spec

## Why
根据对 `results/summary_metrics.csv` 和 `logs/turn_logs.jsonl` 等实验数据的深入分析，虽然之前的优化改善了认知纠正率和交互轮数，但系统目前存在四个全新的、甚至致命的问题：
1. **消融实验失效**：`simulator.py` 中传入的 `system_version` （如 Baseline, FSM, FSM+Guardrail）仅用于打日志，并没有真正传递给底层的 LangGraph（`app_graph`），导致所有版本实际上都在运行全量的 FSM+Guardrail 逻辑。这使得实验指标差异仅仅是随机波动。
2. **护栏拦截率与拒绝成功率假象**：日志中几乎没有触发 `Direct_Answer_Seek` 意图，导致计算“拒绝成功率”时分母为 0，进而代码默认返回 0.0%。这掩盖了护栏逻辑其实未被有效调用的问题。
3. **缺乏对抗性测试用例**：学生模拟器（`SimulatedStudent`）的 Prompt 设定过于单一，缺乏“向老师直接索要答案”或“偏离物理话题”等对抗性行为，无法压力测试安全护栏（Guardrail）。
4. **防死循环策略导致的生硬跳转**：在 `router.py` 中，如果学生连续 3 次卡在 `S5` 状态（支架引导），系统会强行跳转到 `S6`（验证加深），这违背了教学逻辑。如果学生困惑，系统应该退回 `S4`（认知冲突）或保持 `S5` 提供更多不同角度的支架，而不是强行逼迫学生验证。

## What Changes
- **修复消融实验的参数传递**：修改 `src/state.py`，在 `GraphState` 中增加 `system_version` 字段。并在 `src/main.py` 中将该字段传递给 `app_graph.invoke`。
- **在图的执行节点中生效消融逻辑**：
  - 修改 `src/graph.py` 中的节点和条件边逻辑：如果 `system_version == "Baseline"`，则跳过状态机的决策逻辑，直接使用 `baseline_node` 生成回复；如果 `system_version == "FSM"`，则跳过 `guardrail_node` 等安全拦截机制。
- **增强学生模拟器的对抗性**：修改 `src/simulator.py` 中的系统提示词，随机赋予学生“懒惰索要答案”或“容易跑题”的隐藏属性，以激发并测试 Guardrail。
- **优化防死循环逻辑**：修改 `src/router.py` 中的启发式规则。如果学生在 `S5` 连续卡壳多次，应将其重定向至 `S4` 重新引发认知冲突，或使用不同的类比策略，而不是生硬跳转到 `S6`。

## Impact
- Affected specs: 修复基础消融实验的有效性；提升护栏机制的测试覆盖率；优化苏格拉底教学的状态机流转。
- Affected code: `src/state.py`, `src/main.py`, `src/graph.py`, `src/simulator.py`, `src/router.py`

## MODIFIED Requirements
### Requirement: 有效的消融实验
- **WHEN** `simulator.py` 传入不同的 `system_version` (如 "Baseline", "FSM", "FSM+Guardrail")
- **THEN** 底层的状态图（Graph）必须动态绕过或激活对应的功能模块（决策路由、安全护栏等），从而产生真实的指标差异。

### Requirement: 柔性防卡死教学流转
- **WHEN** 学生在 `S5` (Scaffolding_Guidance) 状态连续卡壳（>=3次）
- **THEN** 路由机制应将其回退至 `S4` (Cognitive_Conflict) 以重新寻找认知矛盾，或尝试全新的类比支架，严禁强制跃迁至 `S6`。