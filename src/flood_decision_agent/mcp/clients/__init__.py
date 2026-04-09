"""MCP Clients - MCP 客户端

用于连接各类 MCP Server，提供统一的调用接口。
支持结果包装和 LLM 解释功能。
"""

from flood_decision_agent.mcp.clients.base import MCPClientManager
from flood_decision_agent.mcp.clients.filesystem import FilesystemMCPClient
from flood_decision_agent.mcp.clients.prompts import (
    PromptManager,
    HIPIMS_INTERPRETATION_PROMPT,
    HYDROLOGY_INTERPRETATION_PROMPT,
    RAINFALL_INTERPRETATION_PROMPT,
    DISPATCH_INTERPRETATION_PROMPT,
    GENERAL_DATA_INTERPRETATION_PROMPT,
    NO_PROMPT_NEEDED,
)
from flood_decision_agent.mcp.clients.wrappers import (
    BaseMCPWrapper,
    SimpleClientWrapper,
    ComplexClientWrapper,
    MCPWrapperFactory,
    MCPWrappedClientManager,
    call_tool_with_wrapper,
)
from flood_decision_agent.mcp.clients.health_check import (
    MCPHealthCheckManager,
    HealthCheckResult,
    ServiceHealthConfig,
    get_mcp_health_manager,
    initialize_mcp_services,
)

__all__ = [
    # 基础客户端
    "MCPClientManager",
    "FilesystemMCPClient",
    # 健康检查与初始化
    "MCPHealthCheckManager",
    "HealthCheckResult",
    "ServiceHealthConfig",
    "get_mcp_health_manager",
    "initialize_mcp_services",
    # 提示词管理
    "PromptManager",
    "HIPIMS_INTERPRETATION_PROMPT",
    "HYDROLOGY_INTERPRETATION_PROMPT",
    "RAINFALL_INTERPRETATION_PROMPT",
    "DISPATCH_INTERPRETATION_PROMPT",
    "GENERAL_DATA_INTERPRETATION_PROMPT",
    "NO_PROMPT_NEEDED",
    # 包装器
    "BaseMCPWrapper",
    "SimpleClientWrapper",
    "ComplexClientWrapper",
    "MCPWrapperFactory",
    "MCPWrappedClientManager",
    "call_tool_with_wrapper",
]
