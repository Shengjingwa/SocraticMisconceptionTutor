# Tasks
- [x] Task 1: 盘点实验产物与完整性（run_01/run_02）
  - [x] 读取 suite 根目录文件清单（aggregate_summary.*、run_* 子目录）
  - [x] 校验 run_01 是否包含 logs/results/pipeline 三类产物
  - [x] 校验 run_02 是否包含 logs/results/pipeline 三类产物，并列出缺失项（若未跑完则标注）
- [x] Task 2: 生成定量汇总与二次统计（优先 run_01，补充 run_02 可得项）
  - [x] 读取 run_01 summary_metrics.csv 与 suite aggregate_summary.csv，汇总版本级关键指标
  - [x] 从 run_01 session_summary.jsonl 统计 resolved/termination_reason/turn_count，并按 profile 分组
  - [x] 从 run_01 turn_logs.jsonl 统计泄露、护栏触发次数与原因分布，并提取典型样例
  - [x] 统计诊断混淆（重点 M-ELE-002→M-ELE-001）并输出 top confusions
  - [x] 对 run_02 仅做“存在的字段统计”（如有 session_summary/turn_logs），并明确不可比原因（缺失 summary_metrics/evaluation_results 等）
- [x] Task 3: 汇总盲评结果（若存在）
  - [x] 读取 run_01 evaluation_results.json，计算各版本 socratic/effectiveness 均值与分布
  - [x] 若 run_02 缺失 evaluation_results.json，则在报告中明确标注
- [x] Task 4: 输出分析报告（仅对话输出，不落盘）
  - [x] 输出“总体结论（2-3句）+ 指标解读 + 失败模式案例 + 问题清单（证据/原因/建议）+ 未完备 run 的影响说明”

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 1
- Task 4 depends on Task 2 and Task 3
