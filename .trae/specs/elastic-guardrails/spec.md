# 弹性护栏 (Elastic Guardrails) Spec

## Why
目前系统的护栏机制 (Guardrails) 采用一刀切的判定标准。无论系统处于拒绝直接代答阶段 (S2) 还是支架式引导阶段 (S5)，LLM Judge 都会用同样严格的标准拦截“可能泄露答案”的回复。这导致在 S5 阶段当学生陷入严重僵局时，助教为了绕过护栏只能给出极其隐晦的提示，反而降低了认知纠正率和教学有效性。为了解决这个问题，需要将护栏与 FSM 状态机解耦，实现“弹性伸缩”——在 S2 和 S4 阶段保持绝对严格，在 S5 僵局阶段适度放宽。

## What Changes
- [修改] 更新 `src/guardrails.py`，让护栏检查函数 (`apply_guardrails` 和 `check_output`) 接收当前的 FSM 状态 (`current_state`)。
- [修改] 在 `src/guardrails.py` 的 LLM Judge 提示词中，基于 `current_state` 动态注入不同的判定标准（例如 S2/S4 严格模式，S5 弹性模式）。
- [修改] 更新 `src/tutor_graph.py` 中的 `guardrail_node`，在调用护栏时传入 `decision.state`。

## Impact
- Affected specs: 护栏拦截机制、教学引导策略。
- Affected code: `src/guardrails.py`, `src/tutor_graph.py`

## ADDED Requirements
### Requirement: 基于状态的弹性护栏
系统 SHALL 根据当前的教学状态动态调整护栏的拦截严格度。

#### Scenario: 处于 S5 且陷入僵局
- **WHEN** 当前状态为 S5 (支架引导) 且连续触发护栏拦截
- **THEN** 护栏模块切换为弹性模式，允许助教给出更多知识铺垫和部分推导过程，只要不直接给出最终结论即可。

#### Scenario: 处于 S2 或 S4
- **WHEN** 当前状态为 S2 (拒绝直接代答) 或 S4 (认知冲突)
- **THEN** 护栏模块保持严格模式，绝对禁止提供任何实质性的完整解题步骤。

## MODIFIED Requirements
### Requirement: 护栏拦截判断
LLM Judge 的拦截判断 SHALL 不仅依赖于生成的文本和连续触发次数，还必须参考当前系统所处的 FSM 状态。

## REMOVED Requirements
无