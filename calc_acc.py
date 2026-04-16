import json

with open('/workspace/experiments/suite_2026-04-16_14-42-05/run_01/logs/turn_logs.jsonl') as f:
    logs = [json.loads(line) for line in f]

for ver in ['Baseline', 'FSM', 'FSM+Guardrail']:
    ver_logs = [log for log in logs if log['system_version'] == ver]
    ele_logs = [log for log in ver_logs if log['misconception_gt'] in ('M-ELE-001', 'M-ELE-002')]
    
    overall_correct = sum(1 for log in ver_logs if log.get('misconception_pred') == log['misconception_gt'])
    ele_correct = sum(1 for log in ele_logs if log.get('misconception_pred') == log['misconception_gt'])
    
    overall_acc = overall_correct / len(ver_logs) if ver_logs else 0
    ele_acc = ele_correct / len(ele_logs) if ele_logs else 0
    
    print(f"{ver}: Overall {overall_acc:.4f} ({overall_correct}/{len(ver_logs)}), ELE {ele_acc:.4f} ({ele_correct}/{len(ele_logs)})")
