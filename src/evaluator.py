import csv
import json
import os
from collections import defaultdict


def evaluate() -> None:
    base_dir = os.path.dirname(__file__)
    logs_dir = os.environ.get("LOG_DIR", os.path.join(base_dir, "..", "logs"))
    results_dir = os.environ.get("RESULTS_DIR", os.path.join(base_dir, "..", "results"))
    with open(
        os.path.join(base_dir, "..", "data", "misconceptions.json"), "r", encoding="utf-8"
    ) as f:
        misconceptions = json.load(f)
        name_to_id = {m["misconception_name"]: m["id"] for m in misconceptions}

    turn_logs = []
    with open(os.path.join(logs_dir, "turn_logs.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            turn_logs.append(json.loads(line))

    session_logs = []
    with open(os.path.join(logs_dir, "session_summary.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            session_logs.append(json.loads(line))

    versions = ["Baseline", "FSM", "FSM+Guardrail"]
    metrics = defaultdict(
        lambda: {
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
            "abnormal_terminations": 0,
        }
    )

    for s in session_logs:
        v = s["system_version"]
        metrics[v]["total_sessions"] += 1
        if s["resolved_flag"]:
            metrics[v]["resolved_sessions"] += 1
        if s["abnormal_end_flag"] or s["termination_reason"] == "error":
            metrics[v]["abnormal_terminations"] += 1

    prev_states = {}

    for t in turn_logs:
        v = t["system_version"]
        metrics[v]["total_turns"] += 1

        gt = t.get("misconception_gt")
        if gt and gt != "Unknown":
            metrics[v]["total_identification_turns"] += 1
            gt_id = name_to_id.get(gt, gt)
            pred = t.get("misconception_pred")
            if pred == gt or pred == gt_id:
                metrics[v]["correct_identification_turns"] += 1

        if t["intent_pred"] == "Direct_Answer_Seek":
            metrics[v]["direct_answer_seek_turns"] += 1
            if t["current_state"] == "S2" or t["guardrail_triggered"]:
                metrics[v]["refused_turns"] += 1

        if t["guardrail_triggered"]:
            metrics[v]["guardrail_triggered_turns"] += 1

        if t["answer_leakage_flag"]:
            metrics[v]["answer_leakage_turns"] += 1

        session_id = t["session_id"]
        current_state = t["current_state"]
        prev_state = prev_states.get(session_id)
        if prev_state is not None and current_state != prev_state:
            metrics[v]["successful_transitions"] += 1
        prev_states[session_id] = current_state

    present_versions = {s.get("system_version") for s in session_logs if s.get("system_version")}
    if present_versions:
        versions = [v for v in versions if v in present_versions] + sorted(
            present_versions - set(versions)
        )

    results = []
    for v in versions:
        m = metrics[v]
        total_s = m["total_sessions"] or 1
        total_t = m["total_turns"] or 1

        id_acc = (
            m["correct_identification_turns"] / m["total_identification_turns"]
            if m["total_identification_turns"] > 0
            else 0.0
        )
        cog_corr = m["resolved_sessions"] / total_s
        avg_turns = total_t / total_s
        refusal_rate = (
            m["refused_turns"] / m["direct_answer_seek_turns"]
            if m["direct_answer_seek_turns"] > 0
            else 0.0
        )
        guardrail_rate = m["guardrail_triggered_turns"] / total_t
        leakage_rate = m["answer_leakage_turns"] / total_t
        transition_rate = (
            m["successful_transitions"] / (total_t - total_s) if total_t > total_s else 0.0
        )
        abnormal_rate = m["abnormal_terminations"] / total_s

        results.append(
            {
                "Version": v,
                "Identification Accuracy": f"{id_acc:.2%}",
                "Cognitive Correction Rate": f"{cog_corr:.2%}",
                "Avg Turns": f"{avg_turns:.2f}",
                "Refusal Success Rate": f"{refusal_rate:.2%}",
                "Guardrail Interception Rate": f"{guardrail_rate:.2%}",
                "Answer Leakage Rate": f"{leakage_rate:.2%}",
                "Transition Success Rate": f"{transition_rate:.2%}",
                "Abnormal Termination Rate": f"{abnormal_rate:.2%}",
            }
        )

    os.makedirs(results_dir, exist_ok=True)
    fieldnames = (
        results[0].keys()
        if results
        else [
            "Version",
            "Identification Accuracy",
            "Cognitive Correction Rate",
            "Avg Turns",
            "Refusal Success Rate",
            "Guardrail Interception Rate",
            "Answer Leakage Rate",
            "Transition Success Rate",
            "Abnormal Termination Rate",
        ]
    )
    with open(
        os.path.join(results_dir, "summary_metrics.csv"), "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Metrics calculated and saved to {os.path.join(results_dir, 'summary_metrics.csv')}")


def sample_audit() -> None:
    import random

    base_dir = os.path.dirname(__file__)
    logs_dir = os.environ.get("LOG_DIR", os.path.join(base_dir, "..", "logs"))
    results_dir = os.environ.get("RESULTS_DIR", os.path.join(base_dir, "..", "results"))
    sessions_by_version = {}

    with open(os.path.join(logs_dir, "session_summary.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            session = json.loads(line)
            v = session.get("system_version") or "Unknown"
            sessions_by_version.setdefault(v, []).append(session.get("session_id"))

    # Sample 2 sessions per version
    sampled_ids = set()
    for v in sessions_by_version:
        if sessions_by_version[v]:
            sampled_ids.update(
                random.sample(sessions_by_version[v], min(2, len(sessions_by_version[v])))
            )

    audit_rows = []
    with open(os.path.join(logs_dir, "turn_logs.jsonl"), "r", encoding="utf-8") as f:
        for line in f:
            turn = json.loads(line)
            if turn["session_id"] in sampled_ids:
                audit_rows.append(
                    {
                        "Session ID": turn["session_id"],
                        "Version": turn["system_version"],
                        "Turn ID": turn["turn_id"],
                        "Student Input": turn["student_input"],
                        "System Reply": turn["final_reply"],
                        "Audit - Score (1-5)": "",
                        "Audit - Comments": "",
                    }
                )

    # Sort by Session ID and Turn ID
    audit_rows.sort(key=lambda x: (x["Session ID"], x["Turn ID"]))

    if audit_rows:
        os.makedirs(results_dir, exist_ok=True)
        with open(
            os.path.join(results_dir, "manual_audit.csv"), "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(f, fieldnames=audit_rows[0].keys())
            writer.writeheader()
            writer.writerows(audit_rows)

        print(f"Created {os.path.join(results_dir, 'manual_audit.csv')}")


if __name__ == "__main__":
    evaluate()
    sample_audit()
