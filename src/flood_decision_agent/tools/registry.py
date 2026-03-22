"""工具注册中心 - 管理所有可用工具"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

from flood_decision_agent.core.shared_data_pool import SharedDataPool


@dataclass
class ToolMetadata:
    """工具元数据"""
    name: str
    description: str
    task_types: Set[str]  # 该工具支持的任务类型
    priority: int = 100  # 优先级，数字越小优先级越高
    config_schema: Dict[str, Any] = field(default_factory=dict)  # 配置参数schema
    required_keys: Set[str] = field(default_factory=set)  # 需要的输入数据key
    output_keys: Set[str] = field(default_factory=set)  # 输出的数据key


ToolFn = Callable[[SharedDataPool, Dict[str, Any]], Dict[str, Any]]


class ToolRegistry:
    """工具注册中心 - 支持动态注册和查询"""

    def __init__(self):
        self._tools: Dict[str, ToolFn] = {}
        self._metadata: Dict[str, ToolMetadata] = {}
        self._logger = None

    def set_logger(self, logger):
        """设置日志器"""
        self._logger = logger

    def register(
        self,
        name: str,
        handler: ToolFn,
        metadata: ToolMetadata,
    ) -> None:
        """注册工具"""
        if name in self._tools:
            if self._logger:
                self._logger.warning(f"工具 {name} 已存在，将被覆盖")

        self._tools[name] = handler
        self._metadata[name] = metadata

        if self._logger:
            self._logger.info(f"工具 {name} 注册成功，支持任务类型: {metadata.task_types}")

    def unregister(self, name: str) -> None:
        """注销工具"""
        if name in self._tools:
            del self._tools[name]
            del self._metadata[name]
            if self._logger:
                self._logger.info(f"工具 {name} 已注销")

    def get(self, name: str) -> Optional[ToolFn]:
        """获取工具处理器"""
        return self._tools.get(name)

    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        """获取工具元数据"""
        return self._metadata.get(name)

    def list_tools(self) -> List[str]:
        """列出所有已注册工具名称"""
        return list(self._tools.keys())

    def find_by_task_type(self, task_type: str) -> List[ToolMetadata]:
        """根据任务类型查找匹配的工具"""
        matching = []
        for name, meta in self._metadata.items():
            if task_type in meta.task_types:
                matching.append(meta)
        # 按优先级排序
        return sorted(matching, key=lambda x: x.priority)

    def is_available(self, name: str) -> bool:
        """检查工具是否可用"""
        return name in self._tools

    def validate_tool_config(self, name: str, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """验证工具配置是否合法"""
        meta = self.get_metadata(name)
        if not meta:
            return False, f"工具 {name} 不存在"

        # 简单的配置验证，可扩展为JSON Schema验证
        required_keys = set(meta.config_schema.get("required", []))
        provided_keys = set(config.keys())
        missing = required_keys - provided_keys

        if missing:
            return False, f"缺少必需配置项: {missing}"

        return True, None

    def execute(
        self,
        name: str,
        data_pool: SharedDataPool,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """执行指定工具"""
        tool = self.get(name)
        if not tool:
            raise KeyError(f"工具 {name} 未找到")

        config = config or {}

        # 验证配置
        valid, error = self.validate_tool_config(name, config)
        if not valid:
            raise ValueError(f"工具 {name} 配置验证失败: {error}")

        # 执行工具
        if self._logger:
            self._logger.debug(f"执行工具 {name}，配置: {config}")

        return tool(data_pool, config)


# 全局工具注册中心实例
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """获取全局工具注册中心"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def register_tool(metadata: ToolMetadata):
    """装饰器：注册工具到全局注册中心"""
    def decorator(func: ToolFn) -> ToolFn:
        registry = get_tool_registry()
        registry.register(metadata.name, func, metadata)
        return func
    return decorator
