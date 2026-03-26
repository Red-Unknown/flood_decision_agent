"""Agent 模块.

提供洪水调度决策系统的各类 Agent 实现。

目录结构:
    base/: Agent 基类和执行策略接口
    decision_chain/: 决策链生成和优化
    node_scheduler/: 节点调度和任务图执行
    task_executor/: 单元任务执行
    intent_parser/: 意图解析
"""

# 从子模块重导出主要类
from flood_decision_agent.agents.base import (
    AgentStatus,
    BaseAgent,
    DefaultExecutionStrategy,
    ExecutionStrategy,
)
from flood_decision_agent.agents.decision_chain import (
    BottleneckInfo,
    ChainAlternative,
    ChainOptimizer,
    DecisionChainGeneratorAgent,
    DecisionPipeline,
    DecompositionRule,
    DecompositionRuleLibrary,
    PromptTemplates,
    TaskDecomposer,
    TaskNodeInfo,
    TaskType,
    get_system_prompt,
)
from flood_decision_agent.agents.intent_parser import (
    IntentParser,
    IntentParserV2,
    TaskIntent,
)
from flood_decision_agent.agents.node_scheduler import NodeSchedulerAgent
from flood_decision_agent.agents.task_executor import (
    UnitTaskExecutionAgent,
    build_default_handlers,
)

__all__ = [
    # base
    "AgentStatus",
    "BaseAgent",
    "ExecutionStrategy",
    "DefaultExecutionStrategy",
    # decision_chain
    "DecisionChainGeneratorAgent",
    "DecisionPipeline",
    "ChainOptimizer",
    "ChainAlternative",
    "BottleneckInfo",
    "TaskDecomposer",
    "TaskNodeInfo",
    "TaskType",
    "DecompositionRule",
    "DecompositionRuleLibrary",
    "PromptTemplates",
    "get_system_prompt",
    # intent_parser
    "IntentParser",
    "IntentParserV2",
    "TaskIntent",
    # node_scheduler
    "NodeSchedulerAgent",
    # task_executor
    "UnitTaskExecutionAgent",
    "build_default_handlers",
]
