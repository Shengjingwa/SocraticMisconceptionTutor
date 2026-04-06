
# 教学状态机 V1（MVP 版）
state_machine_v1.md

## 1. 文档目的

本文件定义一个用于**苏格拉底式对话干预**的最小可执行教学状态机（FSM, Finite State Machine），用于在 **5 天内**实现一个**可运行、可测试、可记录日志**的教育智能体原型。

该状态机**服务对象不是通用问答**，而是面向**初中物理典型迷思概念**的教学干预任务。

V1 版本仅保留论文与实验所需的**主链路教学阶段**：

> 监听分析 → 护栏检查 → 迷思诊断 →  
> 认知冲突 / 支架引导 → 验证深化

通过**显式状态转移约束生成行为**，避免无状态对话中常见的：
- 过早给答案  
- 教学逻辑漂移  
- 上下文断裂  

## 2. 设计原则（V1）

- **教学目标优先**  
  状态机的核心目标是促进学生从迷思概念走向更接近科学概念的解释，而不是输出正确答案。

- **引导而非代答**  
  一旦识别到直接索要答案、规避思考等高风险意图，必须进入护栏链路。

- **最小可执行**  
  V1 仅包含 **7 个状态（S0–S6）**，不引入情绪建模、多代理或长期记忆等复杂功能。

- **策略与状态耦合**  
  每个状态只允许使用有限的提问策略，保证路径稳定、便于评估。

- **可日志化、可评估**  
  所有状态跳转必须可记录，用于后续实验分析。

## 3. 适用范围（V1 冻结）

### 3.1 教学主题
- 电学
- 浮力

### 3.2 迷思概念（仅限 4 个）
- **M-ELE-001**：电流会被灯泡消耗  
- **M-ELE-002**：单极模型 / 不需要闭合回路  
- **M-BUO-001**：重物一定下沉  
- **M-BUO-002**：浮力只由深度决定  

### 3.3 允许的教学策略（5 类）
- Clarification（澄清）
- Assumption_Probing（挑战假设）
- Evidence_Seeking（证据追问）
- Consequence_Exploration（后果探索）
- Analogical_Scaffolding（类比支架）

## 4. 状态总览

### 4.1 状态集合

| 状态 | 名称 | 功能摘要 |
|----|----|----|
| S0 | Listen_And_Analyze | 接收输入并分析意图、迷思与风险 |
| S1 | Guardrail_Check | 判断是否触发教学护栏 |
| S2 | Refusal_And_Guidance | 教学式拒答并重定向 |
| S3 | Misconception_Diagnosis | 判断认知状态与迷思类型 |
| S4 | Cognitive_Conflict | 制造认知冲突 |
| S5 | Scaffolding_Guidance | 提供理解支架 |
| S6 | Verification_Deepening | 验证与迁移理解 |

## 5. 输入与输出接口

### 5.1 输入（来自感知 / 分类模块）

```json
{
  "intent": "Direct_Answer_Seek | Misconception_Expression | Knowledge_Inquiry",
  "misconception_tag": "M-ELE-001 | M-BUO-002 | None",
  "cognitive_state": "固守错误概念 | 开始动摇 | 认知僵局 | 接近正确 | 已基本掌握",
  "risk_flag": true | false,
  "confidence": 0.0-1.0
}
````

### 5.2 输出（给生成层 / 日志层）

```json
{
  "state": "S4",
  "state_name": "Cognitive_Conflict",
  "strategy": "Assumption_Probing",
  "need_guardrail": false,
  "next_goal": "制造认知冲突"
}
```

## 6. 状态定义

### S0 — Listen\_And\_Analyze

**功能**

*   接收学生输入
*   识别意图、迷思标签、认知状态、风险标记
*   更新会话摘要与轮次

**转移**

*   无条件 → S1

### S1 — Guardrail\_Check

**功能**

*   检查是否存在直接索要答案等高风险输入

**转移**

*   risk\_flag == true → S2
*   否则 → S3

### S2 — Refusal\_And\_Guidance

**功能**

*   教学式拒绝直接代答
*   立即追加一个引导性问题或类比

**约束**

*   **不允许给出标准结论**

**转移**

*   → S0

### S3 — Misconception\_Diagnosis

**功能**

*   判断是否存在明确迷思概念
*   决定后续教学路径

**转移**

*   固守错误概念 → S4
*   开始动摇 / 认知僵局 → S5
*   接近正确 / 已基本掌握 → S6
*   其他 → S5

### S4 — Cognitive\_Conflict

**功能**

*   挑战隐含前提
*   暴露错误推理的后果

**策略**

*   Assumption\_Probing
*   Consequence\_Exploration

**转移**

*   → S0

### S5 — Scaffolding\_Guidance

**功能**

*   在学生动摇或卡顿时提供支撑

**策略**

*   Clarification
*   Evidence\_Seeking
*   Analogical\_Scaffolding

**转移**

*   → S0

### S6 — Verification\_Deepening

**功能**

*   通过变式与迁移验证理解真实性

**策略**

*   Evidence\_Seeking（主）
*   Consequence\_Exploration（辅）

**转移**

*   理解稳定 → resolved = true → S0 或 END
*   否则 → S4 或 S5

## 7. 状态转移伪代码（最小版）

```python
START -> S0

S0 -> analyze(input) -> S1

S1:
  if risk_flag:
    goto S2
  else:
    goto S3

S3:
  if misconception and 固守错误概念:
    goto S4
  elif 认知僵局 or 开始动摇:
    goto S5
  elif 接近正确:
    goto S6
  else:
    goto S5
```

## 8. 策略与状态约束

*   S2：只允许“拒绝 + 引导”
*   S4 / S5：禁止给出完整答案
*   S6：至少一轮迁移验证
*   类比必须标注**类比边界**

## 9. 防死循环规则

*   连续两轮 S4 无进展 → 强制转 S5
*   连续两轮 S5 “不知道” → 降低难度
*   单一模板连续使用 ≤ 2 次

## 10. 轮次与异常处理

*   单问题建议上限：6–8 轮
*   连续 3 次状态失败 → 标记异常并结束会话

## 11. 会话内存字段（建议）

```json
{
  "session_id": "sim_001",
  "topic": "电学",
  "current_state": "S4",
  "current_misconception": "M-ELE-001",
  "turn_count": 3,
  "history_summary": "学生认为前面的灯泡会消耗电流",
  "used_strategies": ["Clarification", "Assumption_Probing"],
  "risk_events": [],
  "resolved": false
}
```

## 12. V1 结论

该教学状态机 V1 为“**初中物理典型迷思概念的苏格拉底式干预**”提供了一条：

*   可执行
*   可测试
*   可评估

的最小主链路，实现了**教学控制权从生成模型回拆到显式结构**。


