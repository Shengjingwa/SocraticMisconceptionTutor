# 项目 Code Wiki：苏格拉底式对话教育智能体

## 1. 项目概述
本项目是一个基于大语言模型（LLM）的教育智能体，专门面向初中物理（主要聚焦电学与浮力），采用**苏格拉底式对话**方法进行教学。系统旨在通过引导式提问、制造认知冲突和提供认知支架，帮助学生纠正典型的物理迷思概念（Misconceptions），而不是直接给出标准答案。

核心架构基于 **LangGraph** 实现的状态机（FSM），工作流严格遵循“感知 (Perception) -> 决策 (Decision) -> 生成 (Generation) -> 护栏 (Guardrail)”的流水线设计。系统底层默认调用 DeepSeek 大模型（通过 `langchain_openai`），支持不同版本运行模式（如 Baseline、FSM、FSM+Guardrail）进行消融实验和评估。

## 2. 项目整体架构
系统采用模块化和流水线设计，整个对话处理流程被定义为一个有向图（Graph），具体架构如下：

1. **输入感知 (Perception)**：通过自然语言理解（NLU）模块，利用 LLM 的结构化输出能力，从用户的自然语言输入中提取用户的意图（Intent）、认知状态（Cognitive State）以及具体的错误概念标签（Misconception Tag），并给出置信度。
2. **决策路由 (Decision/Routing)**：基于当前会话状态、历史状态记忆和 NLU 解析结果，决定下一轮教学的干预状态（如 S3: 迷思概念诊断，S4: 认知冲突等）和具体策略（如提供类比支架、澄清等）。
3. **回复生成 (Generation)**：结合状态机的决策指令、策略以及对应的物理知识切片（包含核心知识点、反例、类比等），组装系统 Prompt 并调用 LLM 生成符合苏格拉底式教学风格的回复。
4. **安全护栏 (Guardrail)**：
   - **输入护栏**：防范学生直接索要答案或偏离物理主题。
   - **输出护栏**：防止大模型直接“泄露答案”或代替学生完成逻辑推导。采用正则匹配与 LLM-as-a-Judge 结合的方式，若触发拦截，则通过 LangGraph 的条件边触发重新生成机制。
5. **仿真与评估闭环**：内置基于 LLM 的“模拟学生”模块，能够自动化模拟具有特定迷思概念和性格特征的初中生，与智能体进行批量对话，并自动计算和评估教学有效性、护栏拦截率等核心指标。

## 3. 主要模块职责
代码主要位于 [src/](file:///workspace/src) 目录下：

- [main.py](file:///workspace/src/main.py)：应用的主入口。定义了核心的 `SocraticTutorApp` 类，负责管理会话记忆、调度 LangGraph 工作流、执行日志记录，并提供交互式的终端聊天界面。
- [graph.py](file:///workspace/src/graph.py)：工作流引擎。利用 LangGraph 构建了核心的状态流转图，包含 `classify`、`route`、`generate` 和 `guardrail` 四个核心节点，并配置了条件边（Conditional Edges）以支持护栏拦截时的重试机制。
- [classifiers.py](file:///workspace/src/classifiers.py)：自然语言理解（NLU）模块。调用 LLM 分析用户输入，结构化提取意图、认知状态及错误概念标签，输出 `PerceptionResult`。
- [router.py](file:///workspace/src/router.py)：状态机与决策模块。根据感知结果和会话记忆，执行状态转换逻辑和启发式策略推荐，输出 `RouteDecision`。
- [generator.py](file:///workspace/src/generator.py)：回复生成模块。加载 [data/](file:///workspace/data) 目录中的知识库和错误概念数据，根据决策策略组装 Prompt，生成启发式回复。
- [guardrails.py](file:///workspace/src/guardrails.py)：安全护栏模块。负责输入与输出的双向检测，确保生成的回复符合“不直接给答案”的教学规则。
- [simulator.py](file:///workspace/src/simulator.py)：仿真实验模块。利用 LLM 扮演具有特定错误概念和性格的“模拟初中生”，与智能体进行批量对话对弈，生成实验日志。
- [evaluator.py](file:///workspace/src/evaluator.py)：客观指标评估模块。解析仿真实验生成的日志，计算迷思概念识别准确率、认知纠正率、护栏拦截率等核心指标，并输出 CSV 报告。
- [llm_judge.py](file:///workspace/src/llm_judge.py)：主观评估模块。利用 LLM-as-a-Judge 评估对话的“苏格拉底度”和“教学有效性”。
- [state.py](file:///workspace/src/state.py)：定义了 LangGraph 全局数据状态 `GraphState` 的数据结构。
- [logger.py](file:///workspace/src/logger.py)：日志记录模块，负责将会话详情和轮次数据记录到 [logs/](file:///workspace/logs) 目录下的 JSONL 文件中。
- [config.py](file:///workspace/src/config.py)：全局配置文件，包括 LLM 的 API Key、Base URL、模型名称以及重试策略等。

## 4. 关键类与函数说明

### 4.1 核心类
- **`SocraticTutorApp`** ([main.py](file:///workspace/src/main.py#L23))：智能体会话管理核心类。`step()` 和 `astep()` 方法用于执行单轮的状态图调用。
- **`SimulatedStudent`** ([simulator.py](file:///workspace/src/simulator.py#L11))：封装了模拟初中生人格的 Prompt 和对话逻辑，用于自动化仿真对弈。
- **`SessionMemory`** ([router.py](file:///workspace/src/router.py#L14))：用于存储当前会话的历史消息、主题、当前状态、错误概念以及近期使用的策略。

### 4.2 核心函数与实例
- **`app_graph`** ([graph.py](file:///workspace/src/graph.py#L94))：编译后的 LangGraph 状态图实例，是串联各个子模块的处理中枢。
- **`classify_input`** ([classifiers.py](file:///workspace/src/classifiers.py#L36))：调用 LLM 的 `with_structured_output` 提取信息，返回 `PerceptionResult`。
- **`route_state`** ([router.py](file:///workspace/src/router.py#L99))：执行状态流转和反死循环（Anti-loop heuristics）逻辑，返回 `RouteDecision` 决策信息。
- **`generate_reply`** ([generator.py](file:///workspace/src/generator.py#L45))：根据路由结果和本地知识切片组装系统提示词，调用 LLM 生成最终的回复。
- **`apply_guardrails`** ([guardrails.py](file:///workspace/src/guardrails.py#L107))：执行输入意图校验，并结合正则表达式与 LLM 判断对输出进行拦截判定。
- **`evaluate_session`** ([llm_judge.py](file:///workspace/src/llm_judge.py#L19))：调用大模型对对话历史的教学质量进行 1-5 分的打分评估。

## 5. 依赖关系

项目的核心依赖如下：
- **核心框架**：`langgraph`, `langchain-openai`, `langchain-core`
- **数据与类型校验**：`pydantic`（用于约束大模型输出 JSON 的字段格式）
- **重试机制**：`tenacity`（用于处理大模型 API 调用的超时和重试）
- **大模型服务**：项目默认向 `https://api.deepseek.com` 发送请求，采用 `deepseek-chat` 模型。可在 [config.py](file:///workspace/src/config.py) 中配置。

## 6. 运行与使用方式

### 6.1 环境准备
运行前必须在环境中配置 DeepSeek 的 API Key 作为环境变量（否则系统会返回 Mock 数据）：
```bash
export DEEPSEEK_API_KEY="你的真实_API_KEY"
```

### 6.2 交互式对话体验
在终端启动苏格拉底式辅导助教，你可以扮演学生直接输入物理问题（输入 `exit` 退出）：
```bash
python src/main.py
```

### 6.3 运行批量仿真实验
自动启动模拟学生与智能体的批量对话对弈，用于测试不同版本（Baseline/FSM/FSM+Guardrail）下的系统表现，日志会存入 `logs/` 目录：
```bash
python src/simulator.py
```

### 6.4 生成客观评测指标报告
基于仿真实验生成的日志，计算多维度评估数据（准确率、纠正率、泄漏率等），结果将导出至 `results/summary_metrics.csv`：
```bash
python src/evaluator.py
```

### 6.5 运行主观教学质量评估
使用 LLM 对已生成的对话日志进行教学质量和苏格拉底度评估：
```bash
python src/llm_judge.py
```

### 6.6 运行基础模块测试
根目录下包含部分用于调试子模块的快速测试脚本：
```bash
python test_run.py         # 检查应用初始化与导包情况
python test_graph.py       # 测试工作流图执行与护栏拦截逻辑
python test_classifier.py  # 测试意图分类模块
python test_generator.py   # 测试生成模块
```