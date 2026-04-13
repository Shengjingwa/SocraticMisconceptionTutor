# Tasks
- [ ] Task 1: 修复 API 模型配置与硬编码密钥
  - [ ] SubTask 1.1: 更新 `src/config.py` 中的默认模型名称为真实可用的（例如 `qwen-plus`, `deepseek-chat`）。
  - [ ] SubTask 1.2: 移除 `tests/simple_test.py` 中所有硬编码的明文 API Key，改用 `os.environ.get()`，并在缺失时抛出 `ValueError`。
  - [ ] SubTask 1.3: 更新 `Code_Wiki.md` 中关于模型配置的文档说明。

- [ ] Task 2: 引入护栏动态退避机制
  - [ ] SubTask 2.1: 在 `src/guardrails.py` 的 `check_output` 逻辑中，增加对护栏连续触发次数的追踪。
  - [ ] SubTask 2.2: 当护栏连续拦截达到阈值（如 3 次）时，实施动态退避，放宽判定规则（例如，暂时允许给出更多提示），以打破对话死循环。

- [ ] Task 3: 优化认知纠正率的评价逻辑
  - [ ] SubTask 3.1: 在 `src/main.py` 或相关路由模块中，重构 `resolved` 判定标准。
  - [ ] SubTask 3.2: 引入“教后测”机制，即在系统到达 `S6` 状态时，要求学生用自己的话解释原理，只有通过独立判定后，才将 `resolved` 设为 `True`。

- [ ] Task 4: 验证系统表现
  - [ ] SubTask 4.1: 运行单元测试（如 `tests/simple_test.py` 或 `tests/import_smoke_test.py`），确保系统不会因为 API 错误或逻辑修改而崩溃。

# Task Dependencies
- Task 2 和 Task 3 相互独立，可并行开发。
- Task 4 依赖前三个任务的完成。