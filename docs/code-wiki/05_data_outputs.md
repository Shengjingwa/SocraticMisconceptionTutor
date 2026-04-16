# 5. 数据、日志与评估产物

## 5.1 静态数据（data/）

### data/misconceptions.json
链接：[misconceptions.json](file:///workspace/data/misconceptions.json)

- 作用：迷思概念主库（系统的“任务空间”），既用于诊断，也为生成与护栏提供约束信号。
- 典型字段（不同条目可能略有差异）：
  - `id`：如 `M-ELE-001`
  - `topic`：如 `电学`
  - `misconception_name / misconception_summary`
  - `student_expression_examples / diagnosis_keywords`
  - `core_science_points`
  - `counterexamples / analogies / reasoning_flaws`
  - `forbidden_direct_answers`：护栏用的“直接答案短语”黑名单
- 主要消费者：
  - 生成：[`generator.py`](file:///workspace/src/generator.py#L42-L48)
  - 护栏：[`guardrails.py`](file:///workspace/src/guardrails.py#L19-L45)
  - 指标计算：[`evaluator.py`](file:///workspace/src/evaluator.py#L9-L12)

### data/knowledge_chunks.json
链接：[knowledge_chunks.json](file:///workspace/data/knowledge_chunks.json)

- 作用：更偏“可提示的知识块”，在生成时作为支架素材。
- 典型字段：
  - `misconception_tag`：与 `misconceptions.json.id` 对齐
  - `core_science_points / counterexamples / analogies ...`
- 主要消费者：
  - 生成：[`generator.py`](file:///workspace/src/generator.py#L44-L48)
  - 教后测：[`classifiers.py`](file:///workspace/src/classifiers.py#L40-L56)

### data/simulation_profiles.json
链接：[simulation_profiles.json](file:///workspace/data/simulation_profiles.json)

- 作用：仿真学生画像，用于控制“固执/动摇/困惑”等对话行为模式。
- 典型字段：
  - `profile_id`：P1/P2/P3
  - `behavior_rule / followup_style`
  - `traits`：如 `cognitive_flexibility/defensiveness`
  - `dynamic_states`：触发改变的条件、后撤行为等
- 主要消费者：[`simulator.py`](file:///workspace/src/simulator.py#L19-L67)

## 5.2 运行日志（logs/）

### logs/turn_logs.jsonl（逐轮日志）
- 写入点：[`main.py`](file:///workspace/src/main.py#L53-L79) → [`logger.py`](file:///workspace/src/logger.py#L34-L38)
- 一行一个 JSON，核心字段（节选）：
  - `session_id / turn_id / timestamp`
  - `system_version / student_profile / topic / misconception_gt`
  - `student_input`
  - `intent_pred / misconception_pred / cognitive_state_pred / sentiment_pred / confidence`
  - `current_state / strategy_used`
  - `guardrail_triggered / guardrail_reason / answer_leakage_flag`
  - `raw_reply / final_reply`
  - `turn_end_resolved_flag`

### logs/session_summary.jsonl（会话汇总）
- 写入点：[`main.py`](file:///workspace/src/main.py#L151-L167) → [`logger.py`](file:///workspace/src/logger.py#L39-L42)
- 一行一个 JSON，核心字段（节选）：
  - `session_id / system_version / student_profile / topic`
  - `turn_count / first_detected_misconception / resolved_flag`
  - `guardrail_trigger_count / answer_leakage_count`
  - `abnormal_end_flag / termination_reason`

### logs/app.log（应用日志）
- 配置：[`logger.py`](file:///workspace/src/logger.py#L13-L33)
- 作用：记录运行过程信息、异常、护栏/仿真事件等。

### logs/evaluation_results.json（LLM 盲评结果）
- 生成脚本：[`llm_judge.py`](file:///workspace/src/llm_judge.py#L46-L92)
- 结构：以 `session_id` 为 key 的 dict，每个 value 包含：
  - `socratic_degree: 1..5`
  - `teaching_effectiveness: 1..5`
  - `reasoning: str`

## 5.3 评估产物（results/）

### results/summary_metrics.csv（汇总指标）
- 生成脚本：[`evaluator.py`](file:///workspace/src/evaluator.py#L7-L113)
- 指标字段：
  - `Identification Accuracy`：迷思概念识别准确率（仅统计带 GT 的 turn）
  - `Cognitive Correction Rate`：会话 resolved 率
  - `Avg Turns`：平均轮数
  - `Refusal Success Rate`：当意图为 Direct_Answer_Seek 时，进入 S2 或触发护栏的比例
  - `Guardrail Interception Rate`：护栏触发比例（turn 粒度）
  - `Answer Leakage Rate`：答案泄露比例（turn 粒度）
  - `Transition Success Rate`：状态变化次数 / 可变化步数（粗略反映推进效率）
  - `Abnormal Termination Rate`：异常终止比例

### results/manual_audit.csv（人工审计抽样）
- 生成脚本：[`evaluator.py`](file:///workspace/src/evaluator.py#L115-L157)
- 内容：每个版本抽样若干 session 的逐轮对话，预留人工评分与评语列。

## 5.4 实验套件产物（experiments/）
当使用 [`experiment_suite.py`](file:///workspace/src/experiment_suite.py) 时，会将每次运行的日志与评估产物隔离到 `experiments/suite_*` 下，避免覆盖仓库根目录的 `logs/` 与 `results/`。

目录结构（示例）：

```text
experiments/
  suite_YYYY-MM-DD_HH-MM-SS/
    run_01/
      logs/
        turn_logs.jsonl
        session_summary.jsonl
        evaluation_results.json  (若未 --no-judge)
      results/
        summary_metrics.csv
        manual_audit.csv
      pipeline.log
    aggregate_summary.csv
    aggregate_summary.md
```

- `pipeline.log`：该 run 的完整流水线输出（仿真 → 评估 → 盲评）
- `aggregate_summary.csv/.md`：对 `runs` 次执行的 `summary_metrics.csv` 做均值/方差/CI95 聚合（按版本汇总）
