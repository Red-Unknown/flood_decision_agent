"""MCP Core Client - MCP 客户端基类

提供 MCP 客户端的基础实现，支持连接管理、工具发现和调用。
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable

from flood_decision_agent.mcp.protocol.types import (
    MCPToolInfo,
    MCPRequest,
    MCPResponse,
    ToolResult,
    ErrorCode,
)
from flood_decision_agent.mcp.protocol.constants import (
    DEFAULT_TIMEOUT,
    CONNECTION_TIMEOUT,
    MAX_RETRY_COUNT,
    RETRY_DELAY,
)
from flood_decision_agent.infra.logging import get_logger


@dataclass
class MCPClientConfig:
    """MCP 客户端配置
    
    Attributes:
        name: 客户端名称
        timeout: 请求超时（秒）
        retry_count: 重试次数
        retry_delay: 重试延迟（秒）
        auto_reconnect: 是否自动重连
    """
    name: str = "mcp-client"
    timeout: float = DEFAULT_TIMEOUT
    retry_count: int = MAX_RETRY_COUNT
    retry_delay: float = RETRY_DELAY
    auto_reconnect: bool = True


class MCPClientBase(ABC):
    """MCP 客户端基类
    
    提供 MCP 客户端的基础功能，包括连接管理、工具发现和调用。
    
    Example:
        ```python
        class MyClient(MCPClientBase):
            async def connect(self) -> bool:
                # 实现连接逻辑
                pass
            
            async def disconnect(self) -> None:
                # 实现断开连接逻辑
                pass
            
            async def send_request(self, request: MCPRequest) -> MCPResponse:
                # 实现请求发送逻辑
                pass
        ```
    """
    
    def __init__(self, config: Optional[MCPClientConfig] = None):
        self.config = config or MCPClientConfig()
        self._connected = False
        self._tools: List[MCPToolInfo] = []
        self._logger = get_logger().bind(name=f"MCPClient-{self.config.name}")
        self._lock = asyncio.Lock()
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected
    
    @property
    def available_tools(self) -> List[MCPToolInfo]:
        """可用工具列表"""
        return self._tools.copy()
    
    def get_tool_info(self, name: str) -> Optional[MCPToolInfo]:
        """获取工具信息
        
        Args:
            name: 工具名称
            
        Returns:
            工具信息，不存在则返回 None
        """
        for tool in self._tools:
            if tool.name == name:
                return tool
        return None
    
    def has_tool(self, name: str) -> bool:
        """检查工具是否可用
        
        Args:
            name: 工具名称
            
        Returns:
            工具是否可用
        """
        return any(t.name == name for t in self._tools)
    
    async def connect(self) -> bool:
        """连接到服务器
        
        Returns:
            连接是否成功
        """
        async with self._lock:
            if self._connected:
                return True
            
            try:
                success = await self._do_connect()
                if success:
                    self._connected = True
                    # 获取工具列表
                    await self._fetch_tools()
                    self._logger.info("客户端已连接")
                return success
            except Exception as e:
                self._logger.error(f"连接失败: {e}")
                return False
    
    async def disconnect(self) -> None:
        """断开连接"""
        async with self._lock:
            if not self._connected:
                return
            
            try:
                await self._do_disconnect()
                self._connected = False
                self._tools = []
                self._logger.info("客户端已断开")
            except Exception as e:
                self._logger.error(f"断开连接时出错: {e}")
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> ToolResult:
        """调用工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            timeout: 超时时间（秒）
            
        Returns:
            工具执行结果
        """
        if not self._connected:
            return ToolResult(
                success=False,
                error="客户端未连接",
                tool_name=tool_name,
            )
        
        if not self.has_tool(tool_name):
            return ToolResult(
                success=False,
                error=f"工具不存在: {tool_name}",
                tool_name=tool_name,
            )
        
        request = MCPRequest(
            method=tool_name,
            params=arguments,
            timeout=timeout or self.config.timeout,
        )
        
        # 重试逻辑
        for attempt in range(self.config.retry_count + 1):
            try:
                response = await self.send_request(request)
                
                if response.error:
                    return ToolResult(
                        success=False,
                        error=response.error.message,
                        tool_name=tool_name,
                    )
                
                return ToolResult(
                    success=True,
                    data=response.result,
                    tool_name=tool_name,
                )
                
            except asyncio.TimeoutError:
                if attempt < self.config.retry_count:
                    self._logger.warning(f"请求超时，重试 {attempt + 1}/{self.config.retry_count}")
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    return ToolResult(
                        success=False,
                        error="请求超时",
                        tool_name=tool_name,
                    )
            except Exception as e:
                self._logger.error(f"调用工具失败: {e}")
                return ToolResult(
                    success=False,
                    error=str(e),
                    tool_name=tool_name,
                )
        
        return ToolResult(
            success=False,
            error="调用失败",
            tool_name=tool_name,
        )
    
    async def _fetch_tools(self) -> None:
        """获取工具列表"""
        try:
            self._tools = await self._do_fetch_tools()
            self._logger.debug(f"获取到 {len(self._tools)} 个工具")
        except Exception as e:
            self._logger.warning(f"获取工具列表失败: {e}")
            self._tools = []
    
    @abstractmethod
    async def _do_connect(self) -> bool:
        """执行连接（子类实现）"""
        pass
    
    @abstractmethod
    async def _do_disconnect(self) -> None:
        """执行断开连接（子类实现）"""
        pass
    
    @abstractmethod
    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """发送请求（子类实现）"""
        pass
    
    @abstractmethod
    async def _do_fetch_tools(self) -> List[MCPToolInfo]:
        """获取工具列表（子类实现）"""
        pass
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()


class MCPClientManager:
    """MCP 客户端管理器
    
    管理多个 MCP 客户端连接，提供统一的工具调用接口。
    """
    
    def __init__(self):
        self._clients: Dict[str, MCPClientBase] = {}
        self._logger = get_logger().bind(name="MCPClientManager")
    
    def register_client(self, name: str, client: MCPClientBase) -> None:
        """注册客户端
        
        Args:
            name: 客户端名称
            client: 客户端实例
        """
        self._clients[name] = client
        self._logger.info(f"已注册客户端: {name}")
    
    def unregister_client(self, name: str) -> bool:
        """注销客户端
        
        Args:
            name: 客户端名称
            
        Returns:
            是否成功注销
        """
        if name in self._clients:
            del self._clients[name]
            self._logger.info(f"已注销客户端: {name}")
            return True
        return False
    
    def get_client(self, name: str) -> Optional[MCPClientBase]:
        """获取客户端
        
        Args:
            name: 客户端名称
            
        Returns:
            客户端实例，不存在则返回 None
        """
        return self._clients.get(name)
    
    async def connect_all(self) -> Dict[str, bool]:
        """连接所有客户端
        
        Returns:
            各客户端连接结果
        """
        results = {}
        for name, client in self._clients.items():
            try:
                results[name] = await client.connect()
            except Exception as e:
                self._logger.error(f"连接 {name} 失败: {e}")
                results[name] = False
        return results
    
    async def disconnect_all(self) -> None:
        """断开所有客户端"""
        for name, client in self._clients.items():
            try:
                await client.disconnect()
            except Exception as e:
                self._logger.error(f"断开 {name} 失败: {e}")
    
    def list_all_tools(self) -> List[MCPToolInfo]:
        """列出所有可用工具"""
        all_tools = []
        for client in self._clients.values():
            all_tools.extend(client.available_tools)
        return all_tools
    
    async def call_tool(
        self,
        client_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> ToolResult:
        """调用指定客户端的工具
        
        Args:
            client_name: 客户端名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        client = self._clients.get(client_name)
        if not client:
            return ToolResult(
                success=False,
                error=f"客户端不存在: {client_name}",
                tool_name=tool_name,
            )
        
        return await client.call_tool(tool_name, arguments)
    
    async def call_tool_auto(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> ToolResult:
        """自动查找并调用工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        for client in self._clients.values():
            if client.has_tool(tool_name):
                return await client.call_tool(tool_name, arguments)
        
        return ToolResult(
            success=False,
            error=f"未找到工具: {tool_name}",
            tool_name=tool_name,
        )
