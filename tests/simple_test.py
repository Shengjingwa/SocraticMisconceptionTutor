import os
import sys
from pathlib import Path

# 添加项目根目录到 sys.path，以便导入 src 模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# 设置 DeepSeek API 密钥
os.environ["DEEPSEEK_API_KEY"] = "sk-b8ad0a83bb8e4083bebd65be5645e7df"

from main import SocraticTutorApp

def main():
    print("Initializing SocraticTutorApp...")
    app = SocraticTutorApp(session_id="test_session_001", topic="物理：电路基础")
    
    test_inputs = [
        "为什么灯泡会发光？",
        "如果我只把灯泡连在电池正极，它会亮吗？"
    ]
    
    for user_input in test_inputs:
        print(f"\nUser: {user_input}")
        result = app.step(user_input)
        
        reply = result.get('generation', {}).get('final_reply', '')
        print(f"System: {reply}")
        
        # 检查是否返回了默认的错误信息
        if "抱歉，系统遇到了一些问题" in reply:
            print("\nError detected in generation!")
            sys.exit(1)
            
    app.end_session("test_completed")
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()
