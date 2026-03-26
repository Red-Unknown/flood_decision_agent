"""任务实体"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """任务状态"""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """任务实体"""
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def start(self):
        """开始任务"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
    
    def complete(self, result: Any):
        """完成任务"""
        self.result = result
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def fail(self, error: str):
        """标记任务失败"""
        self.error = error
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
