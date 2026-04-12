import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from main import SocraticTutorApp

def main():
    print("Initializing SocraticTutorApp for simple test...")
    app = SocraticTutorApp(session_id="simple_test_002", system_version="FSM+Guardrail")
    app.memory.topic = "电学"
    app.memory.current_misconception = "M-ELE-001"

    test_inputs = [
        "为什么灯泡会发光？是不是电流被它消耗掉了？",
        "物理太难了，我们聊点别的吧"
    ]

    for user_input in test_inputs:
        print(f"\nUser: {user_input}")
        result = app.step(user_input)
        print(f"System ({result['decision']['state']}): {result['generation']['final_reply']}")

    print("\nTest completed successfully!")

if __name__ == '__main__':
    main()
