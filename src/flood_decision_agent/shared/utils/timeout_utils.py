"""
超时控制工具模块

提供统一的异步操作超时控制功能，包括装饰器和上下文管理器。
"""

import asyncio
import functools
from typing import Any, Callable, Optional, TypeVar, Union
from contextlib import asynccontextmanager
from datetime import datetime

# 类型变量
T = TypeVar("T")


class TimeoutError(asyncio.TimeoutError):
    """
    自定义超时异常

    提供额外的上下文信息，如超时时间、操作名称等。
    """

    def __init__(
        self,
        message: str = "Operation timed out",
        timeout_seconds: Optional[float] = None,
        operation_name: Optional[str] = None,
    ):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds
        self.operation_name = operation_name
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        parts = [self.args[0]]
        if self.operation_name:
            parts.append(f"operation='{self.operation_name}'")
        if self.timeout_seconds:
            parts.append(f"timeout={self.timeout_seconds}s")
        return " | ".join(parts)


def with_timeout(
    timeout_seconds: float,
    operation_name: Optional[str] = None,
    on_timeout: Optional[Callable] = None,
):
    """
    超时装饰器

    为异步函数添加超时控制。如果函数执行时间超过指定秒数，
    将抛出TimeoutError。

    Args:
        timeout_seconds: 超时时间（秒）
        operation_name: 操作名称（用于错误信息）
        on_timeout: 超时时的回调函数

    Returns:
        装饰器函数

    Example:
        >>> @with_timeout(30.0, operation_name="LLM call")
        ... async def call_llm(prompt: str) -> str:
        ...     # 可能长时间运行的操作
        ...     return await llm_client.generate(prompt)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds,
                )
            except asyncio.TimeoutError as e:
                # 调用超时回调（如果提供）
                if on_timeout:
                    try:
                        on_timeout()
                    except Exception:
                        pass  # 忽略回调中的错误

                # 抛出自定义超时异常
                raise TimeoutError(
                    message=f"Operation '{operation_name or func.__name__}' timed out",
                    timeout_seconds=timeout_seconds,
                    operation_name=operation_name or func.__name__,
                ) from e

        return wrapper

    return decorator


@asynccontextmanager
async def async_timeout(
    timeout_seconds: float,
    operation_name: Optional[str] = None,
    suppress_timeout: bool = False,
):
    """
    异步超时上下文管理器

    在指定时间内执行代码块，超时则抛出TimeoutError。

    Args:
        timeout_seconds: 超时时间（秒）
        operation_name: 操作名称（用于错误信息）
        suppress_timeout: 是否抑制超时异常（返回None而不是抛出）

    Yields:
        None

    Raises:
        TimeoutError: 如果操作超时且suppress_timeout为False

    Example:
        >>> async with async_timeout(10.0, "database query"):
        ...     result = await db.execute_long_query()
        ...     print(result)
    """
    try:
        yield
    except asyncio.TimeoutError as e:
        if not suppress_timeout:
            raise TimeoutError(
                message=f"Operation '{operation_name}' timed out",
                timeout_seconds=timeout_seconds,
                operation_name=operation_name,
            ) from e


class TimeoutManager:
    """
    超时管理器

    用于管理多个操作的超时配置。
    """

    # 默认超时配置（秒）
    DEFAULT_TIMEOUTS = {
        "llm_chat": 60.0,
        "llm_stream": 120.0,
        "mcp_call": 30.0,
        "mcp_connect": 10.0,
        "task_execute": 300.0,
        "chain_generate": 60.0,
        "web_search": 30.0,
        "file_io": 30.0,
    }

    def __init__(self, custom_timeouts: Optional[dict] = None):
        """
        初始化超时管理器

        Args:
            custom_timeouts: 自定义超时配置，将覆盖默认值
        """
        self._timeouts = self.DEFAULT_TIMEOUTS.copy()
        if custom_timeouts:
            self._timeouts.update(custom_timeouts)

    def get_timeout(self, operation: str) -> float:
        """
        获取指定操作的超时时间

        Args:
            operation: 操作名称

        Returns:
            超时时间（秒）
        """
        return self._timeouts.get(operation, 30.0)  # 默认30秒

    def set_timeout(self, operation: str, timeout_seconds: float):
        """
        设置指定操作的超时时间

        Args:
            operation: 操作名称
            timeout_seconds: 超时时间（秒）
        """
        self._timeouts[operation] = timeout_seconds

    def decorator_for(
        self, operation: str, on_timeout: Optional[Callable] = None
    ) -> Callable:
        """
        获取指定操作的超时装饰器

        Args:
            operation: 操作名称
            on_timeout: 超时回调函数

        Returns:
            超时装饰器
        """
        timeout = self.get_timeout(operation)
        return with_timeout(
            timeout_seconds=timeout,
            operation_name=operation,
            on_timeout=on_timeout,
        )

    @asynccontextmanager
    async def context_for(
        self, operation: str, suppress_timeout: bool = False
    ):
        """
        获取指定操作的超时上下文管理器

        Args:
            operation: 操作名称
            suppress_timeout: 是否抑制超时异常

        Yields:
            None
        """
        timeout = self.get_timeout(operation)
        async with async_timeout(
            timeout_seconds=timeout,
            operation_name=operation,
            suppress_timeout=suppress_timeout,
        ):
            yield


# 全局超时管理器实例
default_timeout_manager = TimeoutManager()


def get_timeout(operation: str) -> float:
    """
    获取默认超时时间

    Args:
        operation: 操作名称

    Returns:
        超时时间（秒）
    """
    return default_timeout_manager.get_timeout(operation)


def set_timeout(operation: str, timeout_seconds: float):
    """
    设置默认超时时间

    Args:
        operation: 操作名称
        timeout_seconds: 超时时间（秒）
    """
    default_timeout_manager.set_timeout(operation, timeout_seconds)


async def run_with_timeout(
    coro: Any,
    timeout_seconds: float,
    operation_name: Optional[str] = None,
) -> Any:
    """
    在指定超时时间内运行协程

    Args:
        coro: 要运行的协程
        timeout_seconds: 超时时间（秒）
        operation_name: 操作名称

    Returns:
        协程的返回值

    Raises:
        TimeoutError: 如果超时

    Example:
        >>> result = await run_with_timeout(
        ...     fetch_data(),
        ...     timeout_seconds=10.0,
        ...     operation_name="fetch data"
        ... )
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError as e:
        raise TimeoutError(
            message=f"Operation '{operation_name}' timed out",
            timeout_seconds=timeout_seconds,
            operation_name=operation_name,
        ) from e


class RetryWithTimeout:
    """
    带超时的重试机制

    在超时后自动重试指定次数。
    """

    def __init__(
        self,
        timeout_seconds: float,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        operation_name: Optional[str] = None,
    ):
        """
        初始化重试配置

        Args:
            timeout_seconds: 每次尝试的超时时间
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
            operation_name: 操作名称
        """
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.operation_name = operation_name

    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        执行带重试的函数

        Args:
            func: 要执行的异步函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数返回值

        Raises:
            TimeoutError: 如果所有重试都失败
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                return await run_with_timeout(
                    func(*args, **kwargs),
                    timeout_seconds=self.timeout_seconds,
                    operation_name=f"{self.operation_name} (attempt {attempt + 1}/{self.max_retries})",
                )
            except TimeoutError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        # 所有重试都失败
        raise TimeoutError(
            message=f"Operation '{self.operation_name}' failed after {self.max_retries} attempts",
            timeout_seconds=self.timeout_seconds,
            operation_name=self.operation_name,
        ) from last_error


if __name__ == "__main__":
    # 测试代码
    async def test_timeout():
        print("Testing timeout utilities...")

        # 测试装饰器
        @with_timeout(1.0, operation_name="slow operation")
        async def slow_operation():
            await asyncio.sleep(2.0)
            return "completed"

        try:
            await slow_operation()
            print("[ERR] Should have timed out")
        except TimeoutError as e:
            print(f"[OK] Decorator timeout: {e}")

        # 测试上下文管理器
        try:
            async with async_timeout(1.0, "context test"):
                await asyncio.sleep(2.0)
            print("[ERR] Should have timed out")
        except TimeoutError as e:
            print(f"[OK] Context timeout: {e}")

        # 测试超时管理器
        manager = TimeoutManager()
        print(f"[OK] LLM timeout: {manager.get_timeout('llm_chat')}s")

        # 测试正常执行
        @with_timeout(2.0)
        async def fast_operation():
            await asyncio.sleep(0.5)
            return "success"

        result = await fast_operation()
        print(f"[OK] Fast operation: {result}")

        print("\nAll tests passed!")

    asyncio.run(test_timeout())
