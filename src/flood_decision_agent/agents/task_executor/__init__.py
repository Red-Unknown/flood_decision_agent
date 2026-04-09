"""任务执行模块.

提供单元任务执行功能，支持动态工具选择和自主选用。
"""

from flood_decision_agent.agents.task_executor.executor import (
    UnitTaskExecutionAgent,
    build_default_handlers,
)
from flood_decision_agent.agents.task_executor.streaming_executor import (
    StreamingTaskExecutor,
    ExecutionEvent,
    ExecutionResult,
    TaskDetail,
    TaskStatus,
)

__all__ = [
    # 基础执行器
    "UnitTaskExecutionAgent",
    "build_default_handlers",
    # 流式执行器
    "StreamingTaskExecutor",
    "ExecutionEvent",
    "ExecutionResult",
    "TaskDetail",
    "TaskStatus",
]
