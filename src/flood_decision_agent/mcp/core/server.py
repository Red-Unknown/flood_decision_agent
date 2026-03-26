"""MCP Core Server - MCP 服务器基类

提供 MCP 服务器的基础实现，支持工具注册和调用。
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic

from flood_decision_agent.mcp.protocol.types import (
    MCPToolInfo,
    MCPServerInfo,
    ToolResult,
    ToolInput,
    ErrorCode,
)
from flood_decision_agent.mcp.protocol.constants import (
    PROTOCOL_VERSION,
    SERVER_STATUS_UNKNOWN,
    SERVER_STATUS_READY,
    SERVER_STATUS_ERROR,
    SERVER_STATUS_INITIALIZING,
)
from flood_decision_agent.infra.logging import get_logger


T = TypeVar('T')

# 工具处理器类型
ToolHandler = Callable[[Dict[str, Any]], Any]


@dataclass
class MCPServerConfig:
    """MCP 服务器配置
    
    Attributes:
        name: 服务器名称
        version: 服务器版本
        description: 服务器描述
        timeout: 请求超时（秒）
        max_concurrent: 最大并发请求数
    """
    name: str
    version: str = "1.0.0"
    description: str = ""
    timeout: float = 30.0
    max_concurrent: int = 10


class MCPServerBase(ABC):
    """MCP 服务器基类
    
    提供 MCP 服务器的基础功能，包括工具注册、管理和调用。
    
    Example:
        ```python
        class MyServer(MCPServerBase):
            def __init__(self):
                config = MCPServerConfig(name="my-server")
                super().__init__(config)
                self.register_tool("echo", self._handle_echo)
            
            def _handle_echo(self, args):
                return args.get("message", "")
        ```
    """
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self._tools: Dict[str, MCPToolInfo] = {}
        self._handlers: Dict[str, ToolHandler] = {}
        self._status = SERVER_STATUS_UNKNOWN
        self._logger = get_logger().bind(name=f"MCPServer-{config.name}")
        self._semaphore = asyncio.Semaphore(config.max_concurrent)
    
    @property
    def name(self) -> str:
        """服务器名称"""
        return self.config.name
    
    @property
    def version(self) -> str:
        """服务器版本"""
        return self.config.version
    
    @property
    def status(self) -> str:
        """服务器状态"""
        return self._status
    
    @property
    def is_ready(self) -> bool:
        """服务器是否就绪"""
        return self._status == SERVER_STATUS_READY
    
    def register_tool(
        self,
        name: str,
        handler: ToolHandler,
        description: str = "",
        input_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        """注册工具
        
        Args:
            name: 工具名称
            handler: 工具处理函数
            description: 工具描述
            input_schema: 输入参数 JSON Schema
        """
        if name in self._tools:
            self._logger.warning(f"工具 {name} 已存在，将被覆盖")
        
        self._tools[name] = MCPToolInfo(
            name=name,
            description=description,
            input_schema=input_schema or {"type": "object"},
            server_name=self.name,
        )
        self._handlers[name] = handler
        self._logger.debug(f"已注册工具: {name}")
    
    def unregister_tool(self, name: str) -> bool:
        """注销工具
        
        Args:
            name: 工具名称
            
        Returns:
            是否成功注销
        """
        if name in self._tools:
            del self._tools[name]
            del self._handlers[name]
            self._logger.debug(f"已注销工具: {name}")
            return True
        return False
    
    def list_tools(self) -> List[MCPToolInfo]:
        """列出所有工具"""
        return list(self._tools.values())
    
    def get_tool_info(self, name: str) -> Optional[MCPToolInfo]:
        """获取工具信息"""
        return self._tools.get(name)
    
    def has_tool(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self._tools
    
    async def call_tool(self, tool_input: ToolInput) -> ToolResult:
        """调用工具
        
        Args:
            tool_input: 工具输入
            
        Returns:
            工具执行结果
        """
        tool_name = tool_input.tool_name
        
        if tool_name not in self._handlers:
            return ToolResult(
                success=False,
                error=f"工具不存在: {tool_name}",
                tool_name=tool_name,
            )
        
        handler = self._handlers[tool_name]
        
        async with self._semaphore:
            try:
                import time
                start_time = time.time()
                
                # 执行工具
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(tool_input.arguments)
                else:
                    result = handler(tool_input.arguments)
                
                execution_time = (time.time() - start_time) * 1000
                
                return ToolResult(
                    success=True,
                    data=result,
                    tool_name=tool_name,
                    execution_time=execution_time,
                )
                
            except Exception as e:
                self._logger.error(f"工具 {tool_name} 执行失败: {e}")
                return ToolResult(
                    success=False,
                    error=str(e),
                    tool_name=tool_name,
                )
    
    async def initialize(self) -> bool:
        """初始化服务器
        
        Returns:
            初始化是否成功
        """
        self._status = SERVER_STATUS_INITIALIZING
        try:
            await self._on_initialize()
            self._status = SERVER_STATUS_READY
            self._logger.info(f"服务器 {self.name} 已就绪")
            return True
        except Exception as e:
            self._status = SERVER_STATUS_ERROR
            self._logger.error(f"服务器初始化失败: {e}")
            return False
    
    async def shutdown(self) -> None:
        """关闭服务器"""
        try:
            await self._on_shutdown()
            self._status = SERVER_STATUS_STOPPED
            self._logger.info(f"服务器 {self.name} 已关闭")
        except Exception as e:
            self._logger.error(f"服务器关闭时出错: {e}")
    
    def get_server_info(self) -> MCPServerInfo:
        """获取服务器信息"""
        return MCPServerInfo(
            name=self.name,
            version=self.version,
            description=self.config.description,
            tools=self.list_tools(),
            status=self._status,
        )
    
    @abstractmethod
    async def _on_initialize(self) -> None:
        """初始化钩子（子类实现）"""
        pass
    
    @abstractmethod
    async def _on_shutdown(self) -> None:
        """关闭钩子（子类实现）"""
        pass
    
    @abstractmethod
    async def run(self) -> None:
        """运行服务器（子类实现）"""
        pass
