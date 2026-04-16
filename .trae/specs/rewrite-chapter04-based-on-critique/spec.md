# Rewrite Chapter 04 Based on Critique Spec

## Why
The user wants to improve the draft of Chapter 4 (`/workspace/docs/Chapter04.tex`) based on the detailed consistency and academic critique provided in `/workspace/docs/Chapter04_分析报告.md`. The goal is to retain existing correct content and citations while addressing the severe discrepancies and academic shortcomings identified in the report (e.g., FSM state mismatch, missing emotional guardrails, lack of simulation pipeline mention, and abstract case studies).

## What Changes
- **FSM State Correction (Sec 4.3.2 & 4.3.3)**: Rewrite the description of S0-S8 to accurately reflect the engineering reality (S1/S2 as guardrail/refusal, S7 as Fact Grounding/兜底, S8 as Acknowledge and Park/搁置). Add a specific discussion on "facing cognitive deadlocks and downgrade intervention strategies".
- **Guardrails Expansion (Sec 4.4.2)**: Include emotional scaffolding (positive reinforcement/affirming correct derivations) and explanatory analogies in the guardrail exemption mechanisms.
- **Knowledge Base Terminology (Sec 4.5.2)**: Remove the misleading term "static teaching case entries" and replace it with "Micro-scaffolding and Dynamic Prompt Generation".
- **Simulation Pipeline Intro (Sec 4.5.1/4.5.4)**: Add a brief section or paragraph at the end of the implementation section detailing the output interfaces (log formats) that pave the way for Chapter 5's multi-agent simulation and LLM-as-a-Judge evaluation.
- **Case Study Enhancement (Sec 4.6)**: Add explicit FSM state transitions (e.g., `[系统由 S3 切换至 S4]`) to the dialogue case studies to prove the FSM logic works as described.
- **Constraint**: Do not delete existing correct academic theories (Posner, Chi, etc.) or citations. Retain all image placeholders (`\begin{figure}...`).

## Impact
- Affected specs: None.
- Affected code: `/workspace/docs/Chapter04.tex` will be significantly expanded and corrected.

## ADDED Requirements
### Requirement: Rewrite Chapter 4
The system SHALL rewrite `Chapter04.tex` to resolve all issues raised in `Chapter04_分析报告.md` without losing existing academic value.

#### Scenario: Success case
- **WHEN** the user requests the rewrite
- **THEN** the system generates a new, academically rigorous, and engineering-accurate `Chapter04.tex` file.