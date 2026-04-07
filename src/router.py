
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class PerceptionResult:
    intent: str
    misconception_tag: Optional[str] = None
    cognitive_state: str = "认知僵局"
    risk_flag: bool = False
    confidence: float = 0.0

@dataclass
class SessionMemory:
    session_id: str
    topic: Optional[str] = None
    current_state: str = "S0"
    current_misconception: Optional[str] = None
    turn_count: int = 0
    history_summary: str = ""
    messages: List[Dict[str, str]] = field(default_factory=list)
    used_strategies: List[str] = field(default_factory=list)
    recent_states: List[str] = field(default_factory=list)
    risk_events: List[str] = field(default_factory=list)
    resolved: bool = False

@dataclass
class RouteDecision:
    state: str
    state_name: str
    strategy: Optional[str]
    need_guardrail: bool
    next_goal: str
    meta: Dict[str, Any] = field(default_factory=dict)

STATE_NAMES = {
    "S0": "Listen_And_Analyze",
    "S1": "Guardrail_Check",
    "S2": "Refusal_And_Guidance",
    "S3": "Misconception_Diagnosis",
    "S4": "Cognitive_Conflict",
    "S5": "Scaffolding_Guidance",
    "S6": "Verification_Deepening",
}
MISCONCEPTION_TO_TOPIC = {
    "M-ELE-001": "电学",
    "M-ELE-002": "电学",
    "M-BUO-001": "浮力",
    "M-BUO-002": "浮力",
}
STATE_STRATEGIES = {
    "S2": [None],
    "S3": [None],
    "S4": ["Assumption_Probing", "Consequence_Exploration"],
    "S5": ["Clarification", "Evidence_Seeking", "Analogical_Scaffolding"],
    "S6": ["Evidence_Seeking", "Consequence_Exploration"],
}
STRATEGY_GOALS = {
    None: "引导学生进一步明确自己的想法或提供更多细节。",
    "S2_None": "拒绝直接代答，并将对话重定向回引导式学习路径。",
    "Clarification": "澄清学生表述中的模糊概念，找准真正的认知问题。",
    "Assumption_Probing": "暴露学生结论背后的隐含前提，制造认知冲突。",
    "Evidence_Seeking": "引导学生用现象、实验或理由支持自己的判断。",
    "Consequence_Exploration": "把学生当前解释继续推演，检验其后果是否合理。",
    "Analogical_Scaffolding": "用有边界的类比支架帮助学生跨过理解障碍。",
}

def _choose_strategy(state: str, memory: SessionMemory) -> Optional[str]:
    candidates = STATE_STRATEGIES.get(state, [None])
    last = memory.used_strategies[-1] if memory.used_strategies else None
    for c in candidates:
        if c != last:
            return c
    return candidates[0] if candidates else None

def route_state(perception: PerceptionResult, memory: SessionMemory) -> RouteDecision:
    memory.turn_count += 1
    memory.current_state = "S1"
    if perception.risk_flag:
        decision = RouteDecision(
            state="S2", state_name=STATE_NAMES.get("S2", "Unknown_State"), strategy=None,
            need_guardrail=True, next_goal=STRATEGY_GOALS["S2_None"],
            meta={"from":"S1","reason":"risk_flag=true","intent":perception.intent}
        )
        memory.current_state = decision.state
        memory.recent_states.append(decision.state)
        if perception.intent:
            memory.risk_events.append(perception.intent)
        return decision
        
    memory.current_state = "S3"
    if perception.misconception_tag:
        memory.current_misconception = perception.misconception_tag
        memory.topic = MISCONCEPTION_TO_TOPIC.get(perception.misconception_tag, memory.topic)
        
    # State Transition Matrix based on Cognitive State
    transition_map = {
        "固守错误概念": "S4",
        "认知冲突触发": "S4",
        "认知僵局": "S5",
        "新概念探索": "S6",
        "概念掌握验证": "S6"
    }
    
    target = transition_map.get(perception.cognitive_state, "S3")
    if target == "S4" and perception.misconception_tag is None:
        target = "S3" # Cannot do cognitive conflict without knowing the misconception
        
    # Anti-loop heuristics
    if target == "S4" and memory.recent_states.count("S4") >= 2:
        target = "S5"
    elif target != "S4" and target != "S6" and memory.recent_states[-3:] == [target] * 3:
        # 强制打破连续相同的非验证状态循环，推进到下一步或者退回澄清
        if target == "S5":
            target = "S6" # 如果在提供支架上卡住，尝试推进到验证环节看学生反应
        else:
            target = "S5" # 其他状态卡住，退回到提供支架

    strategy = _choose_strategy(target, memory)
    decision = RouteDecision(
        state=target, state_name=STATE_NAMES.get(target, "Unknown_State"), strategy=strategy,
        need_guardrail=False, next_goal=STRATEGY_GOALS.get(strategy, "未知目标"),
        meta={"from":"S3","intent":perception.intent,"misconception_tag":perception.misconception_tag,
              "cognitive_state":perception.cognitive_state,"confidence":perception.confidence,"topic":memory.topic}
    )
    memory.current_state = decision.state
    memory.recent_states.append(decision.state)
    if strategy is not None:
        memory.used_strategies.append(strategy)
    return decision

def update_after_turn(memory: SessionMemory, user_input: str, final_reply: str, history_summary: Optional[str] = None, understanding_verified: bool = False) -> SessionMemory:
    memory.messages.append({"role": "user", "content": user_input})
    memory.messages.append({"role": "assistant", "content": final_reply})
    memory.history_summary = history_summary if history_summary is not None else final_reply[:120]
    if understanding_verified:
        memory.resolved = True
    memory.recent_states = memory.recent_states[-10:]
    memory.used_strategies = memory.used_strategies[-10:]
    memory.risk_events = memory.risk_events[-10:]
    return memory
