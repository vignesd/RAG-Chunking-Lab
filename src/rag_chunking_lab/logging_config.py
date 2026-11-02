
"""Logging setup for RAG Chunking Lab."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Configuration defaults
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"
DEFAULT_LEVEL = "INFO"


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that transforms standard log records into 
    structured JSON strings for observability platforms (Datadog, Loki, etc.).
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Safely fetch 'props' using getattr to prevent type checker warnings
        props = getattr(record, "props", None)
        if isinstance(props, dict):
            log_data.update(props)

        return json.dumps(log_data)


def get_log_level() -> int:
    """Safely parse log level from environment with a fallback."""
    level_str = os.environ.get("LOGLEVEL", DEFAULT_LEVEL).upper()
    level = getattr(logging, level_str, None)
    if not isinstance(level, int):
        return logging.INFO
    return level


def setup_logging() -> None:
    """
    Configure enterprise-grade logging with rotating files, 
    optional JSON production format, and clean third-party management.
    """
    root_logger = logging.getLogger()
    log_level = get_log_level()
    root_logger.setLevel(log_level)

    # Prevent duplicate handlers if setup_logging() is called multiple times
    if root_logger.handlers:
        root_logger.handlers.clear()

    # Define standard human-readable format for local development
    use_json_logs = os.getenv("ENABLE_JSON_LOGGING", "false").lower() in {
        "true", "1", "yes", "on"}
    if use_json_logs:
        dev_formatter = JSONFormatter()
    else:
        dev_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    # 1. Console Handler (Standard Output)
    enable_console = os.getenv("ENABLE_CONSOLE_LOGGING", "true").lower() in {
        "true", "1", "yes", "on"}
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(dev_formatter)
        root_logger.addHandler(console_handler)

    # 2. File Handler (Rotating log files to prevent disk overflow)
    enable_file = os.getenv("ENABLE_FILE_LOGGING", "false").lower() in {
        "true", "1", "yes", "on"}
    if enable_file:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,               # Keep up to 5 archive files
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(dev_formatter)
        root_logger.addHandler(file_handler)

    # 3. Quiet overly chatty third-party libraries in development
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpx2").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Factory function to get a named logger respecting project namespace.
    Usage: logger = get_logger(__name__)
    """
    return logging.getLogger(name)
