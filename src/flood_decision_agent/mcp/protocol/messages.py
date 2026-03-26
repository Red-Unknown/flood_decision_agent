"""MCP Protocol Messages - 消息处理工具

提供 MCP 消息的创建、解析和验证功能。
"""

import json
import uuid
from typing import Any, Dict, Optional, Union

from flood_decision_agent.mcp.protocol.types import (
    MCPError,
    MCPMessage,
    MCPRequest,
    MCPResponse,
    MessageType,
    ErrorCode,
)


def generate_request_id() -> str:
    """生成唯一请求 ID"""
    return str(uuid.uuid4())[:8]


def create_request(
    method: str,
    params: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
    timeout: Optional[float] = None,
) -> MCPRequest:
    """创建 MCP 请求
    
    Args:
        method: 请求方法/工具名
        params: 请求参数
        request_id: 请求 ID（可选，自动生成）
        timeout: 超时时间
        
    Returns:
        MCPRequest 实例
    """
    return MCPRequest(
        method=method,
        params=params or {},
        request_id=request_id or generate_request_id(),
        timeout=timeout,
    )


def create_response(
    result: Any,
    request_id: Optional[str] = None,
) -> MCPResponse:
    """创建 MCP 响应
    
    Args:
        result: 响应结果
        request_id: 对应请求 ID
        
    Returns:
        MCPResponse 实例
    """
    return MCPResponse(
        result=result,
        request_id=request_id,
    )


def create_error(
    message: str,
    code: ErrorCode = ErrorCode.INTERNAL_ERROR,
    data: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> MCPResponse:
    """创建错误响应
    
    Args:
        message: 错误消息
        code: 错误码
        data: 附加错误数据
        request_id: 对应请求 ID
        
    Returns:
        包含错误的 MCPResponse 实例
    """
    error = MCPError(
        code=code,
        message=message,
        data=data,
    )
    return MCPResponse(
        result=None,
        request_id=request_id,
        error=error,
    )


def parse_message(data: Union[str, bytes, Dict[str, Any]]) -> MCPMessage:
    """解析 MCP 消息
    
    Args:
        data: JSON 字符串、字节或字典
        
    Returns:
        MCPMessage 实例
        
    Raises:
        ValueError: 解析失败
    """
    try:
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        if isinstance(data, str):
            data = json.loads(data)
        
        if not isinstance(data, dict):
            raise ValueError("消息必须是字典类型")
        
        message_type_str = data.get("message_type", "REQUEST")
        message_type = MessageType[message_type_str]
        
        return MCPMessage(
            message_type=message_type,
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {}),
        )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise ValueError(f"消息解析失败: {e}")


def serialize_message(message: MCPMessage) -> str:
    """序列化 MCP 消息为 JSON 字符串
    
    Args:
        message: MCPMessage 实例
        
    Returns:
        JSON 字符串
    """
    return json.dumps(message.to_dict(), ensure_ascii=False)


def create_notification(
    event: str,
    data: Dict[str, Any],
) -> MCPMessage:
    """创建通知消息
    
    Args:
        event: 事件名称
        data: 事件数据
        
    Returns:
        MCPMessage 实例
    """
    return MCPMessage(
        message_type=MessageType.NOTIFICATION,
        payload={
            "event": event,
            "data": data,
        },
    )


def validate_request(request: MCPRequest) -> Optional[MCPError]:
    """验证请求有效性
    
    Args:
        request: MCPRequest 实例
        
    Returns:
        如果验证失败返回 MCPError，否则返回 None
    """
    if not request.method:
        return MCPError(
            code=ErrorCode.INVALID_REQUEST,
            message="请求方法不能为空",
        )
    
    if request.params is None:
        return MCPError(
            code=ErrorCode.INVALID_PARAMS,
            message="请求参数不能为 None",
        )
    
    return None


def validate_response(response: MCPResponse) -> Optional[MCPError]:
    """验证响应有效性
    
    Args:
        response: MCPResponse 实例
        
    Returns:
        如果验证失败返回 MCPError，否则返回 None
    """
    if response.error and not isinstance(response.error, MCPError):
        return MCPError(
            code=ErrorCode.INVALID_REQUEST,
            message="错误格式无效",
        )
    
    return None
