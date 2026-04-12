import json
from pathlib import Path
from typing import Any, Dict
import logging
from logging.handlers import RotatingFileHandler

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

class SessionLogger:
    def __init__(self):
        self.turn_log_path = LOG_DIR / "turn_logs.jsonl"
        self.session_log_path = LOG_DIR / "session_summary.jsonl"
        
        self.logger = logging.getLogger("SessionLogger")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            log_file = LOG_DIR / "app.log"
            handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log_turn(self, record: Dict[str, Any]) -> None:
        with self.turn_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def log_session(self, record: Dict[str, Any]) -> None:
        with self.session_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def info(self, msg: str):
        self.logger.info(msg)

logger_instance = SessionLogger()
