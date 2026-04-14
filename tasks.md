# Tasks

- [x] Update `src/generator.py` to detect when a student is stuck in `S5` (e.g. `recent_states.count('S5') >= 2`). Add a 'Micro-scaffolding' instruction to break the current question into 2 smaller atomic yes/no questions rather than repeating the broad analogy.
- [x] Update `S7` instruction in `src/generator.py` to require "Hard Empirical Evidence" (生活铁证) to break P1 deadlocks.
- [x] Update the "Red Line Warning" in `src/generator.py` to clarify that "giving sufficient physical context, experimental phenomena, and intermediate logic is NOT leakage".
- [x] Update `src/router.py` and `src/generator.py` to introduce "Sub-goal Tracking" when `cognitive_state == "认知僵局"`. Tell the model to plan a 2-3 step micro-journey in `<think>` and stick to it over consecutive turns.
