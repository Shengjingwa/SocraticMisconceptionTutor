# Run Simple Test Spec

## Why
需要使用真实的 `DEEPSEEK_API_KEY` 对项目进行简单的端到端测试，验证系统（特别是大模型调用和柔性护栏机制）能否正确运行，同时避免运行完整的耗时仿真测试以节省时间和 token。

## What Changes
- 编写并执行一个轻量级的测试脚本，或者直接运行 `src/main.py` 中的 `demo()` 函数。
- 传入提供的 API Key 进行真实调用，验证系统响应。

## Impact
- Affected specs: 无
- Affected code: 测试脚本或直接命令行执行。

## ADDED Requirements
### Requirement: 简单验证测试
The system SHALL provide 能够快速验证整个问答链路与大模型集成可用性的能力，且无需启动庞大的全量评估。

#### Scenario: 成功验证测试用例
- **WHEN** 运行轻量级测试脚本且环境变量中注入真实 API Key
- **THEN** 应该输出带大模型实际生成的自然语言响应，且无运行错误或鉴权异常。
