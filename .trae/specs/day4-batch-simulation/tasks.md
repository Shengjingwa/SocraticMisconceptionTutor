# Tasks

- [x] Task 1: 定义实验版本与配置
  - [x] SubTask 1.1: 创建 `docs/experiment_versions.md`，记录 Baseline、FSM、FSM+Guardrail 三个版本的定义。
  - [x] SubTask 1.2: 修改 `src/main.py` 和相关流转逻辑（如 `src/graph.py`），支持根据传入的 `system_version` 参数（Baseline / FSM / FSM+Guardrail）切换执行链路。

- [x] Task 2: 编写仿真运行脚本
  - [x] SubTask 2.1: 创建 `src/simulator.py`。
  - [x] SubTask 2.2: 实现基于大模型（DeepSeek）的模拟学生类 `SimulatedStudent`，使其能根据设定的 `profile`（固执型/动摇型/困惑型）和迷思概念（从 `misconceptions.json` 获取）生成回复。
  - [x] SubTask 2.3: 实现主控循环，执行 4(迷思) × 3(画像) × 3(版本) × 5(次数) = 180 组对话（如因接口限速可调为3次即108组），并将日志落盘。

- [x] Task 3: 批量跑仿真实验
  - [x] SubTask 3.1: 运行 `src/simulator.py` 完成自动对话测试，确保 `logs/turn_logs.jsonl` 和 `logs/session_summary.jsonl` 中正确记录各轮次与各会话的数据（需附带 `system_version` 等标识）。

- [x] Task 4: 自动抽取指标
  - [x] SubTask 4.1: 创建 `src/evaluator.py`，用于读取并解析所有日志文件。
  - [x] SubTask 4.2: 实现 8 项核心指标的计算逻辑：识别准确率、认知修正率、平均轮数、拒答成功率、护栏拦截率、答案泄露率、状态流转成功率、异常中断率。
  - [x] SubTask 4.3: 将计算结果按实验设计模板要求的格式输出至 `results/summary_metrics.csv`（包含总体结果表和版本对比汇总表）。

- [x] Task 5: 准备人工抽样校验文件
  - [x] SubTask 5.1: 编写脚本或手动整理，从仿真结果中每个版本抽样生成包含 10-15 组对话记录的 `results/manual_audit.csv`（或 Markdown 表格），供后续人工填写校验反馈。