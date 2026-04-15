# Tasks
- [x] Task 1: Fix Guardrail JSON Parsing
  - [x] SubTask 1.1: Update `src/guardrails.py` to use a robust JSON extraction method (e.g. `re.search(r'\{.*\}', text, re.DOTALL)`) before parsing `GuardrailOutput`.
- [x] Task 2: Implement S8 (Acknowledge and Park) for Unresolvable P1 Deadlocks
  - [x] SubTask 2.1: Add `S8` to `STATE_NAMES` and strategies in `src/router.py`.
  - [x] SubTask 2.2: Add a transition rule from `S7` to `S8` if the student is stuck in S7 for 2 or 3 turns.
  - [x] SubTask 2.3: Update `src/generator.py` with specific empathetic instructions for `S8` (e.g., "I see where you're coming from, let's pause here and maybe do a real experiment next time...").
- [x] Task 3: Soften Hardcoded Fallback Phrases
  - [x] SubTask 3.1: Locate the rigid fallback phrases in `src/generator.py` and `src/router.py` (e.g., "为了确保准确性...") and replace them with a dynamic array of softer, more conversational options.