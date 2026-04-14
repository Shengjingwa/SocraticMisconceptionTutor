from src.router import apply_transition_rules, SessionMemory, PerceptionResult

m = SessionMemory(session_id="123")
p = PerceptionResult(intent="ask", cognitive_state="认知僵局")

# Test 1: Stuck in S7
m.recent_states = ["S5", "S7", "S7"]
target = "S7"
new_target = apply_transition_rules(target, p, m)
print(f"Target: {target} -> {new_target} (Expected: S8)")

# Test 2: Stuck in S4
m.recent_states = ["S4", "S4"]
target = "S4"
new_target = apply_transition_rules(target, p, m)
print(f"Target: {target} -> {new_target} (Expected: S5)")
