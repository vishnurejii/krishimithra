"""
Structured logger for KrishiMitra AI.
Provides clean console output and persistent file logging.
"""

import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from core.config import LOG_DIR, LOG_LEVEL

class ISOFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        return dt.isoformat()

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # Console Handler (safe against UnicodeEncodeError on Windows cp1252 consoles)
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(level)
    c_fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%H:%M:%S")
    c_handler.setFormatter(c_fmt)
    logger.addHandler(c_handler)

    # File Handler
    log_file = LOG_DIR / "krishimitra.log"
    f_handler = logging.FileHandler(log_file, encoding="utf-8")
    f_handler.setLevel(logging.DEBUG)
    f_fmt = ISOFormatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}')
    f_handler.setFormatter(f_fmt)
    logger.addHandler(f_handler)

    return logger
