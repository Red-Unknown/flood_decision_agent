"""决策链生成模块.

提供决策链生成、优化和任务分解功能。
"""

from flood_decision_agent.agents.decision_chain.chain_generator import (
    ChainGenerator,
    GenerationEvent,
    GenerationResult,
    GenerationStage,
)
from flood_decision_agent.agents.decision_chain.chain_optimizer import (
    BottleneckInfo,
    ChainAlternative,
    ChainOptimizer,
)
from flood_decision_agent.agents.decision_chain.checkpoint_agent import (
    Checkpoint,
    CheckpointResumptionAgent,
    CheckpointStatus,
    CheckpointStorage,
    InterruptionReason,
    MemoryCheckpointStorage,
)
from flood_decision_agent.agents.decision_chain.heuristic_optimizer import HeuristicOptimizer
from flood_decision_agent.agents.decision_chain.unified_optimizer import (
    UnifiedOptimizer,
    SimpleOptimizer,
    PlanOptimizer,
)
from flood_decision_agent.agents.decision_chain.generator import (
    DecisionChainGeneratorAgent,
    DecisionPipeline,
)
from flood_decision_agent.agents.decision_chain.mode_detector import (
    ComplexityMetrics,
    ModeDetector,
    ModeType,
)
from flood_decision_agent.agents.prompts import (
    DocumentType,
    PlanSpecPrompts,
    PromptContext,
    BasePrompts,
    get_system_prompt,
)

# 向后兼容：PromptTemplates 是 BasePrompts 的别名
PromptTemplates = BasePrompts
from flood_decision_agent.agents.decision_chain.task_decomposer import (
    DecompositionRule,
    DecompositionRuleLibrary,
    TaskDecomposer,
    TaskNodeInfo,
    TaskType,
)
from flood_decision_agent.agents.decision_chain.task_extractor import (
    TaskExtractor,
    ExtractedTask,
    ExtractionResult,
    ExtractionStrategy,
)
from flood_decision_agent.agents.decision_chain.cancel_handler import (
    CancelHandler,
    CancelCommandType,
    CancelState,
    ModificationRequest,
    ModeType as CancelModeType,
)

__all__ = [
    # 生成器（流式）
    "ChainGenerator",
    "GenerationEvent",
    "GenerationResult",
    "GenerationStage",
    # 基础生成器
    "DecisionChainGeneratorAgent",
    "DecisionPipeline",
    # 断点续传
    "CheckpointResumptionAgent",
    "Checkpoint",
    "CheckpointStatus",
    "CheckpointStorage",
    "MemoryCheckpointStorage",
    "InterruptionReason",
    # 链路优化
    "ChainOptimizer",
    "ChainAlternative",
    "BottleneckInfo",
    "SimpleOptimizer",
    "PlanOptimizer",
    "HeuristicOptimizer",
    "UnifiedOptimizer",
    # 任务分解
    "TaskDecomposer",
    "TaskNodeInfo",
    "TaskType",
    "DecompositionRule",
    "DecompositionRuleLibrary",
    # 任务提取
    "TaskExtractor",
    "ExtractedTask",
    "ExtractionResult",
    "ExtractionStrategy",
    # 提示词
    "PromptTemplates",
    "get_system_prompt",
    # Plan/Spec 模式
    "DocumentType",
    "PlanSpecPrompts",
    "PromptContext",
    "get_prompt_for_mode",
    # 模式识别器
    "ModeDetector",
    "ModeType",
    "ComplexityMetrics",
    # 取消处理
    "CancelHandler",
    "CancelCommandType",
    "CancelState",
    "ModificationRequest",
    "CancelModeType",
]
