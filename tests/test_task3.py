import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from classifiers import verify_post_test
from langchain_core.messages import HumanMessage, AIMessage

messages = [
    HumanMessage(content="你能用自己的话总结一下吗？"),
    AIMessage(content="嗯，我懂了！")
]

print("Test 1 (No explanation):", verify_post_test("嗯，我懂了！", "M-ELE-001", messages))

messages2 = [
    HumanMessage(content="你能用自己的话总结一下吗？"),
    AIMessage(content="电流在电路里没有被用掉，它只是从电池正极流出来，经过灯泡，然后再回到负极。")
]

print("Test 2 (Good explanation):", verify_post_test("电流在电路里没有被用掉，它只是从电池正极流出来，经过灯泡，然后再回到负极。", "M-ELE-001", messages2))
