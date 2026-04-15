# 苏格拉底式对话教育智能体 - Code Wiki

## 1. 项目概述

这是一个基于LangGraph的苏格拉底式对话教育智能体，专注于初中物理教育，特别是针对电学和浮力的典型迷思概念。该系统通过引导式对话帮助学生识别和纠正物理学习中的错误概念，采用状态机管理教学流程，确保教学质量和安全性。

## 2. 项目结构

```
├── src/             # 源代码目录
│   ├── main.py      # 主应用入口
│   ├── tutor_graph.py # 状态机定义和工作流程
│   ├── router.py    # 路由和会话内存管理
│   ├── classifiers.py # 输入分类和误解概念识别
│   ├── generator.py # 回复生成
│   ├── guardrails.py # 安全护栏
│   ├── config.py    # 配置信息
│   ├── logger.py    # 日志记录
│   └── state.py     # 状态定义
├── data/            # 数据目录
│   ├── knowledge_chunks.json # 知识点数据
│   ├── misconceptions.json # 错误概念数据
│   └── simulation_profiles.json # 模拟配置文件
├── logs/            # 日志目录
├── tests/           # 测试目录
└── docs/            # 文档目录
```

## 3. 系统架构与工作流程

### 3.1 核心架构

该系统采用基于LangGraph的状态机架构，主要包含以下组件：

1. **输入处理**：通过classifiers.py进行意图识别、错误概念检测和认知状态评估
2. **状态管理**：通过router.py和tutor_graph.py实现教学状态的转换和管理
3. **回复生成**：通过generator.py生成符合教学策略的引导性回复
4. **安全护栏**：通过guardrails.py防止直接泄露答案
5. **会话管理**：通过SessionMemory跟踪会话状态和历史
6. **日志记录**：通过logger.py记录对话和会话信息

### 3.2 工作流程

1. **输入分析**：接收学生输入，进行意图识别和错误概念检测
2. **状态路由**：根据输入分析结果和当前状态，决定下一个教学状态
3. **回复生成**：根据当前状态和策略生成引导性回复
4. **安全检查**：检查回复是否符合安全规则，防止直接泄露答案
5. **记忆更新**：更新会话记忆，记录当前状态和历史
6. **会话评估**：评估会话是否达到学习目标，决定是否结束会话

## 4. 主要模块职责

### 4.1 主应用 (main.py)

**职责**：
- 提供SocraticTutorApp类，作为应用的主要入口
- 处理用户输入和系统输出
- 管理会话生命周期
- 集成各个模块的功能

**核心功能**：
- 初始化会话和内存
- 处理用户输入并调用状态机
- 生成学习报告
- 记录会话信息

### 4.2 状态机 (tutor_graph.py)

**职责**：
- 定义系统的状态机结构
- 管理状态之间的转换
- 协调各个处理节点的执行

**核心功能**：
- 定义状态节点和边
- 实现条件路由逻辑
- 处理状态转换和执行

### 4.3 路由与内存 (router.py)

**职责**：
- 管理会话内存和状态
- 实现状态转换逻辑
- 提供路由决策

**核心功能**：
- 定义SessionMemory类，跟踪会话状态
- 实现状态转换规则
- 提供防死循环机制

### 4.4 分类器 (classifiers.py)

**职责**：
- 分析用户输入，识别意图和错误概念
- 评估学生的认知状态和情感状态
- 判断是否可以进入下一个教学环节

**核心功能**：
- 实现自然语言理解（NLU）
- 检测错误概念
- 评估认知状态

### 4.5 回复生成器 (generator.py)

**职责**：
- 根据当前状态和策略生成引导性回复
- 确保回复符合教学策略和安全规则
- 生成学习报告

**核心功能**：
- 构建系统提示词
- 调用LLM生成回复
- 清理和处理回复

### 4.6 安全护栏 (guardrails.py)

**职责**：
- 检查输入和输出是否符合安全规则
- 防止直接泄露答案
- 确保教学过程的安全性

**核心功能**：
- 检查输入风险
- 检查输出是否泄露答案
- 应用LLM-as-a-Judge进行深度语义检测

### 4.7 配置管理 (config.py)

**职责**：
- 管理系统配置
- 提供LLM实例
- 定义常量和参数

**核心功能**：
- 管理API密钥和模型配置
- 提供LLM实例创建函数
- 定义重试和历史配置

### 4.8 日志记录 (logger.py)

**职责**：
- 记录对话和会话信息
- 提供日志管理功能

**核心功能**：
- 记录回合日志
- 记录会话摘要
- 提供日志级别管理

## 5. 关键类与函数

### 5.1 SocraticTutorApp (main.py)

**功能**：主应用类，管理整个对话流程

**方法**：
- `__init__(session_id, system_version, student_profile, topic)`: 初始化应用实例
- `step(user_input)`: 处理用户输入，执行状态机
- `astep(user_input)`: 异步处理用户输入
- `end_session(termination_reason)`: 结束会话，记录会话摘要
- `chat()`: 启动交互式对话

### 5.2 SessionMemory (router.py)

**功能**：管理会话状态和历史

**属性**：
- `session_id`: 会话ID
- `topic`: 对话主题
- `current_state`: 当前教学状态
- `current_misconception`: 当前错误概念
- `turn_count`: 对话回合数
- `history_summary`: 历史对话摘要
- `used_strategies`: 使用过的策略
- `recent_states`: 最近的状态
- `risk_events`: 风险事件
- `resolved`: 是否已解决
- `aborted`: 是否已中止

### 5.3 PerceptionResult (router.py)

**功能**：表示对用户输入的感知结果

**属性**：
- `intent`: 用户意图
- `misconception_tag`: 错误概念标签
- `cognitive_state`: 认知状态
- `sentiment`: 情感状态
- `risk_flag`: 风险标志
- `confidence`: 置信度
- `transition_approved`: 是否允许状态转移
- `reasoning`: 推理过程

### 5.4 RouteDecision (router.py)

**功能**：表示状态路由决策

**属性**：
- `state`: 目标状态
- `state_name`: 状态名称
- `strategy`: 使用的策略
- `need_guardrail`: 是否需要护栏
- `next_goal`: 下一个目标
- `meta`: 元数据

### 5.5 classify_input (classifiers.py)

**功能**：分析用户输入，返回感知结果

**参数**：
- `user_input`: 用户输入文本
- `messages`: 历史消息
- `history_summary`: 历史摘要
- `current_state`: 当前状态

**返回值**：PerceptionResult对象

### 5.6 route_state (router.py)

**功能**：根据感知结果和内存状态，决定下一个状态

**参数**：
- `perception`: 感知结果
- `memory`: 会话内存

**返回值**：(RouteDecision, SessionMemory)元组

### 5.7 generate_reply (generator.py)

**功能**：根据当前状态和策略生成回复

**参数**：
- `user_input`: 用户输入
- `decision`: 路由决策
- `memory`: 会话内存
- `messages`: 历史消息

**返回值**：包含回复信息的字典

### 5.8 apply_guardrails (guardrails.py)

**功能**：应用安全护栏检查

**参数**：
- `user_input`: 用户输入
- `intent`: 用户意图
- `generated_text`: 生成的文本
- `misconception_tag`: 错误概念标签
- `is_already_safe`: 是否已经安全
- `consecutive_triggers`: 连续触发次数
- `current_state`: 当前状态

**返回值**：包含护栏检查结果的字典

### 5.9 app_graph (tutor_graph.py)

**功能**：预编译的状态机图

**使用方式**：通过invoke或ainvoke方法执行状态机

## 6. 依赖关系

### 6.1 核心依赖

| 依赖项 | 用途 | 来源 |
|-------|------|------|
| Python 3.13+ | 运行环境 | 系统 |
| langgraph | 状态机实现 | config.py |
| langchain_core | 消息处理 | main.py, tutor_graph.py |
| langchain_openai | LLM接口 | config.py |
| pydantic | 数据模型 | router.py, classifiers.py |
| tenacity | 重试机制 | classifiers.py, generator.py |

### 6.2 环境变量

| 环境变量 | 用途 | 默认值 |
|---------|------|--------|
| DASHSCOPE_API_KEY | API密钥 | "" |
| DEEPSEEK_API_KEY | 备用API密钥 | "" |
| LLM_BASE_URL | LLM API基础URL | "https://dashscope.aliyuncs.com/compatible-mode/v1" |
| TUTOR_MODEL | 教学模型 | "qwen3.6-plus" |
| JUDGE_MODEL | 评判模型 | "deepseek-v3.2" |
| MAX_HISTORY_TURNS | 最大历史回合数 | 6 |
| SIMULATION_CONCURRENCY | 模拟并发数 | 6 |

## 7. 项目运行方式

### 7.1 环境设置

1. **安装依赖**：
   ```bash
   pip install langgraph langchain_core langchain_openai pydantic tenacity
   ```

2. **设置环境变量**：
   ```bash
   export DASHSCOPE_API_KEY=your_api_key
   ```

### 7.2 运行方式

1. **交互式对话**：
   ```bash
   python src/main.py
   ```

2. **演示模式**：
   ```bash
   python src/main.py demo
   ```

3. **API调用**：
   ```python
   from src.main import SocraticTutorApp
   
   app = SocraticTutorApp(session_id="test_session")
   result = app.step("电流经过前面的灯泡会变少，所以后面的灯泡更暗。")
   print(result['generation']['final_reply'])
   ```

## 8. 教学状态与策略

### 8.1 教学状态

| 状态 | 名称 | 描述 |
|-----|------|------|
| S0 | Listen_And_Analyze | 初始状态，监听和分析用户输入 |
| S1 | Guardrail_Check | 护栏检查，防止直接求答案等风险 |
| S2 | Refusal_And_Guidance | 拒绝直接代答，引导回学习路径 |
| S3 | Misconception_Diagnosis | 错误概念诊断，识别学生的错误概念 |
| S4 | Cognitive_Conflict | 认知冲突，制造矛盾，让学生怀疑错误概念 |
| S5 | Scaffolding_Guidance | 脚手架引导，提供支持，帮助学生构建正确概念 |
| S6 | Verification_Deepening | 验证深化，确保学生真正理解 |
| S7 | Fact_Grounding | 事实兜底，提供无可辩驳的事实 |
| S8 | Acknowledge_and_Park | 承认并搁置，处理无法解决的情况 |

### 8.2 教学策略

| 策略 | 描述 | 适用状态 |
|-----|------|----------|
| Assumption_Probing | 暴露学生结论背后的隐含前提 | S4 |
| Consequence_Exploration | 推演学生当前解释的后果 | S4, S6 |
| Clarification | 澄清学生表述中的模糊概念 | S5 |
| Evidence_Seeking | 引导学生用现象或实验支持判断 | S5, S6 |
| Analogical_Scaffolding | 用类比支架帮助学生理解 | S5 |
| Sub_goal_Tracking | 通过微引导路径逐步打破僵局 | S5 |
| Fact_Grounding | 提供不可反驳的物理事实 | S7 |
| Acknowledge_and_Park | 承认问题难度，提议暂时搁置 | S8 |

## 9. 错误概念管理

### 9.1 支持的错误概念

| 标签 | 名称 | 领域 |
|-----|------|------|
| M-ELE-001 | 认为电流在电路中会被消耗 | 电学 |
| M-ELE-002 | 认为电路不需要闭合回路，单线即可工作 | 电学 |
| M-BUO-001 | 认为物体越重越容易沉，越轻越容易浮 | 浮力 |
| M-BUO-002 | 认为水压越大浮力越大，浮力随深度增加 | 浮力 |

### 9.2 错误概念数据结构

每个错误概念包含以下信息：
- 错误概念名称
- 核心科学知识点
- 反例
- 类比
- 推理漏洞
- 禁止的直接答案

## 10. 日志与监控

### 10.1 日志文件

| 文件名 | 用途 | 位置 |
|-------|------|------|
| turn_logs.jsonl | 记录每个回合的详细信息 | logs/turn_logs.jsonl |
| session_summary.jsonl | 记录会话摘要 | logs/session_summary.jsonl |
| app.log | 应用日志 | logs/app.log |

### 10.2 监控指标

- 会话解决率
- 错误概念识别准确率
- 护栏触发次数
- 答案泄露次数
- 平均对话回合数

## 11. 性能与优化

### 11.1 性能优化

- **历史压缩**：当对话历史过长时，自动压缩历史记录
- **并发处理**：支持并发模拟多个会话
- **缓存机制**：缓存LLM响应，减少重复请求

### 11.2 安全优化

- **多层护栏**：输入和输出双重检查
- **LLM-as-a-Judge**：深度语义检测
- **弹性策略**：根据对话状态调整安全规则

## 12. 测试与验证

### 12.1 测试文件

| 测试文件 | 测试内容 | 位置 |
|---------|----------|------|
| import_smoke_test.py | 导入测试 | tests/import_smoke_test.py |
| simple_test.py | 简单功能测试 | tests/simple_test.py |
| test_guardrail_metrics.py | 护栏指标测试 | tests/test_guardrail_metrics.py |
| test_p1_fact_grounding.py | 事实兜底测试 | tests/test_p1_fact_grounding.py |
| test_s8_abort.py | 中止功能测试 | tests/test_s8_abort.py |
| test_task3.py | 任务测试 | tests/test_task3.py |

### 12.2 验证方法

- **单元测试**：测试各个模块的功能
- **集成测试**：测试模块之间的协作
- **模拟测试**：模拟学生行为，测试系统响应
- **人工评估**：人工评估系统性能和教学效果

## 13. 扩展与未来发展

### 13.1 扩展方向

- **支持更多学科**：扩展到其他学科的错误概念
- **个性化学习**：根据学生特点调整教学策略
- **多语言支持**：支持不同语言的教学
- **多媒体集成**：集成图片、视频等多媒体内容

### 13.2 技术路线

- **模型优化**：使用更适合教育场景的LLM
- **知识图谱**：构建物理知识图谱，提供更准确的知识支持
- **自适应学习**：根据学生反馈自动调整教学策略
- **多模态交互**：支持语音、文本等多种交互方式

## 14. 总结

苏格拉底式对话教育智能体是一个基于LangGraph的智能教育系统，通过引导式对话帮助学生识别和纠正物理学习中的错误概念。系统采用状态机管理教学流程，确保教学质量和安全性，同时提供了丰富的教学策略和安全护栏机制。

该系统具有以下特点：
- **智能识别**：自动识别学生的错误概念和认知状态
- **引导式教学**：通过提问和类比引导学生自主思考
- **安全保障**：多层护栏防止直接泄露答案
- **个性化适应**：根据学生状态调整教学策略
- **完整记录**：详细记录对话和会话信息，支持分析和改进

未来，该系统可以扩展到更多学科和场景，为学生提供更个性化、更有效的学习体验。