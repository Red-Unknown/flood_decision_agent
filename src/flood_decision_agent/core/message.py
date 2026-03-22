from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class MessageType(Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    NODE_EXECUTE = "node_execute"
    NODE_RESULT = "node_result"
    ERROR = "error"
    EVENT = "event"


@dataclass(frozen=True)
class BaseMessage:
    """消息基类，提供统一的消息格式、序列化与幂等性保障"""

    type: MessageType
    payload: dict[str, Any]
    sender: str
    receiver: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    idempotency_key: Optional[str] = None

    def serialize(self) -> str:
        """将消息序列化为 JSON 字符串"""
        data = asdict(self)
        data["type"] = self.type.value
        data["timestamp"] = self.timestamp.isoformat()
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def deserialize(cls, json_str: str) -> BaseMessage:
        """从 JSON 字符串反序列化为消息对象"""
        data = json.loads(json_str)
        data["type"] = MessageType(data["type"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def get_idempotency_key(self) -> str:
        """获取或生成幂等键"""
        return self.idempotency_key or f"{self.sender}:{self.type.value}:{self.id}"
