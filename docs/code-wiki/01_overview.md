# 1. 项目总览

## 1.1 目标与问题定义
该项目实现了一个面向“初中物理迷思概念（misconception）纠正”的苏格拉底式对话导师系统。核心约束是：

- 不能直接把“标准答案/最终结论”喂给学生。
- 要通过提问、类比、思想实验、反例等方式制造认知冲突并推进概念重构。
- 要能批量仿真与评估，做 Baseline / FSM / FSM+Guardrail 的消融对比。

## 1.2 代码入口与核心组件
- 交互式 App 入口：[`src/main.py`](file:///workspace/src/main.py)
  - `SocraticTutorApp.chat()` 提供终端对话体验。
  - `SocraticTutorApp.step()/astep()` 将一次用户输入送入 LangGraph 工作流。
- LangGraph 工作流：[`src/tutor_graph.py`](file:///workspace/src/tutor_graph.py)
  - 编排“感知 → 路由 → 生成 → 护栏 → 记忆写回”的全链路。
  - 内置版本开关：`Baseline` vs `FSM` vs `FSM+Guardrail`。

## 1.3 仓库目录结构
```text
src/        核心逻辑（工作流编排、分类、FSM、生成、护栏、仿真、评估）
data/       静态数据（迷思概念库、知识块、学生画像）
logs/       运行日志（jsonl/json + app.log）
results/    评估输出（csv）
```

## 1.4 快速定位（按问题）
- “一次对话轮次到底怎么走？”：[`src/tutor_graph.py`](file:///workspace/src/tutor_graph.py)
- “系统状态机怎么设计？”：[`src/router.py`](file:///workspace/src/router.py)
- “怎么防止直接给答案？”：[`src/guardrails.py`](file:///workspace/src/guardrails.py)
- “prompt 怎么拼、怎么控制输出风格？”：[`src/generator.py`](file:///workspace/src/generator.py)
- “怎么跑批量实验与评估？”：[`src/simulator.py`](file:///workspace/src/simulator.py)、[`src/evaluator.py`](file:///workspace/src/evaluator.py)、[`src/llm_judge.py`](file:///workspace/src/llm_judge.py)

