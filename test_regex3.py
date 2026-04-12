import re

def clean_reply(text: str) -> str:
    if "<think>" in text:
        text = re.sub(r'^.*?<think>', '<think>', text, flags=re.DOTALL)
        text = re.sub(r'<think>.*?(?:</think>|回复：|回答：|回复:|回答:|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'[（\(].*?[）\)]', '', text)
    return text.strip()

tests = [
    "<think>思考</think>回答",
    "<think>未闭合思考\n回答：真正的回答",
    "<think>未闭合思考没有回答",
    "前置废话<think>思考</think>回复:真正的回复"
]

for t in tests:
    print(f"RAW:\n{t}\nCLEAN:\n{clean_reply(t)}\n---")
