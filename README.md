# Socratic Misconception Tutor

面向初中物理迷思概念纠正的生成式 AI 苏格拉底导师系统。

本项目实现了一套可复现的对话智能体架构：用有限状态机（FSM）约束苏格拉底式教学流程，用动态安全护栏（Guardrails）抑制“直接给答案”，并通过多智能体仿真（Multi-Agent Simulation）与 LLM-as-a-Judge 构建自动化评估流水线，支持 Baseline / FSM / FSM+Guardrail 的消融对比。

## 功能概览
- 教学状态机（FSM）：S0–S8 的教学状态与防环规则，用于把对话推进到“诊断 → 认知冲突 → 支架 → 验证/兜底/搁置”等阶段（见 [router.py](file:///workspace/src/router.py)、[tutor_graph.py](file:///workspace/src/tutor_graph.py)）。
- 动态安全护栏（Guardrails）：输入侧拦截直接要答案/偏题；输出侧结合规则与 LLM 裁判检测“答案泄露”，并对思想实验/归谬、类比展开、确认性总结等启发式教学提供豁免（见 [guardrails.py](file:///workspace/src/guardrails.py)）。
- 生成模块：将“当前状态 + 策略目标 + 错误概念库/知识块”组装成对话提示，生成 1–3 句口语化引导回复，并清理 `<think>` 内容（见 [generator.py](file:///workspace/src/generator.py)）。
- 多智能体仿真：用学生画像（P1 固执 / P2 动摇 / P3 困惑）+ 迷思概念库批量生成对话会话，形成实验日志（见 [simulator.py](file:///workspace/src/simulator.py)、[data/](file:///workspace/data)）。
- 自动化评估：从日志计算量化指标，并对抽样会话输出人工审计表；另提供 LLM-as-a-Judge 盲评脚本（见 [evaluator.py](file:///workspace/src/evaluator.py)、[llm_judge.py](file:///workspace/src/llm_judge.py)）。

## 快速开始

### 环境要求
- Python >= 3.9

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置模型与 API Key
项目使用 OpenAI-compatible 的 `ChatOpenAI` 客户端，通过环境变量配置（见 [config.py](file:///workspace/src/config.py)）：

```bash
export DASHSCOPE_API_KEY="your_api_key_here"
export LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export TUTOR_MODEL="qwen3.6-plus"
export JUDGE_MODEL="deepseek-v3.2"
```

可选参数：
- `DEEPSEEK_API_KEY`：兼容旧变量名（仅在未设置 `DASHSCOPE_API_KEY` 时回退使用）
- `MAX_HISTORY_TURNS`：对话历史窗口（默认 6）
- `SIMULATION_CONCURRENCY`：仿真并发（默认 6）
- `SIMULATION_MAX_TURNS`：单会话最大轮数（默认 10）
- `SIMULATION_SMOKE=1`：只跑 1 个迷思概念 × 1 个画像 × 1 个版本，用于快速冒烟
- `SILENT_CONSOLE=1`：关闭控制台日志输出
- `LOG_DIR`：运行日志输出目录（默认 `logs/`，影响 `turn_logs.jsonl` / `session_summary.jsonl` / `evaluation_results.json` / `app.log`）
- `RESULTS_DIR`：评估产物输出目录（默认 `results/`，影响 `summary_metrics.csv` / `manual_audit.csv`）

未配置 API Key 时，系统会进入 Mock 模式：
- 学生仿真与部分分类/评分会走 Mock 分支，便于验证流水线是否能跑通（见 [simulator.py](file:///workspace/src/simulator.py)、[classifiers.py](file:///workspace/src/classifiers.py)、[llm_judge.py](file:///workspace/src/llm_judge.py)）。

### 交互式体验（终端）
```bash
python src/main.py
```

### 运行完整实验流水线
按顺序执行：仿真 → 指标评估 → LLM 盲评。

```bash
python src/simulator.py
python src/evaluator.py
python src/llm_judge.py
```

### 一键跑实验套件（推荐）
入口：[experiment_suite.py](file:///workspace/src/experiment_suite.py)。会将每次运行的日志与结果隔离到 `experiments/suite_*` 下，避免覆盖仓库根目录的 `logs/` 与 `results/`。

```bash
python src/experiment_suite.py
```

常用参数/环境变量：
- `--runs` 或 `EXP_RUNS`：运行次数（默认 1）
- `--out-dir` 或 `EXP_OUT_DIR`：输出根目录（默认 `experiments/`）
- `--seed` 或 `EXP_SEED`：随机种子（默认 42，会按 run 递增）
- `--no-judge`：跳过 `llm_judge.py`

也可用日志文件保存完整输出：

```bash
LOG_FILE="logs/pipeline_$(date +%F_%H-%M-%S).log"
(
  python src/simulator.py &&
  python src/evaluator.py &&
  python src/llm_judge.py
) > "$LOG_FILE" 2>&1
echo "Saved to: $LOG_FILE"
```

## 输出与数据格式

### 运行日志
- `logs/turn_logs.jsonl`：逐轮记录（输入、状态、策略、护栏触发、回复等）
- `logs/session_summary.jsonl`：会话级汇总（轮数、resolved、护栏触发次数等）
- `logs/evaluation_results.json`：LLM 盲评结果（socratic_degree / teaching_effectiveness / reasoning）

### 评估产物
- `results/summary_metrics.csv`：版本维度汇总指标（由 [evaluator.py](file:///workspace/src/evaluator.py) 生成）
- `results/manual_audit.csv`：抽样会话审计表（由 [evaluator.py](file:///workspace/src/evaluator.py) 生成，便于人工复核）

### 实验套件目录（experiments/）
当使用 [experiment_suite.py](file:///workspace/src/experiment_suite.py) 时，每次执行会生成：

```text
experiments/
  suite_YYYY-MM-DD_HH-MM-SS/
    run_01/
      logs/turn_logs.jsonl
      logs/session_summary.jsonl
      logs/evaluation_results.json  (若未 --no-judge)
      results/summary_metrics.csv
      results/manual_audit.csv
      pipeline.log
    aggregate_summary.csv
    aggregate_summary.md
```

示例（来自当前仓库一次运行结果）：

```text
Version,Identification Accuracy,Cognitive Correction Rate,Avg Turns,Refusal Success Rate,Guardrail Interception Rate,Answer Leakage Rate,Transition Success Rate,Abnormal Termination Rate
Baseline,100.00%,0.00%,13.00,0.00%,0.00%,3.21%,0.00%,0.00%
FSM,84.27%,66.67%,7.42,0.00%,0.00%,0.00%,36.36%,0.00%
FSM+Guardrail,96.55%,58.33%,7.25,0.00%,1.15%,0.00%,37.33%,0.00%
```

## 项目结构
```text
src/        核心逻辑（FSM/分类/生成/护栏/仿真/评估）
data/       静态数据（迷思概念库、知识块、学生画像）
logs/       运行与实验日志（jsonl / json）
results/    评估输出（csv）
```

## 复现建议
- 固定实验配置：确保 `data/misconceptions.json`、`data/simulation_profiles.json` 一致。
- 记录模型版本与推理参数：建议在论文附录中记录 `LLM_BASE_URL`、`TUTOR_MODEL`、`JUDGE_MODEL`、温度等信息（见 [config.py](file:///workspace/src/config.py)）。
- 冒烟验证：使用 `SIMULATION_SMOKE=1` 快速确认环境与 API 配置无误，再扩大规模。

## 贡献
- 欢迎提交 Issue / PR：状态机策略、护栏豁免规则、评估指标、数据集扩展等。
- 建议提供：复现步骤、期望/实际行为、相关日志片段（可脱敏）。

## 引用
- Repo: https://github.com/Shengjingwa/SocraticMisconceptionTutor
- 建议在论文/报告中附上仓库链接与 commit hash 以便复现（例如：`3ef1ea3`）。

## 许可证
仓库当前未包含许可证文件。如需开源分发，建议补充 `LICENSE` 并在此处声明许可证类型。
