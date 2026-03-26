"""消息实体"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class MessageRole(Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """消息实体"""
    id: str
    role: MessageRole
    content: str
    conversation_id: str
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def user_message(cls, id: str, content: str, conversation_id: str) -> "Message":
        """创建用户消息"""
        return cls(
            id=id,
            role=MessageRole.USER,
            content=content,
            conversation_id=conversation_id
        )
    
    @classmethod
    def assistant_message(cls, id: str, content: str, conversation_id: str) -> "Message":
        """创建助手消息"""
        return cls(
            id=id,
            role=MessageRole.ASSISTANT,
            content=content,
            conversation_id=conversation_id
        )
