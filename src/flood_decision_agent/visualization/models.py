"""可视化数据模型.

定义可视化所需的数据结构和枚举类型。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """任务执行状态枚举."""

    PENDING = "pending"  # 等待中
    READY = "ready"  # 准备就绪
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 执行失败


class EventType(Enum):
    """可视化事件类型枚举."""

    TASK_GRAPH_CREATED = "task_graph_created"  # TaskGraph 创建完成
    TASK_LIST_DISPLAYED = "task_list_displayed"  # 任务列表展示
    NODE_STARTED = "node_started"  # 节点开始执行
    NODE_COMPLETED = "node_completed"  # 节点执行完成
    NODE_FAILED = "node_failed"  # 节点执行失败
    AGENT_CALLED = "agent_called"  # Agent 被调用
    DATA_FLOW = "data_flow"  # 数据流动
    PIPELINE_STARTED = "pipeline_started"  # 流程开始
    PIPELINE_COMPLETED = "pipeline_completed"  # 流程完成


@dataclass
class TaskInfo:
    """任务信息数据类.

    Attributes:
        node_id: 节点唯一标识
        task_name: 任务名称（可读）
        task_type: 任务类型
        status: 当前状态
        dependencies: 依赖任务ID列表
        start_time: 开始时间
        end_time: 结束时间
        duration_ms: 执行耗时（毫秒）
        retry_count: 重试次数
        error_message: 错误信息（如果失败）
    """

    node_id: str
    task_name: str
    task_type: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None


@dataclass
class AgentCallInfo:
    """Agent 调用信息数据类.

    Attributes:
        caller_agent: 调用方 Agent ID
        callee_agent: 被调用方 Agent ID
        call_time: 调用时间
        duration_ms: 调用耗时（毫秒）
        input_summary: 输入摘要
        output_summary: 输出摘要
    """

    caller_agent: str
    callee_agent: str
    call_time: datetime = field(default_factory=datetime.now)
    duration_ms: Optional[float] = None
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None


@dataclass
class DataFlowInfo:
    """数据流信息数据类.

    Attributes:
        source_node: 数据源节点ID
        target_node: 数据目标节点ID
        data_keys: 传输的数据键列表
        flow_time: 流动时间
    """

    source_node: str
    target_node: str
    data_keys: List[str] = field(default_factory=list)
    flow_time: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionEvent:
    """执行事件数据类.

    Attributes:
        event_type: 事件类型
        timestamp: 事件发生时间
        task_info: 相关任务信息（可选）
        agent_call: Agent 调用信息（可选）
        data_flow: 数据流信息（可选）
        metadata: 额外元数据
    """

    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    task_info: Optional[TaskInfo] = None
    agent_call: Optional[AgentCallInfo] = None
    data_flow: Optional[DataFlowInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionSummary:
    """执行汇总数据类.

    Attributes:
        total_tasks: 总任务数
        completed_tasks: 已完成任务数
        failed_tasks: 失败任务数
        total_duration_ms: 总耗时（毫秒）
        task_infos: 所有任务信息列表
        agent_calls: Agent 调用链列表
        data_flows: 数据流列表
    """

    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_duration_ms: float = 0.0
    task_infos: List[TaskInfo] = field(default_factory=list)
    agent_calls: List[AgentCallInfo] = field(default_factory=list)
    data_flows: List[DataFlowInfo] = field(default_factory=list)
