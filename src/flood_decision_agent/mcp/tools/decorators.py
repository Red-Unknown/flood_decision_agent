"""MCP 工具装饰器

提供工具相关的装饰器：
- @auto_write_to_pool: 自动将工具结果写入共享数据池
- @with_logging: 自动记录工具调用日志
- @with_timeout: 添加超时控制
"""

import asyncio
import functools
import time
from typing import Any, Callable, Dict, Optional, TypeVar

from src.flood_decision_agent.mcp.log import get_mcp_logger, ToolCallContext
from src.flood_decision_agent.mcp.log.error_formatter import format_error as format_error_dict
from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps
from mcp.types import TextContent

T = TypeVar('T')


def auto_write_to_pool(
    data_pool_getter: Callable[[], Any],
    key_generator: Optional[Callable[[str, Dict[str, Any]], str]] = None
):
    """自动将工具结果写入共享数据池的装饰器
    
    Args:
        data_pool_getter: 获取数据池实例的函数
        key_generator: 可选的自定义键生成函数
        
    Example:
        @auto_write_to_pool(lambda: get_data_pool())
        async def my_tool(args):
            return {"result": "data"}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            try:
                data_pool = data_pool_getter()
                if data_pool and hasattr(data_pool, 'put') and isinstance(result, dict):
                    tool_name = func.__name__
                    if key_generator:
                        key = key_generator(tool_name, result)
                    else:
                        key = f"mcp_result:{tool_name}"
                    
                    data_pool.put(key, result)
            except Exception:
                pass
            
            return result
        return wrapper
    return decorator


def with_logging(server_name: str):
    """自动记录工具调用日志的装饰器
    
    Args:
        server_name: 服务器名称
        
    Example:
        @with_logging("rainfall")
        async def get_current_rainfall(args):
            return {"data": "result"}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_mcp_logger(server_name)
            tool_name = func.__name__
            
            start_time = time.perf_counter()
            logger.info(f"工具调用开始: {tool_name} | 参数: {args[1] if len(args) > 1 else kwargs}")
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.info(f"工具调用成功: {tool_name} | 耗时: {duration_ms:.2f}ms")
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.error(f"工具调用失败: {tool_name} | 耗时: {duration_ms:.2f}ms | 错误: {e}")
                raise
        return wrapper
    return decorator


def with_standard_error_handling(server_name: str):
    """标准化错误处理的装饰器
    
    Args:
        server_name: 服务器名称
        
    Example:
        @with_standard_error_handling("rainfall")
        async def get_current_rainfall(args):
            return {"data": "result"}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tool_name = func.__name__
            arguments = args[1] if len(args) > 1 else kwargs
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_dict = format_error_dict(e, server_name, tool_name, arguments)
                return [TextContent(
                    type="text",
                    text=fast_json_dumps(error_dict, ensure_ascii=False)
                )]
        return wrapper
    return decorator


def with_timeout(seconds: float, default: Any = None):
    """添加超时控制的装饰器
    
    Args:
        seconds: 超时秒数
        default: 超时后的默认返回值
        
    Example:
        @with_timeout(30.0)
        async def slow_tool(args):
            return await some_async_call()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                return default
        return wrapper
    return decorator


def with_retry(max_retries: int = 3, delay: float = 1.0):
    """添加重试机制的装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
        
    Example:
        @with_retry(max_retries=3, delay=1.0)
        async def unreliable_api_call(args):
            return await api_call()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator


def with_cache(ttl_seconds: int = 300):
    """添加结果缓存的装饰器
    
    Args:
        ttl_seconds: 缓存有效期（秒）
        
    Example:
        @with_cache(ttl_seconds=300)
        async def get_weather(city):
            return await fetch_weather(city)
    """
    def decorator(func: Callable) -> Callable:
        cache: Dict[str, tuple[Any, float]] = {}
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = str(args) + str(kwargs)
            current_time = time.time()
            
            if cache_key in cache:
                cached_result, cached_time = cache[cache_key]
                if current_time - cached_time < ttl_seconds:
                    return cached_result
            
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            return result
        return wrapper
    return decorator


class ToolContext:
    """工具执行上下文
    
    提供工具执行的上下文管理，包括：
    - 参数验证
    - 日志记录
    - 错误处理
    - 数据池写入
    """
    
    def __init__(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        data_pool: Optional[Any] = None
    ):
        self.server_name = server_name
        self.tool_name = tool_name
        self.arguments = arguments
        self.data_pool = data_pool
        self.logger = get_mcp_logger(server_name)
        self._start_time: float = 0
        self._result: Any = None

    def __enter__(self):
        self._start_time = time.perf_counter()
        self.logger.info(
            f"工具调用开始: {self.tool_name} | 参数: {self._mask_sensitive_args(self.arguments)}"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self._start_time) * 1000
        
        if exc_type is not None:
            self.logger.error(
                f"工具调用失败: {self.tool_name} | 耗时: {duration_ms:.2f}ms | 错误: {exc_val}"
            )
        else:
            self.logger.info(
                f"工具调用成功: {self.tool_name} | 耗时: {duration_ms:.2f}ms"
            )
            
            if self.data_pool and self._result:
                self._write_to_pool()
        
        return False

    def _mask_sensitive_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """掩码敏感参数"""
        sensitive_keys = {"api_key", "password", "token", "secret", "key", "auth"}
        masked = {}
        
        for k, v in args.items():
            if k.lower() in sensitive_keys:
                masked[k] = "***"
            else:
                masked[k] = v
                
        return masked

    def _write_to_pool(self):
        """写入数据池"""
        try:
            if hasattr(self.data_pool, 'put'):
                key = f"{self.server_name}:{self.tool_name}"
                self.data_pool.put(key, self._result)
                self.logger.debug(f"结果写入数据池: {key}")
        except Exception as e:
            self.logger.warning(f"写入数据池失败: {e}")

    def set_result(self, result: Any):
        """设置结果"""
        self._result = result

    @property
    def duration_ms(self) -> float:
        """获取执行耗时"""
        if self._start_time:
            return (time.perf_counter() - self._start_time) * 1000
        return 0
