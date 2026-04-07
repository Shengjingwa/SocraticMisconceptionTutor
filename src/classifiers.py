import os
from typing import Optional, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from router import PerceptionResult

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
    
    confidence: float = Field(description="分类置信度，范围0.0到1.0")

def classify_input(user_input: str, history_summary: str = "") -> PerceptionResult:
    api_key = os.getenv("DEEPSEEK_API_KEY", "dummy_key")
    if not api_key or api_key == "dummy_key":
        return PerceptionResult(
            intent="Misconception_Expression",
            misconception_tag="M-ELE-001",
            cognitive_state="固守错误概念",
            risk_flag=False,
            confidence=1.0
        )

    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    
    structured_llm = llm.with_structured_output(NLUOutput)
    
    system_prompt = """你是一个专门用于物理辅导对话的自然语言理解(NLU)模块。
你的任务是根据用户的输入和历史对话摘要，提取出用户的意图、错误概念、认知状态以及你的置信度。

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
- 认知僵局: 卡壳，不知道怎么做
- 固守错误概念: 坚持错误的物理想法
- 认知冲突触发: 开始怀疑自己的错误想法
- 新概念探索: 开始向正确的方向思考
- 概念掌握验证: 已经理解，需要验证

请分析用户的输入，并输出对应的字段。"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "历史对话摘要: {history_summary}\n用户输入: {user_input}")
    ])
    
    chain = prompt | structured_llm
    
    try:
        result = chain.invoke({
            "history_summary": history_summary,
            "user_input": user_input
        })
    except Exception as e:
        # Fallback in case of API failure
        return PerceptionResult(
            intent="Knowledge_Inquiry",
            misconception_tag=None,
            cognitive_state="认知僵局",
            risk_flag=False,
            confidence=0.0
        )
    
    # Calculate risk_flag based on intent
    risk_flag = result.intent == "Direct_Answer_Seek"
    
    return PerceptionResult(
        intent=result.intent,
        misconception_tag=result.misconception_tag,
        cognitive_state=result.cognitive_state,
        risk_flag=risk_flag,
        confidence=result.confidence
    )
