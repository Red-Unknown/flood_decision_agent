"""测试场景基类模块.

定义测试场景的抽象基类和通用接口。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from flood_decision_agent.evaluation.test_cases import TestCase, TestSuite


@dataclass
class ScenarioContext:
    """场景上下文.

    保存场景执行过程中的状态和数据。
    """

    scenario_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)

    def set(self, key: str, value: Any) -> None:
        """设置状态值."""
        self.state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取状态值."""
        return self.state.get(key, default)

    def add_artifact(self, path: str) -> None:
        """添加产物路径."""
        self.artifacts.append(path)


class BaseScenario(ABC):
    """测试场景基类.

    所有具体场景实现都应继承此类。
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.context: Optional[ScenarioContext] = None

    @abstractmethod
    def setup(self, context: ScenarioContext) -> None:
        """场景设置.

        在执行测试前进行必要的初始化。

        Args:
            context: 场景上下文
        """
        pass

    @abstractmethod
    def create_test_suite(self) -> TestSuite:
        """创建测试集.

        Returns:
            该场景对应的测试集
        """
        pass

    @abstractmethod
    def teardown(self, context: ScenarioContext) -> None:
        """场景清理.

        在测试执行完成后进行清理工作。

        Args:
            context: 场景上下文
        """
        pass

    def validate_prerequisites(self) -> bool:
        """验证前置条件.

        Returns:
            是否满足前置条件
        """
        return True

    def get_metadata(self) -> Dict[str, Any]:
        """获取场景元数据.

        Returns:
            元数据字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
        }


class ScenarioRegistry:
    """场景注册表.

    管理所有可用的测试场景。
    """

    _scenarios: Dict[str, type[BaseScenario]] = {}

    @classmethod
    def register(cls, name: str, scenario_class: type[BaseScenario]) -> None:
        """注册场景."""
        cls._scenarios[name] = scenario_class

    @classmethod
    def get(cls, name: str) -> Optional[type[BaseScenario]]:
        """获取场景类."""
        return cls._scenarios.get(name)

    @classmethod
    def list_scenarios(cls) -> List[str]:
        """列出所有已注册场景."""
        return list(cls._scenarios.keys())

    @classmethod
    def create(cls, name: str, **kwargs) -> Optional[BaseScenario]:
        """创建场景实例."""
        scenario_class = cls.get(name)
        if scenario_class:
            return scenario_class(**kwargs)
        return None
