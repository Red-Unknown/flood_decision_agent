"""核心模块.

提供Agent基础类、消息系统、任务图数据结构和任务分解功能。
"""

from flood_decision_agent.core.agent import BaseAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import Node, NodeStatus, TaskGraph
from flood_decision_agent.core.task_decomposer import (
    DecompositionRule,
    DecompositionRuleLibrary,
    TaskDecomposer,
    TaskNodeInfo,
    TaskType,
)
from flood_decision_agent.core.chain_optimizer import (
    BottleneckInfo,
    ChainAlternative,
    ChainOptimizer,
)
from flood_decision_agent.core.intent_parser import IntentParser, TaskIntent
from flood_decision_agent.core.task_graph_builder import TaskGraphBuilder, TaskChainItem

__all__ = [
    "BaseAgent",
    "BaseMessage",
    "MessageType",
    "SharedDataPool",
    "Node",
    "NodeStatus",
    "TaskGraph",
    "TaskDecomposer",
    "TaskNodeInfo",
    "TaskType",
    "DecompositionRule",
    "DecompositionRuleLibrary",
    "ChainOptimizer",
    "ChainAlternative",
    "BottleneckInfo",
    "IntentParser",
    "TaskIntent",
    "TaskGraphBuilder",
    "TaskChainItem",
]
