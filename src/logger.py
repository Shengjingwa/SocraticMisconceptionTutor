import json
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

class SessionLogger:
    def __init__(self):
        self.turn_log_path = LOG_DIR / "turn_logs.jsonl"
        self.session_log_path = LOG_DIR / "session_summary.jsonl"

    def log_turn(self, record: Dict[str, Any]) -> None:
        with self.turn_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def log_session(self, record: Dict[str, Any]) -> None:
        with self.session_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def warning(self, msg: str):
        print(f"[WARNING] {msg}")

    def error(self, msg: str):
        print(f"[ERROR] {msg}")

    def info(self, msg: str):
        print(f"[INFO] {msg}")

logger_instance = SessionLogger()
