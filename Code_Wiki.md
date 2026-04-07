# 项目 Code Wiki：苏格拉底式对话教育智能体 (MVP)

## 1. 项目概述

本项目是一个面向初中物理典型迷思概念（以电学与浮力为例）的**苏格拉底式对话教育智能体原型（MVP）**。该系统旨在通过引导式提问、制造认知冲突和提供认知支架，帮助学生克服物理学习中的迷思概念。
本项目采用有限状态机（FSM）严格控制对话和教学流程，避免了大型语言模型（LLM）常见的过早给出答案、教学逻辑漂移等问题。

---

## 2. 整体架构

系统采用了典型的**“感知-决策-生成” (Perception-Decision-Generation)** 三层架构流水线，并通过基于规则的状态机串联：

1. **输入感知层 (Perception)**：接收学生输入，通过正则和关键字匹配识别意图、提取迷思概念标签、评估认知状态和风险。
2. **路由决策层 (Routing/Decision)**：根据感知结果和当前会话记忆，基于 V1 版教学状态机（7个状态 S0-S6）决定下一个教学状态和应采用的教学策略。
3. **回复生成层 (Generation)**：基于决策结果，结合内置的学科知识库和策略模板，生成符合当前教学状态的回复。
4. **日志记录 (Logging)**：在每轮对话结束后，将状态、意图、置信度及回复数据结构化落盘，用于后续论文的数据分析和评估。

---

## 3. 核心模块与职责

项目的核心逻辑集中在 `src/` 目录下的 Python 脚本中：

- **`main.py`**：项目入口与主控模块。负责组装各模块、运行交互式命令行对话（CLI）、维护 `SocraticTutorApp` 实例，以及将对话状态和日志写入文件。
- **`router.py`**：核心路由与状态机管理模块。定义了 `SessionMemory` 会话记忆，实现了状态机流转逻辑（`route_state`），控制教学流向认知冲突（S4）、支架引导（S5）或验证深化（S6）。
- **`classifiers.py`**：输入分类与意图识别模块。通过预设的正则表达式和关键词列表（Heuristics），对学生的输入进行多维度分类（意图、迷思概念、认知状态、直接索要答案的风险等）。
- **`generator.py`**：回复生成模块。内置了各迷思概念的科学核心点、反例、类比及策略模板。负责将 `router.py` 选定的教学策略实例化为具体的自然语言回复。
- **`logger.py`**：日志工具（在 `main.py` 中有简易实现），负责保存 `.jsonl` 格式的对话日志。
- *注：`evaluator.py`, `guardrails.py`, `simulator.py` 目前为空文件，是为后续扩展评估、安全护栏增强和批量模拟对话预留的占位模块。*

---

## 4. 关键类与函数说明

### 4.1 核心类 (Classes)
- **`SocraticTutorApp`** (`main.py`)
  - **职责**：封装了整个对话智能体的上下文。
  - **核心方法**：`step(user_input)` 执行单轮对话推理流水线；`chat()` 启动控制台持续交互循环。
- **`SessionMemory`** (`router.py`)
  - **职责**：数据类 (Dataclass)，用于记录单次会话状态。
  - **属性**：保存 `session_id`, `current_state`, `current_misconception`（当前迷思）, `turn_count`（轮次）, `used_strategies`（已用策略）, `recent_states` 等。
- **`PerceptionResult` & `RouteDecision`** (`router.py`)
  - **职责**：数据契约类，分别表示感知模块的输出结果和路由模块的决策结果。

### 4.2 核心函数 (Functions)
- **`classify_input(user_input, history_summary)`** (`classifiers.py`)
  - **功能**：综合调用多个子预测函数（如 `predict_intent`, `predict_misconception` 等），输出 `PerceptionResult`。
- **`route_state(perception, memory)`** (`router.py`)
  - **功能**：实现状态机流转的核心业务逻辑。例如当存在风险标记时转入 S2（拒绝代答），当学生认知“固守错误”时转入 S4（制造冲突）。
- **`generate_reply(user_input, decision, memory, ...)`** (`generator.py`)
  - **功能**：基于策略模板（如 `Clarification`）和学科知识点（如 `DEFAULT_KNOWLEDGE`）渲染最终回复字符串，并附加验证性或支架性追问。

---

## 5. 状态机与教学策略设计

系统基于 `docs/state_machine_v1.md` 设定的 7 个核心状态运行：
- **S0 (Listen_And_Analyze)**：接收输入并分析。
- **S1 (Guardrail_Check)**：检查高风险输入（如直接索要答案）。
- **S2 (Refusal_And_Guidance)**：拒绝代答并引导。
- **S3 (Misconception_Diagnosis)**：诊断迷思并分流。
- **S4 (Cognitive_Conflict)**：制造认知冲突（策略：澄清、挑战假设、后果探索）。
- **S5 (Scaffolding_Guidance)**：提供理解支架（策略：类比支架、提供科学核心点）。
- **S6 (Verification_Deepening)**：验证与深化（策略：变式提问）。

**支持的迷思概念**：
- 电学：`M-ELE-001` (电流消耗模型), `M-ELE-002` (单极模型/无闭合回路)。
- 浮力：`M-BUO-001` (重物必沉), `M-BUO-002` (浮力只由深度决定)。

---

## 6. 依赖关系

- **内部依赖**：项目内部模块高度解耦，数据流向清晰 (`main` -> `classifiers` -> `router` -> `generator`)。
- **外部依赖**：当前 MVP 版本采用纯规则和模板实现，**无任何第三方 Python 包依赖**（如 `requests`, `openai`, `langchain` 等），全部基于 Python 标准库（`json`, `re`, `dataclasses`, `pathlib` 等）构建。

---

## 7. 运行与使用方式

### 7.1 启动交互式对话
直接运行 `main.py` 即可进入控制台交互模式：
```bash
python src/main.py
```
输入 `exit`、`quit` 或 `q` 可退出程序。

### 7.2 运行 Demo 测试
`main.py` 中包含一个 `demo()` 函数，可用于对预设的测试用例进行批量测试：
在 `src/main.py` 中将 `if __name__ == "__main__":` 块下的代码修改为调用 `demo()` 并执行即可。

### 7.3 查看日志
交互过程中产生的所有日志会被记录在项目根目录的 `logs/` 文件夹中（如 `logs/interactive_main.jsonl`），日志包含每轮的意图预测、状态跳转、采用策略及回复文本，方便后续数据分析。

---

## 8. 目录结构说明

```text
/workspace/
├── src/                    # 核心源代码目录
│   ├── main.py             # 入口文件与交互循环
│   ├── router.py           # 状态机路由与内存管理
│   ├── classifiers.py      # 用户输入分类器（规则引擎）
│   ├── generator.py        # 话术与回复生成器
│   ├── logger.py           # 日志工具模块
│   ├── evaluator.py        # （待开发）评估模块
│   ├── guardrails.py       # （待开发）安全护栏模块
│   └── simulator.py        # （待开发）对话模拟器
├── data/                   # 配置文件与静态数据（目前供参考）
│   ├── knowledge_chunks.json
│   ├── misconceptions.json
│   └── ...
├── docs/                   # 项目说明与学术设计文档
│   ├── state_machine_v1.md # FSM 状态机 V1 核心设计文档
│   ├── scope_freeze.md     # 论文范围冻结声明
│   └── ...
└── logs/                   # 运行生成的 jsonl 日志文件目录
```