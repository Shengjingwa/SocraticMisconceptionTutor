import re
from typing import List, Literal, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

import config
from router import PerceptionResult

MisconceptionTag = Literal["M-ELE-001", "M-ELE-002", "M-BUO-001", "M-BUO-002"]
VALID_MISCONCEPTION_TAGS = {"M-ELE-001", "M-ELE-002", "M-BUO-001", "M-BUO-002"}


def _normalize_misconception_tag(tag: Optional[str]) -> Optional[str]:
    if not tag:
        return None
    t = str(tag).strip().upper()
    t = re.sub(r"\s+", "", t)
    fixes = {
        "M-BUO-02": "M-BUO-002",
        "M-BUO-2": "M-BUO-002",
        "M-BUO-01": "M-BUO-001",
        "M-BUO-1": "M-BUO-001",
        "M-ELE-01": "M-ELE-001",
        "M-ELE-1": "M-ELE-001",
        "M-ELE-02": "M-ELE-002",
        "M-ELE-2": "M-ELE-002",
    }
    t = fixes.get(t, t)
    return t if t in VALID_MISCONCEPTION_TAGS else None


def _keyword_hit(text: str, keywords: List[str]) -> bool:
    if not text:
        return False
    return any(k in text for k in keywords if k)


def _heuristic_misconception_override(user_input: str, predicted: Optional[str]) -> Optional[str]:
    text = user_input.strip()
    ele002_kw = [
        "只接正极",
        "只接负极",
        "单线",
        "一根线",
        "不用回路",
        "不需要回路",
        "不闭合",
        "不用闭合",
        "回路没必要",
        "只要接",
        "电流不是已经出来",
    ]
    ele001_kw = [
        "电流变少",
        "电流会变少",
        "被消耗",
        "用掉",
        "吃掉",
        "前面的灯泡",
        "后面的灯泡",
        "后面更暗",
        "串联",
        "流入大于流出",
    ]
    if _keyword_hit(text, ele002_kw):
        return "M-ELE-002"
    if _keyword_hit(text, ele001_kw):
        return "M-ELE-001"
    return predicted


class NLUOutput(BaseModel):
    intent: Literal[
        "Direct_Answer_Seek",
        "Off_Topic",
        "Cognitive_Stuck",
        "Knowledge_Inquiry",
        "Misconception_Expression",
        "Hypothesis_Put_Forward",
    ] = Field(description="用户当前的意图")

    misconception_tag: Optional[MisconceptionTag] = Field(
        default=None,
        description="识别到的错误概念标签，只能从预设标签中选择；如果没有明确的错误概念则必须返回 null",
    )

    cognitive_state: str = Field(
        description="用户当前的认知状态，必须严格从以下选项中选择：'认知僵局', '固守错误概念', '认知冲突触发', '新概念探索', '概念掌握验证'"
    )

    transition_approved: bool = Field(
        description="用户是否满足了当前教学状态的退出条件，可以进入下一个教学环节"
    )
    reasoning: str = Field(description="判断是否允许状态转移的理由")

    sentiment: str = Field(
        description="用户当前的情感状态，必须严格从以下选项中选择：'焦虑/挫败', '困惑', '自信', '平静'"
    )

    confidence: float = Field(description="分类置信度，范围0.0到1.0")


class PostTestOutput(BaseModel):
    passed: bool = Field(description="学生是否已经用自己的话正确地解释了物理原理，且没有事实错误")
    reason: str = Field(description="判断理由")


def verify_post_test(user_input: str, misconception_tag: str, messages: list = None) -> bool:
    if not config.DASHSCOPE_API_KEY:
        return True

    if not misconception_tag:
        return False

    from generator import KNOWLEDGE_CHUNKS, MISCONCEPTIONS

    misconception = MISCONCEPTIONS.get(misconception_tag, {})
    knowledge = KNOWLEDGE_CHUNKS.get(misconception_tag, {})

    llm = config.get_tutor_llm(**config.DEFAULT_LLM_KWARGS)

    structured_llm = llm.with_structured_output(PostTestOutput, method="json_mode")

    core_points = "\n- ".join(knowledge.get("core_science_points", []))

    system_prompt = f"""你是一个物理老师，正在进行“教后测”评估。
请判断学生最新的回答是否已经用自己的话正确解释了相关物理原理，且没有事实错误。
当前主题相关的核心科学知识点是:
{core_points}
学生的初始错误观念是:
{misconception.get("misconception_name", "")}

要求:
1. 学生必须用自己的话进行解释或推理。
2. 如果学生只是简单说“我懂了”、“是的”、“对的”，没有给出具体解释，视为未通过 (passed: false)。
3. 如果学生的解释依然包含错误观念，视为未通过 (passed: false)。
4. 只有当学生的解释基本符合核心科学知识点，且逻辑自洽时，才视为通过 (passed: true)。

请返回 JSON 格式结果，包含 passed (布尔值) 和 reason (判断理由的字符串)。"""

    if messages is None:
        messages = []

    from langchain_core.messages import AIMessage

    formatted_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            formatted_messages.append({"role": "assistant", "content": msg.content})
        else:
            formatted_messages.append(msg)

    recent_text = "\n".join(
        [
            f"{'学生' if m['role'] == 'user' else '助教'}: {m['content']}"
            for m in formatted_messages[-4:]
        ]
    )

    @retry(
        stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        reraise=True,
    )
    def _invoke_eval():
        prompt_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"近期对话:\n{recent_text}\n\n请评估学生最新输入: {user_input}"),
        ]
        return structured_llm.invoke(prompt_messages)

    try:
        result = _invoke_eval()
        return result.passed
    except Exception as e:
        from logger import logger_instance

        logger_instance.error(f"Post-test evaluation failed: {e}")
        return False


def classify_input(
    user_input: str, messages: list = None, history_summary: str = "", current_state: str = "S0"
) -> PerceptionResult:
    if messages is None:
        messages = []

    # 将 AnyMessage 列表转换为适合 prompt 的文本形式
    from langchain_core.messages import AIMessage

    formatted_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            formatted_messages.append({"role": "assistant", "content": msg.content})
        else:
            formatted_messages.append(msg)
    messages = formatted_messages

    if not config.DASHSCOPE_API_KEY:
        # Mock mode if API key is missing
        return PerceptionResult(
            intent="Knowledge_Inquiry",
            misconception_tag="M-ELE-001",
            cognitive_state="认知僵局",
            sentiment="平静",
            risk_flag=False,
            confidence=0.8,
        )

    llm = config.get_tutor_llm(**config.DEFAULT_LLM_KWARGS)

    structured_llm = llm.with_structured_output(NLUOutput, method="json_mode")

    system_prompt = f"""你是一个专门用于物理辅导对话的自然语言理解(NLU)和教学状态评估(Assessor)模块。
你的任务是根据用户的输入和历史对话，提取出用户的意图、错误概念、认知状态、情感状态，并判断是否允许进入下一个教学环节(transition_approved)。

当前所在的教学状态是: {current_state}

各状态的允许转移(transition_approved=true)退出条件如下:
- S3 (Misconception_Diagnosis): 已经明确知道学生存在哪个具体的错误概念(Misconception)。
- S4 (Cognitive_Conflict): 学生开始对自己的原始错误想法产生怀疑，或者发现自己的想法导致了矛盾，表示“好像不对”。
- S5 (Scaffolding_Guidance): 学生在引导下，能够提出新的、向正确方向靠拢的假设或解释。
- S6 (Verification_Deepening): 学生能够用自己的话准确、完整地解释物理原理，没有事实错误。
- S7 (Fact_Grounding): 学生在事实兜底的强认知冲突下，开始动摇原有的错误框架，并尝试解释该现象。
- 其他状态(S0, S1, S2, S8): 默认设为 false。

你需要严格判断学生当前的回复是否满足了【{current_state}】状态的退出条件。如果满足，设置 transition_approved 为 true，并给出 reasoning；如果不满足，设为 false，并给出 reasoning。

可用的错误概念标签(Misconception)（只能从下面四个中选择，禁止输出其他任何字符串；如果无法判断必须输出 null）:
- M-ELE-001: 认为电流在电路中会被消耗(如灯泡用掉电流)
- M-ELE-002: 认为电路不需要闭合回路，单线即可工作
- M-BUO-001: 认为物体越重越容易沉，越轻越容易浮
- M-BUO-002: 认为水压越大浮力越大，浮力随深度增加

意图(Intent)包括:
- Direct_Answer_Seek: 直接要答案
- Off_Topic: 偏离物理辅导主题
- Cognitive_Stuck: 表示不知道、不懂，或者仅表达同意而无实质内容
- Knowledge_Inquiry: 询问具体的知识点
- Misconception_Expression: 明确表达了错误的物理想法
- Hypothesis_Put_Forward: 提出了一个猜测或假设（无论对错）

认知状态(Cognitive State)包括:
- 认知僵局: 卡壳，不知道怎么做，或者只是含糊地说“我懂了”但没有给出具体解释
- 固守错误概念: 依然坚持最初的错误物理想法
- 认知冲突触发: 开始怀疑自己的错误想法，发现矛盾，或表现出极大的不确定性
- 新概念探索: 开始尝试用正确的视角思考，尽管可能还不完整
- 概念掌握验证: 已经完全理解，并且**必须**用自己的话给出了正确的物理机制解释或推理！如果只有同意而无解释，请选“认知僵局”。

### 判定逻辑增强 ###
1. **化繁为简**：如果学生回复“我明白了”或“对”，但没有任何推理过程，意图直接归为 `Cognitive_Stuck`，认知状态归为“认知僵局”，且 `transition_approved` 必须为 false。不要过度解读学生的顺从。
2. **优先识别错误概念**：如果回复中包含任何与预设错误标签吻合的内容，优先标记该标签并设为 `Misconception_Expression`。
3. **识别认知动摇**：如果学生说“难道是因为...吗？”或者“如果那样的话，岂不是...”，这通常意味着“认知冲突触发”，应标记为 transition_approved: true。

情感状态(Sentiment)包括:
- 焦虑/挫败: 表现出烦躁、气馁或想要放弃
- 困惑: 表现出不解、迷茫或犹豫
- 自信: 表现出确定、肯定或得意
- 平静: 情绪平稳，无明显波动

### Few-Shot 示例 ###
【示例1】
历史对话: 无
当前用户输入: "灯泡亮了是因为它把电流吃掉了吗？"
输出: {{"intent": "Misconception_Expression", "misconception_tag": "M-ELE-001", "cognitive_state": "固守错误概念", "transition_approved": true, "reasoning": "学生表达了具体的错误观念，S3的退出条件已满足", "sentiment": "平静", "confidence": 0.95}}

【示例2】
历史对话: 助教: 那你觉得如果水压越大浮力越大，为什么深海里的石头不会浮上来呢？
当前用户输入: "呃……好像也是哦，那到底是怎么回事啊？我不知道了。"
输出: {{"intent": "Cognitive_Stuck", "misconception_tag": "M-BUO-002", "cognitive_state": "认知冲突触发", "transition_approved": true, "reasoning": "学生已经开始怀疑自己水压大浮力大的想法(S4条件满足)", "sentiment": "困惑", "confidence": 0.90}}

【示例3】
历史对话: 助教: 回想一下我们刚刚讨论的阿基米德原理，排开的水的体积决定了什么？
当前用户输入: "嗯，所以浮力只和排开的水的体积有关，和深度没有关系，对吧？"
输出: {{"intent": "Hypothesis_Put_Forward", "misconception_tag": "M-BUO-002", "cognitive_state": "新概念探索", "transition_approved": true, "reasoning": "学生提出了向正确方向靠拢的新解释(S5条件满足)", "sentiment": "平静", "confidence": 0.85}}

【示例4】
历史对话: 助教: 你能总结一下串联电路里各处的电流大小吗？
当前用户输入: "我懂了，串联电路里处处电流都相等！"
输出: {{"intent": "Knowledge_Inquiry", "misconception_tag": "M-ELE-001", "cognitive_state": "概念掌握验证", "transition_approved": true, "reasoning": "学生用自己的话准确解释了原理(S6条件满足)", "sentiment": "自信", "confidence": 0.95}}

【示例5】
历史对话: 助教: 你觉得水管里的水流过水车后，水变少了吗？
当前用户输入: "哦，原来是这样，我懂了！"
输出: {{"intent": "Cognitive_Stuck", "misconception_tag": "M-ELE-001", "cognitive_state": "认知僵局", "transition_approved": false, "reasoning": "学生只说懂了但没有给出具体解释，不满足状态退出条件", "sentiment": "平静", "confidence": 0.85}}

【示例6】
历史对话: 助教: 再仔细想想，如果电流被消耗了，后面的灯泡应该怎样？
当前用户输入: "哎呀我不知道！你直接告诉我答案行不行啊，太难了！"
输出: {{"intent": "Direct_Answer_Seek", "misconception_tag": "M-ELE-001", "cognitive_state": "认知僵局", "transition_approved": false, "reasoning": "学生处于挫败状态，要求直接给答案，不满足认知冲突的推进条件", "sentiment": "焦虑/挫败", "confidence": 0.95}}

请分析用户的输入，并务必返回JSON格式的结果。"""

    # Format history
    history_text = ""
    if len(messages) > config.MAX_HISTORY_TURNS and history_summary:
        history_text += f"【早期对话总结】\n{history_summary}\n\n【近期对话】\n"

    recent_text = "\n".join(
        [
            f"{'学生' if m['role'] == 'user' else '助教'}: {m['content']}"
            for m in messages[-config.MAX_HISTORY_TURNS :]
        ]
    )
    if not recent_text:
        recent_text = "无"

    history_text += recent_text

    @retry(
        stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        reraise=True,
    )
    def _invoke_chain():
        prompt_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"历史对话:\n{history_text}\n\n当前用户输入: {user_input}"),
        ]
        return structured_llm.invoke(prompt_messages)

    try:
        result = _invoke_chain()
    except Exception as e:
        from logger import logger_instance

        logger_instance.warning(f"Structured NLU parsing failed, falling back to raw parsing: {e}")
        try:
            import json
            import re

            prompt_messages = [
                SystemMessage(
                    content=system_prompt + "\n请只输出JSON格式的结果，不要包含其他任何字符。"
                ),
                HumanMessage(content=f"历史对话:\n{history_text}\n\n当前用户输入: {user_input}"),
            ]
            raw_response = llm.invoke(prompt_messages)
            raw_text = raw_response.content.strip()

            # Use regex to find JSON block
            json_match = re.search(r"\{[\s\S]*\}", raw_text)
            if json_match:
                raw_text = json_match.group(0)

            data = json.loads(raw_text)

            raw_tag = _normalize_misconception_tag(data.get("misconception_tag"))
            raw_tag = _heuristic_misconception_override(user_input, raw_tag)

            return PerceptionResult(
                intent=data.get("intent") or "Knowledge_Inquiry",
                misconception_tag=raw_tag,
                cognitive_state=data.get("cognitive_state") or "认知僵局",
                sentiment=data.get("sentiment") or "平静",
                risk_flag=data.get("intent") == "Direct_Answer_Seek",
                confidence=float(data.get("confidence") or 0.0),
                transition_approved=bool(data.get("transition_approved") or False),
                reasoning=data.get("reasoning") or "",
            )
        except Exception as fallback_e:
            logger_instance.error(f"Fallback NLU parsing failed: {fallback_e}")
            return PerceptionResult(
                intent="Knowledge_Inquiry",
                misconception_tag=None,
                cognitive_state="认知僵局",
                sentiment="平静",
                risk_flag=False,
                confidence=0.0,
                transition_approved=False,
                reasoning="Fallback NLU Error",
            )

    # Calculate risk_flag based on intent
    risk_flag = result.intent in ["Direct_Answer_Seek", "Off_Topic"]

    normalized_tag = _normalize_misconception_tag(result.misconception_tag)
    normalized_tag = _heuristic_misconception_override(user_input, normalized_tag)

    return PerceptionResult(
        intent=result.intent,
        misconception_tag=normalized_tag,
        cognitive_state=result.cognitive_state,
        sentiment=result.sentiment,
        risk_flag=risk_flag,
        confidence=result.confidence,
        transition_approved=result.transition_approved,
        reasoning=result.reasoning,
    )
