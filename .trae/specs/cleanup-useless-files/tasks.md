# Tasks
- [x] Task 1: 扫描并识别项目中的无用文件
  - [x] SubTask 1.1: 检查根目录及各子目录，列出临时测试文件（如 `test_serde.py` 等非核心测试脚本）。
  - [x] SubTask 1.2: 检查 `logs/` 目录，列出过期的旧日志文件。
- [x] Task 2: 删除无用文件
  - [x] SubTask 2.1: 使用代理删除识别出的冗余脚本文件和过期日志文件。
- [x] Task 3: 验证核心功能
  - [x] SubTask 3.1: 运行核心测试（如 `tests/simple_test.py`），确保清理未影响项目正常运行。