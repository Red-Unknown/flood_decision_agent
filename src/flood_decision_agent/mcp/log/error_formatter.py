"""MCP 错误格式化工具

提供标准化的错误格式生成功能。
"""

import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class MCPError:
    """MCP 错误数据结构"""
    success: bool = False
    error: str = ""
    error_type: str = ""
    timestamp: str = ""
    server_name: str = ""
    tool_name: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)

    @classmethod
    def from_exception(
        cls,
        exception: Exception,
        server_name: str,
        tool_name: str,
        details: Optional[Dict[str, Any]] = None
    ) -> "MCPError":
        """从异常创建 MCPError

        Args:
            exception: 异常对象
            server_name: 服务器名称
            tool_name: 工具名称
            details: 额外详情

        Returns:
            MCPError 实例
        """
        return cls(
            success=False,
            error=str(exception),
            error_type=type(exception).__name__,
            timestamp=datetime.now().isoformat(),
            server_name=server_name,
            tool_name=tool_name,
            details=details or {}
        )


def format_error(
    error: Exception,
    server_name: str,
    tool_name: str,
    arguments: Optional[Dict[str, Any]] = None,
    include_traceback: bool = False
) -> Dict[str, Any]:
    """格式化错误为标准 JSON 格式

    Args:
        error: 异常对象
        server_name: 服务器名称
        tool_name: 工具名称
        arguments: 工具参数（可选，用于调试）
        include_traceback: 是否包含堆栈跟踪

    Returns:
        标准化的错误字典
    """
    result = {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "timestamp": datetime.now().isoformat(),
        "server_name": server_name,
        "tool_name": tool_name,
    }

    details = {}
    if arguments:
        safe_args = _sanitize_arguments(arguments)
        details["arguments"] = safe_args

    if include_traceback:
        details["traceback"] = traceback.format_exc()

    if details:
        result["details"] = details

    return result


def _sanitize_arguments(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """清理敏感参数

    Args:
        arguments: 原始参数字典

    Returns:
        清理后的参数字典
    """
    sensitive_keys = {"api_key", "password", "token", "secret", "key", "auth"}
    sanitized = {}

    for key, value in arguments.items():
        if key.lower() in sensitive_keys:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_arguments(value)
        elif isinstance(value, list):
            sanitized[key] = [
                _sanitize_arguments(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def create_error_response(
    error: Exception,
    server_name: str,
    tool_name: str,
    arguments: Optional[Dict[str, Any]] = None
) -> str:
    """创建错误响应 JSON 字符串

    Args:
        error: 异常对象
        server_name: 服务器名称
        tool_name: 工具名称
        arguments: 工具参数

    Returns:
        JSON 格式的错误响应字符串
    """
    from flood_decision_agent.shared.utils.json_utils import fast_json_dumps
    return fast_json_dumps(
        format_error(error, server_name, tool_name, arguments),
        ensure_ascii=False,
        indent=2
    )


class MCPErrorBuilder:
    """MCP 错误构建器"""

    def __init__(self, server_name: str, tool_name: str):
        self._server_name = server_name
        self._tool_name = tool_name
        self._error: Optional[Exception] = None
        self._details: Dict[str, Any] = {}
        self._arguments: Optional[Dict[str, Any]] = None

    def with_exception(self, error: Exception) -> "MCPErrorBuilder":
        """设置异常"""
        self._error = error
        return self

    def with_details(self, **kwargs) -> "MCPErrorBuilder":
        """添加详情"""
        self._details.update(kwargs)
        return self

    def with_arguments(self, arguments: Dict[str, Any]) -> "MCPErrorBuilder":
        """设置参数"""
        self._arguments = arguments
        return self

    def build(self) -> Dict[str, Any]:
        """构建错误字典"""
        error = self._error or RuntimeError("Unknown error")
        result = format_error(error, self._server_name, self._tool_name, self._arguments)

        if self._details:
            if "details" not in result:
                result["details"] = {}
            result["details"].update(self._details)

        return result

    def build_json(self) -> str:
        """构建错误 JSON 字符串"""
        from flood_decision_agent.shared.utils.json_utils import fast_json_dumps
        return fast_json_dumps(self.build(), ensure_ascii=False, indent=2)
