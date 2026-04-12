# Code Wiki: 面向初中物理的苏格拉底式对话教育智能体

## 1. 项目概述
本项目是一个基于大语言模型（LLM）的**面向初中物理（电学与浮力）的苏格拉底式对话教育智能体（Socratic Tutor Agent）**。系统结合了有限状态机（FSM）与安全护栏（Guardrails），旨在通过提问、类比和认知冲突来引导学生主动思考，帮助学生克服物理学习中的典型迷思概念（Misconceptions），而不是直接给出标准答案。

## 2. 项目整体架构
项目的核心架构基于 **LangGraph** 构建了一个状态流转图（State Graph）。每一次用户输入都会经过一个由四个核心节点组成的流水线，并通过长期记忆（SessionMemory）维护会话上下文：

1. **Classify（自然语言理解）**：解析学生输入的意图、错误概念（Misconception）和当前的认知状态。
2. **Route（路由与状态机）**：基于分类结果和历史状态，决定下一步的教学状态（S0-S6）和具体的教学策略（如：澄清、制造认知冲突、提供类比支架）。
3. **Generate（回复生成）**：结合当前教学状态、策略和预设的物理知识块（反例、类比等）生成引导式回复。
4. **Guardrail（安全护栏）**：检查输入是否包含“直接求答案”等违规意图，并严格校验输出是否“泄漏了最终答案”。如果触发护栏，则会修改状态并触发重新生成（条件边循环）。

## 3. 主要模块职责
代码主要集中在 `src/` 目录下，各个模块分工明确：

- **[src/main.py](file:///workspace/src/main.py)**: **主应用入口**。封装了核心应用类，负责初始化会话记忆，调用 LangGraph 工作流处理单轮对话，并将对话过程记录到日志中。提供交互式的终端聊天循环。
- **[src/graph.py](file:///workspace/src/graph.py)**: **工作流编排**。定义了 LangGraph 的状态图，将具体的处理函数注册为图节点，并定义了节点间的边和条件路由。
- **[src/router.py](file:///workspace/src/router.py)**: **有限状态机与策略大脑**。维护从 `S0`（倾听分析）到 `S6`（验证深化）的教学状态流转，包含防死循环的启发式规则。
- **[src/classifiers.py](file:///workspace/src/classifiers.py)**: **NLU 分类器**。利用 LLM 的结构化输出，将非结构化的学生语言转化为系统可处理的意图、错误概念和认知状态。
- **[src/generator.py](file:///workspace/src/generator.py)**: **提示词组装与生成**。根据路由层决定的策略，从数据文件中提取对应的物理反例、类比支架，动态拼装系统 Prompt 并调用 LLM 生成回复。
- **[src/guardrails.py](file:///workspace/src/guardrails.py)**: **教学安全校验**。实现双重防御机制（规则匹配与 LLM-as-a-Judge），防止直接给出结论或泄露答案。
- **[src/state.py](file:///workspace/src/state.py)**: **状态定义**。定义了 LangGraph 节点间传递的数据结构和会话记忆结构。
- **[src/config.py](file:///workspace/src/config.py)**: **配置管理**。集中管理 LLM 配置（API Key、Base URL）和重试参数。
- **[src/logger.py](file:///workspace/src/logger.py)**: **日志记录**。将会话摘要和单轮对话明细以 JSONL 格式落盘。
- **外围与评估模块**:
  - **[src/simulator.py](file:///workspace/src/simulator.py)**: 利用 LLM 扮演具有特定“错误概念”的虚拟学生，进行自动化批量测试。
  - **[src/evaluator.py](file:///workspace/src/evaluator.py)** & **[src/llm_judge.py](file:///workspace/src/llm_judge.py)**: 解析日志文件，计算状态流转成功率、护栏拦截率等指标，并依靠 LLM 评估对话的“苏格拉底度”。

## 4. 关键类与函数说明

### 核心类
- **`SocraticTutorApp`** ([src/main.py](file:///workspace/src/main.py)): 核心应用类。`step(user_input)` 方法负责驱动整个工作流，并统一处理异常和日志埋点。
- **`GraphState`** ([src/state.py](file:///workspace/src/state.py)): LangGraph 节点间传递数据的 TypedDict，包含用户输入、分类结果、路由状态、生成的回复等信息。
- **`SessionMemory`** ([src/state.py](file:///workspace/src/state.py)): 承载了跨轮次的上下文，包括对话历史、当前识别的物理谬误、最近使用的策略轨迹等。

### 核心函数
- **`classify_input`** ([src/classifiers.py](file:///workspace/src/classifiers.py)): 基于带有 Few-Shot 示例的 Prompt 和 Tenacity 重试机制，调用 LLM 返回结构化的感知结果。
- **`route_state`** ([src/router.py](file:///workspace/src/router.py)): 核心路由函数。根据学生的认知状态，通过状态转移矩阵推导目标状态，并分配具体教学战术（如暴露前提、类比支架）。
- **`generate_response`** ([src/generator.py](file:///workspace/src/generator.py)): 核心生成函数。结合当前状态和物理知识库，生成符合苏格拉底式教学风格的回复。
- **`apply_guardrails`** ([src/guardrails.py](file:///workspace/src/guardrails.py)): 执行护栏校验，返回布尔值及阻断原因，决定是否需要重新生成回复。

## 5. 依赖关系

### 外部依赖
- **LangChain 生态**: `langchain`, `langchain_openai`, `langchain_core`, `langgraph`（核心架构依赖，用于构建 LLM 链和状态图）。
- **Pydantic**: 用于定义 LLM 的结构化输出数据模型（如 NLUOutput, EvaluationOutput）。
- **Tenacity**: 用于处理 LLM 接口调用的自动重试和指数退避（`@retry`）。

### 内部依赖
- **静态数据**: 强依赖 `data/` 目录下的静态数据文件（如 `misconceptions.json`, `knowledge_chunks.json` 等），所有教学引导的物理知识储备均来源于此。
- **环境变量**: 各模块均依赖 `src/config.py` 读取环境变量中的模型配置（默认采用 DeepSeek 体系：`deepseek-chat`）。

## 6. 项目运行方式

### 6.1 环境变量配置
项目强依赖 DeepSeek 的 API。在运行任何脚本前，需在环境变量或终端中设置：
```bash
export DEEPSEEK_API_KEY="你的_API_KEY"
# 可选: 
export LLM_MODEL="deepseek-chat"
```
*(注：如果未配置 API Key，代码中内置了 Mock 机制以防直接崩溃，但会返回预设的测试回复)*

### 6.2 启动交互式对话（测试主程序）
可以通过根目录的测试脚本，或直接运行 main 文件启动控制台聊天交互：
```bash
python test_run.py 
# 或者
python src/main.py
```
这会启动终端的 `学生> ` 交互界面。输入 `exit` 或当系统判定学生已掌握概念时，对话会自动结束。

### 6.3 运行批量自动化仿真测试
用于评估不同策略（Baseline, FSM, FSM+Guardrail）的效果，模拟学生会自动与系统进行对话：
```bash
python src/simulator.py
```

### 6.4 运行结果评估
在积累了 `logs/` 目录下的对话日志后，可执行以下命令生成分析报告（结果将生成到 `results/` 目录下）：
```bash
# 生成指标统计报表 (CSV)
python src/evaluator.py

# 运行大模型作为裁判，评估对话质量
python src/llm_judge.py
```
