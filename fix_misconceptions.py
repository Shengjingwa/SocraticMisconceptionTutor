import json

with open('/workspace/data/misconceptions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    # Rename verification_prompts to verification_questions
    if 'verification_prompts' in item:
        item['verification_questions'] = item.pop('verification_prompts')
    
    # Add preferred_strategies based on the document or notes
    if item['id'] == 'M-ELE-001':
        item['preferred_strategies'] = ["Assumption_Probing", "Consequence_Exploration", "Clarification", "Evidence_Seeking"]
    elif item['id'] == 'M-ELE-002':
        item['preferred_strategies'] = ["Clarification", "Assumption_Probing", "Evidence_Seeking"]
    elif item['id'] == 'M-BUO-001':
        item['preferred_strategies'] = ["Assumption_Probing", "Analogical_Scaffolding"]
    elif item['id'] == 'M-BUO-002':
        item['preferred_strategies'] = ["Clarification", "Evidence_Seeking", "Consequence_Exploration"]

with open('/workspace/data/misconceptions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
