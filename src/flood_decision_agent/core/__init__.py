"""核心模块.

提供消息系统、任务图数据结构和任务分解功能。
"""

from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import Node, NodeStatus, TaskGraph
from flood_decision_agent.core.task_graph_builder import TaskChainItem, TaskGraphBuilder

__all__ = [
    "BaseMessage",
    "MessageType",
    "SharedDataPool",
    "Node",
    "NodeStatus",
    "TaskGraph",
    "TaskGraphBuilder",
    "TaskChainItem",
]
