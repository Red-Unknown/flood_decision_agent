from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from flood_decision_agent.core.parameter_types import ParameterRequirement


@dataclass
class ToolCandidate:
    """工具候选（轻量级元数据）
    
    TaskDecomposer 为任务节点推荐的工具候选。
    包含工具名称、优先级、推荐理由和参数需求。
    
    Attributes:
        tool_name: 工具名称
        priority: 优先级 0-100，越高越优先
        reason: 推荐理由（用于调试和透明度）
        param_requirements: 该工具的参数需求列表
    """

    tool_name: str
    priority: int = 50
    reason: str = ""
    param_requirements: List[ParameterRequirement] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "tool_name": self.tool_name,
            "priority": self.priority,
            "reason": self.reason,
            "param_requirements": [p.to_dict() for p in self.param_requirements],
        }

    def __lt__(self, other: "ToolCandidate") -> bool:
        """用于排序比较"""
        return self.priority < other.priority

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ToolCandidate):
            return NotImplemented
        return self.tool_name == other.tool_name

    def __hash__(self) -> int:
        return hash(self.tool_name)
