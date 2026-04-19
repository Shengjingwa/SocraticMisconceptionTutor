import os

# LLM Configuration
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
# 为了兼容以前的代码，如果没设置 DASHSCOPE，可以回退找 DEEPSEEK
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not DASHSCOPE_API_KEY and DEEPSEEK_API_KEY:
    DASHSCOPE_API_KEY = DEEPSEEK_API_KEY

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

TUTOR_MODEL = os.environ.get("TUTOR_MODEL", "qwen3.6-plus")
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "deepseek-v3.2")

# Legacy fallback for older code
LLM_MODEL = os.environ.get("LLM_MODEL", TUTOR_MODEL)

# Default kwargs for ChatOpenAI
DEFAULT_LLM_KWARGS = {"model_kwargs": {}, "extra_body": {"enable_thinking": False}}

# Retry Configuration for Tenacity
RETRY_MIN_WAIT = 2
RETRY_MAX_WAIT = 10
RETRY_STOP_ATTEMPT = 3

# Memory / History Configuration
MAX_HISTORY_TURNS = int(os.environ.get("MAX_HISTORY_TURNS", "6"))
SIMULATION_CONCURRENCY = int(os.environ.get("SIMULATION_CONCURRENCY", "6"))

from langchain_openai import ChatOpenAI


def get_tutor_llm(**kwargs):
    dashscope_llm = ChatOpenAI(
        model=TUTOR_MODEL, base_url=LLM_BASE_URL, api_key=DASHSCOPE_API_KEY, **kwargs
    )

    return dashscope_llm


def get_judge_llm(**kwargs):
    return ChatOpenAI(model=JUDGE_MODEL, base_url=LLM_BASE_URL, api_key=DASHSCOPE_API_KEY, **kwargs)
