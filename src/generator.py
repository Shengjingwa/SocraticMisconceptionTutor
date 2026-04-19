from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential

import config
from router import RouteDecision, SessionMemory

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _clean_reply(text: str) -> str:
    """清理回复文本，去掉思考标签及其前置内容和括号内的动作提示。"""
    if "<think>" in text:
        # 移除第一个 <think> 标签之前的所有内容
        text = re.sub(r"^.*?<think>", "<think>", text, flags=re.DOTALL)
        # 移除 <think>...</think> 标签及其内容，同时处理未闭合的情况
        text = re.sub(
            r"<think>.*?(?:</think>|回复：|回答：|回复:|回答:|$)", "", text, flags=re.DOTALL
        )

    # 彻底清理可能残留的单个标签
    text = text.replace("<think>", "").replace("</think>", "")

    # 清理大模型可能残留的思考过程前缀词
    text = re.sub(r"^(?:\n)*?(?:优化回复|最终回复|回复|回答|分析|思考)[：:]\s*", "", text).strip()

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
    return {
        "S2": "refusal_and_guidance",
        "S4": "cognitive_conflict_question",
        "S5": "scaffolded_prompt",
        "S6": "verification_prompt",
        "S8": "acknowledge_and_park",
    }.get(state, "guiding_question")


def _safe_question_template(user_input: str, decision: RouteDecision, memory: SessionMemory) -> str:
    tag = memory.current_misconception
    if decision.state == "S2":
        follow_up = "你能先把你最确定的那一步说出来吗？"
        if tag == "M-ELE-002":
            follow_up = "如果只有一根线连着电池和灯泡，电荷走到灯泡后“回到电池”的那条路在哪里？"
        elif tag == "M-ELE-001":
            follow_up = "如果电流真的被前面的灯泡“用掉”变少了，那多出来的电荷会去哪儿？会不会在某段导线里越堆越多？"
        elif tag == "M-BUO-001":
            follow_up = (
                "你觉得“重”到底指重量，还是指材料本身的性质？能举一个重但能浮、轻但会沉的例子吗？"
            )
        elif tag == "M-BUO-002":
            follow_up = "同一个物体完全没入水里以后继续下沉，它排开水的体积变了吗？"
        return _pick_one(REFUSAL_REDIRECT_TEMPLATES).format(follow_up=follow_up)
    if tag == "M-ELE-001":
        return "如果电流真的会被前面的灯泡“用掉”变少，你觉得那一秒钟流进第一个灯泡的电荷，会有一部分“卡住”不出来吗？"
    if tag == "M-ELE-002":
        return "如果只接正极也能一直亮，那电荷从正极出来以后，最后会一直堆在灯泡那一端吗？你觉得会发生什么？"
    if tag == "M-BUO-001":
        return "一根很大的木头往往比一颗小石子重，你觉得它一定会沉吗？如果不沉，你的“越重越沉”要怎么解释？"
    if tag == "M-BUO-002":
        return "压强越深越大没错，但上表面和下表面都一起变大时，你觉得它们的“差值”一定会变大吗？"
    return "你愿不愿意先说一个你认为最关键的依据（现象/推理步骤）？我只问一个问题：这个依据在更极端的情况下还成立吗？"


LLM_ERROR_FALLBACK_PHRASES = [
    "抱歉，我现在有些卡壳，我们能重新梳理一下刚才的问题吗？",
    "哎呀，我这会儿脑子有点转不过弯了，能换个说法再问我一次吗？",
    "不好意思，刚刚系统好像走神了，你能把刚才的想法再跟我说一遍吗？",
    "有点小故障，我没太理解。能麻烦你重新讲一下你最确定的部分吗？",
]


def generate_reply(
    user_input: str, decision: RouteDecision, memory: SessionMemory, messages: list = None
) -> Dict[str, Any]:
    if messages is None:
        messages = []


    formatted_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            formatted_messages.append({"role": "assistant", "content": msg.content})
        else:
            formatted_messages.append(msg)

    recent_history_text = "\n".join(
        [
            f"{msg['role']}: {msg['content']}"
            for msg in formatted_messages[-config.MAX_HISTORY_TURNS * 2 :]
        ]
    )
    knowledge = KNOWLEDGE_CHUNKS.get(memory.current_misconception, {})
    misconception = MISCONCEPTIONS.get(memory.current_misconception, {})

    if decision.meta.get("force_safe_template") is True:
        reply_text = _safe_question_template(user_input, decision, memory)
        final_reply = _clean_reply(reply_text)
        return {
            "raw_reply": reply_text,
            "final_reply": final_reply,
            "reply_type": _reply_type_from_state(decision.state),
            "knowledge_used": misconception.get("misconception_name"),
            "state": decision.state,
            "strategy": decision.strategy,
            "assembled_prompt": {"role_identity": "safe_template"},
        }

    # 构建自然语言系统提示词
    core_points = "\n- ".join(misconception.get("core_science_points", []))

    # 解析反例 (Counterexamples)
    ce_list = []
    for ce in misconception.get("counterexamples", []):
        if isinstance(ce, dict):
            ce_list.append(
                f"情境: {ce.get('scenario')} | 错误预测: {ce.get('misconception_prediction')} | 科学事实: {ce.get('actual_scientific_outcome')} | 冲突焦点: {ce.get('conflict_focus')}"
            )
        else:
            ce_list.append(str(ce))
    counterexamples = "\n- ".join(ce_list)

    # 解析类比 (Analogies)
    ana_list = []
    for a in misconception.get("analogies", []):
        if isinstance(a, dict):
            ana_list.append(
                f"模型: {a.get('model')} | 用途: {a.get('use_for')} | 局限性: {a.get('boundary')}"
            )
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
    cognitive_state = decision.meta.get("cognitive_state", "")

    empathy_scaffolding = ""
    fallback_strategy = ""
    subgoal_tracking = ""

    if cognitive_state == "认知僵局":
        subgoal_tracking = "\n\n【子目标追踪 (Sub-goal Tracking)】\n检测到学生处于“认知僵局”。请在 <think> 标签内规划一个 2-3 步的微引导路径（Micro-journey），并且在接下来的连续几轮对话中严格执行这个路径，不要轻易偏离。每次回复只执行其中一步，逐步引导学生打破僵局。"

    if sentiment in ["焦虑/挫败", "困惑"]:
        empathy_scaffolding = "\n\n【认知共情支架】\n检测到学生当前处于焦虑、挫败或困惑的情绪状态。严禁使用“没关系”、“别着急”等生硬套话！你必须通过指出物理概念本身容易混淆或反直觉的地方（例如：“这个现象确实反直觉，因为我们在生活中很少注意到……”）来建立“认知共情”，并将共情与下一个引导问题无缝融合。"

    # 针对多次卡壳或严重挫败的降级干预
    if (
        decision.state == "S5" and memory.recent_states.count("S5") >= 3
    ) or sentiment == "焦虑/挫败":
        fallback_strategy += "\n\n【降级干预策略】\n学生目前多次卡壳或极度挫败，请放宽引导要求。允许你先直接给出部分浅显的物理原理解释或实验现象说明，以此作为脚手架，然后再就下一步进行确认性提问。避免单纯的拒绝和反问。"

    if decision.state == "S4":
        if sentiment == "焦虑/挫败":
            fallback_strategy += "\n\n【认知共情策略】\n检测到学生处于焦虑/挫败状态且需要制造认知冲突(S4)。请使用“Yes, but...”(是的，但是...)的温和方式进行引导，先肯定学生推理中合理的部分，然后再抛出一个温和的反例或日常现象。**严禁使用极端的反例或强烈的归谬法**，以免加重学生的挫败感。"
        else:
            fallback_strategy += "\n\n【深度认知冲突与极端归谬策略】\n检测到学生极度固执。请设计一个**极其极端、甚至荒谬的思想实验**（例如：如果电流被消耗，串联100个灯泡，最后一个还会亮吗？如果浮力只看重力，把一根针和一艘万吨巨轮放进水里呢？），顺应学生的错误逻辑推导出一个明显荒谬的后果。\n**关键应对预案**：如果学生顺着你的极端假设得出了荒谬的结论（比如回答“第100个灯泡肯定不亮了”），**你绝对不能去反驳他，也不能搬出书本定论或实验事实去压迫他**。相反，你必须**顺势而为，继续放大荒谬感**，比如“原来如此！那如果在最后接一台需要很大电流的电视机呢，电视机还能开机吗？”或者“那你觉得家里接了那么多电器，离电闸最远的电器岂不是经常用不了？”通过引入生活常识，让学生自己发现逻辑的漏洞。"
    elif decision.state == "S5":
        if memory.recent_states.count("S5") >= 3:
            fallback_strategy += "\n\n【焦点转移与破而后立策略】\n检测到学生处于连续卡壳状态。**绝对停止当前的类比！** 学生已经陷入思维死胡同。你必须立即转移话题焦点（Focus Shift），例如从“水流”转移到“微观电子”，或者从“排水量”转移到“上下表面压力差”。在转移焦点后，用极其通俗的语言指出学生混淆的底层概念（如“能量”与“电荷”），提供一个新的、正确的物理起点，绝不留学生在原地内耗。"
        elif memory.recent_states.count("S5") >= 2:
            fallback_strategy += "\n\n【概念拆解与微支架策略 (Micro-scaffolding)】\n检测到学生在S5阶段卡壳。请停止重复宽泛的类比，而是将当前问题拆解为2个更小的、原子化的「概念区分」问题。例如，明确向学生指出他们可能混淆了哪两个物理量，然后通过一个「是/否」的判断题，逐步引导学生推导。"
    elif decision.state == "S7":
        fallback_strategy += (
            "\n\n【降级干预：事实兜底与具象体感重构 (Fact-Grounding & Concrete Rebuild)】\n"
            "检测到学生陷入极度顽固的认知僵局（P1死锁）。**立即停止所有的抽象类比、数字计算和极端归谬！**\n"
            "为了绝对不触碰泄题红线且打破学生的防御心理，你必须采取“先陈述客观事实，再引导具象体感”的终极策略：\n"
            "1. 直接抛出一个无可辩驳的、真实的【物理实验现象或硬核事实】。这个事实必须与学生的错误认知形成极强的反差。\n"
            "2. 在陈述完事实后，**严禁诉诸权威或强行说教**！相反，你应该引导学生去想象一个**极其具象的身体感官体验**（Concrete Physical Sensation）。例如：想象用手把一个空矿泉水瓶按进水里时的感受；想象在拥挤的走廊里大家一起往前挤的感受。\n"
            "3. 用这个强烈的体感经验作为“脚手架”，让学生重新思考之前的物理事实。例如：‘真实的物理实验结果是 [陈述打脸现象]。既然结果如此，你回忆一下 [某个身体感官体验] 的时候，是不是和这个现象很像？你觉得这是为什么？’"
        )
    elif decision.state == "S8":
        if memory.aborted:
            fallback_strategy += "\n\n【强制结束会话 (Force Termination)】\n学生拒绝搁置话题或继续纠缠。请直接用一句简短、温和但坚定的结束语结束本次讨论（例如：‘好的，我理解你的坚持。咱们今天先聊到这里，这个问题先放一放，辛苦啦！’）。绝对不要再提问或继续解释物理原理。"
        else:
            fallback_strategy += "\n\n【承认并搁置策略 (Acknowledge and Park)】\n检测到学生处于极度固执的僵局。请停止任何物理原理的讲授或提问！\n你必须表现出极强的同理心，承认这个问题确实很反直觉，肯定学生的独立思考，然后**主动提议暂时搁置这个问题**，例如：“我完全理解你的想法，这个点确实非常绕。咱们今天先不争论这个，下次找个真实的实验器材亲自试一试，怎么样？”"

    system_prompt = f"""你是引导思考的初中物理苏格拉底式助教。

【当前教学状态】
状态阶段: {decision.state_name} ({decision.state})
你的当前目标: {decision.next_goal}
采用的引导策略: {decision.strategy}

【可参考的知识点(仅供引导参考，请勿直接剧透)】
核心科学知识点: 
- {core_points if core_points else "无"}

可用的反例: 
- {counterexamples if counterexamples else "无"}

可用的类比: 
- {analogies if analogies else "无"}

学生可能的推理漏洞:
- {reasoning_flaws if reasoning_flaws else "无"}

【安全护栏规则 - 必须绝对遵守】
1. 绝不直接给出本题最终结论或标准答案。
2. 绝不代替学生完成关键的逻辑推理过程。
3. 只能通过提问、制造矛盾（认知冲突）或提供类比来进行引导（除降级干预外）。
4. 绝对不要顺应或肯定学生提出的错误物理观念！如果学生提出了迷思概念（例如“电流被消耗了”、“重物下落更快”），你只能说“这听起来很直觉，但我们可以看看这个实验...”，**严禁使用“你说得对”、“逻辑完全正确”等肯定词汇来附和错误的物理知识**。
5. 回复必须简短、自然，符合日常口语习惯（1-3句话即可）。
6. 绝不要向学生暴露“反例”、“类比”、“知识点”、“支架”、“策略”等教学设计术语，必须将它们自然地转化为对话。
7. 当学生表现出困惑或多次卡壳时，绝不要重复相同的反问，必须提供一个具体的生活类比（如水流、跑步、木块等）或将问题拆解为更小的分步提问。
8. **绝对禁止为类比辩护 (No Analogy Defense)**：类比只是工具，不是目的！如果学生对你举的类比产生误解，或者敏锐地指出了类比的局限性（例如反驳“电又不是人，它不会觉得挤”），你**绝对不能去解释或试图修正这个类比**！你必须大方承认类比的局限性（如：“你说得太对了，这个比喻确实不严谨”），然后**立即彻底抛弃该类比**，强制将对话视角拉回到目标物理情境本身或真实的物理实验数据中。
9. 绝对不要在回复中包含任何内部思考过程、策略说明或动作提示（如括号内的心理活动）。如果需要思考，请将思考过程写在 <think>...</think> 标签内。在 </think> 之后，你只能提出一个引导性的问题或类比，绝对不能把思考标签里的结论直接写出来。
10. 每次回复只能提出一个清晰的问题，严禁自问自答，严禁同时抛出多个维度的变量（如同时混杂重量、形状和体积）。
11. **防重复与防抽象策略**：面对顽固学生，**绝对不要重复已经失败的类比**。如果学生坚持错误，必须切换到完全不同的、日常生活中极其直观的物理经验（如骑自行车、提重物等），严禁使用复杂的数学抽象（如密度计算、排开水的精确体积）来试图说服学生。
12. **防早退机制**：如果学生即将理解（处于认知冲突中或刚开始动摇），**绝对不要提前结束对话**或说“下次再说”、“今天先到这里”。你必须坚持引导，直到学生得出结论或遭遇无法逾越的僵局（P1死锁）。

【红线警告】
在任何情况下，你的公开回复中绝对不允许直接出现本题的核心物理定论（如‘因此浮力等于排开水的重力’、‘只有闭合回路才能持续有电流’等）。你只能陈述现象，最终的定论必须留给学生自己说出来！**请注意：提供充分的物理情境描述、实验现象说明以及中间逻辑推导并不属于泄露，而是必要的引导。**{empathy_scaffolding}{fallback_strategy}{subgoal_tracking}"""

    assembled_prompt = {
        "role_identity": "你是引导思考的初中物理苏格拉底式助教",
        "current_state_instruction": f"当前状态: {decision.state_name} ({decision.state}) - {decision.next_goal}",
        "current_strategy_instruction": f"当前策略: {decision.strategy}",
        "guardrail_rules": "禁泄露规则: 绝不直接给出最终结论，绝不代替学生完成关键推理，只使用提问或类比进行引导。",
    }

    if decision.need_guardrail or decision.state == "S2":
        follow_up = _pick_one(
            knowledge.get("verification_questions", []),
            default="你先说说：你现在最确定的那一步推理是什么？",
        )
        raw_reply = _pick_one(REFUSAL_REDIRECT_TEMPLATES).format(follow_up=follow_up)
        final_reply = _clean_reply(raw_reply)
        return {
            "raw_reply": raw_reply,
            "final_reply": final_reply,
            "reply_type": "refusal_and_guidance",
            "knowledge_used": misconception.get("misconception_name"),
            "state": decision.state,
            "strategy": decision.strategy,
            "assembled_prompt": assembled_prompt,
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
            "assembled_prompt": assembled_prompt,
        }

    llm = config.get_tutor_llm(**config.DEFAULT_LLM_KWARGS)

    # 组装对话历史
    history_messages = []

    if len(messages) > config.MAX_HISTORY_TURNS and getattr(memory, "history_summary", None):
        summary_prompt = f"【早期对话总结】\n{memory.history_summary}\n\n【近期对话】"
        history_messages.append(SystemMessage(content=summary_prompt))

    for msg in formatted_messages[-config.MAX_HISTORY_TURNS :]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        else:
            history_messages.append(AIMessage(content=msg["content"]))

    messages = (
        [SystemMessage(content=system_prompt)]
        + history_messages
        + [HumanMessage(content=user_input)]
    )

    guardrail_feedback = decision.meta.get("guardrail_feedback")
    if guardrail_feedback:
        feedback_prompt = f"【系统安全警告】你上一次的回复因违反安全规则被拦截，拦截理由是：{guardrail_feedback}。\n请重新组织语言，坚决避免直接给出最终结论或代替学生推理，而是通过提问或类比来引导学生。请确保你的回复符合当前状态的要求：{decision.state_name} ({decision.strategy})。"
        messages.append(SystemMessage(content=feedback_prompt))

    @retry(
        stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        reraise=True,
    )
    def _invoke_llm():
        return llm.invoke(messages)

    try:
        response = _invoke_llm()
        reply_text = response.content
    except Exception as e:
        from logger import logger_instance

        logger_instance.error(f"LLM generation failed: {e}")
        reply_text = random.choice(LLM_ERROR_FALLBACK_PHRASES)

    final_reply = _clean_reply(reply_text)

    return {
        "raw_reply": reply_text,
        "final_reply": final_reply,
        "reply_type": _reply_type_from_state(decision.state),
        "knowledge_used": misconception.get("misconception_name"),
        "state": decision.state,
        "strategy": decision.strategy,
        "assembled_prompt": assembled_prompt,
    }


def generate_baseline_reply(
    user_input: str, memory: SessionMemory, messages: list = None
) -> Dict[str, Any]:
    if messages is None:
        messages = []

    from langchain_core.messages import SystemMessage

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
        reply_text = "（Mocked Baseline response）我们在探讨这个概念。你能再多说说你的想法吗？"
        final_reply = _clean_reply(reply_text)
        return {
            "raw_reply": reply_text,
            "final_reply": final_reply,
            "reply_type": "guiding_question",
            "knowledge_used": "Unknown",
            "state": "Baseline",
            "strategy": "General_Reply",
            "assembled_prompt": {"role_identity": "你是引导思考的初中物理苏格拉底式助教"},
        }

    llm = config.get_tutor_llm(**config.DEFAULT_LLM_KWARGS)

    history_messages = []
    if len(messages) > config.MAX_HISTORY_TURNS and getattr(memory, "history_summary", None):
        summary_prompt = f"【早期对话总结】\n{memory.history_summary}\n\n【近期对话】"
        history_messages.append(SystemMessage(content=summary_prompt))

    for msg in formatted_messages[-config.MAX_HISTORY_TURNS :]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        else:
            history_messages.append(AIMessage(content=msg["content"]))

    final_messages = (
        [SystemMessage(content=system_prompt)]
        + history_messages
        + [HumanMessage(content=user_input)]
    )

    @retry(
        stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        reraise=True,
    )
    def _invoke_llm():
        return llm.invoke(final_messages)

    try:
        response = _invoke_llm()
        reply_text = response.content
    except Exception as e:
        from logger import logger_instance

        logger_instance.error(f"LLM baseline generation failed: {e}")
        reply_text = random.choice(LLM_ERROR_FALLBACK_PHRASES)

    final_reply = _clean_reply(reply_text)

    return {
        "raw_reply": reply_text,
        "final_reply": final_reply,
        "reply_type": "guiding_question",
        "knowledge_used": "Unknown",
        "state": "Baseline",
        "strategy": "General_Reply",
        "assembled_prompt": {"role_identity": "你是引导思考的初中物理苏格拉底式助教"},
    }


REPORT_ERROR_FALLBACK_PHRASES = [
    "生成学习报告失败，请稍后重试。",
    "抱歉，总结报告生成遇到了点小问题，等会儿再试试吧。",
    "哎呀，报告生成卡住了，可以稍后再试一下哦。",
]


def generate_learning_report(memory: SessionMemory, messages: list = None) -> str:
    """当会话解决（resolved == True）时生成学习报告"""
    if not config.DASHSCOPE_API_KEY:
        return "（Mocked Report）学生已成功克服迷思概念，掌握了相关知识点。"

    llm = config.get_tutor_llm(**config.DEFAULT_LLM_KWARGS)

    if messages is None:
        messages = []


    formatted_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            formatted_messages.append({"role": "assistant", "content": msg.content})
        else:
            formatted_messages.append(msg)

    history_text = ""
    if getattr(memory, "history_summary", None):
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
        reraise=True,
    )
    def _invoke_llm():
        return llm.invoke(messages)

    try:
        response = _invoke_llm()
        return _clean_reply(response.content)
    except Exception as e:
        from logger import logger_instance

        logger_instance.error(f"Failed to generate learning report: {e}")
        return random.choice(REPORT_ERROR_FALLBACK_PHRASES)
