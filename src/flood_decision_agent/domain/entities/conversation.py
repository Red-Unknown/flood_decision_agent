"""对话实体"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .message import Message


@dataclass
class Conversation:
    """对话实体"""
    id: str
    title: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def add_message(self, message: Message):
        """添加消息"""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_last_message(self) -> Optional[Message]:
        """获取最后一条消息"""
        return self.messages[-1] if self.messages else None
    
    def get_messages_by_role(self, role: str) -> List[Message]:
        """按角色获取消息"""
        return [m for m in self.messages if m.role.value == role]
