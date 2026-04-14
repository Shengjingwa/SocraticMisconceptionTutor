from __future__ import annotations
import json
import random
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from router import RouteDecision, SessionMemory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import config

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _clean_reply(text: str) -> str:
    """清理回复文本，去掉思考标签及其前置内容和括号内的动作提示。"""
    if "<think>" in text:
        # 移除第一个 <think> 标签之前的所有内容
        text = re.sub(r'^.*?<think>', '<think>', text, flags=re.DOTALL)
        # 移除 <think>...</think> 标签及其内容，同时处理未闭合的情况
        text = re.sub(r'<think>.*?(?:</think>|回复：|回答：|回复:|回答:|$)', '', text, flags=re.DOTALL)
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
    "我理解你现在可能有些卡壳，不过别着急，我不能直接把结论喂给你。我们换个简单的角度：{follow_up}",
    "直接告诉你答案可能帮不到你真正弄懂。咱们退一步，看看这个现象：{follow_up}",
    "我知道这有点绕，但我直接说出结论你就没法自己推导了。我们把问题拆开，你觉得：{follow_up}",
]

def _pick_one(items: List[Any], default: Any = None) -> Any:
    return random.choice(items) if items else default

def _reply_type_from_state(state: str) -> str:
    return {"S2":"refusal_and_guidance","S4":"cognitive_conflict_question","S5":"scaffolded_prompt","S6":"verification_prompt"}.get(state, "guiding_question")

def generate_reply(user_input: str, decision: RouteDecision, memory: SessionMemory, messages: list = None) -> Dict[str, Any]:
    if messages is None:
        messages = []
    
    from langchain_core.messages import HumanMessage, AIMessage
    formatted_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            formatted_messages.append({"role": "assistant", "content": msg.content})
        else:
            formatted_messages.append(msg)
            
    recent_history_text = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in formatted_messages[-config.MAX_HISTORY_TURNS*2:]]
    )
    knowledge = KNOWLEDGE_CHUNKS.get(memory.current_misconception, {})
    misconception = MISCONCEPTIONS.get(memory.current_misconception, {})
    
    # 构建自然语言系统提示词
    core_points = "\n- ".join(misconception.get("core_science_points", []))
    
    # 解析反例 (Counterexamples)
    ce_list = []
    for ce in misconception.get("counterexamples", []):
        if isinstance(ce, dict):
            ce_list.append(f"情境: {ce.get('scenario')} | 错误预测: {ce.get('misconception_prediction')} | 科学事实: {ce.get('actual_scientific_outcome')} | 冲突焦点: {ce.get('conflict_focus')}")
        else:
            ce_list.append(str(ce))
    counterexamples = "\n- ".join(ce_list)
    
    # 解析类比 (Analogies)
    ana_list = []
    for a in misconception.get("analogies", []):
        if isinstance(a, dict):
            ana_list.append(f"模型: {a.get('model')} | 用途: {a.get('use_for')} | 局限性: {a.get('boundary')}")
        else:
            ana_list.append(str(a))
    analogies = "\n- ".join(ana_list)
    
    # 解析推理漏洞 (Reasoning Flaws)
    rf_list = []
    for rf in misconception.get("reasoning_flaws", []):
        if isinstance(rf, dict):
            rf_list.append(f"漏洞类型: {rf.get('flaw_type')} | 描述: {rf.get('description')}")
        else:
            rf_list.append(str(rf))
    reasoning_flaws = "\n- ".join(rf_list)

    sentiment = decision.meta.get("sentiment", "")
    empathy_scaffolding = ""
    fallback_strategy = ""

    if sentiment in ["焦虑/挫败", "困惑"]:
        empathy_scaffolding = "\n\n【认知共情支架】\n检测到学生当前处于焦虑、挫败或困惑的情绪状态。严禁使用“没关系”、“别着急”等生硬套话！你必须通过指出物理概念本身容易混淆或反直觉的地方（例如：“这个现象确实反直觉，因为我们在生活中很少注意到……”）来建立“认知共情”，并将共情与下一个引导问题无缝融合。"
        
    # 针对多次卡壳或严重挫败的降级干预
    if (decision.state == "S5" and memory.recent_states.count("S5") >= 3) or sentiment == "焦虑/挫败":
        fallback_strategy += "\n\n【降级干预策略】\n学生目前多次卡壳或极度挫败，请放宽引导要求。允许你先直接给出部分浅显的物理原理解释或实验现象说明，以此作为脚手架，然后再就下一步进行确认性提问。避免单纯的拒绝和反问。"

    if decision.state == "S4":
        if sentiment == "焦虑/挫败":
            fallback_strategy += "\n\n【认知共情策略】\n检测到学生处于焦虑/挫败状态且需要制造认知冲突(S4)。请使用“Yes, but...”(是的，但是...)的温和方式进行引导，先肯定学生推理中合理的部分，然后再抛出一个温和的反例或日常现象。**严禁使用极端的反例或强烈的归谬法**，以免加重学生的挫败感。"
        else:
            fallback_strategy += "\n\n【深度认知冲突策略】\n要求你强制采用“归谬法（Reductio ad absurdum）”或“极端情境法”，顺应学生的错误逻辑推导出一个明显荒谬的后果，以此制造认知冲突并打破僵局。"
    elif decision.state == "S5":
        if memory.recent_states.count("S5") >= 3:
            fallback_strategy += "\n\n【深度认知冲突策略】\n检测到学生处于连续卡壳状态，要求你强制采用“归谬法（Reductio ad absurdum）”或“极端情境法”，顺应学生的错误逻辑推导出一个明显荒谬的后果，以此制造认知冲突并打破僵局。"
        elif memory.recent_states.count("S5") >= 2:
            fallback_strategy += "\n\n【微支架策略 (Micro-scaffolding)】\n检测到学生在S5阶段卡壳。请停止重复宽泛的类比，而是将当前问题拆解为2个更小的、原子化的「是/否」判断题，逐步引导学生推导。"

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

学生可能的推理漏洞:
- {reasoning_flaws if reasoning_flaws else '无'}

【安全护栏规则 - 必须绝对遵守】
1. 绝不直接给出本题最终结论或标准答案。
2. 绝不代替学生完成关键的逻辑推理过程。
3. 只能通过提问、制造矛盾（认知冲突）或提供类比来进行引导（除降级干预外）。
4. 回复必须简短、自然，符合日常口语习惯（1-3句话即可）。
5. 绝不要向学生暴露“反例”、“类比”、“知识点”、“支架”、“策略”等教学设计术语，必须将它们自然地转化为对话。
6. 当学生表现出困惑或多次卡壳时，绝不要重复相同的反问，必须提供一个具体的生活类比（如水流、跑步、木块等）或将问题拆解为更小的分步提问。若学生对当前类比产生误解或排斥，绝对不要去解释或为该类比辩护，必须大方承认其局限性并强制将视角拉回目标物理情境本身或极端条件。
7. 绝对不要在回复中包含任何内部思考过程、策略说明或动作提示（如括号内的心理活动）。如果需要思考，请将思考过程写在 <think>...</think> 标签内。
8. 每次回复只能提出一个清晰的问题，严禁自问自答，严禁同时抛出多个维度的变量（如同时混杂重量、形状和体积）。{empathy_scaffolding}{fallback_strategy}"""

    assembled_prompt = {
        "role_identity": "你是引导思考的初中物理苏格拉底式助教",
        "current_state_instruction": f"当前状态: {decision.state_name} ({decision.state}) - {decision.next_goal}",
        "current_strategy_instruction": f"当前策略: {decision.strategy}",
        "guardrail_rules": "禁泄露规则: 绝不直接给出最终结论，绝不代替学生完成关键推理，只使用提问或类比进行引导。"
    }

    if decision.need_guardrail or decision.state == "S2":
        follow_up = _pick_one(knowledge.get("verification_questions", []), default="你先说说：你现在最确定的那一步推理是什么？")
        raw_reply = _pick_one(REFUSAL_REDIRECT_TEMPLATES).format(follow_up=follow_up)
        final_reply = _clean_reply(raw_reply)
        return {
            "raw_reply": raw_reply,
            "final_reply": final_reply,
            "reply_type": "refusal_and_guidance",
            "knowledge_used": misconception.get("misconception_name"),
            "state": decision.state,
            "strategy": decision.strategy,
            "assembled_prompt": assembled_prompt
        }

    if not config.DASHSCOPE_API_KEY:
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

    llm = config.get_tutor_llm(**config.DEFAULT_LLM_KWARGS)
    
    # 组装对话历史
    history_messages = []
    
    if len(messages) > config.MAX_HISTORY_TURNS and getattr(memory, 'history_summary', None):
        summary_prompt = f"【早期对话总结】\n{memory.history_summary}\n\n【近期对话】"
        history_messages.append(SystemMessage(content=summary_prompt))

    for msg in formatted_messages[-config.MAX_HISTORY_TURNS:]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        else:
            history_messages.append(AIMessage(content=msg["content"]))
            
    messages = [SystemMessage(content=system_prompt)] + history_messages + [HumanMessage(content=user_input)]
    
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

def generate_baseline_reply(user_input: str, memory: SessionMemory, messages: list = None) -> Dict[str, Any]:
    if messages is None:
        messages = []
    
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    formatted_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            formatted_messages.append({"role": "assistant", "content": msg.content})
        else:
            formatted_messages.append(msg)
            
    system_prompt = """你是引导思考的初中物理苏格拉底式助教。
请通过提问或举例的方式引导学生自己思考物理问题。
注意：
1. 绝不直接给出最终结论或标准答案。
2. 绝不代替学生完成关键的逻辑推理过程。
3. 回复必须简短、自然，符合日常口语习惯（1-3句话即可）。
4. 如果需要思考，请将思考过程写在 <think>...</think> 标签内。"""

    if not config.DASHSCOPE_API_KEY:
        reply_text = f"（Mocked Baseline response）我们在探讨这个概念。你能再多说说你的想法吗？"
        final_reply = _clean_reply(reply_text)
        return {
            "raw_reply": reply_text,
            "final_reply": final_reply,
            "reply_type": "guiding_question",
            "knowledge_used": "Unknown",
            "state": "Baseline",
            "strategy": "General_Reply",
            "assembled_prompt": {"role_identity": "你是引导思考的初中物理苏格拉底式助教"}
        }

    llm = config.get_tutor_llm(**config.DEFAULT_LLM_KWARGS)
    
    history_messages = []
    if len(messages) > config.MAX_HISTORY_TURNS and getattr(memory, 'history_summary', None):
        summary_prompt = f"【早期对话总结】\n{memory.history_summary}\n\n【近期对话】"
        history_messages.append(SystemMessage(content=summary_prompt))

    for msg in formatted_messages[-config.MAX_HISTORY_TURNS:]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        else:
            history_messages.append(AIMessage(content=msg["content"]))
            
    final_messages = [SystemMessage(content=system_prompt)] + history_messages + [HumanMessage(content=user_input)]
    
    @retry(
        stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        reraise=True
    )
    def _invoke_llm():
        return llm.invoke(final_messages)

    try:
        response = _invoke_llm()
        reply_text = response.content
    except Exception as e:
        from logger import logger_instance
        logger_instance.error(f"LLM baseline generation failed: {e}")
        reply_text = "抱歉，我现在有些卡壳，我们能重新梳理一下刚才的问题吗？"

    final_reply = _clean_reply(reply_text)

    return {
        "raw_reply": reply_text,
        "final_reply": final_reply,
        "reply_type": "guiding_question",
        "knowledge_used": "Unknown",
        "state": "Baseline",
        "strategy": "General_Reply",
        "assembled_prompt": {"role_identity": "你是引导思考的初中物理苏格拉底式助教"}
    }

def generate_learning_report(memory: SessionMemory, messages: list = None) -> str:
    """当会话解决（resolved == True）时生成学习报告"""
    if not config.DASHSCOPE_API_KEY:
        return "（Mocked Report）学生已成功克服迷思概念，掌握了相关知识点。"

    llm = config.get_tutor_llm(**config.DEFAULT_LLM_KWARGS)

    if messages is None:
        messages = []
    
    from langchain_core.messages import HumanMessage, AIMessage
    formatted_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            formatted_messages.append({"role": "assistant", "content": msg.content})
        else:
            formatted_messages.append(msg)

    history_text = ""
    if getattr(memory, 'history_summary', None):
        history_text += f"早期对话摘要：\n{memory.history_summary}\n\n"

    for msg in formatted_messages:
        role = "学生" if msg["role"] == "user" else "老师"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""请根据以下师生对话历史，生成一份简短的学生学习报告。
报告需要包含以下几点：
1. 初始迷思概念：学生一开始的错误观念是什么。
2. 认知转变过程：学生在哪个环节、因为什么例子或引导产生了认知冲突并发生转变。
3. 最终掌握情况：学生最终建立的正确物理认知是什么。

对话历史：
{history_text}

请以客观、专业的教师视角撰写，字数控制在200-300字左右。"""

    messages = [HumanMessage(content=prompt)]

    @retry(
        stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        reraise=True
    )
    def _invoke_llm():
        return llm.invoke(messages)

    try:
        response = _invoke_llm()
        return _clean_reply(response.content)
    except Exception as e:
        from logger import logger_instance
        logger_instance.error(f"Failed to generate learning report: {e}")
        return "生成学习报告失败，请稍后重试。"
