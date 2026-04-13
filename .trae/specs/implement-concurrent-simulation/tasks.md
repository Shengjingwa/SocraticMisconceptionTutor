# Tasks
- [x] Task 1: 增加并发配置参数
  - [x] SubTask 1.1: 在 `src/config.py` 中添加 `SIMULATION_CONCURRENCY = int(os.environ.get("SIMULATION_CONCURRENCY", "5"))`。

- [x] Task 2: 改造模拟学生支持异步调用
  - [x] SubTask 2.1: 在 `src/simulator.py` 的 `SimulatedStudent` 类中，新增 `areply` 异步方法，内部调用 `self.llm.ainvoke(messages)`。

- [x] Task 3: 重构仿真运行流程
  - [x] SubTask 3.1: 在 `src/simulator.py` 中，抽离出 `run_single_session(v, m, p, r, sem)` 的异步协程函数，该函数使用 `app.astep()` 和 `student.areply()` 执行单场会话。
  - [x] SubTask 3.2: 将 `run_simulation` 改造为使用 `asyncio.gather` 收集并执行所有的单场会话任务，并通过 `asyncio.Semaphore(config.SIMULATION_CONCURRENCY)` 控制最大并发数。
  - [x] SubTask 3.3: 在 `__main__` 块中使用 `asyncio.run(run_simulation())` 启动脚本。
