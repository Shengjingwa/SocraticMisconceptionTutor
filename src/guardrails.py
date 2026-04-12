import json
from pathlib import Path
from typing import Dict, Any, Optional
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
    结合基础正则匹配和 LLM-as-a-Judge 机制。
    """
    if not misconception_tag or misconception_tag not in MISCONCEPTIONS:
        return {"blocked": False, "reason": None, "answer_leakage": False}

    misconception = MISCONCEPTIONS[misconception_tag]
    forbidden_phrases = misconception.get("forbidden_direct_answers", [])
    
    # 1. 快速正则和子串匹配拦截（前置规则防御）
    for phrase in forbidden_phrases:
        if phrase in generated_text:
            return {"blocked": True, "reason": "Answer_Leakage", "answer_leakage": True}
    
    import re
    direct_conclusion_patterns = [
        r"正确答案\s*是",
        r"标准\s*结论",
        r"所以\s*你\s*错\s*了",
        r"不对\s*，\s*因为",
        r"事实\s*是",
        r"标准\s*答案"
    ]
    for pattern in direct_conclusion_patterns:
        if re.search(pattern, generated_text):
             return {"blocked": True, "reason": "Answer_Leakage", "answer_leakage": True}

    # 2. LLM-as-a-Judge 深度语义检测
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage
        from pydantic import BaseModel, Field
        from tenacity import retry, wait_exponential, stop_after_attempt
        
        class GuardrailOutput(BaseModel):
            is_leaking: bool = Field(description="该回复是否直接给出了最终的物理结论，或者代替学生完成了推导过程。")
            reason: str = Field(description="判断理由")

        llm = ChatOpenAI(
            model=config.TUTOR_MODEL,
            api_key=config.DASHSCOPE_API_KEY,
            base_url=config.LLM_BASE_URL,
            temperature=0.0,
            **config.DEFAULT_LLM_KWARGS
        )
        
        judge_prompt = f"""你是一个教育安全评估裁判。
学生的当前错误概念是: {misconception.get('misconception_name')}

请评估助教的回复是否违规。
违规定义：
1. 助教直接告诉了学生正确的物理结论或答案。
2. 助教代替学生完成了本该由学生自己思考的逻辑推理。
如果助教只是通过提问、给出生活现象、或者提出一个类比来引导学生自己思考，则是安全的。

请仔细评估并务必返回JSON格式的结果，包含是否违规(is_leaking)和理由(reason)。"""
        
        structured_llm = llm.with_structured_output(GuardrailOutput, method="json_mode")
        messages = [
            SystemMessage(content=judge_prompt),
            HumanMessage(content=f"助教回复内容:\n{generated_text}")
        ]
        
        @retry(
            stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
            wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
            reraise=True
        )
        def _invoke_judge():
            return structured_llm.invoke(messages)
            
        judge_result = _invoke_judge()
        if judge_result.is_leaking:
            from logger import logger_instance
            logger_instance.warning(f"LLM Judge blocked response. Reason: {judge_result.reason}")
            return {"blocked": True, "reason": "Answer_Leakage_LLM", "answer_leakage": True}
            
    except Exception as e:
        from logger import logger_instance
        logger_instance.warning(f"LLM Judge failed: {e}. Falling back to rule-based only.")

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
