# 项目 Code Wiki：苏格拉底式对话教育智能体

## 1. 项目概述
本项目是一个面向初中物理（聚焦电学与浮力）的苏格拉底式对话教育智能体。该系统旨在通过引导式提问、制造认知冲突和提供认知支架，帮助学生纠正典型的物理迷思概念（Misconceptions）。

核心架构基于 **LangGraph + 状态机（FSM）**，对话工作流严格遵循“感知 (Perception) -> 决策 (Decision) -> 生成 (Generation) -> 护栏 (Guardrail)”的流水线设计。系统底层基于 DeepSeek 大模型（通过 `langchain_openai` 调用），并支持多版本运行模式（Baseline、FSM、FSM+Guardrail）以进行消融实验。

---

## 2. 项目整体架构
系统采用模块化设计，核心处理流水线如下：

1. **输入感知 (Perception)**：自然语言理解（NLU）模块利用 LLM 的结构化输出能力，提取用户的意图、认知状态及具体的错误概念标签。
2. **决策路由 (Decision/Routing)**：基于状态机（FSM），结合 NLU 解析结果和历史对话状态（S0-S6），决定下一轮教学的引导状态和干预策略（如认知冲突、支架引导等）。
3. **回复生成 (Generation)**：结合当前状态机指令，检索本地知识切片（核心知识点、反例、类比），组装 Prompt 并调用 LLM 生成苏格拉底式提问。
4. **安全护栏 (Guardrail)**：输入端防范直接求答案或偏题，输出端防止大模型直接“泄露答案”，若触发拦截则通过条件边触发重新生成循环。
5. **仿真与评估闭环**：内置由 LLM 驱动的“模拟初中生”模块进行自动化对弈测试，并自动计算准确率、纠正率等核心评测指标。

---

## 3. 主要模块职责 (`src/` 目录)

- **`main.py`**：应用主入口。定义系统主类，负责管理会话记忆、调度 LangGraph 工作流、执行日志记录，并提供交互式终端聊天界面。
- **`graph.py`**：工作流引擎。利用 LangGraph 定义核心状态图节点（分类、路由、生成、护栏），并配置条件边以支持护栏拦截时的重新生成。
- **`classifiers.py`**：自然语言理解（NLU）模块。利用 LLM 识别用户意图、认知状态及错误概念标签。
- **`router.py`**：状态机与决策模块。根据 NLU 结果和历史状态决定下一步引导策略。
- **`generator.py`**：回复生成模块。结合策略和 `data/` 目录中的知识切片，组装 Prompt 生成最终的启发式回复。
- **`guardrails.py`**：安全护栏模块。负责输入与输出双向检测，确保教学过程的启发性而非直接灌输。
- **`simulator.py`**：仿真实验模块。利用 LLM 扮演具有特定错误概念的“模拟初中生”，与智能体进行批量对话。
- **`evaluator.py`**：指标计算模块。解析实验日志，计算迷思概念识别准确率、认知纠正率、护栏拦截率等核心指标并生成 CSV 报告。
- **`logger.py`** & **`state.py`**：分别负责日志文件落盘以及 LangGraph 全局数据状态 (`GraphState`) 的类型定义。

---

## 4. 关键类与函数说明

### 4.1 核心类
- **`SocraticTutorApp`** (`src/main.py`)：智能体会话管理核心类，其 `step()` 方法执行单轮的状态图调用。
- **`SimulatedStudent`** (`src/simulator.py`)：封装了模拟初中生人格的 Prompt 和对话逻辑，用于自动化仿真对弈。

### 4.2 核心函数与实例
- **`app_graph`** (`src/graph.py`)：编译后的 LangGraph 状态图实例，是串联各个子模块的处理中枢。
- **`classify_input`** (`src/classifiers.py`)：调用 LLM 提取结构化信息，返回 `PerceptionResult`。
- **`route_state`** (`src/router.py`)：执行状态转换逻辑，返回下一步的 `RouteDecision` 决策信息。
- **`generate_reply`** (`src/generator.py`)：根据策略路由结果和本地 JSON 教学资源组装提示词，返回最终生成的回复。
- **`apply_guardrails`** (`src/guardrails.py`)：执行输入意图校验和输出的正则表达式匹配，判定是否需要拦截或重新生成。

---

## 5. 依赖关系

项目主要依赖以下第三方 Python 库：
- **核心框架**：`langgraph`, `langchain-openai`, `langchain-core`
- **数据与类型校验**：`pydantic`（用于约束大模型输出 JSON 的字段格式）
- **大模型服务**：项目默认向 `https://api.deepseek.com` 发送请求，采用 `deepseek-chat` 模型。

---

## 6. 运行与使用方式

### 6.1 环境准备
运行前必须在终端中配置 DeepSeek 的 API Key 作为环境变量（否则系统可能返回 Mock 数据或调用失败）：
```bash
export DEEPSEEK_API_KEY="你的真实_API_KEY"
```

### 6.2 交互式对话体验
在终端启动苏格拉底式辅导助教，你可以扮演学生直接输入物理问题（输入 `exit` 退出）：
```bash
python src/main.py
```

### 6.3 运行批量仿真实验
自动启动模拟学生与智能体的批量对话对弈，用于测试不同版本下的系统表现，日志会存入 `logs/` 目录：
```bash
python src/simulator.py
```

### 6.4 生成评测指标报告
基于仿真实验生成的日志，计算多维度评估数据，结果将导出至 `results/summary_metrics.csv`：
```bash
python src/evaluator.py
```

### 6.5 运行基础模块测试
根目录下包含部分用于调试子模块的快速测试脚本：
```bash
python test_run.py         # 检查应用初始化与导包情况
python test_graph.py       # 测试工作流图执行与护栏拦截逻辑
python test_classifier.py  # 测试意图分类模块
```
