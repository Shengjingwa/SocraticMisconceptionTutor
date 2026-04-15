# 修复脚本执行时的模块导入路径 Spec

## Why
用户在项目根目录执行 `python src/simulator.py` 时触发 `ModuleNotFoundError: No module named 'graph'`，说明当前工程的模块导入路径在不同执行方式/工作目录下不稳定，导致仿真与简单测试无法可靠运行。

## What Changes
- 统一并加固脚本入口的导入路径初始化：确保以 `python src/*.py` 方式运行时，`src/` 目录始终可被解析为顶层模块搜索路径。
- 规范项目内模块导入口径：将 `src/` 内部相互引用的导入方式统一为“可在脚本模式与模块模式下均可工作”的写法（必要时提供兼容层）。
- 增加最小化可重复的 Smoke Test：在无有效 LLM Key 场景下仍能跑通 1 个最小 session（Mock/Fallback），并验证不会出现 `ModuleNotFoundError`。
- **BREAKING（可选）**：若选择把 `src` 标准化为 Python package 并要求使用 `python -m src.simulator`，则需要更新运行文档与 CI 命令；默认优先保持 `python src/simulator.py` 可用，不做破坏性变更。

## Impact
- Affected specs: 本地运行可靠性、仿真可执行性、开发者体验（“一条命令跑起来”）
- Affected code: `src/simulator.py`, `src/main.py`, `src/graph.py`（以及 `src/` 下被脚本入口直接 import 的其他模块）

## ADDED Requirements
### Requirement: 脚本入口的导入路径稳定
系统 SHALL 在项目根目录执行 `python src/simulator.py` 时成功启动，且不会因模块导入失败而崩溃。

#### Scenario: 根目录执行仿真脚本
- **WHEN** 用户在项目根目录运行 `python src/simulator.py`
- **THEN** 程序成功进入仿真主流程（至少完成初始化与 1 轮对话/Mock 回合），并且不出现 `ModuleNotFoundError: No module named ...`

### Requirement: 最小可运行测试
系统 SHALL 提供一个无需有效 LLM Key 也能运行的最小 Smoke Test，用于验证核心导入链路与主流程可用。

#### Scenario: 无 API Key 环境的最小测试
- **WHEN** 未设置（或设置为无效）LLM API Key，运行最小 Smoke Test
- **THEN** 测试用例能正常完成，并输出明确的“走 fallback/mock”标志，同时不出现导入错误

## MODIFIED Requirements
### Requirement: 项目内模块导入一致性
项目内部（`src/` 下）模块互相引用时，SHALL 使用统一的导入策略，避免依赖“当前工作目录”或“偶然存在的 sys.path”。

## REMOVED Requirements
无

