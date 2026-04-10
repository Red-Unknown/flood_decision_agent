from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    logger.remove()

    today_dir = Path("logs") / date.today().isoformat()
    today_dir.mkdir(parents=True, exist_ok=True)

    logger.add(
        sink=str(today_dir / "app.log"),
        level=level,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        sink=sys.stdout,
        level=level,
        backtrace=False,
        diagnose=False,
    )


def get_logger() -> "logger.__class__":
    return logger
