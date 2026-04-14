# Tasks
- [ ] Task 1: 定位本次实验对应的最新主日志文件，并抽取关键信息（开始/结束时间、会话数量、关键 WARN/ERROR）。
  - [ ] 识别 `logs/pipeline_*.log` 最新文件名，并记录到报告中
  - [ ] 统计并归类关键异常：`Connection error`、`LLM Judge failed: 1 validation error`、`Falling back to rule-based only`
- [ ] Task 2: 汇总并解读核心量化指标（summary_metrics.csv）。
  - [ ] 对比 Baseline / FSM / FSM+Guardrail 的纠错率、平均轮次、泄题率、拒答成功率、护栏拦截率
  - [ ] 标注哪些指标可能被异常终止率污染（例如平均轮次被 0-turn error 会话拉低）
- [ ] Task 3: 基于 session_summary.jsonl 做“终止原因”与“主题/画像”分布分析。
  - [ ] 分版本统计 resolved / aborted / max_turns_reached / error 的占比
  - [ ] 分 topic（电学/浮力）与学生画像（P1/P2/P3）统计 error 的集中度
- [ ] Task 4: 结合 manual_audit.csv 与日志片段做案例分析（Case Study）。
  - [ ] 选择 1 个 resolved 会话（FSM+Guardrail）总结其教学路径亮点
  - [ ] 选择 1 个 error 或 max_turns 会话，判断其属于“教学失败”还是“工程失败”，并定位到日志行/原因
- [ ] Task 5: 输出最终中文分析报告与问题清单。
  - [ ] 按“结论 / 指标解读 / 失效模式 / 建议”结构撰写
  - [ ] 输出问题清单并按优先级排序（例如：API 连接稳定性、LLM Judge 输出 schema 稳定性、评测口径对异常会话的处理）

# Task Dependencies
- Task 5 depends on Task 1-4
