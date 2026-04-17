# Tasks
- [ ] Task 1: 补充 4.5 节开头核心环境与大模型基座选型。交代使用的大模型基座及前后端交互方式，补充物理系统架构图占位符 `\begin{figure}`（如果尚未存在）及引用。
- [ ] Task 2: 在 4.5.3 节（或 4.5 节适当位置）补充核心系统提示词（System Prompt）的结构化示例片段（如：“你现在的角色是物理苏格拉底助教，当前学生处于 S4 阶段，你必须遵守以下约定……”），以增强说服力。
- [ ] Task 3: 扩展 4.2.1 节（表 4.1 或文本），将干瘪的典型话语（如“越深浮力越大”）绑定至具体的初中物理教材（如人教版第八章）或具体例题/实验情境中，提升学科味。
- [ ] Task 4: 在 4.5.2 节（教学阶段推进逻辑）用文本澄清“状态转换的判定机制”（Transition Evaluation），解释大模型如何结合对话历史提取意图标签和迷思强度来自动判断阶段切换。
- [ ] Task 5: 在 4.3.2 节及 4.5 实现部分补充“防物理知识幻觉”机制，强调 S7 阶段如何利用外部本地物理教材库（RAG知识库调用机制）确保提供的物理定律绝对准确。
- [ ] Task 6: 优化 4.6 节的案例展示形式，将纯文本对话录升级为混合维度的时序分析表/图形式，增加系统置信度指标变化和负面情绪触发标记点，并在案例末尾或旁侧加上时序分析点评。

# Task Dependencies
- Task 1 to 5 require updating specific subsections in `/workspace/docs/Chapter04.tex` and can be done concurrently.
- Task 6 requires careful restructuring of Section 4.6 to present cases as analytical tables/figures.
