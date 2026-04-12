# 📚 苏格拉底式对话教育智能体 (Socratic Tutor) Code Wiki

## 🌟 1. 项目简介 (Overview)
本项目是一个基于 LangGraph 构建的**苏格拉底式对话教育智能体 (MVP)**。系统主要针对初中物理典型迷思概念（如电学、浮力），通过**显式教学状态机 (FSM)** 控制对话流，采用**启发式提问策略**和**防答案泄露护栏**，引导学生自主思考并修正错误概念，而不是直接给出标准答案。

---

## 🏗️ 2. 项目整体架构 (Architecture)
系统采用三层架构设计，通过显式状态机确保教学逻辑稳定：
1. **感知层 (Perception)**: 分析用户输入，识别意图、认知状态及错误概念标签。
2. **决策层 (Decision)**: 基于当前认知状态和上下文，选择下一个教学状态及提问策略。
3. **执行层 (Execution)**: 结合教学状态、策略与知识库，动态组装 Prompt，生成安全的启发式回复。

**核心执行流由 LangGraph 编排 (`src/graph.py`)**：
`classify_node` (分类) ➡️ `route_node` (路由决策) ➡️ `generate_node` (生成回复) ➡️ `guardrail_node` (安全拦截)。若未通过护栏，将自动重路由并触发重新生成。

---

## 📂 3. 目录结构与模块职责 (Directory Structure)

```text
/workspace
├── src/                    # 核心源码目录
│   ├── main.py             # 程序入口，定义了应用主类和 CLI 交互逻辑
│   ├── graph.py            # LangGraph 状态机工作流编排
│   ├── state.py            # GraphState 状态数据结构定义
│   ├── classifiers.py      # NLU 意图和认知状态分类器
│   ├── router.py           # 路由决策逻辑与对话记忆管理
│   ├── generator.py        # LLM 回复生成与 Prompt 组装
│   ├── guardrails.py       # 安全护栏（防止代答/越界）
│   ├── logger.py           # 日志记录模块（记录回合和会话指标）
│   ├── config.py           # 系统配置（LLM 模型、API Key 等）
│   ├── simulator.py        # 仿真实验执行脚本
│   ├── evaluator.py        # 实验指标计算与评估
│   └── llm_judge.py        # LLM 裁判（用于护栏拦截与输出评估）
├── data/                   # 静态数据与教学知识库
│   ├── misconceptions.json # 典型错误概念库 (如 M-ELE-001)
│   ├── knowledge_chunks.json # 核心知识点、反例与类比库
│   ├── strategy_templates.json # 提问策略模板
│   ├── simulation_profiles.json# 仿真测试用的学生画像
│   └── adversarial_inputs.json # 对抗测试用例 (索要答案等)
├── docs/                   # 项目文档与设计说明
│   ├── state_machine_v1.md # 状态机 V1 详细设计文档
│   └── 计划安排.md         # 项目开发排期与验收标准
├── logs/                   # 运行日志目录 (turn_logs/session_summary)
└── results/                # 仿真实验结果与评估报告
```

---

## 🧩 4. 关键类与函数说明 (Key Components)

### [src/graph.py](file:///workspace/src/graph.py) (状态机工作流)
- **`workflow = StateGraph(GraphState)`**: 构建了 4 个主要处理节点。
- **`classify_node`**: 调用分类器解析学生输入。
- **`route_node`**: 根据意图和状态转移矩阵，决定状态跳转目标（如 `S3` -> `S4`）。
- **`generate_node`**: 生成助教回复。
- **`guardrail_node`**: 检查输出是否泄露答案。若违规，触发重试。

### [src/router.py](file:///workspace/src/router.py) (路由与策略)
- **`SessionMemory`**: 长期会话记忆类，记录当前迷思概念、历史摘要及已用策略等。
- **`RouteDecision`**: 决策结果封装类，决定下一步的目标 `state` (S0~S6)、使用的 `strategy` 及目标说明。
- **`route_state(perception, memory)`**: 核心状态机路由函数。基于状态转移矩阵和防死循环规则进行动态状态推进。

### [src/classifiers.py](file:///workspace/src/classifiers.py) (意图感知)
- **`classify_input(...)`**: 基于 Pydantic 与 LLM 的结构化输出，提取 `NLUOutput`，包括用户的意图（如直接求答案）、迷思标签（如 `M-ELE-001`）和当前认知状态（如“认知僵局”），最终封装为 `PerceptionResult` 返回。

### [src/generator.py](file:///workspace/src/generator.py) (受控生成)
- **`generate_reply(...)`**: 核心回复生成器。通过组合“教学身份”、“当前状态/策略”、“知识碎片”及严格的“禁泄露规则”组装成强大的 System Prompt，驱动 LLM 输出教学回复。

### [src/guardrails.py](file:///workspace/src/guardrails.py) (安全护栏)
- **`check_input(...)`**: 拦截高风险输入（如用户直接要求给出答案或偏题）。
- **`check_output(...)`**: 使用关键字匹配及 LLM-as-a-Judge 机制，防止模型在回复中不慎直接泄露最终的物理结论或包办关键推理步骤。

### [src/main.py](file:///workspace/src/main.py) (应用入口)
- **`SocraticTutorApp`**: 应用门面类。提供 `step(user_input)` 和 `astep()` 方法单步执行图网络并写入日志。
- **`chat()`**: 交互式 CLI 对话函数，可与智能体进行终端对话。

---

## 🔄 5. 教学状态机设计 (FSM States)
项目在 [docs/state_machine_v1.md](file:///workspace/docs/state_machine_v1.md) 中定义了 7 个核心状态：
- **S0 (Listen_And_Analyze)**: 监听并分析学生意图及状态。
- **S1 (Guardrail_Check)**: 护栏检查，识别风险。
- **S2 (Refusal_And_Guidance)**: 拒绝代答与重定向（用于处理直接要答案的用户）。
- **S3 (Misconception_Diagnosis)**: 迷思诊断，分发不同教学路径。
- **S4 (Cognitive_Conflict)**: 制造认知冲突（触发挑战假设/后果探索策略）。
- **S5 (Scaffolding_Guidance)**: 支架引导（当学生卡壳时，提供类比、证据追问等支架）。
- **S6 (Verification_Deepening)**: 验证与深化（确认学生真正掌握概念，而非蒙对）。

---

## 📦 6. 依赖关系 (Dependencies)
主要依赖于以下库（需结合大模型运行）：
- `langchain`, `langchain-openai`, `langchain-core`: 用于大模型调用与提示词管理。
- `langgraph`: 用于构建和运行循环状态图（StateGraph）。
- `pydantic`: 用于定义 LLM 结构化输出的数据模型。
- `tenacity`: 用于网络调用的退避与重试机制。
- **配置**: 需要在运行环境中提供大模型服务，具体鉴权配置（如 `DEEPSEEK_API_KEY`）见 `src/config.py`。

---

## 🚀 7. 项目运行方式 (How to Run)

1. **环境准备**:
   确保使用 Python 3.10+，并安装相关依赖包 (如 `langchain`, `langgraph` 等)。
2. **配置环境变量**:
   需要在环境中或 `config.py` 里配置 LLM_MODEL 和对应的 API_KEY (默认支持 DeepSeek 格式接口)。
3. **启动交互式对话 (CLI)**:
   ```bash
   cd /workspace
   python src/main.py
   ```
   输入内容后，智能体将开始引导对话；输入 `exit` 或 `quit` 结束会话。
4. **运行单元测试/仿真**:
   可以运行根目录下的 `test_run.py`, `test_graph.py` 等脚本验证各个模块与整体链路：
   ```bash
   python test_run.py
   ```