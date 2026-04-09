"""贪心 + 启发式链路优化器.

基于贪心策略和启发式规则的链路优化实现，适用于快速原型验证。
通过局部最优选择和启发式规则快速生成可靠的优化方案。
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from flood_decision_agent.agents.decision_chain.chain_optimizer import (
    BottleneckInfo,
    ChainAlternative,
    ChainOptimizer,
)
from flood_decision_agent.agents.decision_chain.task_decomposer import TaskNodeInfo, TaskType
from flood_decision_agent.core.task_graph import TaskGraph
from flood_decision_agent.infra.logging import get_logger


@dataclass
class HeuristicScore:
    """启发式评分数据类."""

    total_score: float = 0.0
    parallelism_score: float = 0.0
    load_balance_score: float = 0.0
    critical_path_score: float = 0.0
    resource_util_score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


class HeuristicOptimizer(ChainOptimizer):
    """贪心 + 启发式链路优化器.

    优化策略：
    1. 贪心选择：每次选择当前最优的局部解
    2. 启发式规则：基于领域知识的快速决策
    3. 快速收敛：有限迭代次数内达到可接受解

    适用场景：
    - 快速原型验证
    - 中等复杂度问题
    - 对计算资源有限的场景
    """

    def __init__(
        self,
        max_alternatives: int = 3,
        reliability_threshold: float = 0.7,
        max_iterations: int = 5,
    ):
        """初始化启发式优化器.

        Args:
            max_alternatives: 最大备选链数量
            reliability_threshold: 可靠性阈值
            max_iterations: 最大迭代次数
        """
        super().__init__(max_alternatives, reliability_threshold)
        self.max_iterations = max_iterations
        self._logger = get_logger().bind(name=self.__class__.__name__)

    def optimize_iteratively(
        self,
        nodes: List[TaskNodeInfo],
        max_iterations: Optional[int] = None,
        available_tools: Optional[Set[str]] = None,
    ) -> Tuple[List[TaskNodeInfo], float, List[str]]:
        """贪心 + 启发式迭代优化.

        优化流程：
        1. 初始评估和快速修复
        2. 贪心选择优化策略
        3. 启发式规则应用
        4. 局部搜索改进
        5. 收敛判断

        Args:
            nodes: 初始任务节点列表
            max_iterations: 最大迭代次数（覆盖默认值）
            available_tools: 可用工具集合

        Returns:
            (优化后的节点列表, 最终可靠性评分, 优化日志)
        """
        iterations = max_iterations or self.max_iterations
        current_nodes = [self._copy_node(node) for node in nodes]
        optimization_log: List[str] = []

        self._logger.info(f"开始启发式优化，初始节点数: {len(nodes)}")

        for iteration in range(iterations):
            self._logger.info(f"第 {iteration + 1}/{iterations} 轮优化")

            # 1. 评估当前状态
            reliability, issues, details = self.evaluate_reliability(
                current_nodes, available_tools
            )

            optimization_log.append(
                f"迭代 {iteration + 1}: 可靠性={reliability:.2f}, 问题={len(issues)}"
            )

            # 如果已达到阈值且无问题，提前结束
            if reliability >= self.reliability_threshold and not issues:
                optimization_log.append("达到可靠性阈值，优化完成")
                break

            # 2. 识别优化机会
            improvements = self._identify_improvements(current_nodes, issues, details)

            if not improvements:
                optimization_log.append("无更多优化空间")
                break

            # 3. 贪心选择：按收益排序，选择最优改进
            improvements.sort(key=lambda x: x["benefit"], reverse=True)
            best_improvement = improvements[0]

            # 4. 应用改进
            current_nodes = self._apply_improvement(
                current_nodes, best_improvement
            )

            optimization_log.append(
                f"  应用改进: {best_improvement['name']}, 预期收益={best_improvement['benefit']:.2f}"
            )

        # 最终评估
        final_reliability, final_issues, _ = self.evaluate_reliability(
            current_nodes, available_tools
        )
        optimization_log.append(f"最终可靠性: {final_reliability:.2f}")

        return current_nodes, final_reliability, optimization_log

    def _identify_improvements(
        self,
        nodes: List[TaskNodeInfo],
        issues: List[str],
        details: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """识别可能的改进方案.

        Args:
            nodes: 当前节点列表
            issues: 问题列表
            details: 评估详情

        Returns:
            改进方案列表，每个方案包含名称、收益和执行函数
        """
        improvements: List[Dict[str, Any]] = []

        # 1. 并行化改进
        parallel_opps = self._find_parallelization_opportunities(nodes)
        for opp in parallel_opps:
            improvements.append({
                "name": f"并行化_{opp['node_id']}",
                "benefit": opp["benefit"],
                "type": "parallelize",
                "data": opp,
            })

        # 2. 任务拆分改进
        split_opps = self._find_split_opportunities(nodes)
        for opp in split_opps:
            improvements.append({
                "name": f"拆分_{opp['node_id']}",
                "benefit": opp["benefit"],
                "type": "split",
                "data": opp,
            })

        # 3. 执行顺序优化
        if self._can_reorder(nodes):
            improvements.append({
                "name": "优化执行顺序",
                "benefit": 0.15,
                "type": "reorder",
                "data": {},
            })

        # 4. 依赖关系简化
        if issues and any("依赖" in issue for issue in issues):
            improvements.append({
                "name": "简化依赖关系",
                "benefit": 0.2,
                "type": "simplify_deps",
                "data": {},
            })

        # 5. 关键路径优化
        critical_path = self._identify_critical_path(nodes)
        if len(critical_path) > 3:
            improvements.append({
                "name": "优化关键路径",
                "benefit": 0.25,
                "type": "optimize_critical",
                "data": {"critical_path": critical_path},
            })

        return improvements

    def _find_parallelization_opportunities(
        self, nodes: List[TaskNodeInfo]
    ) -> List[Dict[str, Any]]:
        """寻找并行化机会.

        启发式规则：
        - 数据采集类任务通常可以并行
        - 无依赖关系的独立任务可以并行
        - 计算密集型任务在资源允许时可以并行

        Args:
            nodes: 任务节点列表

        Returns:
            并行化机会列表
        """
        opportunities: List[Dict[str, Any]] = []

        # 按任务类型分组
        nodes_by_type: Dict[TaskType, List[TaskNodeInfo]] = {}
        for node in nodes:
            nodes_by_type.setdefault(node.task_type, []).append(node)

        # 规则1: 数据采集任务并行化
        data_collection_nodes = nodes_by_type.get(TaskType.DATA_COLLECTION, [])
        if len(data_collection_nodes) >= 2:
            # 计算潜在收益（节省的时间）
            potential_saving = len(data_collection_nodes) * 0.3
            opportunities.append({
                "node_id": "data_collection_group",
                "benefit": min(potential_saving, 0.5),
                "nodes": [n.task_id for n in data_collection_nodes],
                "strategy": "parallel_data_collection",
            })

        # 规则2: 独立任务并行化
        independent_nodes = [
            node for node in nodes
            if not node.dependencies and node.task_id not in [
                opp["node_id"] for opp in opportunities
            ]
        ]

        if len(independent_nodes) >= 2:
            opportunities.append({
                "node_id": "independent_group",
                "benefit": 0.2,
                "nodes": [n.task_id for n in independent_nodes[:3]],  # 最多3个
                "strategy": "parallel_independent",
            })

        return opportunities

    def _find_split_opportunities(
        self, nodes: List[TaskNodeInfo]
    ) -> List[Dict[str, Any]]:
        """寻找任务拆分机会.

        启发式规则：
        - 输出过多的复杂任务应该拆分
        - 计算密集型任务可以拆分为子任务
        - 多步骤任务可以按步骤拆分

        Args:
            nodes: 任务节点列表

        Returns:
            拆分机会列表
        """
        opportunities: List[Dict[str, Any]] = []

        for node in nodes:
            # 规则1: 输出过多的任务
            if len(node.outputs) > 3:
                benefit = min((len(node.outputs) - 2) * 0.1, 0.3)
                opportunities.append({
                    "node_id": node.task_id,
                    "benefit": benefit,
                    "reason": "too_many_outputs",
                    "suggested_splits": len(node.outputs),
                })

            # 规则2: 计算密集型任务
            elif (
                node.task_type == TaskType.CALCULATION
                and len(node.inputs) > 2
            ):
                opportunities.append({
                    "node_id": node.task_id,
                    "benefit": 0.15,
                    "reason": "complex_calculation",
                    "suggested_splits": 2,
                })

        return opportunities

    def _apply_improvement(
        self,
        nodes: List[TaskNodeInfo],
        improvement: Dict[str, Any],
    ) -> List[TaskNodeInfo]:
        """应用改进方案.

        Args:
            nodes: 当前节点列表
            improvement: 改进方案

        Returns:
            改进后的节点列表
        """
        improvement_type = improvement["type"]
        new_nodes = [self._copy_node(node) for node in nodes]

        if improvement_type == "parallelize":
            new_nodes = self._apply_parallel_optimization(
                new_nodes, improvement["data"]
            )

        elif improvement_type == "split":
            new_nodes = self._apply_split_optimization(
                new_nodes, improvement["data"]
            )

        elif improvement_type == "reorder":
            new_nodes = self._apply_reorder_optimization(new_nodes)

        elif improvement_type == "simplify_deps":
            new_nodes = self._apply_dependency_simplification(new_nodes)

        elif improvement_type == "optimize_critical":
            new_nodes = self._apply_critical_path_optimization(
                new_nodes, improvement["data"]["critical_path"]
            )

        return new_nodes

    def _apply_parallel_optimization(
        self,
        nodes: List[TaskNodeInfo],
        data: Dict[str, Any],
    ) -> List[TaskNodeInfo]:
        """应用并行化优化.

        Args:
            nodes: 节点列表
            data: 并行化数据

        Returns:
            优化后的节点列表
        """
        strategy = data.get("strategy", "")
        target_nodes = data.get("nodes", [])

        if strategy == "parallel_data_collection":
            # 让数据采集任务并行执行
            dc_nodes = [
                n for n in nodes
                if n.task_id in target_nodes
            ]

            if dc_nodes:
                # 找到第一个数据采集任务的依赖
                first_deps = dc_nodes[0].dependencies

                for node in dc_nodes[1:]:
                    # 让其他数据采集任务也依赖相同的前置任务
                    node.dependencies = [
                        dep for dep in node.dependencies
                        if dep not in [n.task_id for n in dc_nodes]
                    ]
                    if not node.dependencies:
                        node.dependencies = list(first_deps)

                self._logger.debug(f"并行化 {len(dc_nodes)} 个数据采集任务")

        elif strategy == "parallel_independent":
            # 独立任务已经是并行的，标记为可并行执行
            for node in nodes:
                if node.task_id in target_nodes:
                    node.metadata["parallel_executable"] = True

        return nodes

    def _apply_split_optimization(
        self,
        nodes: List[TaskNodeInfo],
        data: Dict[str, Any],
    ) -> List[TaskNodeInfo]:
        """应用任务拆分优化.

        Args:
            nodes: 节点列表
            data: 拆分数据

        Returns:
            优化后的节点列表
        """
        node_id = data["node_id"]
        reason = data.get("reason", "")

        # 找到要拆分的节点
        target_idx = None
        target_node = None

        for idx, node in enumerate(nodes):
            if node.task_id == node_id:
                target_idx = idx
                target_node = node
                break

        if target_node is None:
            return nodes

        # 根据原因执行不同的拆分策略
        new_nodes: List[TaskNodeInfo] = []

        if reason == "too_many_outputs":
            # 按输出拆分
            outputs = target_node.outputs
            mid = len(outputs) // 2

            # 第一个子任务
            sub_node_1 = TaskNodeInfo(
                task_id=f"{node_id}_sub_1",
                task_type=target_node.task_type,
                description=f"{target_node.description} (部分1)",
                inputs=target_node.inputs,
                outputs=outputs[:mid],
                dependencies=target_node.dependencies,
                metadata={"parent_task": node_id, "split_part": 1},
            )

            # 第二个子任务
            sub_node_2 = TaskNodeInfo(
                task_id=f"{node_id}_sub_2",
                task_type=target_node.task_type,
                description=f"{target_node.description} (部分2)",
                inputs=target_node.inputs,
                outputs=outputs[mid:],
                dependencies=target_node.dependencies + [sub_node_1.task_id],
                metadata={"parent_task": node_id, "split_part": 2},
            )

            # 替换原节点
            new_nodes = nodes[:target_idx] + [sub_node_1, sub_node_2] + nodes[target_idx + 1:]

            # 更新其他节点对原节点的依赖
            for node in new_nodes:
                if node_id in node.dependencies:
                    node.dependencies.remove(node_id)
                    node.dependencies.append(sub_node_2.task_id)

            self._logger.debug(f"拆分任务 {node_id} 为2个子任务")

        else:
            # 其他情况暂不拆分
            new_nodes = nodes

        return new_nodes

    def _apply_reorder_optimization(
        self, nodes: List[TaskNodeInfo]
    ) -> List[TaskNodeInfo]:
        """应用执行顺序优化.

        使用拓扑排序确保依赖关系正确，同时优化执行顺序。

        Args:
            nodes: 节点列表

        Returns:
            优化后的节点列表
        """
        return self._optimize_execution_order(nodes)

    def _apply_dependency_simplification(
        self, nodes: List[TaskNodeInfo]
    ) -> List[TaskNodeInfo]:
        """应用依赖关系简化.

        移除冗余的传递依赖。

        Args:
            nodes: 节点列表

        Returns:
            优化后的节点列表
        """
        node_map = {node.task_id: node for node in nodes}

        for node in nodes:
            # 检查每个依赖是否是冗余的
            deps_to_remove: List[str] = []

            for dep in node.dependencies:
                # 如果该依赖可以通过其他依赖间接到达，则是冗余的
                for other_dep in node.dependencies:
                    if dep != other_dep and self._can_reach(other_dep, dep, node_map):
                        deps_to_remove.append(dep)
                        break

            # 移除冗余依赖
            for dep in deps_to_remove:
                node.dependencies.remove(dep)
                self._logger.debug(f"移除冗余依赖: {node.task_id} -> {dep}")

        return nodes

    def _apply_critical_path_optimization(
        self,
        nodes: List[TaskNodeInfo],
        critical_path: List[str],
    ) -> List[TaskNodeInfo]:
        """应用关键路径优化.

        对关键路径上的任务进行优先处理和资源分配。

        Args:
            nodes: 节点列表
            critical_path: 关键路径节点ID列表

        Returns:
            优化后的节点列表
        """
        for node in nodes:
            if node.task_id in critical_path:
                # 标记为关键路径任务
                node.metadata["critical_path"] = True
                node.metadata["priority"] = "high"

                # 为关键任务添加重试机制
                if node.task_type in [TaskType.DECISION, TaskType.EXECUTION]:
                    node.metadata["retry_enabled"] = True
                    node.metadata["max_retries"] = 3

        return nodes

    def _can_reach(
        self,
        start: str,
        target: str,
        node_map: Dict[str, TaskNodeInfo],
    ) -> bool:
        """检查从start是否可以到达target（通过依赖关系）.

        Args:
            start: 起始节点ID
            target: 目标节点ID
            node_map: 节点映射

        Returns:
            是否可以到达
        """
        if start == target:
            return True

        visited: Set[str] = set()
        stack = [start]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)

            node = node_map.get(current)
            if node:
                for dep in node.dependencies:
                    if dep == target:
                        return True
                    stack.append(dep)

        return False

    def _identify_critical_path(self, nodes: List[TaskNodeInfo]) -> List[str]:
        """识别关键路径.

        关键路径是任务链中最长的依赖路径。

        Args:
            nodes: 节点列表

        Returns:
            关键路径节点ID列表
        """
        if not nodes:
            return []

        # 构建节点深度映射
        node_map = {node.task_id: node for node in nodes}
        depths: Dict[str, int] = {}

        def get_depth(node_id: str) -> int:
            if node_id in depths:
                return depths[node_id]

            node = node_map.get(node_id)
            if not node:
                return 0

            if not node.dependencies:
                depths[node_id] = 1
            else:
                depths[node_id] = 1 + max(
                    get_depth(dep) for dep in node.dependencies
                )

            return depths[node_id]

        # 计算所有节点深度
        for node in nodes:
            get_depth(node.task_id)

        # 找到最大深度
        if not depths:
            return []

        max_depth = max(depths.values())

        # 回溯关键路径
        critical_path: List[str] = []
        current_depth = max_depth

        # 找到最深层的节点
        candidates = [nid for nid, d in depths.items() if d == current_depth]
        if not candidates:
            return []

        # 选择第一个（可以添加更多启发式规则选择最优）
        current = candidates[0]
        critical_path.append(current)

        # 回溯
        while current_depth > 1:
            node = node_map.get(current)
            if not node or not node.dependencies:
                break

            # 找到前驱中深度最大的
            prev_nodes = [
                dep for dep in node.dependencies
                if dep in depths and depths[dep] == current_depth - 1
            ]

            if not prev_nodes:
                break

            current = prev_nodes[0]
            critical_path.append(current)
            current_depth -= 1

        critical_path.reverse()
        return critical_path

    def _can_reorder(self, nodes: List[TaskNodeInfo]) -> bool:
        """检查是否可以重新排序.

        Args:
            nodes: 节点列表

        Returns:
            是否可以重排序
        """
        # 如果有多个独立任务，可以重排序
        independent_count = sum(
            1 for node in nodes if not node.dependencies
        )
        return independent_count >= 2

    def generate_heuristic_alternatives(
        self,
        base_nodes: List[TaskNodeInfo],
    ) -> List[ChainAlternative]:
        """基于启发式规则生成备选链.

        Args:
            base_nodes: 基础任务节点列表

        Returns:
            备选链列表
        """
        alternatives: List[ChainAlternative] = []

        # 策略1: 默认策略
        default_nodes = [self._copy_node(node) for node in base_nodes]
        alt1 = ChainAlternative(
            chain_id="heuristic_default",
            nodes=default_nodes,
            strategy="default",
            metadata={"description": "原始任务链"},
        )
        alternatives.append(alt1)

        # 策略2: 最大化并行
        parallel_nodes = self._apply_parallel_strategy(base_nodes)
        alt2 = ChainAlternative(
            chain_id="heuristic_parallel",
            nodes=parallel_nodes,
            strategy="max_parallel",
            metadata={"description": "最大化并行执行"},
        )
        alternatives.append(alt2)

        # 策略3: 优化关键路径
        critical_nodes = self._optimize_critical_path(base_nodes)
        alt3 = ChainAlternative(
            chain_id="heuristic_critical",
            nodes=critical_nodes,
            strategy="critical_path",
            metadata={"description": "关键路径优化"},
        )
        alternatives.append(alt3)

        # 评估所有备选链
        for alt in alternatives:
            reliability, _, _ = self.evaluate_reliability(alt.nodes)
            alt.reliability_score = reliability

        return alternatives

    def _optimize_critical_path(
        self, nodes: List[TaskNodeInfo]
    ) -> List[TaskNodeInfo]:
        """优化关键路径.

        Args:
            nodes: 节点列表

        Returns:
            优化后的节点列表
        """
        new_nodes = [self._copy_node(node) for node in nodes]
        critical_path = self._identify_critical_path(new_nodes)

        # 对关键路径上的任务进行优化
        for node in new_nodes:
            if node.task_id in critical_path:
                # 减少关键任务的依赖（如果可能）
                if len(node.dependencies) > 1:
                    # 保留最重要的依赖
                    node.dependencies = node.dependencies[:2]

        return new_nodes

    def get_optimization_report(
        self,
        original_nodes: List[TaskNodeInfo],
        optimized_nodes: List[TaskNodeInfo],
    ) -> Dict[str, Any]:
        """生成优化报告.

        Args:
            original_nodes: 原始节点列表
            optimized_nodes: 优化后的节点列表

        Returns:
            优化报告
        """
        orig_reliability, orig_issues, _ = self.evaluate_reliability(original_nodes)
        opt_reliability, opt_issues, _ = self.evaluate_reliability(optimized_nodes)

        return {
            "original": {
                "node_count": len(original_nodes),
                "reliability": orig_reliability,
                "issues": len(orig_issues),
            },
            "optimized": {
                "node_count": len(optimized_nodes),
                "reliability": opt_reliability,
                "issues": len(opt_issues),
            },
            "improvement": {
                "reliability_gain": opt_reliability - orig_reliability,
                "issue_reduction": len(orig_issues) - len(opt_issues),
                "node_change": len(optimized_nodes) - len(original_nodes),
            },
            "strategies_applied": [
                "并行化",
                "任务拆分",
                "依赖简化",
                "关键路径优化",
            ],
        }
