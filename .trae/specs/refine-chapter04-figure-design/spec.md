# Refine Chapter 04 Figure Design Spec

## Why
当前 `/workspace/docs/Chapter04_Figure_Design.md` 中的绘图方案不够细致精确。为了确保绘图者能画出符合项目真实情况且教育学语义准确的高质量学术配图，需要结合 `/workspace/docs/Chapter04.tex` 的正文精修版及项目的实际架构、日志和源码机制，对6张核心插图的设计方案进行深度细化，补充所有必要的节点名称、连线条件、输入输出数据结构及中英文字段映射。

## What Changes
- **深度扩展图表方案**：在现有的图表设计大纲基础上，补充确切的模块边界、状态字段名、数据交互内容（如 JSON 载荷概念）、防环规则的具体判断逻辑等。
- **与项目真实情况对齐**：通过检查 `/workspace/src` 下的路由 (`router.py`)、护栏 (`guardrails.py`) 和核心控制流，将工程真实存在的数据流和状态名精准映射到设计图中，杜绝“想象绘图”。
- **细化布局与色彩语义**：为每张图提供具体的视觉图层（如前端层、算法层、教育控制层）和配色语义说明，提升学术感。
- **添加代码映射对照**：在相关方案中明确指出图中某个节点对应于哪个具体代码模块或状态枚举，确保图文和项目的一致性。

## Impact
- Affected specs: `Chapter04_Figure_Design.md`
- Affected code: 无代码变更，仅修改绘图设计文档。

## ADDED Requirements
### Requirement: 细致的模块与数据流映射
方案 SHALL 包含精确的节点层级、连接线上的动作或条件判断（如 `recent_states.count('S4') >= 2`），以及具体的中英文术语对照（如 S0 进入与分析 `Listen_And_Analyze`）。

#### Scenario: 绘制状态流转图
- **WHEN** 绘图者绘制 `fig:state-flow` 时
- **THEN** 能清晰看到 T1-T5 教学主线与 G1-G4 护栏分支的具体进入与退出条件，以及降级触发阈值，避免画成简单的直线。

## MODIFIED Requirements
### Requirement: `Chapter04_Figure_Design.md` 质量提升
文档中的每个图表设计 MUST 包含：
1. 绘图目标与学术定位
2. 图层与区域划分（视觉布局）
3. 核心节点字典（带精确中英文名称）
4. 逻辑流转与连线条件（带具体触发机制）
5. 项目真实性对应（说明节点对应的项目文件或逻辑）

## REMOVED Requirements
无。
