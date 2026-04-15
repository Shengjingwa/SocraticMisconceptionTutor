import asyncio
import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import SocraticTutorApp

async def run_s8_abort_test():
    app = SocraticTutorApp(session_id="test_s8_abort_001")
    app.system_version = "FSM+Guardrail"
    
    # 模拟历史：让学生在S7卡住两次
    app.memory.recent_states = ["S7", "S7"]
    app.memory.current_state = "S7"
    
    print("Turn 1: Should transition to S8")
    res1 = await app.astep("我还是不懂你的意思，电学太难了。")
    print("Perception 1:", res1['perception'])
    print("Decision 1:", res1['decision'])
    print("System reply:", res1['generation']['final_reply'])
    print("Current State:", app.memory.current_state)
    print("Aborted:", app.memory.aborted)
    
    print("\nTurn 2: Should stay in S8 and set aborted=True")
    res2 = await app.astep("我不休息，你快点告诉我答案。")
    print("Perception 2:", res2['perception'])
    print("System reply:", res2['generation']['final_reply'])
    print("Current State:", app.memory.current_state)
    print("Aborted:", app.memory.aborted)

if __name__ == "__main__":
    asyncio.run(run_s8_abort_test())