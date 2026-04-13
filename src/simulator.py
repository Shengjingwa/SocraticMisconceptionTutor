import asyncio
import json
import time
import uuid
from pathlib import Path
import sys
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_exponential

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import config

from main import SocraticTutorApp

class SimulatedStudent:
    def __init__(self, profile: Dict[str, Any], misconception: Dict[str, Any]):
        self.profile = profile
        self.misconception = misconception

        self.api_key = config.DASHSCOPE_API_KEY
        self.is_mock = not self.api_key
        
        if not self.is_mock:
            import copy
            kwargs = copy.deepcopy(config.DEFAULT_LLM_KWARGS)
            if "extra_body" in kwargs and "enable_thinking" in kwargs["extra_body"]:
                kwargs["extra_body"]["enable_thinking"] = False
            else:
                kwargs.setdefault("extra_body", {})["enable_thinking"] = False

            self.llm = config.get_tutor_llm(
                temperature=0.7,
                **kwargs
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
            raise e

        self.history.append(AIMessage(content=reply_text))
        return reply_text

    async def areply(self, teacher_message: str) -> str:
        if self.is_mock:
            mock_resp = "哦，原来是这样。（Mocked response）"
            self.history.append(AIMessage(content=mock_resp))
            return mock_resp
            
        self.history.append(HumanMessage(content=f"老师说：{teacher_message}\n请根据你的性格和迷思概念回复（1-2句话）："))

        temp_history = [self.history[0]] + self.history[-(config.MAX_HISTORY_TURNS):] if len(self.history) > config.MAX_HISTORY_TURNS + 1 else self.history

        @retry(
            stop=stop_after_attempt(config.RETRY_STOP_ATTEMPT),
            wait=wait_exponential(multiplier=1, min=config.RETRY_MIN_WAIT, max=config.RETRY_MAX_WAIT),
            reraise=True
        )
        async def _invoke_llm():
            return await self.llm.ainvoke(temp_history)

        try:
            response = await _invoke_llm()
            reply_text = response.content
        except Exception as e:
            from logger import logger_instance
            logger_instance.error(f"Simulated student failed to reply: {e}")
            raise e

        self.history.append(AIMessage(content=reply_text))
        return reply_text

async def run_single_session(v, m, p, i, sem):
    from logger import logger_instance
    async with sem:
        session_id = f"sim_{v}_{p['profile_id']}_{m['id']}_{uuid.uuid4().hex[:6]}"
        logger_instance.info(f"[{session_id}] Starting session")
        
        app = SocraticTutorApp(session_id=session_id)
        app.system_version = v
        app.student_profile = p['profile_id']
        app.memory.topic = m['topic']
        app.memory.current_misconception = m['id']
        app.misconception_init = m['id']
        
        student = SimulatedStudent(p, m)
        
        try:
            user_input = student.generate_opening()
            logger_instance.info(f"[{session_id}] Student Opening: {user_input}")
            
            import os
            max_turns = int(os.getenv("SIMULATION_MAX_TURNS", "10"))
            turn = 0
            resolved = False
            
            while turn < max_turns:
                turn += 1
                result = await app.astep(user_input)
                teacher_reply = result['generation']['final_reply']
                logger_instance.info(f"[{session_id}] Teacher: {teacher_reply}")
                
                if getattr(app, "abnormal_end_flag", False):
                    raise Exception("Tutor agent encountered an error")

                if app.memory.resolved:
                    resolved = True
                    break
                    
                user_input = await student.areply(teacher_reply)
                logger_instance.info(f"[{session_id}] Student: {user_input}")
                
            app.end_session("resolved" if resolved else "max_turns_reached")
            logger_instance.info(f"[{session_id}] Session finished. Resolved: {resolved}")
        except Exception as e:
            logger_instance.error(f"[{session_id}] Error in session: {e}")
            app.abnormal_end_flag = True
            app.end_session("error")

async def run_simulation() -> None:
    import os
    base_dir = os.path.dirname(__file__)
    
    # 清理旧日志文件，避免污染
    logs_dir = os.path.join(base_dir, '..', 'logs')
    for log_file in ['turn_logs.jsonl', 'session_summary.jsonl']:
        log_path = os.path.join(logs_dir, log_file)
        if os.path.exists(log_path):
            os.remove(log_path)
            
    with open(os.path.join(base_dir, '..', 'data', 'simulation_profiles.json'), 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    with open(os.path.join(base_dir, '..', 'data', 'misconceptions.json'), 'r', encoding='utf-8') as f:
        misconceptions = json.load(f)
        
    versions = ["Baseline", "FSM", "FSM+Guardrail"]
    num_runs = 3  # 为了避免API限速，这里设定为3次（总计108组对话）

    if os.getenv("SIMULATION_SMOKE") == "1":
        misconceptions = misconceptions[:1]
        profiles = profiles[:1]
        versions = versions[:1]
        num_runs = 1
    
    sem = asyncio.Semaphore(config.SIMULATION_CONCURRENCY)
    tasks = []
    
    for m in misconceptions:
        for p in profiles:
            for v in versions:
                for i in range(num_runs):
                    tasks.append(run_single_session(v, m, p, i, sem))
                    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("开始批量仿真实验...")
    asyncio.run(run_simulation())
    print("仿真实验完成。")
