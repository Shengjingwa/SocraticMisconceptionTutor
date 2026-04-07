# 修复技术债与架构隐患 Spec

## Why
当前 Socratic Tutor 系统虽然完成了主要功能的开发并集成了 LangGraph 和 DeepSeek 模型，但在实际运行中暴露了大量静态代码隐患、异常处理缺失、工作流死循环风险以及提示词鲁棒性问题。这些技术债（如硬编码密钥、脆弱的 JSON 解析、缺乏超时熔断机制等）严重威胁系统的稳定性和健壮性。为确保系统能够长期可靠运行，需要进行一次全面的系统加固与技术债清理。

## What Changes
- **全局异常处理增强**：在 `main.py` 调用大模型图时增加异常捕获；在 `generator.py` 等处为 API 调用增加 Timeout、RateLimit 处理和重试策略；在 `classifiers.py` 意图识别的 fallback 中加入错误日志记录；为 `generator.py` 和 `guardrails.py` 等的 JSON 读取添加文件异常与解码错误处理。
- **架构与工作流健壮性优化**：为 `graph.py` 中的 `guardrail_node` 添加最大重试次数以防止死循环；为 `router.py` 的各个状态机分支增加最大轮次/超时退出机制（如强制跳转至 S5 结束或兜底状态）；修复 `RouteDecision` 中对 `STATE_NAMES` 的潜在 `KeyError` 字典抛错风险。
- **模型交互与提示词鲁棒性提升**：优化 `classifiers.py` 中 Pydantic 的解析逻辑，容忍模型输出多余的空格或变体；移除残留的提示词注入风险节点（如 `baseline_node` 等的 f-string 直接拼接，转为系统消息隔离）；优化 `guardrails.py`，使用更灵活的正则表达式或模糊匹配替代精确的硬编码字符串拦截规则。
- **技术债清理**：在核心代码（如 `graph.py`、`classifiers.py`、`generator.py`）中移除冗余的硬编码 `"dummy_key"`，统一通过依赖或环境变量入口管理；将 `evaluator.py` 和 `simulator.py` 中的相对文件路径修改为基于项目根目录的绝对/安全路径；补全 `evaluator.py` 和 `simulator.py` 中类方法与脚本主函数的类型提示（Type Hints）。

## Impact
- Affected specs: 系统的容错与异常恢复能力、会话状态流转控制能力。
- Affected code:
  - `src/main.py` (全局入口)
  - `src/generator.py` (LLM生成与重试)
  - `src/classifiers.py` (输出解析与异常记录)
  - `src/graph.py` (死循环熔断)
  - `src/router.py` (防卡死机制与安全字典取值)
  - `src/guardrails.py` (JSON读取容错与正则匹配)
  - `src/evaluator.py` & `src/simulator.py` (路径依赖修复与类型提示)

## ADDED Requirements
### Requirement: LLM调用容错与重试机制
系统应当在调用大语言模型（如 DeepSeek API）时，具备超时（Timeout）、速率限制（RateLimit）错误的捕获能力，并实现自动重试逻辑。

#### Scenario: 模型接口超时
- **WHEN** 用户输入问题后，LLM 接口响应超时。
- **THEN** 系统应捕获异常并记录日志，在有限次重试后返回友好的错误提示，而不是直接崩溃。

### Requirement: 工作流防死循环与卡死机制
系统在路由跳转和护栏重试时，必须拥有“最大重试次数”和“最大对话轮次”的熔断机制。

#### Scenario: 护栏持续拦截导致死循环
- **WHEN** 模型的生成结果连续多次被护栏拦截触发重试。
- **THEN** 达到最大重试次数后，系统应停止重试，直接使用兜底的安全回复返回给用户，防止死循环。

## MODIFIED Requirements
### Requirement: JSON解析与硬编码匹配规则
修改原有基于 Pydantic 的严苛校验与硬编码的字符串精确匹配规则，增强对空白字符和细微错别的容错能力。

## REMOVED Requirements
### Requirement: 硬编码测试密钥与脆弱路径
**Reason**: 重复的 `"dummy_key"` 与不安全的相对路径严重影响了项目可维护性和不同工作目录下的运行稳定性。
**Migration**: 移除各处的假密钥硬编码，统一由集中配置或异常检查处理；脚本路径全部迁移为基于 `os.path.dirname(__file__)` 向上寻找的项目绝对路径。