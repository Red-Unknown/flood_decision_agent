"""支持可视化的 Pipeline 模块.

扩展标准 Pipeline，集成可视化能力，展示 Agent 调用链和任务执行过程。
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from flood_decision_agent.agents.decision_chain_generator import (
    DecisionChainGeneratorAgent,
)
from flood_decision_agent.agents.node_scheduler import NodeSchedulerAgent
from flood_decision_agent.agents.summarizer import SummarizerAgent
from flood_decision_agent.agents.unit_task_executor import (
    UnitTaskExecutionAgent,
    build_default_handlers,
)
from flood_decision_agent.core.message import BaseMessage, MessageType
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import NodeStatus, TaskGraph
from flood_decision_agent.core.task_graph_builder import TaskGraphBuilder
from flood_decision_agent.data.mock_data import MockDataGenerator
from flood_decision_agent.fusion.decision_fusion import DecisionFusion
from flood_decision_agent.infra.kimi_guard import require_kimi_api_key
from flood_decision_agent.tools.execution_tools import register_execution_tools
from flood_decision_agent.tools.registry import ToolRegistry
from flood_decision_agent.visualization.base import BaseVisualizer
from flood_decision_agent.visualization.terminal import TerminalVisualizer


@dataclass(frozen=True)
class VisualizedPipelineResult:
    """可视化 Pipeline 执行结果.

    Attributes:
        data_pool_snapshot: 数据池快照
        execution_summary: 执行汇总信息
        success: 是否成功执行
    """

    data_pool_snapshot: Dict[str, Any]
    execution_summary: Dict[str, Any]
    success: bool


class VisualizedPipeline:
    """支持可视化的 Pipeline.

    在标准 Pipeline 基础上集成可视化能力，展示：
    - TaskGraph 生成后的任务列表
    - NodeSchedulerAgent 执行时的实时状态更新
    - Agent 调用链
    - 执行汇总统计

    Attributes:
        visualizer: 可视化器实例
        seed: 随机种子
        mock_generator: Mock 数据生成器
        fusion: 决策融合模块
        executor: 单元任务执行 Agent
        scheduler: 节点调度 Agent
        chain_generator: 决策链生成 Agent
    """

    def __init__(
        self,
        visualizer: Optional[BaseVisualizer] = None,
        seed: int = 42,
        enable_visualization: bool = True,
    ):
        """初始化可视化 Pipeline.

        Args:
            visualizer: 可视化器实例，为 None 时自动创建 TerminalVisualizer
            seed: 随机种子
            enable_visualization: 是否启用可视化
        """
        # 检查 API Key
        require_kimi_api_key()

        self.visualizer = visualizer or (
            TerminalVisualizer(enabled=enable_visualization)
            if enable_visualization
            else None
        )
        self.seed = seed

        # 初始化组件
        self.mock_generator = MockDataGenerator(seed=seed)
        self.fusion = DecisionFusion()
        
        # 创建工具注册表并注册执行工具
        self.tool_registry = ToolRegistry()
        register_execution_tools(self.tool_registry)
        
        self.executor = UnitTaskExecutionAgent(
            handlers=build_default_handlers(mock_generator=self.mock_generator),
            fusion=self.fusion,
            tool_registry=self.tool_registry,
        )

        # 创建带可视化的调度器
        self.scheduler = VisualizedNodeSchedulerAgent(
            executor=self.executor,
            visualizer=self.visualizer,
        )

        # 创建 TaskGraphBuilder 并传入相同的工具注册表
        task_graph_builder = TaskGraphBuilder(tool_registry=self.tool_registry)
        self.chain_generator = DecisionChainGeneratorAgent(
            task_graph_builder=task_graph_builder
        )

        # 创建总结智能体
        self.summarizer = SummarizerAgent(enable_streaming=True)

    def run(self, task_request: Dict[str, Any]) -> VisualizedPipelineResult:
        """执行可视化 Pipeline.

        Args:
            task_request: 任务请求字典

        Returns:
            可视化 Pipeline 执行结果
        """
        # 判断输入类型
        input_type = task_request.get("type", "unknown")
        
        # 如果是自然语言输入
        if input_type == "natural_language":
            user_input = task_request.get("input", "")
            input_type_for_chain = "natural_language"
        else:
            # 结构化输入
            user_input = str(task_request)
            input_type_for_chain = "structured"

        # 通知可视化器流程开始
        if self.visualizer:
            self.visualizer.on_pipeline_start(
                context={
                    "task_type": input_type,
                    "seed": self.seed,
                }
            )

        # 生成 TaskGraph
        graph, metadata = self.chain_generator.generate_chain(
            user_input=user_input,
            input_type=input_type_for_chain,
        )

        # 检查是否出错
        if "error" in metadata:
            error_message = metadata["error"]
            print(f"\n✗ 意图解析失败: {error_message}")
            
            # 通知可视化器流程完成（失败）
            if self.visualizer:
                self.visualizer.on_pipeline_completed(success=False)
            
            return VisualizedPipelineResult(
                data_pool_snapshot={"error": error_message},
                execution_summary={
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 1,
                    "total_duration_ms": 0,
                    "error": error_message,
                },
                success=False,
            )

        # 展示任务列表
        if self.visualizer:
            self.visualizer.on_task_graph_created(graph)
            # 记录 Agent 调用
            self.visualizer.on_agent_called(
                caller_agent="Pipeline",
                callee_agent="DecisionChainGeneratorAgent",
                input_summary=f"task_type={task_request.get('type', 'unknown')}",
            )

        # 创建数据池并执行
        data_pool = SharedDataPool()

        # 保存用户原始输入到数据池
        if input_type == "natural_language":
            data_pool.set("raw_user_input", user_input)
        else:
            data_pool.set("raw_user_input", str(task_request))
        data_pool.set("input_type", input_type)

        # 记录调度 Agent 调用
        if self.visualizer:
            self.visualizer.on_agent_called(
                caller_agent="Pipeline",
                callee_agent="NodeSchedulerAgent",
                input_summary=f"nodes={len(graph.get_all_nodes())}",
            )

        # 执行任务图
        result = self.scheduler.run(graph=graph, data_pool=data_pool)

        # 判断执行结果
        success = result.get("status") == "success"

        # 通知可视化器流程完成
        if self.visualizer:
            self.visualizer.on_pipeline_completed(success=success)

        # 获取执行汇总
        execution_summary = {}
        if self.visualizer:
            summary = self.visualizer.get_execution_summary()
            execution_summary = {
                "total_tasks": summary.total_tasks,
                "completed_tasks": summary.completed_tasks,
                "failed_tasks": summary.failed_tasks,
                "total_duration_ms": summary.total_duration_ms,
            }

        # 收集节点执行结果
        node_results = result.get("node_results", [])

        # 调用总结智能体生成执行总结
        if success and self.summarizer:
            summary_payload = {
                "task_request": task_request,
                "execution_summary": execution_summary,
                "data_pool_snapshot": data_pool.snapshot(),
                "task_graph": {
                    "node_count": len(graph.get_all_nodes()),
                    "edge_count": sum(len(deps) for deps in graph._edges.values()),
                },
                "node_results": node_results,
            }
            summary_message = BaseMessage(
                type=MessageType.TASK_REQUEST,
                payload=summary_payload,
                sender="Pipeline",
                receiver="Summarizer",
            )
            summary_result = self.summarizer.execute(summary_message)
            # 总结结果已通过流式输出打印到控制台

        return VisualizedPipelineResult(
            data_pool_snapshot=data_pool.snapshot(),
            execution_summary=execution_summary,
            success=success,
        )


class VisualizedNodeSchedulerAgent(NodeSchedulerAgent):
    """支持可视化的节点调度 Agent.

    继承自 NodeSchedulerAgent，在执行节点时触发可视化事件。
    """

    def __init__(
        self,
        executor: Optional[UnitTaskExecutionAgent] = None,
        agent_id: str = "NodeScheduler",
        visualizer: Optional[BaseVisualizer] = None,
        **kwargs,
    ):
        """初始化可视化节点调度 Agent.

        Args:
            executor: 单元任务执行 Agent
            agent_id: Agent ID
            visualizer: 可视化器实例
            **kwargs: 传递给父类的其他参数
        """
        super().__init__(executor=executor, agent_id=agent_id, **kwargs)
        self.visualizer = visualizer

    def execute_node(self, node, data_pool) -> Dict[str, Any]:
        """执行单个节点（带可视化）.

        Args:
            node: 节点对象
            data_pool: 共享数据池

        Returns:
            执行结果
        """
        node_id = node.node_id

        # 通知可视化器节点开始
        if self.visualizer:
            self.visualizer.on_node_started(
                node_id=node_id,
                agent_id="UnitTaskExecutionAgent",
            )

        # 记录 Agent 调用
        if self.visualizer:
            self.visualizer.on_agent_called(
                caller_agent="NodeSchedulerAgent",
                callee_agent="UnitTaskExecutionAgent",
                input_summary=f"task_type={node.task_type}",
            )

        # 记录开始时间
        start_time = time.time()

        # 调用父类方法执行节点
        result = super().execute_node(node, data_pool)

        # 计算耗时
        duration_ms = (time.time() - start_time) * 1000

        # 通知可视化器节点完成或失败
        if self.visualizer:
            if result.get("status") == "success":
                self.visualizer.on_node_completed(
                    node_id=node_id,
                    agent_id="UnitTaskExecutionAgent",
                    duration_ms=duration_ms,
                    output_summary=self._summarize_output(result.get("output", {})),
                )
            else:
                self.visualizer.on_node_failed(
                    node_id=node_id,
                    agent_id="UnitTaskExecutionAgent",
                    error_message=result.get("error", "未知错误"),
                    retry_count=result.get("metrics", {}).get("retry_count", 0),
                )

        return result

    def _summarize_output(self, output: Dict[str, Any]) -> str:
        """生成输出摘要.

        Args:
            output: 输出数据

        Returns:
            输出摘要字符串
        """
        if not output:
            return "无输出"

        keys = list(output.keys())
        if len(keys) <= 3:
            return f"keys={keys}"
        else:
            return f"keys={keys[:3]}...({len(keys)} total)"


def run_visualized_pipeline(
    task_request: Dict[str, Any],
    seed: int = 42,
    enable_visualization: bool = True,
    visualizer: Optional[BaseVisualizer] = None,
) -> VisualizedPipelineResult:
    """便捷函数：执行可视化 Pipeline.

    Args:
        task_request: 任务请求字典
        seed: 随机种子
        enable_visualization: 是否启用可视化
        visualizer: 自定义可视化器

    Returns:
        可视化 Pipeline 执行结果

    Example:
        >>> result = run_visualized_pipeline(
        ...     task_request={"type": "flood_warning", "params": {"station": "test"}},
        ...     enable_visualization=True,
        ... )
    """
    pipeline = VisualizedPipeline(
        visualizer=visualizer,
        seed=seed,
        enable_visualization=enable_visualization,
    )
    return pipeline.run(task_request)


if __name__ == "__main__":
    # 示例运行
    result = run_visualized_pipeline(
        task_request={
            "type": "flood_warning",
            "params": {"station": "test_station", "date": "2024-01-01"},
        },
        enable_visualization=True,
    )

    print(f"\n执行结果: {'成功' if result.success else '失败'}")
    print(f"执行汇总: {result.execution_summary}")
