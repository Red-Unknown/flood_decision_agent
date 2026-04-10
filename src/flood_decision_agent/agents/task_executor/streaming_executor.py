"""
流式任务执行器 - 支持生成器模式的流式执行

提供 StreamingTaskExecutor 类，支持 async generator 模式，
在任务执行过程中 yield 中间状态（task_update），供 WebSocket 实时推送。
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

from flood_decision_agent.agents.task_executor.executor import UnitTaskExecutionAgent
from flood_decision_agent.core.shared_data_pool import SharedDataPool
from flood_decision_agent.core.task_graph import TaskGraph
from flood_decision_agent.infrastructure.logging import get_logger


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskDetail:
    """任务执行详情"""
    stage: str = ""
    message: str = ""
    progress: float = 0.0
    modalities: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionEvent:
    """执行事件"""
    event_type: str  # task_update, execution_progress, execution_complete, execution_error
    task_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    detail: Optional[TaskDetail] = None
    progress: Optional[float] = None  # 总体进度 0.0 - 1.0
    completed_count: Optional[int] = None
    total_count: Optional[int] = None
    success: Optional[bool] = None  # 执行是否成功（用于execution_complete事件）


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    results: Dict[str, Any] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class StreamingTaskExecutor:
    """流式任务执行器
    
    使用生成器模式，在任务执行过程中 yield 中间状态事件，
    使 WebSocket 能够实时推送执行进度。
    
    特性：
    1. 支持任务级流式更新（task_update）
    2. 支持总体进度更新（execution_progress）
    3. 支持 detail 字段的流式更新（预留多模态）
    4. 支持取消操作
    
    Example:
        ```python
        executor = StreamingTaskExecutor()
        task_graph = ...  # 生成的任务图
        
        async for event in executor.execute(task_graph):
            if event.event_type == "task_update":
                print(f"任务 {event.task_id}: {event.status}")
                if event.detail:
                    print(f"  详情: {event.detail.message}")
            elif event.event_type == "execution_progress":
                print(f"总体进度: {event.progress * 100}%")
                
        # 获取最终结果
        result = executor.get_last_result()
        ```
    """

    def __init__(
        self,
        task_executor: Optional[UnitTaskExecutionAgent] = None,
    ):
        """初始化流式执行器
        
        Args:
            task_executor: 任务执行器实例
        """
        self._logger = get_logger().bind(name=self.__class__.__name__)
        self._task_executor = task_executor or UnitTaskExecutionAgent()
        self._last_result: Optional[ExecutionResult] = None
        self._cancelled: bool = False
        self._data_pool: SharedDataPool = SharedDataPool()

    async def execute(
        self,
        task_graph: TaskGraph,
        initial_data: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[ExecutionEvent, None]:
        """流式执行任务图
        
        Args:
            task_graph: 任务图
            initial_data: 初始数据
            
        Yields:
            ExecutionEvent: 执行事件
        """
        try:
            self._cancelled = False
            self._data_pool = SharedDataPool()
            
            # 加载初始数据
            if initial_data:
                for key, value in initial_data.items():
                    self._data_pool.set(key, value)
            
            # 获取所有任务节点
            nodes = task_graph.get_all_nodes()
            total_tasks = len(nodes)
            completed_tasks = 0
            failed_tasks = 0
            
            self._logger.info(f"开始执行任务图，共 {total_tasks} 个任务")
            
            # 发送执行开始事件
            yield ExecutionEvent(
                event_type="execution_started",
                total_count=total_tasks,
            )
            
            # 按依赖顺序执行任务
            executed_tasks: set = set()
            task_results: Dict[str, Any] = {}
            
            while len(executed_tasks) < total_tasks:
                # 检查是否被取消
                if self._cancelled:
                    yield ExecutionEvent(
                        event_type="execution_error",
                        error="执行已取消",
                    )
                    self._last_result = ExecutionResult(
                        success=False,
                        error_message="执行已取消",
                    )
                    return
                
                # 找到可以执行的任务（依赖已满足）
                ready_tasks = self._get_ready_tasks(nodes, executed_tasks)
                
                if not ready_tasks:
                    # 没有可执行的任务，但还有未完成的任务，说明有循环依赖
                    if len(executed_tasks) < total_tasks:
                        error_msg = "检测到循环依赖或无法执行的任务"
                        yield ExecutionEvent(
                            event_type="execution_error",
                            error=error_msg,
                        )
                        self._last_result = ExecutionResult(
                            success=False,
                            error_message=error_msg,
                        )
                        return
                    break
                
                # 执行就绪的任务
                for node_id, node in ready_tasks:
                    # 检查是否被取消
                    if self._cancelled:
                        yield ExecutionEvent(
                            event_type="execution_error",
                            error="执行已取消",
                        )
                        self._last_result = ExecutionResult(
                            success=False,
                            error_message="执行已取消",
                        )
                        return
                    
                    # 发送任务开始事件
                    task_type = getattr(node, 'task_type', 'unknown')
                    if hasattr(task_type, 'value'):
                        task_type = task_type.value
                    
                    yield ExecutionEvent(
                        event_type="task_update",
                        task_id=node_id,
                        status=TaskStatus.RUNNING,
                        detail=TaskDetail(
                            stage="executing",
                            message=f"开始执行任务 {node_id}...",
                            progress=0.0,
                        ),
                    )
                    
                    try:
                        # 执行任务
                        result = await self._execute_task(node_id, node, task_type)
                        
                        if result.get("status") == "success":
                            # 任务成功
                            task_results[node_id] = result.get("output", {})
                            completed_tasks += 1
                            
                            # 将结果存入数据池
                            output = result.get("output", {})
                            for key, value in output.items():
                                self._data_pool.set(f"{node_id}_{key}", value)
                            
                            # 发送任务完成事件
                            yield ExecutionEvent(
                                event_type="task_update",
                                task_id=node_id,
                                status=TaskStatus.COMPLETED,
                                result=result,
                                detail=TaskDetail(
                                    stage="completed",
                                    message=f"任务 {node_id} 执行完成",
                                    progress=1.0,
                                ),
                            )
                        else:
                            # 任务失败
                            failed_tasks += 1
                            error_msg = result.get("error", "未知错误")
                            
                            yield ExecutionEvent(
                                event_type="task_update",
                                task_id=node_id,
                                status=TaskStatus.FAILED,
                                error=error_msg,
                                detail=TaskDetail(
                                    stage="failed",
                                    message=f"任务 {node_id} 执行失败: {error_msg}",
                                    progress=0.0,
                                ),
                            )
                    
                    except Exception as e:
                        failed_tasks += 1
                        error_msg = str(e)
                        self._logger.error(f"任务 {node_id} 执行异常: {error_msg}")
                        
                        yield ExecutionEvent(
                            event_type="task_update",
                            task_id=node_id,
                            status=TaskStatus.FAILED,
                            error=error_msg,
                            detail=TaskDetail(
                                stage="failed",
                                message=f"任务 {node_id} 执行异常: {error_msg}",
                                progress=0.0,
                            ),
                        )
                    
                    # 标记任务为已执行
                    executed_tasks.add(node_id)
                    
                    # 发送总体进度更新
                    progress = len(executed_tasks) / total_tasks if total_tasks > 0 else 0
                    yield ExecutionEvent(
                        event_type="execution_progress",
                        progress=progress,
                        completed_count=len(executed_tasks),
                        total_count=total_tasks,
                    )
            
            # 执行完成
            success = failed_tasks == 0
            
            yield ExecutionEvent(
                event_type="execution_complete",
                success=success,
            )
            
            self._last_result = ExecutionResult(
                success=success,
                results=task_results,
                summary={
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "failed_tasks": failed_tasks,
                },
            )
            
        except Exception as e:
            error_msg = str(e)
            self._logger.error(f"执行器异常: {error_msg}")
            
            yield ExecutionEvent(
                event_type="execution_error",
                error=error_msg,
            )
            
            self._last_result = ExecutionResult(
                success=False,
                error_message=error_msg,
            )

    async def _execute_task(
        self,
        node_id: str,
        node: Any,
        task_type: str,
    ) -> Dict[str, Any]:
        """执行单个任务
        
        Args:
            node_id: 节点ID
            node: 节点对象
            task_type: 任务类型
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        # 获取节点的工具规格
        tools_spec = []
        if hasattr(node, 'metadata') and node.metadata:
            mcp_tools = node.metadata.get('mcp_tools', [])
            for tool in mcp_tools:
                tools_spec.append({
                    'tool_name': tool.get('tool_name'),
                    'tool_config': {},
                    'server_name': tool.get('server_name'),
                    'is_mcp_tool': tool.get('is_mcp_tool', False),
                    'priority': tool.get('priority', 80),
                })
        
        # 在后台线程中执行任务，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._task_executor.execute_task,
            node_id,
            task_type,
            self._data_pool,
            tools_spec,
            "auto",
            {
                'description': getattr(node, 'description', ''),
                'node_id': node_id,
            },
        )
        
        return result

    def _get_ready_tasks(
        self,
        nodes: Dict[str, Any],
        executed_tasks: set,
    ) -> List[tuple]:
        """获取可以执行的任务（依赖已满足）
        
        Args:
            nodes: 所有节点
            executed_tasks: 已执行的任务集合
            
        Returns:
            List[tuple]: (node_id, node) 列表
        """
        ready = []
        
        for node_id, node in nodes.items():
            if node_id in executed_tasks:
                continue
            
            # 获取依赖
            dependencies = set()
            if hasattr(node, 'dependencies'):
                deps = node.dependencies
                if isinstance(deps, (list, tuple)):
                    dependencies = set(deps)
                elif isinstance(deps, str):
                    dependencies = {deps}
            elif hasattr(node, 'metadata') and node.metadata:
                deps = node.metadata.get('dependencies', [])
                if isinstance(deps, (list, tuple)):
                    dependencies = set(deps)
            
            # 检查依赖是否都已执行
            if dependencies.issubset(executed_tasks):
                ready.append((node_id, node))
        
        return ready

    def cancel(self) -> None:
        """取消执行"""
        self._logger.info("收到取消请求")
        self._cancelled = True

    def get_last_result(self) -> Optional[ExecutionResult]:
        """获取最后一次执行结果
        
        Returns:
            ExecutionResult: 执行结果，如果尚未完成则返回 None
        """
        return self._last_result

    def reset(self) -> None:
        """重置执行器状态"""
        self._last_result = None
        self._cancelled = False
        self._data_pool = SharedDataPool()
