# Analyze Latest Experiment Results v10 Spec

## Why
用户运行了一组新的实验并生成了新的日志文件，需要全面分析 `/logs` 和 `/results` 目录下的实验结果和日志，并找出存在的问题，以便为后续的优化提供依据。当前阶段明确要求仅进行分析，暂时无需修改代码文件。

## What Changes
- 全面读取并分析 `/logs` 和 `/results` 目录下的最新实验数据（包括刚生成的日志）。
- 提取关键性能指标（Metrics）、对话深度、误解纠正率等信息。
- 分析实验中出现的错误、异常或表现不佳的地方（如 guardrails 绕过、思考标签泄漏、JSON 格式错误等）。
- 撰写并提供详细的实验分析报告，明确当前系统存在的具体问题。

## Impact
- Affected specs: 无直接功能规格变化，但分析结果将为后续代码优化指明方向。
- Affected code: 无（当前为只读的分析和诊断任务）。

## ADDED Requirements
### Requirement: Analyze New Experiment Data
系统需要通过检索最新的日志和结果文件，全面评估最近一次实验的表现。

#### Scenario: 成功分析实验结果
- **WHEN** 代理读取并分析 `/logs` 和 `/results` 中的最新文件
- **THEN** 输出包含性能指标、问题清单的综合分析报告。
