# 项目当前存在的问题与改进建议分析

基于对项目 `src/` 目录下核心代码（包括 `graph.py`, `router.py`, `classifiers.py`, `generator.py`, `guardrails.py`, `main.py` 等）的走查，当前项目主要存在以下问题及可改进的空间：

## 1. 上下文记忆丢失（关键缺陷）
* **问题描述**：在 `generator.py` 和 `classifiers.py` 中调用大模型时，**并没有传入完整的多轮对话历史**（Message History）。目前每次请求仅传入了当前的 `user_input` 和一个名为 `history_summary` 的字段。
* **深层原因**：在 `main.py` 和 `router.py` 的 `update_after_turn` 逻辑中，`history_summary` 仅仅被赋值为系统最后一次回复的前120个字符（`final_reply[:120]`）。这导致智能体实际上是**无记忆**的，大模型完全不知道前几轮学生说了什么、自己又引导了什么，使得深度的苏格拉底式对话难以连贯。
* **改进建议**：在 `SessionMemory` 中引入真正的 `messages` 列表（如 LangChain 的 BaseMessage 序列）保存完整对话历史，并在生成和意图识别时传入；或实现真正的 LLM 对话摘要更新机制。

## 2. 提示词构建方式欠佳 (Prompt Engineering)
* **问题描述**：在 `generator.py` 的 `generate_reply` 函数中，系统提示词（System Prompt）是通过将一个 Python 字典直接 `json.dumps` 序列化为 JSON 字符串传递给大模型的。
* **改进建议**：虽然大模型能解析 JSON，但其对自然语言的指令依从性通常更好。建议使用 `ChatPromptTemplate` 或多行字符串（f-string），将当前状态、策略、核心知识点（反例、类比）和护栏规则格式化为结构清晰、语义连贯的自然语言 Prompt。

## 3. 输出安全护栏过于脆弱 (Guardrails)
* **问题描述**：`guardrails.py` 中的 `check_output` 函数完全依赖**硬编码的正则表达式**（如 `r"正确答案\s*是"`）和简单的子串匹配来检测是否“泄露答案”。
* **改进建议**：这种基于规则的匹配极易被大模型换种说法绕过（例如“其实真实的物理规律是...”）。对于教育引导场景，建议引入 LLM-as-a-Judge 机制，通过一个低延迟的模型专门评估回复是否直接给出了结论，或者使用更先进的语义相似度检测。

## 4. 配置硬编码与缺乏灵活性
* **问题描述**：模型名称（`deepseek-chat`）、API Base URL、重试次数（Tenacity 配置）等参数散落在 `classifiers.py`、`generator.py` 和 `simulator.py` 等多个独立文件中。
* **改进建议**：引入统一的配置管理模块（如 `config.py` 结合 `.env` 解析），集中管理模型参数、URL 和系统超参，便于后续一键切换模型（如测试 GPT-4o 或本地模型）或调整实验参数。

## 5. 状态机流转逻辑的硬编码与脆弱性 (Router)
* **问题描述**：`router.py` 中的 `route_state` 函数包含了复杂的 `if-elif` 嵌套逻辑，并且使用了硬编码的列表切片（如 `memory.recent_states[-2:] == ["S4", "S4"]`）来强行控制死循环防范和状态跳转。
* **改进建议**：随着状态机变复杂，这种面向过程的硬编码极难维护。建议将状态转移逻辑抽象为声明式的转移矩阵（Transition Matrix），或者更充分地将这部分逻辑交给 LangGraph 的条件边（Conditional Edges）来进行图级别的路由。

## 6. NLU 解析与降级策略鲁棒性不足 (Classifiers)
* **问题描述**：在 `classifiers.py` 中，如果 `with_structured_output` 解析失败，后备逻辑（Fallback）仅仅是简单的去除 Markdown 符号后执行 `json.loads`。一旦模型输出包含额外的解释性文字，解析依然会直接崩溃。
* **改进建议**：在 Fallback 逻辑中使用更健壮的 JSON 提取工具（例如正则提取首尾的 `{}` 块），并且可以配置默认的安全兜底决策，防止解析失败导致整个服务链路中断。

---
*注：按您的要求，本分析报告仅在此列出，无需修改任务文件或执行实际代码变更。*