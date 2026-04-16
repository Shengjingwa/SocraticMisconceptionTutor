# Tasks
- [x] Task 1: 检查 Git 状态并提交当前更改
  - [x] 查看当前 Git 分支状态 (`git status`, `git branch`)。
  - [x] 提交所有关于 `Chapter04.tex`、`refs.bib` 以及 spec 文件的修改。
  - [x] 切换至 `main` 分支并将修改合并，然后推送到远程（如果有的话，或确保合并至本地 `main`）。
- [x] Task 2: 提取第四章所有占位图片信息
  - [x] 使用 `grep` 工具查找 `/workspace/docs/Chapter04.tex` 中的所有 `\begin{figure}` 环境及其 `\caption` 和 `\label`。
  - [x] 分析每张图片的上下文段落，提取出该图需要表达的核心逻辑（模块构成、状态流转、系统闭环等）。
- [x] Task 3: 编写图片绘制详细方案文档
  - [x] 在 `/workspace/docs/Chapter04_Figure_Design.md` 文件中，为提取出的每张图片设计具体的绘制方案。
  - [x] 方案内容需包含：图的类型（如流程图、系统架构图）、节点清单、连线与逻辑流向、关键文本标注（须与正文中统一教育化后的术语一致）、布局建议。
- [x] Task 4: 复核与确认
  - [x] 确保方案文档覆盖了所有的图片。
  - [x] 确认方案中的术语（如 `S1 安全护栏检查`，`T1–T5 教学主线`）与 `Chapter04.tex` 精修版完全一致。

# Task Dependencies
- Task 3 依赖于 Task 2。
- Task 1 可以独立并行执行，但建议在任何新代码生成前优先执行以确保工作区干净。
