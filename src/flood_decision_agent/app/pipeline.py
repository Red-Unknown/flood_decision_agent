from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flood_decision_agent.agents.decision_chain_generator import (
    DecisionChainGeneratorAgent,
)
from flood_decision_agent.agents.node_scheduler import NodeSchedulerAgent
from flood_decision_agent.agents.unit_task_executor import (
    UnitTaskExecutionAgent,
    build_default_handlers,
)
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.data.mock_data import MockDataGenerator
from flood_decision_agent.fusion.decision_fusion import DecisionFusion


@dataclass(frozen=True)
class PipelineResult:
    data_pool_snapshot: dict[str, Any]


def run_minimal_pipeline(
    task_request: dict[str, Any], seed: int = 42
) -> PipelineResult:
    mock_generator = MockDataGenerator(seed=seed)
    fusion = DecisionFusion()
    executor = UnitTaskExecutionAgent(
        handlers=build_default_handlers(mock_generator=mock_generator),
        fusion=fusion,
    )
    scheduler = NodeSchedulerAgent(executor=executor)
    chain_generator = DecisionChainGeneratorAgent()

    graph = chain_generator.generate(task=task_request)
    data_pool = SharedDataPool()
    scheduler.run(graph=graph, data_pool=data_pool)

    return PipelineResult(data_pool_snapshot=data_pool.snapshot())
