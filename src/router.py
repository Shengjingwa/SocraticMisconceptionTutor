from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from pydantic import BaseModel, Field

# Try to silence the warning by setting the module level allowed types
if hasattr(builtins, "allowed_msgpack_modules"):
    builtins.allowed_msgpack_modules.extend(
        [("router", "SessionMemory"), ("router", "PerceptionResult"), ("router", "RouteDecision")]
    )
else:
    builtins.allowed_msgpack_modules = [
        ("router", "SessionMemory"),
        ("router", "PerceptionResult"),
        ("router", "RouteDecision"),
    ]


@dataclass
class PerceptionResult:
    intent: str
    misconception_tag: Optional[str] = None
    cognitive_state: str = "认知僵局"
    sentiment: str = "平静"
    risk_flag: bool = False
    confidence: float = 0.0
    transition_approved: bool = False
    reasoning: str = ""


class SessionMemory(BaseModel):
    session_id: str
    topic: Optional[str] = None
    current_state: str = "S0"
    current_misconception: Optional[str] = None
    turn_count: int = 0
    history_summary: str = ""
    used_strategies: List[str] = Field(default_factory=list)
    recent_states: List[str] = Field(default_factory=list)
    risk_events: List[str] = Field(default_factory=list)
    resolved: bool = False
    aborted: bool = False
    consecutive_guardrail_triggers: int = 0
    turn_guardrail_triggers: int = 0


@dataclass
class RouteDecision:
    state: str
    state_name: str
    strategy: Optional[str]
    need_guardrail: bool
    next_goal: str
    meta: Dict[str, Any] = field(default_factory=dict)


# Explicitly register to the global JsonPlusSerializer module namespace
try:
    from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

    JsonPlusSerializer.with_msgpack_allowlist(
        None, [SessionMemory, PerceptionResult, RouteDecision]
    )
except Exception:
    pass

STATE_NAMES = {
    "S0": "Listen_And_Analyze",
    "S1": "Guardrail_Check",
    "S2": "Refusal_And_Guidance",
    "S3": "Misconception_Diagnosis",
    "S4": "Cognitive_Conflict",
    "S5": "Scaffolding_Guidance",
    "S6": "Verification_Deepening",
    "S7": "Fact_Grounding",
    "S8": "Acknowledge_and_Park",
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
    "S5": ["Clarification", "Evidence_Seeking", "Analogical_Scaffolding", "Sub_goal_Tracking"],
    "S6": ["Evidence_Seeking", "Consequence_Exploration"],
    "S7": ["Fact_Grounding"],
    "S8": ["Acknowledge_and_Park"],
}
STRATEGY_GOALS = {
    None: "引导学生进一步明确自己的想法或提供更多细节。",
    "S2_None": "拒绝直接代答，并将对话重定向回引导式学习路径。",
    "Clarification": "澄清学生表述中的模糊概念，找准真正的认知问题。",
    "Assumption_Probing": "暴露学生结论背后的隐含前提，制造认知冲突。",
    "Evidence_Seeking": "引导学生用现象、实验或理由支持自己的判断。",
    "Consequence_Exploration": "把学生当前解释继续推演，检验其后果是否合理。",
    "Analogical_Scaffolding": "用有边界的类比支架帮助学生跨过理解障碍。",
    "Fact_Grounding": "直接提供不可反驳的物理实验现象或事实，制造强烈的认知冲突，且绝对不给出原理解释。",
    "Sub_goal_Tracking": "引导学生通过2-3步的微引导路径逐步打破僵局。",
    "Acknowledge_and_Park": "承认当前问题的难度，肯定学生的努力，并主动提议暂时搁置该问题以缓解焦虑。",
}


@dataclass
class TransitionRule:
    """声明式状态转移与防环规则"""

    condition: Callable[[str, PerceptionResult, SessionMemory], bool]
    action: Callable[[str], str]
    description: str


TRANSITION_RULES = [
    # 基础转移规则：如果目标是S4但缺失错误概念标签，降级为S3
    TransitionRule(
        condition=lambda target, p, m: target == "S4" and p.misconception_tag is None,
        action=lambda target: "S3",
        description="Cannot do cognitive conflict without knowing the misconception",
    )
]

ANTI_LOOP_RULES = [
    # 防环规则1：S4死循环防备 (近期连续多次S4) -> 强制转移到S5
    TransitionRule(
        condition=lambda target, p, m: target == "S4" and m.recent_states.count("S4") >= 2,
        action=lambda target: "S5",
        description="Break S4 loop",
    ),
    # 防环规则2：用户拒绝思想实验（在S4且表现出焦虑/挫败情绪） -> 降级到S5
    TransitionRule(
        condition=lambda target, p, m: target == "S4" and p.sentiment == "焦虑/挫败",
        action=lambda target: "S5",
        description="User rejects thought experiment (negative sentiment in S4), downgrade to S5",
    ),
    # 防环规则3：S5深度死循环防备 (近期连续3次以上S5) -> 降级到S7事实兜底
    TransitionRule(
        condition=lambda target, p, m: (
            target == "S5" and m.recent_states[-3:] == ["S5", "S5", "S5"]
        ),
        action=lambda target: "S7",
        description="Break S5 deep loop, fallback to S7 Fact-Grounding",
    ),
    # 防环规则4：S7死循环防备 (近期在S7卡住2次或以上) -> 转移到S8承认并搁置
    TransitionRule(
        condition=lambda target, p, m: target == "S7" and m.recent_states.count("S7") >= 2,
        action=lambda target: "S8",
        description="Break S7 loop, transition to S8 Acknowledge and Park",
    ),
    # 防环规则5：S8状态退出机制 (如果上一轮已经是S8，这一轮强制留在S8并准备结束会话)
    TransitionRule(
        condition=lambda target, p, m: len(m.recent_states) >= 1 and m.recent_states[-1] == "S8",
        action=lambda target: "S8",
        description="Already in S8, force stay in S8 to abort session",
    ),
    # 防环规则6：其他非验证状态连续卡住3次 -> 强制转移到S5提供支架
    TransitionRule(
        condition=lambda target, p, m: (
            target not in ("S4", "S6", "S7", "S8") and m.recent_states[-3:] == [target] * 3
        ),
        action=lambda target: "S5",
        description="Break other loops",
    ),
]


def apply_transition_rules(
    initial_target: str, perception: PerceptionResult, memory: SessionMemory
) -> str:
    """应用声明式的防环与转移规则"""
    target = initial_target

    # 1. 应用基础转移规则
    for rule in TRANSITION_RULES:
        if rule.condition(target, perception, memory):
            target = rule.action(target)

    # 2. 应用防死循环规则（互斥，匹配一条即止）
    for rule in ANTI_LOOP_RULES:
        if rule.condition(target, perception, memory):
            target = rule.action(target)
            break

    return target


def _choose_strategy(
    state: str, memory: SessionMemory, perception: Optional[PerceptionResult] = None
) -> Optional[str]:
    candidates = STATE_STRATEGIES.get(state, [None])
    if not candidates or candidates == [None]:
        return None

    recent_states = memory.recent_states

    # 启发式动态推荐规则: 认知僵局强制走 Sub_goal_Tracking
    if (
        perception
        and perception.cognitive_state == "认知僵局"
        and "Sub_goal_Tracking" in candidates
    ):
        return "Sub_goal_Tracking"

    # 启发式动态推荐规则 1: 如果在 S5 (Scaffolding) 状态卡住多次，优先使用类比支架
    if state == "S5":
        # 如果因为负面情绪从S4降级过来，或者用户明确拒绝思想实验
        if (
            perception
            and perception.sentiment == "焦虑/挫败"
            and len(recent_states) >= 1
            and recent_states[-1] == "S4"
        ):
            return "Analogical_Scaffolding"

        if len(recent_states) >= 2 and recent_states[-1] == "S5" and recent_states[-2] == "S5":
            return "Analogical_Scaffolding"
        # 刚从认知冲突(S4)转移过来，先尝试澄清
        if len(recent_states) >= 1 and recent_states[-1] == "S4":
            return "Clarification"

    # 启发式动态推荐规则 2: 在 S4 (Cognitive Conflict) 状态，逐步深入
    if state == "S4":
        # 刚从 S5 卡壳退回来的情况，尝试推演后果
        if len(recent_states) >= 1 and recent_states[-1] == "S5":
            return "Consequence_Exploration"
        # 连续处于认知冲突时，尝试推演后果
        if len(recent_states) >= 1 and recent_states[-1] == "S4":
            return "Consequence_Exploration"
        # 首次进入认知冲突，暴露隐含前提
        return "Assumption_Probing"

    # 启发式动态推荐规则 3: 默认避免连续使用同一策略
    last = memory.used_strategies[-1] if memory.used_strategies else None
    for c in candidates:
        if c != last:
            return c
    return candidates[0]


def route_state(
    perception: PerceptionResult, memory: SessionMemory
) -> Tuple[RouteDecision, SessionMemory]:
    new_memory = memory.model_copy(deep=True)
    new_memory.turn_count += 1
    new_memory.current_state = "S1"

    # 强制熔断机制：如果上一轮已经是S8，强制停留在S8并终止会话，忽略其他任何护栏或意图
    if len(memory.recent_states) >= 1 and memory.recent_states[-1] == "S8":
        decision = RouteDecision(
            state="S8",
            state_name=STATE_NAMES.get("S8", "Acknowledge_and_Park"),
            strategy="Acknowledge_and_Park",
            need_guardrail=False,
            next_goal=STRATEGY_GOALS["Acknowledge_and_Park"],
            meta={"from": "S8", "reason": "force_abort_from_s8"},
        )
        new_memory.current_state = decision.state
        new_memory.recent_states.append(decision.state)
        new_memory.used_strategies.append("Acknowledge_and_Park")
        new_memory.aborted = True
        return decision, new_memory

    if perception.risk_flag:
        decision = RouteDecision(
            state="S2",
            state_name=STATE_NAMES.get("S2", "Unknown_State"),
            strategy=None,
            need_guardrail=True,
            next_goal=STRATEGY_GOALS["S2_None"],
            meta={
                "from": "S1",
                "reason": "risk_flag=true",
                "intent": perception.intent,
                "sentiment": perception.sentiment,
            },
        )
        new_memory.current_state = decision.state
        new_memory.recent_states.append(decision.state)
        if perception.intent:
            new_memory.risk_events.append(perception.intent)
        return decision, new_memory

    new_memory.current_state = "S3"
    if perception.misconception_tag:
        new_memory.current_misconception = perception.misconception_tag
        new_memory.topic = MISCONCEPTION_TO_TOPIC.get(
            perception.misconception_tag, new_memory.topic
        )

    # State Transition Logic based on Assessor Agent
    # Find the last valid pedagogical state
    valid_states = [s for s in memory.recent_states if s in ["S3", "S4", "S5", "S6", "S7", "S8"]]
    base_state = valid_states[-1] if valid_states else "S3"

    if perception.transition_approved:
        if base_state == "S3":
            target = "S4"
        elif base_state == "S4":
            target = "S5"
        elif base_state in ["S5", "S7", "S8"]:
            target = "S6"
        else:
            target = "S6"
    else:
        target = base_state

    # 应用声明式转移与防死循环规则
    target = apply_transition_rules(target, perception, new_memory)

    strategy = _choose_strategy(target, new_memory, perception)
    decision = RouteDecision(
        state=target,
        state_name=STATE_NAMES.get(target, "Unknown_State"),
        strategy=strategy,
        need_guardrail=False,
        next_goal=STRATEGY_GOALS.get(strategy, "未知目标"),
        meta={
            "from": "S3",
            "intent": perception.intent,
            "misconception_tag": perception.misconception_tag,
            "cognitive_state": perception.cognitive_state,
            "confidence": perception.confidence,
            "sentiment": perception.sentiment,
            "transition_approved": perception.transition_approved,
            "reasoning": perception.reasoning,
            "topic": new_memory.topic,
        },
    )
    new_memory.current_state = decision.state
    new_memory.recent_states.append(decision.state)
    if strategy is not None:
        new_memory.used_strategies.append(strategy)

    if (
        decision.state == "S8"
        and len(memory.recent_states) >= 1
        and memory.recent_states[-1] == "S8"
    ):
        new_memory.aborted = True

    return decision, new_memory


def update_after_turn(
    memory: SessionMemory,
    user_input: str,
    final_reply: str,
    history_summary: Optional[str] = None,
    understanding_verified: bool = False,
) -> SessionMemory:
    new_memory = memory.model_copy(deep=True)
    if understanding_verified:
        new_memory.resolved = True
    if history_summary is not None:
        new_memory.history_summary = history_summary
    new_memory.recent_states = new_memory.recent_states[-10:]
    new_memory.used_strategies = new_memory.used_strategies[-10:]
    new_memory.risk_events = new_memory.risk_events[-10:]
    new_memory.turn_guardrail_triggers = 0
    return new_memory
