"""MCP Client 包装器

为不同复杂度的 MCP 工具提供结果包装和 LLM 解释功能。
Server 层保持纯净（只返回原始数据），Client 层负责结果包装。
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from flood_decision_agent.infra.logging import get_logger
from flood_decision_agent.mcp.clients.base import MCPClientManager
from flood_decision_agent.mcp.clients.prompts import PromptManager


logger = get_logger().bind(name="MCPWrappers")


class BaseMCPWrapper(ABC):
    """MCP 包装器基类
    
    所有具体包装器的抽象基类，定义统一接口。
    """
    
    def __init__(self, mcp_manager: MCPClientManager):
        """初始化包装器
        
        Args:
            mcp_manager: MCP 客户端管理器
        """
        self.mcp_manager = mcp_manager
        self.logger = logger.bind(wrapper=self.__class__.__name__)
    
    @abstractmethod
    async def execute(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工具调用
        
        Args:
            server_name: MCP Server 名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            执行结果（包装后的格式）
        """
        pass
    
    async def _call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用底层 MCP 工具
        
        Args:
            server_name: MCP Server 名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            原始执行结果
        """
        try:
            result = await self.mcp_manager.call_tool(
                server_name=server_name,
                tool_name=tool_name,
                arguments=arguments
            )
            return result
        except Exception as e:
            self.logger.error(f"调用 MCP 工具失败 {server_name}.{tool_name}: {e}")
            raise


class SimpleClientWrapper(BaseMCPWrapper):
    """简单任务包装器 - 直接透传
    
    适用于数据查询等简单任务，直接返回原始结果，无需 LLM 解释。
    """
    
    async def execute(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工具调用（直接透传）
        
        Args:
            server_name: MCP Server 名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            原始执行结果
        """
        self.logger.debug(f"简单透传: {server_name}.{tool_name}")
        
        # 直接调用并返回原始结果
        result = await self._call_tool(server_name, tool_name, arguments)
        
        return {
            "success": True,
            "raw_data": result,
            "wrapped": False,
            "server": server_name,
            "tool": tool_name,
        }
    
    async def get_data(self, server_name: str, tool_name: str, **kwargs) -> Dict[str, Any]:
        """便捷方法：获取数据
        
        Args:
            server_name: MCP Server 名称
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            原始执行结果
        """
        return await self.execute(server_name, tool_name, kwargs)


class ComplexClientWrapper(BaseMCPWrapper):
    """复杂任务包装器 - 使用 LLM 解释结果
    
    适用于洪水模拟、水文计算等复杂任务，使用 LLM 对结果进行专业解释。
    """
    
    def __init__(
        self,
        mcp_manager: MCPClientManager,
        llm_client: Optional[Any] = None,
    ):
        """初始化复杂任务包装器
        
        Args:
            mcp_manager: MCP 客户端管理器
            llm_client: LLM 客户端，用于结果解释
        """
        super().__init__(mcp_manager)
        self.llm_client = llm_client
        self._llm_initialized = False
    
    async def _ensure_llm(self) -> bool:
        """确保 LLM 客户端已初始化
        
        Returns:
            是否成功初始化
        """
        if self._llm_initialized and self.llm_client:
            return True
        
        try:
            # 尝试从基础设施导入 KimiClient
            from flood_decision_agent.infrastructure.llm.kimi_client import (
                KimiClient,
                get_kimi_client,
            )
            
            self.llm_client = get_kimi_client()
            self._llm_initialized = True
            self.logger.debug("LLM 客户端已初始化")
            return True
            
        except Exception as e:
            self.logger.warning(f"LLM 客户端初始化失败: {e}")
            return False
    
    async def _explain_with_llm(
        self,
        tool_name: str,
        raw_result: Dict[str, Any]
    ) -> Optional[str]:
        """使用 LLM 解释结果
        
        Args:
            tool_name: 工具名称
            raw_result: 原始结果
            
        Returns:
            LLM 解释文本，如果失败则返回 None
        """
        if not await self._ensure_llm():
            return None
        
        # 获取提示词模板
        prompt = PromptManager.format_prompt(
            tool_name,
            simulation_results=json.dumps(raw_result, ensure_ascii=False, indent=2),
            calculation_results=json.dumps(raw_result, ensure_ascii=False, indent=2),
            rainfall_data=json.dumps(raw_result, ensure_ascii=False, indent=2),
            dispatch_plan=json.dumps(raw_result, ensure_ascii=False, indent=2),
            data_result=json.dumps(raw_result, ensure_ascii=False, indent=2),
        )
        
        if prompt is None:
            # 没有对应的提示词模板，使用通用解释
            prompt = f"""请解释以下数据结果：

{json.dumps(raw_result, ensure_ascii=False, indent=2)}

请给出简洁的总结。"""
        
        try:
            # 调用 LLM 进行解释
            messages = [
                {"role": "system", "content": "你是一位专业的水利决策支持助手。"},
                {"role": "user", "content": prompt},
            ]
            
            explanation = await self.llm_client.chat(messages, temperature=0.3)
            return explanation
            
        except Exception as e:
            self.logger.error(f"LLM 解释失败: {e}")
            return None
    
    async def execute(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工具调用（带 LLM 解释）
        
        Args:
            server_name: MCP Server 名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            包装后的执行结果，包含原始数据和 LLM 解释
        """
        self.logger.debug(f"复杂任务: {server_name}.{tool_name}")
        
        # 1. 调用 Server 获取原始数据
        raw_result = await self._call_tool(server_name, tool_name, arguments)
        
        # 2. LLM 包装生成解释
        explanation = await self._explain_with_llm(tool_name, raw_result)
        
        # 3. 合并返回
        return {
            "success": True,
            "raw_data": raw_result,
            "explanation": explanation,
            "summary": self._generate_summary(raw_result, explanation),
            "wrapped": True,
            "server": server_name,
            "tool": tool_name,
        }
    
    def _generate_summary(
        self,
        raw_result: Dict[str, Any],
        explanation: Optional[str]
    ) -> str:
        """生成综合摘要
        
        Args:
            raw_result: 原始结果
            explanation: LLM 解释
            
        Returns:
            综合摘要
        """
        if explanation:
            # 从解释中提取第一句话作为摘要
            lines = explanation.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('【') and not line.startswith('['):
                    # 提取 "一句话总结:" 后面的内容
                    if '一句话总结:' in line:
                        return line.split('一句话总结:')[-1].strip()
                    # 否则返回第一行非空内容
                    if len(line) > 10:
                        return line[:100] + '...' if len(line) > 100 else line
        
        # 如果没有解释，从原始结果生成简单摘要
        if isinstance(raw_result, dict):
            if 'message' in raw_result:
                return str(raw_result['message'])
            if 'status' in raw_result:
                return f"执行状态: {raw_result['status']}"
        
        return "执行完成"
    
    async def run_simulation(self, server_name: str = "hipims", **kwargs) -> Dict[str, Any]:
        """便捷方法：运行模拟
        
        Args:
            server_name: MCP Server 名称
            **kwargs: 模拟参数
            
        Returns:
            包装后的执行结果
        """
        return await self.execute(server_name, "run_2d_simulation", kwargs)


class MCPWrapperFactory:
    """MCP 包装器工厂
    
    根据工具类型自动选择合适的包装器。
    """
    
    def __init__(self, mcp_manager: MCPClientManager, llm_client: Optional[Any] = None):
        """初始化工厂
        
        Args:
            mcp_manager: MCP 客户端管理器
            llm_client: LLM 客户端
        """
        self.mcp_manager = mcp_manager
        self.llm_client = llm_client
        self.logger = logger.bind(name="MCPWrapperFactory")
        
        # 缓存包装器实例
        self._simple_wrapper: Optional[SimpleClientWrapper] = None
        self._complex_wrapper: Optional[ComplexClientWrapper] = None
    
    def _get_simple_wrapper(self) -> SimpleClientWrapper:
        """获取简单包装器实例"""
        if self._simple_wrapper is None:
            self._simple_wrapper = SimpleClientWrapper(self.mcp_manager)
        return self._simple_wrapper
    
    def _get_complex_wrapper(self) -> ComplexClientWrapper:
        """获取复杂包装器实例"""
        if self._complex_wrapper is None:
            self._complex_wrapper = ComplexClientWrapper(self.mcp_manager, self.llm_client)
        return self._complex_wrapper
    
    def get_wrapper(self, tool_name: str) -> BaseMCPWrapper:
        """根据工具名称获取合适的包装器
        
        Args:
            tool_name: 工具名称
            
        Returns:
            合适的包装器实例
        """
        # 判断工具复杂度
        if PromptManager.is_complex_tool(tool_name):
            self.logger.debug(f"为 {tool_name} 选择复杂包装器")
            return self._get_complex_wrapper()
        
        if PromptManager.is_simple_tool(tool_name):
            self.logger.debug(f"为 {tool_name} 选择简单包装器")
            return self._get_simple_wrapper()
        
        # 默认使用简单包装器
        self.logger.debug(f"为 {tool_name} 使用默认简单包装器")
        return self._get_simple_wrapper()
    
    async def execute(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """自动选择包装器并执行
        
        Args:
            server_name: MCP Server 名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            执行结果
        """
        wrapper = self.get_wrapper(tool_name)
        return await wrapper.execute(server_name, tool_name, arguments)


class MCPWrappedClientManager:
    """带包装器的 MCP 客户端管理器
    
    在原有 MCPClientManager 基础上添加结果包装功能。
    """
    
    def __init__(
        self,
        mcp_manager: Optional[MCPClientManager] = None,
        llm_client: Optional[Any] = None,
        auto_load_config: bool = True,
    ):
        """初始化
        
        Args:
            mcp_manager: MCP 客户端管理器，为 None 时创建新实例
            llm_client: LLM 客户端
            auto_load_config: 是否自动加载配置
        """
        self.mcp_manager = mcp_manager or MCPClientManager(auto_load_config=auto_load_config)
        self.wrapper_factory = MCPWrapperFactory(self.mcp_manager, llm_client)
        self.logger = logger.bind(name="MCPWrappedClientManager")
    
    async def connect_all(self) -> int:
        """连接所有 Server"""
        return await self.mcp_manager.connect_all()
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        wrap_result: bool = True,
    ) -> Dict[str, Any]:
        """调用工具（支持结果包装）
        
        Args:
            server_name: MCP Server 名称
            tool_name: 工具名称
            arguments: 工具参数
            wrap_result: 是否包装结果
            
        Returns:
            执行结果
        """
        if not wrap_result:
            # 直接透传，不包装
            return await self.mcp_manager.call_tool(server_name, tool_name, arguments)
        
        # 使用包装器
        return await self.wrapper_factory.execute(server_name, tool_name, arguments)
    
    async def call_tool_auto(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        wrap_result: bool = True,
    ) -> Dict[str, Any]:
        """自动查找并调用工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            wrap_result: 是否包装结果
            
        Returns:
            执行结果
        """
        # 查找工具所在的 Server
        for server_name, client in self.mcp_manager.clients.items():
            if any(t.name == tool_name for t in client.tools):
                return await self.call_tool(server_name, tool_name, arguments, wrap_result)
        
        raise ValueError(f"未找到工具: {tool_name}")
    
    def list_all_tools(self) -> List[Any]:
        """列出所有可用工具"""
        return self.mcp_manager.list_all_tools()
    
    async def close_all(self):
        """关闭所有连接"""
        await self.mcp_manager.close_all()


# 便捷函数

async def call_tool_with_wrapper(
    server_name: str,
    tool_name: str,
    arguments: Dict[str, Any],
    mcp_manager: Optional[MCPClientManager] = None,
    llm_client: Optional[Any] = None,
) -> Dict[str, Any]:
    """使用包装器调用工具
    
    Args:
        server_name: MCP Server 名称
        tool_name: 工具名称
        arguments: 工具参数
        mcp_manager: MCP 客户端管理器
        llm_client: LLM 客户端
        
    Returns:
        包装后的执行结果
    """
    manager = mcp_manager or MCPClientManager()
    factory = MCPWrapperFactory(manager, llm_client)
    return await factory.execute(server_name, tool_name, arguments)
