"""
决策链生成器 - 支持生成器模式的流式生成

提供 ChainGenerator 类，支持 async generator 模式，
在决策链生成过程中 yield 中间状态，供 WebSocket 实时推送。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from flood_decision_agent.agents.decision_chain.generator import DecisionChainGeneratorAgent
from flood_decision_agent.agents.intent_parser.parser import IntentParser, TaskIntent
from flood_decision_agent.core.task_graph import TaskGraph
from flood_decision_agent.infra.logging import get_logger


class GenerationStage(str, Enum):
    """决策链生成阶段"""
    INTENT_PARSING = "intent_parsing"
    TASK_DECOMPOSITION = "task_decomposition"
    CHAIN_OPTIMIZATION = "chain_optimization"
    TASK_GRAPH_BUILDING = "task_graph_building"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class GenerationEvent:
    """生成事件"""
    stage: GenerationStage
    progress: float  # 0.0 - 1.0
    message: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResult:
    """生成结果"""
    task_graph: TaskGraph
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None


class ChainGenerator:
    """决策链生成器 - 支持流式生成
    
    使用生成器模式，在生成过程中 yield 中间状态事件，
    使 WebSocket 能够实时推送生成进度。
    
    支持三种模式：
    - 普通模式：从用户输入直接生成
    - Plan模式：从 Plan 文档提取任务后生成
    - Spec模式：从 Spec 文档提取任务后生成
    
    Example:
        ```python
        generator = ChainGenerator()
        
        async for event in generator.generate("查询今日水位"):
            print(f"阶段: {event.stage}, 进度: {event.progress}")
            # 通过 WebSocket 发送给前端
            
        # 获取最终结果
        result = generator.get_last_result()
        ```
    """

    def __init__(
        self,
        base_generator: Optional[DecisionChainGeneratorAgent] = None,
        intent_parser: Optional[IntentParser] = None,
    ):
        """初始化生成器
        
        Args:
            base_generator: 基础决策链生成器
            intent_parser: 意图解析器
        """
        self._logger = get_logger().bind(name=self.__class__.__name__)
        self._base_generator = base_generator or DecisionChainGeneratorAgent()
        self._intent_parser = intent_parser or IntentParser()
        self._last_result: Optional[GenerationResult] = None

    async def generate(
        self,
        user_input: str,
        input_type: str = "natural_language",
    ) -> AsyncGenerator[GenerationEvent, None]:
        """流式生成决策链 - 普通模式
        
        Args:
            user_input: 用户输入
            input_type: 输入类型
            
        Yields:
            GenerationEvent: 生成事件（阶段、进度、消息、数据）
        """
        try:
            # 阶段1: 意图解析
            yield GenerationEvent(
                stage=GenerationStage.INTENT_PARSING,
                progress=0.1,
                message="正在解析用户意图...",
            )
            
            # 在后台线程中执行意图解析，避免阻塞事件循环
            loop = asyncio.get_event_loop()
            intent = await loop.run_in_executor(
                None, 
                self._intent_parser.parse_natural_language, 
                user_input
            )
            
            # 检查意图解析错误
            if intent.error_message:
                # 先设置结果，再发送错误事件
                self._last_result = GenerationResult(
                    task_graph=TaskGraph(),
                    metadata={"error": intent.error_message},
                    success=False,
                    error_message=intent.error_message,
                )
                
                yield GenerationEvent(
                    stage=GenerationStage.ERROR,
                    progress=0.0,
                    message=f"意图解析失败: {intent.error_message}",
                    data={"error": intent.error_message},
                )
                return
            
            yield GenerationEvent(
                stage=GenerationStage.INTENT_PARSING,
                progress=0.2,
                message="意图解析完成",
                data={
                    "intent": {
                        "task_type": intent.task_type.value if intent.task_type else "unknown",
                        "goal": intent.goal,
                        "constraints": intent.constraints,
                    }
                },
            )
            
            # 阶段2: 任务分解
            yield GenerationEvent(
                stage=GenerationStage.TASK_DECOMPOSITION,
                progress=0.3,
                message="正在分解任务...",
            )
            
            # 在后台线程中执行任务分解
            task_nodes = await loop.run_in_executor(
                None,
                self._base_generator._decompose_tasks,
                intent
            )
            
            yield GenerationEvent(
                stage=GenerationStage.TASK_DECOMPOSITION,
                progress=0.4,
                message=f"任务分解完成，共 {len(task_nodes)} 个任务",
                data={
                    "task_count": len(task_nodes),
                    "tasks": [
                        {"id": n.task_id, "type": n.task_type.value if hasattr(n.task_type, 'value') else str(n.task_type)}
                        for n in task_nodes
                    ],
                },
            )
            
            # 阶段3: 链路优化
            yield GenerationEvent(
                stage=GenerationStage.CHAIN_OPTIMIZATION,
                progress=0.5,
                message="正在优化任务链...",
            )
            
            # 在后台线程中执行链路优化
            optimized_nodes, reliability, optimization_log = await loop.run_in_executor(
                None,
                self._base_generator._optimize_chain,
                task_nodes
            )
            
            yield GenerationEvent(
                stage=GenerationStage.CHAIN_OPTIMIZATION,
                progress=0.6,
                message=f"链路优化完成，可靠性评分: {reliability:.2f}",
                data={
                    "reliability_score": reliability,
                    "optimization_log": optimization_log,
                },
            )
            
            # 阶段4: 任务图构建
            yield GenerationEvent(
                stage=GenerationStage.TASK_GRAPH_BUILDING,
                progress=0.7,
                message="正在构建任务图...",
            )
            
            # 在后台线程中执行任务图构建
            context = {"description": intent.goal.get("description", ""), "user_input": user_input}
            task_graph = await loop.run_in_executor(
                None,
                self._base_generator._build_task_graph,
                optimized_nodes,
                context
            )
            
            nodes = task_graph.get_all_nodes()
            yield GenerationEvent(
                stage=GenerationStage.TASK_GRAPH_BUILDING,
                progress=0.8,
                message=f"任务图构建完成，共 {len(nodes)} 个节点",
                data={
                    "node_count": len(nodes),
                    "edge_count": sum(len(edges) for edges in task_graph._edges.values()),
                },
            )
            
            # 完成
            metadata = {
                "input": user_input,
                "input_type": input_type,
                "mode": "normal",
                "intent": {
                    "task_type": intent.task_type.value if intent.task_type else None,
                    "goal": intent.goal,
                },
                "decomposition": {
                    "node_count": len(task_nodes),
                },
                "optimization": {
                    "reliability_score": reliability,
                    "log": optimization_log,
                },
                "task_graph": {
                    "node_count": len(nodes),
                    "edge_count": sum(len(edges) for edges in task_graph._edges.values()),
                },
            }
            
            # 先设置结果，再发送完成事件
            self._last_result = GenerationResult(
                task_graph=task_graph,
                metadata=metadata,
                success=True,
            )
            
            yield GenerationEvent(
                stage=GenerationStage.COMPLETED,
                progress=1.0,
                message="决策链生成完成",
                data={"metadata": metadata},
            )
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"决策链生成失败: {error_msg}")
            
            # 先设置结果，再发送错误事件
            self._last_result = GenerationResult(
                task_graph=TaskGraph(),
                metadata={"error": error_msg},
                success=False,
                error_message=error_msg,
            )
            
            yield GenerationEvent(
                stage=GenerationStage.ERROR,
                progress=0.0,
                message=f"生成失败: {error_msg}",
                data={"error": error_msg},
            )

    async def generate_from_plan(
        self,
        plan_document: str,
        user_input: str = "",
    ) -> AsyncGenerator[GenerationEvent, None]:
        """流式生成决策链 - Plan 模式
        
        Args:
            plan_document: Plan 文档内容
            user_input: 原始用户输入
            
        Yields:
            GenerationEvent: 生成事件
        """
        try:
            # 阶段1: 任务提取
            yield GenerationEvent(
                stage=GenerationStage.INTENT_PARSING,
                progress=0.2,
                message="正在从 Plan 文档提取任务...",
            )
            
            # 在后台线程中提取实施步骤
            loop = asyncio.get_event_loop()
            steps = await loop.run_in_executor(
                None,
                self._base_generator._extract_implementation_steps,
                plan_document
            )
            
            if not steps:
                # 先设置结果，再发送错误事件
                self._last_result = GenerationResult(
                    task_graph=TaskGraph(),
                    metadata={"error": "No implementation steps found"},
                    success=False,
                    error_message="Plan 文档中未找到实施步骤",
                )
                
                yield GenerationEvent(
                    stage=GenerationStage.ERROR,
                    progress=0.0,
                    message="Plan 文档中未找到实施步骤",
                    data={"error": "No implementation steps found"},
                )
                return
            
            yield GenerationEvent(
                stage=GenerationStage.INTENT_PARSING,
                progress=0.3,
                message=f"提取到 {len(steps)} 个实施步骤",
                data={"steps_count": len(steps)},
            )
            
            # 阶段2: 转换为任务节点
            yield GenerationEvent(
                stage=GenerationStage.TASK_DECOMPOSITION,
                progress=0.4,
                message="正在转换任务节点...",
            )
            
            task_nodes = await loop.run_in_executor(
                None,
                self._base_generator._steps_to_task_nodes,
                steps
            )
            
            yield GenerationEvent(
                stage=GenerationStage.TASK_DECOMPOSITION,
                progress=0.5,
                message=f"任务转换完成，共 {len(task_nodes)} 个任务",
                data={"task_count": len(task_nodes)},
            )
            
            # 阶段3: 链路优化
            yield GenerationEvent(
                stage=GenerationStage.CHAIN_OPTIMIZATION,
                progress=0.6,
                message="正在优化任务链...",
            )
            
            optimized_nodes, reliability, optimization_log = await loop.run_in_executor(
                None,
                self._base_generator._optimize_chain,
                task_nodes
            )
            
            yield GenerationEvent(
                stage=GenerationStage.CHAIN_OPTIMIZATION,
                progress=0.7,
                message=f"链路优化完成，可靠性评分: {reliability:.2f}",
                data={"reliability_score": reliability},
            )
            
            # 阶段4: 任务图构建
            yield GenerationEvent(
                stage=GenerationStage.TASK_GRAPH_BUILDING,
                progress=0.8,
                message="正在构建任务图...",
            )
            
            context = {"description": user_input, "source": "plan_document"}
            task_graph = await loop.run_in_executor(
                None,
                self._base_generator._build_task_graph,
                optimized_nodes,
                context
            )
            
            nodes = task_graph.get_all_nodes()
            yield GenerationEvent(
                stage=GenerationStage.TASK_GRAPH_BUILDING,
                progress=0.9,
                message=f"任务图构建完成，共 {len(nodes)} 个节点",
                data={
                    "node_count": len(nodes),
                    "edge_count": sum(len(edges) for edges in task_graph._edges.values()),
                },
            )
            
            # 完成
            metadata = {
                "source": "plan_document",
                "steps_extracted": len(steps),
                "node_count": len(nodes),
                "reliability_score": reliability,
                "optimization_log": optimization_log,
            }
            
            # 先设置结果，再发送完成事件
            self._last_result = GenerationResult(
                task_graph=task_graph,
                metadata=metadata,
                success=True,
            )
            
            yield GenerationEvent(
                stage=GenerationStage.COMPLETED,
                progress=1.0,
                message="决策链生成完成",
                data={"metadata": metadata},
            )
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"Plan 模式决策链生成失败: {error_msg}")
            
            # 先设置结果，再发送错误事件
            self._last_result = GenerationResult(
                task_graph=TaskGraph(),
                metadata={"error": error_msg},
                success=False,
                error_message=error_msg,
            )
            
            yield GenerationEvent(
                stage=GenerationStage.ERROR,
                progress=0.0,
                message=f"生成失败: {error_msg}",
                data={"error": error_msg},
            )

    async def generate_from_spec(
        self,
        spec_document: str,
        user_input: str = "",
    ) -> AsyncGenerator[GenerationEvent, None]:
        """流式生成决策链 - Spec 模式
        
        Args:
            spec_document: Spec 文档内容
            user_input: 原始用户输入
            
        Yields:
            GenerationEvent: 生成事件
        """
        # Spec 模式与 Plan 模式逻辑相同，复用 generate_from_plan
        async for event in self.generate_from_plan(spec_document, user_input):
            yield event

    def get_last_result(self) -> Optional[GenerationResult]:
        """获取最后一次生成结果
        
        Returns:
            GenerationResult: 生成结果，如果尚未完成则返回 None
        """
        return self._last_result

    def reset(self) -> None:
        """重置生成器状态"""
        self._last_result = None
