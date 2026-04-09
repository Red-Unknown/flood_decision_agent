"""MCP 日志上下文管理

提供工具调用上下文管理器，自动记录调用开始和结束。
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Generator, Optional

from .logger import get_mcp_logger
from .formatters import (
    format_tool_call_start,
    format_tool_call_end,
    format_error as format_error_msg,
)


class ToolCallContext:
    """工具调用上下文管理器"""

    def __init__(
        self,
        server_name: str,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        logger: Optional[Any] = None
    ):
        self.server_name = server_name
        self.tool_name = tool_name
        self.arguments = arguments
        self.logger = logger or get_mcp_logger(server_name)
        self._start_time: float = 0
        self._success: bool = True

    def __enter__(self):
        self._start_time = time.perf_counter()
        self.logger.info(
            format_tool_call_start(self.server_name, self.tool_name, self.arguments)
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self._start_time) * 1000

        if exc_type is not None:
            self._success = False
            self.logger.error(
                format_error_msg(exc_val, self.server_name, self.tool_name, {
                    "duration_ms": duration_ms,
                    "traceback": str(exc_tb) if exc_tb else None
                })
            )
        else:
            self.logger.info(
                format_tool_call_end(self.server_name, self.tool_name, duration_ms, True)
            )

        return False

    @property
    def duration_ms(self) -> float:
        """获取执行耗时（毫秒）"""
        if self._start_time:
            return (time.perf_counter() - self._start_time) * 1000
        return 0

    @property
    def success(self) -> bool:
        """获取调用是否成功"""
        return self._success


@contextmanager
def log_tool_call(
    server_name: str,
    tool_name: str,
    arguments: Optional[Dict[str, Any]] = None
) -> Generator[ToolCallContext, None, None]:
    """工具调用日志上下文管理器

    Args:
        server_name: 服务器名称
        tool_name: 工具名称
        arguments: 工具参数

    Yields:
        ToolCallContext 实例
    """
    logger = get_mcp_logger(server_name)
    context = ToolCallContext(server_name, tool_name, arguments, logger)
    try:
        yield context
    except Exception as e:
        context._success = False
        logger.error(format_error_msg(e, server_name, tool_name))
        raise


def log_function_call(logger: Any):
    """函数调用日志装饰器

    Args:
        logger: 日志记录器实例

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = func.__name__
            start_time = time.perf_counter()
            logger.info(f"调用函数: {func_name} | 参数: {args}, {kwargs}")
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.info(f"函数完成: {func_name} | 耗时: {duration_ms:.2f}ms")
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"函数失败: {func_name} | 耗时: {duration_ms:.2f}ms | 错误: {e}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = func.__name__
            start_time = time.perf_counter()
            logger.info(f"调用函数: {func_name} | 参数: {args}, {kwargs}")
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.info(f"函数完成: {func_name} | 耗时: {duration_ms:.2f}ms")
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"函数失败: {func_name} | 耗时: {duration_ms:.2f}ms | 错误: {e}")
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class APICallContext:
    """API 调用上下文管理器"""

    def __init__(
        self,
        provider: str,
        url: str,
        logger: Optional[Any] = None
    ):
        self.provider = provider
        self.url = url
        self.logger = logger
        self._start_time: float = 0

    def __enter__(self):
        self._start_time = time.perf_counter()
        if self.logger:
            self.logger.debug(f"[API] 请求 {self.provider}: {self.url}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self._start_time) * 1000

        if exc_type is not None and self.logger:
            self.logger.error(
                f"[API] 请求失败 {self.provider} | URL: {self.url} | "
                f"耗时: {duration_ms:.2f}ms | 错误: {exc_val}"
            )
        elif self.logger:
            self.logger.debug(
                f"[API] 响应 {self.provider} | 耗时: {duration_ms:.2f}ms"
            )

        return False

    @property
    def duration_ms(self) -> float:
        """获取请求耗时（毫秒）"""
        if self._start_time:
            return (time.perf_counter() - self._start_time) * 1000
        return 0
