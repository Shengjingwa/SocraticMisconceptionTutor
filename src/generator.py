from __future__ import annotations
import json
import random
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from router import RouteDecision, SessionMemory
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import config

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        from logger import logger_instance
        logger_instance.error(f"Failed to load JSON {filename}: {e}")
    return []

# Load data
misconceptions_data = _load_json("misconceptions.json")
knowledge_chunks_data = _load_json("knowledge_chunks.json")

MISCONCEPTIONS = {item["id"]: item for item in misconceptions_data}
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
    
    # 构建自然语言系统提示词
    core_points = "\n- ".join(knowledge.get("core_science_points", []))
    counterexamples = "\n- ".join(knowledge.get("counterexamples", []))
    analogies = "\n- ".join([a.get("analogy") for a in knowledge.get("analogies", []) if isinstance(a, dict)])

    system_prompt = f"""你是引导思考的初中物理苏格拉底式助教。

【当前教学状态】
状态阶段: {decision.state_name} ({decision.state})
你的当前目标: {decision.next_goal}
采用的引导策略: {decision.strategy}

【可参考的知识点(仅供引导参考，请勿直接剧透)】
核心科学知识点: 
- {core_points if core_points else '无'}

可用的反例: 
- {counterexamples if counterexamples else '无'}

可用的类比: 
- {analogies if analogies else '无'}

【安全护栏规则 - 必须绝对遵守】
1. 绝不直接给出最终结论或标准答案。
2. 绝不代替学生完成关键的逻辑推理过程。
3. 只能通过提问、制造矛盾（认知冲突）或提供类比来进行引导。
4. 回复必须简短、自然，符合日常口语习惯（1-3句话即可）。"""

    assembled_prompt = {
        "role_identity": "你是引导思考的初中物理苏格拉底式助教",
        "current_state_instruction": f"当前状态: {decision.state_name} ({decision.state}) - {decision.next_goal}",
        "current_strategy_instruction": f"当前策略: {decision.strategy}",
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

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.LLM_BASE_URL
    )
    
    # 组装对话历史
    history_messages = []
    for msg in memory.messages[-config.MAX_HISTORY_TURNS:]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        else:
            history_messages.append(AIMessage(content=msg["content"]))
            
    messages = [SystemMessage(content=system_prompt)] + history_messages + [HumanMessage(content=user_input)]
    
    @retry(
        stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        reraise=True
    )
    def _invoke_llm():
        return llm.invoke(messages)

    try:
        response = _invoke_llm()
        reply_text = response.content
    except Exception as e:
        from logger import logger_instance
        logger_instance.error(f"LLM generation failed: {e}")
        reply_text = "抱歉，我现在有些卡壳，我们能重新梳理一下刚才的问题吗？"
    
    return {
        "raw_reply": reply_text,
        "final_reply": reply_text,
        "reply_type": _reply_type_from_state(decision.state),
        "knowledge_used": misconception.get("misconception_name"),
        "state": decision.state,
        "strategy": decision.strategy,
        "assembled_prompt": assembled_prompt
    }