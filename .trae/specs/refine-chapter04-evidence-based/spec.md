# Refine Chapter 04 Evidence-Based Spec

## Why
ChatGPT's critique (`Chapter04问题01.md`) raised several issues regarding the draft of `Chapter04.tex`. It claimed the description of the S0-S8 state machine, Guardrail exemptions, and Cognitive Downgrade Intervention were mere "design abstractions" unsupported by the project's codebase. However, a review of the actual project (`src/router.py`, `src/guardrails.py`) confirms these features **are explicitly implemented** (e.g., `STATE_NAMES`, `ANTI_LOOP_RULES`, `LLM-as-a-Judge` prompts). Therefore, we must *not* blindly downgrade the text to hypothetical designs. Instead, we must retain the factual descriptions while injecting real code/prompt evidence to prove their implementation.

Simultaneously, the critique correctly identified that the chapter reads too much like a software engineering manual and lacks alignment with the 2022 Compulsory Education Physics Curriculum Standards, structured physics knowledge tables, and real system log formats for case studies. These are genuine educational thesis requirements that must be addressed.

## What Changes
- **Reject "Downgrade to Abstraction"**: Retain the assertive tone (e.g., "系统实现了...") regarding S0-S8 and Guardrails, as they are real.
- **Inject Real Code Evidence**: Add actual snippets from `src/router.py` (e.g., `ANTI_LOOP_RULES` for Cognitive Deadlock Downgrade) and `src/guardrails.py` (e.g., `judge_prompt` for LLM-as-a-Judge exemptions) to Section 4.3 and 4.5 to prove implementation.
- **Curriculum Alignment**: In Section 4.2, add a paragraph explicitly mapping Socratic strategies (Clarification/probing -> 证据与解释; Consequence exploration -> 逻辑推理与模型检验; Analogy -> 从生活走向物理的认知桥接; Understanding check -> 形成性评价) to the core competencies in the 2022 Compulsory Education Physics Curriculum Standards.
- **Tables for Physics Content**: Restructure Section 4.2.1 to include two explicit LaTeX tables (`\begin{table}`):
  1. Textbook Knowledge Points vs. Typical Misconceptions & Diagnostic Cues (电学与浮力).
  2. Misconception Types vs. Recommended Dialogue Strategies.
- **Teaching Function Perspective**: Rename Section 4.5 subheadings to focus on teaching functions (e.g., "教学功能构成与诊断—干预闭环" instead of "原型系统模块构成").
- **Add Rule Table for Guardrails**: In Section 4.4, add a rule table (Table 3: “引导而非代答”系统护栏与支架豁免规则表) detailing the criteria for "Direct Answer Seeking", "Cognitive Overload", "Exempted Scaffolding", and the corresponding system actions.
- **Reformat Case Studies**: Rewrite the case studies in Section 4.6 to resemble actual system logs (Student Profile, Topic, Rounds, Initial Misconception, Strategy Sequence, Dialogue Excerpt, Outcome).
- **Bibliography Updates**: Add Chinese educational references (2022 Curriculum Standards, Physics Teaching Research) to `Chapter4.bib` and cite them in `Chapter04.tex`.
- **Design-Validation Hooks**: Add concluding sentences at the end of key sections (4.3, 4.4, 4.5) linking the designs to the validation metrics in Chapter 5.

## Impact
- Affected specs: Thesis writing and formatting
- Affected code: `/workspace/docs/Chapter04.tex` and `/workspace/docs/ThesisProposal/ref/Chapter4.bib`

## MODIFIED Requirements
### Requirement: Chapter 4 Content and Evidence
The chapter MUST present the technical implementation using actual code/prompt snippets as evidence, explicitly tie strategies to the 2022 Chinese physics curriculum standards, use structured tables for physics concepts and guardrail rules, format case studies as real system logs, and include clear hooks to the Chapter 5 evaluation metrics. It MUST NOT downgrade verifiable implemented features to hypothetical designs.
