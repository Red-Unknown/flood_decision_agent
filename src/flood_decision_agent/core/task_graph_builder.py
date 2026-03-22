"""任务图构建器模块.

提供从任务链构建任务图的功能，包括依赖管理、图结构验证和节点配置生成。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from flood_decision_agent.core.task_graph import Node, TaskGraph
from flood_decision_agent.tools.registry import ToolMetadata, ToolRegistry


@dataclass
class TaskChainItem:
    """任务链项数据类.

    表示任务链中的一个任务项，包含任务的基本信息和依赖关系。

    Attributes:
        task_id: 任务唯一标识
        task_type: 任务类型
        description: 任务描述
        inputs: 输入参数字典
        outputs: 输出参数列表
        dependencies: 依赖任务ID列表
    """

    task_id: str
    task_type: str
    description: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class NodeConfig:
    """节点配置数据类.

    包含节点的详细执行配置信息。

    Attributes:
        handler_candidates: 工具候选列表，每个工具为字典格式
        strategy: 执行策略
        input_keys: 输入数据key列表
        output_keys: 输出数据key列表
    """

    handler_candidates: List[Dict[str, Any]] = field(default_factory=list)
    strategy: str = ""
    input_keys: List[str] = field(default_factory=list)
    output_keys: List[str] = field(default_factory=list)


class TaskGraphBuilder:
    """任务图构建器类.

    负责从任务链构建完整的任务图，包括节点创建、依赖添加、
    图结构验证和节点详细配置生成。

    Attributes:
        tool_registry: 工具注册中心实例
        _logger: 可选的日志记录器
    """

    def __init__(self, tool_registry: Optional[ToolRegistry] = None) -> None:
        """初始化任务图构建器.

        Args:
            tool_registry: 工具注册中心实例，若为None则使用全局注册中心
        """
        if tool_registry is None:
            from flood_decision_agent.tools.registry import get_tool_registry

            self.tool_registry = get_tool_registry()
        else:
            self.tool_registry = tool_registry
        self._logger: Optional[Any] = None

    def set_logger(self, logger: Any) -> None:
        """设置日志记录器.

        Args:
            logger: 日志记录器实例
        """
        self._logger = logger

    def build_from_chain(self, task_chain: List[TaskChainItem]) -> TaskGraph:
        """从任务链构建任务图.

        根据任务链列表创建任务图，包括节点创建、依赖添加和配置生成。

        Args:
            task_chain: 任务链列表，每个项包含任务的基本信息

        Returns:
            构建完成的TaskGraph对象

        Raises:
            ValueError: 如果任务链为空或存在无效的任务ID
        """
        if not task_chain:
            raise ValueError("任务链不能为空")

        graph = TaskGraph()

        # 第一步：创建所有节点（不添加依赖）
        for task in task_chain:
            node_config = self._generate_node_config(task)
            node = Node(
                node_id=task.task_id,
                task_type=task.task_type,
                dependencies=[],  # 先不设置依赖，后面统一添加
                tool_candidates=node_config.handler_candidates,
                execution_strategy=node_config.strategy,
                output_keys=node_config.output_keys,
            )
            graph.add_node(node)

            if self._logger:
                self._logger.debug(f"添加节点: {task.task_id}, 类型: {task.task_type}")

        # 第二步：添加依赖边
        for task in task_chain:
            if task.dependencies:
                self.add_dependencies(graph, task.task_id, task.dependencies)

        # 第三步：验证图结构
        self.validate_graph(graph)

        if self._logger:
            self._logger.info(f"任务图构建完成，共 {len(task_chain)} 个节点")

        return graph

    def add_dependencies(
        self, graph: TaskGraph, node_id: str, dependencies: List[str]
    ) -> None:
        """为指定节点添加依赖边.

        Args:
            graph: 任务图对象
            node_id: 目标节点ID
            dependencies: 依赖节点ID列表

        Raises:
            ValueError: 如果节点不存在或形成循环依赖
        """
        node = graph.get_node(node_id)
        if node is None:
            raise ValueError(f"节点不存在: {node_id}")

        for dep_id in dependencies:
            if graph.get_node(dep_id) is None:
                raise ValueError(f"依赖节点不存在: {dep_id}")

            # 添加依赖关系到节点的dependencies列表
            if dep_id not in node.dependencies:
                node.dependencies.append(dep_id)

            # 添加边到图的邻接表
            graph.add_edge(dep_id, node_id)

            if self._logger:
                self._logger.debug(f"添加依赖边: {dep_id} -> {node_id}")

    def validate_graph(self, graph: TaskGraph) -> Tuple[bool, Optional[str]]:
        """验证任务图结构的合法性.

        检查内容包括：
        1. 循环依赖检测
        2. 孤立节点检测
        3. 依赖节点存在性检查

        Args:
            graph: 要验证的任务图对象

        Returns:
            (是否有效, 错误信息) 元组，若有效则错误信息为None

        Raises:
            ValueError: 如果图结构存在严重问题
        """
        nodes = graph.get_all_nodes()

        if not nodes:
            return False, "任务图为空"

        # 1. 检查循环依赖（使用拓扑排序）
        try:
            graph.topological_sort()
        except ValueError as e:
            error_msg = f"循环依赖检测失败: {str(e)}"
            if self._logger:
                self._logger.error(error_msg)
            raise ValueError(error_msg)

        # 2. 检查孤立节点（没有依赖也没有被依赖的节点）
        isolated_nodes = self._find_isolated_nodes(graph)
        if isolated_nodes:
            warning_msg = f"发现孤立节点: {isolated_nodes}"
            if self._logger:
                self._logger.warning(warning_msg)

        # 3. 检查依赖节点存在性
        missing_deps = self._check_missing_dependencies(graph)
        if missing_deps:
            error_msg = f"存在未找到的依赖节点: {missing_deps}"
            if self._logger:
                self._logger.error(error_msg)
            raise ValueError(error_msg)

        # 4. 检查节点配置完整性
        incomplete_nodes = self._check_node_config_integrity(graph)
        if incomplete_nodes:
            warning_msg = f"节点配置不完整: {incomplete_nodes}"
            if self._logger:
                self._logger.warning(warning_msg)

        if self._logger:
            self._logger.info("任务图验证通过")

        return True, None

    def _generate_node_config(self, task: TaskChainItem) -> NodeConfig:
        """生成节点的详细配置.

        包括工具候选分配、执行策略确定和输入输出key定义。

        Args:
            task: 任务链项

        Returns:
            节点配置对象
        """
        config = NodeConfig()

        # 1. 分配工具候选
        config.handler_candidates = self._assign_tool_candidates(task)

        # 2. 确定执行策略
        config.strategy = self._determine_execution_strategy(task, config.handler_candidates)

        # 3. 定义输入输出key
        config.input_keys = self._define_input_keys(task)
        config.output_keys = self._define_output_keys(task)

        return config

    def _assign_tool_candidates(self, task: TaskChainItem) -> List[Dict[str, Any]]:
        """为任务分配工具候选.

        根据任务类型从工具注册中心查找匹配的工具。

        Args:
            task: 任务链项

        Returns:
            工具候选列表，按优先级排序
        """
        candidates: List[Dict[str, Any]] = []

        # 从注册中心查找支持该任务类型的工具
        matching_tools = self.tool_registry.find_by_task_type(task.task_type)

        for tool_meta in matching_tools:
            candidate = {
                "name": tool_meta.name,
                "description": tool_meta.description,
                "priority": tool_meta.priority,
                "required_keys": list(tool_meta.required_keys),
                "output_keys": list(tool_meta.output_keys),
            }
            candidates.append(candidate)

        if self._logger:
            self._logger.debug(
                f"任务 {task.task_id} 找到 {len(candidates)} 个工具候选"
            )

        return candidates

    def _determine_execution_strategy(
        self, task: TaskChainItem, candidates: List[Dict[str, Any]]
    ) -> str:
        """确定任务的执行策略.

        根据工具候选数量和任务特性选择合适的执行策略。

        Args:
            task: 任务链项
            candidates: 工具候选列表

        Returns:
            执行策略名称
        """
        # 策略选择逻辑：
        # - 如果没有候选工具，返回 "no_handler"
        # - 如果只有一个候选，返回 "single"
        # - 如果有多个候选，返回 "fallback"（支持回退）
        # - 如果任务类型为关键决策，返回 "ensemble"（集成多个工具）

        if not candidates:
            return "no_handler"

        if len(candidates) == 1:
            return "single"

        # 关键决策类任务使用集成策略
        critical_task_types = {"flood_forecast", "risk_assessment", "decision_making"}
        if task.task_type in critical_task_types:
            return "ensemble"

        return "fallback"

    def _define_input_keys(self, task: TaskChainItem) -> List[str]:
        """定义节点的输入数据key.

        从任务的inputs和依赖关系确定输入key列表。

        Args:
            task: 任务链项

        Returns:
            输入数据key列表
        """
        input_keys: Set[str] = set()

        # 添加任务定义的输入参数
        if isinstance(task.inputs, dict):
            input_keys.update(task.inputs.keys())
        elif isinstance(task.inputs, list):
            input_keys.update(task.inputs)

        # 添加依赖任务的输出作为输入
        # 注意：这里只是标记需要依赖任务的输出，具体映射在执行时处理
        for dep_id in task.dependencies:
            input_keys.add(f"dep:{dep_id}")

        return list(input_keys)

    def _define_output_keys(self, task: TaskChainItem) -> List[str]:
        """定义节点的输出数据key.

        从任务的outputs和工具候选确定输出key列表。

        Args:
            task: 任务链项

        Returns:
            输出数据key列表
        """
        output_keys: Set[str] = set()

        # 添加任务定义的输出参数
        output_keys.update(task.outputs)

        # 从工具候选中获取输出key
        candidates = self.tool_registry.find_by_task_type(task.task_type)
        for tool_meta in candidates:
            output_keys.update(tool_meta.output_keys)

        return list(output_keys)

    def _find_isolated_nodes(self, graph: TaskGraph) -> List[str]:
        """查找孤立节点.

        孤立节点是指没有依赖其他节点也没有被其他节点依赖的节点。

        Args:
            graph: 任务图对象

        Returns:
            孤立节点ID列表
        """
        nodes = graph.get_all_nodes()
        isolated: List[str] = []

        # 构建反向依赖图（哪些节点依赖当前节点）
        depended_by: Dict[str, Set[str]] = {node_id: set() for node_id in nodes}
        for node_id, node in nodes.items():
            for dep_id in node.dependencies:
                if dep_id in depended_by:
                    depended_by[dep_id].add(node_id)

        for node_id, node in nodes.items():
            # 没有依赖且没有被依赖
            if not node.dependencies and not depended_by[node_id]:
                isolated.append(node_id)

        return isolated

    def _check_missing_dependencies(self, graph: TaskGraph) -> List[Tuple[str, str]]:
        """检查缺失的依赖节点.

        Args:
            graph: 任务图对象

        Returns:
            (节点ID, 缺失的依赖ID) 元组列表
        """
        nodes = graph.get_all_nodes()
        missing: List[Tuple[str, str]] = []

        for node_id, node in nodes.items():
            for dep_id in node.dependencies:
                if dep_id not in nodes:
                    missing.append((node_id, dep_id))

        return missing

    def _check_node_config_integrity(self, graph: TaskGraph) -> List[Tuple[str, str]]:
        """检查节点配置的完整性.

        Args:
            graph: 任务图对象

        Returns:
            (节点ID, 问题描述) 元组列表
        """
        nodes = graph.get_all_nodes()
        incomplete: List[Tuple[str, str]] = []

        for node_id, node in nodes.items():
            # 检查是否有工具候选
            if not node.tool_candidates:
                incomplete.append((node_id, "没有可用的工具候选"))

            # 检查执行策略
            if not node.execution_strategy:
                incomplete.append((node_id, "未设置执行策略"))

            # 检查输出key
            if not node.output_keys:
                incomplete.append((node_id, "未定义输出key"))

        return incomplete

    def get_execution_order(self, graph: TaskGraph) -> List[str]:
        """获取任务的执行顺序.

        使用拓扑排序返回节点的执行顺序。

        Args:
            graph: 任务图对象

        Returns:
            按执行顺序排列的节点ID列表

        Raises:
            ValueError: 如果图中存在循环依赖
        """
        return graph.topological_sort()

    def rebuild_graph(
        self, graph: TaskGraph, task_chain: List[TaskChainItem]
    ) -> TaskGraph:
        """基于新的任务链重建任务图.

        保留已存在节点的状态，只更新变更的部分。

        Args:
            graph: 原始任务图
            task_chain: 新的任务链

        Returns:
            重建后的任务图
        """
        # 创建新图
        new_graph = self.build_from_chain(task_chain)

        # 保留原图中已完成节点的状态
        for node_id in new_graph.get_all_nodes():
            old_node = graph.get_node(node_id)
            if old_node is not None:
                # 可以在这里保留一些状态信息
                pass

        if self._logger:
            self._logger.info("任务图重建完成")

        return new_graph
