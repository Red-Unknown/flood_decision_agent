"""WebSocket聊天服务.

提供实时双向通信，支持流式消息传输。
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Dict, List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器."""

    def __init__(self):
        """初始化连接管理器."""
        # conversation_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str) -> None:
        """建立WebSocket连接.

        Args:
            websocket: WebSocket对象
            conversation_id: 对话ID
        """
        await websocket.accept()

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "conversation_id": conversation_id,
            "timestamp": time.time(),
        })

    def disconnect(self, websocket: WebSocket, conversation_id: str) -> None:
        """断开WebSocket连接.

        Args:
            websocket: WebSocket对象
            conversation_id: 对话ID
        """
        if conversation_id in self.active_connections:
            if websocket in self.active_connections[conversation_id]:
                self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def send_message(
        self,
        conversation_id: str,
        message: dict,
    ) -> None:
        """向指定对话的所有连接发送消息.

        Args:
            conversation_id: 对话ID
            message: 消息内容
        """
        if conversation_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[conversation_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)

            # 清理断开的连接
            for conn in disconnected:
                self.active_connections[conversation_id].remove(conn)

    async def broadcast(self, message: dict) -> None:
        """广播消息到所有连接.

        Args:
            message: 消息内容
        """
        for conversation_id in list(self.active_connections.keys()):
            await self.send_message(conversation_id, message)


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str) -> None:
    """WebSocket聊天端点.

    Args:
        websocket: WebSocket对象
        conversation_id: 对话ID
    """
    await manager.connect(websocket, conversation_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message_data = json.loads(data)

            message_type = message_data.get("type", "message")

            if message_type == "message":
                # 处理用户消息
                user_message = message_data.get("content", "")

                # 确认收到消息
                await manager.send_message(
                    conversation_id,
                    {
                        "type": "user_message",
                        "content": user_message,
                        "timestamp": time.time(),
                    },
                )

                # 模拟流式响应（实际应调用Pipeline）
                await simulate_streaming_response(conversation_id, user_message)

            elif message_type == "ping":
                # 心跳响应
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": time.time(),
                })

            elif message_type == "typing":
                # 打字状态（可选）
                await manager.send_message(
                    conversation_id,
                    {
                        "type": "typing",
                        "is_typing": message_data.get("is_typing", False),
                    },
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
    except Exception as e:
        # 发送错误消息
        try:
            await websocket.send_json({
                "type": "error",
                "content": str(e),
                "timestamp": time.time(),
            })
        except Exception:
            pass
        finally:
            manager.disconnect(websocket, conversation_id)


async def simulate_streaming_response(
    conversation_id: str,
    user_message: str,
) -> None:
    """模拟流式响应.

    Args:
        conversation_id: 对话ID
        user_message: 用户消息
    """
    # 这里应该调用实际的Pipeline
    # 现在使用模拟响应

    # 简单的响应模板
    responses = {
        "你好": "你好！我是水利智脑，有什么可以帮助你的吗？",
        "hello": "Hello! I'm the Water Resources AI Assistant. How can I help you?",
    }

    response_text = responses.get(
        user_message.strip().lower(),
        f"收到您的消息：{user_message}\n\n我正在处理您的请求，请稍候..."
    )

    # 发送开始标记
    await manager.send_message(
        conversation_id,
        {
            "type": "start",
            "timestamp": time.time(),
        },
    )

    # 流式发送响应
    accumulated = ""
    chunk_size = 2

    for i in range(0, len(response_text), chunk_size):
        chunk = response_text[i:i+chunk_size]
        accumulated += chunk

        await manager.send_message(
            conversation_id,
            {
                "type": "chunk",
                "content": chunk,
                "accumulated": accumulated,
                "timestamp": time.time(),
            },
        )

        await asyncio.sleep(0.05)  # 模拟打字延迟

    # 发送完成标记
    await manager.send_message(
        conversation_id,
        {
            "type": "complete",
            "content": response_text,
            "timestamp": time.time(),
        },
    )
