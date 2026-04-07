from langgraph.graph import StateGraph, END, START
from typing import Dict, Any
from langchain_openai import ChatOpenAI

from state import GraphState
from classifiers import classify_input
from router import route_state, RouteDecision
from generator import generate_reply
from guardrails import apply_guardrails

def baseline_node(state: GraphState) -> Dict[str, Any]:
    user_input = state["user_input"]
    memory = state["memory"]
    memory.turn_count += 1
    
    import os
    api_key = os.environ.get("DEEPSEEK_API_KEY", "dummy_key")
    if not api_key or api_key == "dummy_key":
        response_content = "Mocked baseline response"
    else:
        # Simple direct LLM call for baseline
        llm = ChatOpenAI(
            model="deepseek-chat", 
            temperature=0.7,
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Construct a simple prompt including history
        history_text = memory.history_summary
        prompt = f"你是一个苏格拉底式的物理老师。请根据以下对话历史，回复学生的最新问题。\n\n历史对话摘要：\n{history_text}\n\n学生：{user_input}\n老师："
        
        response = llm.invoke(prompt)
        response_content = response.content
        
    generation = {
        "final_reply": response_content,
        "raw_reply": response_content,
        "strategy": "baseline",
        "thought": "Direct LLM generation"
    }
    return {"generation": generation}

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
    system_version = state.get("system_version", "FSM+Guardrail")
    
    if system_version == "FSM":
        # Skip guardrails, always safe
        guardrail_result = {
            "is_safe": True,
            "guardrail_triggered": False,
            "reason": "Guardrail skipped in FSM version",
            "modified_reply": None
        }
        return {"guardrail_result": guardrail_result, "regeneration_required": False}
        
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

def route_entry(state: GraphState) -> str:
    version = state.get("system_version", "FSM+Guardrail")
    if version == "Baseline":
        return "baseline"
    return "classify"

workflow = StateGraph(GraphState)

workflow.add_node("baseline", baseline_node)
workflow.add_node("classify", classify_node)
workflow.add_node("route", route_node)
workflow.add_node("generate", generate_node)
workflow.add_node("guardrail", guardrail_node)

workflow.add_conditional_edges(
    START,
    route_entry,
    {
        "baseline": "baseline",
        "classify": "classify"
    }
)

workflow.add_edge("baseline", END)
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
