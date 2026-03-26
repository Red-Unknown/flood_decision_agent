"""Interfaces 接口适配层 - API/WebSocket/CLI"""

# API 路由
from .api.routes.chat import chat_router
from .api.routes.conversations import conversations_router
from .api.routes.health import health_router

# WebSocket 处理器
from .websocket.handlers.chat_handler import ChatWebSocketHandler

# CLI 命令
from .cli.commands.chat import chat_command
from .cli.commands.evaluate import evaluate_command

__all__ = [
    # API 路由
    "chat_router",
    "conversations_router",
    "health_router",
    # WebSocket
    "ChatWebSocketHandler",
    # CLI
    "chat_command",
    "evaluate_command",
]
