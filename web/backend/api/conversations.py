"""对话管理API.

提供对话的创建、查询、删除等管理功能。
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class Conversation(BaseModel):
    """对话模型."""

    id: str = Field(..., description="对话ID")
    title: str = Field(..., description="对话标题")
    created_at: float = Field(..., description="创建时间戳")
    updated_at: float = Field(..., description="更新时间戳")
    message_count: int = Field(default=0, description="消息数量")


class ConversationCreate(BaseModel):
    """创建对话请求."""

    title: Optional[str] = Field(default=None, description="对话标题")


class ConversationResponse(BaseModel):
    """对话响应."""

    id: str
    title: str
    created_at: float
    updated_at: float
    message_count: int


# 内存存储（生产环境应使用数据库）
_conversations: Dict[str, Conversation] = {}


def generate_title() -> str:
    """生成默认对话标题."""
    return f"新对话 {len(_conversations) + 1}"


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations() -> List[ConversationResponse]:
    """获取对话列表.

    Returns:
        对话列表，按更新时间倒序排列
    """
    sorted_conversations = sorted(
        _conversations.values(),
        key=lambda x: x.updated_at,
        reverse=True,
    )
    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=c.message_count,
        )
        for c in sorted_conversations
    ]


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(data: ConversationCreate) -> ConversationResponse:
    """创建新对话.

    Args:
        data: 创建对话请求数据

    Returns:
        新创建的对话信息
    """
    conversation_id = str(uuid.uuid4())
    now = time.time()

    conversation = Conversation(
        id=conversation_id,
        title=data.title or generate_title(),
        created_at=now,
        updated_at=now,
        message_count=0,
    )

    _conversations[conversation_id] = conversation

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=conversation.message_count,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str) -> ConversationResponse:
    """获取对话详情.

    Args:
        conversation_id: 对话ID

    Returns:
        对话详情

    Raises:
        HTTPException: 对话不存在时返回404
    """
    conversation = _conversations.get(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=conversation.message_count,
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str) -> dict:
    """删除对话.

    Args:
        conversation_id: 对话ID

    Returns:
        删除结果

    Raises:
        HTTPException: 对话不存在时返回404
    """
    if conversation_id not in _conversations:
        raise HTTPException(status_code=404, detail="对话不存在")

    del _conversations[conversation_id]

    return {"success": True, "message": "对话已删除"}


def update_conversation_message_count(conversation_id: str, count: int) -> None:
    """更新对话消息数量.

    Args:
        conversation_id: 对话ID
        count: 消息数量
    """
    if conversation_id in _conversations:
        _conversations[conversation_id].message_count = count
        _conversations[conversation_id].updated_at = time.time()


def update_conversation_title(conversation_id: str, title: str) -> None:
    """更新对话标题.

    Args:
        conversation_id: 对话ID
        title: 新标题
    """
    if conversation_id in _conversations:
        _conversations[conversation_id].title = title
        _conversations[conversation_id].updated_at = time.time()
