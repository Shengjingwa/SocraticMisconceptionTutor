# Tasks
- [x] Task 1: Fix P1 Pedagogical Deadlock
  - [x] SubTask 1.1: Update `src/generator.py` for `decision.state == "S7"` to require "Hard Empirical Evidence" (生活铁证) rather than just abstract explanations and fill-in-the-blanks.
- [x] Task 2: Mitigate Strict Guardrail Side Effects
  - [x] SubTask 2.1: Update the "Red Line Warning" in `src/generator.py` to clarify that "giving sufficient physical context, experimental phenomena, and intermediate logic is NOT leakage, as long as the final physical rule is left for the student to state."
- [x] Task 3: Improve Long-term State Transitions
  - [x] SubTask 3.1: Update `src/router.py` and `src/generator.py` to introduce "Sub-goal Tracking" when `cognitive_state == "认知僵局"`. Tell the model to plan a 2-3 step micro-journey in `<think>` and stick to it over consecutive turns.