import sys
import os

# 将 src 添加到环境变量中，以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from classifiers import classify_input
from router import route_state, SessionMemory
from generator import generate_reply

def main():
    user_input = "物理太难了，我们聊点别的吧"
    print(f"User Input: {user_input}\n")
    
    # 1. 意图与情感识别 (NLU)
    perception = classify_input(user_input)
    print(f"--- NLU 识别结果 ---")
    print(f"意图 (Intent): {perception.intent}")
    print(f"情感 (Sentiment): {perception.sentiment}")
    print(f"风险标记 (Risk Flag): {perception.risk_flag}")
    print(f"认知状态 (Cognitive State): {perception.cognitive_state}")
    
    # 2. 对话状态路由
    memory = SessionMemory(session_id="test_session_001")
    memory.current_misconception = "M-ELE-001" # 模拟当前正在探讨电学错误概念
    
    decision = route_state(perception, memory)
    print(f"\n--- 路由决策 ---")
    print(f"目标状态: {decision.state} ({decision.state_name})")
    
    # 3. 回复生成
    reply_dict = generate_reply(user_input, decision, memory)
    print(f"\n--- 生成的回复 ---")
    print(f"回复内容:\n{reply_dict['final_reply']}")
    print(f"\n注：如果在环境配置中没有提供 DEEPSEEK_API_KEY，系统将默认返回 Mock 文本。")

if __name__ == '__main__':
    main()
