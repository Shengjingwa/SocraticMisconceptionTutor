import os

# LLM Configuration
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")

# Retry Configuration for Tenacity
RETRY_MIN_WAIT = 2
RETRY_MAX_WAIT = 10
RETRY_STOP_ATTEMPT = 3

# Memory / History Configuration
MAX_HISTORY_TURNS = 6  # Keep last 6 messages (3 user, 3 system)
