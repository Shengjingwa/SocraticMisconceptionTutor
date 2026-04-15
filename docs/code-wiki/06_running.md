# 6. 运行与复现

## 6.1 安装依赖
依赖列表见 [requirements.txt](file:///workspace/requirements.txt)。

```bash
pip install -r requirements.txt
```

## 6.2 环境变量与模型配置
配置实现：[`config.py`](file:///workspace/src/config.py)

必须（在线模式）：

```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

可选：

```bash
export LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export TUTOR_MODEL="qwen3.6-plus"
export JUDGE_MODEL="deepseek-v3.2"
export MAX_HISTORY_TURNS="6"
export SIMULATION_CONCURRENCY="6"
export SIMULATION_MAX_TURNS="10"
export SILENT_CONSOLE="1"
```

兼容变量：
- `DEEPSEEK_API_KEY`：当 `DASHSCOPE_API_KEY` 未设置时回退使用（[`config.py`](file:///workspace/src/config.py#L4-L8)）

## 6.3 交互式运行（终端）
入口：[`src/main.py`](file:///workspace/src/main.py)

```bash
python src/main.py
```

退出命令：`exit` / `quit` / `q`。

## 6.4 跑批量仿真（Multi-Agent Simulation）
入口：[`src/simulator.py`](file:///workspace/src/simulator.py)

```bash
python src/simulator.py
```

关键行为：
- 会在启动前删除 `logs/turn_logs.jsonl` 与 `logs/session_summary.jsonl`，避免污染历史结果（[`simulator.py`](file:///workspace/src/simulator.py#L185-L191)）
- 生成的会话会按版本跑：`Baseline` / `FSM` / `FSM+Guardrail`（[`simulator.py`](file:///workspace/src/simulator.py#L197-L204)）

快速冒烟（只跑 1×1×1）：

```bash
SIMULATION_SMOKE=1 python src/simulator.py
```

## 6.5 计算指标与导出人工审计表
入口：[`src/evaluator.py`](file:///workspace/src/evaluator.py)

```bash
python src/evaluator.py
```

输出：
- `results/summary_metrics.csv`
- `results/manual_audit.csv`

## 6.6 LLM 盲评（LLM-as-a-Judge）
入口：[`src/llm_judge.py`](file:///workspace/src/llm_judge.py)

```bash
python src/llm_judge.py
```

输出：`logs/evaluation_results.json`

## 6.7 Baseline / FSM / FSM+Guardrail 的切换方式
在应用层，`SocraticTutorApp` 默认 `system_version="FSM+Guardrail"`（[`main.py`](file:///workspace/src/main.py#L25-L33)）。

二次开发建议：
- 在创建 app 时显式传入 `system_version`，或在仿真脚本里设置 `app.system_version = v`（[`simulator.py`](file:///workspace/src/simulator.py#L131-L136)）。

## 6.8 Mock 模式说明
当缺少 `DASHSCOPE_API_KEY` 时：

- NLU：`classify_input()` 返回固定的 `PerceptionResult`（[`classifiers.py`](file:///workspace/src/classifiers.py#L117-L127)）
- 学生仿真：`SimulatedStudent` 会输出 mocked opening/reply（[`simulator.py`](file:///workspace/src/simulator.py#L68-L101)）
- Baseline 生成：会走 mocked 文本（[`generator.py`](file:///workspace/src/generator.py#L302-L313)）
- 盲评：`llm_judge.evaluate_session()` 返回 mock 评分（但提示语仍写着 “DEEPSEEK_API_KEY”，见 [`llm_judge.py`](file:///workspace/src/llm_judge.py#L19-L22)）

Mock 模式的目标是“让流水线可运行”，而不是提供真实评估结论。

