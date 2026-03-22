"""LLM 工具模块 - 支持官方工具和自定义工具.

参照 Kimi 官方文档实现:
- 官方工具: web_search 等
- 自定义工具: function 类型
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable

from openai import OpenAI


@dataclass
class ToolResult:
    """工具执行结果."""
    success: bool
    output: Any = None
    error_message: Optional[str] = None


class BaseTool(ABC):
    """工具基类."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def get_tool_definition(self) -> Dict[str, Any]:
        """获取工具定义（用于 LLM 的 tools 参数）."""
        pass

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """执行工具."""
        pass


class FunctionTool(BaseTool):
    """自定义 Function 工具.

    使用标准的 function 类型，兼容 OpenAI API。
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
    ):
        super().__init__(name, description)
        self.parameters = parameters
        self.handler = handler

    def get_tool_definition(self) -> Dict[str, Any]:
        """获取 function 类型工具定义."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """执行 function 工具."""
        try:
            result = self.handler(arguments)
            return ToolResult(success=True, output=result)
        except Exception as e:
            return ToolResult(success=False, error_message=str(e))


class OfficialTool(BaseTool):
    """Kimi 官方工具基类.

    官方工具通过 formula URI 调用，如 moonshot/web-search:latest
    """

    def __init__(self, name: str, description: str, formula_uri: str):
        super().__init__(name, description)
        self.formula_uri = formula_uri

    def get_tool_definition(self) -> Dict[str, Any]:
        """获取官方工具定义.

        官方工具在 API 中也是作为 function 类型，但 name 需要唯一。
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """官方工具的执行在 LLM 侧完成，这里不需要实现."""
        # 官方工具由 LLM 自动调用，结果在响应中返回
        return ToolResult(success=True, output=None)


class WebSearchTool(OfficialTool):
    """Web 搜索工具."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="搜索互联网获取实时信息",
            formula_uri="moonshot/web-search:latest",
        )

    def get_tool_definition(self) -> Dict[str, Any]:
        """Web 搜索工具定义."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词",
                        },
                    },
                    "required": ["query"],
                },
            },
        }


class ToolRegistry:
    """工具注册表.

    管理所有可用工具，包括官方工具和自定义工具。
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._official_tools: Dict[str, str] = {}  # name -> formula_uri

    def register(self, tool: BaseTool) -> None:
        """注册工具."""
        self._tools[tool.name] = tool

    def register_official(self, name: str, formula_uri: str) -> None:
        """注册官方工具."""
        self._official_tools[name] = formula_uri

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具."""
        return self._tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        """获取所有自定义工具."""
        return list(self._tools.values())

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取所有工具定义（用于 LLM 请求）."""
        definitions = []
        for tool in self._tools.values():
            definitions.append(tool.get_tool_definition())
        return definitions

    def get_official_formula_uri(self, name: str) -> Optional[str]:
        """获取官方工具的 formula URI."""
        return self._official_tools.get(name)

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """执行工具."""
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, error_message=f"工具不存在: {name}")
        return tool.execute(arguments)


class LLMToolManager:
    """LLM 工具管理器.

    处理工具调用流程：
    1. 发送请求（带 tools 定义）
    2. 处理 tool_calls 响应
    3. 执行工具
    4. 继续对话
    """

    def __init__(self, client: OpenAI, tool_registry: Optional[ToolRegistry] = None):
        self.client = client
        self.tool_registry = tool_registry or ToolRegistry()
        self._init_default_tools()

    def _init_default_tools(self) -> None:
        """初始化默认工具."""
        # 注册 web_search 官方工具
        self.tool_registry.register_official("web_search", "moonshot/web-search:latest")
        # 注册 web_search 的 function 定义
        self.tool_registry.register(WebSearchTool())

    def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        model: str = "moonshot-v1-8k",
        temperature: float = 0.1,
        max_tokens: int = 800,
    ) -> str:
        """带工具调用的对话.

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度
            max_tokens: 最大 token 数

        Returns:
            最终响应内容
        """
        # 获取工具定义
        tools = self.tool_registry.get_tool_definitions()

        # 发送请求
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools if tools else None,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        message = response.choices[0].message

        # 检查是否需要调用工具
        if message.tool_calls:
            # 处理工具调用
            tool_messages = self._handle_tool_calls(message.tool_calls)

            # 将 assistant 消息和 tool 消息添加到对话
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })
            messages.extend(tool_messages)

            # 继续对话
            return self.chat_with_tools(messages, model, temperature, max_tokens)

        # 返回最终响应
        return message.content or ""

    def _handle_tool_calls(self, tool_calls: List[Any]) -> List[Dict[str, Any]]:
        """处理工具调用.

        Args:
            tool_calls: 工具调用列表

        Returns:
            tool 消息列表
        """
        tool_messages = []

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # 检查是否是官方工具
            formula_uri = self.tool_registry.get_official_formula_uri(tool_name)
            if formula_uri:
                # 官方工具：构造调用结果
                # 实际调用需要通过 Formula API
                tool_result = self._call_official_tool(formula_uri, arguments)
            else:
                # 自定义工具：直接执行
                result = self.tool_registry.execute_tool(tool_name, arguments)
                tool_result = result.output if result.success else result.error_message

            # 构造 tool 消息
            tool_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps({"result": tool_result}, ensure_ascii=False),
            })

        return tool_messages

    def _call_official_tool(self, formula_uri: str, arguments: Dict[str, Any]) -> Any:
        """调用官方工具.

        注意：这里简化处理，实际应该调用 Formula API
        """
        # 简化版本：直接返回提示信息
        # 实际应该调用 POST /formulas/{formula_uri}/fibers
        return f"[官方工具调用: {formula_uri}, 参数: {arguments}]"


# 便捷函数
def create_default_tool_manager(client: OpenAI) -> LLMToolManager:
    """创建默认工具管理器."""
    return LLMToolManager(client)
