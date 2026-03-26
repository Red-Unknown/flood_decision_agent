"""MCP 相关异常"""
from .base import FloodDecisionAgentError


class MCPError(FloodDecisionAgentError):
    """MCP 基础异常"""
    
    def __init__(self, message: str, code: str = "MCP_ERROR", details: dict = None):
        super().__init__(message, code, details)


class MCPServerError(MCPError):
    """MCP 服务器异常"""
    
    def __init__(self, message: str, server_name: str = None, details: dict = None):
        super().__init__(
            message,
            code="MCP_SERVER_ERROR",
            details={"server_name": server_name, **(details or {})}
        )
        self.server_name = server_name


class MCPClientError(MCPError):
    """MCP 客户端异常"""
    
    def __init__(self, message: str, client_name: str = None, details: dict = None):
        super().__init__(
            message,
            code="MCP_CLIENT_ERROR",
            details={"client_name": client_name, **(details or {})}
        )
        self.client_name = client_name


class MCPConnectionError(MCPError):
    """MCP 连接异常"""
    
    def __init__(self, message: str, server_name: str = None, details: dict = None):
        super().__init__(
            message,
            code="MCP_CONNECTION_ERROR",
            details={"server_name": server_name, **(details or {})}
        )
