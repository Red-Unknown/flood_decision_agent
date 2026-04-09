"""
WebSocket 决策链生成集成测试

测试三种模式的完整流程：
1. 普通模式：chat_message -> 意图解析 -> 决策链生成 -> 执行
2. Plan模式：confirm_plan -> 任务提取 -> 决策链生成 -> 执行
3. Spec模式：confirm_spec -> 任务提取 -> 决策链生成 -> 执行
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# 跳过需要真实 LLM 的测试
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
]


class MockWebSocket:
    """模拟 WebSocket 连接"""

    def __init__(self):
        self.sent_messages: List[Dict[str, Any]] = []
        self.closed = False

    async def accept(self):
        pass

    async def send_json(self, data: Dict[str, Any]):
        self.sent_messages.append(data)

    async def send_text(self, text: str):
        self.sent_messages.append({"type": "text", "content": text})

    async def receive_text(self):
        # 模拟接收消息
        await asyncio.sleep(0.1)
        return json.dumps({"type": "ping"})

    async def close(self, code: int = 1000, reason: str = ""):
        self.closed = True


@pytest.fixture
def mock_websocket():
    """创建模拟 WebSocket"""
    return MockWebSocket()


@pytest.fixture
def mock_manager(mock_websocket):
    """创建模拟连接管理器"""
    from web.backend.websocket.chat_ws import ConnectionManager

    manager = ConnectionManager()
    manager.active_connections["test_conversation"] = mock_websocket
    return manager


class TestWebSocketMessageTypes:
    """测试 WebSocket 消息类型定义"""

    def test_message_type_enum(self):
        """测试消息类型枚举"""
        from web.backend.websocket.message_types import MessageType

        # 验证新增的消息类型
        assert MessageType.CONFIRM_PLAN == "confirm_plan"
        assert MessageType.CONFIRM_SPEC == "confirm_spec"
        assert MessageType.PLAN_CONFIRMED == "plan_confirmed"
        assert MessageType.SPEC_CONFIRMED == "spec_confirmed"
        assert MessageType.INTENT_PARSED == "intent_parsed"
        assert MessageType.CHAIN_GENERATION_STAGE == "chain_generation_stage"
        assert MessageType.TASK_GRAPH_GENERATED == "task_graph_generated"
        assert MessageType.CHAIN_GENERATED == "chain_generated"
        assert MessageType.EXECUTION_STARTED == "execution_started"
        assert MessageType.TASK_UPDATE == "task_update"
        assert MessageType.EXECUTION_PROGRESS == "execution_progress"
        assert MessageType.EXECUTION_COMPLETE == "execution_complete"
        assert MessageType.ASSISTANT_MESSAGE == "assistant_message"
        assert MessageType.CANCEL_OPERATION == "cancel_operation"
        assert MessageType.OPERATION_CANCELLED == "operation_cancelled"


class TestWebSocketVisualizer:
    """测试 WebSocket 可视化器"""

    @pytest.mark.asyncio
    async def test_visualizer_initialization(self, mock_manager):
        """测试可视化器初始化"""
        from web.backend.websocket.message_handlers import WebSocketVisualizer

        visualizer = WebSocketVisualizer(
            manager=mock_manager,
            conversation_id="test_conversation",
            enabled=True
        )

        assert visualizer.manager == mock_manager
        assert visualizer.conversation_id == "test_conversation"
        assert visualizer.enabled is True

    @pytest.mark.asyncio
    async def test_visualizer_send_event(self, mock_manager):
        """测试可视化器发送事件"""
        from web.backend.websocket.message_handlers import WebSocketVisualizer

        visualizer = WebSocketVisualizer(
            manager=mock_manager,
            conversation_id="test_conversation",
            enabled=True
        )

        # 发送测试事件
        await visualizer._send_event("test_event", {"data": "test"})

        # 验证消息已发送
        websocket = mock_manager.active_connections["test_conversation"]
        assert len(websocket.sent_messages) > 0
        last_message = websocket.sent_messages[-1]
        assert last_message["type"] == "test_event"
        assert last_message["data"] == "test"


class TestChatMessageHandler:
    """测试普通模式处理器"""

    @pytest.mark.asyncio
    async def test_handler_initialization(self, mock_manager):
        """测试处理器初始化"""
        from web.backend.websocket.message_handlers import ChatMessageHandler

        handler = ChatMessageHandler(manager=mock_manager)
        assert handler.manager == mock_manager

    @pytest.mark.asyncio
    async def test_empty_message_handling(self, mock_manager):
        """测试空消息处理"""
        from web.backend.websocket.message_handlers import ChatMessageHandler

        handler = ChatMessageHandler(manager=mock_manager)

        # 发送空消息
        await handler.handle({"content": ""}, "test_conversation")

        # 验证错误响应
        websocket = mock_manager.active_connections["test_conversation"]
        assert len(websocket.sent_messages) > 0
        last_message = websocket.sent_messages[-1]
        assert last_message["type"] == "error"
        assert last_message["code"] == "EMPTY_MESSAGE"

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要真实 LLM 服务")
    async def test_full_chat_flow(self, mock_manager):
        """测试完整聊天流程（需要 LLM）"""
        from web.backend.websocket.message_handlers import ChatMessageHandler

        handler = ChatMessageHandler(manager=mock_manager)

        # 发送测试消息
        await handler.handle(
            {"content": "查询今日水位"},
            "test_conversation"
        )

        # 验证响应序列
        websocket = mock_manager.active_connections["test_conversation"]
        messages = websocket.sent_messages

        # 验证消息类型序列
        message_types = [m.get("type") for m in messages]
        assert "user_message_confirm" in message_types
        assert "intent_parsed" in message_types or "error" in message_types


class TestConfirmPlanHandler:
    """测试 Plan 模式确认处理器"""

    @pytest.mark.asyncio
    async def test_missing_plan_id(self, mock_manager):
        """测试缺少 Plan ID"""
        from web.backend.websocket.message_handlers import ConfirmPlanHandler

        handler = ConfirmPlanHandler(manager=mock_manager)

        # 发送缺少 plan_id 的消息
        await handler.handle({"action": "confirm"}, "test_conversation")

        # 验证错误响应
        websocket = mock_manager.active_connections["test_conversation"]
        assert len(websocket.sent_messages) > 0
        last_message = websocket.sent_messages[-1]
        assert last_message["type"] == "error"
        assert last_message["code"] == "MISSING_PLAN_ID"

    @pytest.mark.asyncio
    async def test_cancel_action(self, mock_manager):
        """测试取消操作"""
        from web.backend.websocket.message_handlers import ConfirmPlanHandler

        handler = ConfirmPlanHandler(manager=mock_manager)

        # 发送取消消息
        await handler.handle(
            {"plan_id": "test_plan", "action": "cancel"},
            "test_conversation"
        )

        # 验证取消响应
        websocket = mock_manager.active_connections["test_conversation"]
        assert len(websocket.sent_messages) > 0
        last_message = websocket.sent_messages[-1]
        assert last_message["type"] == "operation_cancelled"
        assert last_message["operation_type"] == "plan"

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要真实 LLM 服务")
    async def test_full_plan_flow(self, mock_manager):
        """测试完整 Plan 流程（需要 LLM）"""
        from web.backend.websocket.message_handlers import ConfirmPlanHandler

        handler = ConfirmPlanHandler(manager=mock_manager)

        # 发送确认消息
        await handler.handle(
            {"plan_id": "test_plan", "action": "confirm"},
            "test_conversation"
        )

        # 验证响应序列
        websocket = mock_manager.active_connections["test_conversation"]
        messages = websocket.sent_messages

        # 验证消息类型序列
        message_types = [m.get("type") for m in messages]
        assert "plan_confirmed" in message_types or "error" in message_types


class TestConfirmSpecHandler:
    """测试 Spec 模式确认处理器"""

    @pytest.mark.asyncio
    async def test_missing_feature_name(self, mock_manager):
        """测试缺少功能名称"""
        from web.backend.websocket.message_handlers import ConfirmSpecHandler

        handler = ConfirmSpecHandler(manager=mock_manager)

        # 发送缺少 feature_name 的消息
        await handler.handle({"action": "confirm"}, "test_conversation")

        # 验证错误响应
        websocket = mock_manager.active_connections["test_conversation"]
        assert len(websocket.sent_messages) > 0
        last_message = websocket.sent_messages[-1]
        assert last_message["type"] == "error"
        assert last_message["code"] == "MISSING_FEATURE_NAME"

    @pytest.mark.asyncio
    async def test_cancel_action(self, mock_manager):
        """测试取消操作"""
        from web.backend.websocket.message_handlers import ConfirmSpecHandler

        handler = ConfirmSpecHandler(manager=mock_manager)

        # 发送取消消息
        await handler.handle(
            {"feature_name": "test_feature", "action": "cancel"},
            "test_conversation"
        )

        # 验证取消响应
        websocket = mock_manager.active_connections["test_conversation"]
        assert len(websocket.sent_messages) > 0
        last_message = websocket.sent_messages[-1]
        assert last_message["type"] == "operation_cancelled"
        assert last_message["operation_type"] == "spec"


class TestCancelOperationHandler:
    """测试取消操作处理器"""

    @pytest.mark.asyncio
    async def test_cancel_operation(self, mock_manager):
        """测试取消操作"""
        from web.backend.websocket.message_handlers import CancelOperationHandler

        handler = CancelOperationHandler(manager=mock_manager)

        # 发送取消消息
        await handler.handle(
            {
                "operation_type": "execution",
                "operation_id": "exec_123",
                "reason": "用户请求"
            },
            "test_conversation"
        )

        # 验证取消响应
        websocket = mock_manager.active_connections["test_conversation"]
        assert len(websocket.sent_messages) > 0
        last_message = websocket.sent_messages[-1]
        assert last_message["type"] == "operation_cancelled"
        assert last_message["operation_type"] == "execution"
        assert last_message["operation_id"] == "exec_123"


class TestMessageHandlerRegistry:
    """测试消息处理器注册表"""

    def test_handler_map(self):
        """测试处理器映射表"""
        from web.backend.websocket.message_handlers import HANDLER_MAP, get_handler
        from web.backend.websocket.chat_ws import ConnectionManager

        # 验证所有处理器已注册
        assert "ping" in HANDLER_MAP
        assert "chat_message" in HANDLER_MAP
        assert "start_plan" in HANDLER_MAP
        assert "start_spec" in HANDLER_MAP
        assert "confirm_plan" in HANDLER_MAP
        assert "confirm_spec" in HANDLER_MAP
        assert "cancel_operation" in HANDLER_MAP

    def test_get_handler(self):
        """测试获取处理器"""
        from web.backend.websocket.message_handlers import (
            get_handler, ChatMessageHandler, ConfirmPlanHandler,
            ConfirmSpecHandler, CancelOperationHandler
        )
        from web.backend.websocket.chat_ws import ConnectionManager

        manager = ConnectionManager()

        # 测试获取已知处理器
        handler = get_handler("chat_message", manager)
        assert isinstance(handler, ChatMessageHandler)

        handler = get_handler("confirm_plan", manager)
        assert isinstance(handler, ConfirmPlanHandler)

        handler = get_handler("confirm_spec", manager)
        assert isinstance(handler, ConfirmSpecHandler)

        handler = get_handler("cancel_operation", manager)
        assert isinstance(handler, CancelOperationHandler)

        # 测试获取未知处理器
        handler = get_handler("unknown_type", manager)
        assert handler is None


class TestEventFlow:
    """测试事件流"""

    def test_normal_mode_event_flow(self):
        """测试普通模式事件流"""
        # 普通模式事件流：
        # chat_message -> user_message_confirm -> intent_parsed -> chain_generation_stage ->
        # task_graph_generated -> chain_generated -> execution_started -> task_update ->
        # execution_progress -> execution_complete -> assistant_message

        expected_events = [
            "user_message_confirm",
            "intent_parsed",
            "chain_generation_stage",
            "task_graph_generated",
            "chain_generated",
            "execution_started",
            "task_update",
            "execution_complete",
            "assistant_message",
        ]

        # 验证所有事件类型在 MessageType 中定义
        from web.backend.websocket.message_types import MessageType

        for event in expected_events:
            assert hasattr(MessageType, event.upper())

    def test_plan_mode_event_flow(self):
        """测试 Plan 模式事件流"""
        # Plan模式事件流：
        # confirm_plan -> plan_confirmed -> task_extracting -> chain_generation_stage ->
        # task_graph_generated -> chain_generated -> execution_started -> task_update ->
        # execution_progress -> execution_complete -> assistant_message

        expected_events = [
            "plan_confirmed",
            "task_extracting",
            "chain_generation_stage",
            "task_graph_generated",
            "chain_generated",
            "execution_started",
            "task_update",
            "execution_complete",
            "assistant_message",
        ]

        from web.backend.websocket.message_types import MessageType

        for event in expected_events:
            assert hasattr(MessageType, event.upper())

    def test_spec_mode_event_flow(self):
        """测试 Spec 模式事件流"""
        # Spec模式事件流：
        # confirm_spec -> spec_confirmed -> task_extracting -> chain_generation_stage ->
        # task_graph_generated -> chain_generated -> execution_started -> task_update ->
        # execution_progress -> execution_complete -> assistant_message

        expected_events = [
            "spec_confirmed",
            "task_extracting",
            "chain_generation_stage",
            "task_graph_generated",
            "chain_generated",
            "execution_started",
            "task_update",
            "execution_complete",
            "assistant_message",
        ]

        from web.backend.websocket.message_types import MessageType

        for event in expected_events:
            assert hasattr(MessageType, event.upper())


class TestIntegrationWithVisualizedPipeline:
    """测试与 VisualizedPipeline 的集成"""

    @pytest.mark.asyncio
    async def test_websocket_visualizer_integration(self, mock_manager):
        """测试 WebSocketVisualizer 集成"""
        from web.backend.websocket.message_handlers import WebSocketVisualizer
        from flood_decision_agent.visualization.models import TaskInfo, TaskStatus

        visualizer = WebSocketVisualizer(
            manager=mock_manager,
            conversation_id="test_conversation",
            enabled=True
        )

        # 模拟任务信息
        task_info = TaskInfo(
            node_id="task_001",
            task_name="测试任务",
            task_type="data_collection",
            status=TaskStatus.PENDING,
            dependencies=[],
        )

        # 添加到任务映射
        visualizer._task_info_map["task_001"] = task_info

        # 测试渲染节点开始
        visualizer._render_node_started("task_001", "UnitTaskExecutionAgent", task_info)

        # 等待异步任务完成
        await asyncio.sleep(0.1)

        # 验证消息已发送
        websocket = mock_manager.active_connections["test_conversation"]
        task_update_messages = [
            m for m in websocket.sent_messages
            if m.get("type") == "task_update"
        ]
        assert len(task_update_messages) > 0

    @pytest.mark.asyncio
    async def test_visualizer_pipeline_start(self, mock_manager):
        """测试可视化器流程开始"""
        from web.backend.websocket.message_handlers import WebSocketVisualizer

        visualizer = WebSocketVisualizer(
            manager=mock_manager,
            conversation_id="test_conversation",
            enabled=True
        )

        # 触发流程开始
        visualizer.on_pipeline_start({"task_type": "test"})

        # 等待异步任务完成
        await asyncio.sleep(0.1)

        # 验证消息已发送
        websocket = mock_manager.active_connections["test_conversation"]
        stage_messages = [
            m for m in websocket.sent_messages
            if m.get("type") == "chain_generation_stage"
        ]
        assert len(stage_messages) > 0


class TestErrorHandling:
    """测试错误处理"""

    @pytest.mark.asyncio
    async def test_handler_exception_handling(self, mock_manager):
        """测试处理器异常处理"""
        from web.backend.websocket.message_handlers import ChatMessageHandler

        handler = ChatMessageHandler(manager=mock_manager)

        # 发送无效消息（缺少 content 字段）
        await handler.handle({}, "test_conversation")

        # 验证错误响应
        websocket = mock_manager.active_connections["test_conversation"]
        assert len(websocket.sent_messages) > 0
        last_message = websocket.sent_messages[-1]
        assert last_message["type"] == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
