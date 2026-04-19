import json
import logging
import os
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = Path(os.environ.get("LOG_DIR", str(BASE_DIR / "logs"))).resolve()
LOG_DIR.mkdir(parents=True, exist_ok=True)


class SessionLogger:
    def __init__(self):
        self.turn_log_path = LOG_DIR / "turn_logs.jsonl"
        self.session_log_path = LOG_DIR / "session_summary.jsonl"
        self.lock = threading.Lock()

        self.logger = logging.getLogger("SessionLogger")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            log_file = LOG_DIR / "app.log"
            handler = RotatingFileHandler(
                log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
            )
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

            if os.getenv("SILENT_CONSOLE") != "1":
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)

    def log_turn(self, record: Dict[str, Any]) -> None:
        with self.lock:
            with self.turn_log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def log_session(self, record: Dict[str, Any]) -> None:
        with self.lock:
            with self.session_log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def info(self, msg: str):
        self.logger.info(msg)


logger_instance = SessionLogger()
