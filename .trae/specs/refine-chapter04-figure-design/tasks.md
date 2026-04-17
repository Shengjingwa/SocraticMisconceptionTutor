# Tasks
- [x] Task 1: 解析当前文档与项目核心逻辑
  - [x] 仔细阅读 `docs/Chapter04.tex` 中关于图 1 至图 6 附近的文字描述（包括 S0-S8、防环规则、双向拦截等）。
  - [x] 结合 `src/router.py`、`src/guardrails.py` 和知识图谱设计，明确每个状态和控制流的确切技术条件与中英文字段。
- [x] Task 2: 细化图 1 (迷思概念图谱化表征) 和 图 2 (对话架构)
  - [x] 图 1：扩展为树状图谱的实体属性说明，明确给出 `浮力`、`电学` 两个主题的节点实例与关联类型（如 `has_misconception`、`triggered_by`）。
  - [x] 图 2：补充 5 层架构的具体组件，细化数据流箭头，加入如 `LLM`、`Vector DB`、`Prompt Template` 等技术底层支撑元素。
- [x] Task 3: 细化图 3 (阶段化控制流) 和 图 4 (诊断—干预闭环)
  - [x] 图 3：设计双轨状态机（T1-T5 主线与 G1-G4 分支），补充各阶段的转移条件（如 `confidence > 0.8`，`sentiment == "焦虑/挫败"`，`loop_count >= 2`）。
  - [x] 图 4：构建 6 大模块的环形交互，补充各模块间的通信载荷（如 `JSON: {topic, misconception, certainty}`，`State Context`）。
- [x] Task 4: 细化图 5 (知识策略映射) 和 图 6 (系统化防卸载机制)
  - [x] 图 5：将知识库调用设计为动态决策树，细化“高置信”、“低置信回退”及“异常终止”的判断分支逻辑与对应模板。
  - [x] 图 6：设计“漏斗机制+UI”对比图，细化 4 重约束的拦截逻辑（生成前、生成中、生成后审查的 LLM Judge 逻辑）与学生端 UI 的关键视觉元素。
- [x] Task 5: 整合并输出最终设计文档
  - [x] 将所有精修后的方案写入 `/workspace/docs/Chapter04_Figure_Design.md`，确保结构清晰，直接可供绘图人员操作。

# Task Dependencies
- Task 2、Task 3、Task 4 均依赖 Task 1 的信息解析。
- Task 5 依赖 Task 2-4 的输出结果。
