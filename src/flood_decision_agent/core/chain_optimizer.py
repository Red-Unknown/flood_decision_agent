"""链路优化模块.

提供 ChainOptimizer 类，支持生成备选任务链、评估链路可靠性和迭代优化。
主要用于决策链生成后的优化和选择。
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from flood_decision_agent.core.task_decomposer import TaskNodeInfo, TaskType
from flood_decision_agent.core.task_graph import TaskGraph
from flood_decision_agent.infra.logging import get_logger


@dataclass
class ChainAlternative:
    """任务链备选方案数据类.

    Attributes:
        chain_id: 链唯一标识
        nodes: 任务节点列表
        reliability_score: 可靠性评分 (0-1)
        strategy: 生成策略
        metadata: 额外元数据
    """

    chain_id: str
    nodes: List[TaskNodeInfo] = field(default_factory=list)
    reliability_score: float = 0.0
    strategy: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BottleneckInfo:
    """瓶颈节点信息数据类.

    Attributes:
        node_id: 节点ID
        bottleneck_type: 瓶颈类型
        severity: 严重程度 (0-1)
        suggestions: 优化建议
    """

    node_id: str
    bottleneck_type: str
    severity: float = 0.0
    suggestions: List[str] = field(default_factory=list)


class ChainOptimizer:
    """链路优化器.

    支持生成备选任务链、评估链路可靠性和迭代优化。
    通过多种策略生成多条备选链，评估可靠性后选择最优方案。

    Attributes:
        max_alternatives: 最大备选链数量
        reliability_threshold: 可靠性阈值
        logger: 日志记录器
    """

    def __init__(
        self,
        max_alternatives: int = 3,
        reliability_threshold: float = 0.7,
    ):
        """初始化链路优化器.

        Args:
            max_alternatives: 最大备选链数量
            reliability_threshold: 可靠性阈值
        """
        self.max_alternatives = max_alternatives
        self.reliability_threshold = reliability_threshold
        self._logger = get_logger().bind(name=self.__class__.__name__)

    def generate_alternatives(
        self,
        base_nodes: List[TaskNodeInfo],
        strategies: Optional[List[str]] = None,
    ) -> List[ChainAlternative]:
        """生成备选任务链.

        使用不同策略生成多条备选任务链。

        Args:
            base_nodes: 基础任务节点列表
            strategies: 生成策略列表，默认使用 ["default", "parallel", "granular"]

        Returns:
            备选链列表
        """
        if strategies is None:
            strategies = ["default", "parallel", "granular"]

        alternatives: List[ChainAlternative] = []

        for i, strategy in enumerate(strategies[: self.max_alternatives]):
            chain_id = f"chain_{strategy}_{i}"

            if strategy == "default":
                nodes = self._apply_default_strategy(base_nodes)
            elif strategy == "parallel":
                nodes = self._apply_parallel_strategy(base_nodes)
            elif strategy == "granular":
                nodes = self._apply_granular_strategy(base_nodes)
            else:
                nodes = list(base_nodes)

            alternative = ChainAlternative(
                chain_id=chain_id,
                nodes=nodes,
                strategy=strategy,
            )
            alternatives.append(alternative)
            self._logger.info(f"生成备选链: {chain_id}, 策略: {strategy}, 节点数: {len(nodes)}")

        return alternatives

    def _apply_default_strategy(self, nodes: List[TaskNodeInfo]) -> List[TaskNodeInfo]:
        """应用默认策略.

        保持原始任务链不变。

        Args:
            nodes: 原始节点列表

        Returns:
            处理后的节点列表
        """
        return [self._copy_node(node) for node in nodes]

    def _apply_parallel_strategy(self, nodes: List[TaskNodeInfo]) -> List[TaskNodeInfo]:
        """应用并行化策略.

        识别可以并行执行的任务并调整依赖关系。

        Args:
            nodes: 原始节点列表

        Returns:
            处理后的节点列表
        """
        new_nodes = [self._copy_node(node) for node in nodes]

        # 识别数据采集类任务，它们通常可以并行
        data_collection_nodes = [
            node for node in new_nodes if node.task_type == TaskType.DATA_COLLECTION
        ]

        if len(data_collection_nodes) > 1:
            # 让这些数据采集任务并行执行（移除它们之间的依赖）
            first_dc = data_collection_nodes[0]
            for node in data_collection_nodes[1:]:
                # 如果节点依赖其他数据采集任务，改为依赖第一个
                node.dependencies = [
                    dep for dep in node.dependencies if dep not in [n.task_id for n in data_collection_nodes]
                ]
                if not node.dependencies:
                    node.dependencies = [dep for dep in first_dc.dependencies if dep != node.task_id]

        self._logger.debug(f"并行化策略: 识别 {len(data_collection_nodes)} 个可并行数据采集任务")
        return new_nodes

    def _apply_granular_strategy(self, nodes: List[TaskNodeInfo]) -> List[TaskNodeInfo]:
        """应用细粒度策略.

        将复杂任务拆分为更细的子任务。

        Args:
            nodes: 原始节点列表

        Returns:
            处理后的节点列表
        """
        new_nodes: List[TaskNodeInfo] = []

        for node in nodes:
            if node.task_type == TaskType.CALCULATION and len(node.outputs) > 2:
                # 将复杂计算任务拆分为多个子任务
                for i, output in enumerate(node.outputs):
                    sub_node = TaskNodeInfo(
                        task_id=f"{node.task_id}_sub_{i}",
                        task_type=TaskType.CALCULATION,
                        description=f"{node.description} - 子任务 {i+1}",
                        inputs=node.inputs if i == 0 else [node.outputs[i - 1]],
                        outputs=[output],
                        dependencies=node.dependencies if i == 0 else [f"{node.task_id}_sub_{i-1}"],
                    )
                    new_nodes.append(sub_node)
            else:
                new_nodes.append(self._copy_node(node))

        self._logger.debug(f"细粒度策略: 原始 {len(nodes)} 个节点 -> 新 {len(new_nodes)} 个节点")
        return new_nodes

    def _copy_node(self, node: TaskNodeInfo) -> TaskNodeInfo:
        """复制任务节点.

        Args:
            node: 原始节点

        Returns:
            复制的节点
        """
        return TaskNodeInfo(
            task_id=node.task_id,
            task_type=node.task_type,
            description=node.description,
            inputs=list(node.inputs),
            outputs=list(node.outputs),
            dependencies=list(node.dependencies),
            metadata=dict(node.metadata) if node.metadata else {},
        )

    def evaluate_reliability(
        self,
        nodes: List[TaskNodeInfo],
        available_tools: Optional[Set[str]] = None,
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        """评估链路可靠性.

        检查循环依赖、工具可用性、数据依赖合理性，计算可靠性评分。

        Args:
            nodes: 任务节点列表
            available_tools: 可用工具集合

        Returns:
            (可靠性评分, 问题列表, 详细评估信息)
        """
        issues: List[str] = []
        details: Dict[str, Any] = {
            "cycle_check": {},
            "tool_check": {},
            "dependency_check": {},
        }

        # 1. 检查循环依赖
        has_cycle, cycle_info = self._check_circular_dependencies(nodes)
        details["cycle_check"] = {"has_cycle": has_cycle, "info": cycle_info}
        if has_cycle:
            issues.append(f"发现循环依赖: {cycle_info}")

        # 2. 评估工具可用性
        tool_score, tool_issues = self._evaluate_tool_availability(nodes, available_tools)
        details["tool_check"] = {"score": tool_score, "issues": tool_issues}
        issues.extend(tool_issues)

        # 3. 评估数据依赖合理性
        dep_score, dep_issues = self._evaluate_data_dependencies(nodes)
        details["dependency_check"] = {"score": dep_score, "issues": dep_issues}
        issues.extend(dep_issues)

        # 4. 计算总体可靠性评分
        if has_cycle:
            reliability_score = 0.0
        else:
            # 权重: 工具可用性 40%, 数据依赖 40%, 其他因素 20%
            reliability_score = tool_score * 0.4 + dep_score * 0.4 + 0.2
            # 根据问题数量扣分
            reliability_score -= len(issues) * 0.05
            reliability_score = max(0.0, min(1.0, reliability_score))

        self._logger.info(f"可靠性评估: 评分={reliability_score:.2f}, 问题数={len(issues)}")
        return reliability_score, issues, details

    def _check_circular_dependencies(
        self, nodes: List[TaskNodeInfo]
    ) -> Tuple[bool, Optional[str]]:
        """检查循环依赖.

        Args:
            nodes: 任务节点列表

        Returns:
            (是否存在循环, 循环信息)
        """
        # 构建邻接表
        node_ids = {node.task_id for node in nodes}
        graph: Dict[str, Set[str]] = {node.task_id: set() for node in nodes}

        for node in nodes:
            for dep in node.dependencies:
                if dep in node_ids:
                    graph[dep].add(node.task_id)

        # DFS检测循环
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(node_id: str) -> Optional[List[str]]:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in graph.get(node_id, set()):
                if neighbor not in visited:
                    cycle = has_cycle(neighbor)
                    if cycle:
                        cycle.append(node_id)
                        return cycle
                elif neighbor in rec_stack:
                    return [node_id, neighbor]

            rec_stack.remove(node_id)
            return None

        for node_id in graph:
            if node_id not in visited:
                cycle = has_cycle(node_id)
                if cycle:
                    cycle.reverse()
                    return True, " -> ".join(cycle)

        return False, None

    def _evaluate_tool_availability(
        self,
        nodes: List[TaskNodeInfo],
        available_tools: Optional[Set[str]],
    ) -> Tuple[float, List[str]]:
        """评估工具可用性.

        Args:
            nodes: 任务节点列表
            available_tools: 可用工具集合

        Returns:
            (可用性评分, 问题列表)
        """
        if available_tools is None:
            # 默认假设所有工具都可用
            return 1.0, []

        issues: List[str] = []
        unsupported_count = 0

        for node in nodes:
            # 检查节点是否有对应的工具支持
            task_type = node.task_type.value
            if task_type not in available_tools:
                # 尝试检查metadata中的工具信息
                required_tools = node.metadata.get("required_tools", [])
                if required_tools and not any(t in available_tools for t in required_tools):
                    unsupported_count += 1
                    issues.append(f"任务 {node.task_id} 缺少工具支持")

        score = 1.0 - (unsupported_count / len(nodes)) if nodes else 1.0
        return max(0.0, score), issues

    def _evaluate_data_dependencies(
        self, nodes: List[TaskNodeInfo]
    ) -> Tuple[float, List[str]]:
        """评估数据依赖合理性.

        Args:
            nodes: 任务节点列表

        Returns:
            (依赖评分, 问题列表)
        """
        issues: List[str] = []
        node_output_map: Dict[str, Set[str]] = {}

        # 构建节点输出映射
        for node in nodes:
            node_output_map[node.task_id] = set(node.outputs)

        # 检查每个节点的输入是否都能被满足
        missing_inputs = 0
        total_inputs = 0

        for node in nodes:
            for input_key in node.inputs:
                total_inputs += 1
                # 检查是否有前置节点提供此输入
                found = False
                for dep_id in node.dependencies:
                    if input_key in node_output_map.get(dep_id, set()):
                        found = True
                        break

                if not found and not node.metadata.get("external_input", False):
                    missing_inputs += 1
                    issues.append(f"任务 {node.task_id} 的输入 '{input_key}' 未被满足")

        score = 1.0 - (missing_inputs / total_inputs) if total_inputs > 0 else 1.0
        return max(0.0, score), issues

    def identify_bottlenecks(
        self,
        nodes: List[TaskNodeInfo],
        execution_times: Optional[Dict[str, float]] = None,
    ) -> List[BottleneckInfo]:
        """识别瓶颈节点.

        Args:
            nodes: 任务节点列表
            execution_times: 节点执行时间预估

        Returns:
            瓶颈节点信息列表
        """
        bottlenecks: List[BottleneckInfo] = []

        # 1. 识别高度数节点（依赖多或被依赖多）
        dependency_count: Dict[str, int] = {node.task_id: 0 for node in nodes}
        for node in nodes:
            for dep in node.dependencies:
                dependency_count[dep] = dependency_count.get(dep, 0) + 1

        for node in nodes:
            total_degree = len(node.dependencies) + dependency_count.get(node.task_id, 0)
            if total_degree >= 4:  # 高度数阈值
                bottlenecks.append(
                    BottleneckInfo(
                        node_id=node.task_id,
                        bottleneck_type="high_degree",
                        severity=min(1.0, total_degree / 6.0),
                        suggestions=["考虑拆分任务", "优化依赖关系"],
                    )
                )

        # 2. 识别长执行时间任务
        if execution_times:
            avg_time = sum(execution_times.values()) / len(execution_times)
            for node_id, time in execution_times.items():
                if time > avg_time * 2:
                    bottlenecks.append(
                        BottleneckInfo(
                            node_id=node_id,
                            bottleneck_type="long_execution",
                            severity=min(1.0, time / (avg_time * 3)),
                            suggestions=["考虑并行化", "优化算法", "增加资源"],
                        )
                    )

        # 3. 识别关键路径上的单点故障
        critical_types = {TaskType.DECISION, TaskType.EXECUTION}
        for node in nodes:
            if node.task_type in critical_types:
                # 检查是否有冗余
                has_backup = any(
                    n.task_type == node.task_type and n.task_id != node.task_id
                    for n in nodes
                )
                if not has_backup:
                    bottlenecks.append(
                        BottleneckInfo(
                            node_id=node.task_id,
                            bottleneck_type="single_point_failure",
                            severity=0.8,
                            suggestions=["添加备用方案", "增加重试机制"],
                        )
                    )

        self._logger.info(f"识别到 {len(bottlenecks)} 个瓶颈节点")
        return bottlenecks

    def optimize_iteratively(
        self,
        nodes: List[TaskNodeInfo],
        max_iterations: int = 3,
        available_tools: Optional[Set[str]] = None,
    ) -> Tuple[List[TaskNodeInfo], float, List[str]]:
        """迭代优化任务链.

        多轮优化：识别瓶颈 -> 调整分解粒度 -> 优化执行顺序

        Args:
            nodes: 初始任务节点列表
            max_iterations: 最大迭代次数
            available_tools: 可用工具集合

        Returns:
            (优化后的节点列表, 最终可靠性评分, 优化日志)
        """
        current_nodes = [self._copy_node(node) for node in nodes]
        optimization_log: List[str] = []

        for iteration in range(max_iterations):
            self._logger.info(f"开始第 {iteration + 1} 轮优化")

            # 1. 评估当前链的可靠性
            reliability, issues, _ = self.evaluate_reliability(
                current_nodes, available_tools
            )
            optimization_log.append(
                f"迭代 {iteration + 1}: 可靠性评分 = {reliability:.2f}, 问题数 = {len(issues)}"
            )

            if reliability >= self.reliability_threshold and not issues:
                self._logger.info(f"达到可靠性阈值，提前结束优化")
                break

            # 2. 识别瓶颈
            bottlenecks = self.identify_bottlenecks(current_nodes)

            # 3. 根据瓶颈优化
            if bottlenecks:
                current_nodes = self._optimize_based_on_bottlenecks(
                    current_nodes, bottlenecks
                )
                optimization_log.append(
                    f"  处理 {len(bottlenecks)} 个瓶颈节点"
                )

            # 4. 优化执行顺序
            current_nodes = self._optimize_execution_order(current_nodes)

        # 最终评估
        final_reliability, final_issues, _ = self.evaluate_reliability(
            current_nodes, available_tools
        )
        optimization_log.append(f"最终可靠性评分: {final_reliability:.2f}")

        return current_nodes, final_reliability, optimization_log

    def _optimize_based_on_bottlenecks(
        self,
        nodes: List[TaskNodeInfo],
        bottlenecks: List[BottleneckInfo],
    ) -> List[TaskNodeInfo]:
        """基于瓶颈优化节点.

        Args:
            nodes: 当前节点列表
            bottlenecks: 瓶颈信息列表

        Returns:
            优化后的节点列表
        """
        new_nodes = [self._copy_node(node) for node in nodes]
        bottleneck_ids = {b.node_id for b in bottlenecks}

        for bottleneck in bottlenecks:
            if bottleneck.bottleneck_type == "high_degree":
                # 拆分高度数节点
                node = next(
                    (n for n in new_nodes if n.task_id == bottleneck.node_id), None
                )
                if node and len(node.outputs) > 1:
                    # 简化：将多个输出拆分到不同节点
                    pass  # 实际实现需要更复杂的逻辑

            elif bottleneck.bottleneck_type == "single_point_failure":
                # 为关键节点添加重试标记
                for node in new_nodes:
                    if node.task_id == bottleneck.node_id:
                        node.metadata["retry_enabled"] = True
                        node.metadata["max_retries"] = 3

        return new_nodes

    def _optimize_execution_order(
        self, nodes: List[TaskNodeInfo]
    ) -> List[TaskNodeInfo]:
        """优化节点执行顺序.

        Args:
            nodes: 当前节点列表

        Returns:
            优化后的节点列表
        """
        # 构建任务图并进行拓扑排序
        try:
            graph = TaskGraph()
            for node in nodes:
                from flood_decision_agent.core.task_graph import Node as TaskNode

                task_node = TaskNode(
                    node_id=node.task_id,
                    task_type=node.task_type.value,
                    dependencies=node.dependencies,
                )
                graph.add_node(task_node)

            # 添加边
            for node in nodes:
                for dep in node.dependencies:
                    graph.add_edge(dep, node.task_id)

            # 拓扑排序
            sorted_ids = graph.topological_sort()

            # 按排序结果重新排列节点
            node_map = {node.task_id: node for node in nodes}
            sorted_nodes = [node_map[node_id] for node_id in sorted_ids if node_id in node_map]

            return sorted_nodes

        except Exception as e:
            self._logger.warning(f"执行顺序优化失败: {e}")
            return nodes

    def select_best_chain(
        self,
        alternatives: List[ChainAlternative],
        min_reliability: float = 0.6,
    ) -> Optional[ChainAlternative]:
        """选择最优任务链.

        Args:
            alternatives: 备选链列表
            min_reliability: 最低可靠性要求

        Returns:
            最优链，如果没有满足条件的返回 None
        """
        if not alternatives:
            return None

        # 过滤满足最低可靠性要求的链
        valid_alternatives = [
            alt for alt in alternatives if alt.reliability_score >= min_reliability
        ]

        if not valid_alternatives:
            # 如果没有满足条件的，选择可靠性最高的
            self._logger.warning("没有链满足最低可靠性要求，选择最优者")
            valid_alternatives = alternatives

        # 按可靠性评分排序，选择最高的
        best = max(valid_alternatives, key=lambda x: x.reliability_score)
        self._logger.info(f"选择最优链: {best.chain_id}, 可靠性: {best.reliability_score:.2f}")

        return best
