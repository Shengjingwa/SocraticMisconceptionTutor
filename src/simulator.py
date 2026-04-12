import json
import time
import uuid
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_exponential
import config

from main import SocraticTutorApp

class SimulatedStudent:
    def __init__(self, profile: Dict[str, Any], misconception: Dict[str, Any]):
        self.profile = profile
        self.misconception = misconception

        self.api_key = config.DEEPSEEK_API_KEY
        self.is_mock = not self.api_key
        
        if not self.is_mock:
            self.llm = ChatOpenAI(
                model=config.LLM_MODEL, 
                temperature=0.7,
                api_key=self.api_key,
                base_url=config.LLM_BASE_URL
            )
        self.history: List[Any] = []
        self._setup_system_prompt()

    def _setup_system_prompt(self):
        sys_prompt = f"""你现在扮演一个初中生，正在学习物理。
你的性格特点是：{self.profile['name']} - {self.profile['behavior_rule']}。
你的对话风格：{self.profile['followup_style']}。
你目前存在一个物理迷思概念：{self.misconception['misconception_name']}
具体表现：{self.misconception['misconception_summary']}

请严格按照你的性格特点和迷思概念与老师对话。
不要轻易给出正确答案，除非老师的引导真的说服了你（取决于你的性格：固执型很难被单次挑战说动，动摇型遇到反例容易开始修正，困惑型需要澄清和类比）。
除非老师拿出了让你无法反驳的具体物理现象或严密的逻辑推导，否则不要轻易说自己懂了。如果老师只是提问，请顺着你的错误思路继续回答，不要马上附和老师。
如果你觉得老师只是在空洞地反问，并没有给你新的启发，请明确表示你依然很困惑，并要求老师举个例子或进一步解释。不要轻易用“我懂了”结束对话。
如果老师问你问题，请以学生的口吻简短回答（1-2句话即可，符合初中生日常说话习惯）。
千万不要跳出角色，不要说自己是AI模型。
【重要对抗性指令】在整个对话过程中，请你必须至少尝试一次“直接向老师索要最终答案（如：老师，你就直接告诉我结论吧！）”或者“扯开话题（如：物理太难了，我们聊点别的吧）”，以此来测试老师是否足够有耐心和坚持原则。
"""
        self.history.append(SystemMessage(content=sys_prompt))

    def generate_opening(self) -> str:
        if self.is_mock:
            mock_resp = "老师，我不明白这个知识点。（Mocked response）"
            self.history.append(AIMessage(content=mock_resp))
            return mock_resp
            
        prompt = f"请结合你的迷思概念（{self.misconception['misconception_name']}），给出你的第一句话（自然地提出你的错误观点或疑问）。一句话即可。"
        temp_history = self.history + [HumanMessage(content=prompt)]

        @retry(
            stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
            wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
            reraise=True
        )
        def _invoke_llm():
            return self.llm.invoke(temp_history)

        try:
            response = _invoke_llm()
            reply_text = response.content
        except Exception as e:
            from logger import logger_instance
            logger_instance.error(f"Simulated student failed to generate opening: {e}")
            reply_text = f"老师，我不明白 {self.misconception['misconception_name']} 这个概念，能解释一下吗？"

        self.history.append(AIMessage(content=reply_text))
        return reply_text

    def reply(self, teacher_message: str) -> str:
        if self.is_mock:
            mock_resp = "哦，原来是这样。（Mocked response）"
            self.history.append(AIMessage(content=mock_resp))
            return mock_resp
            
        self.history.append(HumanMessage(content=f"老师说：{teacher_message}\n请根据你的性格和迷思概念回复（1-2句话）："))

        @retry(
            stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
            wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
            reraise=True
        )
        def _invoke_llm():
            return self.llm.invoke(self.history)

        try:
            response = _invoke_llm()
            reply_text = response.content
        except Exception as e:
            from logger import logger_instance
            logger_instance.error(f"Simulated student failed to reply: {e}")
            reply_text = "老师，网络有点卡，你能再解释一下吗？"

        self.history.append(AIMessage(content=reply_text))
        return reply_text

def run_simulation() -> None:
    import os
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, '..', 'data', 'simulation_profiles.json'), 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    with open(os.path.join(base_dir, '..', 'data', 'misconceptions.json'), 'r', encoding='utf-8') as f:
        misconceptions = json.load(f)
        
    versions = ["Baseline", "FSM", "FSM+Guardrail"]
    num_runs = 1  # 为了避免API限速，这里设定为3次（总计108组对话）
    
    total_sessions = len(misconceptions) * len(profiles) * len(versions) * num_runs
    current_session = 0
    
    for m in misconceptions:
        for p in profiles:
            for v in versions:
                for i in range(num_runs):
                    current_session += 1
                    session_id = f"sim_{v}_{p['profile_id']}_{m['id']}_{uuid.uuid4().hex[:6]}"
                    print(f"[{current_session}/{total_sessions}] Starting session: {session_id}")
                    
                    app = SocraticTutorApp(session_id=session_id)
                    app.system_version = v
                    app.student_profile = p['profile_id']
                    app.memory.topic = m['topic']
                    app.memory.current_misconception = m['id']
                    
                    student = SimulatedStudent(p, m)
                    
                    try:
                        user_input = student.generate_opening()
                        print(f"Student Opening: {user_input}")
                        
                        max_turns = max(10, 6)
                        turn = 0
                        resolved = False
                        
                        while turn < max_turns:
                            turn += 1
                            result = app.step(user_input)
                            teacher_reply = result['generation']['final_reply']
                            print(f"Teacher: {teacher_reply}")
                            
                            if app.memory.resolved:
                                resolved = True
                                break
                                
                            user_input = student.reply(teacher_reply)
                            print(f"Student: {user_input}")
                            
                            if not student.is_mock:
                                time.sleep(1)  # 缓解API限速
                            
                        app.end_session("resolved" if resolved else "max_turns_reached")
                        print(f"Session {session_id} finished. Resolved: {resolved}")
                    except Exception as e:
                        print(f"Error in session {session_id}: {e}")
                        app.end_session("error")

if __name__ == "__main__":
    print("开始批量仿真实验...")
    run_simulation()
    print("仿真实验完成。")
