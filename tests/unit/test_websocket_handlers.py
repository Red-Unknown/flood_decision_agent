"""WebSocket 消息处理器单元测试

测试 WebSocket 消息处理器的各个功能
"""

import pytest
import json
import time
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from web.backend.websocket.message_handlers import (
    LLMService,
    ChatMessageHandler,
    StartPlanHandler,
    StartSpecHandler,
    PingHandler,
    get_handler,
    HANDLER_REGISTRY,
)
from web.backend.websocket.message_types import MessageType


class TestLLMService:
    """测试 LLMService 类"""

    @patch.dict("os.environ", {"KIMI_API_KEY": "test_key"})
    def test_init_with_api_key(self):
        """测试有 API Key 时的初始化"""
        with patch("web.backend.websocket.message_handlers.OpenAI") as mock_openai:
            service = LLMService()
            assert service._client is not None
            mock_openai.assert_called_once()

    def test_init_without_api_key(self):
        """测试无 API Key 时的初始化"""
        # 清除 API Key 并确保 OpenAI 不会被调用
        with patch.dict("os.environ", {"KIMI_API_KEY": ""}, clear=True):
            service = LLMService()
            # 当没有 API Key 时，_client 应该为 None
            assert service._client is None

    @pytest.mark.asyncio
    async def test_stream_generate_without_client(self):
        """测试无客户端时的流式生成"""
        service = LLMService()
        service._client = None
        
        with pytest.raises(RuntimeError, match="LLM 客户端未初始化"):
            await service.stream_generate(
                system_prompt="系统提示",
                user_prompt="用户提示",
                on_chunk=AsyncMock(),
            )


class TestChatMessageHandler:
    """测试 ChatMessageHandler"""

    @pytest.fixture
    def mock_manager(self):
        """创建模拟的连接管理器"""
        manager = MagicMock()
        manager.send_message = AsyncMock()
        return manager

    @pytest.mark.asyncio
    async def test_handle_chat_message(self, mock_manager):
        """测试处理聊天消息"""
        handler = ChatMessageHandler(mock_manager)
        message = {"content": "你好"}
        
        await handler.handle(message, "conv_001")
        
        # 验证发送了用户消息确认
        calls = mock_manager.send_message.call_args_list
        assert any(call[0][0] == "conv_001" and call[0][1].get("type") == "user_message" for call in calls)

    @pytest.mark.asyncio
    async def test_handle_known_message(self, mock_manager):
        """测试处理已知消息（如"你好"）"""
        handler = ChatMessageHandler(mock_manager)
        message = {"content": "你好"}
        
        await handler.handle(message, "conv_001")
        
        # 验证发送了完整响应
        calls = mock_manager.send_message.call_args_list
        types = [call[0][1].get("type") for call in calls]
        assert "user_message" in types
        assert "start" in types
        assert "chunk" in types
        assert "complete" in types


class TestStartPlanHandler:
    """测试 StartPlanHandler"""

    @pytest.fixture
    def mock_manager(self):
        """创建模拟的连接管理器"""
        manager = MagicMock()
        manager.send_message = AsyncMock()
        return manager

    @pytest.mark.asyncio
    @patch("web.backend.websocket.message_handlers.get_file_storage")
    async def test_handle_start_plan(self, mock_get_storage, mock_manager):
        """测试处理启动 Plan 消息"""
        # 模拟文件存储
        mock_storage = MagicMock()
        mock_storage.save_document.return_value = True
        mock_get_storage.return_value = mock_storage
        
        # 模拟 LLM 服务
        with patch("web.backend.websocket.message_handlers.get_llm_service") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.stream_generate = AsyncMock(return_value="# 测试规划")
            mock_get_llm.return_value = mock_llm
            
            handler = StartPlanHandler(mock_manager)
            message = {"user_input": "设计洪水预警系统"}
            
            await handler.handle(message, "conv_001")
        
        # 验证发送了 process_event 消息
        calls = mock_manager.send_message.call_args_list
        types = [call[0][1].get("type") for call in calls]
        assert "process_event" in types


class TestStartSpecHandler:
    """测试 StartSpecHandler"""

    @pytest.fixture
    def mock_manager(self):
        """创建模拟的连接管理器"""
        manager = MagicMock()
        manager.send_message = AsyncMock()
        return manager

    @pytest.mark.asyncio
    @patch("web.backend.websocket.message_handlers.get_file_storage")
    async def test_handle_start_spec(self, mock_get_storage, mock_manager):
        """测试处理启动 Spec 消息"""
        # 模拟文件存储
        mock_storage = MagicMock()
        mock_storage.save_document.return_value = True
        mock_get_storage.return_value = mock_storage
        
        # 模拟 LLM 服务
        with patch("web.backend.websocket.message_handlers.get_llm_service") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.stream_generate = AsyncMock(return_value="# 测试规格")
            mock_get_llm.return_value = mock_llm
            
            handler = StartSpecHandler(mock_manager)
            message = {"user_input": "实现洪水预警模块"}
            
            await handler.handle(message, "conv_001")
        
        # 验证发送了 process_event 消息
        calls = mock_manager.send_message.call_args_list
        types = [call[0][1].get("type") for call in calls]
        assert "process_event" in types


class TestPingHandler:
    """测试 PingHandler"""

    @pytest.mark.asyncio
    async def test_handle_ping(self):
        """测试处理心跳消息"""
        manager = MagicMock()
        manager.send_message = AsyncMock()
        
        handler = PingHandler(manager)
        message = {}
        
        await handler.handle(message, "conv_001")
        
        # 验证发送了 pong 消息
        manager.send_message.assert_called_once()
        call_args = manager.send_message.call_args[0]
        assert call_args[0] == "conv_001"
        assert call_args[1]["type"] == "pong"


class TestGetHandler:
    """测试 get_handler 函数"""

    def test_get_existing_handler(self):
        """测试获取存在的处理器"""
        manager = MagicMock()
        
        handler = get_handler("chat_message", manager)
        assert handler is not None
        assert isinstance(handler, ChatMessageHandler)

    def test_get_nonexistent_handler(self):
        """测试获取不存在的处理器"""
        manager = MagicMock()
        
        handler = get_handler("unknown_type", manager)
        assert handler is None

    def test_handler_registry(self):
        """测试处理器注册表"""
        assert "chat_message" in HANDLER_REGISTRY
        assert "start_plan" in HANDLER_REGISTRY
        assert "start_spec" in HANDLER_REGISTRY
        assert "ping" in HANDLER_REGISTRY
