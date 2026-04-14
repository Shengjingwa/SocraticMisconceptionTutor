import asyncio
import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import SocraticTutorApp

async def test_p1_fact_grounding():
    app = SocraticTutorApp(session_id="test_p1_fact_grounding_001")
    app.system_version = "FSM+Guardrail"
    
    # 手动设定迷思概念
    app.memory.current_misconception = "M-ELE-001"
    
    # 手动将状态设定到 S7（事实兜底干预）
    app.memory.recent_states = ["S3", "S4", "S5", "S7"]
    app.memory.current_state = "S7"
    
    print("--- 模拟 P1 学生极其固执的发言 ---")
    user_input = "我觉得串联电路就是越往后灯泡越暗，因为前面的灯泡已经把电吃掉了，后面的电肯定就变少了啊。这是常识，你别绕弯子了。"
    print(f"Student: {user_input}")
    
    res = await app.astep(user_input)
    
    print("\n--- 验证助教回复 (应抛出客观实验现象，但不给原理解释) ---")
    print(f"Tutor (S7 Fact-Grounding): {res['generation']['final_reply']}")
    
    print("\n--- 验证护栏状态 (应为 False，不应被拦截) ---")
    print(f"Guardrail Triggered: {res['guardrail']['guardrail_triggered']}")
    if res['guardrail']['guardrail_triggered']:
        print(f"Reason: {res['guardrail'].get('guardrail_reason')}")

if __name__ == "__main__":
    asyncio.run(test_p1_fact_grounding())