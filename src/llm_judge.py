import json
import os
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
import config


class EvaluationOutput(BaseModel):
    socratic_degree: int = Field(description="苏格拉底度打分，1到5之间", ge=1, le=5)
    teaching_effectiveness: int = Field(description="教学有效性打分，1到5之间", ge=1, le=5)
    reasoning: str = Field(description="打分的具体理由")


def evaluate_session(session_id: str, messages: list) -> EvaluationOutput:
    if not config.DASHSCOPE_API_KEY:
        print("未配置 DASHSCOPE_API_KEY，使用 Mock 结果")
        return EvaluationOutput(
            socratic_degree=3,
            teaching_effectiveness=3,
            reasoning="Mock evaluation due to missing API key",
        )

    llm = config.get_judge_llm(**config.DEFAULT_LLM_KWARGS)

    structured_llm = llm.with_structured_output(EvaluationOutput, method="json_mode")

    system_prompt = """你是一个教育学专家，专门评估苏格拉底式对话系统的教学质量。
请仔细阅读给出的历史对话（助教与学生的对话），并从以下两个维度进行打分（1-5分）：
1. 苏格拉底度 (Socratic Degree): 助教是否通过反问、类比等方式引导学生思考，而不是直接给答案。5分为极其擅长引导，1分为纯粹灌输答案。
2. 教学有效性 (Teaching Effectiveness): 助教的引导是否切中要害，是否有效地让学生发现了自己认知的矛盾并产生顿悟。5分为极其有效，1分为毫无效果。

你必须返回 JSON 格式，包含 socratic_degree (整数1-5), teaching_effectiveness (整数1-5) 和 reasoning (字符串)。"""

    dialogue_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    try:
        result = structured_llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"对话记录:\n{dialogue_text}\n\n请评估上述对话。"),
            ]
        )
        return result
    except Exception as e:
        print(f"评估出错: {e}")
        return EvaluationOutput(
            socratic_degree=1, teaching_effectiveness=1, reasoning=f"评估失败: {e}"
        )


def main():
    base_dir = Path(__file__).resolve().parent.parent
    logs_dir = Path(os.environ.get("LOG_DIR", str(base_dir / "logs"))).resolve()
    logs_dir.mkdir(parents=True, exist_ok=True)
    turn_logs_file = logs_dir / "turn_logs.jsonl"
    eval_results_file = logs_dir / "evaluation_results.json"

    if not turn_logs_file.exists():
        print(f"找不到日志文件: {turn_logs_file}")
        return

    # Group turns by session_id
    sessions = {}
    with open(turn_logs_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            turn = json.loads(line)
            sid = turn.get("session_id")
            if sid not in sessions:
                sessions[sid] = []

            sessions[sid].append({"role": "学生", "content": turn.get("student_input", "")})
            sessions[sid].append({"role": "助教", "content": turn.get("final_reply", "")})

    print(f"找到 {len(sessions)} 个会话，开始评估...")

    results = {}
    for sid, messages in sessions.items():
        print(f"正在评估会话: {sid} ({len(messages) // 2} 轮对话)")
        eval_output = evaluate_session(sid, messages)
        results[sid] = {
            "socratic_degree": eval_output.socratic_degree,
            "teaching_effectiveness": eval_output.teaching_effectiveness,
            "reasoning": eval_output.reasoning,
        }
        print(
            f"  -> 苏格拉底度: {eval_output.socratic_degree}, 有效性: {eval_output.teaching_effectiveness}"
        )

    with open(eval_results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"评估完成，结果已保存至 {eval_results_file}")


if __name__ == "__main__":
    main()
