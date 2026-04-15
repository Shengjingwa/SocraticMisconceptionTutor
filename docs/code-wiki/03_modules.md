# 3. 模块说明

本章以 `src/` 为主，按“从运行时必经链路 → 离线评估工具”的顺序梳理模块职责与边界。

## 3.1 应用与入口

### src/main.py
链接：[main.py](file:///workspace/src/main.py)

- 职责：对话应用封装、交互式 CLI、调用 LangGraph、落盘日志、会话级统计与收尾。
- 核心实体：`SocraticTutorApp`
  - `step()/astep()`：一次用户输入对应一次图执行
  - `chat()`：终端 REPL
  - `_process_graph_result()`：将图执行产物写入日志，并触发“教后测/学习报告”
- 输出：写入 `logs/turn_logs.jsonl` 和 `logs/session_summary.jsonl`（通过 [logger.py](file:///workspace/src/logger.py)）

## 3.2 工作流编排（LangGraph）

### src/tutor_graph.py
链接：[tutor_graph.py](file:///workspace/src/tutor_graph.py)

- 职责：定义 LangGraph 状态机（节点、边、条件跳转、checkpointer）。
- 节点：
  - `classify_node` → `route_node` → `generate_node` → `guardrail_node` → `finalize_node`
  - 另有 `baseline_node` 作为消融版本 Baseline 的入口
- 关键点：
  - 版本开关：`route_start()` 根据 `system_version` 选择 Baseline 或标准链路
  - 护栏再生成：`guardrail_node` 在触发护栏时设置 `regeneration_required=True`，让图回到 `generate_node` 重生成
  - 记忆压缩：`finalize_node` 会在消息过长时调用 LLM 生成摘要，并删除早期消息
  - 序列化配置：使用 `JsonPlusSerializer` + msgpack allowlist 让 `SessionMemory/PerceptionResult/RouteDecision` 可被 checkpoint

### src/state.py
链接：[state.py](file:///workspace/src/state.py)

- 职责：定义 LangGraph 的状态结构 `GraphState`（TypedDict），用于约束每个节点读写哪些字段。

### src/graph.py（旧版/备用）
链接：[graph.py](file:///workspace/src/graph.py)

- 职责：同样定义了一套 LangGraph 工作流，但当前应用层使用的是 `tutor_graph.py`（`main.py` 引用 `tutor_graph.app_graph`）。
- 备注：可视作早期版本或备用实现，二次开发建议以 `tutor_graph.py` 为准。

## 3.3 感知（NLU / Assessor）

### src/classifiers.py
链接：[classifiers.py](file:///workspace/src/classifiers.py)

- 职责：
  - 将用户输入与上下文对话映射为结构化的 `PerceptionResult`（意图、迷思概念、认知状态、情绪、是否允许状态推进）。
  - 在收尾阶段做“教后测”验证：判断学生是否真正用自己的话说明了正确机制。
- 关键点：
  - `classify_input(..., current_state=...)`：`current_state` 来自最近有效教学状态，用于决定 `transition_approved` 的判定口径。
  - Mock 模式：缺少 API Key 时返回固定的 `PerceptionResult`，便于跑通流水线。

## 3.4 决策（FSM / 策略）

### src/router.py
链接：[router.py](file:///workspace/src/router.py)

- 职责：
  - 定义 FSM 的状态空间与策略集合。
  - 实现状态转移、防环/熔断规则，以及策略选择。
  - 提供对话后更新函数 `update_after_turn()`。
- 核心数据结构：
  - `PerceptionResult`：感知层输出
  - `SessionMemory`：跨轮次持久状态
  - `RouteDecision`：本轮决策结果（state/strategy/next_goal/meta）

## 3.5 生成（Prompt / Reply）

### src/generator.py
链接：[generator.py](file:///workspace/src/generator.py)

- 职责：
  - 将 `RouteDecision + SessionMemory + 数据库(迷思概念/知识块)` 组装为系统提示词。
  - 生成回复，并清洗模型输出（移除 `<think>` 等）。
  - 在 `resolved=True` 时生成学习报告。
- 数据依赖：
  - `data/misconceptions.json`：迷思概念库（含反例/类比/推理漏洞/禁用短语等）
  - `data/knowledge_chunks.json`：知识块（更偏“可提示内容”）

## 3.6 安全护栏（Guardrails）

### src/guardrails.py
链接：[guardrails.py](file:///workspace/src/guardrails.py)

- 职责：
  - 输入护栏：阻断 Direct_Answer_Seek / Off_Topic 等风险意图。
  - 输出护栏：检测是否“直接泄露答案”或“代替推导”。
- 关键点：
  - 输出侧支持两级：规则匹配（快速）→ LLM Judge（语义）双保险。
  - 判定具有“模式”：
    - 严格模式（如 `S2/S4`）
    - 弹性模式（连续触发多次后放宽）
    - 事实兜底模式（`S7` 强豁免：允许陈述实验现象但不解释原理）

## 3.7 日志

### src/logger.py
链接：[logger.py](file:///workspace/src/logger.py)

- 职责：
  - 文件日志：`logs/app.log`（RotatingFileHandler）
  - 结构化日志：
    - `logs/turn_logs.jsonl`：逐轮
    - `logs/session_summary.jsonl`：会话汇总
- 并发写：通过 `threading.Lock()` 保证写入原子性。

## 3.8 仿真与评估

### src/simulator.py
链接：[simulator.py](file:///workspace/src/simulator.py)

- 职责：
  - 通过学生画像 + 迷思概念库批量生成多会话对话。
  - 支持并发与最大轮数控制；每个会话会复用 `SocraticTutorApp`。

### src/evaluator.py
链接：[evaluator.py](file:///workspace/src/evaluator.py)

- 职责：
  - 从 `logs/*.jsonl` 计算汇总指标，输出 `results/summary_metrics.csv`。
  - 按版本抽样会话，输出 `results/manual_audit.csv` 供人工审阅。

### src/llm_judge.py
链接：[llm_judge.py](file:///workspace/src/llm_judge.py)

- 职责：
  - 读取 `turn_logs.jsonl`，按 `session_id` 聚合对话历史。
  - 调用评审 LLM 输出 `socratic_degree / teaching_effectiveness / reasoning`，写入 `logs/evaluation_results.json`。

