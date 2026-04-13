import os
import sys
from pathlib import Path

# 添加项目根目录到 sys.path，以便导入 src 模块
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 设置 API 密钥
dashscope_api_key = os.environ.get("DASHSCOPE_API_KEY")
if not dashscope_api_key:
    raise ValueError("Missing DASHSCOPE_API_KEY environment variable.")

os.environ["LLM_BASE_URL"] = os.environ.get("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
os.environ["TUTOR_MODEL"] = os.environ.get("TUTOR_MODEL", "qwen-plus")
os.environ["JUDGE_MODEL"] = os.environ.get("JUDGE_MODEL", "deepseek-chat")

from src.main import SocraticTutorApp

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
    
    # Generate and print the learning report
    print("\nGenerating learning report...")
    from src.generator import generate_learning_report
    report = generate_learning_report(app.memory)
    print("\n========== 学习报告 ==========")
    print(report)
    print("=============================\n")

if __name__ == "__main__":
    main()
