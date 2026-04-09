"""MCP 工具基类

提供通用的 MCP 工具抽象基类，自动处理：
- 工具执行结果写入共享数据池
- 统一的错误处理
- 日志记录
- 参数准备和结果格式化
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic

from mcp.types import TextContent

from src.flood_decision_agent.mcp.log import get_mcp_logger, ToolCallContext
from src.flood_decision_agent.mcp.log.error_formatter import format_error as format_error_dict
from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps

T = TypeVar('T')


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "success": self.success,
            "timestamp": self.timestamp,
            "execution_time_ms": self.execution_time_ms,
        }
        if self.success:
            result["data"] = self.data
        else:
            result["error"] = self.error
            result["error_type"] = self.error_type
            result["metadata"] = self.metadata
        return result

    def to_text_content(self) -> TextContent:
        return TextContent(
            type="text",
            text=fast_json_dumps(self.to_dict(), ensure_ascii=False, indent=2)
        )


class MCPToolBase(ABC):
    """MCP 工具基类
    
    提供标准化的工具执行框架，自动处理：
    - 日志记录
    - 错误处理
    - 结果写入数据池
    """

    def __init__(self, server_name: str, tool_name: str):
        self.server_name = server_name
        self.tool_name = tool_name
        self.logger = get_mcp_logger(server_name)

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """执行工具逻辑
        
        Args:
            arguments: 工具参数
            
        Returns:
            ToolResult: 工具执行结果
        """
        pass

    async def call(self, arguments: Dict[str, Any], data_pool: Optional[Any] = None) -> List[TextContent]:
        """调用工具（带日志和错误处理）
        
        Args:
            arguments: 工具参数
            data_pool: 可选的共享数据池
            
        Returns:
            List[TextContent]: MCP 响应
        """
        with ToolCallContext(self.server_name, self.tool_name, arguments, self.logger):
            try:
                result = await self.execute(arguments)
                
                if data_pool and result.success:
                    self._write_to_pool(data_pool, result)
                
                return [result.to_text_content()]
                
            except Exception as e:
                self.logger.error(f"工具 {self.tool_name} 执行失败: {e}")
                error_dict = format_error_dict(e, self.server_name, self.tool_name, arguments)
                return [TextContent(
                    type="text",
                    text=fast_json_dumps(error_dict, ensure_ascii=False)
                )]

    def _write_to_pool(self, data_pool: Any, result: ToolResult) -> None:
        """写入共享数据池
        
        Args:
            data_pool: 共享数据池实例
            result: 工具执行结果
        """
        try:
            if hasattr(data_pool, 'put'):
                key = self._generate_pool_key(result)
                data_pool.put(key, result.to_dict())
                self.logger.debug(f"结果写入数据池: {key}")
        except Exception as e:
            self.logger.warning(f"写入数据池失败: {e}")

    def _generate_pool_key(self, result: ToolResult) -> str:
        """生成数据池键名
        
        Args:
            result: 工具执行结果
            
        Returns:
            str: 键名
        """
        return f"{self.server_name}:{self.tool_name}:{result.timestamp}"


class ToolExecutor:
    """工具执行器
    
    封装工具执行逻辑，支持数据池写入和结果缓存。
    """

    def __init__(self, server_name: str, tool_handlers: Dict[str, Callable]):
        self.server_name = server_name
        self.tool_handlers = tool_handlers
        self.logger = get_mcp_logger(server_name)

    async def execute(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any],
        data_pool: Optional[Any] = None
    ) -> List[TextContent]:
        """执行工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            data_pool: 共享数据池
            
        Returns:
            List[TextContent]: 执行结果
        """
        if tool_name not in self.tool_handlers:
            error = ValueError(f"未知工具: {tool_name}")
            error_dict = format_error_dict(error, self.server_name, tool_name, arguments)
            return [TextContent(
                type="text",
                text=fast_json_dumps(error_dict, ensure_ascii=False)
            )]

        handler = self.tool_handlers[tool_name]
        
        with ToolCallContext(self.server_name, tool_name, arguments, self.logger):
            try:
                start_time = time.perf_counter()
                result = await handler(arguments)
                execution_time = (time.perf_counter() - start_time) * 1000
                
                if data_pool and isinstance(result, dict):
                    self._write_result_to_pool(data_pool, tool_name, result)
                
                self.logger.info(
                    f"工具 {tool_name} 执行成功 | 耗时: {execution_time:.2f}ms"
                )
                
                if isinstance(result, dict):
                    return [TextContent(
                        type="text",
                        text=fast_json_dumps(result, ensure_ascii=False, indent=2)
                    )]
                elif isinstance(result, list):
                    return result
                else:
                    return [TextContent(type="text", text=str(result))]
                    
            except Exception as e:
                self.logger.error(f"工具 {tool_name} 执行失败: {e}")
                error_dict = format_error_dict(e, self.server_name, tool_name, arguments)
                return [TextContent(
                    type="text",
                    text=fast_json_dumps(error_dict, ensure_ascii=False)
                )]

    def _write_result_to_pool(
        self, 
        data_pool: Any, 
        tool_name: str, 
        result: Dict[str, Any]
    ) -> None:
        """写入结果到数据池"""
        try:
            if hasattr(data_pool, 'put'):
                key = f"{self.server_name}:{tool_name}"
                data_pool.put(key, result)
                self.logger.debug(f"结果写入数据池: {key}")
        except Exception as e:
            self.logger.warning(f"写入数据池失败: {e}")


def create_error_response(
    error: Exception,
    server_name: str,
    tool_name: str,
    arguments: Optional[Dict[str, Any]] = None
) -> List[TextContent]:
    """创建错误响应
    
    Args:
        error: 异常对象
        server_name: 服务器名称
        tool_name: 工具名称
        arguments: 工具参数
        
    Returns:
        List[TextContent]: 错误响应
    """
    error_dict = format_error_dict(error, server_name, tool_name, arguments)
    return [TextContent(
        type="text",
        text=fast_json_dumps(error_dict, ensure_ascii=False)
    )]
