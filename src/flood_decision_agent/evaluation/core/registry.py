"""评估注册表 - 管理评估组件注册.

提供插件式架构用于扩展评估功能。
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from flood_decision_agent.infra.logging import get_logger

T = TypeVar("T")


class ComponentRegistry:
    """组件注册表.

    管理评估相关组件的注册和发现：
    - 指标计算器
    - 测试加载器
    - 报告格式化器
    - 验证器
    """

    def __init__(self):
        self.logger = get_logger().bind(name=self.__class__.__name__)
        self._metrics: Dict[str, Type] = {}
        self._loaders: Dict[str, Type] = {}
        self._formatters: Dict[str, Type] = {}
        self._validators: Dict[str, Callable] = {}
        self._hooks: Dict[str, List[Callable]] = {}

    # ========== 指标注册 ==========

    def register_metric(
        self,
        name: str,
        metric_class: Type,
        override: bool = False,
    ) -> None:
        """注册指标类.

        Args:
            name: 指标名称
            metric_class: 指标类
            override: 是否覆盖已存在的注册
        """
        if name in self._metrics and not override:
            self.logger.warning(f"指标 {name} 已存在，使用 override=True 覆盖")
            return

        self._metrics[name] = metric_class
        self.logger.debug(f"注册指标: {name}")

    def get_metric(self, name: str) -> Optional[Type]:
        """获取指标类."""
        return self._metrics.get(name)

    def list_metrics(self) -> List[str]:
        """列出所有已注册指标."""
        return list(self._metrics.keys())

    def create_metric(self, name: str, *args, **kwargs) -> Any:
        """创建指标实例."""
        metric_class = self.get_metric(name)
        if metric_class is None:
            raise ValueError(f"未找到指标: {name}")
        return metric_class(*args, **kwargs)

    # ========== 加载器注册 ==========

    def register_loader(
        self,
        name: str,
        loader_class: Type,
        override: bool = False,
    ) -> None:
        """注册测试加载器."""
        if name in self._loaders and not override:
            self.logger.warning(f"加载器 {name} 已存在，使用 override=True 覆盖")
            return

        self._loaders[name] = loader_class
        self.logger.debug(f"注册加载器: {name}")

    def get_loader(self, name: str) -> Optional[Type]:
        """获取加载器类."""
        return self._loaders.get(name)

    def list_loaders(self) -> List[str]:
        """列出所有已注册加载器."""
        return list(self._loaders.keys())

    # ========== 格式化器注册 ==========

    def register_formatter(
        self,
        name: str,
        formatter_class: Type,
        override: bool = False,
    ) -> None:
        """注册报告格式化器."""
        if name in self._formatters and not override:
            self.logger.warning(f"格式化器 {name} 已存在，使用 override=True 覆盖")
            return

        self._formatters[name] = formatter_class
        self.logger.debug(f"注册格式化器: {name}")

    def get_formatter(self, name: str) -> Optional[Type]:
        """获取格式化器类."""
        return self._formatters.get(name)

    def list_formatters(self) -> List[str]:
        """列出所有已注册格式化器."""
        return list(self._formatters.keys())

    # ========== 验证器注册 ==========

    def register_validator(
        self,
        name: str,
        validator: Callable,
        override: bool = False,
    ) -> None:
        """注册结果验证器."""
        if name in self._validators and not override:
            self.logger.warning(f"验证器 {name} 已存在，使用 override=True 覆盖")
            return

        self._validators[name] = validator
        self.logger.debug(f"注册验证器: {name}")

    def get_validator(self, name: str) -> Optional[Callable]:
        """获取验证器."""
        return self._validators.get(name)

    def list_validators(self) -> List[str]:
        """列出所有已注册验证器."""
        return list(self._validators.keys())

    def validate(self, name: str, *args, **kwargs) -> bool:
        """执行验证."""
        validator = self.get_validator(name)
        if validator is None:
            raise ValueError(f"未找到验证器: {name}")
        return validator(*args, **kwargs)

    # ========== Hook 机制 ==========

    def register_hook(self, event: str, callback: Callable) -> None:
        """注册事件钩子.

        Args:
            event: 事件名称
            callback: 回调函数
        """
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)
        self.logger.debug(f"注册钩子: {event}")

    def unregister_hook(self, event: str, callback: Callable) -> None:
        """注销事件钩子."""
        if event in self._hooks and callback in self._hooks[event]:
            self._hooks[event].remove(callback)

    def trigger_hook(self, event: str, *args, **kwargs) -> List[Any]:
        """触发事件钩子.

        Returns:
            所有回调函数的返回值列表
        """
        results = []
        for callback in self._hooks.get(event, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"钩子执行失败 {event}: {e}")
        return results

    # ========== 批量操作 ==========

    def register_defaults(self) -> None:
        """注册默认组件."""
        # 注册默认指标
        from flood_decision_agent.evaluation.metrics import (
            AutonomyMetrics,
            EffectivenessMetrics,
            EfficiencyMetrics,
            ExplainabilityMetrics,
            RobustnessMetrics,
            SafetyMetrics,
        )

        self.register_metric("effectiveness", EffectivenessMetrics)
        self.register_metric("efficiency", EfficiencyMetrics)
        self.register_metric("robustness", RobustnessMetrics)
        self.register_metric("safety", SafetyMetrics)
        self.register_metric("autonomy", AutonomyMetrics)
        self.register_metric("explainability", ExplainabilityMetrics)

        self.logger.info("默认组件注册完成")


# 全局注册表实例
_registry: Optional[ComponentRegistry] = None


def get_registry() -> ComponentRegistry:
    """获取全局注册表实例."""
    global _registry
    if _registry is None:
        _registry = ComponentRegistry()
        _registry.register_defaults()
    return _registry


def reset_registry() -> None:
    """重置全局注册表."""
    global _registry
    _registry = None
