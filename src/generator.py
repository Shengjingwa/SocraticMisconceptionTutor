
from __future__ import annotations
import random
from typing import Any, Dict, List, Optional
from router import RouteDecision, SessionMemory

DEFAULT_STRATEGY_TEMPLATES = {
    "Clarification": {"template_bank": [
        "你这里说的‘{focus_term}’具体是指什么？",
        "我们先把这个词说清楚：你这里的‘{focus_term}’到底表示什么现象？",
        "你能把刚才那句话换一种更具体的说法吗？"
    ], "fallback_templates": ["我们先把你说的关键词解释清楚，再往下推理。"]},
    "Assumption_Probing": {"template_bank": [
        "你这个判断背后默认了什么前提？这个前提一定成立吗？",
        "你是不是默认‘{assumption}’？如果这个前提不成立，结论还站得住吗？"
    ], "fallback_templates": ["我们先不改答案，先找一找你这个想法最关键的前提是什么。"]},
    "Evidence_Seeking": {"template_bank": [
        "你这个判断有什么现象、实验或测量结果可以支持吗？",
        "如果要说服别人，你会拿出什么证据来证明‘{student_claim}’？"
    ], "fallback_templates": ["先找证据，再下判断。"]},
    "Consequence_Exploration": {"template_bank": [
        "如果按你的想法一直推下去，会出现什么结果？",
        "如果把这个规则推广到同类情况，会不会出现和经验相冲突的地方？"
    ], "fallback_templates": ["先把你的想法继续推到下一个场景看看。"]},
    "Analogical_Scaffolding": {"template_bank": [
        "这个概念有点抽象，我们先借一个熟悉场景来想：{analogy}。不过要注意，它只帮助我们理解{analogy_use_for}。",
        "我们先用一个类比搭桥：{analogy}。你觉得它最像原问题里的哪一部分？"
    ], "fallback_templates": ["我们先借一个简单经验做支架，等抓住核心后再回到正式概念。"]},
}
DEFAULT_KNOWLEDGE = {
    "M-ELE-001": {"misconception_name": "电流会被灯泡消耗（电流消耗模型）", "core_science_points": ["在稳定的串联电路中，电流在各处相同。", "灯泡发光时发生的是电能向光能和内能的转化，而不是电流本身被‘吃掉’。"], "counterexamples": ["如果把电流表接在同一串联回路的不同位置，读数应一致。"], "analogies": [{"analogy": "闭合回路中的连续流动", "use_for": "帮助理解同一路径中的流动必须连续。", "boundary": "不能机械推出‘前面先把电流用掉’。"}], "verification_questions": ["如果把电流表分别接在灯泡前后，读数应该怎样？为什么？"]},
    "M-ELE-002": {"misconception_name": "单极模型 / 不需要闭合回路", "core_science_points": ["电流形成需要连续、闭合的导电路径。", "电路任意一点断开，电流不能持续流动，灯泡不会发光。"], "counterexamples": ["若只接电池一端而不形成完整回路，常规小灯泡不会稳定发光。"], "analogies": [{"analogy": "闭环水路", "use_for": "帮助理解只有形成完整通路，流动才能持续。", "boundary": "类比只帮助理解回路完整性，不代表电流等于水。"}], "verification_questions": ["为什么开关一断开，灯泡就不亮了？"]},
    "M-BUO-001": {"misconception_name": "重物一定下沉（重物必沉）", "core_science_points": ["沉浮不能只看重不重，而要看浮力与重力的关系。", "阿基米德原理表明：浮力等于物体排开液体所受的重力。"], "counterexamples": ["铁钉会沉，但钢制轮船可以漂浮。"], "analogies": [{"analogy": "向下拉与向上托的对抗", "use_for": "帮助理解沉浮是重力与浮力的比较。", "boundary": "类比只帮助理解受力比较，不替代密度与排液体积。"}], "verification_questions": ["为什么‘铁船能浮、铁钉会沉’能反驳‘重物一定下沉’？"]},
    "M-BUO-002": {"misconception_name": "浮力只由深度决定（越深浮力越大）", "core_science_points": ["液体压强随深度增加，但浮力是上下表面压力差形成的净向上力。", "完全浸没后若排开液体体积不变，继续加深位置时浮力通常不再增大。"], "counterexamples": ["同一物体完全浸没后继续下沉，浮力并不会因深度增加而持续增大。"], "analogies": [{"analogy": "上下受压差的净托举", "use_for": "帮助理解浮力来自受力差，不是单看某一点压强。", "boundary": "不能替代排开液体重力的定量理解。"}], "verification_questions": ["为什么同一个物体完全浸没后继续下沉，浮力通常不会继续增大？"]},
}
REFUSAL_REDIRECT_TEMPLATES = [
    "我不会直接给你标准答案，但我们可以一步一步想。{follow_up}",
    "我先不直接代答，我们一起把关键关系想清楚。{follow_up}",
    "这题我不直接给结论，不过我可以陪你把思路搭出来。{follow_up}",
]

def _extract_focus_term(user_input: str, misconception_tag: Optional[str]) -> str:
    return {
        "M-ELE-001": "电流变少/被用掉",
        "M-ELE-002": "闭合回路/只接一端",
        "M-BUO-001": "重就会沉",
        "M-BUO-002": "越深浮力越大",
    }.get(misconception_tag, "这个说法")

def _extract_assumption(misconception_tag: Optional[str]) -> str:
    return {
        "M-ELE-001": "电流像会被用掉的东西一样，经过灯泡就会变少",
        "M-ELE-002": "电流只要从电池出来就够了，不需要返回路径",
        "M-BUO-001": "沉浮只由绝对重量决定",
        "M-BUO-002": "压强更大就必然意味着浮力更大",
    }.get(misconception_tag, "当前结论依赖了一个未被检查的前提")

def _pick_one(items: List[Any], default: Any = None) -> Any:
    return random.choice(items) if items else default

def _render_template(template: str, *, user_input: str, misconception_tag: Optional[str], knowledge: Dict[str, Any]) -> str:
    analogy_item = _pick_one(knowledge.get("analogies", []), default={})
    return template.format(
        focus_term=_extract_focus_term(user_input, misconception_tag),
        student_claim=user_input.strip(),
        assumption=_extract_assumption(misconception_tag),
        analogy=analogy_item.get("analogy", "一个更具体的熟悉场景"),
        analogy_use_for=analogy_item.get("use_for", "帮助你先抓住核心关系"),
    )

def _reply_type_from_state(state: str) -> str:
    return {"S2":"refusal_and_guidance","S4":"cognitive_conflict_question","S5":"scaffolded_prompt","S6":"verification_prompt"}.get(state, "guiding_question")

def generate_reply(user_input: str, decision: RouteDecision, memory: SessionMemory, history_summary: str = "") -> Dict[str, Any]:
    knowledge = DEFAULT_KNOWLEDGE.get(memory.current_misconception, {})
    if decision.need_guardrail or decision.state == "S2":
        follow_up = _pick_one(knowledge.get("verification_questions", []), default="你先说说：你现在最确定的那一步推理是什么？")
        final_reply = _pick_one(REFUSAL_REDIRECT_TEMPLATES).format(follow_up=follow_up)
        return {"raw_reply": final_reply, "final_reply": final_reply, "reply_type": "refusal_and_guidance", "knowledge_used": knowledge.get("misconception_name"), "state": decision.state, "strategy": decision.strategy}
    strategy_item = DEFAULT_STRATEGY_TEMPLATES.get(decision.strategy, {})
    template = _pick_one(strategy_item.get("template_bank", [])) or _pick_one(strategy_item.get("fallback_templates", []), default="我们先一步一步想。")
    main_text = _render_template(template, user_input=user_input, misconception_tag=memory.current_misconception, knowledge=knowledge)
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
    return {"raw_reply": main_text, "final_reply": final_reply, "reply_type": _reply_type_from_state(decision.state), "knowledge_used": knowledge.get("misconception_name"), "state": decision.state, "strategy": decision.strategy}
