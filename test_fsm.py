import sys
from pathlib import Path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from graph import app_graph
from router import SessionMemory

def test():
    memory = SessionMemory(session_id="test_id")
    memory.current_misconception = "some_misconception"
    initial_state = {
        "system_version": "FSM",
        "user_input": "直接给我答案",
        "memory": memory
    }
    final_state = app_graph.invoke(initial_state)
    print("Guardrail triggered:", final_state["guardrail_result"]["guardrail_triggered"])
    print("Answer leakage flag:", final_state["guardrail_result"].get("answer_leakage_flag", False))
    print("Decision state:", final_state["decision"].state)
    print("Reply:", final_state["generation"]["final_reply"])

if __name__ == "__main__":
    test()
