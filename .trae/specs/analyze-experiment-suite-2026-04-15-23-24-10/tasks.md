# Tasks
- [x] Task 1: 盘点实验产物与完整性
  - [x] 读取 suite 根目录文件清单（aggregate_summary.*、run_* 子目录）
  - [x] 校验 run_01 是否包含 logs/results/pipeline 三类产物
- [x] Task 2: 生成定量汇总与二次统计
  - [x] 读取 summary_metrics.csv 与 aggregate_summary.csv，汇总版本级关键指标
  - [x] 从 session_summary.jsonl 统计 resolved/termination_reason/turn_count，并按 profile 分组
  - [x] 从 turn_logs.jsonl 统计泄露、护栏触发次数与原因分布，并提取典型样例
  - [x] 统计诊断混淆（重点 M-ELE-002→M-ELE-001）并输出 top confusions
- [x] Task 3: 汇总盲评结果（若存在）
  - [x] 读取 evaluation_results.json，计算各版本 socratic/effectiveness 均值与分布
- [x] Task 4: 输出分析报告（仅对话输出，不落盘）
  - [x] 输出“总体结论（2-3句）+ 指标解读 + 失败模式案例 + 问题清单（证据/原因/建议）”

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 1
- Task 4 depends on Task 2 and Task 3
