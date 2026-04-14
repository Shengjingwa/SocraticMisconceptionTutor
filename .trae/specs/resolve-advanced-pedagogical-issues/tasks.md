# Tasks
- [x] Task 1: Fix Guardrail False Positives (LLM Judge)
  - [x] SubTask 1.1: Update `judge_prompt` in `src/guardrails.py` to add an explicit "Positive Reinforcement Exemption" (Rule 3).
  - [x] SubTask 1.2: Add a few-shot example to the judge prompt showing a student correctly deducing a fact, the tutor praising them, and the judge allowing it.
- [x] Task 2: Implement Cognitive Empathy for P1 Students
  - [x] SubTask 2.1: Update `src/generator.py` to detect `sentiment == "焦虑/挫败"` and `decision.state == "S4"`.
  - [x] SubTask 2.2: Add a "Cognitive Empathy" strategy instruction to use a "Yes, but..." approach instead of extreme counterexamples.
- [x] Task 3: Implement Micro-scaffolding for S5 Deadlocks
  - [x] SubTask 3.1: Update `src/generator.py` to detect when a student is stuck in `S5` (e.g., `recent_states.count("S5") >= 2`).
  - [x] SubTask 3.2: Add a "Micro-scaffolding" instruction to break the current question into 2 smaller, atomic yes/no questions rather than repeating the broad analogy.