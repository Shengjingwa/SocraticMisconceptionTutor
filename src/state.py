from typing import Annotated, Any, Dict, NotRequired, Optional, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from router import PerceptionResult, RouteDecision, SessionMemory


class GraphState(TypedDict):
    """
    LangGraph 状态管理，包含会话的长期记忆及当前对话轮次的各个中间状态。
    """

    system_version: str

    # 长期会话状态
    memory: SessionMemory
    messages: Annotated[list[AnyMessage], add_messages]

    # 当前轮次输入
    user_input: str

    # 当前轮次处理结果
    perception: NotRequired[Optional[PerceptionResult]]
    decision: NotRequired[Optional[RouteDecision]]
    generation: NotRequired[Optional[Dict[str, Any]]]
    guardrail_result: NotRequired[Optional[Dict[str, Any]]]
    regeneration_required: NotRequired[bool]
