"""MCP Client 基础管理器

提供统一的 MCP Client 管理和工具调用接口。
针对 Windows 环境进行了优化。
"""

import asyncio
import json
import os
import platform
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool as MCPTool

from flood_decision_agent.infra.logging import get_logger


@dataclass
class MCPToolInfo:
    """MCP 工具信息"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str


class MCPClientConnection:
    """单个 MCP Client 连接"""
    
    def __init__(self, name: str, server_params: StdioServerParameters):
        self.name = name
        self.server_params = server_params
        self.session: Optional[ClientSession] = None
        self.client = None
        self.read = None
        self.write = None
        self.tools: List[MCPToolInfo] = []
        self._connected = False
        
    async def connect(self):
        """建立连接（Windows 优化版）"""
        try:
            # Windows 环境下使用正确的事件循环策略
            if platform.system() == "Windows":
                # 确保使用 ProactorEventLoop（支持 stdio 的异步操作）
                if isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsSelectorEventLoopPolicy):
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            # 创建 stdio 客户端
            self.client = stdio_client(self.server_params)
            self.read, self.write = await self.client.__aenter__()
            
            # 创建会话
            self.session = await ClientSession(self.read, self.write).__aenter__()
            
            # 初始化（带超时）
            await asyncio.wait_for(
                self.session.initialize(),
                timeout=10.0
            )
            
            self._connected = True
            
            # 获取可用工具
            await self._fetch_tools()
            
            return True
            
        except asyncio.TimeoutError:
            get_logger().error(f"MCP Client '{self.name}' 连接超时")
            await self._cleanup()
            return False
        except Exception as e:
            get_logger().error(f"MCP Client '{self.name}' 连接失败: {e}")
            await self._cleanup()
            return False
    
    async def _cleanup(self):
        """清理资源"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
        except:
            pass
        try:
            if self.client:
                await self.client.__aexit__(None, None, None)
        except:
            pass
        self._connected = False
    
    async def _fetch_tools(self):
        """获取服务器工具列表"""
        if not self.session:
            return
        
        try:
            tools_response = await self.session.list_tools()
            self.tools = [
                MCPToolInfo(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.inputSchema,
                    server_name=self.name
                )
                for tool in tools_response.tools
            ]
        except Exception as e:
            get_logger().warning(f"获取工具列表失败: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if not self.session or not self._connected:
            raise RuntimeError(f"MCP Client '{self.name}' 未连接")
        
        result = await self.session.call_tool(tool_name, arguments)
        
        # 解析结果
        if result.content:
            content = result.content[0]
            if content.type == "text":
                try:
                    return json.loads(content.text)
                except json.JSONDecodeError:
                    return {"text": content.text, "success": True}
            elif content.type == "image":
                return {"image_data": content.data, "success": True}
        
        return {"success": not result.isError}
    
    async def close(self):
        """关闭连接"""
        await self._cleanup()


class MCPClientManager:
    """MCP Client 管理器
    
    管理多个 MCP Client 连接，提供统一的工具调用接口。
    针对 Windows 环境进行了优化。
    """
    
    def __init__(self):
        self.clients: Dict[str, MCPClientConnection] = {}
        self.logger = get_logger().bind(name="MCPClientManager")
        
        # Windows 环境设置
        if platform.system() == "Windows":
            # 使用 ProactorEventLoop（支持管道和 stdio）
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                self.logger.debug("已设置 WindowsProactorEventLoopPolicy")
            except Exception as e:
                self.logger.warning(f"设置 EventLoopPolicy 失败: {e}")
        
    def register_server(self, name: str, command: str, args: List[str], env: Optional[Dict] = None):
        """注册 MCP Server"""
        # 合并环境变量
        merged_env = dict(os.environ)
        if env:
            merged_env.update(env)
        
        # Windows 环境添加必要变量
        if platform.system() == "Windows":
            merged_env["PYTHONIOENCODING"] = merged_env.get("PYTHONIOENCODING", "utf-8")
            merged_env["PYTHONUNBUFFERED"] = "1"
        
        params = StdioServerParameters(
            command=command,
            args=args,
            env=merged_env
        )
        self.clients[name] = MCPClientConnection(name, params)
        self.logger.info(f"已注册 MCP Server: {name}")
        
    async def connect_all(self):
        """连接所有 Server"""
        if not self.clients:
            self.logger.warning("没有注册的 MCP Server")
            return 0
        
        results = await asyncio.gather(
            *[client.connect() for client in self.clients.values()],
            return_exceptions=True
        )
        
        connected = 0
        for name, result in zip(self.clients.keys(), results):
            if isinstance(result, Exception):
                self.logger.error(f"连接 {name} 失败: {result}")
            elif result:
                connected += 1
                self.logger.info(f"已连接: {name}")
        
        self.logger.info(f"MCP 连接完成: {connected}/{len(self.clients)}")
        return connected
    
    def list_all_tools(self) -> List[MCPToolInfo]:
        """列出所有可用工具"""
        all_tools = []
        for client in self.clients.values():
            all_tools.extend(client.tools)
        return all_tools
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用指定 Server 的工具"""
        if server_name not in self.clients:
            raise ValueError(f"未知的 MCP Server: {server_name}")
        
        client = self.clients[server_name]
        return await client.call_tool(tool_name, arguments)
    
    async def call_tool_auto(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """自动查找并调用工具"""
        for client in self.clients.values():
            if any(t.name == tool_name for t in client.tools):
                return await client.call_tool(tool_name, arguments)
        
        raise ValueError(f"未找到工具: {tool_name}")
    
    async def close_all(self):
        """关闭所有连接"""
        await asyncio.gather(
            *[client.close() for client in self.clients.values()],
            return_exceptions=True
        )
        self.logger.info("所有 MCP 连接已关闭")


# 全局管理器实例
_global_mcp_manager: Optional[MCPClientManager] = None


def get_mcp_manager() -> MCPClientManager:
    """获取全局 MCP 管理器"""
    global _global_mcp_manager
    if _global_mcp_manager is None:
        _global_mcp_manager = MCPClientManager()
    return _global_mcp_manager