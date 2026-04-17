# 《基于大语言模型的初中物理迷思概念干预研究》第四章配图绘制方案

本文档为 `docs/Chapter04.tex` 中占位符为“图待补绘”的 6 张核心插图提供详细的视觉设计、逻辑流向与术语标注方案。绘图者可参考此文档使用 Draw.io、Visio、Figma 或 TikZ 等工具完成最终矢量图绘制。所有出现的术语均已与正文精修版严格对齐，请勿擅自更改中英文缩写。

---

## 图 1：电学与浮力典型迷思概念的图谱化表征示意 (`fig:misconception-graph`)

**1. 绘图目标**
展示系统如何将抽象的“知识点”转化为可计算的“主题—迷思类型—诊断线索—推荐策略”图谱结构。这不是一张表格，而是一个知识图谱（Knowledge Graph）的局部切片。

**2. 推荐排版与图表类型**
- **类型**：树状展开图或关联图谱。
- **布局**：从左至右或从中心向四周辐射。
- **配色语义**：
  - 中心主题（深蓝色）：领域知识（Domain Knowledge）
  - 迷思类型（橙色）：认知偏差节点（Cognitive Bias Node）
  - 诊断线索（绿色边框，对话框样式）：用户话语特征（User Utterance Feature）
  - 推荐策略（紫色边框，带执行图标）：教学动作映射（Pedagogical Action）

**3. 核心节点与连线内容（必须与 `misconceptions.json` 及 4.2.1 表格严格对应）**
- **根节点**：【主题】浮力 (`M-BUO`) / 电学 (`M-ELE`)
  - **分支 A（迷思类型）**：压强经验误投射
    - 关联线属性：`has_utterance_feature` -> 【诊断线索】“因为水越深压强越大，所以浮力也越来越大”
    - 关联线属性：`mapped_to_strategy` -> 【推荐策略】后果探索（归谬 / Consequence Exploration）
  - **分支 B（迷思类型）**：序列衰减观 (电学)
    - 关联线属性：`has_utterance_feature` -> 【诊断线索】“前面的灯泡把电用掉了一部分，后面的灯就暗了”
    - 关联线属性：`mapped_to_strategy` -> 【推荐策略】证据追问 / 思想实验（Evidence Seeking / Analogical Scaffolding）

*(注：右下角需加图例说明：矩形=概念实体，气泡=话语特征，圆角矩形=策略映射)*

---

## 图 2：融合教学感知与动态干预决策的对话架构 (`fig:teaching-architecture`)

**1. 绘图目标**
展示对话系统的5个分层架构，以及一次完整输入输出的链式处理流程（闭环）。重点体现“在生成之前融入感知与决策”，并映射到项目实际组件。

**2. 推荐排版与图表类型**
- **类型**：分层架构图（Layered Architecture）叠加数据流（Data Flow）。
- **布局**：背景为5个水平横向的“层（Layer）”，前景有一条贯穿这些层的“箭头链”。

**3. 层次划分及底层支撑（背景，自下而上排列）**
- **L1 教学感知层 (Perception Layer)**：提取意图 (`intent`)、情感信号 (`sentiment`)、认知僵局 (`cognitive_state`)。*对应组件：Assessor Agent*
- **L2 诊断决策层 (Decision Layer)**：输出迷思标签 (`misconception_tag`)、阶段路由 (`RouteDecision`)。*对应组件：Router (`src/router.py`)*
- **L3 知识调用层 (Knowledge Layer)**：检索策略目标 (`STRATEGY_GOALS`)、防环规则 (`ANTI_LOOP_RULES`)。*对应组件：Prompt Templates*
- **L4 生成执行层 (Generation Layer)**：执行苏格拉底式引导生成。*对应组件：Tutor LLM*
- **L5 安全约束层 (Guardrail Layer)**：拦截风险意图、LLM-as-a-Judge 审查泄露 (`is_leaking`)。*对应组件：`src/guardrails.py`*

**4. 核心流向链（前景箭头连接）**
学生表述观点 -> (经过L1感知) 解析 `PerceptionResult` -> (经过L2决策) 诊断当前 `SessionMemory` -> (经过L3知识) 匹配 `STATE_STRATEGIES` -> (经过L4生成) 组装提示词并生成回应 -> (经过L5约束) `apply_guardrails` 审查 -> 界面反馈给学生
*(注意：需要有一条名为 `update_after_turn` 的虚线箭头从“界面反馈”指回“L2 诊断决策层”，表示 `SessionMemory` 状态回写。)*

---

## 图 3：阶段化教学对话控制与状态流转示意 (`fig:state-flow`)

**1. 绘图目标**
明确区分“教学推进主线（T1-T5）”与“安全护栏分支（G1-G4）”，并展示对应的工程状态（S0-S8）流转路径及精确的路由条件。

**2. 推荐排版与图表类型**
- **类型**：双轨状态机流程图（State Machine Flowchart）。
- **布局**：上下双轨设计。上方为主轨道（教学主线），下方为副轨道（护栏分支）。跨轨连线需带有条件的标签。

**3. 节点定义与连线（必须包含如下文本与编号）**
- **起点**：学生输入 (User Input)
- **主轨道（教学推进主线，绿色/蓝色块）**：
  - T1 进入与定题 (`S0 Listen_And_Analyze`) $\xrightarrow{\text{感知/路由}}$ 
  - T2 迷思诊断 (`S3 Misconception_Diagnosis`) $\xrightarrow{\text{诊断出明确标签}}$ 
  - T3 认知冲突 (`S4 Cognitive_Conflict`) $\xrightarrow{\text{冲突生效}}$ 
  - T4 支架过渡 (`S5 Scaffolding_Guidance`) $\xrightarrow{\text{完成部分解释}}$ 
  - T5 验证与闭环 (`S6 Verification_Deepening`) $\xrightarrow{\text{自我解释通过}}$ 终点 (`S7 Fact_Grounding`)
- **副轨道（安全护栏分支，橙色/红色块）**：
  - G1 安全检查 (`S1 Guardrail_Check`)
  - G2 拒绝与重定向 (`S2 Refusal_And_Guidance`)
  - G3 防环与降级 (`ANTI_LOOP_RULES` 触发点)
  - G4 确认并结束 (`S8 Acknowledge_and_Park`)

**4. 关键跨轨连线与条件规则（与 `src/router.py` 对齐）**
- **输入拦截（G1/G2）**：学生输入 -> `S1`。若 `risk_flag == true` -> `S2` -> (下一轮)回到主线 `S3`。
- **S4 认知死锁降级（G3）**：从 `S4` 引出两条降级虚线到 `S5`。
  - 条件 1：`recent_states.count('S4') >= 2`
  - 条件 2：`sentiment == "焦虑/挫败"`
- **S5 深度卡顿降级（G3）**：从 `S5` 引出虚线到 `S7`。
  - 条件：`recent_states[-3:] == ['S5', 'S5', 'S5']`
- **异常终止（G4）**：若在 `S7` 连续卡住 `count('S7') >= 2`，流向 `S8` 并终止会话 (`aborted = True`)。

---

## 图 4：教学功能构成与诊断—干预闭环结构图 (`fig:prototype-modules`)

**1. 绘图目标**
展示系统 6 个核心模块之间的信息交互闭环，特别突出“学情记录”、“状态回写”和“输出审查”在维持教学一致性中的作用，并标注流转的 JSON 载荷概念。

**2. 推荐排版与图表类型**
- **类型**：模块交互与数据闭环图（Component Interaction Diagram）。
- **布局**：环形布局，中心为 `SessionMemory` (对话记忆与学情状态库)。

**3. 模块清单与输入输出载荷**
- **M1. 学生输入解析模块 (Assessor)**：
  - 输出：`PerceptionResult` (含 `intent`, `cognitive_state`, `sentiment`)
- **M2. 迷思诊断模块**：
  - 输出：`misconception_tag`
- **M3. 阶段控制模块 (Router)**：
  - 动作：基于 `SessionMemory` 应用转移规则 (`TRANSITION_RULES`)
  - 输出：目标状态 `target_state`
- **M4. 知识策略映射模块**：
  - 动作：`_choose_strategy`
  - 输出：`RouteDecision` (含 `strategy`, `next_goal`)
- **M5. 干预生成与审查模块 (Tutor + LLM Judge)**：
  - 动作：生成回复并经过 `apply_guardrails` 审查
  - 重点标识：在出口处标明红色的放大镜图标（**输出审查：防直接给答/Answer Leakage Check**）
- **M6. 学情记录与反馈展示模块**：
  - 动作：`update_after_turn`，向前端抛出最终回复。

**4. 闭环连线逻辑**
- 外圈箭头：`M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> 用户`
- 内圈反馈：M6 引出虚线 `状态回写 (State Update)` 指向中心的 `SessionMemory` 数据库。M1、M2、M3 在下一轮时均从中心数据库拉取 `recent_states` 和 `used_strategies`。

---

## 图 5：教学阶段推进逻辑与知识策略映射示意 (`fig:kb-state-flow`)

**1. 绘图目标**
揭示知识图谱与策略库并不是静态的“查字典”，而是嵌入在教学阶段流转中被动态调用的过程。重点体现“高置信推进”与“低置信回退”决策逻辑。

**2. 推荐排版与图表类型**
- **类型**：带判断节点的循环流程图（Decision Tree Flowchart）。
- **布局**：以“阶段判断（Route Decision）”菱形为中心，向右/向下辐射至不同的资源库调用动作。

**3. 图表内容与节点映射**
- **顶部四大资源库（圆柱体/数据库图标）**：
  1. 迷思特征库 (`MISCONCEPTIONS`)
  2. 策略目标库 (`STRATEGY_GOALS`)
  3. 状态策略候选池 (`STATE_STRATEGIES`)
  4. 阶段转移规则库 (`TRANSITION_RULES` / `ANTI_LOOP_RULES`)
- **中部处理循环**：
  - `PerceptionResult` (当前感知) + `SessionMemory` (历史状态) $\rightarrow$ 【阶段与策略路由判断 (Router 菱形)】
- **判断分支（带具体条件）**：
  - **分支 A（高置信推进）**：`transition_approved == True` $\rightarrow$ 目标状态提升 (如 `S3->S4` 或 `S5->S6`) $\rightarrow$ 调用【策略候选池】获取 `Consequence_Exploration` 等高级策略。
  - **分支 B（认知僵局/低置信回退）**：`cognitive_state == "认知僵局"` 或多次停滞 $\rightarrow$ 目标状态保持或降级 $\rightarrow$ 强制调用【微支架策略】（如 `Sub_goal_Tracking` 或 `Analogical_Scaffolding`）。
  - **分支 C（异常/兜底终止）**：`recent_states` 末尾连续出现 `S8` $\rightarrow$ 强制调用【结束规则】(`aborted = True`)。
- **底部闭环**：
  - 将匹配的策略名称与目标注入大模型生成回复 $\rightarrow$ `update_after_turn` $\rightarrow$ 回到下一轮感知起点。

---

## 图 6：“不直接给答”约束的系统化实现与界面展示示意 (`fig:no-direct-answer-ui`)

**1. 绘图目标**
把抽象的“不直接给答”机制具象化为两部分：系统后台的四重约束机制（对应 `src/guardrails.py`），以及前端展示给学生的 UI 视觉反馈。

**2. 推荐排版与图表类型**
- **类型**：左右对比图 / 机制剖面图 + UI Mockup（线框图界面模拟）。
- **布局**：左侧为系统机制（漏斗式的层层过滤），右侧为模拟的学生交互界面。

**3. 图表内容**
- **左侧（系统化实现：防卸载双向漏斗机制）**：
  - **第 1 层（输入侧意图拦截）**：`check_input()`。拦截 `Direct_Answer_Seek`（直接索答）与 `Off_Topic`（偏题）。
  - **第 2 层（生成前模板约束）**：按 `current_state` 限制 Prompt 指令。如 `S4` 处于严格模式，`S5` 处于弹性模式（允许部分提示）。
  - **第 3 层（生成后正则初筛）**：`check_output()` 正则部分。拦截“正确答案是”、“浮力不变”等敏感词。
  - **第 4 层（LLM Judge 深度审查）**：LLM 裁判执行两阶段评估（方法分类 -> 泄漏评估 `is_leaking`），并应用 5 项豁免规则（归谬法/思想实验、正向强化、解释类比、确认性总结、事实提供）。
- **右侧（界面展示示意：手机/网页对话框 Mockup）**：
  - **系统横幅提示（顶部）**：“我可以陪你一起想，但不会直接把答案交给你”（非直接作答契约说明）。
  - **对话气泡 1（学生，右侧）**：“你直接告诉我浮力公式吧。”
  - **对话气泡 2（系统，左侧，带盾牌/护栏图标）**：“我们一起来推导它。你觉得如果在深水和浅水里……”（展示拦截与重定向 `Refusal_And_Guidance`）。
  - **底部组件**：可显示“后台 LLM Judge 判定安全”的调试悬浮窗（可选），或者“受控思想实验加载中…”的微支架组件标识。