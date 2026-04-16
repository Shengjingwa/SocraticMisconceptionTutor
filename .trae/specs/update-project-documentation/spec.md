# 项目文档更新 Spec

## Why
当前仓库在近期迭代中新增/强化了若干关键能力与使用方式（如一键实验套件脚本 `experiment_suite.py`、`LOG_DIR/RESULTS_DIR` 可配置输出路径、P1 强制结案与澄清话术优化等）。需要全面阅读项目并同步更新 `/workspace/README.md`、`/workspace/CODE_WIKI.md` 与 `/workspace/docs` 下的 Code Wiki 文档，使其与最新代码与实验产物结构一致，便于复现与二次开发。

## What Changes
- 更新 [README.md](file:///workspace/README.md)：补充“一键跑实验套件”与产物目录结构说明，并补齐与代码一致的可选环境变量（如 `LOG_DIR` / `RESULTS_DIR` / `EXP_*`）。
- 更新 [CODE_WIKI.md](file:///workspace/CODE_WIKI.md)：补充索引信息与快速导航。
- 更新 [docs/code-wiki](file:///workspace/docs/code-wiki)：
  - 运行文档补充 `src/experiment_suite.py` 的使用方式与输出结构
  - 数据产物文档补充 `experiments/suite_*` 的目录结构与聚合输出
  - 模块与架构文档补充“实验套件编排”和“近期路由/澄清机制”的定位说明（保持简洁，不引入过度细节）
- **不修改业务代码逻辑，仅更新文档**。

## Impact
- Affected specs: 文档与复现说明
- Affected code: 无（仅改动 Markdown 文档）

## ADDED Requirements
### Requirement: Documentation Alignment
文档应与当前仓库代码一致，包含实验运行入口、环境变量、日志/产物结构与主要模块定位信息。

#### Scenario: Success case
- **WHEN** 用户根据 README 或 Code Wiki 操作
- **THEN** 能够一键跑实验、定位日志与指标产物，并顺利理解主要模块职责与入口路径

