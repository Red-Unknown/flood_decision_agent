"""MCP 日志记录器核心实现

提供统一的日志记录功能，支持日志轮转和分级记录。
"""

import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger as _loguru_logger


class MCPLoggerFactory:
    """MCP 日志记录器工厂类"""

    _loggers: Dict[str, Any] = {}
    _initialized: bool = False
    _log_dir: Path = Path("logs") / "mcp"
    _max_size: int = 10 * 1024 * 1024  # 10MB
    _retention_days: int = 7

    @classmethod
    def initialize(cls, log_dir: Optional[str] = None, max_size: int = 10 * 1024 * 1024, retention_days: int = 7):
        """初始化日志系统

        Args:
            log_dir: 日志目录路径
            max_size: 单个日志文件最大字节数
            retention_days: 日志保留天数
        """
        if cls._initialized:
            return

        cls._log_dir = Path(log_dir) if log_dir else Path("logs") / "mcp"
        cls._max_size = max_size
        cls._retention_days = retention_days

        cls._log_dir.mkdir(parents=True, exist_ok=True)

        _loguru_logger.remove()

        _loguru_logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            backtrace=False,
            diagnose=False,
        )

        cls._initialized = True

    @classmethod
    def get_logger(cls, server_name: str) -> Any:
        """获取指定服务器的日志记录器

        Args:
            server_name: MCP 服务器名称

        Returns:
            配置好的日志记录器实例
        """
        if not cls._initialized:
            cls.initialize()

        if server_name in cls._loggers:
            return cls._loggers[server_name]

        server_log_dir = cls._log_dir / server_name
        server_log_dir.mkdir(parents=True, exist_ok=True)

        log_file = server_log_dir / f"mcp-{server_name}-{date.today().isoformat()}.log"

        log_handler = _loguru_logger.add(
            str(log_file),
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention=f"{cls._retention_days} days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

        bound_logger = _loguru_logger.bind(
            server_name=server_name,
            handler_id=log_handler
        )

        cls._loggers[server_name] = bound_logger
        return bound_logger

    @classmethod
    def cleanup(cls):
        """清理所有日志记录器"""
        for bound_logger in cls._loggers.values():
            try:
                bound_logger.remove()
            except Exception:
                pass
        cls._loggers.clear()


_default_logger_initialized = False


def get_mcp_logger(server_name: str) -> Any:
    """获取 MCP 服务器日志记录器的便捷函数

    Args:
        server_name: MCP 服务器名称

    Returns:
        配置好的日志记录器实例
    """
    global _default_logger_initialized
    if not _default_logger_initialized:
        MCPLoggerFactory.initialize()
        _default_logger_initialized = True
    return MCPLoggerFactory.get_logger(server_name)
