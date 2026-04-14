# Actor-Evaluator Multi-Agent and Refined Judge Spec

## Why
1. **LLM Judge Bias**: The current single-pass LLM Judge in `guardrails.py` misinterprets detailed thought experiments (Reductio ad absurdum) as leaking physical facts, causing false positives and disrupting valid pedagogical strategies.
2. **State Misjudgments**: The NLU and routing layers are overly coupled. The same LLM predicts the student's cognitive state and acts as the "Teacher," leading to hallucinations and deadlocks. We need to decouple this into an Actor-Evaluator Multi-Agent architecture where an Assessor explicitly evaluates if the student meets strict criteria to transition states.

## What Changes
- Update `src/guardrails.py` to implement a **Two-Stage Verification** prompt for the LLM Judge. Stage 1 identifies the pedagogical method (e.g., Thought Experiment, Analogy, Direct Explanation). Stage 2 applies leakage criteria conditionally, explicitly exempting physical facts presented *within* a thought experiment.
- Refactor `src/classifiers.py` to introduce a state-aware **Assessor Agent**. Instead of blindly predicting a static cognitive state, it evaluates whether the student's input satisfies the specific exit conditions of the *current* state.
- Update `src/router.py` to utilize the Assessor Agent's explicit transition evaluation, removing the static `transition_map` and deeply coupling state routing to actual pedagogical progress.

## Impact
- Affected specs: Routing logic, NLU classification, Guardrail interception logic.
- Affected code: `src/guardrails.py`, `src/classifiers.py`, `src/router.py`.

## MODIFIED Requirements
### Requirement: Guardrail Verification
The LLM Judge SHALL use a Two-Stage Verification process to first classify the teaching method and then evaluate for answer leakage, ensuring thought experiments are not falsely flagged.

### Requirement: State Transition Logic
The system SHALL use an Assessor Agent to explicitly evaluate if the user's response meets the criteria to exit the current state before transitioning, rather than relying on a stateless cognitive state prediction.
