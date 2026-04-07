from typing import TypedDict, Dict, Any, Optional, NotRequired
from router import SessionMemory, PerceptionResult, RouteDecision

class GraphState(TypedDict):
    """
    LangGraph 状态管理，包含会话的长期记忆及当前对话轮次的各个中间状态。
    """
    # 系统版本，用于消融实验（Baseline / FSM / FSM+Guardrail）
    system_version: NotRequired[str]
    
    # 长期会话状态
    memory: SessionMemory
    
    # 当前轮次输入
    user_input: str
    
    # 当前轮次处理结果
    perception: NotRequired[Optional[PerceptionResult]]
    decision: NotRequired[Optional[RouteDecision]]
    generation: NotRequired[Optional[Dict[str, Any]]]
    guardrail_result: NotRequired[Optional[Dict[str, Any]]]
    regeneration_required: NotRequired[bool]
