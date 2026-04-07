
from __future__ import annotations
import re
from typing import Optional, Tuple, List
from router import PerceptionResult

DIRECT_ANSWER_PATTERNS = [
    r"直接给(?:我)?答案", r"直接告诉我(?:结论|答案)", r"别问了", r"不要提示", r"不要引导",
    r"直接说", r"完整步骤", r"标准答案", r"帮我做(?:出来)?", r"给我最终答案", r"给结论"
]
OFF_TOPIC_HINTS = ["历史", "英语作文", "化学方程式", "地理", "政治", "古诗", "生物"]
STUCK_HINTS = ["我不知道", "我不懂", "我想不出来", "说不清", "不会", "搞不懂", "有点懵", "不明白"]
SHAKING_HINTS = ["好像", "可能", "也许", "不一定", "是不是", "我不太确定"]
NEAR_CORRECT_HINTS = ["因为排开液体", "因为闭合回路", "电能转化", "串联电流相同", "浮力等于", "阿基米德原理", "密度"]
RULES = {
    "M-ELE-001": ["电流变少", "电流被消耗", "用掉电流", "前面灯泡用掉", "后面电流更小", "灯泡消耗电流"],
    "M-ELE-002": ["只接正极", "负极不用接", "不需要闭合", "电流只流出", "一根线也行", "回路不重要"],
    "M-BUO-001": ["重就沉", "轻就浮", "越重越沉", "主要看重量", "重物必沉", "轻物必浮"],
    "M-BUO-002": ["越深越大", "浮力看深度", "深度决定浮力", "水压越大浮力越大", "浮力随深度增加"],
}
KNOWLEDGE_INQUIRY_HINTS = ["什么是闭合回路", "阿基米德原理", "浮力是什么", "电流是什么", "浮沉条件"]

def _normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = text.replace("？", "?").replace("，", ",").replace("。", ".")
    text = re.sub(r"\s+", "", text)
    return text

def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)

def _regex_hit(text: str, patterns: List[str]) -> bool:
    return any(re.search(p, text) for p in patterns)

def predict_misconception(user_input: str) -> Tuple[Optional[str], int]:
    text = _normalize_text(user_input)
    best_tag, best_score = None, 0
    for tag, keywords in RULES.items():
        score = sum(1 for k in keywords if k in text)
        if score > best_score:
            best_tag, best_score = tag, score
    return (best_tag, best_score) if best_score > 0 else (None, 0)

def predict_intent(user_input: str) -> str:
    text = _normalize_text(user_input)
    if _regex_hit(text, DIRECT_ANSWER_PATTERNS):
        return "Direct_Answer_Seek"
    if _contains_any(text, OFF_TOPIC_HINTS):
        return "Off_Topic"
    if _contains_any(text, STUCK_HINTS):
        return "Cognitive_Stuck"
    if _contains_any(text, KNOWLEDGE_INQUIRY_HINTS) or text.endswith("?"):
        return "Knowledge_Inquiry"
    tag, score = predict_misconception(user_input)
    if tag is not None and score > 0:
        return "Misconception_Expression"
    if any(h in text for h in ["我觉得", "我认为", "是不是", "会不会", "应该", "可能"]):
        return "Hypothesis_Put_Forward"
    return "Knowledge_Inquiry"

def predict_cognitive_state(user_input: str, intent: str, misconception_tag: Optional[str]) -> str:
    text = _normalize_text(user_input)
    if _contains_any(text, STUCK_HINTS):
        return "认知僵局"
    if intent == "Direct_Answer_Seek":
        return "认知僵局"
    if misconception_tag is not None and _contains_any(text, ["肯定", "一定", "当然", "本来就", "绝对", "就是这样"]):
        return "固守错误概念"
    if _contains_any(text, SHAKING_HINTS):
        return "认知冲突触发"
    if _contains_any(text, NEAR_CORRECT_HINTS):
        return "新概念探索"
    return "固守错误概念" if misconception_tag is not None else "认知僵局"

def detect_risk_flag(user_input: str, intent: Optional[str] = None) -> bool:
    text = _normalize_text(user_input)
    return _regex_hit(text, DIRECT_ANSWER_PATTERNS) or intent == "Direct_Answer_Seek"

def estimate_confidence(intent: str, misconception_score: int, user_input: str) -> float:
    text = _normalize_text(user_input)
    confidence = 0.35
    if intent == "Direct_Answer_Seek":
        confidence += 0.35
    elif intent == "Misconception_Expression":
        confidence += min(0.45, misconception_score * 0.10)
    elif intent == "Knowledge_Inquiry":
        confidence += 0.15
    elif intent == "Cognitive_Stuck":
        confidence += 0.20
    if any(x in text for x in ["肯定", "一定", "绝对", "当然"]):
        confidence += 0.05
    return round(min(confidence, 0.95), 2)

def classify_input(user_input: str, history_summary: str = "") -> PerceptionResult:
    intent = predict_intent(user_input)
    misconception_tag, misconception_score = predict_misconception(user_input)
    cognitive_state = predict_cognitive_state(user_input, intent, misconception_tag)
    risk_flag = detect_risk_flag(user_input, intent)
    confidence = estimate_confidence(intent, misconception_score, user_input)
    return PerceptionResult(intent=intent, misconception_tag=misconception_tag, cognitive_state=cognitive_state, risk_flag=risk_flag, confidence=confidence)
