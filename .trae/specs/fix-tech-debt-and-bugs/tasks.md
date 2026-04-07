# Tasks

- [x] Task 1: 修复全局异常与错误吞没问题
  - [x] SubTask 1.1: 在 `src/main.py` 的 `app_graph.invoke` 调用外层增加全局 `try-except` 块，捕获异常并返回友好的错误提示。
  - [x] SubTask 1.2: 在 `src/classifiers.py` 中为 NLU 的 `try-except` 增加详细的 `logger.error`，记录底层解析失败的原始报错。
  - [x] SubTask 1.3: 为 `src/generator.py` 和 `src/guardrails.py` 读取本地 JSON 文件的地方（如 `load_json`）添加 `json.JSONDecodeError` 和 `FileNotFoundError` 的处理，并在失败时提供默认空字典或抛出清晰的错误日志。

- [x] Task 2: 增强 LLM 调用的健壮性与重试机制
  - [x] SubTask 2.1: 在 `src/generator.py` 和 `src/classifiers.py` 中，使用 `tenacity` 库（或其他重试机制）包装 LLM 调用，捕获 `Timeout` 或 API 报错，增加退避重试策略。

- [x] Task 3: 消除架构与 LangGraph 死循环/卡死风险
  - [x] SubTask 3.1: 在 `src/graph.py` 的 `guardrail_node` 中增加重试次数计数（可以在 `GraphState` 的 `decision.meta` 中记录），超过最大重试次数时强制覆盖生成结果为安全兜底话术，并设置 `regeneration_required=False` 打断死循环。
  - [x] SubTask 3.2: 在 `src/router.py` 中，为非 `S4` 状态（如 `S3`、`S5` 等）增加最大轮次判断机制，当连续停留在某状态超过阈值时，强制流转至 `S5` 结束或进行干预。
  - [x] SubTask 3.3: 在 `src/router.py` 的 `RouteDecision` 实例化时，使用 `.get()` 方法安全获取 `STATE_NAMES` 字典中的值，并在找不到时提供默认状态名（如 `Unknown_State`），避免 `KeyError` 崩溃。

- [x] Task 4: 提升提示词鲁棒性与 Pydantic 容错
  - [x] SubTask 4.1: 在 `src/classifiers.py` 的 NLU 识别中，如果 Pydantic 直接解析枚举失败，增加基于文本清洗（如 `strip()`、去除多余引号等）的预处理逻辑，或使用宽容度更高的基础模型解析后手动映射。
  - [x] SubTask 4.2: 排查项目中的提示词拼接（尤其是被提及的注入风险），确保全部使用 `SystemMessage` 和 `HumanMessage` 进行角色隔离，不使用 f-string 直接将用户输入拼接在系统指令中。
  - [x] SubTask 4.3: 在 `src/guardrails.py` 中，将精确的字符串匹配（如 `if "正确答案是" in text`）重构为更鲁棒的正则表达式匹配或模糊匹配（如允许中间有空格或微小变体）。

- [x] Task 5: 消除硬编码技术债与修复类型提示
  - [x] SubTask 5.1: 统一提取 `src/graph.py`、`src/classifiers.py`、`src/generator.py` 中的硬编码 `"dummy_key"`，并确保环境变量 `DEEPSEEK_API_KEY` 获取具有统一入口。
  - [x] SubTask 5.2: 在 `src/evaluator.py` 和 `src/simulator.py` 中，将硬编码的相对路径（如 `'logs/turn_logs.jsonl'`）重构为基于 `os.path.dirname(__file__)` 计算的绝对路径，确保在任意目录下执行脚本均不报错。
  - [x] SubTask 5.3: 为 `src/evaluator.py` 和 `src/simulator.py` 中的类方法（如 `evaluate()`、`run_simulation()` 等）和脚本的 `main()` 函数补全 `-> None` 等返回类型提示。

# Task Dependencies
- [Task 3] 依赖于 [Task 1] 中对状态追踪的正确日志记录。
- 所有 Task 可由不同 Agent 并行或按顺序执行。