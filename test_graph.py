import sys
from pathlib import Path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

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
