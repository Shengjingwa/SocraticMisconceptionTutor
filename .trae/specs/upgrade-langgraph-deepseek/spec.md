# 升级为 LangGraph 编排与 DeepSeek 3.2 语言模型 Spec

## Why
目前系统是一个基于规则和模板的 MVP，使用硬编码的 `if-else` 状态机和正则匹配，缺乏真正的自然语言理解和动态生成能力。引入 LangGraph 可以提供更强大的状态管理和复杂对话流控制能力；引入 DeepSeek 3.2 语言模型可以赋予系统真正的推理、意图识别和符合苏格拉底式教学的动态文本生成能力，从而全面提升智能体的表现。

## What Changes
- 引入 `langgraph` 和相关的 LLM SDK (如 `langchain-openai`)。
- 将当前的 `SessionMemory` 重构为 LangGraph 的 `State` 结构。
- 使用 DeepSeek 3.2 替换 `classifiers.py` 中的正则匹配，实现基于大模型的意图 (Intent) 和迷思概念 (Misconception) 提取。
- 使用 DeepSeek 3.2 替换 `generator.py` 中的模板拼接，利用现有的 `assembled_prompt` 结构生成动态回复。
- 将 `router.py` 中的硬编码路由逻辑重构为 LangGraph 的条件边 (Conditional Edges)。
- 将 `guardrails.py` 的拦截与重试逻辑集成到 LangGraph 的执行流中，作为节点或条件边。
- 在 `main.py` 中编译和调用 LangGraph 编排的执行图。
- **BREAKING**: 系统将从纯本地无网络请求的正则/模板模式，转变为依赖外部网络请求的真实 LLM 驱动模式。需要配置 API Key。

## Impact
- Affected specs: 核心对话编排、自然语言理解 (NLU)、自然语言生成 (NLG)、安全护栏重试机制。
- Affected code: 
  - `src/main.py` (主入口重构为调用 Graph)
  - `src/router.py` (状态管理与路由逻辑)
  - `src/classifiers.py` (分类器)
  - `src/generator.py` (生成器)
  - `src/guardrails.py` (安全护栏)

## ADDED Requirements
### Requirement: 基于 LangGraph 的状态管理与图编排
The system SHALL 提供一个定义明确的 `State` 字典/对象，并使用 LangGraph 的 `StateGraph` 来定义节点 (分类、生成、护栏) 和条件边 (状态流转、护栏拦截重试)。

#### Scenario: Success case
- **WHEN** 用户输入一条消息
- **THEN** LangGraph 按顺序执行分类节点，根据条件边流转至对应的策略节点，再执行生成节点，最后通过护栏节点检查，若安全则返回结果，更新 State。

### Requirement: 接入 DeepSeek 3.2 进行理解与生成
The system SHALL 使用 DeepSeek 3.2 API 进行：
1. 结构化输出：提取用户的意图、认知状态等。
2. 文本生成：根据苏格拉底式 Prompt 组装动态回复。

## MODIFIED Requirements
### Requirement: 苏格拉底式教学流程 (Socratic Tutoring Flow)
将原先 `main.py` 中的线性顺序执行，修改为图 (Graph) 结构的节点流转。保留原有的教学策略状态 (S0-S6)，但其跳转由 LangGraph 控制。

## REMOVED Requirements
### Requirement: 基于正则的分类与基于模板的生成
**Reason**: 静态规则无法处理复杂多变的学生自然语言输入，模板生成过于僵化。
**Migration**: 废弃 `strategy_templates.json` 相关的强拼接逻辑，由 DeepSeek 3.2 动态生成。废弃正则关键词列表，由大模型上下文理解替代。