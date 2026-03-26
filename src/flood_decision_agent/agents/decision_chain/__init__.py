"""决策链生成模块.

提供决策链生成、优化和任务分解功能。
"""

from flood_decision_agent.agents.decision_chain.chain_optimizer import (
    BottleneckInfo,
    ChainAlternative,
    ChainOptimizer,
)
from flood_decision_agent.agents.decision_chain.generator import (
    DecisionChainGeneratorAgent,
    DecisionPipeline,
)
from flood_decision_agent.agents.decision_chain.prompts import (
    PromptTemplates,
    get_system_prompt,
)
from flood_decision_agent.agents.decision_chain.task_decomposer import (
    DecompositionRule,
    DecompositionRuleLibrary,
    TaskDecomposer,
    TaskNodeInfo,
    TaskType,
)

__all__ = [
    # 生成器
    "DecisionChainGeneratorAgent",
    "DecisionPipeline",
    # 链路优化
    "ChainOptimizer",
    "ChainAlternative",
    "BottleneckInfo",
    # 任务分解
    "TaskDecomposer",
    "TaskNodeInfo",
    "TaskType",
    "DecompositionRule",
    "DecompositionRuleLibrary",
    # 提示词
    "PromptTemplates",
    "get_system_prompt",
]
