# Fix Simulation Concurrency and LangGraph Memory Spec

## Why
当前批量仿真产出的日志与指标存在明显异常：`turn_logs.jsonl` 中 356 条记录的 `turn_id` 全为 0、`session_summary.jsonl` 中 36 个会话的 `turn_count` 全为 0，导致人工抽样表与指标统计口径撕裂（例如 [turn_logs.jsonl](file:///workspace/logs/turn_logs.jsonl)、[session_summary.jsonl](file:///workspace/logs/session_summary.jsonl)、[summary_metrics.csv](file:///workspace/results/summary_metrics.csv)）。同时，并发仿真导致 `pipeline_*.log` 输出混行，且 LangGraph Memory 节点存在就地修改状态对象的风险，会在并发或回放时产生不可预期行为。

## What Changes
- 修复 `turn_id/turn_count` 始终为 0 的数据污染：确保 `SocraticTutorApp` 使用 LangGraph 返回的最新 `memory`，并让 Baseline 也能递增 `turn_count`。
- 修复 `history_summary` 不生效/被覆盖的问题：让摘要更新链路（summarize/finalize → main → router.update_after_turn）保持一致且可追踪。
- 修复并发仿真日志混行：统一由 logging 输出，并为 JSONL 写入增加进程内互斥，避免并发写入造成的潜在行撕裂。
- 修复 LangGraph Memory 节点就地修改 `memory`：在节点内使用 copy-on-write（`model_copy(deep=True)`）返回更新，避免共享引用与竞态。
- 让“外部 LLM 调用失败/欠费”等异常能落到会话级汇总：将其标记为 abnormal，并写入原因，避免实验结果被静默污染。

## Impact
- Affected specs: 批量仿真可复现实验、日志可追溯性、指标统计可信度
- Affected code: `src/main.py`, `src/graph.py`, `src/router.py`, `src/logger.py`, `src/simulator.py`, `src/evaluator.py`

## ADDED Requirements
### Requirement: 可靠的回合计数与日志一致性
系统 SHALL 在任意 `system_version` 下输出正确的 `turn_id`（从 1 递增或从 0 递增但不可恒定）并与会话汇总 `turn_count` 一致。

#### Scenario: 批量仿真结束后检查日志
- **WHEN** 运行 `python src/simulator.py` 完成一轮仿真
- **THEN** `turn_logs.jsonl` 中同一 `session_id` 的 `turn_id` 单调递增，且 `session_summary.jsonl.turn_count` 等于该会话对应 turn 的数量（或最大 turn_id + 1，取决于定义）

### Requirement: 并发下的结构化日志可读性
系统 SHALL 在并发仿真下避免 `print()` 与 console handler 混用造成的混行，并确保 JSONL 记录写入原子性。

#### Scenario: 并发仿真运行中查看 pipeline/app log
- **WHEN** `SIMULATION_CONCURRENCY > 1`
- **THEN** 控制台/`pipeline_*.log` 不出现“半行插入”，每条日志具备可追溯的 `session_id`

### Requirement: LangGraph Memory 的纯增量更新
系统 SHALL 避免在 LangGraph 节点内就地修改传入的 `memory`，并通过返回 `{"memory": new_memory}` 的方式进行状态更新。

#### Scenario: finalize/summarize 更新摘要
- **WHEN** 触发摘要压缩逻辑
- **THEN** `memory.history_summary` 在后续 turn 中可被读取到，并且不会因并发会话产生交叉污染

## MODIFIED Requirements
### Requirement: 会话异常终止标记
系统 SHALL 在检测到关键 LLM 调用失败（如 Arrearage、429、超时）时，将会话标记为 abnormal，并写入 `termination_reason` 便于评估过滤。

## REMOVED Requirements
无

