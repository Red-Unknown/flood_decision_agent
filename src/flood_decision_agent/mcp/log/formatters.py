"""MCP 日志格式化器

提供各种日志格式化工具。
"""

from datetime import datetime
from typing import Any, Dict, Optional


def format_tool_call_start(
    server_name: str,
    tool_name: str,
    arguments: Optional[Dict[str, Any]] = None
) -> str:
    """格式化工具调用开始日志消息

    Args:
        server_name: 服务器名称
        tool_name: 工具名称
        arguments: 工具参数

    Returns:
        格式化的日志消息
    """
    args_str = ""
    if arguments:
        args_str = f" | 参数: {arguments}"
    return f"[{server_name}] 工具调用开始: {tool_name}{args_str}"


def format_tool_call_end(
    server_name: str,
    tool_name: str,
    duration_ms: float,
    success: bool = True
) -> str:
    """格式化工具调用结束日志消息

    Args:
        server_name: 服务器名称
        tool_name: 工具名称
        duration_ms: 执行耗时（毫秒）
        success: 是否成功

    Returns:
        格式化的日志消息
    """
    status = "成功" if success else "失败"
    return f"[{server_name}] 工具调用完成: {tool_name} | 状态: {status} | 耗时: {duration_ms:.2f}ms"


def format_api_request(
    provider: str,
    url: str,
    params: Optional[Dict[str, Any]] = None
) -> str:
    """格式化 API 请求日志消息

    Args:
        provider: API 提供商
        url: 请求 URL
        params: 请求参数

    Returns:
        格式化的日志消息
    """
    params_str = ""
    if params:
        params_str = f" | 参数: {params}"
    return f"[API] 请求 {provider}: {url}{params_str}"


def format_api_response(
    provider: str,
    status_code: int,
    duration_ms: float
) -> str:
    """格式化 API 响应日志消息

    Args:
        provider: API 提供商
        status_code: HTTP 状态码
        duration_ms: 请求耗时（毫秒）

    Returns:
        格式化的日志消息
    """
    return f"[API] 响应 {provider} | 状态码: {status_code} | 耗时: {duration_ms:.2f}ms"


def format_error(
    error: Exception,
    server_name: str,
    tool_name: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """格式化错误日志消息

    Args:
        error: 异常对象
        server_name: 服务器名称
        tool_name: 工具名称
        context: 额外上下文信息

    Returns:
        格式化的错误日志消息
    """
    context_str = ""
    if context:
        context_str = f" | 上下文: {context}"
    return f"[{server_name}] 工具调用失败: {tool_name} | 错误类型: {type(error).__name__} | 错误信息: {str(error)}{context_str}"


class ToolCallFormatter:
    """工具调用日志格式化器"""

    @staticmethod
    def format_start(tool_name: str, arguments: Dict[str, Any]) -> str:
        """格式化工具调用开始消息"""
        safe_args = {k: v for k, v in arguments.items() if k not in ("api_key", "password", "token")}
        return format_tool_call_start("server", tool_name, safe_args)

    @staticmethod
    def format_end(tool_name: str, duration_ms: float, success: bool) -> str:
        """格式化工具调用结束消息"""
        return format_tool_call_end("server", tool_name, duration_ms, success)

    @staticmethod
    def format_error(error: Exception, tool_name: str) -> str:
        """格式化错误消息"""
        return format_error(error, "server", tool_name)


class ServerFormatter:
    """服务器日志格式化器"""

    @staticmethod
    def format_startup(server_name: str) -> str:
        """格式化服务器启动消息"""
        return f"[{server_name}] MCP Server 启动"

    @staticmethod
    def format_shutdown(server_name: str) -> str:
        """格式化服务器关闭消息"""
        return f"[{server_name}] MCP Server 关闭"

    @staticmethod
    def format_connection(server_name: str, client_id: str) -> str:
        """格式化客户端连接消息"""
        return f"[{server_name}] 客户端连接: {client_id}"

    @staticmethod
    def format_disconnection(server_name: str, client_id: str) -> str:
        """格式化客户端断开连接消息"""
        return f"[{server_name}] 客户端断开: {client_id}"
