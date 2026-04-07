# 修复模拟器参数与日志记录器缺失属性 Spec

## Why
在测试环节中出现了两个阻塞性报错：
1. **参数不匹配**：`simulator.py` 在初始化 `SocraticTutorApp` 时传入了 `system_version`，但在最近的技术债清理中，`main.py` 里的 `SocraticTutorApp.__init__` 已移除了该参数，导致模拟器抛出 `TypeError` 崩溃。
2. **Logger属性缺失**：当 NLU 调用 DeepSeek 的 `with_structured_output` 失败（如遇到 400 不支持的格式）触发 fallback 时，`classifiers.py` 和 `main.py` 试图调用 `logger_instance.warning` 和 `logger_instance.error`。然而，当前的 `logger_instance` (`SessionLogger`) 并没有实现这些标准日志方法，导致进一步抛出 `AttributeError` 从而完全掩盖了真实错误。

## What Changes
- 修改 `src/simulator.py`，在实例化 `SocraticTutorApp` 时不再通过 `__init__` 传递 `system_version`，而是初始化后通过属性赋值 `app.system_version = v` 或其它兼容方式同步状态。
- 修改 `src/logger.py`，为 `SessionLogger` 类增加 `.warning(msg)` 和 `.error(msg)` 方法，使其能够像标准的 `logging` 模块一样支持不同级别的日志输出（当前可简单打印到控制台或写入日志文件）。

## Impact
- Affected specs: 系统的容错与日志记录能力、仿真测试的可执行性。
- Affected code: 
  - `src/simulator.py`
  - `src/logger.py`

## ADDED Requirements
### Requirement: Logger应支持多级别输出
`SessionLogger` 必须提供 `.warning()` 和 `.error()` 方法，确保在全局异常拦截和 Fallback 时不会因为对象缺少属性而引发二次崩溃。

#### Scenario: 模型接口报错触发降级
- **WHEN** LLM 接口返回 400 Bad Request 等错误。
- **THEN** 系统捕获异常后，调用 `logger_instance.warning` 记录信息，并成功执行 fallback 逻辑返回安全状态，而非抛出 `AttributeError`。

## MODIFIED Requirements
### Requirement: 仿真器兼容最新的App初始化参数
仿真器脚本必须遵循 `main.py` 的最新类签名进行实例创建，不传递已废弃的参数。