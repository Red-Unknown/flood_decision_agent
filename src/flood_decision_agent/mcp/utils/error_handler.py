"""MCP 统一错误处理模块

提供统一的错误处理、日志记录和错误响应格式化功能。
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from functools import wraps


class MCPErrorCode(Enum):
    """MCP 错误代码"""
    # 通用错误
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    MISSING_ARGUMENT = "MISSING_ARGUMENT"
    
    # 服务错误
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    SERVICE_TIMEOUT = "SERVICE_TIMEOUT"
    SERVICE_INTERNAL_ERROR = "SERVICE_INTERNAL_ERROR"
    
    # 数据错误
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    DATA_INVALID = "DATA_INVALID"
    DATA_SOURCE_ERROR = "DATA_SOURCE_ERROR"
    
    # 模拟错误
    SIMULATION_FAILED = "SIMULATION_FAILED"
    SIMULATION_TIMEOUT = "SIMULATION_TIMEOUT"
    SIMULATION_CONFIG_ERROR = "SIMULATION_CONFIG_ERROR"
    
    # 视觉检测错误
    VISION_DETECTION_FAILED = "VISION_DETECTION_FAILED"
    IMAGE_NOT_FOUND = "IMAGE_NOT_FOUND"
    MODEL_LOAD_ERROR = "MODEL_LOAD_ERROR"
    
    # 依赖服务错误
    DATA_HUB_ERROR = "DATA_HUB_ERROR"
    HIPIMS_ERROR = "HIPIMS_ERROR"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"


class MCPError(Exception):
    """MCP 基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: MCPErrorCode = MCPErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        service: str = "unknown"
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.service = service
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": False,
            "error": {
                "code": self.code.value,
                "message": self.message,
                "service": self.service,
                "timestamp": self.timestamp,
                "details": self.details
            }
        }
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)


class MCPServiceError(MCPError):
    """MCP 服务错误"""
    
    def __init__(self, message: str, service: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=MCPErrorCode.SERVICE_INTERNAL_ERROR,
            details=details,
            service=service
        )


class MCPDataError(MCPError):
    """MCP 数据错误"""
    
    def __init__(self, message: str, code: MCPErrorCode = MCPErrorCode.DATA_INVALID, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=code,
            details=details,
            service="data"
        )


class MCPSimulationError(MCPError):
    """MCP 模拟错误"""
    
    def __init__(self, message: str, code: MCPErrorCode = MCPErrorCode.SIMULATION_FAILED, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=code,
            details=details,
            service="simulation"
        )


class MCPVisionError(MCPError):
    """MCP 视觉检测错误"""
    
    def __init__(self, message: str, code: MCPErrorCode = MCPErrorCode.VISION_DETECTION_FAILED, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=code,
            details=details,
            service="vision"
        )


# 配置日志记录
logger = logging.getLogger("mcp")
logger.setLevel(logging.INFO)

# 添加控制台处理器
if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(service)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


class MCPLoggerAdapter(logging.LoggerAdapter):
    """MCP 日志适配器，添加服务名称"""
    
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra'].setdefault('service', self.extra.get('service', 'unknown'))
        return msg, kwargs


def get_logger(service: str = "mcp") -> logging.LoggerAdapter:
    """获取带服务名称的日志记录器"""
    return MCPLoggerAdapter(logger, {'service': service})


def handle_error(
    error: Exception,
    service: str = "unknown",
    default_code: MCPErrorCode = MCPErrorCode.UNKNOWN_ERROR
) -> Dict[str, Any]:
    """统一错误处理函数
    
    Args:
        error: 捕获的异常
        service: 服务名称
        default_code: 默认错误代码
        
    Returns:
        格式化的错误响应字典
    """
    log = get_logger(service)
    
    # 如果已经是 MCPError，直接返回
    if isinstance(error, MCPError):
        log.error(f"MCPError: {error.message}")
        return error.to_dict()
    
    # 根据异常类型确定错误代码
    error_code = default_code
    if isinstance(error, FileNotFoundError):
        error_code = MCPErrorCode.DATA_NOT_FOUND
    elif isinstance(error, TimeoutError):
        error_code = MCPErrorCode.SERVICE_TIMEOUT
    elif isinstance(error, ValueError):
        error_code = MCPErrorCode.INVALID_ARGUMENT
    elif isinstance(error, ConnectionError):
        error_code = MCPErrorCode.SERVICE_UNAVAILABLE
    
    # 获取详细的错误信息
    error_traceback = traceback.format_exc()
    
    # 记录错误日志
    log.error(f"Error ({error_code.value}): {str(error)}")
    log.debug(f"Traceback: {error_traceback}")
    
    # 构建错误响应
    error_response = {
        "success": False,
        "error": {
            "code": error_code.value,
            "message": str(error),
            "service": service,
            "timestamp": datetime.now().isoformat(),
            "details": {
                "error_type": type(error).__name__,
                "traceback": error_traceback if _is_debug_mode() else None
            }
        }
    }
    
    return error_response


def error_response(
    message: str,
    code: MCPErrorCode = MCPErrorCode.UNKNOWN_ERROR,
    service: str = "unknown",
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """创建错误响应
    
    Args:
        message: 错误消息
        code: 错误代码
        service: 服务名称
        details: 额外详情
        
    Returns:
        格式化的错误响应字典
    """
    error = MCPError(message, code, details, service)
    return error.to_dict()


def success_response(
    data: Dict[str, Any],
    service: str = "unknown",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """创建成功响应
    
    Args:
        data: 响应数据
        service: 服务名称
        metadata: 元数据
        
    Returns:
        格式化的成功响应字典
    """
    response = {
        "success": True,
        "service": service,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    if metadata:
        response["metadata"] = metadata
    
    return response


def tool_error_handler(service: str = "unknown"):
    """工具函数错误处理装饰器
    
    自动捕获异常并返回统一格式的错误响应。
    
    Args:
        service: 服务名称
        
    Usage:
        @tool_error_handler("hydrology")
        async def my_tool_handler(args):
            # 业务逻辑
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> List[Any]:
            from mcp.types import TextContent
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_dict = handle_error(e, service)
                return [TextContent(
                    type="text",
                    text=json.dumps(error_dict, ensure_ascii=False, indent=2)
                )]
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> List[Any]:
            from mcp.types import TextContent
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_dict = handle_error(e, service)
                return [TextContent(
                    type="text",
                    text=json.dumps(error_dict, ensure_ascii=False, indent=2)
                )]
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def _is_debug_mode() -> bool:
    """检查是否处于调试模式"""
    return os.environ.get("MCP_DEBUG", "false").lower() == "true"


class ErrorBoundary:
    """错误边界上下文管理器
    
    用于包装代码块，统一处理异常。
    
    Usage:
        with ErrorBoundary("hydrology") as boundary:
            result = risky_operation()
            if boundary.success:
                print(result)
    """
    
    def __init__(self, service: str = "unknown", raise_on_error: bool = False):
        self.service = service
        self.raise_on_error = raise_on_error
        self.success = False
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[Exception] = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.error = exc_val
            self.result = handle_error(exc_val, self.service)
            self.success = False
            if self.raise_on_error:
                return False  # 重新抛出异常
            return True  # 吞掉异常
        else:
            self.success = True
        return False
    
    def set_result(self, data: Dict[str, Any]):
        """设置成功结果"""
        self.result = success_response(data, self.service)
        self.success = True


# 导出公共接口
__all__ = [
    "MCPErrorCode",
    "MCPError",
    "MCPServiceError",
    "MCPDataError",
    "MCPSimulationError",
    "MCPVisionError",
    "handle_error",
    "error_response",
    "success_response",
    "tool_error_handler",
    "get_logger",
    "ErrorBoundary",
]