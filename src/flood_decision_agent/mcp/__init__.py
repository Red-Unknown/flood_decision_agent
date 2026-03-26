"""MCP 模块 - Model Context Protocol 集成

本模块提供分布式 MCP 服务架构，替代原有的本地工具注册表模式。
包含自定义 MCP Server、Client 和适配器层。

目录结构：
- protocol/: 协议类型定义 (types, messages, constants)
- core/: 核心组件 (server, client, session, transport)
- servers/: MCP 服务器实现
- clients/: MCP 客户端实现
- adapters/: 适配器层
"""

# 协议层导出
from flood_decision_agent.mcp.protocol import (
    MCPToolInfo,
    MCPServerInfo,
    MCPMessage,
    MCPRequest,
    MCPResponse,
    MCPError,
    ToolResult,
    ToolInput,
    MessageType,
    create_request,
    create_response,
    create_error,
    parse_message,
    DEFAULT_TIMEOUT,
    MAX_MESSAGE_SIZE,
    PROTOCOL_VERSION,
    ErrorCode,
)

# 核心层导出
from flood_decision_agent.mcp.core import (
    MCPServerBase,
    MCPServerConfig,
    ToolHandler,
    MCPClientBase,
    MCPClientConfig,
    MCPSession,
    SessionState,
    MCPTransport,
    StdioTransport,
    TransportType,
)

# 原有客户端和适配器导出
from flood_decision_agent.mcp.clients.base import MCPClientManager
from flood_decision_agent.mcp.adapters.tool_adapter import MCPToolAdapter

__all__ = [
    # Protocol
    "MCPToolInfo",
    "MCPServerInfo",
    "MCPMessage",
    "MCPRequest",
    "MCPResponse",
    "MCPError",
    "ToolResult",
    "ToolInput",
    "MessageType",
    "create_request",
    "create_response",
    "create_error",
    "parse_message",
    "DEFAULT_TIMEOUT",
    "MAX_MESSAGE_SIZE",
    "PROTOCOL_VERSION",
    "ErrorCode",
    # Core
    "MCPServerBase",
    "MCPServerConfig",
    "ToolHandler",
    "MCPClientBase",
    "MCPClientConfig",
    "MCPSession",
    "SessionState",
    "MCPTransport",
    "StdioTransport",
    "TransportType",
    # Legacy
    "MCPClientManager",
    "MCPToolAdapter",
]