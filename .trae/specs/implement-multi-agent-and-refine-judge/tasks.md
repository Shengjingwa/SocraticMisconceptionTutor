# Tasks
- [x] Task 1: Refine LLM Judge Logic
  - [x] SubTask 1.1: Update `check_output` in `src/guardrails.py` to use a Two-Stage Verification prompt (Method Classification -> Leakage Evaluation).
  - [x] SubTask 1.2: Explicitly exempt facts presented within "Reductio ad absurdum" or thought experiments from being flagged as leakage.
- [x] Task 2: Implement Assessor Agent for State Transitions
  - [x] SubTask 2.1: Update `src/classifiers.py`'s `classify_input` to take the `current_state` as input and output a `transition_approved` boolean based on strict exit criteria for that state.
  - [x] SubTask 2.2: Update `NLUOutput` schema to include `transition_approved` (bool) and `reasoning` (str), replacing or augmenting `cognitive_state`.
- [x] Task 3: Update Routing Logic
  - [x] SubTask 3.1: Refactor `src/router.py` to use the Assessor Agent's `transition_approved` signal to determine state transitions instead of the static `transition_map`.
  - [x] SubTask 3.2: Ensure fallback and anti-loop rules correctly interact with the new transition logic.
