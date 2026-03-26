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


class TaskGraphBuilder:
    """任务图构建器"""
    
    def build_from_chain(self, chain_items: List[TaskChainItem]) -> TaskGraph:
        """从任务链构建任务图"""
        task_graph = TaskGraph()
        
        for item in chain_items:
            node = Node(
                node_id=item.task_id,
                node_type=item.task_type,
                description=item.description,
            )
            task_graph.add_node(node)
        
        # 添加依赖边
        for item in chain_items:
            for dep_id in item.dependencies:
                task_graph.add_edge(dep_id, item.task_id)
        
        return task_graph
