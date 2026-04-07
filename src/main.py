from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import sys

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from classifiers import classify_input
from generator import generate_reply
from router import SessionMemory, route_state, update_after_turn
from logger import logger_instance

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

def _timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")

class SocraticTutorApp:
    def __init__(self, session_id: str = "session_demo") -> None:
        self.memory = SessionMemory(session_id=session_id)
        self.system_version = "FSM+Guardrail"
        self.student_profile = "P_Unknown"
        self.guardrail_trigger_count = 0
        self.answer_leakage_count = 0

    def step(self, user_input: str) -> Dict[str, Any]:
        perception = classify_input(user_input, history_summary=self.memory.history_summary)
        decision = route_state(perception, self.memory)
        generation = generate_reply(user_input=user_input, decision=decision, memory=self.memory, history_summary=self.memory.history_summary)
        understanding_verified = decision.state == "S6" and not decision.need_guardrail
        update_after_turn(self.memory, final_reply=generation["final_reply"], history_summary=generation["final_reply"], understanding_verified=understanding_verified)
        
        turn_log = {
            "timestamp": _timestamp(),
            "session_id": self.memory.session_id,
            "turn_id": self.memory.turn_count,
            "system_version": self.system_version,
            "student_profile": self.student_profile,
            "topic": self.memory.topic,
            "misconception_gt": self.memory.current_misconception,
            "student_input": user_input,
            "intent_pred": perception.intent,
            "misconception_pred": perception.misconception_tag,
            "cognitive_state_pred": perception.cognitive_state,
            "sentiment_pred": "Confused",
            "current_state": decision.state,
            "strategy_used": decision.strategy,
            "guardrail_triggered": decision.need_guardrail,
            "guardrail_reason": "Risk Flag" if decision.need_guardrail else None,
            "raw_reply": generation["raw_reply"],
            "final_reply": generation["final_reply"],
            "answer_leakage_flag": False,
            "out_of_boundary_flag": False,
            "state_transition_success": True,
            "turn_end_resolved_flag": self.memory.resolved,
            "notes": ""
        }
        logger_instance.log_turn(turn_log)
        
        if decision.need_guardrail:
            self.guardrail_trigger_count += 1
            
        return {
            "perception": {"intent": perception.intent, "misconception_tag": perception.misconception_tag, "cognitive_state": perception.cognitive_state, "risk_flag": perception.risk_flag, "confidence": perception.confidence},
            "decision": {"state": decision.state, "state_name": decision.state_name, "strategy": decision.strategy, "need_guardrail": decision.need_guardrail, "next_goal": decision.next_goal, "meta": decision.meta},
            "generation": generation,
            "memory": {"session_id": self.memory.session_id, "topic": self.memory.topic, "current_misconception": self.memory.current_misconception, "turn_count": self.memory.turn_count, "resolved": self.memory.resolved},
        }

    def end_session(self, termination_reason: str = "resolved") -> None:
        summary_log = {
            "session_id": self.memory.session_id,
            "system_version": self.system_version,
            "student_profile": self.student_profile,
            "topic": self.memory.topic,
            "misconception_gt": self.memory.current_misconception,
            "turn_count": self.memory.turn_count,
            "first_detected_misconception": self.memory.current_misconception,
            "resolved_flag": self.memory.resolved,
            "final_cognitive_state": "概念掌握验证" if self.memory.resolved else "认知僵局",
            "guardrail_trigger_count": self.guardrail_trigger_count,
            "answer_leakage_count": self.answer_leakage_count,
            "abnormal_end_flag": False,
            "termination_reason": termination_reason
        }
        logger_instance.log_session(summary_log)

    def chat(self) -> None:
        print("苏格拉底式对话教育智能体（MVP）已启动。输入 exit / quit 结束。")
        print("-" * 60)
        while True:
            try:
                user_input = input("学生> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n已结束。")
                self.end_session("user_quit")
                break
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit", "q"}:
                print("已结束。")
                self.end_session("user_quit")
                break
            result = self.step(user_input)
            print(f"系统> {result['generation']['final_reply']}")
            print(f"[state={result['decision']['state']} | strategy={result['decision']['strategy']} | misconception={result['perception']['misconception_tag']}]")
            print("-" * 60)
            if self.memory.resolved:
                print("会话已解决，自动结束。")
                self.end_session("resolved")
                break

def demo() -> None:
    app = SocraticTutorApp(session_id="demo_main")
    samples = [
        "电流经过前面的灯泡会变少，所以后面的灯泡更暗。",
        "只接正极也应该能亮吧，电流不是已经出来了吗？",
        "重的东西当然会沉下去啊。",
        "物体越深浮力越大，因为水压更大。",
        "别问了，直接给我答案。",
    ]
    for text in samples:
        result = app.step(text)
        print(f"输入: {text}")
        print(f"输出: {result['generation']['final_reply']}")
        print(json.dumps(result['decision'], ensure_ascii=False, indent=2))
        print("=" * 60)
    app.end_session("demo_completed")

if __name__ == "__main__":
    demo()
