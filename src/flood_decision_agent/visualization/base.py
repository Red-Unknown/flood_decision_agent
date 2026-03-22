"""可视化基类模块.

定义可视化器的抽象基类，为终端、Web、桌面应用等提供统一接口。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from flood_decision_agent.core.task_graph import TaskGraph
from flood_decision_agent.visualization.models import (
    AgentCallInfo,
    DataFlowInfo,
    EventType,
    ExecutionEvent,
    ExecutionSummary,
    TaskInfo,
    TaskStatus,
)


class VisualizationEvent:
    """可视化事件包装类.

    用于在可视化器和业务逻辑之间传递事件。
    """

    def __init__(self, event_type: EventType, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = __import__("datetime").datetime.now()


class BaseVisualizer(ABC):
    """可视化器抽象基类.

    提供统一的 Agent 调用链、数据流和决策过程可视化接口。
    支持终端、Web、桌面应用等多种渲染后端。

    Attributes:
        enabled: 是否启用可视化
        event_handlers: 事件处理器字典
        execution_summary: 执行汇总信息
    """

    def __init__(self, enabled: bool = True):
        """初始化可视化器.

        Args:
            enabled: 是否启用可视化，默认为 True
        """
        self.enabled = enabled
        self.event_handlers: Dict[EventType, List[Callable[[ExecutionEvent], None]]] = {}
        self.execution_summary = ExecutionSummary()
        self._task_info_map: Dict[str, TaskInfo] = {}
        self._is_running = False

    def register_event_handler(
        self, event_type: EventType, handler: Callable[[ExecutionEvent], None]
    ) -> None:
        """注册事件处理器.

        Args:
            event_type: 事件类型
            handler: 事件处理函数
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def unregister_event_handler(
        self, event_type: EventType, handler: Callable[[ExecutionEvent], None]
    ) -> None:
        """注销事件处理器.

        Args:
            event_type: 事件类型
            handler: 要注销的处理函数
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type] = [
                h for h in self.event_handlers[event_type] if h != handler
            ]

    def emit_event(self, event: ExecutionEvent) -> None:
        """发射事件到所有注册的处理器.

        Args:
            event: 执行事件
        """
        if not self.enabled:
            return

        # 更新执行汇总
        self._update_summary(event)

        # 调用特定类型的事件处理器
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                handler(event)

        # 调用通用事件处理器（所有事件类型）
        if None in self.event_handlers:
            for handler in self.event_handlers[None]:
                handler(event)

        # 调用渲染方法
        self._render_event(event)

    def _update_summary(self, event: ExecutionEvent) -> None:
        """更新执行汇总信息.

        Args:
            event: 执行事件
        """
        if event.task_info:
            task_info = event.task_info
            self._task_info_map[task_info.node_id] = task_info

            # 更新计数
            self.execution_summary.total_tasks = len(self._task_info_map)
            self.execution_summary.completed_tasks = sum(
                1 for t in self._task_info_map.values() if t.status == TaskStatus.COMPLETED
            )
            self.execution_summary.failed_tasks = sum(
                1 for t in self._task_info_map.values() if t.status == TaskStatus.FAILED
            )

        if event.agent_call:
            self.execution_summary.agent_calls.append(event.agent_call)

        if event.data_flow:
            self.execution_summary.data_flows.append(event.data_flow)

    @abstractmethod
    def _render_event(self, event: ExecutionEvent) -> None:
        """渲染事件（子类实现）.

        Args:
            event: 执行事件
        """
        pass

    def on_pipeline_start(self, context: Optional[Dict[str, Any]] = None) -> None:
        """流程开始时的回调.

        Args:
            context: 上下文信息
        """
        if not self.enabled:
            return

        self._is_running = True
        self.execution_summary = ExecutionSummary()
        self._task_info_map.clear()

        event = ExecutionEvent(
            event_type=EventType.PIPELINE_STARTED,
            metadata=context or {},
        )
        self.emit_event(event)
        self._render_pipeline_start(context)

    @abstractmethod
    def _render_pipeline_start(self, context: Optional[Dict[str, Any]]) -> None:
        """渲染流程开始（子类实现）.

        Args:
            context: 上下文信息
        """
        pass

    def on_task_graph_created(self, task_graph: TaskGraph) -> None:
        """TaskGraph 创建完成时的回调.

        提取 TaskGraph 中的任务信息并展示任务列表。

        Args:
            task_graph: 任务图对象
        """
        if not self.enabled:
            return

        # 从 TaskGraph 提取任务信息
        task_infos = self._extract_task_infos(task_graph)

        # 创建事件
        event = ExecutionEvent(
            event_type=EventType.TASK_GRAPH_CREATED,
            metadata={"task_graph": task_graph, "task_count": len(task_infos)},
        )
        self.emit_event(event)

        # 展示任务列表
        self._render_task_list(task_infos)

        # 发送任务列表展示事件
        list_event = ExecutionEvent(
            event_type=EventType.TASK_LIST_DISPLAYED,
            metadata={"task_infos": task_infos},
        )
        self.emit_event(list_event)

    def _extract_task_infos(self, task_graph: TaskGraph) -> List[TaskInfo]:
        """从 TaskGraph 提取任务信息列表.

        Args:
            task_graph: 任务图对象

        Returns:
            任务信息列表
        """
        task_infos = []
        nodes = task_graph.get_all_nodes()

        for node_id, node in nodes.items():
            # 处理 task_type，可能是枚举或字符串
            task_type_value = node.task_type
            if hasattr(task_type_value, 'value'):
                task_type_value = task_type_value.value

            # 生成可读的任务名称
            task_name = self._generate_task_name(node_id, task_type_value)

            # 映射状态
            status_map = {
                "pending": TaskStatus.PENDING,
                "ready": TaskStatus.READY,
                "running": TaskStatus.RUNNING,
                "completed": TaskStatus.COMPLETED,
                "failed": TaskStatus.FAILED,
            }
            status = status_map.get(node.status.value, TaskStatus.PENDING)

            task_info = TaskInfo(
                node_id=node_id,
                task_name=task_name,
                task_type=task_type_value,
                status=status,
                dependencies=node.dependencies.copy(),
            )
            task_infos.append(task_info)
            self._task_info_map[node_id] = task_info

        return task_infos

    def _generate_task_name(self, node_id: str, task_type: str) -> str:
        """生成可读的任务名称.

        Args:
            node_id: 节点ID
            task_type: 任务类型

        Returns:
            可读的任务名称
        """
        # 导入新的类型系统
        from flood_decision_agent.core.task_types import (
            BusinessTaskType,
            ExecutionTaskType,
            get_business_type_description,
            get_execution_type_description,
        )

        # 尝试解析为业务类型或执行类型
        description = task_type
        try:
            # 尝试作为业务类型
            business_type = BusinessTaskType(task_type)
            description = get_business_type_description(business_type)
        except ValueError:
            try:
                # 尝试作为执行类型
                exec_type = ExecutionTaskType(task_type)
                description = get_execution_type_description(exec_type)
            except ValueError:
                # 使用原始值
                description = task_type

        return f"{description} ({node_id})"

    @abstractmethod
    def _render_task_list(self, task_infos: List[TaskInfo]) -> None:
        """渲染任务列表（子类实现）.

        Args:
            task_infos: 任务信息列表
        """
        pass

    def on_node_started(self, node_id: str, agent_id: str) -> None:
        """节点开始执行时的回调.

        Args:
            node_id: 节点ID
            agent_id: 执行 Agent ID
        """
        if not self.enabled:
            return

        task_info = self._task_info_map.get(node_id)
        if task_info:
            task_info.status = TaskStatus.RUNNING
            task_info.start_time = __import__("datetime").datetime.now()

        event = ExecutionEvent(
            event_type=EventType.NODE_STARTED,
            task_info=task_info,
            metadata={"agent_id": agent_id},
        )
        self.emit_event(event)
        self._render_node_started(node_id, agent_id, task_info)

    @abstractmethod
    def _render_node_started(self, node_id: str, agent_id: str, task_info: Optional[TaskInfo]) -> None:
        """渲染节点开始（子类实现）.

        Args:
            node_id: 节点ID
            agent_id: 执行 Agent ID
            task_info: 任务信息
        """
        pass

    def on_node_completed(
        self, node_id: str, agent_id: str, duration_ms: float, output_summary: Optional[str] = None
    ) -> None:
        """节点执行完成时的回调.

        Args:
            node_id: 节点ID
            agent_id: 执行 Agent ID
            duration_ms: 执行耗时（毫秒）
            output_summary: 输出摘要
        """
        if not self.enabled:
            return

        task_info = self._task_info_map.get(node_id)
        if task_info:
            task_info.status = TaskStatus.COMPLETED
            task_info.end_time = __import__("datetime").datetime.now()
            task_info.duration_ms = duration_ms

        event = ExecutionEvent(
            event_type=EventType.NODE_COMPLETED,
            task_info=task_info,
            metadata={"agent_id": agent_id, "duration_ms": duration_ms, "output_summary": output_summary},
        )
        self.emit_event(event)
        self._render_node_completed(node_id, agent_id, duration_ms, task_info)

    @abstractmethod
    def _render_node_completed(
        self, node_id: str, agent_id: str, duration_ms: float, task_info: Optional[TaskInfo]
    ) -> None:
        """渲染节点完成（子类实现）.

        Args:
            node_id: 节点ID
            agent_id: 执行 Agent ID
            duration_ms: 执行耗时（毫秒）
            task_info: 任务信息
        """
        pass

    def on_node_failed(
        self, node_id: str, agent_id: str, error_message: str, retry_count: int = 0
    ) -> None:
        """节点执行失败时的回调.

        Args:
            node_id: 节点ID
            agent_id: 执行 Agent ID
            error_message: 错误信息
            retry_count: 重试次数
        """
        if not self.enabled:
            return

        task_info = self._task_info_map.get(node_id)
        if task_info:
            task_info.status = TaskStatus.FAILED
            task_info.error_message = error_message
            task_info.retry_count = retry_count

        event = ExecutionEvent(
            event_type=EventType.NODE_FAILED,
            task_info=task_info,
            metadata={"agent_id": agent_id, "error_message": error_message, "retry_count": retry_count},
        )
        self.emit_event(event)
        self._render_node_failed(node_id, agent_id, error_message, task_info)

    @abstractmethod
    def _render_node_failed(
        self, node_id: str, agent_id: str, error_message: str, task_info: Optional[TaskInfo]
    ) -> None:
        """渲染节点失败（子类实现）.

        Args:
            node_id: 节点ID
            agent_id: 执行 Agent ID
            error_message: 错误信息
            task_info: 任务信息
        """
        pass

    def on_agent_called(
        self, caller_agent: str, callee_agent: str, input_summary: Optional[str] = None
    ) -> None:
        """Agent 被调用时的回调.

        Args:
            caller_agent: 调用方 Agent ID
            callee_agent: 被调用方 Agent ID
            input_summary: 输入摘要
        """
        if not self.enabled:
            return

        agent_call = AgentCallInfo(
            caller_agent=caller_agent,
            callee_agent=callee_agent,
            input_summary=input_summary,
        )

        event = ExecutionEvent(
            event_type=EventType.AGENT_CALLED,
            agent_call=agent_call,
        )
        self.emit_event(event)
        self._render_agent_call(agent_call)

    @abstractmethod
    def _render_agent_call(self, agent_call: AgentCallInfo) -> None:
        """渲染 Agent 调用（子类实现）.

        Args:
            agent_call: Agent 调用信息
        """
        pass

    def on_data_flow(
        self, source_node: str, target_node: str, data_keys: List[str]
    ) -> None:
        """数据流动时的回调.

        Args:
            source_node: 数据源节点ID
            target_node: 数据目标节点ID
            data_keys: 传输的数据键列表
        """
        if not self.enabled:
            return

        data_flow = DataFlowInfo(
            source_node=source_node,
            target_node=target_node,
            data_keys=data_keys,
        )

        event = ExecutionEvent(
            event_type=EventType.DATA_FLOW,
            data_flow=data_flow,
        )
        self.emit_event(event)
        self._render_data_flow(data_flow)

    @abstractmethod
    def _render_data_flow(self, data_flow: DataFlowInfo) -> None:
        """渲染数据流（子类实现）.

        Args:
            data_flow: 数据流信息
        """
        pass

    def on_pipeline_completed(self, success: bool = True) -> None:
        """流程完成时的回调.

        Args:
            success: 是否成功完成
        """
        if not self.enabled:
            return

        self._is_running = False

        # 计算总耗时
        total_duration = 0.0
        for task_info in self._task_info_map.values():
            if task_info.duration_ms:
                total_duration += task_info.duration_ms
        self.execution_summary.total_duration_ms = total_duration

        event = ExecutionEvent(
            event_type=EventType.PIPELINE_COMPLETED,
            metadata={"success": success, "summary": self.execution_summary},
        )
        self.emit_event(event)
        self._render_pipeline_completed(success, self.execution_summary)

    @abstractmethod
    def _render_pipeline_completed(self, success: bool, summary: ExecutionSummary) -> None:
        """渲染流程完成（子类实现）.

        Args:
            success: 是否成功完成
            summary: 执行汇总
        """
        pass

    def get_execution_summary(self) -> ExecutionSummary:
        """获取执行汇总信息.

        Returns:
            执行汇总
        """
        # 更新任务信息列表
        self.execution_summary.task_infos = list(self._task_info_map.values())
        return self.execution_summary
