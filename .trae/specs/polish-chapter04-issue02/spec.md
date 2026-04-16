# 基于 Chapter04问题02 的第4章精修 Spec

## Why
在完成“项目一致性增强”和“引用体检”后，[Chapter04.tex](file:///workspace/docs/Chapter04.tex) 的内容更扎实，但 [Chapter04问题02.md](file:///workspace/docs/Chapter04问题02.md) 指出了一批新的高风险点：证据闭环表述过强（日志/代码是否可追溯）、正文工程术语过密、案例来源界线不清，以及 LaTeX 依赖与可编译性风险。需要在不削弱已核实的项目真实性前提下，对这些真实存在的问题进行精修，提升答辩抗质疑能力。

## What Changes
- **证据闭环补强**：对代码清单与“日志档案”增加来源说明（真摘录/匿名化/简化处理/代表性整理），避免“真实性风险”表述过强。
- **工程术语教育化**：正文中状态名与机制名采用“中文主名 + 英文括注一次”的写法，后文统一中文简称；避免英文状态名在视觉上喧宾夺主。
- **教学主线/安全分支分层**：在 4.3 的状态模型中明确区分“教学推进主线”和“系统护栏/兜底分支”，保持与项目实现映射但呈现更贴近概念转变教学阶段。
- **案例体例澄清**：在 4.6 中明确案例是“真实日志节选”或“按日志结构整理的代表性案例”，并补充“失败/边界案例将在第5章讨论”的说明，避免仅呈现成功案例带来的答辩追问风险。
- **新术语操作性定义**：为“认知死锁”“微支架”“情感支架”等提供可操作化的判定—边界—作用描述，与项目中的防环规则和豁免条件对应。
- **LaTeX 可编译性降风险**：移除或最小化对 `booktabs`、`listings` 等宏包的强依赖（例如将 `\\toprule` 等改为标准 `\\hline` 方案；代码清单如需保留则改为不依赖宏包的环境/排版方式），并清理可能导致报错的未转义特殊字符。
- **引用与键名稳定性**：保持 `\\cite{}` 与 [refs.bib](file:///workspace/docs/refs.bib) 的一致性，不引入占位键，新增引用必须可追溯（优先 DOI/官方链接）。

- **BREAKING**：无。

## Impact
- Affected specs: 论文第4章写作体例与可核查性
- Affected code: [Chapter04.tex](file:///workspace/docs/Chapter04.tex), [refs.bib](file:///workspace/docs/refs.bib)

## ADDED Requirements
### Requirement: Evidence Traceability Note
系统 SHALL 在每个“代码清单/日志档案/状态命名”出现处提供可核查性说明（真摘录/代表性整理/匿名化/简化处理/映射关系）。

#### Scenario: 读者追问证据来源
- **WHEN** 评阅/答辩要求定位代码或日志来源
- **THEN** 正文或脚注能给出清晰的可追溯解释，避免将“代表性整理”误写为“真实日志原样节选”

## MODIFIED Requirements
### Requirement: Chapter 4 Style and LaTeX Robustness
第4章 MUST 以教育学主叙事为核心，工程细节作为证据支撑；术语呈现必须教育化；LaTeX 必须在不依赖未知导言区宏包的情况下保持可编译（或显式降低依赖）。

## REMOVED Requirements
无。

