"""MCP Core - 核心组件

提供 MCP 协议的核心实现组件，包括：
- Server: MCP 服务器基类
- Client: MCP 客户端基类
- Session: MCP 会话管理
- Transport: MCP 传输层
"""

from flood_decision_agent.mcp.core.server import (
    MCPServerBase,
    MCPServerConfig,
    ToolHandler,
)
from flood_decision_agent.mcp.core.client import (
    MCPClientBase,
    MCPClientConfig,
)
from flood_decision_agent.mcp.core.session import (
    MCPSession,
    SessionState,
)
from flood_decision_agent.mcp.core.transport import (
    MCPTransport,
    StdioTransport,
    TransportType,
)

__all__ = [
    # Server
    "MCPServerBase",
    "MCPServerConfig",
    "ToolHandler",
    # Client
    "MCPClientBase",
    "MCPClientConfig",
    # Session
    "MCPSession",
    "SessionState",
    # Transport
    "MCPTransport",
    "StdioTransport",
    "TransportType",
]
