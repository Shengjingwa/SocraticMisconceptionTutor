# SocraticMisconceptionTutor Code Wiki

本 Wiki 面向“读代码/做复现/做二次开发”的需求，按 **架构 → 模块 → API → 数据与产物 → 运行方式** 的顺序组织。

详细文档存放于 `docs/code-wiki/` 目录下：

- [1. 项目总览](file:///workspace/docs/code-wiki/01_overview.md)
- [2. 整体架构](file:///workspace/docs/code-wiki/02_architecture.md)
- [3. 模块说明](file:///workspace/docs/code-wiki/03_modules.md)
- [4. 关键类与函数](file:///workspace/docs/code-wiki/04_key_apis.md)
- [5. 数据、日志与评估产物](file:///workspace/docs/code-wiki/05_data_outputs.md)
- [6. 运行与复现](file:///workspace/docs/code-wiki/06_running.md)
- [7. 依赖与调用关系图](file:///workspace/docs/code-wiki/07_dependency_graph.md)

## 项目结构
```text
src/             核心逻辑（工作流编排、分类、FSM、生成、护栏、仿真、评估）
data/            静态数据（迷思概念库、知识块、学生画像）
logs/            运行日志（jsonl/json + app.log）
results/         评估输出（csv）
experiments/     实验数据及归档（archive/ 下存放历史运行记录）
docs/            文档，主要包含代码百科 (code-wiki/)
ThesisProposal/  学位论文的 LaTeX 源码、各章节 (Chapters/) 及参考文献
pyproject.toml   项目配置文件（Ruff / Pytest 等）
```

