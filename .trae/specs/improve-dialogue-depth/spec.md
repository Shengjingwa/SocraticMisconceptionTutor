# Improve Dialogue Depth Spec

## Why
根据 `experiment_analysis.md` 报告，目前仿真对话的平均轮数过短（约 1.4 轮），且认知纠正率偏低（16%）。原因在于系统的退出条件过于宽松（一旦判定进入 S6 状态便立即结束对话，导致学生甚至来不及回答老师的验证问题），并且学生模拟器的性格设定中缺乏足够的“探索与坚持”动机。这违背了苏格拉底对话“深入追问、制造冲突、引导重构”的渐进式教育理念。

## What Changes
- **修复主程序的早退逻辑**：在 `src/main.py` 中，将 `understanding_verified` 的判定条件从单纯的 `decision.state == "S6"` 修改为：必须在上一轮已经是 `S6`（老师已经提出了验证问题），且当前轮次学生的认知状态（`perception.cognitive_state`）被判定为 `"概念掌握验证"` 时，才认为真正解决了迷思并结束对话。
- **延长仿真对话的最大轮次**：在 `src/simulator.py` 中将 `max_turns` 增加（如从 6 调整到 10），给予对话更充分的展开空间。
- **强化模拟器 Prompt 的“抗引导性”**：修改 `src/simulator.py` 中的系统提示词，要求学生模拟器“必须通过具体的物理证据或逻辑推导才能被说服，不要盲目附和老师”，从而模拟更真实的认知冲突过程。

## Impact
- Affected specs: 提升仿真实验的平均对话轮数，改善对话深度，进而提高系统的认知纠正率，验证复杂认知脚手架策略的有效性。
- Affected code: `src/main.py`, `src/simulator.py`

## MODIFIED Requirements
### Requirement: 苏格拉底式对话的完整闭环
- **WHEN** 系统通过状态机路由到达 `S6` 状态，并向学生抛出验证性提问（如要求学生解释原因或提供反例预测）
- **THEN** 系统不能立刻判定会话已解决（Resolved）。必须等待下一轮学生的回复，且该回复被 NLU 模块判定为真正掌握了概念（即 `cognitive_state == "概念掌握验证"`），会话才被标记为成功解决。
