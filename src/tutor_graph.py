from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, RemoveMessage, SystemMessage
from typing import Dict, Any
import config

from state import GraphState
from classifiers import classify_input
from router import route_state, RouteDecision
from generator import generate_reply
from guardrails import apply_guardrails

def classify_node(state: GraphState) -> Dict[str, Any]:
    user_input = state["user_input"]
    memory = state["memory"]
    messages = state.get("messages", [])
    perception = classify_input(user_input, messages=messages, history_summary=memory.history_summary)
    return {"perception": perception}

def route_node(state: GraphState) -> Dict[str, Any]:
    perception = state["perception"]
    memory = state["memory"]
    decision, new_memory = route_state(perception, memory)
    return {"decision": decision, "memory": new_memory}

def generate_node(state: GraphState) -> Dict[str, Any]:
    user_input = state["user_input"]
    decision = state["decision"]
    memory = state["memory"]
    messages = state.get("messages", [])
    generation = generate_reply(user_input, decision, memory, messages=messages)
    return {"generation": generation}

def route_start(state: GraphState) -> str:
    system_version = state.get("system_version", "FSM+Guardrail")
    if system_version == "Baseline":
        return "baseline"
    return "classify"

def route_after_generate(state: GraphState) -> str:
    return "guardrail"

def route_after_guardrail(state: GraphState) -> str:
    if state.get("regeneration_required", False):
        return "generate"
    return "finalize"

def guardrail_node(state: GraphState) -> Dict[str, Any]:
    user_input = state["user_input"]
    perception = state["perception"]
    decision = state["decision"]
    generation = state["generation"]
    system_version = state.get("system_version", "FSM+Guardrail")
    memory = state["memory"]
    
    retries = decision.meta.get("guardrail_retries", 0)
    if retries >= 2:
        new_memory = memory.model_copy(deep=True)
        new_memory.consecutive_guardrail_triggers += 1
        generation["final_reply"] = "为了确保准确性，我建议我们先从基础概念开始梳理。你能告诉我你目前最确定的部分是什么吗？"
        guardrail_result = {"guardrail_triggered": True, "guardrail_reason": "Max_Retries_Exceeded", "answer_leakage_flag": False}
        return {"guardrail_result": guardrail_result, "regeneration_required": False, "generation": generation, "memory": new_memory}

    is_already_safe = not decision.need_guardrail
    guardrail_result = apply_guardrails(
        user_input=user_input,
        intent=perception.intent,
        generated_text=generation["final_reply"],
        misconception_tag=perception.misconception_tag,
        is_already_safe=is_already_safe,
        consecutive_triggers=memory.consecutive_guardrail_triggers,
        current_state=decision.state
    )

    if system_version != "FSM+Guardrail":
        guardrail_result["guardrail_triggered"] = False
        return {"guardrail_result": guardrail_result, "regeneration_required": False}

    new_memory = memory.model_copy(deep=True)
    if guardrail_result["guardrail_triggered"] and (not is_already_safe or guardrail_result.get("answer_leakage_flag", False)):
        new_memory.consecutive_guardrail_triggers += 1
        
        new_meta = decision.meta.copy()
        new_meta["guardrail_retries"] = retries + 1
        
        if guardrail_result.get("answer_leakage_flag", False):
            # 柔性护栏：不改变原始教学状态，将拦截理由作为反馈要求重新生成
            new_meta["guardrail_feedback"] = guardrail_result.get("guardrail_reason", "Answer Leakage")
            new_decision = RouteDecision(
                state=decision.state,
                state_name=decision.state_name,
                strategy=decision.strategy,
                need_guardrail=False,
                next_goal=decision.next_goal,
                meta=new_meta
            )
        else:
            # 硬拦截（如输入包含不当意图未被前置拦截时）
            new_decision = RouteDecision(
                state="S2",
                state_name="Refusal_And_Guidance",
                strategy=None,
                need_guardrail=True,
                next_goal=decision.next_goal,
                meta=new_meta
            )
        return {"guardrail_result": guardrail_result, "decision": new_decision, "regeneration_required": True, "memory": new_memory}

    # 如果没有触发护栏，重置连续触发计数器
    new_memory.consecutive_guardrail_triggers = 0
    return {"guardrail_result": guardrail_result, "regeneration_required": False, "memory": new_memory}

def finalize_node(state: GraphState) -> Dict[str, Any]:
    generation = state["generation"]
    memory = state["memory"]
    messages = state.get("messages", [])
    
    new_memory = memory.model_copy(deep=True)
    
    # 存入本轮 AI 回复
    final_reply = generation["final_reply"]
    new_message = AIMessage(content=final_reply)
    updates = {"messages": [new_message]}
    
    # 动态压缩机制：如果历史轮次过长
    if len(messages) > config.MAX_HISTORY_TURNS * 2:
        import json
        llm = config.get_tutor_llm(max_tokens=500)
        
        # 把前段需要被清理的 messages (保留最近的2个对话，即4条消息) 提取出来合并到旧摘要
        msgs_to_compress = messages[:-4]
        
        text_to_compress = "\n".join([f"{msg.type}: {msg.content}" for msg in msgs_to_compress])
        prompt = f"你是一个教育助手的记忆摘要模块。请将以下之前的对话摘要与最新的一段对话记录合并，写成一段简洁的上下文总结（不超过300字）。重点保留学生表现出的物理误概念、老师的引导策略以及学生情绪状态的变化。\n\n之前的摘要: {new_memory.history_summary}\n\n最新的对话记录:\n{text_to_compress}\n\n请输出新的合并摘要："
        
        response = llm.invoke(prompt)
        new_summary = response.content.strip()
        
        # 更新状态中的 summary
        new_memory.history_summary = new_summary
        
        # 返回 RemoveMessage 剔除已经被压缩的消息
        updates["messages"] = [RemoveMessage(id=m.id) for m in msgs_to_compress] + [new_message]
        
    updates["memory"] = new_memory
    return updates
def baseline_node(state: GraphState) -> Dict[str, Any]:
    from generator import generate_baseline_reply
    from router import PerceptionResult, RouteDecision
    user_input = state["user_input"]
    memory = state["memory"]
    messages = state.get("messages", [])

    new_memory = memory.model_copy(deep=True)
    new_memory.turn_count += 1
    new_memory.current_state = "Baseline"
    new_memory.recent_states.append("Baseline")

    # 填充假的 perception 和 decision
    perception = PerceptionResult(intent="Unknown", misconception_tag=new_memory.current_misconception, cognitive_state="新概念探索", risk_flag=False, confidence=0.0)
    decision = RouteDecision(state="Baseline", state_name="Baseline_Chat", strategy="General_Reply", need_guardrail=False, next_goal=None, meta={})

    generation = generate_baseline_reply(user_input, new_memory, messages=messages)

    return {
        "perception": perception,
        "decision": decision,
        "generation": generation,
        "memory": new_memory
    }

workflow = StateGraph(GraphState)

workflow.add_node("classify", classify_node)
workflow.add_node("route", route_node)
workflow.add_node("generate", generate_node)
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("baseline", baseline_node)
workflow.add_node("finalize", finalize_node)

workflow.add_conditional_edges(
    START,
    route_start,
    {
        "baseline": "baseline",
        "classify": "classify"
    }
)

workflow.add_edge("classify", "route")
workflow.add_edge("route", "generate")

workflow.add_conditional_edges(
    "generate",
    route_after_generate,
    {
        "guardrail": "guardrail"
    }
)

workflow.add_conditional_edges(
    "guardrail",
    route_after_guardrail,
    {
        "generate": "generate",
        "finalize": "finalize"
    }
)

workflow.add_edge("finalize", END)
workflow.add_edge("baseline", "guardrail")

memory_saver = MemorySaver()
app_graph = workflow.compile(checkpointer=memory_saver)
