"""任务图数据结构模块.

提供节点调度Agent所需的核心数据结构，包括节点状态枚举、节点数据类和任务图类。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeStatus(Enum):
    """节点执行状态枚举.

    Attributes:
        PENDING: 等待中
        READY: 准备就绪
        RUNNING: 执行中
        COMPLETED: 已完成
        FAILED: 执行失败
    """

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Node:
    """任务节点数据类.

    表示任务图中的一个节点，包含节点的基本信息、依赖关系和执行状态。

    Attributes:
        node_id: 节点唯一标识
        task_type: 任务类型
        dependencies: 依赖节点ID列表
        status: 节点当前执行状态
        tool_candidates: 工具候选集，每个工具为字典格式
        execution_strategy: 执行策略
        output_keys: 输出数据key列表
    """

    node_id: str
    task_type: str
    dependencies: List[str] = field(default_factory=list)
    status: NodeStatus = field(init=False)
    tool_candidates: List[Dict[str, Any]] = field(default_factory=list)
    execution_strategy: str = ""
    output_keys: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """初始化后处理，设置默认状态为PENDING."""
        self.status = NodeStatus.PENDING

    def __hash__(self) -> int:
        """基于node_id的哈希函数，支持在集合和字典中使用."""
        return hash(self.node_id)

    def __eq__(self, other: object) -> bool:
        """基于node_id的相等性比较."""
        if not isinstance(other, Node):
            return NotImplemented
        return self.node_id == other.node_id


@dataclass
class TaskGraph:
    """任务图类.

    管理任务节点及其依赖关系，提供拓扑排序和节点状态管理功能。

    Attributes:
        _nodes: 节点字典，key为node_id，value为Node对象
        _edges: 邻接表表示的依赖关系，key为节点ID，value为其依赖的节点ID列表
    """

    _nodes: Dict[str, Node] = field(default_factory=dict)
    _edges: Dict[str, List[str]] = field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        """添加节点到任务图.

        Args:
            node: 要添加的节点对象

        Raises:
            ValueError: 如果节点ID已存在
        """
        if node.node_id in self._nodes:
            raise ValueError(f"节点ID已存在: {node.node_id}")
        self._nodes[node.node_id] = node
        # 初始化该节点的邻接表
        if node.node_id not in self._edges:
            self._edges[node.node_id] = []
        # 添加依赖边
        for dep_id in node.dependencies:
            self.add_edge(dep_id, node.node_id)

    def add_edge(self, from_id: str, to_id: str) -> None:
        """添加依赖边.

        表示from_id节点必须在to_id节点之前执行。

        Args:
            from_id: 前置节点ID
            to_id: 后置节点ID

        Raises:
            ValueError: 如果节点ID不存在或形成循环依赖
        """
        if from_id not in self._nodes:
            raise ValueError(f"前置节点不存在: {from_id}")
        if to_id not in self._nodes:
            raise ValueError(f"后置节点不存在: {to_id}")

        # 检查是否已存在该边
        if to_id not in self._edges:
            self._edges[to_id] = []
        if from_id not in self._edges[to_id]:
            self._edges[to_id].append(from_id)

    def topological_sort(self) -> List[str]:
        """拓扑排序返回节点ID列表.

        使用Kahn算法进行拓扑排序，确保依赖节点在前，被依赖节点在后。

        Returns:
            按执行顺序排列的节点ID列表

        Raises:
            ValueError: 如果图中存在循环依赖
        """
        # 计算每个节点的入度
        in_degree: Dict[str, int] = {node_id: 0 for node_id in self._nodes}
        for node_id, deps in self._edges.items():
            in_degree[node_id] = len(deps)

        # 找到所有入度为0的节点
        queue: deque[str] = deque(
            [node_id for node_id, degree in in_degree.items() if degree == 0]
        )
        result: List[str] = []

        while queue:
            current = queue.popleft()
            result.append(current)

            # 找到所有依赖当前节点的节点，减少其入度
            for node_id, deps in self._edges.items():
                if current in deps:
                    in_degree[node_id] -= 1
                    if in_degree[node_id] == 0:
                        queue.append(node_id)

        # 检查是否存在循环依赖
        if len(result) != len(self._nodes):
            raise ValueError("图中存在循环依赖，无法进行拓扑排序")

        return result

    def get_ready_nodes(self) -> List[str]:
        """返回所有依赖已满足的可执行节点ID.

        节点状态为PENDING且所有依赖节点状态为COMPLETED时，该节点为就绪状态。

        Returns:
            就绪节点ID列表
        """
        ready_nodes: List[str] = []

        for node_id, node in self._nodes.items():
            if node.status != NodeStatus.PENDING:
                continue

            # 检查所有依赖是否已完成
            deps_completed = all(
                self._nodes[dep_id].status == NodeStatus.COMPLETED
                for dep_id in node.dependencies
                if dep_id in self._nodes
            )

            if deps_completed:
                ready_nodes.append(node_id)

        return ready_nodes

    def get_node(self, node_id: str) -> Optional[Node]:
        """获取指定节点.

        Args:
            node_id: 节点ID

        Returns:
            节点对象，如果不存在则返回None
        """
        return self._nodes.get(node_id)

    def update_node_status(self, node_id: str, status: NodeStatus) -> None:
        """更新节点状态.

        Args:
            node_id: 节点ID
            status: 新状态

        Raises:
            ValueError: 如果节点不存在
        """
        if node_id not in self._nodes:
            raise ValueError(f"节点不存在: {node_id}")
        self._nodes[node_id].status = status

    def get_all_nodes(self) -> Dict[str, Node]:
        """获取所有节点.

        Returns:
            节点字典的副本
        """
        return self._nodes.copy()

    def get_dependencies(self, node_id: str) -> List[str]:
        """获取指定节点的依赖列表.

        Args:
            node_id: 节点ID

        Returns:
            依赖节点ID列表

        Raises:
            ValueError: 如果节点不存在
        """
        if node_id not in self._nodes:
            raise ValueError(f"节点不存在: {node_id}")
        return self._edges.get(node_id, []).copy()


# 向后兼容的别名
TaskNode = Node
