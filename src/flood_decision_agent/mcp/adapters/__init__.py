"""MCP Adapters - 适配器层

将 MCP 工具适配到现有 Agent 接口，实现平滑过渡。
"""

from flood_decision_agent.mcp.adapters.tool_adapter import MCPToolAdapter

__all__ = ["MCPToolAdapter"]