# Tasks
- [x] Task 1: 第五章真实性审计（仅 suite_2026-04-16_14-42-05）
  - [x] 枚举 Chapter05.tex 中所有表格数据、百分比、结论性断言、案例 session id
  - [x] 在 suite 目录中逐项核对其可追溯性（`aggregate_summary.csv`、各 run 的 `summary_metrics.csv`、`session_summary.jsonl`、`turn_logs.jsonl`、`manual_audit.csv`）
  - [x] 对无法追溯或口径不清之处：改写为可核查表述或移除

- [x] Task 2: 指标口径与方法说明补强
  - [x] 为核心指标补充“定义—分母—数据来源—计算方式”说明（可用脚注或段落）
  - [x] 明确三版本差异仅在“控制与护栏策略”，其余运行条件保持一致（若 suite 日志支持）

- [x] Task 3: 增强中观分析（分主题/画像）
  - [x] 从 `session_summary.jsonl` 或 `evaluation_results.json` 生成按主题（电学/浮力）与画像（P1/P2/P3）的分组统计
  - [x] 在 Chapter05.tex 新增表格与“图待补绘”占位（例如分组柱状图/箱线图），并给出绘图要点
  - [x] 给出解释性分析（把差异与第4章机制对应）

- [x] Task 4: 增强微观证据链（案例扩写）
  - [x] 基于 `manual_audit.csv` 与 `turn_logs.jsonl`：补充至少 1 个成功案例与 1 个边界/失败案例
  - [x] 为每个案例增加“选取理由—关键轮次—机制对应—结果”四段式
  - [x] 将“仅文本对话的边界”与未来改进（多模态/更高权限讲授）写得更论文化

- [x] Task 5: 有效性威胁、局限与改进方向
  - [x] 增加/完善：样本量与模拟画像外推性、LLM Judge 偏差、指标间 trade-off 的解释
  - [x] 将改进方向与项目真实路线一致（仅基于仓库现有内容与 suite 日志可支持的推断）

- [x] Task 6: LaTeX 一致性与引用检查
  - [x] 不引入占位引用键；新增引用必须在 `docs/refs.bib` 存在且可追溯
  - [x] 表格/图编号、label、交叉引用一致；新增图片仅保留“图待补绘”占位

# Task Dependencies
- Task 3/4 依赖 Task 1（先确认哪些数据字段真实存在）
- Task 6 依赖 Task 1-5
