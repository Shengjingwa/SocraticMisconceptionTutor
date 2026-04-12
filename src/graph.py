from langgraph.graph import StateGraph, END
from typing import Dict, Any

from state import GraphState
from classifiers import classify_input
from router import route_state, RouteDecision
from generator import generate_reply
from guardrails import apply_guardrails

def classify_node(state: GraphState) -> Dict[str, Any]:
    user_input = state["user_input"]
    memory = state["memory"]
    perception = classify_input(user_input, messages=memory.messages)
    return {"perception": perception}

def route_node(state: GraphState) -> Dict[str, Any]:
    perception = state["perception"]
    memory = state["memory"]
    decision = route_state(perception, memory)
    return {"decision": decision}

def generate_node(state: GraphState) -> Dict[str, Any]:
    user_input = state["user_input"]
    decision = state["decision"]
    memory = state["memory"]
    generation = generate_reply(user_input, decision, memory, history_summary=memory.history_summary)
    # 每次重新生成都需要清除 regeneration_required 标志，防止死循环。
    # 这里我们不用在 graph state 返回里清空，因为如果再次进入 guardrail 并且 safe, guardrail node 会置 False。
    return {"generation": generation}

def route_after_route(state: GraphState) -> str:
    system_version = state.get("system_version", "FSM+Guardrail")
    if system_version == "Baseline":
        return "baseline"
    return "generate"

def route_after_generate(state: GraphState) -> str:
    system_version = state.get("system_version", "FSM+Guardrail")
    # 只在 FSM+Guardrail 版本使用护栏
    if system_version == "FSM+Guardrail":
        return "guardrail"
    return "end"

def route_after_guardrail(state: GraphState) -> str:
    if state.get("regeneration_required", False):
        return "generate"
    return "end"

def guardrail_node(state: GraphState) -> Dict[str, Any]:
    user_input = state["user_input"]
    perception = state["perception"]
    decision = state["decision"]
    generation = state["generation"]
    
    retries = decision.meta.get("guardrail_retries", 0)
    if retries >= 3:
        generation["final_reply"] = "为了确保准确性，我建议我们先从基础概念开始梳理。你能告诉我你目前最确定的部分是什么吗？"
        guardrail_result = {"guardrail_triggered": True, "guardrail_reason": "Max_Retries_Exceeded", "answer_leakage_flag": False}
        return {"guardrail_result": guardrail_result, "regeneration_required": False, "generation": generation}

    is_already_safe = decision.need_guardrail or decision.state == "S2"
    guardrail_result = apply_guardrails(
        user_input=user_input,
        intent=perception.intent,
        generated_text=generation["final_reply"],
        misconception_tag=perception.misconception_tag,
        is_already_safe=is_already_safe
    )

    if guardrail_result["guardrail_triggered"] and (not is_already_safe or guardrail_result.get("answer_leakage_flag", False)):
        new_meta = decision.meta.copy()
        new_meta["guardrail_retries"] = retries + 1
        new_decision = RouteDecision(
            state="S2",
            state_name="Refusal_And_Guidance",
            strategy=None,
            need_guardrail=True,
            next_goal=decision.next_goal,
            meta=new_meta
        )
        return {"guardrail_result": guardrail_result, "decision": new_decision, "regeneration_required": True}

    return {"guardrail_result": guardrail_result, "regeneration_required": False}

def baseline_node(state: GraphState) -> Dict[str, Any]:
    from generator import generate_reply
    from router import PerceptionResult, RouteDecision
    user_input = state["user_input"]
    memory = state["memory"]

    # 填充假的 perception 和 decision
    perception = PerceptionResult(intent="Unknown", misconception_tag=memory.current_misconception, cognitive_state="新概念探索", risk_flag=False, confidence=0.0)
    decision = RouteDecision(state="S5", state_name="Scaffolding_Guidance", strategy="General_Reply", need_guardrail=False, next_goal=None, meta={})

    generation = generate_reply(user_input, decision, memory)

    return {
        "perception": perception,
        "decision": decision,
        "generation": generation,
        "guardrail_result": {"guardrail_triggered": False, "guardrail_reason": None}
    }

workflow = StateGraph(GraphState)

workflow.add_node("classify", classify_node)
workflow.add_node("route", route_node)
workflow.add_node("generate", generate_node)
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("baseline", baseline_node)

workflow.set_entry_point("classify")

workflow.add_edge("classify", "route")

workflow.add_conditional_edges(
    "route",
    route_after_route,
    {
        "baseline": "baseline",
        "generate": "generate"
    }
)

workflow.add_conditional_edges(
    "generate",
    route_after_generate,
    {
        "guardrail": "guardrail",
        "end": END
    }
)

workflow.add_conditional_edges(
    "guardrail",
    route_after_guardrail,
    {
        "generate": "generate",
        "end": END
    }
)

workflow.add_edge("baseline", END)

app_graph = workflow.compile()
