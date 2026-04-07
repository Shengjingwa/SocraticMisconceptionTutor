import json
import csv
from collections import defaultdict

def evaluate():
    turn_logs = []
    with open('logs/turn_logs.jsonl', 'r') as f:
        for line in f:
            turn_logs.append(json.loads(line))
            
    session_logs = []
    with open('logs/session_summary.jsonl', 'r') as f:
        for line in f:
            session_logs.append(json.loads(line))

    versions = ["Baseline", "FSM", "FSM+Guardrail"]
    metrics = defaultdict(lambda: {
        "total_sessions": 0,
        "resolved_sessions": 0,
        "total_turns": 0,
        "correct_identification_turns": 0,
        "total_identification_turns": 0,
        "direct_answer_seek_turns": 0,
        "refused_turns": 0,
        "guardrail_triggered_turns": 0,
        "answer_leakage_turns": 0,
        "successful_transitions": 0,
        "abnormal_terminations": 0
    })

    for s in session_logs:
        v = s["system_version"]
        metrics[v]["total_sessions"] += 1
        if s["resolved_flag"]:
            metrics[v]["resolved_sessions"] += 1
        if s["abnormal_end_flag"] or s["termination_reason"] == "error":
            metrics[v]["abnormal_terminations"] += 1

    for t in turn_logs:
        v = t["system_version"]
        metrics[v]["total_turns"] += 1
        
        if t["misconception_pred"] != "Unknown" and t["misconception_pred"] is not None:
            metrics[v]["total_identification_turns"] += 1
            if t["misconception_pred"] == t["misconception_gt"]:
                metrics[v]["correct_identification_turns"] += 1
                
        if t["intent_pred"] == "Direct_Answer_Seek":
            metrics[v]["direct_answer_seek_turns"] += 1
            if t["current_state"] == "S2" or t["guardrail_triggered"]:
                metrics[v]["refused_turns"] += 1
                
        if t["guardrail_triggered"]:
            metrics[v]["guardrail_triggered_turns"] += 1
            
        if t["answer_leakage_flag"]:
            metrics[v]["answer_leakage_turns"] += 1
            
        if t["state_transition_success"]:
            metrics[v]["successful_transitions"] += 1

    results = []
    for v in versions:
        m = metrics[v]
        total_s = m["total_sessions"] or 1
        total_t = m["total_turns"] or 1
        
        id_acc = m["correct_identification_turns"] / m["total_identification_turns"] if m["total_identification_turns"] > 0 else 0.0
        cog_corr = m["resolved_sessions"] / total_s
        avg_turns = total_t / total_s
        refusal_rate = m["refused_turns"] / m["direct_answer_seek_turns"] if m["direct_answer_seek_turns"] > 0 else 0.0
        guardrail_rate = m["guardrail_triggered_turns"] / total_t
        leakage_rate = m["answer_leakage_turns"] / total_t
        transition_rate = m["successful_transitions"] / total_t
        abnormal_rate = m["abnormal_terminations"] / total_s

        results.append({
            "Version": v,
            "Identification Accuracy": f"{id_acc:.2%}",
            "Cognitive Correction Rate": f"{cog_corr:.2%}",
            "Avg Turns": f"{avg_turns:.2f}",
            "Refusal Success Rate": f"{refusal_rate:.2%}",
            "Guardrail Interception Rate": f"{guardrail_rate:.2%}",
            "Answer Leakage Rate": f"{leakage_rate:.2%}",
            "Transition Success Rate": f"{transition_rate:.2%}",
            "Abnormal Termination Rate": f"{abnormal_rate:.2%}"
        })

    import os
    os.makedirs('results', exist_ok=True)
    with open('results/summary_metrics.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print("Metrics calculated and saved to results/summary_metrics.csv")

def sample_audit():
    import random
    sessions_by_version = {"Baseline": [], "FSM": [], "FSM+Guardrail": []}
    
    with open('logs/session_summary.jsonl', 'r') as f:
        for line in f:
            session = json.loads(line)
            sessions_by_version[session['system_version']].append(session['session_id'])
            
    # Sample 2 sessions per version
    sampled_ids = set()
    for v in sessions_by_version:
        if sessions_by_version[v]:
            sampled_ids.update(random.sample(sessions_by_version[v], min(2, len(sessions_by_version[v]))))
            
    audit_rows = []
    with open('logs/turn_logs.jsonl', 'r') as f:
        for line in f:
            turn = json.loads(line)
            if turn['session_id'] in sampled_ids:
                audit_rows.append({
                    "Session ID": turn['session_id'],
                    "Version": turn['system_version'],
                    "Turn ID": turn['turn_id'],
                    "Student Input": turn['student_input'],
                    "System Reply": turn['final_reply'],
                    "Audit - Score (1-5)": "",
                    "Audit - Comments": ""
                })
                
    # Sort by Session ID and Turn ID
    audit_rows.sort(key=lambda x: (x["Session ID"], x["Turn ID"]))
    
    if audit_rows:
        with open('results/manual_audit.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=audit_rows[0].keys())
            writer.writeheader()
            writer.writerows(audit_rows)
            
        print("Created results/manual_audit.csv")

if __name__ == "__main__":
    evaluate()
    sample_audit()
