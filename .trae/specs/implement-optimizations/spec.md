# Implement Optimizations Spec

## Why
根据综合评估报告 `docs/comprehensive_evaluation.md` 中的建议，我们需要落实短期（工程与算法）和中期（教育学与策略）的优化目标，以提高分类器准确度、增强系统并发能力、引入个性化的教学策略并建立多维度的对话评估机制。

## What Changes
- **短期优化（工程与算法）**：
  - 优化 `src/classifiers.py`：在 NLU 的 System Prompt 中引入 Few-shot 示例，提升“认知状态”分类的准确性，防止学生未掌握就被误判为“概念掌握验证”。
  - 优化 `src/main.py`：为 `SocraticTutorApp` 增加异步执行方法 `astep()`，底层调用 `app_graph.ainvoke()`，提升系统的异步并发能力。
- **中期优化（教育学与策略）**：
  - 优化 `src/router.py`：引入基于上下文的**动态策略推荐算法**（可基于简单的启发式规则或 LLM 辅助），取代目前同一状态下随机或硬编码的策略选择。
  - 新增 `src/llm_judge.py`：开发 LLM-as-a-Judge 评估脚本，对日志中的历史对话（如 `turn_logs.jsonl`）进行“苏格拉底度（Socratic Degree）”和“教学有效性（Teaching Effectiveness）”的打分。

## Impact
- Affected specs: 无直接冲突。
- Affected code: 
  - `src/classifiers.py` (修改 System Prompt)
  - `src/main.py` (新增 `astep` 异步方法)
  - `src/router.py` (修改 `_choose_strategy` 方法逻辑)
  - `src/llm_judge.py` (新增脚本文件)

## MODIFIED Requirements
### Requirement: Classifier Accuracy
系统应通过提供 Few-shot examples 提高 NLU 分类的鲁棒性。

### Requirement: Concurrency Support
系统应提供支持异步的接口 `astep`，以便在未来整合至高并发 Web 框架（如 FastAPI）。

## ADDED Requirements
### Requirement: Dynamic Strategy Recommendation
系统在不同状态下应当根据历史上下文或轮次，动态选择最合适的教学策略（如在多次认知冲突后提供类比）。

### Requirement: LLM-as-a-Judge Evaluator
系统需要提供独立脚本，读取对话日志，并利用 LLM 自动给出 1-5 分的苏格拉底度与有效性评分。
