# Refine Chapter 04 Based on Educational Critique Spec

## Why
ChatGPT's critique (`Chapter04问题01.md`) identified that the current draft of `Chapter04.tex` reads too much like a technical manual and overstates the system's implemented features as hard facts rather than educational research abstractions. To meet the standard of a master's thesis in education, the chapter needs to be grounded in the 2022 Compulsory Education Physics Curriculum Standards, use more localized Chinese educational literature, present technical architecture through a "teaching function" lens, and incorporate concrete project artifacts (tables, logs, rule sets) to demonstrate the transition from theory to actionable engineering.

## What Changes
- **Tone Adjustment**: Change assertive engineering statements (e.g., "系统实现了...") to educational abstraction statements (e.g., "本研究将原型过程抽象为...", "结合项目实现意图，可归纳为...").
- **Curriculum Alignment**: Add an explicit mapping in Section 4.2 between the Socratic strategies and the core competencies defined in the 2022 Physics Curriculum Standards (evidence & explanation, logic reasoning, teaching-learning-assessment integration).
- **Tables for Physics Content**: Restructure Section 4.2.1 to include two explicit tables:
  1. Textbook Knowledge Points vs. Typical Misconceptions & Diagnostic Cues.
  2. Misconception Types vs. Recommended Dialogue Strategies.
- **Rule Table for Guardrails**: In Section 4.4, add a rule table specifying criteria for "Direct Answer Seeking", "Cognitive Overload", "Exempted Scaffolding", and corresponding system actions.
- **Teaching Function Perspective**: Rename and rewrite Section 4.5 subheadings to focus on teaching functions (e.g., "教学功能构成与诊断—干预闭环" instead of "系统模块构成").
- **Real Artifact Injection**: Insert placeholders and actual code/prompt snippets in Section 4.5 to provide concrete evidence of the implementation (e.g., a prompt snippet or YAML configuration).
- **Case Study Formatting**: Reformat Section 4.6 case studies into structured system logs (Student Profile, Topic, Rounds, Initial Misconception, Strategy Sequence, Dialogue Excerpt).
- **Design-Validation Hooks**: Add concluding sentences at the end of key sections (4.3, 4.4, 4.5) linking the designs to the validation metrics in Chapter 5 (e.g., "本设计将在第五章通过答案泄露率等指标进行验证").
- **Bibliography Updates**: Add Chinese educational references (2022 Curriculum Standards, Physics Teaching Research) to `Chapter4.bib` and cite them in `Chapter04.tex`.

## Impact
- Affected specs: Thesis writing and formatting
- Affected code: `/workspace/docs/Chapter04.tex` and `/workspace/docs/ThesisProposal/ref/Chapter4.bib`

## MODIFIED Requirements
### Requirement: Chapter 4 Content and Tone
The chapter MUST present the technical implementation as an educational research abstraction, explicitly tied to Chinese physics curriculum standards, supported by structured tables, real project artifacts, and properly formatted log-based case studies. It MUST include clear hooks to the evaluation chapter.
