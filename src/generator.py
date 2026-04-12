from __future__ import annotations
import json
import random
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from router import RouteDecision, SessionMemory
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import config

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _clean_reply(text: str) -> str:
    """清理回复文本，去掉思考标签和括号内的动作提示。"""
    # 尝试去除 <think> 标签及其内容。如果大模型忘记闭合标签，尝试匹配到“回复：”或“回答：”
    if "<think>" in text:
        text = re.sub(r'<think>.*?(?:</think>|回复：|回答：|回复:|回答:)', '', text, flags=re.DOTALL)
    # 去除括号包裹的内容（中文或英文括号），例如（思考一下）、(确认学生意图)
    text = re.sub(r'[（\(].*?[）\)]', '', text)
    return text.strip()

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
    analogies = "\n- ".join([a.get("analogy") for a in knowledge.get("analogies", []) if isinstance(a, dict) and a.get("analogy")])

    sentiment = decision.meta.get("sentiment", "")
    empathy_scaffolding = ""
    if sentiment in ["焦虑/挫败", "困惑"]:
        empathy_scaffolding = "\n\n【情感支架】\n检测到学生当前处于焦虑、挫败或困惑的情绪状态。请在回复的开头，先用简短、自然的话语进行共情和鼓励（例如：“没关系，这个问题确实有点绕”、“卡在这里很正常”等），然后再进行提问或引导。"

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
4. 回复必须简短、自然，符合日常口语习惯（1-3句话即可）。
5. 绝不要向学生暴露“反例”、“类比”、“知识点”、“支架”、“策略”等教学设计术语，必须将它们自然地转化为对话。
6. 当学生表现出困惑或多次卡壳时，绝不要重复相同的反问，必须提供一个具体的生活类比（如水流、跑步、木块等）或将问题拆解为更小的分步提问。
7. 绝对不要在回复中包含任何内部思考过程、策略说明或动作提示（如括号内的心理活动）。如果需要思考，请将思考过程写在 <think>...</think> 标签内。
8. 每次回复只能提出一个清晰的问题，严禁自问自答，严禁同时抛出多个维度的变量（如同时混杂重量、形状和体积）。{empathy_scaffolding}"""

    assembled_prompt = {
        "role_identity": "你是引导思考的初中物理苏格拉底式助教",
        "current_state_instruction": f"当前状态: {decision.state_name} ({decision.state}) - {decision.next_goal}",
        "current_strategy_instruction": f"当前策略: {decision.strategy}",
        "guardrail_rules": "禁泄露规则: 绝不直接给出最终结论，绝不代替学生完成关键推理，只使用提问或类比进行引导。"
    }

    if not config.DEEPSEEK_API_KEY:
        # Mock mode if API key is missing
        reply_text = f"（Mocked teacher response）我看到你现在的状态是 {decision.state_name}，我们在探讨 {misconception.get('misconception_name', '这个概念')}。你能再多说说你的想法吗？"
        final_reply = _clean_reply(reply_text)
        return {
            "raw_reply": reply_text,
            "final_reply": final_reply,
            "reply_type": _reply_type_from_state(decision.state),
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
    
    if len(memory.messages) > config.MAX_HISTORY_TURNS and history_summary:
        summary_prompt = f"【早期对话总结】\n{history_summary}\n\n【近期对话】"
        history_messages.append(SystemMessage(content=summary_prompt))

    for msg in memory.messages[-config.MAX_HISTORY_TURNS:]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        else:
            history_messages.append(AIMessage(content=msg["content"]))
            
    messages = [SystemMessage(content=system_prompt)] + history_messages + [HumanMessage(content=user_input)]
    
    if decision.need_guardrail or decision.state == "S2":
        redirect_prompt = "【重定向指令】学生刚刚试图直接索要答案或偏离主题。请用自然、委婉的口吻拒绝直接给出结论，或将话题拉回当前的物理讨论，并提出一个简单的引导问题。"
        messages.append(SystemMessage(content=redirect_prompt))
    
    guardrail_feedback = decision.meta.get("guardrail_feedback")
    if guardrail_feedback:
        feedback_prompt = f"【系统安全警告】你上一次的回复因违反安全规则被拦截，拦截理由是：{guardrail_feedback}。\n请重新组织语言，坚决避免直接给出最终结论或代替学生推理，而是通过提问或类比来引导学生。请确保你的回复符合当前状态的要求：{decision.state_name} ({decision.strategy})。"
        messages.append(SystemMessage(content=feedback_prompt))
    
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
        if decision.state == "S2" or decision.need_guardrail:
            follow_up = _pick_one(knowledge.get("verification_questions", []), default="你先说说：你现在最确定的那一步推理是什么？")
            reply_text = _pick_one(REFUSAL_REDIRECT_TEMPLATES).format(follow_up=follow_up)
        else:
            reply_text = "抱歉，我现在有些卡壳，我们能重新梳理一下刚才的问题吗？"

    final_reply = _clean_reply(reply_text)

    return {
        "raw_reply": reply_text,
        "final_reply": final_reply,
        "reply_type": _reply_type_from_state(decision.state),
        "knowledge_used": misconception.get("misconception_name"),
        "state": decision.state,
        "strategy": decision.strategy,
        "assembled_prompt": assembled_prompt
    }