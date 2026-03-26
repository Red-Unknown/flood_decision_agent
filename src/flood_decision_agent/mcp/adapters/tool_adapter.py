"""MCP 工具适配器

将 MCP 工具适配到现有 Agent 接口，实现平滑过渡。
替代原有的 ToolRegistry 模式。
"""

import json
from typing import Any, Callable, Dict, List, Optional, Set

from flood_decision_agent.mcp.clients.base import MCPClientManager, get_mcp_manager, MCPToolInfo
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.infra.logging import get_logger


class MCPToolAdapter:
    """MCP 工具适配器
    
    替代原有的 ToolRegistry，提供统一的工具调用接口。
    """
    
    def __init__(self, manager: Optional[MCPClientManager] = None):
        self.manager = manager or get_mcp_manager()
        self.logger = get_logger().bind(name="MCPToolAdapter")
        
    def list_tools(self) -> List[MCPToolInfo]:
        """列出所有可用工具"""
        return self.manager.list_all_tools()
    
    def is_available(self, tool_name: str) -> bool:
        """检查工具是否可用"""
        tools = self.list_tools()
        return any(t.name == tool_name for t in tools)
    
    async def execute(
        self,
        tool_name: str,
        data_pool: SharedDataPool,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行工具（兼容旧接口）
        
        Args:
            tool_name: 工具名称
            data_pool: 共享数据池（可选使用）
            config: 工具配置参数
            
        Returns:
            工具执行结果
        """
        config = config or {}
        
        # 从 data_pool 中提取可能需要的参数
        # 这里可以根据 tool_name 做特定的参数映射
        arguments = self._prepare_arguments(tool_name, config, data_pool)
        
        try:
            result = await self.manager.call_tool_auto(tool_name, arguments)
            self.logger.debug(f"工具 {tool_name} 执行成功")
            return result
        except Exception as e:
            self.logger.error(f"工具 {tool_name} 执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    def _prepare_arguments(
        self,
        tool_name: str,
        config: Dict[str, Any],
        data_pool: SharedDataPool
    ) -> Dict[str, Any]:
        """准备工具参数
        
        根据工具类型，从 config 和 data_pool 中提取参数。
        """
        arguments = dict(config)
        
        # 特殊处理：如果参数值是数据池key，尝试获取实际值
        for key, value in arguments.items():
            if isinstance(value, str) and value.startswith("pool:"):
                pool_key = value[5:]  # 去掉 "pool:" 前缀
                arguments[key] = data_pool.get(pool_key)
        
        return arguments
    
    def get_tool_info(self, tool_name: str) -> Optional[MCPToolInfo]:
        """获取工具信息"""
        tools = self.list_tools()
        for tool in tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def find_by_task_type(self, task_type: str) -> List[MCPToolInfo]:
        """根据任务类型查找工具（兼容旧接口）
        
        通过工具描述关键词匹配。
        """
        tools = self.list_tools()
        matching = []
        
        # 任务类型到关键词的映射
        task_keywords = {
            "data_query": ["query", "read", "list", "get"],
            "compute": ["calculate", "compute", "run", "model"],
            "format": ["write", "format", "convert"],
            "log": ["log", "report"],
            "file_operation": ["file", "write", "read"],
            "hydrology": ["rainfall", "flood", "reservoir", "dispatch"],
        }
        
        keywords = task_keywords.get(task_type, [task_type])
        
        for tool in tools:
            desc_lower = tool.description.lower()
            if any(kw in desc_lower or kw in tool.name.lower() for kw in keywords):
                matching.append(tool)
        
        return matching


class LegacyToolAdapter:
    """遗留工具适配器
    
    如果需要保留部分本地工具，可以通过此适配器集成。
    """
    
    def __init__(self):
        self.local_tools: Dict[str, Callable] = {}
        self.logger = get_logger().bind(name="LegacyToolAdapter")
        
    def register_local_tool(
        self,
        name: str,
        handler: Callable[[SharedDataPool, Dict[str, Any]], Dict[str, Any]],
        task_types: Optional[Set[str]] = None
    ):
        """注册本地工具"""
        self.local_tools[name] = {
            "handler": handler,
            "task_types": task_types or set()
        }
        self.logger.info(f"注册本地工具: {name}")
        
    async def execute(
        self,
        tool_name: str,
        data_pool: SharedDataPool,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行本地工具"""
        if tool_name not in self.local_tools:
            raise ValueError(f"未知工具: {tool_name}")
        
        tool = self.local_tools[tool_name]
        try:
            result = tool["handler"](data_pool, config or {})
            return {
                "success": True,
                "data": result,
                "tool_name": tool_name
            }
        except Exception as e:
            self.logger.error(f"本地工具 {tool_name} 执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }


class UnifiedToolExecutor:
    """统一工具执行器
    
    整合 MCP 工具和本地工具，提供统一的执行接口。
    """
    
    def __init__(
        self,
        mcp_adapter: Optional[MCPToolAdapter] = None,
        legacy_adapter: Optional[LegacyToolAdapter] = None
    ):
        self.mcp = mcp_adapter or MCPToolAdapter()
        self.legacy = legacy_adapter
        self.logger = get_logger().bind(name="UnifiedToolExecutor")
        
    async def execute(
        self,
        tool_name: str,
        data_pool: SharedDataPool,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """统一执行入口"""
        # 优先尝试 MCP 工具
        if self.mcp.is_available(tool_name):
            return await self.mcp.execute(tool_name, data_pool, config)
        
        # 尝试本地工具
        if self.legacy and tool_name in self.legacy.local_tools:
            return await self.legacy.execute(tool_name, data_pool, config)
        
        # 工具未找到
        available = [t.name for t in self.mcp.list_tools()]
        if self.legacy:
            available.extend(self.legacy.local_tools.keys())
        
        return {
            "success": False,
            "error": f"工具 {tool_name} 未找到",
            "available_tools": available
        }
    
    def list_all_tools(self) -> List[str]:
        """列出所有可用工具名称"""
        tools = [t.name for t in self.mcp.list_tools()]
        if self.legacy:
            tools.extend(self.legacy.local_tools.keys())
        return tools