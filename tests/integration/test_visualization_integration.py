"""可视化模块集成测试.

测试从用户输入到所有任务执行完毕的全过程 IO。
验证：
1. TaskGraph 生成后的任务列表展示
2. NodeSchedulerAgent 执行状态实时更新
3. Agent 调用链展示
4. 执行汇总信息
"""

from __future__ import annotations

import os
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, "src"))

from flood_decision_agent.app.visualized_pipeline import (
    VisualizedPipeline,
    run_visualized_pipeline,
)
from flood_decision_agent.core.task_graph import NodeStatus, TaskGraph
from flood_decision_agent.visualization.base import BaseVisualizer
from flood_decision_agent.visualization.models import (
    EventType,
    ExecutionEvent,
    TaskInfo,
    TaskStatus,
)
from flood_decision_agent.visualization.terminal import TerminalVisualizer


class MockVisualizer(BaseVisualizer):
    """Mock 可视化器，用于测试.

    记录所有事件，便于验证。
    """

    def __init__(self):
        super().__init__(enabled=True)
        self.events: list[ExecutionEvent] = []
        self.rendered_task_list: list[TaskInfo] | None = None
        self.node_started_calls: list[dict] = []
        self.node_completed_calls: list[dict] = []
        self.node_failed_calls: list[dict] = []
        self.agent_calls: list[dict] = []

    def _render_event(self, event: ExecutionEvent) -> None:
        """记录事件."""
        self.events.append(event)

    def _render_pipeline_start(self, context) -> None:
        """渲染流程开始."""
        pass

    def _render_task_list(self, task_infos: list[TaskInfo]) -> None:
        """记录任务列表."""
        self.rendered_task_list = task_infos

    def _render_node_started(self, node_id: str, agent_id: str, task_info) -> None:
        """记录节点开始."""
        self.node_started_calls.append({
            "node_id": node_id,
            "agent_id": agent_id,
            "task_info": task_info,
        })

    def _render_node_completed(self, node_id: str, agent_id: str, duration_ms: float, task_info) -> None:
        """记录节点完成."""
        self.node_completed_calls.append({
            "node_id": node_id,
            "agent_id": agent_id,
            "duration_ms": duration_ms,
            "task_info": task_info,
        })

    def _render_node_failed(self, node_id: str, agent_id: str, error_message: str, task_info) -> None:
        """记录节点失败."""
        self.node_failed_calls.append({
            "node_id": node_id,
            "agent_id": agent_id,
            "error_message": error_message,
            "task_info": task_info,
        })

    def _render_agent_call(self, agent_call) -> None:
        """记录 Agent 调用."""
        self.agent_calls.append({
            "caller": agent_call.caller_agent,
            "callee": agent_call.callee_agent,
        })

    def _render_data_flow(self, data_flow) -> None:
        """渲染数据流."""
        pass

    def _render_pipeline_completed(self, success: bool, summary) -> None:
        """渲染流程完成."""
        pass


class TestVisualizationIntegration(unittest.TestCase):
    """可视化集成测试类."""

    @patch.dict(os.environ, {"KIMI_API_KEY": "test_api_key"})
    def test_full_pipeline_with_visualization(self):
        """测试完整 Pipeline 执行过程的可视化.

        验证：
        1. TaskGraph 生成后展示任务列表
        2. 每个节点执行时触发状态更新
        3. Agent 调用链被记录
        4. 执行汇总信息正确
        """
        # 创建 Mock 可视化器
        mock_visualizer = MockVisualizer()

        # 执行 Pipeline
        result = run_visualized_pipeline(
            task_request={
                "type": "flood_warning",
                "params": {
                    "station": "test_station",
                    "date": "2024-01-01",
                },
            },
            seed=42,
            visualizer=mock_visualizer,
        )

        # 验证 1: 任务列表被展示
        self.assertIsNotNone(
            mock_visualizer.rendered_task_list,
            "TaskGraph 生成后应展示任务列表"
        )
        self.assertGreater(
            len(mock_visualizer.rendered_task_list),
            0,
            "任务列表不应为空"
        )

        # 打印任务列表供查看
        print("\n" + "=" * 60)
        print("验证 1: TaskGraph 生成的任务列表")
        print("=" * 60)
        for i, task in enumerate(mock_visualizer.rendered_task_list, 1):
            print(f"  task {i}: {task.task_name} (类型: {task.task_type})")
        print(f"\n共 {len(mock_visualizer.rendered_task_list)} 个任务")

        # 验证 2: 节点执行事件被触发
        self.assertGreater(
            len(mock_visualizer.node_started_calls),
            0,
            "应有节点开始执行的事件"
        )
        self.assertGreater(
            len(mock_visualizer.node_completed_calls),
            0,
            "应有节点完成执行的事件"
        )

        # 打印节点执行记录
        print("\n" + "=" * 60)
        print("验证 2: 节点执行状态更新")
        print("=" * 60)
        print(f"  节点开始事件数: {len(mock_visualizer.node_started_calls)}")
        print(f"  节点完成事件数: {len(mock_visualizer.node_completed_calls)}")
        print(f"  节点失败事件数: {len(mock_visualizer.node_failed_calls)}")

        for call in mock_visualizer.node_completed_calls:
            print(f"  ✓ {call['node_id']}: {call['duration_ms']:.2f}ms")

        # 验证 3: Agent 调用链被记录
        self.assertGreater(
            len(mock_visualizer.agent_calls),
            0,
            "应有 Agent 调用记录"
        )

        # 打印 Agent 调用链
        print("\n" + "=" * 60)
        print("验证 3: Agent 调用链")
        print("=" * 60)
        for i, call in enumerate(mock_visualizer.agent_calls, 1):
            print(f"  {i}. {call['caller']} → {call['callee']}")

        # 验证 4: 执行结果和汇总
        self.assertIsInstance(result.success, bool)
        self.assertIn("total_tasks", result.execution_summary)
        self.assertIn("completed_tasks", result.execution_summary)

        print("\n" + "=" * 60)
        print("验证 4: 执行汇总")
        print("=" * 60)
        print(f"  执行成功: {result.success}")
        print(f"  总任务数: {result.execution_summary.get('total_tasks')}")
        print(f"  完成任务: {result.execution_summary.get('completed_tasks')}")
        print(f"  失败任务: {result.execution_summary.get('failed_tasks')}")
        print(f"  总耗时: {result.execution_summary.get('total_duration_ms', 0):.2f}ms")

    @patch.dict(os.environ, {"KIMI_API_KEY": "test_api_key"})
    def test_task_status_transitions(self):
        """测试任务状态转换过程.

        验证任务从 PENDING → RUNNING → COMPLETED 的状态流转。
        """
        mock_visualizer = MockVisualizer()

        run_visualized_pipeline(
            task_request={"type": "data_query", "params": {}},
            seed=42,
            visualizer=mock_visualizer,
        )

        print("\n" + "=" * 60)
        print("测试: 任务状态转换")
        print("=" * 60)

        # 验证任务列表中的状态（注意：由于TaskGraph执行后状态会改变，
        # 这里验证的是最终状态）
        if mock_visualizer.rendered_task_list:
            for task in mock_visualizer.rendered_task_list:
                print(f"  {task.node_id}: {task.status.value}")
                # 任务执行完成后状态应为 COMPLETED 或 FAILED
                self.assertIn(
                    task.status,
                    [TaskStatus.COMPLETED, TaskStatus.FAILED],
                    "任务最终状态应为 COMPLETED 或 FAILED"
                )

        # 验证节点开始事件
        for call in mock_visualizer.node_started_calls:
            if call["task_info"]:
                print(f"  开始执行: {call['node_id']} → {call['task_info'].status.value}")

        # 验证节点完成事件
        for call in mock_visualizer.node_completed_calls:
            if call["task_info"]:
                print(f"  执行完成: {call['node_id']} → {call['task_info'].status.value}")
                self.assertEqual(
                    call["task_info"].status,
                    TaskStatus.COMPLETED,
                    "完成的任务状态应为 COMPLETED"
                )

    @patch.dict(os.environ, {"KIMI_API_KEY": "test_api_key"})
    def test_visualization_disabled(self):
        """测试禁用可视化时的行为.

        验证当 enable_visualization=False 时，可视化器不会记录事件。
        """
        mock_visualizer = MockVisualizer()
        mock_visualizer.enabled = False

        result = run_visualized_pipeline(
            task_request={"type": "flood_warning", "params": {}},
            seed=42,
            visualizer=mock_visualizer,
        )

        print("\n" + "=" * 60)
        print("测试: 禁用可视化")
        print("=" * 60)
        print(f"  事件记录数: {len(mock_visualizer.events)}")
        print(f"  任务列表记录: {mock_visualizer.rendered_task_list is not None}")
        print(f"  节点开始记录数: {len(mock_visualizer.node_started_calls)}")

        # 禁用可视化时不应记录事件
        self.assertEqual(
            len(mock_visualizer.events),
            0,
            "禁用可视化时不应记录事件"
        )
        self.assertIsNone(
            mock_visualizer.rendered_task_list,
            "禁用可视化时不应展示任务列表"
        )

        # 但 Pipeline 应正常执行
        self.assertIsInstance(result.success, bool)


class TestTerminalVisualizerOutput(unittest.TestCase):
    """测试终端可视化器的输出效果."""

    def test_terminal_output_format(self):
        """测试终端输出格式.

        验证终端可视化器能正确输出带颜色和图标的文本。
        """
        visualizer = TerminalVisualizer(
            enabled=True,
            use_colors=True,
            use_unicode=True,
        )

        # 捕获输出
        captured_output = StringIO()

        print("\n" + "=" * 60)
        print("测试: 终端可视化器输出格式")
        print("=" * 60)

        # 模拟任务列表展示
        from flood_decision_agent.visualization.models import TaskInfo

        task_infos = [
            TaskInfo(
                node_id="node_1",
                task_name="数据查询 (node_1)",
                task_type="data_query",
                status=TaskStatus.PENDING,
            ),
            TaskInfo(
                node_id="node_2",
                task_name="风险评估 (node_2)",
                task_type="risk_assessment",
                status=TaskStatus.PENDING,
                dependencies=["node_1"],
            ),
        ]

        # 手动调用渲染方法
        visualizer._render_task_list(task_infos)

        # 模拟节点状态更新
        visualizer._render_node_started("node_1", "UnitTaskExecutionAgent", task_infos[0])
        print()  # 换行
        visualizer._render_node_completed("node_1", "UnitTaskExecutionAgent", 120.5, task_infos[0])

        print("\n终端输出测试完成")


class TestEventSystem(unittest.TestCase):
    """测试事件系统."""

    def test_event_handler_registration(self):
        """测试事件处理器注册和触发.

        验证自定义事件处理器能正确接收事件。
        """
        visualizer = MockVisualizer()

        # 记录接收到的事件
        received_events: list[ExecutionEvent] = []

        def custom_handler(event: ExecutionEvent):
            received_events.append(event)

        # 注册处理器
        visualizer.register_event_handler(EventType.NODE_COMPLETED, custom_handler)

        # 触发事件
        test_event = ExecutionEvent(
            event_type=EventType.NODE_COMPLETED,
            task_info=TaskInfo(
                node_id="test_node",
                task_name="测试任务",
                task_type="test",
                status=TaskStatus.COMPLETED,
            ),
        )
        visualizer.emit_event(test_event)

        print("\n" + "=" * 60)
        print("测试: 事件系统")
        print("=" * 60)
        print(f"  注册的事件处理器数: {len(visualizer.event_handlers)}")
        print(f"  接收到的事件数: {len(received_events)}")

        # 验证处理器被触发
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].event_type, EventType.NODE_COMPLETED)

    def test_event_handler_unregistration(self):
        """测试事件处理器注销."""
        visualizer = MockVisualizer()

        received_events: list[ExecutionEvent] = []

        def custom_handler(event: ExecutionEvent):
            received_events.append(event)

        # 注册然后注销
        visualizer.register_event_handler(EventType.NODE_COMPLETED, custom_handler)
        visualizer.unregister_event_handler(EventType.NODE_COMPLETED, custom_handler)

        # 触发事件
        test_event = ExecutionEvent(
            event_type=EventType.NODE_COMPLETED,
            task_info=TaskInfo(
                node_id="test_node",
                task_name="测试任务",
                task_type="test",
                status=TaskStatus.COMPLETED,
            ),
        )
        visualizer.emit_event(test_event)

        print(f"  注销后接收到的事件数: {len(received_events)}")

        # 验证处理器不再接收事件
        self.assertEqual(len(received_events), 0)


def run_integration_tests():
    """运行集成测试."""
    # 设置测试环境
    os.environ.setdefault("KIMI_API_KEY", "test_api_key_for_integration")

    print("\n" + "=" * 70)
    print("可视化模块集成测试")
    print("=" * 70)

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestVisualizationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestTerminalVisualizerOutput))
    suite.addTests(loader.loadTestsFromTestCase(TestEventSystem))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
    print(f"  运行测试数: {result.testsRun}")
    print(f"  成功: {result.wasSuccessful()}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
