"""MCP服务集成模块

将MCP服务接入单元任务执行Agent，支持通过MCP协议调用外部工具。
支持结果包装和LLM解释功能。
"""

from typing import Any, Dict, List, Optional, Callable
import asyncio
from loguru import logger

from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.tools.registry import ToolMetadata, ToolRegistry
from flood_decision_agent.mcp.clients.base import MCPClientManager
from flood_decision_agent.mcp.clients.wrappers import (
    MCPWrapperFactory,
    MCPWrappedClientManager,
    SimpleClientWrapper,
    ComplexClientWrapper,
)
from flood_decision_agent.mcp.clients.prompts import PromptManager
from flood_decision_agent.mcp.adapters.tool_adapter import MCPToolAdapter


class MCPToolIntegration:
    """MCP工具集成器
    
    负责将MCP服务注册为Agent可调用的工具。
    支持结果包装和LLM解释功能。
    """
    
    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        mcp_manager: Optional[MCPClientManager] = None,
        enable_wrapping: bool = True,
        llm_client: Optional[Any] = None,
    ):
        """初始化MCP工具集成器
        
        Args:
            tool_registry: 工具注册表，为None时使用全局注册表
            mcp_manager: MCP客户端管理器，为None时创建新实例
            enable_wrapping: 是否启用结果包装
            llm_client: LLM客户端，用于结果解释
        """
        self.tool_registry = tool_registry
        self.mcp_manager = mcp_manager or MCPClientManager()
        self.tool_adapter = MCPToolAdapter(mcp_manager)
        self._registered_mcp_tools: Dict[str, str] = {}  # tool_name -> server_name
        self._initialized = False
        
        # 包装器相关
        self._enable_wrapping = enable_wrapping
        self._wrapper_factory: Optional[MCPWrapperFactory] = None
        if enable_wrapping:
            self._wrapper_factory = MCPWrapperFactory(self.mcp_manager, llm_client)
        
        logger.info("MCP工具集成器已创建")
    
    async def initialize(self) -> bool:
        """初始化MCP连接
        
        Returns:
            是否初始化成功
        """
        if self._initialized:
            logger.debug("MCP集成器已初始化，跳过")
            return True
        
        try:
            # 注册默认的MCP服务器
            self._register_default_servers()
            
            # 连接所有服务器
            connected = await self.mcp_manager.connect_all()
            logger.info(f"已连接 {connected} 个 MCP Server")
            
            # 将MCP工具注册到工具注册表
            await self._register_mcp_tools_to_registry()
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"MCP初始化失败: {e}")
            return False
    
    def _register_default_servers(self) -> None:
        """注册默认的MCP服务器"""
        # 文档服务
        self.mcp_manager.register_server(
            name="document",
            command="python",
            args=["-m", "flood_decision_agent.mcp.servers.document_server"]
        )
        logger.debug("已注册 document MCP Server")
        
        # 文件系统服务
        self.mcp_manager.register_server(
            name="filesystem",
            command="python",
            args=["-m", "flood_decision_agent.mcp.servers.filesystem_server"]
        )
        logger.debug("已注册 filesystem MCP Server")
        
        # 水文计算服务
        self.mcp_manager.register_server(
            name="hydrology",
            command="python",
            args=["-m", "flood_decision_agent.mcp.servers.hydrology_server"]
        )
        logger.debug("已注册 hydrology MCP Server")
    
    async def _register_mcp_tools_to_registry(self) -> None:
        """将MCP工具注册到工具注册表"""
        if not self.tool_registry:
            logger.warning("未提供工具注册表，跳过MCP工具注册")
            return
        
        # 获取所有MCP工具
        mcp_tools = self.tool_adapter.list_tools()
        
        for tool_name in mcp_tools:
            # 创建工具元数据
            metadata = ToolMetadata(
                name=f"mcp_{tool_name}",
                description=f"MCP工具: {tool_name}",
                task_types={"mcp", "external"},
                priority=50,
            )
            
            # 创建包装函数
            handler = self._create_mcp_tool_handler(tool_name)
            
            # 注册到工具注册表
            registry_name = f"mcp_{tool_name}"
            self.tool_registry.register_if_not_exists(
                registry_name,
                handler,
                metadata
            )
            
            self._registered_mcp_tools[registry_name] = tool_name
            logger.debug(f"已注册MCP工具: {registry_name}")
        
        logger.info(f"已注册 {len(mcp_tools)} 个MCP工具到工具注册表")
    
    def _create_mcp_tool_handler(self, tool_name: str) -> Callable:
        """创建MCP工具的包装处理函数
        
        Args:
            tool_name: MCP工具名称
            
        Returns:
            包装后的处理函数
        """
        async def handler(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """MCP工具处理函数"""
            try:
                result = await self.tool_adapter.execute(
                    tool_name=tool_name,
                    data_pool=data_pool,
                    config=config
                )
                return {
                    "success": True,
                    "result": result,
                    "tool": tool_name,
                }
            except Exception as e:
                logger.error(f"MCP工具执行失败 {tool_name}: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "tool": tool_name,
                }
        
        # 同步包装（因为ToolRegistry期望同步函数）
        def sync_handler(data_pool: SharedDataPool, config: Dict[str, Any]) -> Dict[str, Any]:
            """同步包装函数"""
            try:
                # 获取或创建事件循环
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # 运行异步函数
                result = loop.run_until_complete(handler(data_pool, config))
                return result
            except Exception as e:
                logger.error(f"MCP工具同步执行失败 {tool_name}: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "tool": tool_name,
                }
        
        return sync_handler
    
    async def execute_mcp_tool(
        self,
        tool_name: str,
        data_pool: SharedDataPool,
        config: Dict[str, Any],
        wrap_result: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """直接执行MCP工具
        
        Args:
            tool_name: 工具名称（可以是原始MCP工具名或注册名mcp_*）
            data_pool: 数据池
            config: 配置参数
            wrap_result: 是否包装结果，None表示自动判断
            
        Returns:
            执行结果
        """
        # 移除mcp_前缀（如果有）
        original_tool_name = tool_name
        if tool_name.startswith("mcp_"):
            tool_name = tool_name[4:]
        
        # 判断是否包装结果
        should_wrap = wrap_result if wrap_result is not None else self._should_wrap_tool(tool_name)
        
        try:
            if should_wrap and self._wrapper_factory:
                # 使用包装器执行（带LLM解释）
                logger.debug(f"使用包装器执行MCP工具: {tool_name}")
                
                # 查找工具所在的Server
                server_name = self._find_tool_server(tool_name)
                if not server_name:
                    raise ValueError(f"未找到工具所在Server: {tool_name}")
                
                result = await self._wrapper_factory.execute(
                    server_name=server_name,
                    tool_name=tool_name,
                    arguments=config,
                )
                return result
            else:
                # 直接执行（不包装）
                result = await self.tool_adapter.execute(
                    tool_name=tool_name,
                    data_pool=data_pool,
                    config=config
                )
                return {
                    "success": True,
                    "raw_data": result,
                    "wrapped": False,
                    "tool": tool_name,
                }
        except Exception as e:
            logger.error(f"MCP工具执行失败 {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name,
            }
    
    def _should_wrap_tool(self, tool_name: str) -> bool:
        """判断是否应该包装工具结果
        
        Args:
            tool_name: 工具名称
            
        Returns:
            是否应该包装
        """
        if not self._enable_wrapping:
            return False
        
        # 复杂工具需要包装，简单工具不需要
        return PromptManager.is_complex_tool(tool_name)
    
    def _find_tool_server(self, tool_name: str) -> Optional[str]:
        """查找工具所在的Server
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Server名称，未找到返回None
        """
        for server_name, client in self.mcp_manager.clients.items():
            if any(t.name == tool_name for t in client.tools):
                return server_name
        return None
    
    def get_registered_mcp_tools(self) -> List[str]:
        """获取已注册的MCP工具列表
        
        Returns:
            工具名称列表
        """
        return list(self._registered_mcp_tools.keys())
    
    def is_mcp_tool(self, tool_name: str) -> bool:
        """检查是否为MCP工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            是否为MCP工具
        """
        return tool_name in self._registered_mcp_tools
    
    async def close(self) -> None:
        """关闭MCP连接"""
        if self.mcp_manager:
            await self.mcp_manager.close_all()
            logger.info("MCP连接已关闭")


class UnitTaskExecutorWithMCP:
    """支持MCP的单元任务执行器
    
    扩展UnitTaskExecutionAgent，支持MCP工具调用和结果包装。
    """
    
    def __init__(
        self,
        base_executor: Any,  # UnitTaskExecutionAgent
        enable_mcp: bool = True,
        enable_wrapping: bool = True,
        llm_client: Optional[Any] = None,
    ):
        """初始化
        
        Args:
            base_executor: 基础执行器实例
            enable_mcp: 是否启用MCP
            enable_wrapping: 是否启用结果包装
            llm_client: LLM客户端，用于结果解释
        """
        self.base_executor = base_executor
        self.enable_mcp = enable_mcp
        self.enable_wrapping = enable_wrapping
        self.mcp_integration: Optional[MCPToolIntegration] = None
        self._llm_client = llm_client
        
        if enable_mcp:
            self._init_mcp()
    
    def _init_mcp(self) -> None:
        """初始化MCP集成"""
        try:
            self.mcp_integration = MCPToolIntegration(
                tool_registry=self.base_executor.tool_registry,
                enable_wrapping=self.enable_wrapping,
                llm_client=self._llm_client,
            )
            logger.info("MCP集成已初始化")
        except Exception as e:
            logger.error(f"MCP集成初始化失败: {e}")
            self.enable_mcp = False
    
    async def initialize_mcp(self) -> bool:
        """初始化MCP连接
        
        Returns:
            是否成功
        """
        if not self.enable_mcp or not self.mcp_integration:
            return False
        
        return await self.mcp_integration.initialize()
    
    def get_available_tools(self) -> List[str]:
        """获取所有可用工具（包括MCP工具）
        
        Returns:
            工具名称列表
        """
        # 基础工具
        base_tools = self.base_executor.tool_registry.list_tools()
        
        # MCP工具
        mcp_tools = []
        if self.mcp_integration:
            mcp_tools = self.mcp_integration.get_registered_mcp_tools()
        
        return base_tools + mcp_tools
    
    def is_mcp_tool(self, tool_name: str) -> bool:
        """检查是否为MCP工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            是否为MCP工具
        """
        if not self.mcp_integration:
            return False
        return self.mcp_integration.is_mcp_tool(tool_name)
    
    async def execute_task(
        self,
        task_type: str,
        data_pool: SharedDataPool,
        config: Optional[Dict[str, Any]] = None,
        wrap_result: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """执行任务（支持MCP工具）
        
        Args:
            task_type: 任务类型或工具名称
            data_pool: 数据池
            config: 配置参数
            wrap_result: 是否包装结果，None表示自动判断
            
        Returns:
            执行结果
        """
        config = config or {}
        
        # 检查是否为MCP工具
        if self.enable_mcp and self.is_mcp_tool(task_type):
            logger.info(f"使用MCP工具执行: {task_type}")
            return await self.mcp_integration.execute_mcp_tool(
                tool_name=task_type,
                data_pool=data_pool,
                config=config,
                wrap_result=wrap_result,
            )
        
        # 使用基础执行器
        return self.base_executor.execute_task(task_type, data_pool, config)
    
    async def close(self) -> None:
        """关闭资源"""
        if self.mcp_integration:
            await self.mcp_integration.close()


# 便捷函数

async def setup_mcp_for_executor(
    executor: Any,
    tool_registry: Optional[ToolRegistry] = None,
) -> MCPToolIntegration:
    """为执行器设置MCP集成
    
    Args:
        executor: 任务执行器
        tool_registry: 工具注册表
        
    Returns:
        MCP工具集成器
    """
    integration = MCPToolIntegration(
        tool_registry=tool_registry or executor.tool_registry,
    )
    
    success = await integration.initialize()
    if success:
        logger.info("MCP集成设置成功")
    else:
        logger.warning("MCP集成设置失败，将使用基础工具")
    
    return integration
