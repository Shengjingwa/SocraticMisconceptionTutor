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
    perception = classify_input(user_input, history_summary=memory.history_summary)
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

def guardrail_node(state: GraphState) -> Dict[str, Any]:
    user_input = state["user_input"]
    perception = state["perception"]
    decision = state["decision"]
    generation = state["generation"]
    
    is_already_safe = decision.need_guardrail or decision.state == "S2"
    guardrail_result = apply_guardrails(
        user_input=user_input, 
        intent=perception.intent, 
        generated_text=generation["final_reply"], 
        misconception_tag=perception.misconception_tag,
        is_already_safe=is_already_safe
    )
    
    if guardrail_result["guardrail_triggered"] and not is_already_safe:
        new_decision = RouteDecision(
            state="S2",
            state_name="Refusal_And_Guidance",
            strategy=None,
            need_guardrail=True,
            next_goal=decision.next_goal,
            meta=decision.meta
        )
        return {"guardrail_result": guardrail_result, "decision": new_decision, "regeneration_required": True}
        
    return {"guardrail_result": guardrail_result, "regeneration_required": False}

def check_guardrail(state: GraphState) -> str:
    if state.get("regeneration_required", False):
        return "generate"
    return END

workflow = StateGraph(GraphState)

workflow.add_node("classify", classify_node)
workflow.add_node("route", route_node)
workflow.add_node("generate", generate_node)
workflow.add_node("guardrail", guardrail_node)

workflow.set_entry_point("classify")

workflow.add_edge("classify", "route")
workflow.add_edge("route", "generate")
workflow.add_edge("generate", "guardrail")

workflow.add_conditional_edges(
    "guardrail",
    check_guardrail,
    {
        "generate": "generate",
        END: END
    }
)

app_graph = workflow.compile()
