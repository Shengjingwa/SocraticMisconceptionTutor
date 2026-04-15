# Resolved 指标对齐（Post-test 驱动）Spec

## Why
当前实验中出现“盲评有效性高，但自动 resolved=0（尤其 Baseline）”的矛盾，导致结果口径难以在论文中自洽。需要将 resolved 的判定与“学生是否能用自己的话解释关键机制”的验收更一致，从而让不同版本的结果可解释、可对比。

## What Changes
- 统一将 `resolved_flag` 的核心判据改为“教后测（post-test）通过”
- 为 Baseline 增加最小化的“收口/验收”机制，使其在学生已被说服时能触发 post-test 并被判定 resolved
- 在评估输出中明确区分“对话过程质量（盲评）”与“闭环验收（resolved）”，并确保二者不再结构性冲突
- **BREAKING**：`resolved_flag` 的语义将从“FSM 路由到 S6 且通过阈值”变为“post-test 通过”，历史结果不可直接横向比较

## Impact
- Affected specs: 指标口径、实验可比性、论文叙事一致性
- Affected code:
  - resolved 判定与日志：`src/main.py`（或对应会话处理逻辑）
  - Baseline 收口策略：`src/tutor_graph.py`/`src/generator.py`（或对应 baseline 生成节点）
  - 汇总评估：`src/evaluator.py`

## ADDED Requirements
### Requirement: 统一 resolved 判据
系统 SHALL 在所有版本（Baseline/FSM/FSM+Guardrail）下，用同一套 post-test 验收逻辑决定 `resolved_flag`。

#### Scenario: 学生达成掌握，判定 resolved
- **WHEN** 系统检测到学生已表现出“概念掌握验证”信号，或会话进入收口阶段触发 post-test
- **AND** 学生对 post-test 的回答通过 `verify_post_test`
- **THEN** 会话 `resolved_flag` 为 true，`termination_reason` 为 resolved

#### Scenario: 未通过验收，不判定 resolved
- **WHEN** 学生无法用自己的话解释机制（仅同意/复读/仍含错误）
- **THEN** 会话不应被标记为 resolved（即使盲评对过程给高分）

### Requirement: Baseline 具备最小收口能力
系统 SHALL 在 Baseline 模式下提供最小化收口步骤，以便在学生已被说服时触发 post-test 并给出 resolved 判定。

#### Scenario: Baseline 收口
- **WHEN** Baseline 会话达到最大轮次前的最后若干轮，或检测到学生已接近掌握
- **THEN** 助教提出 1 个简短的总结/解释型问题（post-test prompt），并据此运行 post-test 验收

## MODIFIED Requirements
### Requirement: 评估输出与论文口径
评估输出 SHALL 明确展示 resolved（post-test）指标，并允许同时保留盲评得分用于过程质量描述，避免将二者混为同一含义。

## REMOVED Requirements
### Requirement: resolved 依赖 S6 状态门槛
**Reason**: 该门槛导致 Baseline 结构性无法 resolved，并造成跨版本不可比。
**Migration**: 将历史结果标记为“旧口径 resolved”，新实验统一使用 post-test 口径重跑。

