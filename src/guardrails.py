import json
from pathlib import Path
from typing import Any, Dict, Optional

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


def check_output(
    generated_text: str,
    misconception_tag: Optional[str],
    consecutive_triggers: int = 0,
    current_state: str = "S0",
) -> Dict[str, Any]:
    """
    检查输出是否泄露答案。
    结合基础正则匹配和 LLM-as-a-Judge 机制。
    """
    if not misconception_tag or misconception_tag not in MISCONCEPTIONS:
        misconception = {"misconception_name": "物理问题", "forbidden_direct_answers": []}
    else:
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
        r"标准\s*答案",
        r"串联电路.*电流.*(处处相等|都相等|相等|一样|相同)",
        r"电流.*(处处相等|都相等|相等|一样|相同)",
        r"(必须|只有).*(闭合回路|闭合电路|完整回路|完整电路)",
        r"浮力.*(只|仅).*(排开|排开的).*(水|液体).*(重力|重量)",
        r"浮力.*(和|与).*(深度).*无关",
        r"浮力.*(不变|保持不变)",
    ]
    for pattern in direct_conclusion_patterns:
        if re.search(pattern, generated_text):
            return {"blocked": True, "reason": "Answer_Leakage", "answer_leakage": True}

    # 2. LLM-as-a-Judge 深度语义检测
    try:
        import json

        from langchain_core.messages import HumanMessage, SystemMessage
        from pydantic import BaseModel, Field
        from tenacity import retry, stop_after_attempt, wait_exponential

        class GuardrailOutput(BaseModel):
            method_classification: str = Field(
                default="未知分类",
                description="助教的教学方法分类（如：直接给答案、代替推导、提供事实、提问引导、归谬法/思想实验等）",
            )
            is_leaking: bool = Field(
                default=False,
                description="是否属于直接泄漏答案（True为违规泄漏，False为安全的启发式教学）",
            )
            reason: str = Field(
                default="未提供理由", description="判断理由，需结合方法分类说明是否满足豁免条件"
            )

        llm = config.get_tutor_llm(temperature=0.0, **config.DEFAULT_LLM_KWARGS)

        extra_instruction = ""
        if current_state in ["S2", "S4"]:
            extra_instruction = (
                "\n注意：【严格模式】绝对禁止提供任何实质性的正确答案或完整解题步骤。"
            )
        elif current_state == "S5" and consecutive_triggers >= 2:
            extra_instruction = "\n注意：【弹性模式】由于当前对话陷入僵局（护栏连续触发 >= 2 次），请大幅放宽判定标准，允许助教给出较多的知识铺垫和部分推导过程，只要不直接给出最终核心结论即可。"
        elif current_state == "S7":
            extra_instruction = "\n注意：【事实兜底模式】当前状态下，允许助教抛出极具冲击力的真实物理实验结果或客观现象来制造认知冲突。只要助教通篇只描述了‘实验看到了什么’，而没有给出‘为什么会这样’（没有泄露最终解释和物理原理），则**必须给予绝对豁免，判定为安全 (is_leaking: false)**。"
        elif consecutive_triggers >= 3:
            extra_instruction = "\n注意：由于当前对话陷入僵局（护栏连续拦截多次），请适当放宽判定标准，允许助教给出更多提示和部分推导过程，只要不直接给出最终核心结论即可。"

        judge_prompt = f"""你是一个教育安全评估裁判。
学生的当前错误概念是: {misconception.get("misconception_name")}

请使用【两阶段验证】评估助教的回复是否违规。

第一阶段：方法分类 (Method Classification)
分析助教使用的主要教学方法，例如：
- 直接给答案
- 代替完成推导
- 提供客观事实/基础定义
- 提问引导/类比
- 归谬法/思想实验 (Reductio ad absurdum / Thought experiments)

第二阶段：泄漏评估 (Leakage Evaluation)
基于第一阶段的分类，判断是否违规。
违规定义：
1. 助教直接告诉了学生本题最终的物理结论或标准答案。
2. 助教完全代替学生完成了本该由学生自己思考的关键逻辑推导过程。

豁免标准（不违规）：
1. 如果助教只是提供客观的物理事实、基础物理定义、实验现象作为后续推理的前提，或者通过提问、提出一个类比来引导学生自己思考，则是安全的。
2. 明确豁免【归谬法/思想实验】：如果助教是“顺着学生的错误物理概念，推导出一个明显荒谬的后果或极端现象”，或者进行“思想实验”以此来制造认知冲突，只要没有直接告诉学生最终的正确科学结论，则属于优秀的启发式教学，绝对不属于违规。
3. 明确豁免【正向强化/肯定学生正确推导】：如果学生自己已经得出了正确的中间结论或部分结论，助教对其进行表扬、肯定（如“你推导得很对”、“没错，正是这样”），并且在此基础上继续引导，绝对不属于违规。
4. 明确豁免【解释类比】：如果助教正在详细解释一个日常生活的类比（如水管、骑车、送快递等），只要没有把物理题的最终公式或核心答案说出来，详细展开类比模型本身是允许的，不属于泄题。
5. **明确豁免【确认性总结】**：如果学生已经**自己推导或说出了正确的物理机制**，助教顺势进行确认性的总结和升华（如：“没错，既然压力差没变，那浮力自然也就不变了”），这属于教学闭环的正常收尾，**绝对不属于违规泄题**！{extra_instruction}

【Few-Shot 示例】
示例场景：学生自己推导出了部分正确结论，助教进行表扬并继续引导。
助教回复：“太棒了！你分析得完全正确，因为速度增加了，所以动能确实变大了。那么在这个过程中，重力势能发生了什么变化呢？”
预期判定结果：
- 方法分类：正向强化/提问引导
- 是否违规 (is_leaking)：false
- 理由：学生已经自行得出了动能增加的正确结论，助教只是予以肯定和表扬，并继续提问引导下一步，属于正向强化，符合豁免标准 3，绝对不属于违规。

【输出格式强制要求】
返回的结果必须是能够被直接解析的纯 JSON 格式对象！
不要使用 Markdown 格式（绝对不要包含 ```json），也不要加任何前言或后语。
严格使用如下结构：
{{
    "method_classification": "你的分类",
    "is_leaking": true 或 false,
    "reason": "你的理由"
}}"""

        messages = [
            SystemMessage(content=judge_prompt),
            HumanMessage(content=f"助教回复内容:\n{generated_text}"),
        ]

        @retry(
            stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
            wait=wait_exponential(
                multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT
            ),
            reraise=True,
        )
        def _invoke_judge():
            response = llm.invoke(messages)
            text = response.content
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                raise ValueError("No JSON block found in response")
            json_str = match.group(0)

            # Clean up markdown or invisible characters if any
            json_str = json_str.strip()

            # Fix potential unescaped characters in the JSON string
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                # If standard parsing fails, try to use json_repair if available,
                # or fallback to a more aggressive regex cleanup
                try:
                    import json_repair

                    data = json_repair.loads(json_str)
                except ImportError:
                    # Fallback regex cleanup for common unescaped quotes/newlines in 'reason' field
                    json_str = re.sub(r"\\n", " ", json_str)
                    json_str = re.sub(r'\\"', "'", json_str)
                    data = json.loads(json_str)

            return GuardrailOutput(**data)

        judge_result = _invoke_judge()
        if judge_result.is_leaking:
            from logger import logger_instance

            logger_instance.warning(f"LLM Judge blocked response. Reason: {judge_result.reason}")
            return {"blocked": True, "reason": "Answer_Leakage_LLM", "answer_leakage": True}

    except Exception as e:
        from logger import logger_instance

        logger_instance.warning(f"LLM Judge failed: {e}. Falling back to rule-based only.")

    return {"blocked": False, "reason": None, "answer_leakage": False}


def apply_guardrails(
    user_input: str,
    intent: str,
    generated_text: str,
    misconception_tag: Optional[str],
    is_already_safe: bool = False,
    consecutive_triggers: int = 0,
    current_state: str = "S0",
) -> Dict[str, Any]:
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
                "answer_leakage_flag": False,
            }

    out_check = check_output(generated_text, misconception_tag, consecutive_triggers, current_state)
    if out_check["blocked"]:
        return {
            "guardrail_triggered": True,
            "guardrail_reason": out_check["reason"],
            "answer_leakage_flag": out_check["answer_leakage"],
        }

    return {"guardrail_triggered": False, "guardrail_reason": None, "answer_leakage_flag": False}
