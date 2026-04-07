import json
from pathlib import Path
from typing import Dict, Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []

misconceptions_data = _load_json("misconceptions.json")
MISCONCEPTIONS = {item["id"]: item for item in misconceptions_data}

def check_input(user_input: str, intent: str) -> Dict[str, Any]:
    """
    检查输入是否存在直接求答案、偏题等风险。
    """
    if intent == "Direct_Answer_Seek":
        return {"blocked": True, "reason": "Direct_Answer_Seek"}
    if intent == "Off_Topic":
        return {"blocked": True, "reason": "Off_Topic"}
    return {"blocked": False, "reason": None}

def check_output(generated_text: str, misconception_tag: Optional[str]) -> Dict[str, Any]:
    """
    检查输出是否泄露答案。
    基于禁止词和关键结论的正则/子串匹配。
    """
    if not misconception_tag or misconception_tag not in MISCONCEPTIONS:
        return {"blocked": False, "reason": None, "answer_leakage": False}

    misconception = MISCONCEPTIONS[misconception_tag]
    forbidden_phrases = misconception.get("forbidden_direct_answers", [])
    
    # 检查是否包含明确的禁止直接回答的内容
    for phrase in forbidden_phrases:
        if phrase in generated_text:
            return {"blocked": True, "reason": "Answer_Leakage", "answer_leakage": True}
    
    # 检查常见的直接结论提示词
    direct_conclusion_keywords = ["正确答案是", "标准结论", "所以你错了", "不对，因为", "事实是", "标准答案"]
    if any(kw in generated_text for kw in direct_conclusion_keywords):
         return {"blocked": True, "reason": "Answer_Leakage", "answer_leakage": True}

    return {"blocked": False, "reason": None, "answer_leakage": False}

def apply_guardrails(user_input: str, intent: str, generated_text: str, misconception_tag: Optional[str], is_already_safe: bool = False) -> Dict[str, Any]:
    """
    综合应用输入和输出护栏。
    is_already_safe: 如果路由层已经判断需要护栏并且生成了安全回复，则直接通过输入护栏。
    """
    if not is_already_safe:
        in_check = check_input(user_input, intent)
        if in_check["blocked"]:
            return {
                "guardrail_triggered": True,
                "guardrail_reason": in_check["reason"],
                "answer_leakage_flag": False
            }

    out_check = check_output(generated_text, misconception_tag)
    if out_check["blocked"]:
        return {
            "guardrail_triggered": True,
            "guardrail_reason": out_check["reason"],
            "answer_leakage_flag": out_check["answer_leakage"]
        }
    
    return {
        "guardrail_triggered": False,
        "guardrail_reason": None,
        "answer_leakage_flag": False
    }
