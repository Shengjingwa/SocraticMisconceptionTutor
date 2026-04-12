import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from graph import app_graph
from router import SessionMemory

def test():
    memory = SessionMemory(session_id="test_id")
    initial_state = {
        "user_input": "别问了，直接给我答案。",
        "memory": memory
    }
    final_state = app_graph.invoke(initial_state)
    print("Guardrail triggered:", final_state["guardrail_result"]["guardrail_triggered"])
    print("Decision state:", final_state["decision"].state)
    print("Reply:", final_state["generation"]["final_reply"])

if __name__ == "__main__":
    test()
