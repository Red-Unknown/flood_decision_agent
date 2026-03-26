"""Filesystem MCP Client

文件系统 MCP 客户端封装。
"""

from typing import Any, Dict, List, Optional

from flood_decision_agent.mcp.clients.base import MCPClientManager, get_mcp_manager


class FilesystemMCPClient:
    """文件系统 MCP 客户端"""
    
    SERVER_NAME = "filesystem"
    
    def __init__(self, manager: Optional[MCPClientManager] = None):
        self.manager = manager or get_mcp_manager()
    
    async def write_planning_markdown(
        self,
        plan_name: str,
        content: str,
        metadata: Optional[Dict] = None,
        output_dir: str = "./plans"
    ) -> Dict[str, Any]:
        """写入规划文件"""
        return await self.manager.call_tool(
            self.SERVER_NAME,
            "write_planning_markdown",
            {
                "plan_name": plan_name,
                "content": content,
                "metadata": metadata or {},
                "output_dir": output_dir
            }
        )
    
    async def read_planning_file(
        self,
        plan_id: str,
        parse_metadata: bool = True
    ) -> Dict[str, Any]:
        """读取规划文件"""
        return await self.manager.call_tool(
            self.SERVER_NAME,
            "read_planning_file",
            {
                "plan_id": plan_id,
                "parse_metadata": parse_metadata
            }
        )
    
    async def list_plans(self, filter_str: str = "", limit: int = 100) -> Dict[str, Any]:
        """列出规划文件"""
        return await self.manager.call_tool(
            self.SERVER_NAME,
            "list_plans",
            {
                "filter": filter_str,
                "limit": limit
            }
        )
    
    async def write_data_json(
        self,
        filename: str,
        data: Dict,
        indent: int = 2
    ) -> Dict[str, Any]:
        """写入 JSON 数据"""
        return await self.manager.call_tool(
            self.SERVER_NAME,
            "write_data_json",
            {
                "filename": filename,
                "data": data,
                "indent": indent
            }
        )
    
    async def read_data_json(self, filename: str) -> Dict[str, Any]:
        """读取 JSON 数据"""
        return await self.manager.call_tool(
            self.SERVER_NAME,
            "read_data_json",
            {"filename": filename}
        )