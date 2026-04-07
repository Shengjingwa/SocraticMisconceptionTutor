# Tasks

- [x] Task 1: 准备依赖和配置
  - [x] SubTask 1.1: 安装 `langgraph`、`langchain-openai`、`pydantic` 等必须的 Python 包。
  - [x] SubTask 1.2: 在系统中支持并加载 `DEEPSEEK_API_KEY` 等必要的环境变量，用于调用 DeepSeek 3.2 API。

- [x] Task 2: 定义 LangGraph 状态管理 (`src/state.py`)
  - [x] SubTask 2.1: 基于 `TypedDict` 或 Pydantic 定义 `GraphState`，包含原始的 `SessionMemory`、当前对话轮次的用户输入 (`user_input`)、分类结果 (`perception`)、决策状态 (`decision`)、生成的回复 (`generation`) 及护栏检查结果 (`guardrail_result`)。

- [x] Task 3: 升级 NLU 模块 (`src/classifiers.py`)
  - [x] SubTask 3.1: 移除硬编码的正则表达式和关键词匹配逻辑。
  - [x] SubTask 3.2: 接入 DeepSeek 3.2 (通过 `ChatOpenAI` 客户端适配 DeepSeek 接口)，并利用结构化输出 (Structured Output) 提取意图 (Intent)、错误概念 (Misconception) 和认知状态 (Cognitive State)。

- [x] Task 4: 升级 NLG 模块 (`src/generator.py`)
  - [x] SubTask 4.1: 保留 `assembled_prompt` 结构，将其转换为 LangChain 的 `SystemMessage` 和 `HumanMessage` 组合。
  - [x] SubTask 4.2: 移除 `strategy_templates.json` 的字符串拼接，调用 DeepSeek 3.2 API 生成动态且连贯的苏格拉底式回复。

- [x] Task 5: 升级路由与护栏机制适配 Graph
  - [x] SubTask 5.1: 修改 `router.py`，将原有的状态机决策树改造为可供 LangGraph 使用的逻辑或节点。
  - [x] SubTask 5.2: 将 `guardrails.py` 改造为 LangGraph 节点，返回是否触发拦截的状态以便条件边处理。

- [x] Task 6: 构建 LangGraph 编排 (`src/graph.py`)
  - [x] SubTask 6.1: 实例化 `StateGraph`，注册 `classify_node`、`route_node`、`generate_node`、`guardrail_node` 等节点。
  - [x] SubTask 6.2: 配置条件边 (Conditional Edges)。重点实现：当护栏被触发时，流转回生成节点并使用安全策略 (S2) 进行重试；正常情况则结束本轮。
  - [x] SubTask 6.3: 编译并导出可运行的 Graph 实例。

- [x] Task 7: 重构主应用入口 (`src/main.py`)
  - [x] SubTask 7.1: 修改 `SocraticTutorApp.step` 方法，不再顺序调用模块，而是调用 `graph.invoke()` 执行图。
  - [x] SubTask 7.2: 确保日志系统 (`logger.py`) 能够从新的 GraphState 中正确提取所需数据并记录。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1, Task 2]
- [Task 4] depends on [Task 1, Task 2]
- [Task 5] depends on [Task 2]
- [Task 6] depends on [Task 2, Task 3, Task 4, Task 5]
- [Task 7] depends on [Task 6]