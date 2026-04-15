# Tasks
- [x] Task 1: Fix Serialization Warnings
  - [x] SubTask 1.1: Import `router.SessionMemory`, `router.PerceptionResult`, and `router.RouteDecision` into `src/tutor_graph.py`.
  - [x] SubTask 1.2: Register these classes in the `MemorySaver` or `checkpointer` configuration to silence the warnings.
- [x] Task 2: Resolve Pedagogical Deadlocks
  - [x] SubTask 2.1: Update `ANTI_LOOP_RULES` in `src/router.py` to identify when a user rejects thought experiments (e.g., stuck in S4 with negative sentiment/frustration).
  - [x] SubTask 2.2: Downgrade the strategy to a simpler analogy ("Analogical_Scaffolding") or clarification if deadlock is detected.
- [x] Task 3: Implement Dynamic Turn Limits
  - [x] SubTask 3.1: In `src/simulator.py`'s `run_simulation`, read the final `cognitive_state` from the latest `NLUOutput`.
  - [x] SubTask 3.2: If `turn_count` == `config.MAX_HISTORY_TURNS` but the state is "新概念探索", extend the loop dynamically by e.g., 3 extra turns.