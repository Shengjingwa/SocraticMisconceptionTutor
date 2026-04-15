# Tasks
- [x] Task 1: 复现与定位导入路径问题
  - [x] SubTask 1.1: 在干净环境下分别用 `python src/simulator.py`、`python -m src.simulator`（若可用）复现报错并记录 `sys.path` 差异
  - [x] SubTask 1.2: 盘点 `src/` 内所有顶层导入（例如 `from graph import ...`）并标注哪些在脚本模式下可能失效

- [x] Task 2: 加固脚本入口的导入路径初始化（保持兼容）
  - [x] SubTask 2.1: 在 `src/simulator.py` 等脚本入口（含 `src/main.py`）统一添加最小的路径初始化逻辑，保证 `src/` 在 `sys.path` 中
  - [x] SubTask 2.2: 统一/修正 `src/main.py` 对 `graph` 等模块的导入方式，确保在不同启动方式下都能解析

- [x] Task 3: 规范模块导入口径（可选增强）
  - [x] SubTask 3.1: 评估是否将 `src/` 标准化为 package（增加 `src/__init__.py`）并迁移到 `python -m` 启动
  - [x] SubTask 3.2: 若采取 package 方案，提供对 `python src/*.py` 的兼容（例如保留路径初始化或提供 wrapper）

- [x] Task 4: 增加最小化 Smoke Test 并集成到现有测试入口
  - [x] SubTask 4.1: 新增/补充 1 个无需有效 API Key 的最小测试（mock/fallback），覆盖 `simulator -> main -> graph` 导入链路
  - [x] SubTask 4.2: 在 CI/README（如存在）中补充推荐运行方式与排错指引（仅限必要改动）

- [x] Task 5: 验证
  - [x] SubTask 5.1: 运行 `python src/simulator.py`（最小规模配置）确认不再出现 `ModuleNotFoundError`
  - [x] SubTask 5.2: 运行现有的 `tests/simple_test.py`，确保核心交互仍可用

# Task Dependencies
- Task 2 依赖 Task 1
- Task 4 依赖 Task 2
- Task 5 依赖 Task 2 与 Task 4
