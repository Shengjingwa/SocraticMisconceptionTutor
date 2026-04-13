# Implement Concurrent Simulation Spec

## Why
目前 `simulator.py` 在运行批量仿真时是完全串行执行的。考虑到我们在系统中启用了具有深度思考能力（Deep Thinking）的大模型，并且使用了包含分类、路由、生成、护栏的多节点工作流，单轮对话的耗时可能长达数分钟，导致整个测试可能需要耗费数小时才能完成。引入并发仿真（Concurrent Simulation）机制，可以通过参数控制最大并发数，大幅度压缩实验时间。

## What Changes
- 在配置文件中引入仿真并发数超参数 `SIMULATION_CONCURRENCY`。
- 将 `src/simulator.py` 中的 `SimulatedStudent.reply` 方法改造或新增异步版本 `areply`，以便利用大模型异步 API `ainvoke`。
- 将 `run_simulation` 函数的核心循环改造为基于 `asyncio` 的并发任务。
- 利用 `asyncio.Semaphore` 来限制最大并发量，防止 API 速率受限或内存爆炸。

## Impact
- Affected specs: 无
- Affected code: `src/config.py`, `src/simulator.py`

## ADDED Requirements
### Requirement: 并发批量仿真能力
The system SHALL provide 利用协程池进行并发仿真的能力，以缩短评估所需的时间。

#### Scenario: 成功开启并发仿真
- **WHEN** 用户执行 `python src/simulator.py`
- **THEN** 系统会根据设定的超参数同时发起多个会话（Session）的仿真测试，并输出进度和结果。
