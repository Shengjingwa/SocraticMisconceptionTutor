# Tasks
- [x] Task 1: 修复 `src/main.py` 中的早退逻辑。
  - [x] SubTask 1.1: 找到 `understanding_verified = decision.state == "S6" and not decision.need_guardrail` 的逻辑。
  - [x] SubTask 1.2: 修改为更严格的逻辑：判断 `perception.cognitive_state == "概念掌握验证"` 并且 `self.memory.recent_states` 中的倒数第二个状态是 `"S6"`。因为 `route_state` 已经追加了当前状态，所以 `self.memory.recent_states[-2]` 应该是上一轮的状态。

- [x] Task 2: 增强学生模拟器 `src/simulator.py` 的深度与抗引导性。
  - [x] SubTask 2.1: 将 `max_turns = 6` 增加到 `max_turns = 10`。
  - [x] SubTask 2.2: 在 `_setup_system_prompt` 中补充规则：“除非老师拿出了让你无法反驳的具体物理现象或严密的逻辑推导，否则不要轻易说自己懂了。如果老师只是提问，请顺着你的错误思路继续回答，不要马上附和老师。”

- [x] Task 3: 优化 `src/router.py` 的状态跃迁条件。
  - [x] SubTask 3.1: 将 `transition_map` 中 `"新概念探索"` 对应的跳转目标从 `"S6"` 更改为 `"S5"`（或者如果是 `"S6"` 则无需修改，只要保证主程序的结束条件正确即可。为了更保守，保持为 `"S6"` 即可）。（注：此任务可视情况仅核对即可，只要 `main.py` 修改正确，就能避免过早退出。）