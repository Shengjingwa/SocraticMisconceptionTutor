# Resolve Remaining Pedagogical and Technical Issues Spec

## Why
Despite previous optimizations, three persistent issues remain:
1. P1 students still reach cognitive deadlocks because empirical evidence isn't enough to overcome their emotional/intuitive resistance.
2. The LLM Judge occasionally outputs non-JSON text (e.g., trailing explanations), causing Pydantic schema validation errors and fallback to rule-based checking.
3. The system occasionally outputs repetitive or rigid fallback phrases (e.g., "为了确保准确性...") when stuck in a loop or after guardrail triggers, breaking conversational naturalness.

## What Changes
1. **Fix Guardrail JSON Parsing**: Update `src/guardrails.py` to add robust JSON extraction logic (e.g., using regex to extract content between `{` and `}`) before feeding the string to Pydantic, bypassing trailing text errors from the LLM.
2. **Soften Fallback Phrases**: Update `src/generator.py` and `src/router.py` to replace rigid, hardcoded fallback strings with dynamic, empathetic transitions.
3. **P1 Extreme Fallback (S8)**: Introduce a new state `S8: Acknowledge_and_Park` (承认并搁置) in `src/router.py`. If a student remains stuck in S7 for too long, the tutor will stop trying to convince them immediately, validate their current perspective, and propose a "let's park this and look at a different experiment next time" approach to gracefully end the loop rather than arguing endlessly.

## Impact
- Affected code: `src/guardrails.py`, `src/generator.py`, `src/router.py`.

## ADDED Requirements
### Requirement: Robust JSON Extraction
The Guardrail system SHALL extract valid JSON substrings from the LLM output before parsing, ignoring any leading or trailing conversational text.

### Requirement: Graceful Impasse Handling
The system SHALL transition to an "Acknowledge and Park" (S8) state if the student is stuck in S7, preventing endless arguing and allowing a graceful conversational exit.

### Requirement: Natural Fallbacks
The system SHALL use varied, context-aware fallback phrases rather than hardcoded, repetitive strings when recovering from guardrail interceptions or state loops.