"""WebSocket 聊天路由模块

提供实时双向通信功能，支持：
- 聊天消息传输
- Plan/Spec 模式启动
- LLM 流式生成
- 心跳检测
"""

from __future__ import annotations

import json
from src.flood_decision_agent.shared.utils.json_utils import fast_json_dumps, fast_json_loads
import time
from typing import Dict, Any
from loguru import logger

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from web.backend.websocket.message_types import MessageType
from web.backend.websocket.message_handlers import get_handler

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        """初始化连接管理器"""
        # 存储连接: {conversation_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str) -> bool:
        """建立 WebSocket 连接

        Args:
            websocket: WebSocket 对象
            conversation_id: 对话ID

        Returns:
            是否连接成功
        """
        # 检查是否已有连接
        if conversation_id in self.active_connections:
            # 关闭旧连接
            old_ws = self.active_connections[conversation_id]
            try:
                await old_ws.close(code=1000, reason="新的连接已建立")
            except Exception:
                pass

        # 接受新连接
        await websocket.accept()
        self.active_connections[conversation_id] = websocket

        # 发送连接成功消息
        await self.send_message(
            conversation_id,
            {
                "type": "connected",
                "conversation_id": conversation_id,
                "timestamp": time.time(),
            },
        )

        return True

    def disconnect(self, conversation_id: str) -> None:
        """断开 WebSocket 连接

        Args:
            conversation_id: 对话ID
        """
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]

    async def send_message(self, conversation_id: str, message: Dict[str, Any]) -> bool:
        """发送消息到指定对话

        Args:
            conversation_id: 对话ID
            message: 消息内容

        Returns:
            是否发送成功
        """
        if conversation_id not in self.active_connections:
            return False

        try:
            websocket = self.active_connections[conversation_id]
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """广播消息到所有连接

        Args:
            message: 消息内容
        """
        disconnected = []
        for conversation_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(conversation_id)

        # 清理断开的连接
        for conversation_id in disconnected:
            self.disconnect(conversation_id)


# 全局连接管理器实例
manager = ConnectionManager()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """WebSocket 端点

    Args:
        websocket: WebSocket 对象
        conversation_id: 对话ID
    """
    # 建立连接
    await manager.connect(websocket, conversation_id)

    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()

            try:
                message = fast_json_loads(data)
                message_type = message.get("type", "unknown")
                logger.info(f"[WebSocket] 收到消息: type={message_type}, conversation_id={conversation_id}")

                # 获取消息处理器
                handler = get_handler(message_type, manager)
                logger.debug(f"[WebSocket] 获取处理器: {handler}")

                if handler:
                    # 处理消息
                    await handler.handle(message, conversation_id)
                else:
                    # 未知消息类型
                    logger.warning(f"[WebSocket] 未知消息类型: {message_type}")
                    await manager.send_message(
                        conversation_id,
                        {
                            "type": "error",
                            "code": "UNKNOWN_MESSAGE_TYPE",
                            "message": f"未知的消息类型: {message_type}",
                            "timestamp": time.time(),
                        },
                    )

            except json.JSONDecodeError:
                # JSON 解析错误
                await manager.send_message(
                    conversation_id,
                    {
                        "type": "error",
                        "code": "INVALID_JSON",
                        "message": "消息格式错误，必须是有效的 JSON",
                        "timestamp": time.time(),
                    },
                )

            except Exception as e:
                # 处理异常
                logger.error(f"处理消息时出错: {e}")
                await manager.send_message(
                    conversation_id,
                    {
                        "type": "error",
                        "code": "PROCESSING_ERROR",
                        "message": f"处理消息时出错: {str(e)}",
                        "timestamp": time.time(),
                    },
                )

    except WebSocketDisconnect:
        # 客户端断开连接
        logger.info(f"客户端断开连接: {conversation_id}")
        manager.disconnect(conversation_id)

    except Exception as e:
        # 其他异常
        logger.error(f"WebSocket 错误: {e}")
        manager.disconnect(conversation_id)
