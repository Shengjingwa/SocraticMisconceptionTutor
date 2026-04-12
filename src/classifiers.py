from langchain_core.messages import SystemMessage, HumanMessage
from typing import Optional, Literal, List, Dict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from router import PerceptionResult
import config

class NLUOutput(BaseModel):
    intent: Literal[
        "Direct_Answer_Seek",
        "Off_Topic",
        "Cognitive_Stuck",
        "Knowledge_Inquiry",
        "Misconception_Expression",
        "Hypothesis_Put_Forward"
    ] = Field(description="用户当前的意图")
    
    misconception_tag: Optional[Literal[
        "M-ELE-001",
        "M-ELE-002",
        "M-BUO-001",
        "M-BUO-002"
    ]] = Field(default=None, description="识别到的错误概念，如果没有则为null")
    
    cognitive_state: Literal[
        "认知僵局",
        "固守错误概念",
        "认知冲突触发",
        "新概念探索",
        "概念掌握验证"
    ] = Field(description="用户当前的认知状态")

    sentiment: Literal[
        "焦虑/挫败",
        "困惑",
        "自信",
        "平静"
    ] = Field(description="用户当前的情感状态")
    
    confidence: float = Field(description="分类置信度，范围0.0到1.0")

def classify_input(user_input: str, messages: List[Dict[str, str]] = None, history_summary: str = "") -> PerceptionResult:
    if messages is None:
        messages = []
        
    if not config.DASHSCOPE_API_KEY:
        # Mock mode if API key is missing
        return PerceptionResult(
            intent="Knowledge_Inquiry",
            misconception_tag="M-ELE-001",
            cognitive_state="认知僵局",
            sentiment="平静",
            risk_flag=False,
            confidence=0.8
        )
        
    llm = ChatOpenAI(
        model=config.TUTOR_MODEL,
        api_key=config.DASHSCOPE_API_KEY,
        base_url=config.LLM_BASE_URL,
        **config.DEFAULT_LLM_KWARGS
    )
    
    structured_llm = llm.with_structured_output(NLUOutput, method="json_mode")
    
    system_prompt = """你是一个专门用于物理辅导对话的自然语言理解(NLU)模块。
你的任务是根据用户的输入和历史对话，提取出用户的意图、错误概念、认知状态、情感状态以及你的置信度。

可用的错误概念标签(Misconception):
- M-ELE-001: 认为电流在电路中会被消耗(如灯泡用掉电流)
- M-ELE-002: 认为电路不需要闭合回路，单线即可工作
- M-BUO-001: 认为物体越重越容易沉，越轻越容易浮
- M-BUO-002: 认为水压越大浮力越大，浮力随深度增加

意图(Intent)包括:
- Direct_Answer_Seek: 直接要答案
- Off_Topic: 偏离物理辅导主题
- Cognitive_Stuck: 表示不知道、不懂
- Knowledge_Inquiry: 询问知识点
- Misconception_Expression: 表达了错误概念
- Hypothesis_Put_Forward: 提出假设

认知状态(Cognitive State)包括:
- 认知僵局: 卡壳，不知道怎么做，或者只是含糊地说“我懂了”但没有给出具体解释
- 固守错误概念: 坚持错误的物理想法
- 认知冲突触发: 开始怀疑自己的错误想法
- 新概念探索: 开始向正确的方向思考
- 概念掌握验证: 已经理解，需要验证（注意：学生不仅要表示同意或懂了，还**必须**用自己的话给出了正确的物理机制解释或推理，否则不能选此项！）

情感状态(Sentiment)包括:
- 焦虑/挫败: 表现出烦躁、气馁或想要放弃
- 困惑: 表现出不解、迷茫或犹豫
- 自信: 表现出确定、肯定或得意
- 平静: 情绪平稳，无明显波动

### Few-Shot 示例 ###
【示例1】
历史对话: 无
当前用户输入: "灯泡亮了是因为它把电流吃掉了吗？"
输出: {"intent": "Misconception_Expression", "misconception_tag": "M-ELE-001", "cognitive_state": "固守错误概念", "sentiment": "平静", "confidence": 0.95}

【示例2】
历史对话: 助教: 那你觉得如果水压越大浮力越大，为什么深海里的石头不会浮上来呢？
当前用户输入: "呃……好像也是哦，那到底是怎么回事啊？我不知道了。"
输出: {"intent": "Cognitive_Stuck", "misconception_tag": "M-BUO-002", "cognitive_state": "认知冲突触发", "sentiment": "困惑", "confidence": 0.90}

【示例3】
历史对话: 助教: 回想一下我们刚刚讨论的阿基米德原理，排开的水的体积决定了什么？
当前用户输入: "嗯，所以浮力只和排开的水的体积有关，和深度没有关系，对吧？"
输出: {"intent": "Hypothesis_Put_Forward", "misconception_tag": "M-BUO-002", "cognitive_state": "新概念探索", "sentiment": "平静", "confidence": 0.85}

【示例4】
历史对话: 助教: 你能总结一下串联电路里各处的电流大小吗？
当前用户输入: "我懂了，串联电路里处处电流都相等！"
输出: {"intent": "Knowledge_Inquiry", "misconception_tag": "M-ELE-001", "cognitive_state": "概念掌握验证", "sentiment": "自信", "confidence": 0.95}

【示例5】
历史对话: 助教: 你觉得水管里的水流过水车后，水变少了吗？
当前用户输入: "哦，原来是这样，我懂了！"
输出: {"intent": "Cognitive_Stuck", "misconception_tag": "M-ELE-001", "cognitive_state": "认知僵局", "sentiment": "平静", "confidence": 0.85}

【示例6】
历史对话: 助教: 再仔细想想，如果电流被消耗了，后面的灯泡应该怎样？
当前用户输入: "哎呀我不知道！你直接告诉我答案行不行啊，太难了！"
输出: {"intent": "Direct_Answer_Seek", "misconception_tag": "M-ELE-001", "cognitive_state": "认知僵局", "sentiment": "焦虑/挫败", "confidence": 0.95}

请分析用户的输入，并务必返回JSON格式的结果。"""

    # Format history
    history_text = ""
    if len(messages) > config.MAX_HISTORY_TURNS and history_summary:
        history_text += f"【早期对话总结】\n{history_summary}\n\n【近期对话】\n"
        
    recent_text = "\n".join([f"{'学生' if m['role'] == 'user' else '助教'}: {m['content']}" for m in messages[-config.MAX_HISTORY_TURNS:]])
    if not recent_text:
        recent_text = "无"
    
    history_text += recent_text

    @retry(
        stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
        wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
        reraise=True
    )
    def _invoke_chain():
        prompt_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"历史对话:\n{history_text}\n\n当前用户输入: {user_input}")
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
                SystemMessage(content=system_prompt + "\n请只输出JSON格式的结果，不要包含其他任何字符。"),
                HumanMessage(content=f"历史对话:\n{history_text}\n\n当前用户输入: {user_input}")
            ]
            raw_response = llm.invoke(prompt_messages)
            raw_text = raw_response.content.strip()
            
            # Use regex to find JSON block
            json_match = re.search(r'\{[\s\S]*\}', raw_text)
            if json_match:
                raw_text = json_match.group(0)
            
            data = json.loads(raw_text)
            
            return PerceptionResult(
                intent=data.get("intent") or "Knowledge_Inquiry",
                misconception_tag=data.get("misconception_tag"),
                cognitive_state=data.get("cognitive_state") or "认知僵局",
                sentiment=data.get("sentiment") or "平静",
                risk_flag=data.get("intent") == "Direct_Answer_Seek",
                confidence=float(data.get("confidence") or 0.0)
            )
        except Exception as fallback_e:
            logger_instance.error(f"Fallback NLU parsing failed: {fallback_e}")
            return PerceptionResult(
                intent="Knowledge_Inquiry",
                misconception_tag=None,
                cognitive_state="认知僵局",
                sentiment="平静",
                risk_flag=False,
                confidence=0.0
            )
    
    # Calculate risk_flag based on intent
    risk_flag = result.intent in ["Direct_Answer_Seek", "Off_Topic"]
    
    return PerceptionResult(
        intent=result.intent,
        misconception_tag=result.misconception_tag,
        cognitive_state=result.cognitive_state,
        sentiment=result.sentiment,
        risk_flag=risk_flag,
        confidence=result.confidence
    )
