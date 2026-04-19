from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from langchain_core.messages import HumanMessage

from logger import logger_instance
from router import SessionMemory, update_after_turn
from tutor_graph import app_graph

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = Path(os.environ.get("LOG_DIR", str(BASE_DIR / "logs"))).resolve()
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


class SocraticTutorApp:
    def __init__(
        self,
        session_id: str,
        system_version: str = "FSM+Guardrail",
        student_profile: str = "Unknown",
        topic: str = "Unknown",
    ):
        self.memory = SessionMemory(session_id=session_id, topic=topic)
        self.system_version = system_version
        self.student_profile = student_profile
        self.misconception_init = None
        self.guardrail_trigger_count = 0
        self.answer_leakage_count = 0
        self.abnormal_end_flag = False
        logger_instance.info(
            f"Initialized Session {session_id} on {topic} for {student_profile} with version {system_version}"
        )

    def _process_graph_result(self, final_state: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        perception = final_state["perception"]
        decision = final_state["decision"]
        generation = final_state["generation"]
        guardrail_result = final_state.get(
            "guardrail_result", {"guardrail_triggered": False, "guardrail_reason": None}
        )

        understanding_verified = False
        if (
            (perception.cognitive_state == "概念掌握验证")
            and (decision.state == "S6")
            and (getattr(perception, "confidence", 0) >= 0.8)
        ):
            from classifiers import verify_post_test

            understanding_verified = verify_post_test(
                user_input=user_input,
                misconception_tag=perception.misconception_tag or self.memory.current_misconception,
                messages=final_state.get("messages", []),
            )

        self.memory = final_state.get("memory", self.memory)
        self.memory = update_after_turn(
            self.memory,
            user_input=user_input,
            final_reply=generation["final_reply"],
            history_summary=None,
            understanding_verified=understanding_verified,
        )

        turn_log = {
            "timestamp": _timestamp(),
            "session_id": self.memory.session_id,
            "turn_id": self.memory.turn_count,
            "system_version": self.system_version,
            "student_profile": self.student_profile,
            "topic": self.memory.topic,
            "misconception_gt": self.misconception_init,
            "student_input": user_input,
            "intent_pred": perception.intent,
            "misconception_pred": perception.misconception_tag,
            "cognitive_state_pred": perception.cognitive_state,
            "sentiment_pred": getattr(perception, "sentiment", "Confused"),
            "current_state": decision.state,
            "strategy_used": decision.strategy,
            "guardrail_triggered": decision.need_guardrail
            or guardrail_result["guardrail_triggered"],
            "guardrail_reason": guardrail_result.get("guardrail_reason")
            or ("Risk Flag" if decision.need_guardrail else None),
            "raw_reply": generation["raw_reply"],
            "final_reply": generation["final_reply"],
            "answer_leakage_flag": guardrail_result.get("answer_leakage_flag", False),
            "out_of_boundary_flag": guardrail_result.get("guardrail_reason") == "Off_Topic",
            "state_transition_success": decision.state
            in ["S0", "S1", "S2", "S3", "S4", "S5", "S6"],
            "turn_end_resolved_flag": self.memory.resolved,
            "notes": "",
        }
        logger_instance.log_turn(turn_log)

        learning_report = None
        if self.memory.resolved:
            from generator import generate_learning_report

            learning_report = generate_learning_report(
                self.memory, messages=final_state.get("messages", [])
            )

        if turn_log["guardrail_triggered"]:
            self.guardrail_trigger_count += 1
            # 累加拦截次数，避免被最后一次成功生成的未触发状态覆盖
            if getattr(self.memory, "turn_guardrail_triggers", 0) > 0:
                self.guardrail_trigger_count += self.memory.turn_guardrail_triggers - 1

        if turn_log["answer_leakage_flag"]:
            self.answer_leakage_count += 1

        return {
            "perception": {
                "intent": perception.intent,
                "misconception_tag": perception.misconception_tag,
                "cognitive_state": perception.cognitive_state,
                "risk_flag": perception.risk_flag,
                "confidence": perception.confidence,
                "sentiment": getattr(perception, "sentiment", "Confused"),
            },
            "decision": {
                "state": decision.state,
                "state_name": decision.state_name,
                "strategy": decision.strategy,
                "need_guardrail": decision.need_guardrail,
                "next_goal": decision.next_goal,
                "meta": decision.meta,
            },
            "generation": generation,
            "memory": {
                "session_id": self.memory.session_id,
                "topic": self.memory.topic,
                "current_misconception": self.memory.current_misconception,
                "turn_count": self.memory.turn_count,
                "resolved": self.memory.resolved,
            },
            "guardrail": guardrail_result,
            "learning_report": learning_report,
        }

    def step(self, user_input: str) -> Dict[str, Any]:
        initial_state = {
            "system_version": self.system_version,
            "user_input": user_input,
            "memory": self.memory,
            "messages": [HumanMessage(content=user_input)],
        }
        config = {"configurable": {"thread_id": self.memory.session_id}}

        try:
            final_state = app_graph.invoke(initial_state, config)
        except Exception as e:
            logger_instance.error(f"Global exception during graph execution: {e}")
            self.abnormal_end_flag = True
            return {
                "perception": {
                    "intent": "Unknown",
                    "misconception_tag": None,
                    "cognitive_state": "认知僵局",
                    "risk_flag": False,
                    "confidence": 0.0,
                    "sentiment": "Confused",
                },
                "decision": {
                    "state": "S5",
                    "state_name": "Error_State",
                    "strategy": "Error_Handling",
                    "need_guardrail": False,
                    "next_goal": None,
                    "meta": {},
                },
                "generation": {
                    "raw_reply": "抱歉，系统遇到了一些问题，请稍后再试。",
                    "final_reply": "抱歉，系统遇到了一些问题，请稍后再试。",
                },
                "memory": {
                    "session_id": self.memory.session_id,
                    "topic": self.memory.topic,
                    "current_misconception": self.memory.current_misconception,
                    "turn_count": self.memory.turn_count,
                    "resolved": self.memory.resolved,
                },
                "guardrail": {"guardrail_triggered": False, "guardrail_reason": None},
            }

        return self._process_graph_result(final_state, user_input)

    async def astep(self, user_input: str) -> Dict[str, Any]:
        initial_state = {
            "system_version": self.system_version,
            "user_input": user_input,
            "memory": self.memory,
            "messages": [HumanMessage(content=user_input)],
        }
        config = {"configurable": {"thread_id": self.memory.session_id}}

        try:
            final_state = await app_graph.ainvoke(initial_state, config)
        except Exception as e:
            logger_instance.error(f"Global exception during async graph execution: {e}")
            self.abnormal_end_flag = True
            return {
                "perception": {
                    "intent": "Unknown",
                    "misconception_tag": None,
                    "cognitive_state": "认知僵局",
                    "risk_flag": False,
                    "confidence": 0.0,
                    "sentiment": "Confused",
                },
                "decision": {
                    "state": "S5",
                    "state_name": "Error_State",
                    "strategy": "Error_Handling",
                    "need_guardrail": False,
                    "next_goal": None,
                    "meta": {},
                },
                "generation": {
                    "raw_reply": "抱歉，系统遇到了一些问题，请稍后再试。",
                    "final_reply": "抱歉，系统遇到了一些问题，请稍后再试。",
                },
                "memory": {
                    "session_id": self.memory.session_id,
                    "topic": self.memory.topic,
                    "current_misconception": self.memory.current_misconception,
                    "turn_count": self.memory.turn_count,
                    "resolved": self.memory.resolved,
                },
                "guardrail": {"guardrail_triggered": False, "guardrail_reason": None},
            }

        return self._process_graph_result(final_state, user_input)

    def end_session(self, termination_reason: str = "resolved") -> None:
        summary_log = {
            "session_id": self.memory.session_id,
            "system_version": self.system_version,
            "student_profile": self.student_profile,
            "topic": self.memory.topic,
            "misconception_gt": self.misconception_init,
            "turn_count": self.memory.turn_count,
            "first_detected_misconception": self.memory.current_misconception,
            "resolved_flag": self.memory.resolved,
            "final_cognitive_state": "概念掌握验证" if self.memory.resolved else "认知僵局",
            "guardrail_trigger_count": self.guardrail_trigger_count,
            "answer_leakage_count": self.answer_leakage_count,
            "abnormal_end_flag": getattr(self, "abnormal_end_flag", False),
            "termination_reason": termination_reason,
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
            print(
                f"[state={result['decision']['state']} | strategy={result['decision']['strategy']} | misconception={result['perception']['misconception_tag']}]"
            )
            print("-" * 60)
            if self.memory.resolved:
                print("会话已解决，自动结束。")
                if result.get("learning_report"):
                    print("\n========== 学习报告 ==========")
                    print(result["learning_report"])
                    print("=============================\n")
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
        print(json.dumps(result["decision"], ensure_ascii=False, indent=2))
        print("=" * 60)
    app.end_session("demo_completed")


if __name__ == "__main__":
    app = SocraticTutorApp(session_id="chat_main")
    app.chat()
