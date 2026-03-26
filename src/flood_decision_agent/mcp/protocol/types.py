"""MCP Protocol Types - 核心协议类型定义

定义 MCP 协议中使用的基础数据类型和结构。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union


class MessageType(Enum):
    """MCP 消息类型"""
    REQUEST = auto()
    RESPONSE = auto()
    ERROR = auto()
    NOTIFICATION = auto()


class ErrorCode(Enum):
    """MCP 错误码"""
    SUCCESS = 0
    UNKNOWN_ERROR = 1
    INVALID_REQUEST = 2
    METHOD_NOT_FOUND = 3
    INVALID_PARAMS = 4
    INTERNAL_ERROR = 5
    SERVER_NOT_INITIALIZED = 6
    TIMEOUT = 7
    CONNECTION_ERROR = 8
    TOOL_NOT_FOUND = 9
    TOOL_EXECUTION_ERROR = 10


@dataclass
class MCPToolInfo:
    """MCP 工具信息
    
    Attributes:
        name: 工具名称
        description: 工具描述
        input_schema: 输入参数 JSON Schema
        server_name: 所属服务器名称
    """
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    server_name: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "server_name": self.server_name,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPToolInfo":
        """从字典创建"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            input_schema=data.get("input_schema", {}),
            server_name=data.get("server_name", ""),
        )


@dataclass
class MCPServerInfo:
    """MCP 服务器信息
    
    Attributes:
        name: 服务器名称
        version: 服务器版本
        description: 服务器描述
        tools: 可用工具列表
        status: 服务器状态
    """
    name: str
    version: str = "1.0.0"
    description: str = ""
    tools: List[MCPToolInfo] = field(default_factory=list)
    status: str = "unknown"  # unknown, initializing, ready, error
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tools": [t.to_dict() for t in self.tools],
            "status": self.status,
        }


@dataclass
class ToolInput:
    """工具输入参数
    
    Attributes:
        tool_name: 工具名称
        arguments: 工具参数
        request_id: 请求 ID
    """
    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None


@dataclass
class ToolResult:
    """工具执行结果
    
    Attributes:
        success: 是否成功
        data: 结果数据
        error: 错误信息
        tool_name: 工具名称
        execution_time: 执行时间（毫秒）
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    tool_name: str = ""
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "tool_name": self.tool_name,
            "execution_time": self.execution_time,
        }


@dataclass
class MCPMessage:
    """MCP 基础消息
    
    Attributes:
        message_type: 消息类型
        payload: 消息载荷
        timestamp: 时间戳
        metadata: 元数据
    """
    message_type: MessageType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_type": self.message_type.name,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class MCPRequest:
    """MCP 请求
    
    Attributes:
        method: 请求方法/工具名
        params: 请求参数
        request_id: 请求 ID
        timeout: 超时时间（秒）
    """
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None
    timeout: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "method": self.method,
            "params": self.params,
            "request_id": self.request_id,
            "timeout": self.timeout,
        }


@dataclass
class MCPResponse:
    """MCP 响应
    
    Attributes:
        result: 响应结果
        request_id: 对应请求 ID
        error: 错误信息（如果有）
    """
    result: Any = None
    request_id: Optional[str] = None
    error: Optional["MCPError"] = None
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "result": self.result,
            "request_id": self.request_id,
            "error": self.error.to_dict() if self.error else None,
        }


@dataclass
class MCPError:
    """MCP 错误
    
    Attributes:
        code: 错误码
        message: 错误消息
        data: 附加错误数据
    """
    code: ErrorCode
    message: str
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code.value,
            "message": self.message,
            "data": self.data,
        }
    
    @classmethod
    def from_exception(cls, exc: Exception, code: ErrorCode = ErrorCode.INTERNAL_ERROR) -> "MCPError":
        """从异常创建错误"""
        return cls(
            code=code,
            message=str(exc),
            data={"exception_type": type(exc).__name__},
        )


# 类型别名
MCPPayload = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
