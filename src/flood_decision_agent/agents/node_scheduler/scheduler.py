"""节点调度 Agent - 负责任务图的遍历执行和节点调度.

该模块提供NodeSchedulerAgent类，负责任务图的节点调度、依赖检查、
工具选择、执行策略生成和节点执行等核心功能。
"""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional, Tuple

from flood_decision_agent.agents.base import BaseAgent
from flood_decision_agent.agents.task_executor.executor import UnitTaskExecutionAgent
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import Node, NodeStatus, TaskGraph
from flood_decision_agent.tools.registry import ToolRegistry, get_tool_registry


class NodeSchedulerAgent(BaseAgent):
    """节点调度 Agent：负责每个单元任务的具体执行，协调数据、模型和工具.

    核心功能：
    1. 节点依赖关系检查
    2. 前置节点结果获取
    3. 工具候选集构建
    4. 执行策略生成
    5. 节点执行代理（带重试机制）
    6. 任务图遍历执行

    Attributes:
        executor: 单元任务执行Agent实例
        tool_registry: 工具注册中心
        max_retries: 最大重试次数
        base_retry_delay: 基础重试延迟（秒）
    """

    def __init__(
        self,
        executor: Optional[UnitTaskExecutionAgent] = None,
        agent_id: str = "NodeScheduler",
        tool_registry: Optional[ToolRegistry] = None,
        max_retries: int = 3,
        base_retry_delay: float = 1.0,
    ):
        """初始化节点调度Agent.

        Args:
            executor: 单元任务执行Agent实例，为None时自动创建
            agent_id: Agent唯一标识
            tool_registry: 工具注册中心，为None时使用全局注册中心
            max_retries: 最大重试次数，默认3次
            base_retry_delay: 基础重试延迟（秒），默认1.0秒
        """
        super().__init__(agent_id)
        self.executor = executor or UnitTaskExecutionAgent()
        self.tool_registry = tool_registry or get_tool_registry()
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay

    def _process(self, message: BaseMessage) -> Dict[str, Any]:
        """处理调度请求.

        根据消息类型分发到不同的处理方法。

        Args:
            message: 包含调度请求的消息对象

        Returns:
            执行结果字典

        Raises:
            ValueError: 如果消息payload格式不正确
        """
        payload = message.payload

        # 检查是否是任务图执行请求
        if "graph" in payload and "data_pool" in payload:
            graph = payload.get("graph")
            data_pool = payload.get("data_pool")

            if not isinstance(graph, TaskGraph) or not isinstance(
                data_pool, SharedDataPool
            ):
                raise ValueError(
                    "消息 payload 必须包含 'graph' (TaskGraph) 和 'data_pool' (SharedDataPool)"
                )

            return self.execute_task_graph(graph, data_pool)

        # 检查是否是单节点执行请求
        if "node" in payload and "data_pool" in payload:
            node = payload.get("node")
            data_pool = payload.get("data_pool")

            if not isinstance(node, Node) or not isinstance(data_pool, SharedDataPool):
                raise ValueError(
                    "消息 payload 必须包含 'node' (Node) 和 'data_pool' (SharedDataPool)"
                )

            return self.execute_node(node, data_pool)

        raise ValueError(
            "消息 payload 必须包含 'graph'+'data_pool' 或 'node'+'data_pool'"
        )

    def check_dependencies(
        self, node_id: str, task_graph: TaskGraph
    ) -> Tuple[bool, List[str]]:
        """检查节点依赖关系是否满足.

        检查指定节点的所有前置节点是否已完成。

        Args:
            node_id: 要检查的节点ID
            task_graph: 任务图对象

        Returns:
            Tuple[bool, List[str]]: (是否满足依赖, 缺失依赖列表)
                - 第一个元素表示所有依赖是否都已完成
                - 第二个元素包含未完成的依赖节点ID列表

        Raises:
            ValueError: 如果节点不存在于任务图中
        """
        node = task_graph.get_node(node_id)
        if node is None:
            raise ValueError(f"节点不存在: {node_id}")

        missing_deps: List[str] = []

        for dep_id in node.dependencies:
            dep_node = task_graph.get_node(dep_id)
            if dep_node is None:
                missing_deps.append(dep_id)
                continue

            if dep_node.status != NodeStatus.COMPLETED:
                missing_deps.append(dep_id)

        return len(missing_deps) == 0, missing_deps

    def fetch_predecessor_results(
        self, node_id: str, data_pool: SharedDataPool, task_graph: TaskGraph
    ) -> Dict[str, Any]:
        """获取前置节点的执行结果.

        从SharedDataPool获取前置节点的输出数据，合并为输入数据字典。

        Args:
            node_id: 当前节点ID
            data_pool: 共享数据池
            task_graph: 任务图对象

        Returns:
            Dict[str, Any]: 合并后的输入数据字典
                - key为数据标识，value为数据值
                - 包含所有前置节点的输出数据

        Raises:
            ValueError: 如果节点不存在于任务图中
        """
        node = task_graph.get_node(node_id)
        if node is None:
            raise ValueError(f"节点不存在: {node_id}")

        predecessor_results: Dict[str, Any] = {}

        # 获取前置节点的输出数据
        for dep_id in node.dependencies:
            dep_node = task_graph.get_node(dep_id)
            if dep_node is None:
                continue

            # 获取前置节点的输出keys对应的数据
            for output_key in dep_node.output_keys:
                if data_pool.has(output_key):
                    predecessor_results[output_key] = data_pool.get(output_key)

        return predecessor_results

    def build_tool_candidates(self, task_type: str) -> List[Dict[str, Any]]:
        """构建工具候选集.

        使用ToolRegistry.find_by_task_type()查询支持指定任务类型的工具，
        返回按优先级排序的工具列表。

        Args:
            task_type: 任务类型标识

        Returns:
            List[Dict[str, Any]]: 工具候选列表，每个工具包含：
                - name: 工具名称
                - priority: 工具优先级（数字越小优先级越高）
                - description: 工具描述
                - task_types: 支持的任务类型集合
                - required_keys: 需要的输入数据key
                - output_keys: 输出的数据key
        """
        matching_tools = self.tool_registry.find_by_task_type(task_type)

        candidates: List[Dict[str, Any]] = []
        for tool_meta in matching_tools:
            candidates.append(
                {
                    "name": tool_meta.name,
                    "priority": tool_meta.priority,
                    "description": tool_meta.description,
                    "task_types": list(tool_meta.task_types),
                    "required_keys": list(tool_meta.required_keys),
                    "output_keys": list(tool_meta.output_keys),
                }
            )

        self.logger.debug(f"任务类型 '{task_type}' 找到 {len(candidates)} 个工具候选")
        return candidates

    def generate_execution_strategy(self, node: Node, tool_count: int) -> str:
        """生成节点执行策略.

        根据工具数量和任务类型选择合适的执行策略。

        Args:
            node: 节点对象
            tool_count: 可用工具数量

        Returns:
            str: 执行策略，可选值：
                - "single": 单工具执行，适用于只有一个工具的情况
                - "parallel": 并行执行多个工具，适用于计算类任务
                - "fallback": 降级策略，适用于需要高可靠性的任务
                - "auto": 自动选择策略

        策略选择逻辑：
        1. 只有一个工具时，使用"single"
        2. 多个工具时，根据任务类型选择：
           - 计算类任务（compute/statistics）使用"parallel"
           - 关键任务（reservoir_dispatch/flood_warning）使用"fallback"
           - 其他任务默认使用"parallel"
        """
        if tool_count <= 0:
            return "auto"

        if tool_count == 1:
            return "single"

        task_type = node.task_type

        # 计算类任务适合并行执行
        parallel_friendly = {"compute", "statistics", "data_query", "analysis"}
        if task_type in parallel_friendly:
            return "parallel"

        # 需要高可靠性的任务使用fallback策略
        reliability_required = {"reservoir_dispatch", "flood_warning", "emergency"}
        if task_type in reliability_required:
            return "fallback"

        # 水文模型相关任务
        hydrological_tasks = {
            "hydrological_model",
            "inflow_forecast",
            "rainfall_forecast",
        }
        if task_type in hydrological_tasks:
            return "parallel"

        # 调度相关任务
        dispatch_tasks = {"dispatch_plan", "dispatch_order", "gate_control"}
        if task_type in dispatch_tasks:
            return "fallback"

        # 默认使用parallel
        return "parallel"

    def execute_node(self, node: Node, data_pool: SharedDataPool) -> Dict[str, Any]:
        """执行单个节点任务（带重试机制）.

        创建UnitTaskExecutionAgent实例，构建NODE_EXECUTE消息，
        调用execute_task()方法执行节点任务。支持指数退避重试机制。

        Args:
            node: 要执行的节点对象
            data_pool: 共享数据池

        Returns:
            Dict[str, Any]: 执行结果字典，包含：
                - node_id: 节点ID
                - status: 执行状态（success/failed）
                - output: 输出数据
                - metrics: 执行指标（耗时、重试次数等）
                - error: 错误信息（如果失败）

        重试机制：
        - 最大重试次数：3次
        - 使用指数退避算法计算延迟
        - 识别可重试错误（网络错误、超时等）
        """
        node_id = node.node_id
        task_type = node.task_type

        self.logger.info(f"开始执行节点: {node_id} (任务类型: {task_type})")

        # 构建工具列表
        tools: List[Dict[str, Any]] = []
        if node.tool_candidates:
            for tool_info in node.tool_candidates:
                tools.append(
                    {
                        "tool_name": tool_info.get("name", "unknown"),
                        "tool_config": {},
                        "priority": tool_info.get("priority", 100),
                    }
                )

        # 确定执行策略
        execution_strategy = node.execution_strategy
        if not execution_strategy or execution_strategy == "auto":
            execution_strategy = self.generate_execution_strategy(node, len(tools))

        self.logger.info(f"节点 {node_id} 执行策略: {execution_strategy}")

        # 执行（带重试机制）
        last_error: Optional[Exception] = None
        retry_count = 0

        while retry_count <= self.max_retries:
            try:
                # 创建执行Agent（如果未提供）
                if self.executor is None:
                    executor = UnitTaskExecutionAgent()
                else:
                    executor = self.executor

                # 执行节点任务
                result = executor.execute_task(
                    node_id=node_id,
                    task_type=task_type,
                    data_pool=data_pool,
                    tools=tools,
                    execution_strategy=execution_strategy,
                    context={"retry_count": retry_count},
                )

                # 更新节点状态为完成
                node.status = NodeStatus.COMPLETED

                # 构建成功响应
                response = {
                    "node_id": node_id,
                    "status": "success",
                    "output": result.get("output", {}),
                    "metrics": {
                        **result.get("metrics", {}),
                        "retry_count": retry_count,
                    },
                }

                self.logger.info(f"节点 {node_id} 执行成功，重试次数: {retry_count}")
                return response

            except Exception as e:
                last_error = e
                retry_count += 1

                if retry_count > self.max_retries:
                    break

                # 检查是否可重试
                if not self._is_retryable_error(e):
                    self.logger.warning(f"节点 {node_id} 遇到不可重试错误: {e}")
                    break

                # 计算指数退避延迟
                delay = self._calculate_retry_delay(retry_count)
                self.logger.warning(
                    f"节点 {node_id} 执行失败（第{retry_count}次重试）: {e}, "
                    f"{delay:.2f}秒后重试..."
                )
                time.sleep(delay)

        # 执行失败
        node.status = NodeStatus.FAILED

        error_response = {
            "node_id": node_id,
            "status": "failed",
            "output": {},
            "error": str(last_error) if last_error else "未知错误",
            "metrics": {
                "retry_count": retry_count - 1,
            },
        }

        self.logger.error(f"节点 {node_id} 执行失败，已重试{retry_count - 1}次")
        return error_response

    def _is_retryable_error(self, error: Exception) -> bool:
        """判断错误是否可重试.

        识别网络错误、超时错误等临时性错误。

        Args:
            error: 异常对象

        Returns:
            bool: 是否可重试
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()

        # 可重试的错误类型
        retryable_patterns = [
            "timeout",
            "connection",
            "network",
            "temporarily",
            "unavailable",
            "rate limit",
            "too many requests",
            "service unavailable",
        ]

        # 不可重试的错误类型
        non_retryable_patterns = [
            "valueerror",
            "keyerror",
            "typeerror",
            "assertionerror",
            "not found",
            "invalid",
            "unauthorized",
            "forbidden",
        ]

        # 检查是否明确不可重试
        for pattern in non_retryable_patterns:
            if pattern in error_str or pattern in error_type:
                return False

        # 检查是否可重试
        for pattern in retryable_patterns:
            if pattern in error_str or pattern in error_type:
                return True

        # 默认允许重试（保守策略）
        return True

    def _calculate_retry_delay(self, retry_count: int) -> float:
        """计算重试延迟时间（指数退避算法）.

        使用指数退避 + 随机抖动，避免惊群效应。

        Args:
            retry_count: 当前重试次数（从1开始）

        Returns:
            float: 延迟时间（秒）
        """
        # 指数退避: base * 2^(retry_count-1)
        exponential_delay = self.base_retry_delay * (2 ** (retry_count - 1))

        # 添加随机抖动 (±25%)
        jitter = exponential_delay * 0.25 * (2 * random.random() - 1)

        return max(0.1, exponential_delay + jitter)

    def execute_task_graph(
        self, task_graph: TaskGraph, data_pool: SharedDataPool
    ) -> Dict[str, Any]:
        """遍历执行任务图中的所有节点.

        主执行方法，循环获取可执行节点(get_ready_nodes)，
        执行节点并更新状态，直到所有节点执行完成或出现不可恢复错误。

        Args:
            task_graph: 任务图对象
            data_pool: 共享数据池

        Returns:
            Dict[str, Any]: 整体执行结果，包含：
                - status: 整体执行状态（success/partial_failed/failed）
                - completed_nodes: 成功完成的节点列表
                - failed_nodes: 执行失败的节点列表
                - results: 各节点的执行结果
                - metrics: 执行指标（总耗时、节点数等）
        """
        start_time = time.time()
        self.logger.info("开始执行任务图")

        completed_nodes: List[str] = []
        failed_nodes: List[str] = []
        node_results: Dict[str, Dict[str, Any]] = {}

        # 获取所有节点
        all_nodes = task_graph.get_all_nodes()
        total_nodes = len(all_nodes)

        self.logger.info(f"任务图包含 {total_nodes} 个节点")

        # 循环执行直到所有节点完成或没有可执行节点
        max_iterations = total_nodes * 2  # 防止无限循环
        iteration = 0

        while len(completed_nodes) + len(failed_nodes) < total_nodes:
            iteration += 1
            if iteration > max_iterations:
                self.logger.error("任务图执行超过最大迭代次数，可能存在循环依赖")
                break

            # 获取可执行节点（依赖已满足且状态为PENDING）
            ready_nodes = task_graph.get_ready_nodes()

            if not ready_nodes:
                # 检查是否还有未完成的节点
                pending_nodes = [
                    node_id
                    for node_id, node in all_nodes.items()
                    if node.status == NodeStatus.PENDING
                ]

                if pending_nodes:
                    self.logger.error(
                        f"存在无法执行的节点（可能依赖缺失）: {pending_nodes}"
                    )
                    for node_id in pending_nodes:
                        failed_nodes.append(node_id)
                        node_results[node_id] = {
                            "status": "failed",
                            "error": "依赖无法满足或循环依赖",
                        }
                break

            self.logger.info(f"本轮可执行节点: {ready_nodes}")

            # 执行可执行节点
            for node_id in ready_nodes:
                node = task_graph.get_node(node_id)
                if node is None:
                    continue

                # 更新节点状态为运行中
                node.status = NodeStatus.RUNNING
                task_graph.update_node_status(node_id, NodeStatus.RUNNING)

                # 执行节点
                result = self.execute_node(node, data_pool)

                # 记录结果
                node_results[node_id] = result

                if result.get("status") == "success":
                    completed_nodes.append(node_id)
                    task_graph.update_node_status(node_id, NodeStatus.COMPLETED)

                    # 将节点输出写入数据池
                    output_data = result.get("output", {})
                    if isinstance(output_data, dict):
                        for key, value in output_data.items():
                            data_pool.put(key, value)
                else:
                    failed_nodes.append(node_id)
                    task_graph.update_node_status(node_id, NodeStatus.FAILED)

                    # 根据错误策略决定是否继续
                    # 默认策略：一个节点失败，继续执行其他独立分支
                    self.logger.warning(
                        f"节点 {node_id} 执行失败，继续执行其他可执行节点"
                    )

        # 计算总耗时
        elapsed_time = time.time() - start_time

        # 确定整体状态
        if len(failed_nodes) == 0:
            overall_status = "success"
        elif len(completed_nodes) > 0:
            overall_status = "partial_failed"
        else:
            overall_status = "failed"

        # 构建整体结果
        final_result = {
            "status": overall_status,
            "completed_nodes": completed_nodes,
            "failed_nodes": failed_nodes,
            "total_nodes": total_nodes,
            "completed_count": len(completed_nodes),
            "failed_count": len(failed_nodes),
            "results": node_results,
            "metrics": {
                "total_elapsed_time": elapsed_time,
                "iteration_count": iteration,
            },
        }

        self.logger.info(
            f"任务图执行完成: 成功{len(completed_nodes)}个, "
            f"失败{len(failed_nodes)}个, 总耗时{elapsed_time:.2f}秒"
        )

        return final_result

    def run(self, graph: TaskGraph, data_pool: SharedDataPool) -> Dict[str, Any]:
        """兼容性方法：供旧代码直接调用.

        Args:
            graph: 任务图对象
            data_pool: 共享数据池

        Returns:
            Dict[str, Any]: 执行结果
        """
        message = BaseMessage(
            type=MessageType.NODE_RESULT,
            payload={"graph": graph, "data_pool": data_pool},
            sender="Pipeline",
        )
        return self.execute(message)
