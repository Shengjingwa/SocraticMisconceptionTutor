# Day 3：实现护栏 + 构建仿真学生与测试集 计划

## 总结
实现苏格拉底式对话教育智能体 Day 3 的核心目标：完成输入与输出的安全护栏（Guardrails）机制，构建三种典型模拟学生画像，并准备用于后续仿真联调与实验的正常测试集及对抗测试集。

## 当前状态分析
- **已完成**：感知层 (`src/classifiers.py`)、决策层 (`src/router.py`)、执行层 (`src/generator.py`) 和日志层 (`src/logger.py`) 的最小原型。
- **现状缺口**：
  - `src/classifiers.py` 中具备初步的风险意图检测 (`detect_risk_flag`)，但缺少完整的拦截与重写逻辑模块 (`src/guardrails.py`)。
  - 缺乏针对输出回复的安全审核机制，可能会出现答案泄露。
  - 缺少自动化仿真测试所需的基础数据，包括学生画像配置和测试样例（正常/对抗）。

## 提议的变更

### 1. 实现护栏模块 (`src/guardrails.py`)
- **What**: 创建并实现独立的输入/输出护栏模块。
- **Why**: 防止学生直接套取答案、偏离主题，并避免系统在生成时无意中直接泄露科学结论。
- **How**:
  - 实现 `check_input(user_input: str, intent: str) -> dict`：检测是否为直接求答案或越界输入。
  - 实现 `check_output(generated_text: str, misconception_tag: str) -> dict`：审核回复内容，检查是否包含直接给出科学结论的违禁词（基于 `misconceptions.json` 中的 `forbidden_direct_answers` 和常规总结性词汇）。
  - 实现统筹函数 `apply_guardrails`：当触发风险时，利用已有的重定向模板生成安全回复（如“我不会直接给你标准答案...”）。

### 2. 集成护栏到主流程 (`src/main.py`)
- **What**: 在主流程中调用护栏模块。
- **Why**: 串联端到端流程，使拦截动作真实生效，并记录到日志中。
- **How**:
  - 在 `SocraticTutorApp.step` 方法中，在执行层生成回复之后（或决策层判断需拦截时），调用 `guardrails.py` 进行检查与可能的内容重写。
  - 确保将 `guardrail_triggered`、`guardrail_reason`、`answer_leakage_flag` 等护栏结果正确写入 `logger_instance.log_turn`。

### 3. 构建模拟学生画像 (`data/simulation_profiles.json`)
- **What**: 建立 3 类结构化学生画像数据。
- **Why**: 为 Day 4 的批量仿真对话提供固定人设，保证实验变量的可控性。
- **How**:
  - 编写 JSON 文件，定义 `P1`（固执型）、`P2`（动摇型）、`P3`（困惑型）。
  - 为每个画像配置特定的 `behavior_rule`（行为规则）、`opening_examples`（开场白示例）和 `followup_style`（后续追问风格）。

### 4. 准备正常测试集 (`data/test_cases_normal.json`)
- **What**: 构建包含 40 条起始输入的正常测试集。
- **Why**: 测试系统对于 4 个核心迷思概念（电流消耗模型、单极模型、重物必沉、浮力由深度决定）的识别和常规干预能力。
- **How**: 基于 `misconceptions.json` 中每个迷思点的 `student_expression_examples`，扩充与提取各 10 条测试用例，记录其预期的 `misconception_gt`。

### 5. 准备对抗测试集 (`data/adversarial_inputs.json`)
- **What**: 构建 24 条用于安全测试的对抗输入。
- **Why**: 专门验证系统护栏对于“骗取答案”行为的拦截稳定性。
- **How**: 设计涵盖“直接要答案”、“假装求助但要代答”、“诱导系统给结论”、“偏题/越界输入”四大类的对抗话术，验证系统的拒答成功率。

## 假设与决策
- **实现方式**：为满足 5 天 MVP 的时间要求，护栏的输入输出审核全部采用基于规则、关键词及正则匹配的方式，不引入额外的外部大模型审核调用。
- **数据管理**：测试集与画像均以 `.json` 格式静态存储在 `data/` 目录下，便于后续 `simulator.py` 批量读取。

## 验证步骤
1. **模块加载测试**：检查所有 `data/*.json` 文件能够被正确解析且无语法错误。
2. **人工联调测试**：运行 `python src/main.py`，分别输入“直接告诉我这题答案”以及正常迷思概念表述，观察系统是否正确触发护栏或正常进入诊断状态。
3. **日志验证**：完成交互后，检查 `logs/turn_logs.jsonl`，核对 `guardrail_triggered` 与 `guardrail_reason` 字段是否被如实记录。