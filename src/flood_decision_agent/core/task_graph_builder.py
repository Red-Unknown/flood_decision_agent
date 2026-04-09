"""任务图构建器"""
from dataclasses import dataclass
from typing import Any, Dict, List

from flood_decision_agent.core.task_graph import Node, TaskGraph


@dataclass
class TaskChainItem:
    """任务链项"""
    task_id: str
    task_type: str
    description: str
    inputs: List[str]
    outputs: List[str]
    dependencies: List[str]
    metadata: Dict[str, Any] = None


class TaskGraphBuilder:
    """任务图构建器"""
    
    def __init__(self, tool_registry=None):
        """初始化任务图构建器.
        
        Args:
            tool_registry: 工具注册表（可选）
        """
        self.tool_registry = tool_registry
    
    def build_from_chain(self, chain_items: List[TaskChainItem]) -> TaskGraph:
        """从任务链构建任务图"""
        task_graph = TaskGraph()
        
        for item in chain_items:
            node = Node(
                node_id=item.task_id,
                task_type=item.task_type,
                metadata=item.metadata if item.metadata else {},
            )
            task_graph.add_node(node)
        
        # 添加依赖边
        for item in chain_items:
            for dep_id in item.dependencies:
                task_graph.add_edge(dep_id, item.task_id)
        
        return task_graph
