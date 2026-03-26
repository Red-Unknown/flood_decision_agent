"""优先级值对象"""
from enum import Enum


class Priority(Enum):
    """优先级值对象"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    
    def __lt__(self, other):
        if isinstance(other, Priority):
            return self.value < other.value
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, Priority):
            return self.value <= other.value
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, Priority):
            return self.value > other.value
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, Priority):
            return self.value >= other.value
        return NotImplemented
