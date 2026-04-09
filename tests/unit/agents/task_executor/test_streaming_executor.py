"""
StreamingTaskExecutor 单元测试

测试流式任务执行器的各种功能。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock

from flood_decision_agent.agents.task_executor.streaming_executor import (
    StreamingTaskExecutor,
    ExecutionEvent,
    ExecutionResult,
    TaskDetail,
    TaskStatus,
)
from flood_decision_agent.core.task_graph import TaskGraph


class TestStreamingTaskExecutor:
    """测试 StreamingTaskExecutor 类"""

    @pytest.fixture
    def executor(self):
        """创建 StreamingTaskExecutor 实例"""
        return StreamingTaskExecutor()

    @pytest.fixture
    def mock_task_graph(self):
        """创建模拟任务图"""
        graph = Mock(spec=TaskGraph)
        
        # 模拟节点
        node1 = Mock()
        node1.task_type = Mock()
        node1.task_type.value = "data_collection"
        node1.description = "任务1"
        node1.dependencies = []
        node1.metadata = {}
        
        node2 = Mock()
        node2.task_type = Mock()
        node2.task_type.value = "data_processing"
        node2.description = "任务2"
        node2.dependencies = ["task_001"]
        node2.metadata = {}
        
        graph.get_all_nodes.return_value = {
            "task_001": node1,
            "task_002": node2,
        }
        graph._edges = {
            "task_001": [],
            "task_002": ["task_001"],
        }
        
        return graph

    @pytest.mark.asyncio
    async def test_execute_empty_graph(self, executor):
        """测试执行空任务图"""
        empty_graph = Mock(spec=TaskGraph)
        empty_graph.get_all_nodes.return_value = {}
        
        events = []
        async for event in executor.execute(empty_graph):
            events.append(event)
        
        # 空图应该直接完成或返回错误
        # 根据实现可能返回 execution_complete 或 execution_error
        assert len(events) > 0
        
        result = executor.get_last_result()
        assert result is not None

    @pytest.mark.asyncio
    async def test_execute_with_tasks(self, executor, mock_task_graph):
        """测试执行任务图"""
        with patch.object(executor._task_executor, 'execute_task', return_value={
            "status": "success",
            "output": {"result": "test"},
        }):
            events = []
            async for event in executor.execute(mock_task_graph):
                events.append(event)
                assert isinstance(event, ExecutionEvent)
            
            # 验证事件类型（根据实际实现调整）
            event_types = [e.event_type for e in events]
            assert "execution_started" in event_types
            assert "task_update" in event_types
            
            # 验证任务更新事件
            task_updates = [e for e in events if e.event_type == "task_update"]
            assert len(task_updates) > 0
            
            # 验证结果
            result = executor.get_last_result()
            assert result is not None

    @pytest.mark.asyncio
    async def test_execute_task_failure(self, executor, mock_task_graph):
        """测试任务失败处理"""
        def side_effect(*args, **kwargs):
            node_id = kwargs.get('node_id', args[0] if args else '')
            if node_id == "task_002":
                return {"status": "failed", "error": "任务执行失败"}
            return {"status": "success", "output": {}}
        
        with patch.object(executor._task_executor, 'execute_task', side_effect=side_effect):
            events = []
            async for event in executor.execute(mock_task_graph):
                events.append(event)
            
            # 验证失败任务的事件
            failed_updates = [e for e in events 
                            if e.event_type == "task_update" 
                            and e.status == TaskStatus.FAILED]
            assert len(failed_updates) > 0
            
            # 验证结果
            result = executor.get_last_result()
            assert not result.success

    @pytest.mark.asyncio
    async def test_execute_exception_handling(self, executor, mock_task_graph):
        """测试异常处理"""
        with patch.object(executor._task_executor, 'execute_task', side_effect=Exception("测试异常")):
            events = []
            async for event in executor.execute(mock_task_graph):
                events.append(event)
            
            # 验证错误事件
            error_events = [e for e in events if e.event_type == "execution_error"]
            assert len(error_events) > 0 or any(e.error for e in events if e.event_type == "task_update")
            
            # 验证结果
            result = executor.get_last_result()
            assert not result.success

    @pytest.mark.asyncio
    async def test_cancel_execution(self, executor, mock_task_graph):
        """测试取消执行"""
        with patch.object(executor._task_executor, 'execute_task', return_value={
            "status": "success",
            "output": {},
        }):
            events = []
            
            # 在第一个事件后取消
            async for event in executor.execute(mock_task_graph):
                events.append(event)
                if len(events) == 1:
                    executor.cancel()
            
            # 验证取消结果
            result = executor.get_last_result()
            assert not result.success
            assert "取消" in result.error_message or result.error_message is not None

    def test_get_last_result_before_execution(self, executor):
        """测试执行前获取结果"""
        result = executor.get_last_result()
        assert result is None

    def test_reset(self, executor):
        """测试重置功能"""
        # 设置一些状态
        executor._last_result = ExecutionResult(
            success=True,
            results={},
            summary={},
        )
        executor._cancelled = True
        
        # 重置
        executor.reset()
        
        # 验证状态已清除
        assert executor.get_last_result() is None
        assert not executor._cancelled

    @pytest.mark.asyncio
    async def test_task_detail_in_events(self, executor, mock_task_graph):
        """测试任务详情在事件中"""
        with patch.object(executor._task_executor, 'execute_task', return_value={
            "status": "success",
            "output": {"result": "test"},
        }):
            events = []
            async for event in executor.execute(mock_task_graph):
                events.append(event)
            
            # 验证任务更新事件包含 detail
            task_updates = [e for e in events 
                          if e.event_type == "task_update" 
                          and e.detail is not None]
            assert len(task_updates) > 0
            
            # 验证 detail 字段
            for update in task_updates:
                if update.detail:
                    assert hasattr(update.detail, 'stage')
                    assert hasattr(update.detail, 'message')
                    assert hasattr(update.detail, 'progress')

    @pytest.mark.asyncio
    async def test_execution_progress_events(self, executor, mock_task_graph):
        """测试执行进度事件"""
        with patch.object(executor._task_executor, 'execute_task', return_value={
            "status": "success",
            "output": {},
        }):
            events = []
            async for event in executor.execute(mock_task_graph):
                events.append(event)
            
            # 验证进度事件
            progress_events = [e for e in events if e.event_type == "execution_progress"]
            assert len(progress_events) > 0
            
            # 验证进度值
            for event in progress_events:
                assert 0.0 <= event.progress <= 1.0
                assert event.completed_count is not None
                assert event.total_count is not None


class TestExecutionEvent:
    """测试 ExecutionEvent 数据类"""

    def test_event_creation(self):
        """测试事件创建"""
        event = ExecutionEvent(
            event_type="task_update",
            task_id="task_001",
            status=TaskStatus.RUNNING,
            detail=TaskDetail(
                stage="executing",
                message="正在执行",
                progress=0.5,
            ),
        )
        
        assert event.event_type == "task_update"
        assert event.task_id == "task_001"
        assert event.status == TaskStatus.RUNNING
        assert event.detail.stage == "executing"
        assert event.detail.progress == 0.5

    def test_event_without_detail(self):
        """测试无详情事件"""
        event = ExecutionEvent(
            event_type="execution_complete",
        )
        
        assert event.detail is None
        assert event.task_id is None
        assert event.status is None


class TestExecutionResult:
    """测试 ExecutionResult 数据类"""

    def test_success_result(self):
        """测试成功结果"""
        result = ExecutionResult(
            success=True,
            results={"task_001": {"output": "test"}},
            summary={"total_tasks": 2, "completed_tasks": 2},
        )
        
        assert result.success
        assert result.error_message is None
        assert result.summary["total_tasks"] == 2

    def test_failed_result(self):
        """测试失败结果"""
        result = ExecutionResult(
            success=False,
            results={},
            summary={},
            error_message="执行失败",
        )
        
        assert not result.success
        assert result.error_message == "执行失败"


class TestTaskDetail:
    """测试 TaskDetail 数据类"""

    def test_detail_creation(self):
        """测试详情创建"""
        detail = TaskDetail(
            stage="processing",
            message="正在处理数据",
            progress=0.75,
            modalities={"image": "base64_data"},
        )
        
        assert detail.stage == "processing"
        assert detail.message == "正在处理数据"
        assert detail.progress == 0.75
        assert detail.modalities == {"image": "base64_data"}

    def test_detail_default_values(self):
        """测试详情默认值"""
        detail = TaskDetail()
        
        assert detail.stage == ""
        assert detail.message == ""
        assert detail.progress == 0.0
        assert detail.modalities is None


class TestTaskStatus:
    """测试 TaskStatus 枚举"""

    def test_status_values(self):
        """测试状态值"""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
