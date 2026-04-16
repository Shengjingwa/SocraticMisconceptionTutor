# Chapter 04 Figures Design & Git Merge Spec

## Why
根据用户的需求，当前需要完成两个核心任务：1) 将近期对 `Chapter04.tex` 和 `refs.bib` 的所有修改提交并合并到 GitHub 的 `main` 分支；2) 为 `Chapter04.tex` 中所有仍是“图待补绘”占位符的图片（如 `fig:misconception-graph` 等）提供详细的绘制方案，并集中输出到一个独立的文件中，以指导后续的绘图工作。

## What Changes
- **Git 操作**：提交当前工作区所有未提交的修改（主要是之前对第四章和参考文献的精修），并确保合并至 `main` 分支。
- **新增文档**：在 `/workspace/docs/` 下新建一个名为 `Chapter04_Figure_Design.md` 的文档。
- **绘制方案设计**：该文档将详细拆解 `Chapter04.tex` 中出现的每一张图片，包括但不限于：
  - 图的类型（流程图、结构图、树状图等）
  - 节点及连接关系（核心模块、数据流向、状态转移）
  - 文本标签建议（与正文完全一致的术语）
  - 视觉排版建议（推荐使用的绘图工具、配色、布局逻辑）

## Impact
- Affected specs: 版本控制规范与配图规范
- Affected code: `/workspace/.git` (状态变更), `/workspace/docs/Chapter04_Figure_Design.md` (新增)

## ADDED Requirements
### Requirement: Detailed Figure Drawing Plans
系统 SHALL 提供针对第四章每张插图的具体视觉与逻辑结构设计方案。

#### Scenario: 绘图者参考方案作图
- **WHEN** 绘图者阅读 `Chapter04_Figure_Design.md`
- **THEN** 能够清楚地知道图中需要包含哪些节点、如何连线、标注什么文本，且术语与正文严格一致。

## MODIFIED Requirements
无。

## REMOVED Requirements
无。
