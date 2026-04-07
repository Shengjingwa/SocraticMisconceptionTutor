# 项目 Code Wiki：苏格拉底式对话教育智能体

## 1. 项目概述

本项目是一个面向初中物理（聚焦电学与浮力）的苏格拉底式对话教育智能体（Socratic Dialogue Educational Agent）。该系统旨在通过引导式提问、制造认知冲突和提供认知支架，帮助学生纠正典型的物理迷思概念（Misconceptions），而非直接灌输正确答案。

核心架构基于 **LangGraph 工作流引擎** 和 **有限状态机（FSM）**，对话流水线严格遵循“感知 (Perception) -> 决策 (Decision) -> 生成 (Generation) -> 护栏 (Guardrail)”的闭环设计。系统底层默认调用 DeepSeek 大模型（`deepseek-chat`），并支持通过消融实验（Baseline、FSM、FSM+Guardrail）评估不同策略的有效性。

---

## 2. 项目整体架构

### 2.1 核心工作流 (LangGraph Pipeline)
系统的单轮对话处理基于 `LangGraph` 状态图进行调度，节点流转逻辑如下：
1. **感知节点 (`classify`)**：对用户的自然语言输入进行结构化解析（NLU），提取意图、错误概念、认知状态。
2. **决策节点 (`route`)**：作为有限状态机（FSM）的引擎，结合 NLU 结果与历史会话记忆，决定当前处于哪个教学状态，并选择恰当的引导策略（如：澄清提问、假设探究等）。
3. **生成节点 (`generate`)**：依据决策目标与当前采用的引导策略，动态拉取本地 JSON 教学资源（核心知识、反例、类比），组装系统提示词并调用大模型生成苏格拉底式回复。
4. **护栏节点 (`guardrail`)**：双向安全检查。若触发拦截（如直接要答案、模型直接泄露物理结论），则通过 LangGraph 的条件边（Conditional Edge）触发重定向至 `route` 或强制 `generate` 重新生成。

### 2.2 有限状态机 (FSM) 教学状态模型
系统定义了七个核心状态以反映教学引导进程（`src/router.py`）：
- **S0 (Listen_And_Analyze)**：初始分析状态。
- **S1 (Guardrail_Check)**：安全检测状态（隐式），识别求答案或偏题。
- **S2 (Refusal_And_Guidance)**：拒绝直接代答，并重定向至引导路径。
- **S3 (Misconception_Diagnosis)**：诊断识别错误概念。
- **S4 (Cognitive_Conflict)**：制造认知冲突（策略：假设探究、后果探索）。
- **S5 (Scaffolding_Guidance)**：提供认知支架（策略：澄清提问、寻找证据、类比支架）。
- **S6 (Verification_Deepening)**：验证与深化概念掌握。

---

## 3. 目录结构与主要模块职责

### 3.1 核心代码 (`src/` 目录)
- **`main.py`**：应用主入口。定义 `SocraticTutorApp` 类，负责管理长期会话记忆（`SessionMemory`），调度 LangGraph 状态图执行，记录交互日志，并提供终端对话接口。
- **`graph.py`**：LangGraph 工作流引擎。编译构建 `app_graph`，串联 `classify`、`route`、`generate`、`guardrail` 四个核心节点。
- **`state.py`**：定义 `GraphState` 数据结构，作为 LangGraph 在各节点间传递的全局强类型数据总线。
- **`classifiers.py`**：NLU 感知模块。利用大模型的结构化输出能力（或正则回退），解析用户意图、认知状态与迷思标签（如 `M-ELE-001`）。
- **`router.py`**：FSM 决策引擎。维护 `SessionMemory`，根据状态转移矩阵和防死循环启发式规则，计算出包含下一目标和策略的 `RouteDecision`。
- **`generator.py`**：回复生成模块。从 `data/` 目录挂载物理知识片段与系统提示词模板，组合上下文对话历史进行 LLM 问答。
- **`guardrails.py`**：安全护栏模块。结合前置正则匹配与 **LLM-as-a-Judge** 机制，防范输入层面的作弊（如求答案）和输出层面的答案泄露（Answer Leakage）。
- **`simulator.py`**：仿真实验模块。包含 `SimulatedStudent` 类，利用大模型扮演具有特定性格和错误概念的初中生，与助教进行多轮自动对弈。
- **`evaluator.py`**：指标评测模块。解析 `logs/` 目录下的 JSONL 会话日志，计算迷思识别准确率、认知纠正率、护栏拦截率、答案泄露率等指标，输出至 CSV 报告。
- **`config.py`**：配置模块。统一定义 API Key、模型版本、重试参数及历史上下文窗口大小。
- **`logger.py`**：日志持久化模块。负责将轮次信息 (`turn_log`) 和会话摘要 (`session_summary`) 落盘为标准 JSONL 格式。

### 3.2 静态数据 (`data/` 目录)
- **`misconceptions.json`**：详细定义物理迷思概念及其表现（如“电流消耗模型”、“单极模型”、“重物必沉”）。
- **`knowledge_chunks.json`**：对应的科学知识点、反例、类比素材及验证问题。
- **`simulation_profiles.json`**：定义模拟初中生的性格模板（如“固执型”、“动摇型”、“困惑型”），用于自动化测试。

### 3.3 输出制品 (`logs/` & `results/` 目录)
- **`logs/turn_logs.jsonl`**：每轮对话详细的输入输出、预测标签、触发策略及护栏状态。
- **`logs/session_summary.jsonl`**：每次对话任务（Session）的全局结束状态和总指标。
- **`results/summary_metrics.csv`**：经由 `evaluator.py` 计算得出的各版本（Baseline/FSM/FSM+Guardrail）性能对比报表。

---

## 4. 关键类与函数说明

### 4.1 核心业务类
- **`SocraticTutorApp`** (`src/main.py`)
  - **职责**：封装单次会话上下文，执行图计算。
  - **关键方法 `step(user_input: str)`**：接收用户输入，包装为 `initial_state`，调用 `app_graph.invoke()`，并调用 `logger_instance` 记录轮次日志。

- **`SimulatedStudent`** (`src/simulator.py`)
  - **职责**：仿真学生模拟器，用于批处理实验。
  - **行为**：初始化时注入特定 `profile` 和 `misconception` 提示词。暴露 `generate_opening()` 和 `reply(teacher_message)` 供自动对弈循环调用。

### 4.2 核心工作流节点函数
- **`classify_input(user_input, messages)`** (`src/classifiers.py`)
  - **输入**：当前用户文本与对话历史。
  - **输出**：`PerceptionResult` (含 `intent`, `misconception_tag`, `cognitive_state`, `risk_flag`)。
  
- **`route_state(perception, memory)`** (`src/router.py`)
  - **输入**：感知结果与当前会话记忆。
  - **输出**：`RouteDecision`，包含目标状态（S0-S6）与采用策略（如 `Assumption_Probing`）。内置启发式规则防止连续卡在同一状态。

- **`generate_reply(user_input, decision, memory)`** (`src/generator.py`)
  - **行为**：组装带有策略目标、安全护栏约束和局部知识片段（`core_points`, `counterexamples`）的 `system_prompt`。若状态为 S2，则直接使用预置的话术模板拒绝并重定向。

- **`apply_guardrails(user_input, intent, generated_text, ...)`** (`src/guardrails.py`)
  - **行为**：
    1. **输入检查 `check_input`**：判断是否 `Direct_Answer_Seek`。
    2. **输出检查 `check_output`**：通过基础关键词正则防范，加 `LLM-as-a-Judge` 的语义判决，确保助教未代替学生完成推理。

---

## 5. 依赖关系

本项目基于 Python 3 开发，核心依赖包如下：
- **`langgraph`**：构建核心的感知-决策-生成有向图流水线。
- **`langchain-openai`** & **`langchain-core`**：提供大模型连接封装与消息传递对象（SystemMessage, HumanMessage）。
- **`pydantic`**：为大模型结构化输出（NLU解析、LLM Judge）提供严格的数据类校验。
- **`tenacity`**：提供调用大模型 API 时的指数退避重试（Retry）机制。

**外部服务依赖**：
- 默认接入 **DeepSeek API**（`https://api.deepseek.com`），调用 `deepseek-chat` 模型。运行前需确保环境内存在有效密钥。

---

## 6. 项目运行与使用方式

### 6.1 环境配置
运行前必须在终端中配置 `DEEPSEEK_API_KEY`（否则将返回 Mock 数据或报错）：
```bash
export DEEPSEEK_API_KEY="你的真实_API_KEY"
```

### 6.2 模式一：交互式对话体验（MVP）
以终端命令行的形式启动助教。用户可以扮演学生，向助教提出诸如“电流经过灯泡会不会变少”等迷思问题。
```bash
python src/main.py
```
> 输入 `exit` 或 `quit` 结束会话。

### 6.3 模式二：批量自动化仿真实验
启动多版本（Baseline, FSM, FSM+Guardrail）、多迷思、多性格组合的模拟测试。用于验证助教系统的纠正效果与护栏触发率，日志会统一写入 `logs/`。
```bash
python src/simulator.py
```

### 6.4 模式三：生成评测指标报告
解析批量仿真实验生成的 `turn_logs.jsonl` 和 `session_summary.jsonl` 日志，计算并导出评测数据：
```bash
python src/evaluator.py
```
> 执行完毕后将在 `results/` 目录下生成 `summary_metrics.csv`（量化指标报表）与 `manual_audit.csv`（抽样人工审计表）。

### 6.5 运行基础模块测试
根目录包含若干独立测试脚本，用于验证各组件逻辑是否正常：
```bash
python test_run.py         # 检查环境依赖与包导入
python test_graph.py       # 验证 LangGraph 工作流运转机制
python test_classifier.py  # 验证意图分类模块的结构化抽取
```