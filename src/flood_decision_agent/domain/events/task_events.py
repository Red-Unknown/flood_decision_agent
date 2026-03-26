"""任务领域事件"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: str
    event_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskCreatedEvent(DomainEvent):
    """任务创建事件"""
    task_id: str = field(default="")
    task_name: str = field(default="")
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = "TASK_CREATED"


@dataclass
class TaskCompletedEvent(DomainEvent):
    """任务完成事件"""
    task_id: str = field(default="")
    task_name: str = field(default="")
    result: Any = field(default=None)
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = "TASK_COMPLETED"


@dataclass
class TaskFailedEvent(DomainEvent):
    """任务失败事件"""
    task_id: str = field(default="")
    task_name: str = field(default="")
    error: str = field(default="")
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = "TASK_FAILED"
