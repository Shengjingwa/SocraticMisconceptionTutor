# Resolve Advanced Pedagogical Issues Spec

## Why
Despite previous metric improvements, the system still struggles with deep state transitions (half of sessions don't reach mastery), causes emotional resistance in stubborn (P1) students due to aggressive "Reductio ad absurdum" tactics, and suffers from LLM Judge false positives that block the tutor from praising a student's correct conclusion. These issues cause pedagogical deadlocks and disrupt the flow of teaching.

## What Changes
1. **Fix Guardrail False Positives**: Update `src/guardrails.py` to explicitly grant a "Positive Reinforcement Exemption." The judge will be instructed (with few-shot examples) NOT to block the tutor when it repeats or affirms a correct physical conclusion that the *student* just deduced.
2. **Fix P1 Student Resistance**: Update `src/generator.py` to inject "Cognitive Empathy" instructions for stubborn or frustrated students. If the student is struggling or resisting, the tutor must use a "Yes, but..." approach, validating their intuition before gently introducing an anomaly, rather than attacking them with extreme counterexamples.
3. **Improve State Transition Depth (Micro-scaffolding)**: Update `src/generator.py` to enforce micro-scaffolding. When a student is stuck in S5 for multiple turns, the tutor must break the question down into smaller yes/no steps rather than repeating the same broad analogy.

## Impact
- Affected code: `src/guardrails.py`, `src/generator.py`.

## ADDED Requirements
### Requirement: Positive Reinforcement Exemption
The LLM Judge SHALL NOT intercept responses where the tutor affirms, praises, or repeats a correct scientific conclusion that was generated or deduced by the student in the preceding turn.

### Requirement: Cognitive Empathy Strategy
The Generator SHALL detect frustrated or stubborn student profiles and switch from aggressive cognitive conflict (Reductio ad absurdum) to empathetic validation ("Yes, but...") to reduce emotional resistance.

### Requirement: Micro-scaffolding
The Generator SHALL break down complex analogies into smaller, atomic questions when the student fails to progress out of the scaffolding state (S5) after multiple turns.