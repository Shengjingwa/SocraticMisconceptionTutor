# Fix Experiment Issues Spec

## Why
Based on the analysis of `logs/pipeline_2026-04-14_09-37-01.log`, several issues were identified that degrade system performance and reliability. We need to fix the LangGraph serialization warnings to prevent future crashes, resolve pedagogical deadlocks for stubborn students (like P1 profile), and introduce a dynamic max-turns mechanism to prevent premature termination of promising sessions.

## What Changes
- Register custom dataclasses/pydantic models (`SessionMemory`, `PerceptionResult`, `RouteDecision`) in LangGraph's checkpointer to eliminate `Deserializing unregistered type` warnings.
- Update `src/router.py` to handle pedagogical deadlocks by detecting repeated rejections of thought experiments and downgrading the strategy (e.g., from `Assumption_Probing` to `Clarification` or providing a simpler analogy).
- Update `src/config.py` and `src/simulator.py` to support dynamic `MAX_HISTORY_TURNS`. If the Assessor Agent identifies the student's `cognitive_state` as "新概念探索" (Exploring New Concepts), the session should be granted a few extra turns (e.g., +3) instead of terminating strictly at 10.

## Impact
- Affected code: `src/tutor_graph.py`, `src/router.py`, `src/simulator.py`, `src/config.py`.

## ADDED Requirements
### Requirement: LangGraph Serialization
The system SHALL explicitly register all custom state objects with the MemorySaver to prevent deserialization warnings and ensure forward compatibility.

### Requirement: Deadlock Resolution
The system SHALL detect when a student is stuck in a rejection loop during "Cognitive Conflict" (S4) and dynamically downgrade the pedagogical strategy to avoid wasting turns.

### Requirement: Dynamic Turn Limits
The simulator SHALL dynamically extend the maximum allowed turns if the student is actively making progress ("新概念探索") near the turn limit.