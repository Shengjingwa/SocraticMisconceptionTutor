# Tasks
- [x] Task 1: 创建 `docs/experiment_analysis.md` 文件。
  - [x] SubTask 1.1: 撰写 **Identification Accuracy** 0% 到 100% 跃升的原因（如 Baseline 缺乏结构化输出，FSM+Guardrail 引入了结构化的意图/迷思概念抽取和 JSON Mode 约束）。
  - [x] SubTask 1.2: 撰写 **Cognitive Correction Rate** 整体偏低且逐步提升的原因（如纠正根深蒂固的物理迷思概念难度极大；FSM+Guardrail 的澄清、反例、类比等策略通过拒绝直接回答强制学生深入思考）。
  - [x] SubTask 1.3: 撰写 **Avg Turns** 短暂（1.19 - 1.40）的原因（可能因为学生模拟器模型在被反问时容易触发终止条件，或者模拟器在未成功纠正时放弃）。
  - [x] SubTask 1.4: 撰写 **Refusal Success Rate** 与 **Guardrail Interception Rate** 提升的原因（如护栏机制成功识别 `Direct_Answer_Seek` 意图，并强行拉回教学主线）。
  - [x] SubTask 1.5: 撰写 **Answer Leakage Rate** 为 0% 与 **Transition Success Rate** 100% 的原因（表明大模型基座指令遵循能力强，且硬编码的状态机路由鲁棒性极高）。