"""核心模块.

提供Agent基础类、消息系统、任务图数据结构和任务分解功能。
"""

# 从 agents/base 重导出
from flood_decision_agent.agents.base.agent import BaseAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import Node, NodeStatus, TaskGraph
from flood_decision_agent.core.task_graph_builder import TaskChainItem, TaskGraphBuilder

# 从 agents/decision_chain 重导出
from flood_decision_agent.agents.decision_chain.task_decomposer import (
    DecompositionRule,
    DecompositionRuleLibrary,
    TaskDecomposer,
    TaskNodeInfo,
    TaskType,
)
from flood_decision_agent.agents.decision_chain.chain_optimizer import (
    BottleneckInfo,
    ChainAlternative,
    ChainOptimizer,
)

# 从 agents/intent_parser 重导出
from flood_decision_agent.agents.intent_parser.parser import IntentParser, TaskIntent

__all__ = [
    "BaseAgent",
    "BaseMessage",
    "MessageType",
    "SharedDataPool",
    "Node",
    "NodeStatus",
    "TaskGraph",
    "TaskGraphBuilder",
    "TaskChainItem",
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
]
