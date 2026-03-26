"""决策链生成 Agent - 系统入口，负责决策链的生成和优化.

该模块提供DecisionChainGeneratorAgent类，作为系统的入口Agent，
负责理解用户意图、分解任务、优化链路并生成可执行的任务图。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from flood_decision_agent.agents.base import BaseAgent
from flood_decision_agent.agents.decision_chain.chain_optimizer import ChainAlternative, ChainOptimizer
from flood_decision_agent.agents.decision_chain.task_decomposer import TaskDecomposer, TaskNodeInfo
from flood_decision_agent.agents.intent_parser.parser import IntentParser, TaskIntent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import TaskGraph
from flood_decision_agent.core.task_graph_builder import TaskChainItem, TaskGraphBuilder
from flood_decision_agent.core.task_types import (
    BusinessTaskType,
    ExecutionTaskType,
    get_execution_types_for_business,
    get_business_type_description,
)
from flood_decision_agent.infra.logging import get_logger


class DecisionChainGeneratorAgent(BaseAgent):
    """决策链生成 Agent：系统入口，负责决策链的生成和优化.

    核心功能：
    1. 意图理解：解析自然语言或结构化输入
    2. 任务分解：逆向分解 + 正向验证
    3. 链路优化：生成备选链 + 可靠性评估 + 迭代优化
    4. TaskGraph生成：构建可执行的任务图

    3阶段处理流程：
    意图理解 → 任务分解 → 链路优化 → TaskGraph

    Attributes:
        intent_parser: 意图解析器
        task_decomposer: 任务分解器
        chain_optimizer: 链路优化器
        task_graph_builder: 任务图构建器
    """

    def __init__(
        self,
        agent_id: str = "DecisionChainGenerator",
        intent_parser: Optional[IntentParser] = None,
        task_decomposer: Optional[TaskDecomposer] = None,
        chain_optimizer: Optional[ChainOptimizer] = None,
        task_graph_builder: Optional[TaskGraphBuilder] = None,
    ):
        """初始化决策链生成Agent.

        Args:
            agent_id: Agent唯一标识
            intent_parser: 意图解析器，为None时自动创建
            task_decomposer: 任务分解器，为None时自动创建
            chain_optimizer: 链路优化器，为None时自动创建
            task_graph_builder: 任务图构建器，为None时自动创建
        """
        super().__init__(agent_id=agent_id)
        self._logger = get_logger().bind(name=self.__class__.__name__)

        # 初始化各模块
        self.intent_parser = intent_parser or IntentParser()
        self.task_decomposer = task_decomposer or TaskDecomposer()
        self.chain_optimizer = chain_optimizer or ChainOptimizer()
        self.task_graph_builder = task_graph_builder or TaskGraphBuilder()

        self._logger.info("DecisionChainGeneratorAgent 初始化完成")

    def _process(self, message: BaseMessage) -> BaseMessage:
        """执行决策链生成.

        这是Agent的主要入口方法，接收用户输入消息，
        经过3阶段处理后返回生成的TaskGraph。

        Args:
            message: 输入消息，包含用户请求

        Returns:
            输出消息，包含生成的TaskGraph
        """
        self._logger.info(f"开始执行决策链生成，消息类型: {message.message_type}")

        # 解析输入
        user_input = message.content.get("input", "")
        input_type = message.content.get("input_type", "natural_language")

        # 生成决策链
        task_graph, metadata = self.generate_chain(user_input, input_type)

        # 构建响应消息
        response = BaseMessage(
            message_type=MessageType.TASK_ASSIGN,
            sender=self.agent_id,
            receiver="NodeSchedulerAgent",
            content={
                "task_graph": task_graph,
                "metadata": metadata,
            },
        )

        self._logger.info("决策链生成完成")
        return response

    def generate_chain(
        self,
        user_input: str,
        input_type: str = "natural_language",
    ) -> Tuple[TaskGraph, Dict[str, Any]]:
        """生成决策链的主方法.

        3阶段处理流程：
        1. 意图理解：解析用户输入
        2. 任务分解：逆向分解 + 正向验证
        3. 链路优化：生成备选链 + 选择最优
        4. 图生成：构建TaskGraph

        Args:
            user_input: 用户输入（自然语言或结构化数据）
            input_type: 输入类型，"natural_language" 或 "structured"

        Returns:
            (生成的TaskGraph, 元数据)
        """
        metadata: Dict[str, Any] = {
            "input": user_input,
            "input_type": input_type,
        }

        # ========== 阶段1: 意图理解 ==========
        self._logger.info("阶段1: 意图理解")
        intent = self._parse_intent(user_input, input_type)
        
        # 检查意图解析是否出错
        if intent.error_message:
            self._logger.error(f"意图解析失败: {intent.error_message}")
            metadata["error"] = intent.error_message
            # 返回一个空的 TaskGraph，但标记为错误
            from flood_decision_agent.core.task_graph import TaskGraph
            return TaskGraph(), metadata
        
        metadata["intent"] = {
            "task_type": intent.task_type.value if intent.task_type else None,
            "goal": intent.goal,
            "constraints": intent.constraints,
        }

        # ========== 阶段2: 任务分解 ==========
        self._logger.info("阶段2: 任务分解")
        task_nodes = self._decompose_tasks(intent)
        metadata["decomposition"] = {
            "node_count": len(task_nodes),
            "nodes": [{"id": n.task_id, "type": n.task_type.value} for n in task_nodes],
        }

        # ========== 阶段3: 链路优化 ==========
        self._logger.info("阶段3: 链路优化")
        optimized_nodes, reliability, optimization_log = self._optimize_chain(task_nodes)
        metadata["optimization"] = {
            "reliability_score": reliability,
            "log": optimization_log,
        }

        # ========== 阶段4: TaskGraph生成 ==========
        self._logger.info("阶段4: TaskGraph生成")
        task_graph = self._build_task_graph(optimized_nodes)
        metadata["task_graph"] = {
            "node_count": len(task_graph.get_all_nodes()),
            "edge_count": sum(len(edges) for edges in task_graph._edges.values()),
        }

        return task_graph, metadata

    def _parse_intent(self, user_input: str, input_type: str) -> TaskIntent:
        """解析用户意图.

        Args:
            user_input: 用户输入
            input_type: 输入类型

        Returns:
            解析后的意图对象
        """
        if input_type == "natural_language":
            intent = self.intent_parser.parse_natural_language(user_input)
        elif input_type == "structured":
            # 将字符串解析为字典
            import json

            try:
                structured_data = json.loads(user_input)
            except json.JSONDecodeError:
                structured_data = {"task_type": "unknown", "description": user_input}
            intent = self.intent_parser.parse_structured(structured_data)
        else:
            # 默认尝试自然语言解析
            intent = self.intent_parser.parse_natural_language(user_input)

        self._logger.info(
            f"意图解析完成: 任务类型={intent.task_type.value if intent.task_type else 'unknown'}, "
            f"目标={intent.goal}"
        )
        return intent

    def _decompose_tasks(self, intent: TaskIntent) -> List[TaskNodeInfo]:
        """分解任务.

        使用新的类型系统，基于业务类型获取执行步骤。

        Args:
            intent: 用户意图

        Returns:
            任务节点列表
        """
        # 获取业务类型和执行步骤
        business_type = intent.task_type
        execution_steps = intent.execution_steps

        # 如果没有执行步骤，使用默认步骤
        if not execution_steps:
            execution_steps = get_execution_types_for_business(business_type)

        # 提取目标描述
        goal_description = intent.goal.get("description", "")
        if not goal_description and intent.raw_input:
            goal_description = intent.raw_input

        # 构建任务节点列表
        task_nodes: List[TaskNodeInfo] = []
        prev_node_id = None

        for idx, exec_type in enumerate(execution_steps):
            node_id = f"{business_type.value}_{idx:03d}"
            
            # 构建依赖关系
            dependencies = []
            if prev_node_id:
                dependencies.append(prev_node_id)

            node = TaskNodeInfo(
                task_id=node_id,
                task_type=exec_type,
                description=f"{get_business_type_description(business_type)} - {exec_type.value}",
                inputs=[],
                outputs=[f"output_{node_id}"],
                dependencies=dependencies,
                metadata={
                    "business_type": business_type.value,
                    "execution_type": exec_type.value,
                    "step_index": idx,
                },
            )
            task_nodes.append(node)
            prev_node_id = node_id

        self._logger.info(f"任务分解完成: {len(task_nodes)} 个节点 (业务类型: {business_type.value})")
        return task_nodes

    def _optimize_chain(
        self, task_nodes: List[TaskNodeInfo]
    ) -> Tuple[List[TaskNodeInfo], float, List[str]]:
        """优化任务链.

        Args:
            task_nodes: 初始任务节点列表

        Returns:
            (优化后的节点列表, 可靠性评分, 优化日志)
        """
        # 生成备选链
        alternatives = self.chain_optimizer.generate_alternatives(task_nodes)
        self._logger.info(f"生成 {len(alternatives)} 条备选链")

        # 评估每条链的可靠性
        for alt in alternatives:
            reliability, issues, _ = self.chain_optimizer.evaluate_reliability(alt.nodes)
            alt.reliability_score = reliability
            alt.metadata["issues"] = issues

        # 选择最优链
        best_chain = self.chain_optimizer.select_best_chain(alternatives)

        if best_chain:
            self._logger.info(
                f"选择最优链: {best_chain.chain_id}, 可靠性={best_chain.reliability_score:.2f}"
            )
            # 对最优链进行迭代优化
            optimized_nodes, final_reliability, log = self.chain_optimizer.optimize_iteratively(
                best_chain.nodes
            )
            return optimized_nodes, final_reliability, log
        else:
            # 如果没有找到合适的链，返回原始节点
            self._logger.warning("未找到合适的备选链，使用原始链")
            reliability, _, _ = self.chain_optimizer.evaluate_reliability(task_nodes)
            return task_nodes, reliability, ["使用原始链"]

    def _build_task_graph(self, task_nodes: List[TaskNodeInfo]) -> TaskGraph:
        """构建任务图.

        Args:
            task_nodes: 任务节点列表

        Returns:
            构建的TaskGraph
        """
        # 转换为TaskChainItem
        chain_items = []
        for node in task_nodes:
            item = TaskChainItem(
                task_id=node.task_id,
                task_type=node.task_type.value,
                description=node.description,
                inputs=node.inputs,
                outputs=node.outputs,
                dependencies=node.dependencies,
            )
            chain_items.append(item)

        # 构建任务图
        task_graph = self.task_graph_builder.build_from_chain(chain_items)

        self._logger.info(
            f"TaskGraph构建完成: {len(task_graph.get_all_nodes())} 个节点, "
            f"{sum(len(edges) for edges in task_graph._edges.values())} 条边"
        )
        return task_graph

    def generate_chain_with_alternatives(
        self,
        user_input: str,
        input_type: str = "natural_language",
        num_alternatives: int = 3,
    ) -> Tuple[TaskGraph, List[ChainAlternative], Dict[str, Any]]:
        """生成决策链并返回所有备选方案.

        用于需要查看所有备选链的场景。

        Args:
            user_input: 用户输入
            input_type: 输入类型
            num_alternatives: 备选链数量

        Returns:
            (最优TaskGraph, 所有备选链, 元数据)
        """
        # 意图理解
        intent = self._parse_intent(user_input, input_type)

        # 任务分解
        task_nodes = self._decompose_tasks(intent)

        # 生成备选链
        alternatives = self.chain_optimizer.generate_alternatives(
            task_nodes, strategies=["default", "parallel", "granular"][:num_alternatives]
        )

        # 评估所有备选链
        for alt in alternatives:
            reliability, issues, _ = self.chain_optimizer.evaluate_reliability(alt.nodes)
            alt.reliability_score = reliability
            alt.metadata["issues"] = issues

        # 选择最优链并构建TaskGraph
        best_chain = self.chain_optimizer.select_best_chain(alternatives)
        if best_chain:
            optimized_nodes, _, _ = self.chain_optimizer.optimize_iteratively(best_chain.nodes)
            task_graph = self._build_task_graph(optimized_nodes)
        else:
            task_graph = self._build_task_graph(task_nodes)

        metadata = {
            "intent": {
                "task_type": intent.task_type.value if intent.task_type else None,
                "goal": intent.goal,
            },
            "alternatives_count": len(alternatives),
            "selected_chain": best_chain.chain_id if best_chain else None,
        }

        return task_graph, alternatives, metadata


class DecisionPipeline:
    """决策流程管道.

    整合 DecisionChainGeneratorAgent 和 NodeSchedulerAgent，
    提供端到端的决策执行流程。
    """

    def __init__(
        self,
        chain_generator: Optional[DecisionChainGeneratorAgent] = None,
        node_scheduler: Optional[Any] = None,
    ):
        """初始化决策管道.

        Args:
            chain_generator: 决策链生成Agent
            node_scheduler: 节点调度Agent
        """
        self._logger = get_logger().bind(name=self.__class__.__name__)

        self.chain_generator = chain_generator or DecisionChainGeneratorAgent()
        self.node_scheduler = node_scheduler

        self._logger.info("DecisionPipeline 初始化完成")

    def execute(
        self,
        user_input: str,
        input_type: str = "natural_language",
        data_pool: Optional[SharedDataPool] = None,
    ) -> Dict[str, Any]:
        """执行完整决策流程.

        Args:
            user_input: 用户输入
            input_type: 输入类型
            data_pool: 共享数据池

        Returns:
            执行结果
        """
        if data_pool is None:
            data_pool = SharedDataPool()

        # 保存用户原始输入到数据池，供后续工具使用
        data_pool.set("raw_user_input", user_input)
        data_pool.set("input_type", input_type)

        # 阶段1: 生成决策链
        self._logger.info("=" * 50)
        self._logger.info("阶段1: 生成决策链")
        self._logger.info("=" * 50)

        task_graph, metadata = self.chain_generator.generate_chain(user_input, input_type)

        # 阶段2: 执行决策链（如果有NodeScheduler）
        if self.node_scheduler:
            self._logger.info("=" * 50)
            self._logger.info("阶段2: 执行决策链")
            self._logger.info("=" * 50)

            execution_result = self.node_scheduler.execute_task_graph(
                task_graph, data_pool
            )

            return {
                "task_graph": task_graph,
                "generation_metadata": metadata,
                "execution_result": execution_result,
            }
        else:
            return {
                "task_graph": task_graph,
                "generation_metadata": metadata,
                "execution_result": None,
            }
