"""Prompts 模块

集中管理所有 Agent 的提示词模板，便于维护和优化。
"""

from .base_prompts import BasePrompts, AgentRole, get_system_prompt
from .intent_parser_prompts import IntentParserPrompts
from .task_decomposer_prompts import TaskDecomposerPrompts
from .decision_generator_prompts import DecisionGeneratorPrompts
from .plan_spec_prompts import PlanSpecPrompts, DocumentType, PromptContext, get_prompt_for_mode
from .water_domain_prompts import (
    WaterDomainPrompts,
    ChainStage,
    DataSource,
    FeatureDefinition,
    IndexDefinition,
    DecisionRule,
    RuleType,
    ExpertRule,
    HistoricalCase,
    Regulation,
    AcceptanceCriterion,
)
from .chain_generation_prompts import ChainGenerationPrompts
from .task_extraction_prompts import TaskExtractionPrompts

__all__ = [
    "BasePrompts",
    "AgentRole",
    "get_system_prompt",
    "IntentParserPrompts",
    "TaskDecomposerPrompts",
    "DecisionGeneratorPrompts",
    "PlanSpecPrompts",
    "DocumentType",
    "PromptContext",
    "get_prompt_for_mode",
    "WaterDomainPrompts",
    "ChainStage",
    "DataSource",
    "FeatureDefinition",
    "IndexDefinition",
    "DecisionRule",
    "RuleType",
    "ExpertRule",
    "HistoricalCase",
    "Regulation",
    "AcceptanceCriterion",
    "ChainGenerationPrompts",
    "TaskExtractionPrompts",
]
