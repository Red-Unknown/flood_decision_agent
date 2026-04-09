"""WebSocket 集成测试

测试 WebSocket 端到端功能
"""

import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect

from web.backend.main import app
from web.backend.websocket.chat_ws import manager


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestWebSocketConnection:
    """测试 WebSocket 连接"""

    def test_websocket_connection_establishment(self, client):
        """测试 WebSocket 连接建立"""
        with client.websocket_connect("/ws/chat/test_conv_001") as websocket:
            # 接收连接成功消息
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["conversation_id"] == "test_conv_001"

    def test_websocket_ping_pong(self, client):
        """测试 WebSocket 心跳"""
        with client.websocket_connect("/ws/chat/test_conv_002") as websocket:
            # 先接收连接成功消息
            websocket.receive_json()
            
            # 发送 ping
            websocket.send_json({"type": "ping", "timestamp": 1234567890})
            
            # 接收 pong
            data = websocket.receive_json()
            assert data["type"] == "pong"


class TestWebSocketChat:
    """测试 WebSocket 聊天功能"""

    def test_chat_message_flow(self, client):
        """测试聊天消息完整流程"""
        with client.websocket_connect("/ws/chat/test_conv_003") as websocket:
            # 接收连接成功消息
            websocket.receive_json()
            
            # 发送聊天消息
            websocket.send_json({
                "type": "chat_message",
                "content": "你好",
                "role": "user",
            })
            
            # 接收响应（可能有多个消息）
            messages = []
            for _ in range(10):  # 最多接收10条消息
                try:
                    data = websocket.receive_json(timeout=2.0)
                    messages.append(data)
                    if data.get("type") == "complete":
                        break
                except Exception:
                    break
            
            # 验证收到了预期的消息类型
            types = [m.get("type") for m in messages]
            assert "user_message" in types
            assert "complete" in types


class TestWebSocketPlanMode:
    """测试 WebSocket Plan 模式"""

    @patch("web.backend.websocket.message_handlers.get_llm_service")
    @patch("web.backend.websocket.message_handlers.get_file_storage")
    def test_start_plan_flow(self, mock_get_storage, mock_get_llm, client):
        """测试启动 Plan 模式流程"""
        # 模拟文件存储
        mock_storage = MagicMock()
        mock_storage.save_document.return_value = True
        mock_get_storage.return_value = mock_storage
        
        # 模拟 LLM 服务
        mock_llm = MagicMock()
        
        async def mock_stream_generate(*args, **kwargs):
            on_chunk = kwargs.get("on_chunk")
            if on_chunk:
                await on_chunk("# 规划文档")
                await on_chunk("\n\n这是规划内容")
            return "# 规划文档\n\n这是规划内容"
        
        mock_llm.stream_generate = mock_stream_generate
        mock_get_llm.return_value = mock_llm
        
        with client.websocket_connect("/ws/chat/test_conv_004") as websocket:
            # 接收连接成功消息
            websocket.receive_json()
            
            # 发送启动 Plan 消息
            websocket.send_json({
                "type": "start_plan",
                "user_input": "设计洪水预警系统",
            })
            
            # 接收响应
            messages = []
            for _ in range(20):
                try:
                    data = websocket.receive_json(timeout=2.0)
                    messages.append(data)
                    if data.get("type") == "document_complete":
                        break
                except Exception:
                    break
            
            # 验证消息类型
            types = [m.get("type") for m in messages]
            assert "process_event" in types
            assert "document_complete" in types


class TestWebSocketSpecMode:
    """测试 WebSocket Spec 模式"""

    @patch("web.backend.websocket.message_handlers.get_llm_service")
    @patch("web.backend.websocket.message_handlers.get_file_storage")
    def test_start_spec_flow(self, mock_get_storage, mock_get_llm, client):
        """测试启动 Spec 模式流程"""
        # 模拟文件存储
        mock_storage = MagicMock()
        mock_storage.save_document.return_value = True
        mock_get_storage.return_value = mock_storage
        
        # 模拟 LLM 服务
        mock_llm = MagicMock()
        
        async def mock_stream_generate(*args, **kwargs):
            on_chunk = kwargs.get("on_chunk")
            if on_chunk:
                await on_chunk("# 规格文档")
                await on_chunk("\n\n这是规格内容")
            return "# 规格文档\n\n这是规格内容"
        
        mock_llm.stream_generate = mock_stream_generate
        mock_get_llm.return_value = mock_llm
        
        with client.websocket_connect("/ws/chat/test_conv_005") as websocket:
            # 接收连接成功消息
            websocket.receive_json()
            
            # 发送启动 Spec 消息
            websocket.send_json({
                "type": "start_spec",
                "user_input": "实现洪水预警模块",
            })
            
            # 接收响应
            messages = []
            for _ in range(20):
                try:
                    data = websocket.receive_json(timeout=2.0)
                    messages.append(data)
                    if data.get("type") == "document_complete":
                        break
                except Exception:
                    break
            
            # 验证消息类型
            types = [m.get("type") for m in messages]
            assert "process_event" in types
            assert "document_complete" in types


class TestWebSocketErrorHandling:
    """测试 WebSocket 错误处理"""

    def test_invalid_json(self, client):
        """测试无效 JSON 处理"""
        with client.websocket_connect("/ws/chat/test_conv_006") as websocket:
            # 接收连接成功消息
            websocket.receive_json()
            
            # 发送无效 JSON
            websocket.send_text("invalid json")
            
            # 接收错误消息
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert data["code"] == "INVALID_JSON"

    def test_unknown_message_type(self, client):
        """测试未知消息类型处理"""
        with client.websocket_connect("/ws/chat/test_conv_007") as websocket:
            # 接收连接成功消息
            websocket.receive_json()
            
            # 发送未知类型消息
            websocket.send_json({
                "type": "unknown_type",
                "data": "test",
            })
            
            # 接收错误消息
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert data["code"] == "UNKNOWN_MESSAGE_TYPE"
