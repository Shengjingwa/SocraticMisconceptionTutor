# Fix Guardrail Routing Spec

## Why
通过分析最新的实验日志（`logs/session_summary.jsonl` 等），我们发现 FSM+Guardrail 版本的表现出现了严重的退化：护栏拦截率和拒绝回答成功率暴跌至 0%。根本原因是 LangGraph 中的执行顺序配置错误：护栏节点（`guardrail`）被错误地放置在了生成节点（`generate`）之前。由于尝试读取尚未生成的 `generation` 字段，导致 `KeyError` 并引发全局异常，系统直接返回了错误提示，从而完全绕过了安全护栏。此外，分类器对 `Off_Topic` 意图未标记为高风险，导致系统未能及时将其引导回物理学习。

## What Changes
- **修复状态图路由逻辑**：重构 `src/graph.py` 中的边（edges），将执行顺序修改为 `route -> generate -> guardrail -> generate(if retry)`。
- **增强风险检测拦截**：修改 `src/classifiers.py`，将 `Off_Topic` 意图也纳入 `risk_flag=True` 的范围。
- **强化护栏重试判断**：在 `guardrail_node` 中，当发生答案泄露（`answer_leakage_flag = True`）时，即使当前状态是安全的（`S2`），也要强制触发重新生成。

## Impact
- Affected specs: 恢复 FSM+Guardrail 模型的安全护栏拦截率与教学成功率，杜绝全局 KeyError 异常。
- Affected code: `src/graph.py`, `src/classifiers.py`

## MODIFIED Requirements
### Requirement: 教师回复生成与护栏后置检查
- **WHEN** 生成节点（`generate`）产出对话回复后
- **THEN** 如果系统版本启用了护栏（`FSM+Guardrail`），图流程必须先流转至护栏节点（`guardrail`）进行内容审核。若审核发现直接给出了答案或脱离了主题，必须更新策略状态并要求系统重新生成回复。

### Requirement: 闲聊与偏题识别
- **WHEN** 学生的输入被分类器识别为 `Off_Topic` 意图时
- **THEN** 分类器必须同时将 `risk_flag` 置为 `True`，以便路由层将其分配至 `S2`（拒绝与引导）状态。