# 4. 关键类与函数

本章聚焦“读源码时最值得先理解的 API 面”，以 **调用方向**（入口 → 工作流 → 分类 → FSM → 生成 → 护栏 → 日志/评估）组织。

## 4.1 SocraticTutorApp（应用入口）
定义位置：[main.py](file:///workspace/src/main.py#L24-L214)

### `class SocraticTutorApp`
- 关键字段
  - `memory: SessionMemory`：跨轮次会话状态（来自 [router.py](file:///workspace/src/router.py#L27-L41)）
  - `system_version: str`：Baseline/FSM/FSM+Guardrail 版本开关
  - `misconception_init`：仿真时注入的“真值”标签（用于评估）
  - `guardrail_trigger_count / answer_leakage_count / abnormal_end_flag`：会话级统计

### `step(user_input: str) -> Dict[str, Any]`
代码：[main.py](file:///workspace/src/main.py#L103-L125)

- 输入：用户本轮输入文本
- 行为：
  - 组装 LangGraph 初始状态（包含 `messages=[HumanMessage(content=user_input)]`）
  - 调用 `app_graph.invoke(initial_state, config)` 执行工作流（`configurable.thread_id` 用于 checkpoint 的 thread）
  - 捕获全局异常并返回兜底回复（Error_State）
- 输出：一个 dict（含 perception/decision/generation/memory/guardrail/learning_report）

### `_process_graph_result(final_state, user_input) -> Dict[str, Any]`
代码：[main.py](file:///workspace/src/main.py#L35-L101)

- 行为：
  - 根据 `perception.cognitive_state == "概念掌握验证"` 且 `decision.state == "S6"` 触发教后测验证：`verify_post_test()`（[`classifiers.py`](file:///workspace/src/classifiers.py#L33-L99)）
  - 更新 `self.memory = update_after_turn(...)`（[`router.py`](file:///workspace/src/router.py#L283-L293)）
  - 生成 turn_log 并写入 `turn_logs.jsonl`（[`logger.py`](file:///workspace/src/logger.py#L34-L38)）
  - 会话 resolved 时生成学习报告：`generate_learning_report()`（[`generator.py`](file:///workspace/src/generator.py#L364-L419)）

### `end_session(termination_reason: str) -> None`
代码：[main.py](file:///workspace/src/main.py#L151-L167)

- 行为：汇总会话级指标写入 `session_summary.jsonl`。

## 4.2 LangGraph 工作流（app_graph）
定义位置：[tutor_graph.py](file:///workspace/src/tutor_graph.py#L43-L251)

### `app_graph`
- 来源：`workflow.compile(checkpointer=memory_saver)`（[`tutor_graph.py`](file:///workspace/src/tutor_graph.py#L208-L251)）
- 状态类型：`GraphState`（[`state.py`](file:///workspace/src/state.py#L6-L24)）
- 关键特点：
  - 通过 `MemorySaver(serde=JsonPlusSerializer(...))` 保存 checkpoint，允许跨调用复用会话状态
  - `messages` 字段采用 LangGraph 的 `add_messages` reducer 自动追加（[`state.py`](file:///workspace/src/state.py#L14-L15)）

### 节点：`classify_node(state) -> {"perception": PerceptionResult}`
代码：[tutor_graph.py](file:///workspace/src/tutor_graph.py#L43-L52)

- 从 `memory.recent_states` 推导“最近有效教学状态”作为 `current_state` 传给 `classify_input()`。

### 节点：`route_node(state) -> {"decision": RouteDecision, "memory": SessionMemory}`
代码：[tutor_graph.py](file:///workspace/src/tutor_graph.py#L54-L58)

- 调用 `route_state(perception, memory)`（[`router.py`](file:///workspace/src/router.py#L210-L281)）。

### 节点：`generate_node(state) -> {"generation": Dict}`
代码：[tutor_graph.py](file:///workspace/src/tutor_graph.py#L60-L66)

- 调用 `generate_reply(user_input, decision, memory, messages=...)`（[`generator.py`](file:///workspace/src/generator.py#L68-L279)）。

### 节点：`guardrail_node(state) -> Dict`
代码：[tutor_graph.py](file:///workspace/src/tutor_graph.py#L82-L147)

- 输入：`user_input/perception/decision/generation/memory/system_version`
- 关键逻辑：
  - 重试上限：`decision.meta.guardrail_retries >= 2` 则直接给出兜底回复并停止再生成
  - `system_version != "FSM+Guardrail"` 时禁用拦截（但仍返回检测结果）
  - 真正触发护栏时：
    - `new_memory.consecutive_guardrail_triggers += 1`
    - 写入 `decision.meta.guardrail_feedback`（用于生成时的“安全警告提示”）
    - 返回 `regeneration_required=True`，让图回到 `generate_node`

### 节点：`finalize_node(state) -> Dict`
代码：[tutor_graph.py](file:///workspace/src/tutor_graph.py#L149-L182)

- 关键逻辑：
  - 将 `raw_reply` 写入 `AIMessage` 追加到 `messages`
  - 当消息过长时调用 LLM 生成摘要并更新 `memory.history_summary`，随后删除早期消息（`RemoveMessage`）

## 4.3 classify_input（NLU / Assessor）
定义位置：[classifiers.py](file:///workspace/src/classifiers.py#L100-L292)

### `classify_input(user_input, messages, history_summary, current_state) -> PerceptionResult`
- 输出：[`PerceptionResult`](file:///workspace/src/router.py#L16-L25)
  - `intent`：Direct_Answer_Seek / Off_Topic / Cognitive_Stuck / Knowledge_Inquiry / Misconception_Expression / Hypothesis_Put_Forward
  - `misconception_tag`：M-ELE-001 等
  - `cognitive_state`：认知僵局 / 固守错误概念 / 认知冲突触发 / 新概念探索 / 概念掌握验证
  - `transition_approved`：是否满足当前状态退出条件（由 system prompt 明确约束）
  - `sentiment/confidence/reasoning`
- 关键点：
  - `risk_flag` = `intent in ["Direct_Answer_Seek","Off_Topic"]`
  - 解析失败时提供“raw parsing fallback”：正则抓 JSON block 再构造 `PerceptionResult`

### `verify_post_test(user_input, misconception_tag, messages) -> bool`
定义位置：[classifiers.py](file:///workspace/src/classifiers.py#L33-L99)

- 用于“概念掌握验证”状态的闭环：学生必须用自己的话解释正确机制，且不包含事实错误。
- Mock 模式下直接返回 True（用于跑通流程）。

## 4.4 route_state（FSM 路由）
定义位置：[router.py](file:///workspace/src/router.py#L210-L281)

### `route_state(perception: PerceptionResult, memory: SessionMemory) -> (RouteDecision, SessionMemory)`
核心行为（按优先级）：

1. **S8 熔断**：如果上一轮已经是 `S8`，强制停留 `S8` 并将 `memory.aborted=True`（[`router.py`](file:///workspace/src/router.py#L215-L226)）
2. **风险处理**：如果 `perception.risk_flag`，进入 `S2`（拒答并重定向），并记录 `risk_events`（[`router.py`](file:///workspace/src/router.py#L228-L238)）
3. **更新当前迷思概念**：若识别到 `perception.misconception_tag`，写入 `memory.current_misconception` 并设置 topic（[`router.py`](file:///workspace/src/router.py#L240-L244)）
4. **基于 `transition_approved` 推进状态**：
   - S3 → S4 → S5 → S6（S7/S8 也可在满足条件时走向 S6）（[`router.py`](file:///workspace/src/router.py#L245-L261)）
5. **应用声明式规则（防环/降级/兜底）**：`apply_transition_rules()`（[`router.py`](file:///workspace/src/router.py#L152-L167)）
6. **选择策略**：`_choose_strategy()`（[`router.py`](file:///workspace/src/router.py#L169-L208)）
7. **写回 memory**：更新 `recent_states/used_strategies`，并维护 `turn_count/current_state`

### `update_after_turn(memory, ..., understanding_verified) -> SessionMemory`
定义位置：[router.py](file:///workspace/src/router.py#L283-L293)

- 将 `understanding_verified=True` 映射为 `memory.resolved=True`
- 截断 `recent_states/used_strategies/risk_events` 以限制长度
- 重置 `turn_guardrail_triggers`

## 4.5 generate_reply / generate_baseline_reply / generate_learning_report
定义位置：[generator.py](file:///workspace/src/generator.py)

### `_clean_reply(text: str) -> str`
代码：[generator.py](file:///workspace/src/generator.py#L15-L29)

- 去除 `<think>...</think>` 和常见“最终回复/分析”前缀，得到对外可展示的 `final_reply`。

### `generate_reply(user_input, decision, memory, messages) -> Dict[str, Any]`
代码：[generator.py](file:///workspace/src/generator.py#L68-L279)

- 产出字段：
  - `raw_reply`：模型原始输出
  - `final_reply`：清洗后的可展示回复
  - `reply_type/state/strategy/assembled_prompt`：便于分析与调试
- 关键点：
  - 数据源：`MISCONCEPTIONS`（来自 `data/misconceptions.json`）与 `KNOWLEDGE_CHUNKS`（来自 `data/knowledge_chunks.json`）
  - 依据 `decision.state` 与 `decision.meta`（如 sentiment/cognitive_state）向系统提示词注入不同的“教学约束/降级策略”
  - 若 `decision.meta.guardrail_feedback` 存在，会额外加入“系统安全警告”提示，推动模型改写而不是泄题

### `generate_baseline_reply(user_input, memory, messages) -> Dict[str, Any]`
代码：[generator.py](file:///workspace/src/generator.py#L280-L356)

- Baseline 版本使用的生成器：只做通用的苏格拉底式提问，不依赖 FSM 的具体状态/策略。

### `generate_learning_report(memory, messages) -> str`
代码：[generator.py](file:///workspace/src/generator.py#L364-L419)

- 在 `memory.resolved=True` 时生成 200–300 字学习报告（初始迷思、转变过程、最终掌握）。

## 4.6 apply_guardrails（输入/输出护栏）
定义位置：[guardrails.py](file:///workspace/src/guardrails.py#L186-L212)

### `apply_guardrails(user_input, intent, generated_text, misconception_tag, ...) -> Dict[str, Any]`
- 返回：
  - `guardrail_triggered: bool`
  - `guardrail_reason: str | None`（例如 Direct_Answer_Seek / Off_Topic / Answer_Leakage_LLM）
  - `answer_leakage_flag: bool`
- 行为：
  - 输入侧：`check_input()`（[`guardrails.py`](file:///workspace/src/guardrails.py#L22-L30)）
  - 输出侧：`check_output()`（[`guardrails.py`](file:///workspace/src/guardrails.py#L32-L185)）

## 4.7 SessionLogger（日志落盘）
定义位置：[logger.py](file:///workspace/src/logger.py#L13-L53)

- `log_turn(record)`：追加写入 `logs/turn_logs.jsonl`
- `log_session(record)`：追加写入 `logs/session_summary.jsonl`
- `info/warning/error`：写入 `logs/app.log`（可选同步到控制台）

