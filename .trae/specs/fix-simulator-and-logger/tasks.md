# Tasks

- [x] Task 1: 修复 `SocraticTutorApp` 实例化参数错误
  - [x] SubTask 1.1: 打开 `src/simulator.py`。
  - [x] SubTask 1.2: 定位到 `run_simulation()` 中 `app = SocraticTutorApp(session_id=session_id, system_version=v)` 这行代码。
  - [x] SubTask 1.3: 将其修改为 `app = SocraticTutorApp(session_id=session_id)`。
  - [x] SubTask 1.4: 随后在下一行添加属性赋值 `app.system_version = v`，以满足日志统计记录版本号的需求。

- [x] Task 2: 补齐 `SessionLogger` 缺失的方法
  - [x] SubTask 2.1: 打开 `src/logger.py`。
  - [x] SubTask 2.2: 在 `SessionLogger` 类中增加 `warning(self, msg: str)` 和 `error(self, msg: str)` 两个方法。可以简单地将这些信息 `print` 到控制台，或者追加到日志记录中（例如：`print(f"[WARNING] {msg}")` / `print(f"[ERROR] {msg}")`）。

# Task Dependencies
- 这两个 Task 互相独立，可以由 Sub-Agent 并行修复。
- [Task 1] 修复 `TypeError`。
- [Task 2] 修复 `AttributeError`。