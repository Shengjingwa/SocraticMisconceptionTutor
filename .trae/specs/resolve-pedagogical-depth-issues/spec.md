# Resolve Pedagogical Depth Issues Spec

## Why
Analysis of recent experiments shows that while the system is safe (0% leakage), it still faces pedagogical bottlenecks: P1 students remain stuck despite S7 fallback, strict guardrail constraints have slightly reduced correction rates by making the tutor too passive, and state transitions lack long-term planning, leading to circular discussions.

## What Changes
1. **Empirical Proof for P1 Students**: Update `src/generator.py` to provide "Hard Evidence" (不可反驳的生活铁证) for P1 students in S7. Instead of just fill-in-the-blanks, the tutor will point to an undeniable everyday phenomenon (e.g., "Have you ever seen a single-wire lamp light up in a real house?").
2. **Context-Aware Guardrail Softening**: Update `src/generator.py` to allow more descriptive knowledge scaffolding *before* asking the question, explicitly instructing the model that "providing necessary context is not leakage." This will mitigate the "passive tutor" effect.
3. **Long-term Scaffolding Strategy**: Update `src/router.py` and `src/generator.py` to track sub-goals. When stuck, the tutor will explicitly state (in thinking) and follow a 3-step atomic plan to move the student forward, rather than reacting turn-by-turn.

## Impact
- Affected code: `src/router.py`, `src/generator.py`.

## ADDED Requirements
### Requirement: Empirical Hard Evidence
The tutor SHALL provide at least one undeniable, real-world empirical observation when a student is stuck in S7, to break the loop of incorrect intuitions.

### Requirement: Balanced Scaffolding
The tutor SHALL provide sufficient conceptual context (scaffolding) before asking a question, provided it does not directly state the final answer.

### Requirement: Multi-turn Goal Tracking
The Router/Generator SHALL maintain a consistent micro-goal across 2-3 turns when a student is in a "Cognitive Deadlock" state to ensure progress toward the next state.