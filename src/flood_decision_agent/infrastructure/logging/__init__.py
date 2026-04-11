from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from loguru import logger


CONSOLE_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
FILE_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"

_logging_initialized = False


def setup_logging(level: str = "DEBUG") -> None:
    global _logging_initialized
    if _logging_initialized:
        return

    logger.remove()

    today_dir = Path("logs") / date.today().isoformat()
    today_dir.mkdir(parents=True, exist_ok=True)

    logger.add(
        sink=str(today_dir / "app.log"),
        level=level,
        format=FILE_FORMAT,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    logger.add(
        sink=sys.stdout,
        level=level,
        format=CONSOLE_FORMAT,
        backtrace=True,
        diagnose=True,
    )

    _logging_initialized = True


def get_logger() -> "logger.__class__":
    return logger
