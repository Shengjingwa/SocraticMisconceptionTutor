# 2. 整体架构

## 2.1 分层视角
该仓库可以按职责分为 7 层（从运行时主链路出发）：

- **应用层**：会话封装、交互式聊天、日志落盘（[`main.py`](file:///workspace/src/main.py)）
- **编排层**：LangGraph 节点与边、重试/再生成策略、记忆写回（[`tutor_graph.py`](file:///workspace/src/tutor_graph.py)）
- **感知层**：NLU 分类（意图/迷思概念/认知状态/情绪）与“教后测”验证（[`classifiers.py`](file:///workspace/src/classifiers.py)）
- **决策层**：FSM 状态机、策略选择、防环与熔断（[`router.py`](file:///workspace/src/router.py)）
- **生成层**：Prompt 拼装、输出清洗、学习报告（[`generator.py`](file:///workspace/src/generator.py)）
- **安全层**：输入/输出护栏（规则 + LLM-as-a-Judge），并支持“严格/弹性/事实兜底”模式（[`guardrails.py`](file:///workspace/src/guardrails.py)）
- **评估层**：多会话仿真、指标汇总、抽样审计、LLM 盲评（[`simulator.py`](file:///workspace/src/simulator.py)、[`evaluator.py`](file:///workspace/src/evaluator.py)、[`llm_judge.py`](file:///workspace/src/llm_judge.py)）

## 2.2 运行时主链路（一次对话轮次）
一次 `SocraticTutorApp.step(user_input)` 的核心流程如下：

1. **构建初始状态**：`system_version/user_input/memory/messages`（[`main.py`](file:///workspace/src/main.py#L103-L125)）
2. **进入 LangGraph**：`app_graph.invoke()`（[`main.py`](file:///workspace/src/main.py#L112-L125)）
3. **classify_node**（感知）：`classify_input()` 输出 `PerceptionResult`（[`tutor_graph.py`](file:///workspace/src/tutor_graph.py#L43-L52)）
4. **route_node**（决策）：`route_state()` 输出 `RouteDecision` 与更新后的 `SessionMemory`（[`tutor_graph.py`](file:///workspace/src/tutor_graph.py#L54-L58)）
5. **generate_node**（生成）：`generate_reply()` 生成 `raw_reply/final_reply`（[`tutor_graph.py`](file:///workspace/src/tutor_graph.py#L60-L66)）
6. **guardrail_node**（安全）：`apply_guardrails()` 检测与“再生成”控制（[`tutor_graph.py`](file:///workspace/src/tutor_graph.py#L82-L147)）
7. **finalize_node**（记忆写回）：写入 `AIMessage(raw_reply)`，必要时压缩历史并更新 `memory.history_summary`（[`tutor_graph.py`](file:///workspace/src/tutor_graph.py#L149-L182)）
8. **应用层后处理**：落盘 turn log、触发 learning report、更新会话指标（[`main.py`](file:///workspace/src/main.py#L35-L101)）

## 2.3 版本开关（消融对比）
版本由 `GraphState.system_version` 控制（默认 `"FSM+Guardrail"`）：

- **Baseline**：走 `baseline_node` 直接生成通用引导回复（不做 NLU/FSM），但仍会进入护栏节点（[`tutor_graph.py`](file:///workspace/src/tutor_graph.py#L68-L73)、[`tutor_graph.py`](file:///workspace/src/tutor_graph.py#L183-L206)）
- **FSM**：走 NLU + FSM + 生成，但在护栏节点中强制 `guardrail_triggered = False`（即仅记录，不拦截）（[`tutor_graph.py`](file:///workspace/src/tutor_graph.py#L110-L113)）
- **FSM+Guardrail**：完整链路 + 真实拦截/再生成（同上护栏节点）

## 2.4 状态（State）与记忆（Memory）
运行时共享状态结构为 `GraphState`（[`state.py`](file:///workspace/src/state.py#L6-L24)），其中：

- `memory: SessionMemory`：跨轮次持久化（当前状态、迷思概念、摘要、策略历史、护栏统计等）
- `messages: list[AnyMessage]`：对话消息序列（LangGraph 的 message reducer 负责追加/删除）
- `perception/decision/generation/guardrail_result`：本轮中间产物

`SessionMemory` 的字段定义见 [`router.py`](file:///workspace/src/router.py#L27-L41)。

## 2.5 FSM 状态语义（S0–S8）
状态名映射在 `STATE_NAMES`（[`router.py`](file:///workspace/src/router.py#L58-L68)）：

- `S2`：拒答并重定向（Refusal_And_Guidance）
- `S3`：错误概念诊断（Misconception_Diagnosis）
- `S4`：认知冲突（Cognitive_Conflict）
- `S5`：支架式引导（Scaffolding_Guidance）
- `S6`：验证与加深（Verification_Deepening）
- `S7`：事实兜底（Fact_Grounding）
- `S8`：承认并搁置/结束（Acknowledge_and_Park）

状态转移采用 “Assessor(=NLU) 给出 `transition_approved` → FSM 推进” 的机制（详见 [4. 关键类与函数](file:///workspace/docs/code-wiki/04_key_apis.md)）。

