# Tasks

- [x] Update `src/generator.py` to detect when a student is stuck in `S5` (e.g. `recent_states.count('S5') >= 2`). Add a 'Micro-scaffolding' instruction to break the current question into 2 smaller atomic yes/no questions rather than repeating the broad analogy.
- [x] Update `S7` instruction in `src/generator.py` to require "Hard Empirical Evidence" (生活铁证) to break P1 deadlocks.
- [x] Update the "Red Line Warning" in `src/generator.py` to clarify that "giving sufficient physical context, experimental phenomena, and intermediate logic is NOT leakage".
- [x] Update `src/router.py` and `src/generator.py` to introduce "Sub-goal Tracking" when `cognitive_state == "认知僵局"`. Tell the model to plan a 2-3 step micro-journey in `<think>` and stick to it over consecutive turns.
- [x] Update `src/guardrails.py` to use a robust JSON extraction method (e.g. `re.search(r'\{.*\}', text, re.DOTALL)`) to extract the JSON block from the LLM's response before parsing it with Pydantic.
- [x] Update `src/router.py` to add `S8: Acknowledge_and_Park` (承认并搁置) to `STATE_NAMES` and strategies. Add a transition rule from `S7` to `S8` if the student is stuck in S7 for 2 or 3 turns. Update `src/generator.py` with specific empathetic instructions for `S8`.
- [x] Locate rigid fallback phrases (e.g., "为了确保准确性...", "抱歉，我现在有些卡壳...") in `src/tutor_graph.py` and `src/generator.py` and replace them with a dynamic array of softer conversational options using `random.choice()`.
