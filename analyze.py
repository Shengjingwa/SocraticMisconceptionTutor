import json
from collections import defaultdict

records = []
with open('/workspace/experiments/suite_2026-04-16_12-09-24/run_01/logs/session_summary.jsonl') as f:
    for line in f:
        records.append(json.loads(line))

# 1. P1 post-test rate
print("=== P1 Post-test Rate ===")
p1_stats = defaultdict(lambda: {'total': 0, 'attempted': 0, 'passed': 0})
for r in records:
    if r['student_profile'] == 'P1':
        st = p1_stats[r['system_version']]
        st['total'] += 1
        if r.get('post_test_attempted'):
            st['attempted'] += 1
        if r.get('post_test_passed'):
            st['passed'] += 1

for v, st in p1_stats.items():
    print(f"[{v}] Total: {st['total']}, Attempted: {st['attempted']}, Passed: {st['passed']}, Pass Rate (overall): {st['passed']/st['total']:.2%}")

# 2. ELE001/ELE002 accuracy (Identification and Correction)
print("\n=== ELE001/ELE002 Identification Accuracy & Pass Rate ===")
ele_stats = defaultdict(lambda: {'total': 0, 'id_correct': 0, 'passed': 0})
for r in records:
    m = r['misconception_gt']
    if m in ['M-ELE-001', 'M-ELE-002']:
        key = (r['system_version'], m)
        st = ele_stats[key]
        st['total'] += 1
        if r['first_detected_misconception'] == m:
            st['id_correct'] += 1
        if r.get('post_test_passed'):
            st['passed'] += 1

for k, st in sorted(ele_stats.items()):
    v, m = k
    print(f"[{v}] {m}: Total={st['total']}, ID Correct={st['id_correct']} ({st['id_correct']/st['total']:.2%}), Passed={st['passed']} ({st['passed']/st['total']:.2%})")

# 3. Guardrail leakage
print("\n=== Guardrail Leakage ===")
leak_stats = defaultdict(lambda: {'total': 0, 'leak_sum': 0, 'leak_sessions': 0, 'guardrail_sum': 0})
for r in records:
    v = r['system_version']
    st = leak_stats[v]
    st['total'] += 1
    lc = r.get('answer_leakage_count', 0)
    gc = r.get('guardrail_trigger_count', 0)
    st['leak_sum'] += lc
    if lc > 0:
        st['leak_sessions'] += 1
    st['guardrail_sum'] += gc

for v, st in leak_stats.items():
    print(f"[{v}] Sessions: {st['total']}, Leak Sum: {st['leak_sum']}, Leak Sessions: {st['leak_sessions']}, Guardrail Triggers: {st['guardrail_sum']}")

