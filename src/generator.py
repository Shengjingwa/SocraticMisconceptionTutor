from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
from router import RouteDecision, SessionMemory

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []

# Load data
misconceptions_data = _load_json("misconceptions.json")
strategy_templates_data = _load_json("strategy_templates.json")
knowledge_chunks_data = _load_json("knowledge_chunks.json")

MISCONCEPTIONS = {item["id"]: item for item in misconceptions_data}
STRATEGY_TEMPLATES = {item["strategy_name"]: item for item in strategy_templates_data}
KNOWLEDGE_CHUNKS = {item["misconception_tag"]: item for item in knowledge_chunks_data}

REFUSAL_REDIRECT_TEMPLATES = [
    "我不会直接给你标准答案，但我们可以一步一步想。{follow_up}",
    "我先不直接代答，我们一起把关键关系想清楚。{follow_up}",
    "这题我不直接给结论，不过我可以陪你把思路搭出来。{follow_up}",
]

def _pick_one(items: List[Any], default: Any = None) -> Any:
    return random.choice(items) if items else default

def _reply_type_from_state(state: str) -> str:
    return {"S2":"refusal_and_guidance","S4":"cognitive_conflict_question","S5":"scaffolded_prompt","S6":"verification_prompt"}.get(state, "guiding_question")

def generate_reply(user_input: str, decision: RouteDecision, memory: SessionMemory, history_summary: str = "") -> Dict[str, Any]:
    knowledge = KNOWLEDGE_CHUNKS.get(memory.current_misconception, {})
    misconception = MISCONCEPTIONS.get(memory.current_misconception, {})
    
    # 组装受控生成提示（5个Prompt部件）
    assembled_prompt = {
        "role_identity": "你是引导思考的初中物理苏格拉底式助教",
        "current_state_instruction": f"当前状态: {decision.state_name} ({decision.state}) - {decision.next_goal}",
        "current_strategy_instruction": f"当前策略: {decision.strategy}",
        "knowledge_snippets": {
            "core_points": knowledge.get("core_science_points", []),
            "counterexamples": knowledge.get("counterexamples", []),
            "analogies": [a.get("analogy") for a in knowledge.get("analogies", []) if isinstance(a, dict)],
        },
        "guardrail_rules": "禁泄露规则: 绝不直接给出最终结论，绝不代替学生完成关键推理，只使用提问或类比进行引导。"
    }

    if decision.need_guardrail or decision.state == "S2":
        follow_up = _pick_one(knowledge.get("verification_questions", []), default="你先说说：你现在最确定的那一步推理是什么？")
        final_reply = _pick_one(REFUSAL_REDIRECT_TEMPLATES).format(follow_up=follow_up)
        return {
            "raw_reply": final_reply, 
            "final_reply": final_reply, 
            "reply_type": "refusal_and_guidance", 
            "knowledge_used": misconception.get("misconception_name"), 
            "state": decision.state, 
            "strategy": decision.strategy,
            "assembled_prompt": assembled_prompt
        }

    strategy_item = STRATEGY_TEMPLATES.get(decision.strategy, {})
    template = _pick_one(strategy_item.get("template_bank", [])) or _pick_one(strategy_item.get("fallback_templates", []), default="我们先一步一步想。")
    
    main_text = template
    
    extension = ""
    if decision.state == "S4":
        counterexample = _pick_one(knowledge.get("counterexamples", []))
        if counterexample:
            extension = f" 如果你愿意，可以顺便检查这个情况：{counterexample}"
    elif decision.state == "S5":
        core_point = _pick_one(knowledge.get("core_science_points", []))
        if core_point:
            extension = f" 先给你一个小支架：{core_point}"
    elif decision.state == "S6":
        verification_q = _pick_one(knowledge.get("verification_questions", []))
        if verification_q:
            extension = f" 再验证一步：{verification_q}"
            
    final_reply = (main_text + extension).strip()
    return {
        "raw_reply": main_text, 
        "final_reply": final_reply, 
        "reply_type": _reply_type_from_state(decision.state), 
        "knowledge_used": misconception.get("misconception_name"), 
        "state": decision.state, 
        "strategy": decision.strategy,
        "assembled_prompt": assembled_prompt
    }