"""任务分解模块.

提供 TaskDecomposer 类，支持从最终目标逆向分解任务，并进行正向验证和节点结构化。
主要用于洪水调度决策链的生成。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from flood_decision_agent.core.task_graph import Node, NodeStatus


class TaskType(Enum):
    """任务类型枚举.

    Attributes:
        DATA_COLLECTION: 数据采集任务
        PREDICTION: 预测任务
        CALCULATION: 计算任务
        DECISION: 决策任务
        EXECUTION: 执行任务
        VERIFICATION: 验证任务
    """

    DATA_COLLECTION = "data_collection"
    PREDICTION = "prediction"
    CALCULATION = "calculation"
    DECISION = "decision"
    EXECUTION = "execution"
    VERIFICATION = "verification"


@dataclass
class TaskNodeInfo:
    """任务节点信息数据类.

    表示分解后的任务节点，包含完整的任务描述、输入输出和依赖关系。

    Attributes:
        task_id: 任务唯一标识
        task_type: 任务类型
        description: 任务描述
        inputs: 输入数据key列表
        outputs: 输出数据key列表
        dependencies: 依赖任务ID列表
        metadata: 额外元数据
    """

    task_id: str
    task_type: TaskType
    description: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式.

        Returns:
            包含节点信息的字典
        """
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


@dataclass
class DecompositionRule:
    """任务分解规则数据类.

    定义特定任务类型的分解模式。

    Attributes:
        task_type: 任务类型
        sub_tasks: 子任务定义列表
        input_mappings: 输入映射关系
        output_mappings: 输出映射关系
    """

    task_type: TaskType
    sub_tasks: List[Dict[str, Any]]
    input_mappings: Dict[str, List[str]] = field(default_factory=dict)
    output_mappings: Dict[str, List[str]] = field(default_factory=dict)


class DecompositionRuleLibrary:
    """任务分解规则库.

    定义常见任务分解模式、任务类型到子任务的映射、输入输出依赖关系。
    """

    def __init__(self) -> None:
        """初始化规则库，加载预定义规则."""
        self._rules: Dict[TaskType, DecompositionRule] = {}
        self._initialize_rules()

    def _initialize_rules(self) -> None:
        """初始化预定义的分解规则."""
        # 洪水调度任务分解规则
        self._rules[TaskType.EXECUTION] = DecompositionRule(
            task_type=TaskType.EXECUTION,
            sub_tasks=[
                {
                    "task_type": TaskType.EXECUTION,
                    "description": "执行调度操作",
                    "inputs": ["dispatch_plan", "current_state"],
                    "outputs": ["execution_result", "outflow_rate"],
                },
                {
                    "task_type": TaskType.CALCULATION,
                    "description": "计算调度方案",
                    "inputs": ["inflow_forecast", "current_state", "constraints"],
                    "outputs": ["dispatch_plan"],
                },
                {
                    "task_type": TaskType.DATA_COLLECTION,
                    "description": "获取当前水库状态",
                    "inputs": [],
                    "outputs": ["current_state", "water_level", "inflow_rate", "constraints"],
                },
                {
                    "task_type": TaskType.PREDICTION,
                    "description": "预测未来来水",
                    "inputs": ["rainfall_data", "upstream_flow"],
                    "outputs": ["inflow_forecast"],
                },
                {
                    "task_type": TaskType.DATA_COLLECTION,
                    "description": "采集降雨数据",
                    "inputs": [],
                    "outputs": ["rainfall_data"],
                },
                {
                    "task_type": TaskType.DATA_COLLECTION,
                    "description": "采集上游流量数据",
                    "inputs": [],
                    "outputs": ["upstream_flow"],
                },
            ],
            input_mappings={
                "target_outflow": ["dispatch_plan"],
            },
            output_mappings={
                "execution_result": ["execution_result"],
                "outflow_rate": ["outflow_rate"],
            },
        )

        # 决策任务分解规则
        self._rules[TaskType.DECISION] = DecompositionRule(
            task_type=TaskType.DECISION,
            sub_tasks=[
                {
                    "task_type": TaskType.DECISION,
                    "description": "生成最终决策",
                    "inputs": ["options", "risk_assessment"],
                    "outputs": ["decision"],
                },
                {
                    "task_type": TaskType.CALCULATION,
                    "description": "评估各方案风险",
                    "inputs": ["options", "scenario_predictions"],
                    "outputs": ["risk_assessment"],
                },
                {
                    "task_type": TaskType.CALCULATION,
                    "description": "生成备选方案",
                    "inputs": ["constraints", "objectives"],
                    "outputs": ["options"],
                },
            ],
            input_mappings={
                "decision_context": ["constraints", "objectives"],
            },
            output_mappings={
                "decision": ["decision"],
            },
        )

        # 预测任务分解规则
        self._rules[TaskType.PREDICTION] = DecompositionRule(
            task_type=TaskType.PREDICTION,
            sub_tasks=[
                {
                    "task_type": TaskType.PREDICTION,
                    "description": "综合预测",
                    "inputs": ["model_inputs", "historical_data"],
                    "outputs": ["prediction_result"],
                },
                {
                    "task_type": TaskType.DATA_COLLECTION,
                    "description": "准备模型输入数据",
                    "inputs": ["raw_data"],
                    "outputs": ["model_inputs"],
                },
                {
                    "task_type": TaskType.DATA_COLLECTION,
                    "description": "获取历史数据",
                    "inputs": [],
                    "outputs": ["historical_data"],
                },
            ],
            input_mappings={
                "prediction_target": ["raw_data"],
            },
            output_mappings={
                "prediction": ["prediction_result"],
            },
        )

    def get_rule(self, task_type: TaskType) -> Optional[DecompositionRule]:
        """获取指定任务类型的分解规则.

        Args:
            task_type: 任务类型

        Returns:
            分解规则，如果不存在则返回None
        """
        return self._rules.get(task_type)

    def add_rule(self, rule: DecompositionRule) -> None:
        """添加自定义分解规则.

        Args:
            rule: 分解规则对象
        """
        self._rules[rule.task_type] = rule

    def get_all_rules(self) -> Dict[TaskType, DecompositionRule]:
        """获取所有分解规则.

        Returns:
            规则字典的副本
        """
        return self._rules.copy()


class TaskDecomposer:
    """任务分解器.

    支持从最终目标逆向分解任务，并进行正向验证和节点结构化。

    Attributes:
        rule_library: 分解规则库
        _decomposition_cache: 分解结果缓存
    """

    def __init__(self, rule_library: Optional[DecompositionRuleLibrary] = None) -> None:
        """初始化任务分解器.

        Args:
            rule_library: 分解规则库，如果为None则使用默认规则库
        """
        self.rule_library = rule_library or DecompositionRuleLibrary()
        self._decomposition_cache: Dict[str, List[TaskNodeInfo]] = {}

    def decompose_backward(
        self,
        goal: str,
        task_type: TaskType,
        required_outputs: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[TaskNodeInfo]:
        """逆向分解任务.

        从最终目标反向推导所需的子任务，采用自顶向下的分解策略。

        Args:
            goal: 最终目标描述
            task_type: 任务类型
            required_outputs: 需要的输出数据key列表
            context: 额外上下文信息

        Returns:
            分解后的任务节点列表（按执行顺序排列）

        Example:
            >>> decomposer = TaskDecomposer()
            >>> nodes = decomposer.decompose_backward(
            ...     goal="调整出库流量到19000m³/s",
            ...     task_type=TaskType.EXECUTION,
            ...     required_outputs=["outflow_rate"],
            ... )
        """
        context = context or {}
        cache_key = f"{goal}:{task_type.value}:{','.join(sorted(required_outputs))}"

        if cache_key in self._decomposition_cache:
            return self._decomposition_cache[cache_key]

        rule = self.rule_library.get_rule(task_type)
        if not rule:
            # 如果没有预定义规则，创建单节点任务
            node = TaskNodeInfo(
                task_id=self._generate_task_id(task_type.value, 0),
                task_type=task_type,
                description=goal,
                outputs=required_outputs,
            )
            return [node]

        # 逆向构建任务链
        nodes: List[TaskNodeInfo] = []
        node_map: Dict[str, TaskNodeInfo] = {}
        output_to_node: Dict[str, str] = {}

        # 从最终任务开始逆向处理
        for idx, sub_task_def in enumerate(rule.sub_tasks):
            task_id = self._generate_task_id(sub_task_def["task_type"].value, idx)

            # 确定依赖关系：当前任务的输入由哪些节点提供
            deps = []
            for input_key in sub_task_def.get("inputs", []):
                if input_key in output_to_node:
                    dep_id = output_to_node[input_key]
                    if dep_id not in deps:
                        deps.append(dep_id)

            node = TaskNodeInfo(
                task_id=task_id,
                task_type=sub_task_def["task_type"],
                description=sub_task_def.get("description", ""),
                inputs=sub_task_def.get("inputs", []),
                outputs=sub_task_def.get("outputs", []),
                dependencies=deps,
                metadata={
                    "goal": goal,
                    "sequence": idx,
                    **context,
                },
            )

            nodes.append(node)
            node_map[task_id] = node

            # 记录输出到节点的映射
            for output_key in node.outputs:
                output_to_node[output_key] = task_id

        # 反转节点顺序（逆向分解后需要反转得到执行顺序）
        nodes.reverse()

        # 重新计算依赖关系（反转后）
        self._recompute_dependencies(nodes)

        self._decomposition_cache[cache_key] = nodes
        return nodes

    def verify_forward(self, nodes: List[TaskNodeInfo]) -> Tuple[bool, List[str]]:
        """正向验证任务可行性.

        验证任务链的可行性，检查输入输出匹配、循环依赖等。

        Args:
            nodes: 任务节点列表

        Returns:
            (是否验证通过, 错误信息列表)

        Checks:
            1. 输入输出匹配：每个任务的输入都有前置任务提供
            2. 循环依赖检测
            3. 任务ID唯一性
            4. 依赖任务存在性
        """
        errors: List[str] = []

        if not nodes:
            return False, ["任务节点列表为空"]

        # 检查任务ID唯一性
        task_ids = [node.task_id for node in nodes]
        if len(task_ids) != len(set(task_ids)):
            duplicates = self._find_duplicates(task_ids)
            errors.append(f"存在重复的任务ID: {duplicates}")

        # 构建节点映射和可用输出集合
        node_map = {node.task_id: node for node in nodes}
        available_outputs: Set[str] = set()

        # 按顺序验证每个节点
        for idx, node in enumerate(nodes):
            # 检查依赖任务是否存在
            for dep_id in node.dependencies:
                if dep_id not in node_map:
                    errors.append(
                        f"节点 '{node.task_id}' 依赖不存在的任务 '{dep_id}'"
                    )
                else:
                    # 检查循环依赖（依赖的任务必须在当前任务之前）
                    dep_idx = next(
                        (i for i, n in enumerate(nodes) if n.task_id == dep_id), -1
                    )
                    if dep_idx >= idx:
                        errors.append(
                            f"节点 '{node.task_id}' 存在循环依赖或顺序错误"
                        )

            # 检查输入是否满足
            for input_key in node.inputs:
                if input_key not in available_outputs:
                    errors.append(
                        f"节点 '{node.task_id}' 的输入 '{input_key}' 未在前面节点中生成"
                    )

            # 添加当前节点的输出到可用集合
            available_outputs.update(node.outputs)

        return len(errors) == 0, errors

    def structure_nodes(
        self,
        nodes: List[TaskNodeInfo],
        start_id: int = 1,
    ) -> List[Node]:
        """将任务节点信息转换为标准Node对象.

        Args:
            nodes: 任务节点信息列表
            start_id: 起始节点编号

        Returns:
            标准Node对象列表

        Example:
            >>> task_nodes = decomposer.decompose_backward(...)
            >>> structured = decomposer.structure_nodes(task_nodes)
        """
        structured_nodes: List[Node] = []

        for idx, task_node in enumerate(nodes):
            node = Node(
                node_id=f"N{start_id + idx}",
                task_type=task_node.task_type.value,
                dependencies=task_node.dependencies,
                output_keys=task_node.outputs,
                tool_candidates=[],
                execution_strategy="sequential",
            )
            # 添加额外元数据到tool_candidates中
            node.tool_candidates.append({
                "description": task_node.description,
                "inputs": task_node.inputs,
                "metadata": task_node.metadata,
            })
            structured_nodes.append(node)

        return structured_nodes

    def decompose_and_structure(
        self,
        goal: str,
        task_type: TaskType,
        required_outputs: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[TaskNodeInfo], List[Node], List[str]]:
        """一站式分解和结构化.

        执行完整的分解流程：逆向分解 -> 正向验证 -> 节点结构化。

        Args:
            goal: 最终目标描述
            task_type: 任务类型
            required_outputs: 需要的输出数据key列表
            context: 额外上下文信息

        Returns:
            (任务节点信息列表, 标准Node对象列表, 验证错误列表)
            如果验证失败，返回错误信息
        """
        # 1. 逆向分解
        nodes = self.decompose_backward(goal, task_type, required_outputs, context)

        # 2. 正向验证
        is_valid, errors = self.verify_forward(nodes)

        if not is_valid:
            return nodes, [], errors

        # 3. 节点结构化
        structured = self.structure_nodes(nodes)

        return nodes, structured, []

    def _generate_task_id(self, prefix: str, index: int) -> str:
        """生成任务ID.

        Args:
            prefix: ID前缀
            index: 索引号

        Returns:
            生成的任务ID
        """
        return f"{prefix}_{index:03d}"

    def _recompute_dependencies(self, nodes: List[TaskNodeInfo]) -> None:
        """重新计算节点依赖关系.

        在节点顺序反转后，需要重新计算依赖关系。

        Args:
            nodes: 任务节点列表（已按执行顺序排列）
        """
        # 构建输出到节点的映射
        output_to_node: Dict[str, str] = {}
        for node in nodes:
            for output in node.outputs:
                output_to_node[output] = node.task_id

        # 重新计算每个节点的依赖
        for node in nodes:
            new_deps = []
            for input_key in node.inputs:
                if input_key in output_to_node:
                    dep_id = output_to_node[input_key]
                    # 只添加在当前节点之前的依赖
                    dep_idx = next(
                        (i for i, n in enumerate(nodes) if n.task_id == dep_id), -1
                    )
                    current_idx = next(
                        (i for i, n in enumerate(nodes) if n.task_id == node.task_id), -1
                    )
                    if dep_idx < current_idx and dep_id not in new_deps:
                        new_deps.append(dep_id)
            node.dependencies = new_deps

    def _find_duplicates(self, items: List[str]) -> List[str]:
        """查找列表中的重复项.

        Args:
            items: 字符串列表

        Returns:
            重复项列表
        """
        seen = set()
        duplicates = set()
        for item in items:
            if item in seen:
                duplicates.add(item)
            seen.add(item)
        return list(duplicates)

    def clear_cache(self) -> None:
        """清除分解结果缓存."""
        self._decomposition_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计信息.

        Returns:
            缓存统计字典
        """
        return {
            "cache_size": len(self._decomposition_cache),
        }
