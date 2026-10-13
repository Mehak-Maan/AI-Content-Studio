import logging
import sys
from datetime import datetime, timezone
from typing import Callable, Optional, List

# Custom color log formatter for terminal
class AgentFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
        "RESET": "\033[0m"
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        log_time = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        record.msg = f"{color}[{record.levelname}]{reset} [{log_time}] {record.msg}"
        return super().format(record)

# In-memory log buffer for streaming to web client
_recent_logs: List[dict] = []
_log_listeners: List[Callable[[dict], None]] = []

def add_log_listener(listener: Callable[[dict], None]):
    _log_listeners.append(listener)

def remove_log_listener(listener: Callable[[dict], None]):
    if listener in _log_listeners:
        _log_listeners.remove(listener)

def broadcast_agent_log(agent_name: str, message: str, level: str = "INFO", project_id: Optional[str] = None):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "message": message,
        "level": level,
        "project_id": project_id
    }
    _recent_logs.append(log_entry)
    if len(_recent_logs) > 500:
        _recent_logs.pop(0)
    for listener in _log_listeners:
        try:
            listener(log_entry)
        except Exception:
            pass

def setup_logger(name: str = "ai_studio") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(AgentFormatter("%(message)s"))
        logger.addHandler(handler)
    return logger

logger = setup_logger()
