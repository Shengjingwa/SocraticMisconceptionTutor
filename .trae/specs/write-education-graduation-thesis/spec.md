# Write Education Graduation Thesis Spec

## Why
目前项目的所有核心功能（基于 LangGraph 的 FSM + 护栏多智能体架构）已经开发完毕，消融实验（Baseline vs FSM vs FSM+Guardrail）的数据也已收集齐全。系统的最终指标展示出了非常经典的“教学有效性与安全性”的权衡（Trade-off），且攻克了针对 P1（固执型）学生的“事实兜底”难题。项目具备了成为一篇高质量教育科技方向（AIED）硕士毕业论文的所有条件。用户决定停止代码修改，开始根据当前项目撰写教育学毕业论文。

## What Changes
- [新建] 创建一份完整的教育学毕业论文文档（例如 `thesis/graduation_thesis.md`），或者按章节分为多个文档。
- 论文结构需包含：
  - **摘要与绪论**：研究背景、问题提出、研究意义。
  - **文献综述与理论基础**：概念转变理论（Conceptual Change Theory）、苏格拉底教学法、大模型在教育中的应用及挑战（幻觉与直接给答案）。
  - **系统架构与方法论**：基于有限状态机（FSM）的认知状态流转建模、教学逻辑护栏（Pedagogical Guardrails）、针对不同学生画像（P1-P3）的自适应动态策略（如 S8 熔断与事实兜底）。
  - **实验设计与结果分析**：消融实验设置（Baseline vs FSM vs FSM+Guardrail），核心指标对比（认知纠错率、平均轮次、泄题率），案例分析（Case Study）。
  - **讨论与展望**：硬护栏带来的教学连贯性折损、未来向“柔性护栏”演进的思考、多模态事实接入的展望。
  - **结论**。

## Impact
- Affected specs: 无。
- Affected code: 无（仅生成文档）。

## ADDED Requirements
### Requirement: 毕业论文撰写
系统应能够全面总结当前代码库的架构、实验数据和之前的分析报告，提炼出具有高学术价值的观点，输出一份格式规范、逻辑严密、学术用语标准的教育学方向毕业论文草稿。

#### Scenario: Success case
- **WHEN** 用户要求基于当前项目写论文
- **THEN** 在 `thesis/` 目录下生成一份完整的 markdown 格式毕业论文，覆盖所有标准学术章节，准确引用了最新的实验数据。