# Enhance Chapter 04 Implementation Details Spec

## Why
根据用户的深度评析，`/docs/Chapter04.tex` 在“实现”环节（特别是 4.5 节及其他相关小节）存在内容完备性缺失和行文质感上的问题。需要补充大模型基座选型、核心提示词模板示例、结合教材的物理情境、状态转换的判定机制透明化、防物理知识幻觉机制（如 RAG），并将 4.6 节的朴素案例展示升级为混合维度的时序分析表，以提升教育学毕业论文“设计与实现章”的说服力和学术调性。

## What Changes
- **4.5 节开头补充基座选型**：简要交代技术平台（如使用的具体大模型 API）、前后端交互方式（如基于 Web 的交互架构）。
- **4.5.x 补充 Prompt 示例**：加入一段核心的结构化系统提示词（System Prompt）示例片段，展示如何控制大模型遵循苏格拉底式提问。
- **4.2.1 节增强情境落地感**：扩展表 4.1 或补充文本，将干瘪的迷思话语绑定到具体的初中物理教材（如人教版）章节或经典易错题实验情境中。
- **4.5.2 节澄清状态判定机制**：补充说明状态（如 S3 到 S4）是如何由模型结合对话历史和小 Prompt 自动判定的（Transition Evaluation）。
- **4.3.2/4.5 节强调防幻觉（Fact Grounding）**：着重说明系统如何通过挂载外部本地物理教材库（RAG 机制）或特定审查机制，确保 S7 等阶段提供的物理原理和公式百分之百准确。
- **4.6 节案例呈现升级**：将原本单一的纯文本对话剧本，改写/重新排版为“混合维度的时序分析图/表”（或带有详细状态/置信度标注的结构），左侧对话，右侧或旁注展示后台状态流转与诊断指标。

## Impact
- Affected specs: Chapter 04 implementation and design documentation.
- Affected code: `/workspace/docs/Chapter04.tex`

## ADDED Requirements
### Requirement: Implementation Transparency
The system SHALL document the specific LLM foundation model used, provide examples of the core System Prompts, and explain the dynamic state transition evaluation mechanism.

#### Scenario: Reviewer checking implementation details
- **WHEN** a reviewer reads Section 4.5
- **THEN** they find concrete engineering details (model choice, prompt examples, transition logic) that substantiate the theoretical design, grounding the system as a real, implemented prototype rather than just a concept.

## MODIFIED Requirements
### Requirement: Case Study Presentation
Section 4.6 MUST present dialogue cases not merely as raw transcripts, but as multi-dimensional temporal analyses that juxtapose student-system interaction with backend cognitive state tracking and FSM transitions.

## REMOVED Requirements
None.
