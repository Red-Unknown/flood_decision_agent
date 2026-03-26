"""状态值对象"""
from enum import Enum, auto


class Status(Enum):
    """状态值对象"""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()
    
    @property
    def is_terminal(self) -> bool:
        """是否为终止状态"""
        return self in (Status.COMPLETED, Status.FAILED, Status.CANCELLED)
    
    @property
    def is_active(self) -> bool:
        """是否为活动状态"""
        return self in (Status.PENDING, Status.IN_PROGRESS)
